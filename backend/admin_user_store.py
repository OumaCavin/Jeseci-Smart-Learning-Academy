# Admin user storage using PostgreSQL database
# Uses the existing User model from SQLAlchemy

import os
import threading
import datetime
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Import database utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))
from database import get_postgres_manager

# Import user auth module for proper user registration (handles bcrypt, preferences, Neo4j sync)
import user_auth as auth_module

# In-memory cache for quick lookups (synced with PostgreSQL)
admin_users_cache = {}
admin_users_lock = threading.Lock()
cache_initialized = False

def initialize_admin_store():
    """Initialize admin store by loading all users from PostgreSQL"""
    global admin_users_cache, cache_initialized
    
    if cache_initialized:
        return
    
    with admin_users_lock:
        if cache_initialized:
            return
            
        # Load all users from PostgreSQL
        pg_manager = get_postgres_manager()
        
        try:
            query = """
            SELECT u.id, u.user_id, u.username, u.email, u.is_admin, u.admin_role, 
                   u.is_active, u.created_at, u.last_login_at, u.updated_at,
                   p.first_name, p.last_name
            FROM jeseci_academy.users u
            LEFT JOIN jeseci_academy.user_profile p ON u.id = p.user_id
            ORDER BY u.created_at DESC
            """
            
            result = pg_manager.execute_query(query)
            
            admin_users_cache = {}
            if result:
                for row in result:
                    user_id = row.get('user_id')
                    admin_users_cache[user_id] = {
                        "user_id": user_id,
                        "username": row.get('username'),
                        "email": row.get('email'),
                        "first_name": row.get('first_name') or "",
                        "last_name": row.get('last_name') or "",
                        "is_admin": row.get('is_admin'),
                        "admin_role": row.get('admin_role') or "",
                        "is_active": row.get('is_active'),
                        "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
                        "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None,
                        "last_login": row.get('last_login_at').isoformat() if row.get('last_login_at') else None
                    }
            
            cache_initialized = True
        except Exception as e:
            logger.error(f"Error initializing admin store: {e}")
            cache_initialized = False

def get_all_users():
    """Get all users from PostgreSQL"""
    initialize_admin_store()
    with admin_users_lock:
        return list(admin_users_cache.values())

def get_admin_user_by_id(user_id):
    """Get a specific admin user by ID"""
    initialize_admin_store()
    with admin_users_lock:
        return admin_users_cache.get(user_id)

def get_admin_user_by_email(email):
    """Get a specific admin user by email"""
    initialize_admin_store()
    with admin_users_lock:
        for user in admin_users_cache.values():
            if user.get('email', '').lower() == email.lower():
                return user
    return None

