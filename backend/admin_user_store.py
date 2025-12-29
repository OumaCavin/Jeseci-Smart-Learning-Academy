# Admin user storage using PostgreSQL database
# Uses the existing User model from SQLAlchemy

import os
import threading
import datetime
from typing import Optional

# Import database utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))
from database import get_postgres_manager

# In-memory cache for quick lookups (synced with PostgreSQL)
admin_users_cache = {}
admin_users_lock = threading.Lock()
cache_initialized = False

def initialize_admin_store():
    """Initialize admin store by loading users from PostgreSQL"""
    global admin_users_cache, cache_initialized
    
    if cache_initialized:
        return
    
    with admin_users_lock:
        if cache_initialized:
            return
            
        # Load admin users from PostgreSQL
        pg_manager = get_postgres_manager()
        
        query = """
        SELECT u.user_id, u.username, u.email, u.is_admin, u.admin_role, 
               u.is_active, u.created_at, u.last_login_at,
               p.first_name, p.last_name
        FROM jeseci_academy.users u
        LEFT JOIN jeseci_academy.user_profile p ON u.user_id = p.user_id
        WHERE u.is_admin = true
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
                    "last_login": row.get('last_login_at').isoformat() if row.get('last_login_at') else None
                }
        
        cache_initialized = True

def get_all_admin_users():
    """Get all admin users from PostgreSQL"""
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
    """Search admin users in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Build dynamic query with positional parameters
    sql_conditions = ["u.is_admin = true"]
    params = []
    
    if not include_inactive:
        sql_conditions.append("u.is_active = true")
    if query:
        sql_conditions.append("(u.username ILIKE %s OR u.email ILIKE %s OR p.first_name ILIKE %s OR p.last_name ILIKE %s)")
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"])
    
    where_clause = " AND ".join(sql_conditions)
    
    search_query = f"""
    SELECT u.user_id, u.username, u.email, u.is_admin, u.admin_role, 
           u.is_active, u.created_at, u.last_login_at,
           p.first_name, p.last_name
    FROM jeseci_academy.users u
    LEFT JOIN jeseci_academy.user_profile p ON u.user_id = p.user_id
    WHERE {where_clause}
    ORDER BY u.created_at DESC
    """
    
    result = pg_manager.execute_query(search_query, params)
    
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
            "last_login": row.get('last_login_at').isoformat() if row.get('last_login_at') else None
        })
    
    return users

def create_admin_user(username, email, password, admin_role, first_name="", last_name=""):
    """Create a new admin user in PostgreSQL"""
    import hashlib
    
    pg_manager = get_postgres_manager()
    
    # Check for existing user using positional parameters
    check_query = """
    SELECT user_id FROM jeseci_academy.users 
    WHERE email = %s OR username = %s
    """
    existing = pg_manager.execute_query(check_query, (email, username))
    
    if existing:
        for row in existing:
            if row.get('email') == email:
                return {"success": False, "error": "User with this email already exists", "code": "DUPLICATE_EMAIL"}
            if row.get('username') == username:
                return {"success": False, "error": "Username already exists", "code": "DUPLICATE_USERNAME"}
    
    # Generate user ID
    timestamp = str(int(datetime.datetime.now().timestamp()))
    user_id = f"user_{username}_{timestamp[0:8]}"
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Insert new admin user into users table (without first_name/last_name)
    insert_user_query = """
    INSERT INTO jeseci_academy.users 
    (user_id, username, email, password_hash, is_admin, admin_role, is_active, created_at, updated_at)
    VALUES (%s, %s, %s, %s, true, %s, true, NOW(), NOW())
    """
    
    user_result = pg_manager.execute_query(insert_user_query, 
        (user_id, username, email, password_hash, admin_role), fetch=False)
    
    if user_result or user_result is not None:
        # Also insert into user_profile table for first_name/last_name
        if first_name or last_name:
            insert_profile_query = """
            INSERT INTO jeseci_academy.user_profile 
            (user_id, first_name, last_name, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON CONFLICT (user_id) DO UPDATE SET 
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                updated_at = NOW()
            """
            pg_manager.execute_query(insert_profile_query, (user_id, first_name, last_name), fetch=False)
        
        # Invalidate cache to force reload
        global cache_initialized
        cache_initialized = False
        
        return {
            "success": True, 
            "user": {
                "user_id": user_id,
                "username": username,
                "email": email,
                "admin_role": admin_role,
                "first_name": first_name,
                "last_name": last_name,
                "is_admin": True,
                "is_active": True,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "message": "Admin user created successfully"
        }
    
    return {"success": False, "error": "Failed to create user", "code": "INSERT_ERROR"}

def update_admin_user(user_id, updates):
    """Update an existing admin user in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Check if user exists
    check_query = "SELECT user_id FROM jeseci_academy.users WHERE user_id = %s"
    existing = pg_manager.execute_query(check_query, (user_id,))
    
    if not existing:
        return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
    
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
        pg_manager.execute_query(user_update_query, user_params, fetch=False)
    
    # Update profile table if needed
    if profile_fields:
        profile_set_clauses = []
        profile_params = [user_id]
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
            pg_manager.execute_query(profile_update_query, profile_params, fetch=False)
    
    # Invalidate cache
    global cache_initialized
    cache_initialized = False
    
    return {"success": True, "message": "User updated successfully"}

def bulk_admin_action(user_ids, action, reason=""):
    """Perform bulk action on admin users in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    if action == 'suspend':
        update_query = """
        UPDATE jeseci_academy.users 
        SET is_active = false, updated_at = NOW()
        WHERE user_id = ANY(%s)
        """
    elif action == 'activate':
        update_query = """
        UPDATE jeseci_academy.users 
        SET is_active = true, updated_at = NOW()
        WHERE user_id = ANY(%s)
        """
    elif action == 'delete':
        # Delete from profile first (foreign key)
        delete_profile = "DELETE FROM jeseci_academy.user_profile WHERE user_id = ANY(%s)"
        pg_manager.execute_query(delete_profile, (user_ids,), fetch=False)
        
        update_query = """
        DELETE FROM jeseci_academy.users 
        WHERE user_id = ANY(%s)
        """
    else:
        return {"success": False, "error": "Unknown action", "code": "INVALID_ACTION"}
    
    result = pg_manager.execute_query(update_query, (user_ids,), fetch=False)
    
    if result or result is not None:
        # Invalidate cache
        global cache_initialized
        cache_initialized = False
        
        return {"success": True, "users_affected": len(user_ids), "action": action}
    
    return {"success": False, "error": "Failed to perform action", "code": "ACTION_ERROR"}
