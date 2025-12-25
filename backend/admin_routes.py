"""
Admin API Routes - Jeseci Smart Learning Academy
FastAPI Admin Routes with Role-Based Access Control

This module provides admin-only API endpoints for platform management
including user management, content administration, and analytics.

Author: Cavin Otieno
License: MIT License
"""

import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import modules
import user_auth as auth_module
import admin_auth
from admin_auth import AdminRole, AdminUser, SuperAdminUser, UserAdminUser

# =============================================================================
# Admin Pydantic Models
# =============================================================================

class AdminUserListResponse(BaseModel):
    success: bool
    users: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int
    filters: Dict[str, Any]

class AdminUserUpdateRequest(BaseModel):
    user_id: str = Field(..., description="User ID to update")
    is_admin: Optional[bool] = Field(None, description="Admin status")
    admin_role: Optional[str] = Field(None, description="Admin role")
    is_active: Optional[bool] = Field(None, description="Account active status")

class AdminUserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    admin_role: str = Field(default=AdminRole.ADMIN)
    learning_style: str = Field(default="visual")
    skill_level: str = Field(default="beginner")

class AdminStatsResponse(BaseModel):
    success: bool
    stats: Dict[str, Any]
    generated_at: str

class AdminActionResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    action: str
    timestamp: str

class BulkUserActionRequest(BaseModel):
    user_ids: List[str] = Field(..., description="List of user IDs")
    action: str = Field(..., description="Action: suspend, activate, delete")
    reason: Optional[str] = Field(None, description="Reason for action")

# =============================================================================
# Admin Router Creation
# =============================================================================