def search_admin_users(query, include_inactive=False, admin_only=False):
    """Search users in PostgreSQL with optional admin filtering.
    
    Args:
        query: Search string to match against username, email, first_name, last_name
        include_inactive: Include inactive users in results
        admin_only: If True, only search admin users. If False, search all users.
    """
    pg_manager = get_postgres_manager()
    
    # Build dynamic query with positional parameters
    # Only apply is_admin filter if admin_only is True
    if admin_only:
        sql_conditions = ["u.is_admin = true"]
    else:
        sql_conditions = []  # No admin filter - search all users
    
    params = []
    
    if not include_inactive:
        sql_conditions.append("u.is_active = true")
    if query:
        sql_conditions.append("(u.username ILIKE %s OR u.email ILIKE %s OR p.first_name ILIKE %s OR p.last_name ILIKE %s)")
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"])
    
    where_clause = " AND ".join(sql_conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause
    
    search_query = f"""
    SELECT u.id, u.user_id, u.username, u.email, u.is_admin, u.admin_role, 
           u.is_active, u.created_at, u.last_login_at, u.updated_at,
           p.first_name, p.last_name
    FROM jeseci_academy.users u
    LEFT JOIN jeseci_academy.user_profile p ON u.id = p.user_id
    {where_clause}
    ORDER BY u.created_at DESC
    """
    
    try:
        result = pg_manager.execute_query(search_query, params)
    except Exception as e:
        logger.error(f"Error searching admin users: {e}")
        return []
    
    users = []
    for row in result or []:
        users.append({
            "user_id": row.get('user_id'),
            "username": row.get('username'),
            "email": row.get('email'),
            "first_name": row.get('first_name') or "",
            "last_name": row.get('last_name') or "",
            "is_admin": row.get('is_admin'),
            "admin_role": row.get('admin_role') or "",
            "is_active": row.get('is_active'),
            "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
            "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None,
            "last_login": row.get('last_login_at').isoformat() if row.get('last_login_at') else None
        })
    
    return users

def create_admin_user(username, email, password, admin_role, first_name="", last_name="", 
               learning_style="visual", skill_level="beginner", skip_verification=True,
               daily_goal_minutes=30, notifications_enabled=True, email_reminders=True, 
               dark_mode=False, auto_play_videos=True):
    """Create a new admin user using the proper registration flow from user_auth module.
    
    This ensures:
    - Proper bcrypt password hashing
    - Creation of user_learning_preferences record with configurable settings
    - Neo4j graph sync
    - Proper transaction handling with commit/rollback
    - Optional email verification (skip_verification=True by default)
    - Configurable learning style, skill level, and learning preferences
    
    Args:
        username: Admin username
        email: Admin email
        password: Admin password
        admin_role: Admin role (admin, content_admin, user_admin, super_admin)
        first_name: Optional first name
        last_name: Optional last name
        learning_style: Learning style (visual, auditory, reading, kinesthetic)
        skill_level: Skill level (beginner, intermediate, advanced)
        skip_verification: If True, user is pre-verified and can login immediately.
                         If False, a verification email is sent and user must verify first.
        daily_goal_minutes: Daily learning goal in minutes (default: 30)
        notifications_enabled: Enable push notifications (default: True)
        email_reminders: Enable email reminders (default: True)
        dark_mode: Enable dark mode UI (default: False)
        auto_play_videos: Auto-play video content (default: True)
    """
    
    # Use the user_auth.register_user function which handles all the required operations
    result = auth_module.register_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        learning_style=learning_style,
        skill_level=skill_level,
        is_admin=True,
        admin_role=admin_role,
        skip_verification=skip_verification,
        daily_goal_minutes=daily_goal_minutes,
        notifications_enabled=notifications_enabled,
        email_reminders=email_reminders,
        dark_mode=dark_mode,
        auto_play_videos=auto_play_videos
    )
    
    if result.get('success'):
        # Invalidate cache to force reload
        global cache_initialized
        cache_initialized = False
        
        # Build complete user object matching the cache structure
        user_object = {
            "user_id": result.get('user_id'),
            "username": result.get('username'),
            "email": result.get('email'),
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": True,
            "admin_role": result.get('admin_role'),
            "is_active": True,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_login": None
        }
        
        return {
            "success": True, 
            "user": user_object,
            "message": "Admin user created successfully"
        }
    
    # Return the error from auth_module
    error_code = result.get('code', 'UNKNOWN_ERROR')
    error_msg = result.get('error', 'Failed to create user')
    
    if error_code == 'CONFLICT':
        error_msg = "User with this email or username already exists"
    
    return {"success": False, "error": error_msg, "code": error_code}

