"""
Admin Authentication and Authorization Module
Jeseci Smart Learning Academy

This module provides admin-specific authentication, authorization middleware,
and role-based access control for the admin interface.

Author: Cavin Otieno
License: MIT License
"""

import os
import jwt
from typing import Optional, Dict, Any, List
from functools import wraps
from fastapi import HTTPException, Header, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Import user auth module
import user_auth as auth_module

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jeseci_secret_key_change_in_production")
JWT_ALGORITHM = "HS256"

# Initialize FastAPI security
security = HTTPBearer()

# =============================================================================
# Admin Role Definitions
# =============================================================================

class AdminRole:
    """Admin role definitions with hierarchical permissions"""
    
    STUDENT = "student"
    ADMIN = "admin"
    CONTENT_ADMIN = "content_admin"
    USER_ADMIN = "user_admin"
    ANALYTICS_ADMIN = "analytics_admin"
    SUPER_ADMIN = "super_admin"
    
    # Role hierarchy (higher values include lower permissions)
    HIERARCHY = {
        STUDENT: 0,
        ADMIN: 1,
        CONTENT_ADMIN: 2,
        USER_ADMIN: 2,
        ANALYTICS_ADMIN: 2,
        SUPER_ADMIN: 3
    }
    
    @classmethod
    def has_permission(cls, user_role: str, required_role: str) -> bool:
        """Check if user role has required permission level"""
        user_level = cls.HIERARCHY.get(user_role, 0)
        required_level = cls.HIERARCHY.get(required_role, 0)
        return user_level >= required_level
    
    @classmethod
    def get_admin_roles(cls) -> List[str]:
        """Get all admin roles (excluding student)"""
        return [role for role, level in cls.HIERARCHY.items() if level > 0]


# =============================================================================
# Admin Authentication Functions
# =============================================================================

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Extract and validate user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    # Validate token
    token_data = auth_module.validate_jwt_token(token)
    
    if not token_data.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid or expired token",
                "message": token_data.get("error", "Authentication failed"),
                "code": "INVALID_TOKEN"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


def require_admin(min_role: str = AdminRole.ADMIN):
    """
    Decorator factory for requiring admin privileges.
    
    Args:
        min_role: Minimum admin role required
        
    Returns:
        Dependency function for FastAPI
    """
    def admin_required(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
        """
        Verify user has admin privileges.
        
        Args:
            current_user: Current user data from token
            
        Returns:
            User data if authorized
            
        Raises:
            HTTPException: If user lacks admin privileges
        """
        user_role = current_user.get("admin_role", AdminRole.STUDENT)
        is_admin = current_user.get("is_admin", False)
        
        # Check if user is admin
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Admin privileges required",
                    "message": "You must be an administrator to access this resource",
                    "code": "INSUFFICIENT_PRIVILEGES"
                }
            )
        
        # Check role hierarchy
        if not AdminRole.has_permission(user_role, min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": f"Insufficient admin privileges",
                    "message": f"Minimum required role: {min_role}, current role: {user_role}",
                    "code": "INSUFFICIENT_ROLE",
                    "required_role": min_role,
                    "current_role": user_role
                }
            )
        
        return current_user
    
    return admin_required


def require_super_admin():
    """Require super admin privileges"""
    return require_admin(AdminRole.SUPER_ADMIN)


def require_content_admin():
    """Require content admin privileges"""
    return require_admin(AdminRole.CONTENT_ADMIN)


def require_user_admin():
    """Require user admin privileges"""
    return require_admin(AdminRole.USER_ADMIN)


def require_analytics_admin():
    """Require analytics admin privileges"""
    return require_admin(AdminRole.ANALYTICS_ADMIN)


# =============================================================================
# Admin Utility Functions
# =============================================================================

def get_user_permissions(user_data: Dict[str, Any]) -> Dict[str, bool]:
    """
    Get user permissions based on admin role.
    
    Args:
        user_data: User data dictionary
        
    Returns:
        Dictionary of permission flags
    """
    if not user_data.get("is_admin", False):
        return {
            "is_admin": False,
            "can_manage_users": False,
            "can_manage_content": False,
            "can_view_analytics": False,
            "can_configure_system": False
        }
    
    role = user_data.get("admin_role", AdminRole.STUDENT)
    
    return {
        "is_admin": True,
        "can_manage_users": AdminRole.has_permission(role, AdminRole.USER_ADMIN),
        "can_manage_content": AdminRole.has_permission(role, AdminRole.CONTENT_ADMIN),
        "can_view_analytics": AdminRole.has_permission(role, AdminRole.ANALYTICS_ADMIN),
        "can_configure_system": AdminRole.has_permission(role, AdminRole.SUPER_ADMIN),
        "admin_role": role
    }


def create_admin_user(username: str, email: str, password: str, 
                     admin_role: str = AdminRole.ADMIN,
                     first_name: str = "", last_name: str = "") -> Dict[str, Any]:
    """
    Create a new admin user.
    
    Args:
        username: Admin username
        email: Admin email
        password: Admin password
        admin_role: Admin role level
        first_name: Admin first name
        last_name: Admin last name
        
    Returns:
        Registration result dictionary
    """
    # Validate admin role
    if admin_role not in AdminRole.get_admin_roles():
        raise ValueError(f"Invalid admin role: {admin_role}")
    
    return auth_module.register_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_admin=True,
        admin_role=admin_role
    )


def verify_admin_session_timeout(user_data: Dict[str, Any]) -> bool:
    """
    Verify admin session hasn't exceeded timeout.
    Admin sessions have shorter timeout than regular users.
    
    Args:
        user_data: User data from JWT token
        
    Returns:
        True if session is valid, False if expired
    """
    import datetime
    
    # Get token expiration
    exp_timestamp = user_data.get("exp")
    if not exp_timestamp:
        return False
    
    # Check if token is still valid
    current_time = datetime.datetime.utcnow().timestamp()
    return current_time < exp_timestamp


# =============================================================================
# Admin Logging and Audit Functions
# =============================================================================

def log_admin_action(admin_user: Dict[str, Any], action: str, 
                    target: str = "", details: Dict[str, Any] = None) -> None:
    """
    Log admin actions for audit trail.
    
    Args:
        admin_user: Admin user data
        action: Action performed (e.g., "user_suspended", "course_created")
        target: Target of action (e.g., user ID, course ID)
        details: Additional action details
    """
    import logging
    import datetime
    
    logger = logging.getLogger("admin_audit")
    
    audit_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "admin_user_id": admin_user.get("user_id"),
        "admin_username": admin_user.get("username"),
        "admin_role": admin_user.get("admin_role"),
        "action": action,
        "target": target,
        "details": details or {}
    }
    
    logger.info(f"ADMIN_ACTION: {audit_entry}")


# =============================================================================
# FastAPI Dependencies for Admin Routes
# =============================================================================

# Standard admin authentication
AdminUser = Depends(require_admin())

# Role-specific authentication
SuperAdminUser = Depends(require_super_admin())
ContentAdminUser = Depends(require_content_admin())
UserAdminUser = Depends(require_user_admin())
AnalyticsAdminUser = Depends(require_analytics_admin())

# Current user (any authenticated user)
CurrentUser = Depends(get_current_user_from_token)