def create_admin_router() -> FastAPI:
    """Create admin-only FastAPI router with endpoints"""
    
    admin_app = FastAPI(
        title="Jeseci Admin API",
        description="Admin-only endpoints for platform management",
        version="1.0.0",
        docs_url="/admin/docs",
        redoc_url="/admin/redoc",
        openapi_url="/admin/openapi.json"
    )

    # Add CORS middleware
    admin_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # =============================================================================
    # Admin Dashboard & Overview
    # =============================================================================

    @admin_app.get("/admin/dashboard", response_model=AdminStatsResponse)
    async def get_admin_dashboard(admin_user: Dict[str, Any] = AdminUser):
        """Get admin dashboard overview statistics"""
        try:
            # Get user statistics
            all_users = auth_module.get_all_users(limit=1000, include_inactive=True)
            admin_users = auth_module.get_all_users(limit=1000, admin_only=True)
            active_users = auth_module.get_all_users(limit=1000, include_inactive=False)
            
            # Calculate statistics
            total_users = all_users.get("total", 0)
            total_admins = admin_users.get("total", 0)
            active_user_count = active_users.get("total", 0)
            inactive_users = total_users - active_user_count
            
            # Get recent registrations (last 7 days)
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            recent_users = [
                user for user in all_users.get("users", [])
                if user.get("created_at") and 
                datetime.fromisoformat(user["created_at"]) > week_ago
            ]
            
            # Admin role distribution
            admin_role_dist = {}
            for user in admin_users.get("users", []):
                role = user.get("admin_role", "student")
                admin_role_dist[role] = admin_role_dist.get(role, 0) + 1
            
            stats = {
                "user_statistics": {
                    "total_users": total_users,
                    "active_users": active_user_count,
                    "inactive_users": inactive_users,
                    "total_admins": total_admins,
                    "new_users_this_week": len(recent_users)
                },
                "admin_statistics": {
                    "total_admins": total_admins,
                    "role_distribution": admin_role_dist
                },
                "system_health": {
                    "database_status": "healthy",
                    "api_status": "healthy",
                    "auth_system": "operational"
                }
            }
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "dashboard_accessed", 
                details={"stats_generated": True}
            )
            
            return AdminStatsResponse(
                success=True,
                stats=stats,
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to generate dashboard statistics",
                    "message": str(e)
                }
            )

    # =============================================================================
    # User Management Endpoints
    # =============================================================================

    @admin_app.get("/admin/users", response_model=AdminUserListResponse)
    async def get_all_users_admin(
        limit: int = Query(default=50, le=200, description="Maximum users to return"),
        offset: int = Query(default=0, ge=0, description="Number of users to skip"),
        include_inactive: bool = Query(default=False, description="Include inactive users"),
        admin_only: bool = Query(default=False, description="Only admin users"),
        search: Optional[str] = Query(default=None, description="Search username/email"),
        admin_user: Dict[str, Any] = UserAdminUser
    ):
        """Get all users with filtering and pagination (User Admin+)"""
        try:
            # Get users from database
            result = auth_module.get_all_users(
                limit=limit,
                offset=offset,
                include_inactive=include_inactive,
                admin_only=admin_only
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Database error", "message": result.get("error")}
                )
            
            users = result["users"]
            
            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                users = [
                    user for user in users
                    if search_lower in user.get("username", "").lower() or
                       search_lower in user.get("email", "").lower() or
                       search_lower in user.get("first_name", "").lower() or
                       search_lower in user.get("last_name", "").lower()
                ]
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "users_list_accessed",
                details={
                    "filters": {
                        "limit": limit,
                        "offset": offset,
                        "include_inactive": include_inactive,
                        "admin_only": admin_only,
                        "search": search
                    },
                    "results_count": len(users)
                }
            )
            
            return AdminUserListResponse(
                success=True,
                users=users,
                total=len(users),
                limit=limit,
                offset=offset,
                filters={
                    "include_inactive": include_inactive,
                    "admin_only": admin_only,
                    "search": search
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve users",
                    "message": str(e)
                }
            )

    @admin_app.post("/admin/users/create", response_model=AdminActionResponse)
    async def create_admin_user(
        request: AdminUserCreateRequest,
        admin_user: Dict[str, Any] = UserAdminUser
    ):
        """Create a new admin user (User Admin+)"""
        try:
            # Validate admin role
            if request.admin_role not in AdminRole.get_admin_roles():
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid admin role",
                        "message": f"Must be one of: {AdminRole.get_admin_roles()}"
                    }
                )
            
            # Only super admins can create other super admins
            if (request.admin_role == AdminRole.SUPER_ADMIN and 
                admin_user.get("admin_role") != AdminRole.SUPER_ADMIN):
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Insufficient privileges",
                        "message": "Only super admins can create super admin accounts"
                    }
                )
            
            # Create admin user
            result = auth_module.register_user(
                username=request.username,
                email=request.email,
                password=request.password,
                first_name=request.first_name,
                last_name=request.last_name,
                learning_style=request.learning_style,
                skill_level=request.skill_level,
                is_admin=True,
                admin_role=request.admin_role
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "User creation failed",
                        "message": result.get("error"),
                        "code": result.get("code")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "admin_user_created",
                target=result["user_id"],
                details={
                    "created_username": request.username,
                    "created_email": request.email,
                    "admin_role": request.admin_role
                }
            )
            
            return AdminActionResponse(
                success=True,
                message=f"Admin user created successfully with role: {request.admin_role}",
                user_id=result["user_id"],
                action="admin_user_created",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create admin user",
                    "message": str(e)
                }
            )

    @admin_app.put("/admin/users/update", response_model=AdminActionResponse)
    async def update_user_admin(
        request: AdminUserUpdateRequest,
        admin_user: Dict[str, Any] = UserAdminUser
    ):
        """Update user admin status and account settings (User Admin+)"""
        try:
            actions_performed = []
            
            # Update admin status if provided
            if request.is_admin is not None or request.admin_role is not None:
                is_admin = request.is_admin if request.is_admin is not None else False
                admin_role = request.admin_role or AdminRole.STUDENT
                
                # Validate admin role
                if is_admin and admin_role not in AdminRole.get_admin_roles():
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Invalid admin role",
                            "message": f"Must be one of: {AdminRole.get_admin_roles()}"
                        }
                    )
                
                # Only super admins can modify super admin roles
                if (admin_role == AdminRole.SUPER_ADMIN and 
                    admin_user.get("admin_role") != AdminRole.SUPER_ADMIN):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "Insufficient privileges",
                            "message": "Only super admins can modify super admin accounts"
                        }
                    )
                
                result = auth_module.update_user_admin_status(
                    request.user_id, is_admin, admin_role
                )
                
                if not result["success"]:
                    raise HTTPException(
                        status_code=400 if result.get("code") == "NOT_FOUND" else 500,
                        detail={
                            "error": "Admin status update failed",
                            "message": result.get("error")
                        }
                    )
                
                actions_performed.append(f"admin_status_{'granted' if is_admin else 'revoked'}")
            
            # Update active status if provided
            if request.is_active is not None:
                suspended = not request.is_active
                result = auth_module.suspend_user(request.user_id, suspended)
                
                if not result["success"]:
                    raise HTTPException(
                        status_code=400 if result.get("code") == "NOT_FOUND" else 500,
                        detail={
                            "error": "User status update failed",
                            "message": result.get("error")
                        }
                    )
                
                actions_performed.append(f"user_{'activated' if request.is_active else 'suspended'}")
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "user_updated",
                target=request.user_id,
                details={
                    "actions": actions_performed,
                    "is_admin": request.is_admin,
                    "admin_role": request.admin_role,
                    "is_active": request.is_active
                }
            )
            
            return AdminActionResponse(
                success=True,
                message=f"User updated successfully. Actions: {', '.join(actions_performed)}",
                user_id=request.user_id,
                action="user_updated",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to update user",
                    "message": str(e)
                }
            )

    @admin_app.post("/admin/users/bulk-action", response_model=AdminActionResponse)
    async def bulk_user_action(
        request: BulkUserActionRequest,
        admin_user: Dict[str, Any] = UserAdminUser
    ):
        """Perform bulk actions on multiple users (User Admin+)"""
        try:
            if not request.user_ids:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "No user IDs provided"}
                )
            
            if len(request.user_ids) > 100:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Cannot process more than 100 users at once"}
                )
            
            results = {"success": 0, "failed": 0, "errors": []}
            
            for user_id in request.user_ids:
                try:
                    if request.action == "suspend":
                        result = auth_module.suspend_user(user_id, True)
                    elif request.action == "activate":
                        result = auth_module.suspend_user(user_id, False)
                    else:
                        results["errors"].append(f"Invalid action: {request.action}")
                        results["failed"] += 1
                        continue
                    
                    if result["success"]:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"{user_id}: {result.get('error')}")
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"{user_id}: {str(e)}")
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, f"bulk_{request.action}",
                details={
                    "user_count": len(request.user_ids),
                    "success_count": results["success"],
                    "failed_count": results["failed"],
                    "reason": request.reason
                }
            )
            
            return AdminActionResponse(
                success=True,
                message=f"Bulk action completed: {results['success']} successful, {results['failed']} failed",
                action=f"bulk_{request.action}",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to perform bulk action",
                    "message": str(e)
                }
            )

    # =============================================================================
    # System Administration (Super Admin Only)
    # =============================================================================

    @admin_app.get("/admin/system/health")
    async def get_system_health(admin_user: Dict[str, Any] = SuperAdminUser):
        """Get comprehensive system health status (Super Admin only)"""
        try:
            # Check database health
            db_result = True  # TODO: Implement actual database health check
            
            # Check authentication system
            auth_result = True  # TODO: Implement auth system health check
            
            health_status = {
                "overall_status": "healthy" if db_result and auth_result else "degraded",
                "components": {
                    "database": "healthy" if db_result else "error",
                    "authentication": "healthy" if auth_result else "error",
                    "api": "healthy"
                },
                "checked_at": datetime.now().isoformat()
            }
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "system_health_checked"
            )
            
            return {
                "success": True,
                "health": health_status
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to check system health",
                    "message": str(e)
                }
            )

    return admin_app


# =============================================================================
# Export admin router
# =============================================================================

# Create the admin router instance
admin_router = create_admin_router()