def update_admin_user(user_id, updates):
    """Update an existing admin user in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Check if user exists and get INTEGER id
    check_query = "SELECT id, user_id FROM jeseci_academy.users WHERE user_id = %s"
    try:
        existing = pg_manager.execute_query(check_query, (user_id,))
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")
        return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
    
    if not existing:
        return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
    
    user_db_id = existing[0]['id']  # Get INTEGER id for profile operations
    
    # Build update query for users table
    allowed_user_fields = ['is_admin', 'admin_role', 'is_active']
    user_set_clauses = []
    user_params = [user_id]
    
    # Handle profile fields separately
    profile_fields = {}
    for field, value in updates.items():
        if field in allowed_user_fields:
            user_set_clauses.append(f"{field} = %s")
            user_params.append(value)
        elif field in ['first_name', 'last_name']:
            profile_fields[field] = value
    
    if user_set_clauses:
        user_set_clauses.append("updated_at = NOW()")
        user_update_query = f"""
        UPDATE jeseci_academy.users 
        SET {', '.join(user_set_clauses)}
        WHERE user_id = %s
        """
        try:
            pg_manager.execute_query(user_update_query, user_params, fetch=False)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
    
    # Update profile table if needed (using INTEGER user_db_id)
    if profile_fields:
        profile_set_clauses = []
        profile_params = [user_db_id]
        for field, value in profile_fields.items():
            profile_set_clauses.append(f"{field} = %s")
            profile_params.append(value)
        
        if profile_set_clauses:
            profile_set_clauses.append("updated_at = NOW()")
            profile_update_query = f"""
            UPDATE jeseci_academy.user_profile 
            SET {', '.join(profile_set_clauses)}
            WHERE user_id = %s
            """
            try:
                pg_manager.execute_query(profile_update_query, profile_params, fetch=False)
            except Exception as e:
                logger.error(f"Error updating user profile: {e}")
                return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
    
    # Invalidate cache
    global cache_initialized
    cache_initialized = False
    
    return {"success": True, "message": "User updated successfully"}

def bulk_admin_action(user_ids, action, reason=""):
    """Perform bulk action on admin users in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # For delete action, we need INTEGER ids for user_profile deletion
    if action == 'delete':
        # Look up INTEGER ids from the VARCHAR user_ids
        lookup_query = "SELECT id FROM jeseci_academy.users WHERE user_id = ANY(%s)"
        try:
            lookup_result = pg_manager.execute_query(lookup_query, (user_ids,))
        except Exception as e:
            logger.error(f"Error looking up user IDs for bulk delete: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
        
        integer_ids = [row['id'] for row in lookup_result] if lookup_result else []
        
        # Delete from profile first (foreign key uses INTEGER id)
        if integer_ids:
            delete_profile = "DELETE FROM jeseci_academy.user_profile WHERE user_id = ANY(%s)"
            try:
                pg_manager.execute_query(delete_profile, (integer_ids,), fetch=False)
            except Exception as e:
                logger.error(f"Error deleting user profiles: {e}")
                return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
        
        # Delete from users table using VARCHAR user_id
        update_query = """
        DELETE FROM jeseci_academy.users 
        WHERE user_id = ANY(%s)
        """
        try:
            result = pg_manager.execute_query(update_query, (user_ids,), fetch=False)
        except Exception as e:
            logger.error(f"Error deleting users: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
    elif action == 'suspend':
        update_query = """
        UPDATE jeseci_academy.users 
        SET is_active = false, updated_at = NOW()
        WHERE user_id = ANY(%s)
        """
        try:
            result = pg_manager.execute_query(update_query, (user_ids,), fetch=False)
        except Exception as e:
            logger.error(f"Error suspending users: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
    elif action == 'activate':
        update_query = """
        UPDATE jeseci_academy.users 
        SET is_active = true, updated_at = NOW()
        WHERE user_id = ANY(%s)
        """
        try:
            result = pg_manager.execute_query(update_query, (user_ids,), fetch=False)
        except Exception as e:
            logger.error(f"Error activating users: {e}")
            return {"success": False, "error": f"Database error: {str(e)}", "code": "DATABASE_ERROR"}
    else:
        return {"success": False, "error": "Unknown action", "code": "INVALID_ACTION"}
    
    if result or result is not None:
        # Invalidate cache
        global cache_initialized
        cache_initialized = False
        
        return {"success": True, "users_affected": len(user_ids), "action": action}
    
    return {"success": False, "error": "Failed to perform action", "code": "ACTION_ERROR"}
