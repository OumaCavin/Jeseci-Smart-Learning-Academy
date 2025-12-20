#!/usr/bin/env python3
"""
Create Admin User Script for Jeseci Smart Learning Companion
This script uses the API to create an admin user safely
"""

import requests
import sys

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"

def create_admin():
    print("🚀 Creating Admin User via API...")
    print("=" * 50)

    # Matches the User model in sqlite_models.py
    payload = {
        "username": "cavin_admin",
        "email": "cavin@jeseci.com", 
        "password": "secure_password_123",
        "first_name": "Cavin",
        "last_name": "Admin"
    }
    
    try:
        print(f"📧 Creating user: {payload['username']} ({payload['email']})")
        
        # Register the user via API
        resp = requests.post(f"{API_URL}/auth/register", json=payload, timeout=10)
        
        if resp.status_code in [200, 201]:
            print(f"✅ Success! Admin '{payload['username']}' created successfully.")
            print(f"🔑 Password: {payload['password']}")
            print(f"📧 Email: {payload['email']}")
            
            # Test login
            login_data = {
                "username": payload['username'],
                "password": payload['password']
            }
            login_resp = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
            
            if login_resp.status_code == 200:
                print("✅ Login test successful!")
                return True
            else:
                print("⚠️ User created but login test failed")
                
        elif resp.status_code == 400:
            # Check if it's because user already exists
            resp_text = resp.text.lower()
            if "exists" in resp_text or "already" in resp_text:
                print(f"⚠️  User '{payload['username']}' already exists.")
                print(f"🔑 Password: {payload['password']}")
                print(f"📧 Email: {payload['email']}")
                
                # Test login with existing user
                login_data = {
                    "username": payload['username'],
                    "password": payload['password']
                }
                login_resp = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
                
                if login_resp.status_code == 200:
                    print("✅ Existing user login test successful!")
                    return True
                else:
                    print("❌ Login test failed for existing user")
                    print(f"Response: {login_resp.text}")
            else:
                print(f"❌ Registration failed: {resp.text}")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Cannot connect to API")
        print("💡 Hint: Is the backend running?")
        print("   Run: uvicorn main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: API is not responding")
        print("💡 Hint: Check if the backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    return False

def test_api_connection():
    """Test if the API is running"""
    try:
        resp = requests.get(f"{API_URL}/auth/ping", timeout=5)
        print("✅ API connection successful")
        return True
    except:
        print("❌ API connection failed")
        print("💡 Start the backend with: uvicorn main:app --reload")
        return False

if __name__ == "__main__":
    print("🎓 Jeseci Smart Learning Companion - Admin Creation")
    print("=" * 60)
    
    # Test API connection first
    if not test_api_connection():
        sys.exit(1)
    
    # Create admin user
    success = create_admin()
    
    if success:
        print("\n🎉 Admin creation completed successfully!")
    else:
        print("\n❌ Admin creation failed. Please check the error messages above.")