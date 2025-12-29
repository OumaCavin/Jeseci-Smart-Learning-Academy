# In-memory admin user storage for Jaclang backend
# This module provides persistent storage for admin users across requests

import json
import os
import threading

# In-memory storage
admin_users_store = {}
admin_users_lock = threading.Lock()

# File path for persistence
DATA_FILE = "data/admin_users.json"

def load_admin_users():
    """Load admin users from file if it exists"""
    global admin_users_store
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                admin_users_store = json.load(f)
    except Exception as e:
        print(f"Error loading admin users: {e}")
        admin_users_store = {}

def save_admin_users():
    """Save admin users to file"""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(admin_users_store, f, indent=2)
    except Exception as e:
        print(f"Error saving admin users: {e}")

def initialize_admin_store():
    """Initialize the admin user store with default admin"""
    global admin_users_store
    load_admin_users()
    
    # If store is empty, add default admin
    if not admin_users_store:
        admin_users_store = {
            "user_cavin_78a5d49f": {
                "user_id": "user_cavin_78a5d49f",
                "username": "cavin",
                "email": "otienocavin2025@gmail.com",
                "first_name": "",
                "last_name": "",
                "is_admin": True,
                "admin_role": "super_admin",
                "is_active": True,
                "created_at": "2025-12-01T10:00:00Z",
                "last_login": "2025-12-29T11:08:26Z"
            }
        }
        save_admin_users()
    
    return admin_users_store

def get_all_admin_users():
    """Get all admin users from store"""
    with admin_users_lock:
        return list(admin_users_store.values())

def get_admin_user_by_id(user_id):
    """Get a specific admin user by ID"""
    with admin_users_lock:
        return admin_users_store.get(user_id)

def get_admin_user_by_email(email):
    """Get a specific admin user by email"""
    with admin_users_lock:
        for user in admin_users_store.values():
            if user.get('email', '').lower() == email.lower():
                return user
    return None

def search_admin_users(query, include_inactive=False, admin_only=False):
    """Search admin users by query string"""
    with admin_users_lock:
        results = []
        query_lower = query.lower() if query else ""
        
        for user in admin_users_store.values():
            # Filter by inactive status
            if not include_inactive and not user.get('is_active', True):
                continue
            
            # Filter by admin only
            if admin_only and not user.get('is_admin', False):
                continue
            
            # Search in username, email, first_name, last_name
            if query_lower:
                searchable = f"{user.get('username', '')} {user.get('email', '')} {user.get('first_name', '')} {user.get('last_name', '')}".lower()
                if query_lower not in searchable:
                    continue
            
            results.append(user)
        
        return results

def create_admin_user(username, email, password, admin_role, first_name="", last_name=""):
    """Create a new admin user"""
    import datetime
    import uuid
    
    with admin_users_lock:
        # Check if user already exists
        for user in admin_users_store.values():
            if user.get('email', '').lower() == email.lower():
                return {"success": False, "error": "User with this email already exists", "code": "DUPLICATE_EMAIL"}
            if user.get('username', '').lower() == username.lower():
                return {"success": False, "error": "Username already exists", "code": "DUPLICATE_USERNAME"}
        
        # Generate user ID
        timestamp = str(int(datetime.datetime.now().timestamp()))
        user_id = f"user_{username}_{timestamp[0:8]}"
        
        # Create user
        new_user = {
            "user_id": user_id,
            "username": username,
            "email": email.lower(),
            "password": password,  # In production, this should be hashed
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": True,
            "admin_role": admin_role,
            "is_active": True,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_login": None
        }
        
        admin_users_store[user_id] = new_user
        save_admin_users()
        
        # Return user without password
        safe_user = {k: v for k, v in new_user.items() if k != 'password'}
        return {"success": True, "user": safe_user, "message": "Admin user created successfully"}

def update_admin_user(user_id, updates):
    """Update an existing admin user"""
    with admin_users_lock:
        if user_id not in admin_users_store:
            return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
        
        # Update user fields
        for key, value in updates.items():
            if key not in ['user_id', 'created_at']:
                admin_users_store[user_id][key] = value
        
        save_admin_users()
        return {"success": True, "message": "User updated successfully"}

def bulk_admin_action(user_ids, action, reason=""):
    """Perform bulk action on admin users"""
    with admin_users_lock:
        affected = 0
        
        for user_id in user_ids:
            if user_id in admin_users_store:
                if action == 'suspend':
                    admin_users_store[user_id]['is_active'] = False
                elif action == 'activate':
                    admin_users_store[user_id]['is_active'] = True
                elif action == 'delete':
                    del admin_users_store[user_id]
                
                affected += 1
        
        if affected > 0:
            save_admin_users()
        
        return {"success": True, "users_affected": affected, "action": action}
