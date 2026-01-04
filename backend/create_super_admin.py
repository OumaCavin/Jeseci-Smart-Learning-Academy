#!/usr/bin/env python3
"""
Create Super Admin User Script
Jeseci Smart Learning Academy

This script creates the first super administrator user for the platform.
Run this once during initial setup to create the master admin account.

Usage:
    python create_super_admin.py --username admin --email admin@jeseci.com --password secure123

Author: Cavin Otieno
"""

import os
import sys
import argparse
import getpass
from datetime import datetime

# CRITICAL: Load environment variables FIRST, before any imports
# This ensures all modules see the correct environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', '.env'))

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import user_auth as auth_module

# Define AdminRole locally to avoid FastAPI dependency
class AdminRole:
    """Admin role constants"""
    STUDENT = "student"
    ADMIN = "admin"
    CONTENT_ADMIN = "content_admin"
    USER_ADMIN = "user_admin"
    SUPER_ADMIN = "super_admin"

def create_super_admin(username: str, email: str, password: str, 
                      first_name: str = "", last_name: str = "") -> bool:
    """
    Create a super administrator user.
    
    Args:
        username: Admin username
        email: Admin email
        password: Admin password
        first_name: First name (optional)
        last_name: Last name (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("Creating super administrator user...")
        
        result = auth_module.register_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_admin=True,
            admin_role=AdminRole.SUPER_ADMIN
        )
        
        if result["success"]:
            print(f"✅ Super admin user created successfully!")
            print(f"   Username: {result['username']}")
            print(f"   Email: {result['email']}")
            print(f"   User ID: {result['user_id']}")
            print(f"   Admin Role: {result['admin_role']}")
            print(f"   Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"❌ Failed to create super admin user: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating super admin user: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Create super administrator user')
    parser.add_argument('--username', required=True, help='Admin username')
    parser.add_argument('--email', required=True, help='Admin email address')
    parser.add_argument('--password', help='Admin password (will prompt if not provided)')
    parser.add_argument('--first-name', default="", help='First name (optional)')
    parser.add_argument('--last-name', default="", help='Last name (optional)')
    parser.add_argument('--force', action='store_true', help='Force creation without confirmation')
    
    args = parser.parse_args()
    
    # Get password securely if not provided
    if not args.password:
        args.password = getpass.getpass("Enter admin password: ")
        confirm_password = getpass.getpass("Confirm admin password: ")
        
        if args.password != confirm_password:
            print("❌ Passwords do not match!")
            sys.exit(1)
    
    # Validate password strength
    if len(args.password) < 8:
        print("❌ Password must be at least 8 characters long!")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("SUPER ADMIN USER CREATION")
    print("="*50)
    print(f"Username: {args.username}")
    print(f"Email: {args.email}")
    print(f"First Name: {args.first_name or '(not set)'}")
    print(f"Last Name: {args.last_name or '(not set)'}")
    print(f"Role: {AdminRole.SUPER_ADMIN}")
    print("="*50)
    
    # Confirm creation
    if not args.force:
        confirm = input("\nCreate this super admin user? (y/N): ").lower().strip()
        if confirm != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    # Create the user
    success = create_super_admin(
        username=args.username,
        email=args.email,
        password=args.password,
        first_name=args.first_name,
        last_name=args.last_name
    )
    
    if success:
        print("\n🎉 Super admin user creation completed successfully!")
        print("\nYou can now log in to the admin interface with these credentials.")
        print("\nAdmin endpoints are available at:")
        print("  - Dashboard: GET /admin/dashboard")
        print("  - User Management: GET /admin/users")
        print("  - API Documentation: /admin/docs")
    else:
        print("\n❌ Super admin user creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()