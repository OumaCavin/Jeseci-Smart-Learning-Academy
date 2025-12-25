#!/usr/bin/env python3
"""
Content Management Test Script - Phase 2
Jeseci Smart Learning Academy

This script tests the Phase 2 content management implementation including
course creation, learning path management, and AI content administration.

Usage:
    python test_content_management.py

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
CONTENT_ADMIN_USERNAME = "content_admin_test"
CONTENT_ADMIN_EMAIL = "content_admin@jeseci.com"
CONTENT_ADMIN_PASSWORD = "content_admin_123"

class ContentManagementTest:
    """Test suite for content management functionality"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.content_admin_token = None
        self.test_course_id = None
        self.test_path_id = None
        self.test_concept_id = None
        self.test_ai_content_id = None
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
    
    def create_content_admin(self) -> bool:
        """Create a content admin user for testing"""
        try:
            result = auth_module.register_user(
                username=CONTENT_ADMIN_USERNAME,
                email=CONTENT_ADMIN_EMAIL,
                password=CONTENT_ADMIN_PASSWORD,
                first_name="Content",
                last_name="Admin",
                is_admin=True,
                admin_role=AdminRole.CONTENT_ADMIN
            )
            
            if result["success"]:
                self.log_test("Create content admin user", True, 
                            f"User ID: {result['user_id']}")
                return True
            else:
                self.log_test("Create content admin user", False, result.get("error"))
                return False
                
        except Exception as e:
            self.log_test("Create content admin user", False, str(e))
            return False
    
    def authenticate_content_admin(self) -> bool:
        """Authenticate content admin user"""
        try:
            result = auth_module.authenticate_user(CONTENT_ADMIN_USERNAME, CONTENT_ADMIN_PASSWORD)
            
            if result["success"]:
                self.content_admin_token = result["access_token"]
                user_data = result["user"]
                
                # Verify admin status
                if (user_data.get("is_admin") and 
                    user_data.get("admin_role") == AdminRole.CONTENT_ADMIN):
                    self.log_test("Content admin authentication", True, 
                                f"Role: {user_data.get('admin_role')}")
                    return True
                else:
                    self.log_test("Content admin authentication", False, 
                                "User not recognized as content admin")
                    return False
            else:
                self.log_test("Content admin authentication", False, result.get("error"))
                return False
                
        except Exception as e:
            self.log_test("Content admin authentication", False, str(e))
            return False
    
    def test_create_course(self) -> bool:
        """Test course creation endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.content_admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "title": "Advanced Jac Walker Patterns",
                "description": "Deep dive into advanced Jac concepts including walker coordination, graph traversal optimization, and multi-walker systems",
                "domain": "Jac Programming",
                "difficulty": "advanced",
                "estimated_duration": 2400,
                "prerequisites": ["course_jac_fundamentals"],
                "learning_objectives": [
                    "Master advanced walker patterns",
                    "Understand graph traversal optimization",
                    "Build complex multi-walker systems"
                ],
                "tags": ["jaclang", "advanced", "walkers", "graph"],
                "is_published": False
            }
            
            response = requests.post(f"{self.base_url}/admin/content/courses", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("content_id"):
                    self.test_course_id = data.get("content_id")
                    self.log_test("Course creation", True, 
                                f"Created course: {self.test_course_id}")
                    return True
                else:
                    self.log_test("Course creation", False, 
                                "Invalid course creation response")
                    return False
            else:
                self.log_test("Course creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Course creation", False, str(e))
            return False
    
    def test_get_courses(self) -> bool:
        """Test course listing endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.content_admin_token}"}
            response = requests.get(f"{self.base_url}/admin/content/courses", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "content" in data:
                    course_count = len(data["content"])
                    self.log_test("Course listing", True, 
                                f"Retrieved {course_count} courses")
                    return True
                else:
                    self.log_test("Course listing", False, 
                                "Invalid course listing response")
                    return False
            else:
                self.log_test("Course listing", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Course listing", False, str(e))
            return False
    
    def test_update_course(self) -> bool:
        """Test course update endpoint"""
        if not self.test_course_id:
            self.log_test("Course update", False, "No test course available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.content_admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "course_id": self.test_course_id,
                "title": "Advanced Jac Walker Patterns - Updated",
                "is_published": True,
                "tags": ["jaclang", "advanced", "walkers", "updated"]
            }
            
            response = requests.put(f"{self.base_url}/admin/content/courses", 
                                  headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Course update", True, 
                                f"Updated course: {self.test_course_id}")
                    return True
                else:
                    self.log_test("Course update", False, 
                                "Course update response invalid")
                    return False
            else:
                self.log_test("Course update", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Course update", False, str(e))
            return False
    
    def test_create_learning_path(self) -> bool:
        """Test learning path creation endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.content_admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "title": "Full-Stack Jac Development",
                "description": "Complete learning path for graph-based Jac development with nodes and walkers",
                "category": "Jac Programming",
                "difficulty": "intermediate",
                "estimated_duration": 6000,
                "target_audience": "Intermediate programmers",
                "course_sequence": ["course_jac_fundamentals", "course_jac_nodes"],
                "prerequisites": [],
                "learning_outcomes": [
                    "Build complex graph-based applications",
                    "Deploy Jac walker systems to production",
                    "Integrate multiple walker coordination patterns"
                ],
                "is_published": False
            }
            
            response = requests.post(f"{self.base_url}/admin/content/learning-paths", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("content_id"):
                    self.test_path_id = data.get("content_id")
                    self.log_test("Learning path creation", True, 
                                f"Created path: {self.test_path_id}")
                    return True
                else:
                    self.log_test("Learning path creation", False, 
                                "Invalid path creation response")
                    return False
            else:
                self.log_test("Learning path creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Learning path creation", False, str(e))
            return False
    
    def test_create_concept(self) -> bool:
        """Test concept creation endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.content_admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "name": "Jac Walker Spawning",
                "display_name": "Walker Spawning and Lifecycle Management",
                "category": "Advanced Jac",
                "domain": "Jac Programming",
                "difficulty_level": "advanced",
                "description": "Understanding walker spawning patterns, lifecycle management, and multi-walker coordination",
                "detailed_description": "Jac walkers can be spawned dynamically to perform parallel operations on the graph...",
                "key_terms": ["walker", "spawn", "lifecycle", "coordination"],
                "learning_objectives": [
                    "Understand walker spawning syntax",
                    "Create custom walker spawners",
                    "Use walker coordination patterns effectively"
                ],
                "practical_applications": [
                    "Parallel graph traversal",
                    "Distributed computation",
                    "Multi-agent systems"
                ]
            }
            
            response = requests.post(f"{self.base_url}/admin/content/concepts", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("content_id"):
                    self.test_concept_id = data.get("content_id")
                    self.log_test("Concept creation", True, 
                                f"Created concept: {self.test_concept_id}")
                    return True
                else:
                    self.log_test("Concept creation", False, 
                                "Invalid concept creation response")
                    return False
            else:
                self.log_test("Concept creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Concept creation", False, str(e))
            return False
    
    def test_ai_content_generation(self) -> bool:
        """Test AI content generation endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.content_admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "content_type": "lesson",
                "concept_name": "Jac Node Attributes",
                "domain": "Jac Programming",
                "difficulty": "intermediate",
                "target_audience": "Jaclang learners",
                "learning_objectives": [
                    "Understand node attribute declarations",
                    "Compare with traditional class attributes",
                    "Use type annotations effectively"
                ],
                "context": "Focus on practical examples and graph structure benefits"
            }
            
            response = requests.post(f"{self.base_url}/admin/ai/generate", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("content_id"):
                    self.test_ai_content_id = data.get("content_id")
                    self.log_test("AI content generation", True, 
                                f"Generated AI content: {self.test_ai_content_id}")
                    return True
                else:
                    self.log_test("AI content generation", False, 
                                "Invalid AI generation response")
                    return False
            else:
                self.log_test("AI content generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI content generation", False, str(e))
            return False
    
    def test_ai_content_review(self) -> bool:
        """Test AI content review endpoint"""
        if not self.test_ai_content_id:
            self.log_test("AI content review", False, "No AI content to review")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.content_admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "content_id": self.test_ai_content_id,
                "status": "approved",
                "quality_score": 8.5,
                "quality_rating": "good",
                "reviewer_feedback": "Well-structured lesson with clear examples and good flow. Approved for publication.",
                "requires_revision": False
            }
            
            response = requests.put(f"{self.base_url}/admin/ai/review", 
                                  headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("AI content review", True, 
                                f"Reviewed AI content: {self.test_ai_content_id}")
                    return True
                else:
                    self.log_test("AI content review", False, 
                                "AI review response invalid")
                    return False
            else:
                self.log_test("AI content review", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI content review", False, str(e))
            return False
    
    def test_ai_usage_analytics(self) -> bool:
        """Test AI usage analytics endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.content_admin_token}"}
            response = requests.get(f"{self.base_url}/admin/ai/analytics?period=monthly", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "usage_statistics" in data:
                    self.log_test("AI usage analytics", True, 
                                f"Retrieved analytics for period: {data.get('period')}")
                    return True
                else:
                    self.log_test("AI usage analytics", False, 
                                "Invalid analytics response")
                    return False
            else:
                self.log_test("AI usage analytics", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI usage analytics", False, str(e))
            return False
    
    def test_bulk_content_operations(self) -> bool:
        """Test bulk content operations"""
        if not (self.test_course_id and self.test_concept_id):
            self.log_test("Bulk content operations", False, "No test content available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.content_admin_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "content_ids": [self.test_course_id],
                "action": "publish",
                "content_type": "course"
            }
            
            response = requests.post(f"{self.base_url}/admin/content/bulk-action", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Bulk content operations", True, 
                                "Bulk publish operation completed")
                    return True
                else:
                    self.log_test("Bulk content operations", False, 
                                "Bulk operation response invalid")
                    return False
            else:
                self.log_test("Bulk content operations", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk content operations", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all content management tests"""
        print("🧪 Starting Content Management Tests - Phase 2")
        print("=" * 60)
        
        # Run tests in sequence
        tests = [
            self.create_content_admin,
            self.authenticate_content_admin,
            self.test_create_course,
            self.test_get_courses,
            self.test_update_course,
            self.test_create_learning_path,
            self.test_create_concept,
            self.test_ai_content_generation,
            self.test_ai_content_review,
            self.test_ai_usage_analytics,
            self.test_bulk_content_operations
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Display summary
        print("=" * 60)
        print("📊 CONTENT MANAGEMENT TEST SUMMARY")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

def main():
    """Main test runner"""
    print("🚀 Content Management Test Suite - Phase 2")
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
    test_suite = ContentManagementTest()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All content management tests passed!")
        print("\nContent management features are working correctly:")
        print("   ✅ Course creation and management")
        print("   ✅ Learning path administration")
        print("   ✅ Concept management")
        print("   ✅ AI content generation and review")
        print("   ✅ Usage analytics and bulk operations")
        sys.exit(0)
    else:
        print("\n⚠️  Some content management tests failed.")
        print("   Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()