#!/usr/bin/env python3
"""
Test script for admin user creation
"""

import sys
import os

# Add workspace to path
sys.path.append('/workspace')

def test_admin_creation():
    """Test the admin creation function"""
    try:
        # Import the function directly
        from create_admin import create_admin_user
        
        print("🚀 Testing admin user creation...")
        user = create_admin_user()
        print("✅ Admin creation test successful!")
        print(f"👤 Created user: {user.username} ({user.email})")
        return True
        
    except Exception as e:
        print(f"❌ Error during admin creation test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_list_admins():
    """Test the admin listing function"""
    try:
        # Import the function directly
        from create_admin import list_admin_users
        
        print("🚀 Testing admin user listing...")
        list_admin_users()
        print("✅ Admin listing test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error during admin listing test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎓 Jeseci Admin Creation Tests")
    print("=" * 40)
    
    # Test admin creation
    success1 = test_admin_creation()
    print()
    
    # Test admin listing
    success2 = test_list_admins()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed.")