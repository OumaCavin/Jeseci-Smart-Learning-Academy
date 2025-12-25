#!/usr/bin/env python3
"""
Test Suite for Quiz Management and Analytics Admin Interface (Phase 3)
Jeseci Smart Learning Academy - Admin Interface

This test suite covers all the quiz management and analytics features including:
- Quiz creation and management
- Question bank administration  
- Assessment systems
- Analytics dashboards
- User performance metrics
- Content performance analysis
- System health monitoring

Author: Matrix Agent
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from main import app

# Create test client
client = TestClient(app)

# Test data fixtures
@pytest.fixture
def mock_admin_user():
    """Mock admin user for testing"""
    return {
        "user_id": "admin_test_001",
        "username": "test_admin",
        "email": "admin@test.com",
        "is_admin": True,
        "admin_role": "SUPER_ADMIN",
        "first_name": "Test",
        "last_name": "Admin"
    }

@pytest.fixture
def mock_admin_token():
    """Mock JWT token for admin authentication"""
    return "Bearer mock_admin_jwt_token_123"

@pytest.fixture
def sample_quiz_data():
    """Sample quiz data for testing"""
    return {
        "title": "Python Fundamentals Quiz",
        "description": "Test your knowledge of Python basics",
        "course_id": "course_python_101",
        "difficulty": "beginner",
        "time_limit": 30,
        "passing_score": 70,
        "question_ids": ["q1", "q2", "q3"],
        "tags": ["python", "programming", "basics"]
    }

@pytest.fixture
def sample_question_data():
    """Sample question data for testing"""
    return {
        "question_text": "What is the correct way to create a list in Python?",
        "question_type": "multiple_choice",
        "options": [
            "list = []",
            "list = ()",
            "list = {}",
            "list = ''"
        ],
        "correct_answer": 0,
        "explanation": "In Python, lists are created using square brackets []",
        "difficulty": "beginner",
        "topic": "data_structures",
        "estimated_time": 60,
        "tags": ["python", "lists", "data_structures"]
    }

# =============================================================================
# Quiz Management Tests
# =============================================================================

class TestQuizManagement:
    """Test quiz creation and management functionality"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_quizzes_success(self, mock_admin_auth, mock_admin_user):
        """Test successful quiz retrieval"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/quiz/",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "quizzes" in data
        assert isinstance(data["quizzes"], list)
    
    @patch('admin_auth.get_current_admin_user')
    def test_create_quiz_success(self, mock_admin_auth, mock_admin_user, sample_quiz_data):
        """Test successful quiz creation"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/admin/quiz/create",
            headers={"Authorization": "Bearer mock_token"},
            json=sample_quiz_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["quiz"]["title"] == sample_quiz_data["title"]
        assert "quiz_id" in data["quiz"]
    
    @patch('admin_auth.get_current_admin_user')
    def test_update_quiz_success(self, mock_admin_auth, mock_admin_user):
        """Test successful quiz update"""
        mock_admin_auth.return_value = mock_admin_user
        
        quiz_id = "quiz_123"
        update_data = {
            "title": "Updated Python Quiz",
            "difficulty": "intermediate"
        }
        
        response = client.put(
            f"/admin/quiz/{quiz_id}",
            headers={"Authorization": "Bearer mock_token"},
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["quiz"]["title"] == update_data["title"]
    
    @patch('admin_auth.get_current_admin_user')
    def test_delete_quiz_success(self, mock_admin_auth, mock_admin_user):
        """Test successful quiz deletion"""
        mock_admin_auth.return_value = mock_admin_user
        
        quiz_id = "quiz_to_delete"
        
        response = client.delete(
            f"/admin/quiz/{quiz_id}",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Quiz deleted successfully"

# =============================================================================
# Question Management Tests
# =============================================================================

class TestQuestionManagement:
    """Test question bank and question management functionality"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_questions_success(self, mock_admin_auth, mock_admin_user):
        """Test successful question retrieval"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/quiz/questions",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "questions" in data
        assert isinstance(data["questions"], list)
    
    @patch('admin_auth.get_current_admin_user')
    def test_create_question_success(self, mock_admin_auth, mock_admin_user, sample_question_data):
        """Test successful question creation"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/admin/quiz/questions",
            headers={"Authorization": "Bearer mock_token"},
            json=sample_question_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["question"]["question_text"] == sample_question_data["question_text"]
        assert "question_id" in data["question"]
    
    @patch('admin_auth.get_current_admin_user')
    def test_bulk_create_questions_success(self, mock_admin_auth, mock_admin_user):
        """Test successful bulk question creation"""
        mock_admin_auth.return_value = mock_admin_user
        
        bulk_data = {
            "questions": [
                {
                    "question_text": "What is Python?",
                    "question_type": "multiple_choice",
                    "options": ["Language", "Snake", "Tool", "Framework"],
                    "correct_answer": 0,
                    "topic": "python_basics"
                },
                {
                    "question_text": "What is a variable?",
                    "question_type": "multiple_choice", 
                    "options": ["Storage", "Function", "Loop", "Class"],
                    "correct_answer": 0,
                    "topic": "variables"
                }
            ]
        }
        
        response = client.post(
            "/admin/quiz/questions/bulk",
            headers={"Authorization": "Bearer mock_token"},
            json=bulk_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["questions"]) == 2
        assert data["created_count"] == 2

# =============================================================================
# Assessment Management Tests
# =============================================================================

class TestAssessmentManagement:
    """Test assessment and evaluation functionality"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_assessments_success(self, mock_admin_auth, mock_admin_user):
        """Test successful assessment retrieval"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/quiz/assessments",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "assessments" in data
    
    @patch('admin_auth.get_current_admin_user')
    def test_create_assessment_success(self, mock_admin_auth, mock_admin_user):
        """Test successful assessment creation"""
        mock_admin_auth.return_value = mock_admin_user
        
        assessment_data = {
            "title": "Mid-term Python Assessment",
            "description": "Comprehensive Python assessment",
            "quiz_ids": ["quiz_1", "quiz_2", "quiz_3"],
            "total_time": 120,
            "passing_criteria": {
                "minimum_score": 75,
                "required_quizzes": 2
            },
            "schedule": {
                "available_from": "2025-01-15T09:00:00Z",
                "available_until": "2025-01-22T17:00:00Z"
            }
        }
        
        response = client.post(
            "/admin/quiz/assessments",
            headers={"Authorization": "Bearer mock_token"},
            json=assessment_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["assessment"]["title"] == assessment_data["title"]
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_assessment_submissions_success(self, mock_admin_auth, mock_admin_user):
        """Test successful assessment submissions retrieval"""
        mock_admin_auth.return_value = mock_admin_user
        
        assessment_id = "assessment_123"
        
        response = client.get(
            f"/admin/quiz/assessments/{assessment_id}/submissions",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "submissions" in data
        assert "statistics" in data

# =============================================================================
# Analytics Dashboard Tests
# =============================================================================

class TestAnalyticsDashboard:
    """Test analytics dashboard and metrics functionality"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_analytics_overview_success(self, mock_admin_auth, mock_admin_user):
        """Test successful analytics overview retrieval"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/analytics/overview",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data
        assert "charts" in data
        assert "kpis" in data
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_user_analytics_success(self, mock_admin_auth, mock_admin_user):
        """Test successful user analytics retrieval"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/analytics/users",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user_metrics" in data
        assert "engagement_data" in data
        assert "demographics" in data
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_content_performance_success(self, mock_admin_auth, mock_admin_user):
        """Test successful content performance analytics"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/analytics/content",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "course_analytics" in data
        assert "quiz_analytics" in data
        assert "content_effectiveness" in data
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_learning_progress_analytics_success(self, mock_admin_auth, mock_admin_user):
        """Test successful learning progress analytics"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/analytics/learning-progress",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "completion_rates" in data
        assert "progress_trends" in data
        assert "learning_paths_analytics" in data

# =============================================================================
# System Analytics Tests  
# =============================================================================

class TestSystemAnalytics:
    """Test system performance and health analytics"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_system_health_success(self, mock_admin_auth, mock_admin_user):
        """Test successful system health analytics"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/analytics/system/health",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "system_metrics" in data
        assert "performance_data" in data
        assert "health_status" in data
    
    @patch('admin_auth.get_current_admin_user')
    def test_get_api_usage_analytics_success(self, mock_admin_auth, mock_admin_user):
        """Test successful API usage analytics"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/admin/analytics/system/api-usage",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "api_metrics" in data
        assert "endpoint_usage" in data
        assert "response_times" in data

# =============================================================================
# Custom Analytics Tests
# =============================================================================

class TestCustomAnalytics:
    """Test custom analytics and reporting functionality"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_create_custom_report_success(self, mock_admin_auth, mock_admin_user):
        """Test successful custom report creation"""
        mock_admin_auth.return_value = mock_admin_user
        
        report_config = {
            "name": "Weekly Learning Report",
            "description": "Weekly summary of learning activities",
            "data_sources": ["user_progress", "quiz_results", "content_engagement"],
            "filters": {
                "date_range": {"start": "2025-01-01", "end": "2025-01-07"},
                "user_groups": ["all_users"],
                "content_types": ["courses", "quizzes"]
            },
            "visualization": "dashboard",
            "schedule": "weekly"
        }
        
        response = client.post(
            "/admin/analytics/reports",
            headers={"Authorization": "Bearer mock_token"},
            json=report_config
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["report"]["name"] == report_config["name"]
        assert "report_id" in data["report"]
    
    @patch('admin_auth.get_current_admin_user')
    def test_export_analytics_data_success(self, mock_admin_auth, mock_admin_user):
        """Test successful analytics data export"""
        mock_admin_auth.return_value = mock_admin_user
        
        export_config = {
            "data_type": "user_analytics",
            "format": "csv",
            "date_range": {"start": "2025-01-01", "end": "2025-01-31"},
            "include_fields": ["user_id", "progress", "quiz_scores", "time_spent"]
        }
        
        response = client.post(
            "/admin/analytics/export",
            headers={"Authorization": "Bearer mock_token"},
            json=export_config
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "export_url" in data
        assert "file_size" in data

# =============================================================================
# Security and Authorization Tests
# =============================================================================

class TestQuizAnalyticsSecurity:
    """Test security and authorization for quiz and analytics features"""
    
    def test_quiz_endpoints_require_authentication(self):
        """Test that quiz endpoints require authentication"""
        # Test without token
        response = client.get("/admin/quiz/")
        assert response.status_code == 401 or response.status_code == 403
        
        # Test with invalid token
        response = client.get(
            "/admin/quiz/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401 or response.status_code == 403
    
    def test_analytics_endpoints_require_authentication(self):
        """Test that analytics endpoints require authentication"""
        # Test without token
        response = client.get("/admin/analytics/overview")
        assert response.status_code == 401 or response.status_code == 403
        
        # Test with invalid token
        response = client.get(
            "/admin/analytics/overview",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401 or response.status_code == 403
    
    @patch('admin_auth.get_current_admin_user')
    def test_content_admin_can_access_quiz_features(self, mock_admin_auth):
        """Test that content admins can access quiz features"""
        mock_admin_auth.return_value = {
            "user_id": "content_admin_001",
            "username": "content_admin",
            "admin_role": "CONTENT_ADMIN"
        }
        
        response = client.get(
            "/admin/quiz/",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
    
    @patch('admin_auth.get_current_admin_user')
    def test_analytics_admin_can_access_analytics_features(self, mock_admin_auth):
        """Test that analytics admins can access analytics features"""
        mock_admin_auth.return_value = {
            "user_id": "analytics_admin_001", 
            "username": "analytics_admin",
            "admin_role": "ANALYTICS_ADMIN"
        }
        
        response = client.get(
            "/admin/analytics/overview",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200

# =============================================================================
# Integration Tests
# =============================================================================

class TestQuizAnalyticsIntegration:
    """Test integration between quiz and analytics systems"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_quiz_creation_updates_analytics(self, mock_admin_auth, mock_admin_user, sample_quiz_data):
        """Test that quiz creation is reflected in analytics"""
        mock_admin_auth.return_value = mock_admin_user
        
        # Create a quiz
        create_response = client.post(
            "/admin/quiz/create",
            headers={"Authorization": "Bearer mock_token"},
            json=sample_quiz_data
        )
        assert create_response.status_code == 200
        
        # Check that analytics reflect the new quiz
        analytics_response = client.get(
            "/admin/analytics/content",
            headers={"Authorization": "Bearer mock_token"}
        )
        assert analytics_response.status_code == 200
        
        # Verify quiz appears in content analytics
        analytics_data = analytics_response.json()
        assert "quiz_analytics" in analytics_data
    
    @patch('admin_auth.get_current_admin_user')
    def test_quiz_performance_analytics_integration(self, mock_admin_auth, mock_admin_user):
        """Test quiz performance data integration with analytics"""
        mock_admin_auth.return_value = mock_admin_user
        
        quiz_id = "quiz_performance_test"
        
        # Get quiz performance analytics
        response = client.get(
            f"/admin/analytics/quiz/{quiz_id}/performance",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "performance_metrics" in data
        assert "quiz_id" in data
        assert data["quiz_id"] == quiz_id

# =============================================================================
# Performance Tests
# =============================================================================

class TestQuizAnalyticsPerformance:
    """Test performance of quiz and analytics features"""
    
    @patch('admin_auth.get_current_admin_user')
    def test_large_dataset_analytics_performance(self, mock_admin_auth, mock_admin_user):
        """Test analytics performance with large datasets"""
        mock_admin_auth.return_value = mock_admin_user
        
        # Test with large date range
        response = client.get(
            "/admin/analytics/users",
            headers={"Authorization": "Bearer mock_token"},
            params={
                "start_date": "2024-01-01",
                "end_date": "2025-12-31",
                "limit": 10000
            }
        )
        
        assert response.status_code == 200
        # Response should complete within reasonable time
        # This is a basic test - in production, you'd measure actual response times
    
    @patch('admin_auth.get_current_admin_user')
    def test_bulk_quiz_operations_performance(self, mock_admin_auth, mock_admin_user):
        """Test performance of bulk quiz operations"""
        mock_admin_auth.return_value = mock_admin_user
        
        # Create many questions at once
        bulk_data = {
            "questions": [
                {
                    "question_text": f"Question {i}",
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": 0,
                    "topic": "bulk_test"
                } for i in range(100)
            ]
        }
        
        response = client.post(
            "/admin/quiz/questions/bulk",
            headers={"Authorization": "Bearer mock_token"},
            json=bulk_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["created_count"] == 100

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])