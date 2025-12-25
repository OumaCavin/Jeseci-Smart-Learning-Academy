#!/usr/bin/env python3
"""
Admin Interface Test Script
Jeseci Smart Learning Academy

This script tests the admin interface implementation to ensure all components
are working correctly. It tests authentication, authorization, and admin endpoints.

Usage:
    python test_admin_interface.py

Author: Cavin Otieno
"""

import os
import sys
import requests
import json
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import user_auth as auth_module
from admin_auth import AdminRole

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_ADMIN_USERNAME = "test_admin_user"
TEST_ADMIN_EMAIL = "test_admin@jeseci.com"
TEST_ADMIN_PASSWORD = "test_password_123"

class AdminInterfaceTest:
    """Test suite for admin interface functionality"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.test_user_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
    
    def create_test_admin(self) -> bool:
        """Create a test admin user"""
        try:
            result = auth_module.register_user(
                username=TEST_ADMIN_USERNAME,
                email=TEST_ADMIN_EMAIL,
                password=TEST_ADMIN_PASSWORD,
                first_name="Test",
                last_name="Admin",
                is_admin=True,
                admin_role=AdminRole.SUPER_ADMIN
            )
            
            if result["success"]:
                self.test_user_id = result["user_id"]
                self.log_test("Create test admin user", True, f"User ID: {self.test_user_id}")
                return True
            else:
                self.log_test("Create test admin user", False, result.get("error"))
                return False
                
        except Exception as e:
            self.log_test("Create test admin user", False, str(e))
            return False
    
    def test_admin_login(self) -> bool:
        """Test admin user authentication"""
        try:
            result = auth_module.authenticate_user(TEST_ADMIN_USERNAME, TEST_ADMIN_PASSWORD)
            
            if result["success"]:
                self.admin_token = result["access_token"]
                user_data = result["user"]
                
                # Verify admin status
                if user_data.get("is_admin") and user_data.get("admin_role") == AdminRole.SUPER_ADMIN:
                    self.log_test("Admin login and token generation", True, 
                                f"Role: {user_data.get('admin_role')}")
                    return True
                else:
                    self.log_test("Admin login and token generation", False, 
                                "User not recognized as admin")
                    return False
            else:
                self.log_test("Admin login and token generation", False, result.get("error"))
                return False
                
        except Exception as e:
            self.log_test("Admin login and token generation", False, str(e))
            return False
    
    def test_admin_dashboard(self) -> bool:
        """Test admin dashboard endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/admin/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "stats" in data:
                    self.log_test("Admin dashboard access", True, 
                                f"Got stats with {len(data['stats'])} categories")
                    return True
                else:
                    self.log_test("Admin dashboard access", False, 
                                "Invalid dashboard response format")
                    return False
            else:
                self.log_test("Admin dashboard access", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin dashboard access", False, str(e))
            return False
    
    def test_admin_user_list(self) -> bool:
        """Test admin user list endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "users" in data:
                    user_count = len(data["users"])
                    self.log_test("Admin user list access", True, 
                                f"Retrieved {user_count} users")
                    return True
                else:
                    self.log_test("Admin user list access", False, 
                                "Invalid user list response format")
                    return False
            else:
                self.log_test("Admin user list access", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin user list access", False, str(e))
            return False
    
    def test_admin_user_creation(self) -> bool:
        """Test admin user creation endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "username": "test_content_admin",
                "email": "content_admin@test.com",
                "password": "test_password_456",
                "admin_role": AdminRole.CONTENT_ADMIN,
                "first_name": "Test",
                "last_name": "Content Admin"
            }
            
            response = requests.post(f"{self.base_url}/admin/users/create", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("user_id"):
                    self.log_test("Admin user creation", True, 
                                f"Created user: {data.get('user_id')}")
                    return True
                else:
                    self.log_test("Admin user creation", False, 
                                "User creation response invalid")
                    return False
            else:
                self.log_test("Admin user creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin user creation", False, str(e))
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Test that non-admin users cannot access admin endpoints"""
        try:
            # Create regular user
            regular_result = auth_module.register_user(
                username="regular_user_test",
                email="regular@test.com",
                password="regular123",
                is_admin=False
            )
            
            if not regular_result["success"]:
                self.log_test("Unauthorized access prevention", False, 
                            "Could not create regular user for test")
                return False
            
            # Authenticate as regular user
            auth_result = auth_module.authenticate_user("regular_user_test", "regular123")
            if not auth_result["success"]:
                self.log_test("Unauthorized access prevention", False, 
                            "Could not authenticate regular user")
                return False
            
            # Try to access admin endpoint
            headers = {"Authorization": f"Bearer {auth_result['access_token']}"}
            response = requests.get(f"{self.base_url}/admin/dashboard", headers=headers)
            
            if response.status_code == 403:
                self.log_test("Unauthorized access prevention", True, 
                            "Regular user correctly denied admin access")
                return True
            else:
                self.log_test("Unauthorized access prevention", False, 
                            f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized access prevention", False, str(e))
            return False
    
    def test_token_validation(self) -> bool:
        """Test JWT token validation"""
        try:
            # Test invalid token
            headers = {"Authorization": "Bearer invalid_token_here"}
            response = requests.get(f"{self.base_url}/admin/dashboard", headers=headers)
            
            if response.status_code == 401:
                self.log_test("Token validation", True, 
                            "Invalid token correctly rejected")
                return True
            else:
                self.log_test("Token validation", False, 
                            f"Expected 401 for invalid token, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token validation", False, str(e))
            return False
    
    def cleanup_test_users(self):
        """Clean up test users created during testing"""
        try:
            # This would require a delete user endpoint
            # For now, just mark them as inactive
            if self.test_user_id:
                auth_module.suspend_user(self.test_user_id, True)
                print(f"🧹 Cleaned up test user: {self.test_user_id}")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def run_all_tests(self):
        """Run all tests and display results"""
        print("🧪 Starting Admin Interface Tests")
        print("=" * 50)
        
        # Run tests in sequence
        tests = [
            self.create_test_admin,
            self.test_admin_login,
            self.test_admin_dashboard,
            self.test_admin_user_list,
            self.test_admin_user_creation,
            self.test_unauthorized_access,
            self.test_token_validation
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Display summary
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        # Cleanup
        self.cleanup_test_users()
        
        return self.results['failed'] == 0

def main():
    """Main test runner"""
    print("🚀 Admin Interface Test Suite")
    print("Jeseci Smart Learning Academy\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the API server first.")
            print("   Run: python main.py")
            sys.exit(1)
    except Exception as e:
        print("❌ Cannot connect to server. Please start the API server first.")
        print("   Run: python main.py")
        sys.exit(1)
    
    # Run tests
    test_suite = AdminInterfaceTest()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Admin interface is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()