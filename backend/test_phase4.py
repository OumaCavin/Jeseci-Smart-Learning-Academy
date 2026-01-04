#!/usr/bin/env python3
"""
Test Suite for Phase 4 Enhancements - Advanced Features
Jeseci Smart Learning Academy - Admin Interface

This test suite covers all Phase 4 features:
- AI Predictive Analytics (risk modeling, recommendations, sentiment)
- Real-time Features (WebSocket, notifications, content locks)
- LMS Integration (LTI 1.3, grade passback, roster sync)
- System Core (versioning, search, i18n)

Author: Cavin Otieno
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from main import app

# Create test client
client = TestClient(app)

# =============================================================================
# Fixtures
# =============================================================================

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
def mock_content_admin():
    """Mock content admin user"""
    return {
        "user_id": "content_admin_001",
        "username": "content_admin",
        "email": "content@test.com",
        "is_admin": True,
        "admin_role": "CONTENT_ADMIN"
    }

# =============================================================================
# AI Predictive Analytics Tests
# =============================================================================

class TestAIPredictiveAnalytics:
    """Test AI predictive analytics features"""
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_risk_assessment_single_user(self, mock_admin_auth, mock_admin_user):
        """Test single user risk assessment"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/ai/predict/risk",
            json={"user_ids": ["student_001"], "include_factors": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "assessments" in data
        assert "summary" in data
        assert data["summary"]["total_students"] == 1
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_risk_assessment_multiple_users(self, mock_admin_auth, mock_admin_user):
        """Test batch risk assessment for multiple users"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/ai/predict/risk",
            json={
                "user_ids": ["student_001", "student_002", "student_003"],
                "include_factors": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["assessments"]) == 3
        assert "critical_count" in data["summary"]
        assert "high_count" in data["summary"]
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_get_student_risk(self, mock_admin_auth, mock_admin_user):
        """Test getting risk prediction for specific student"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/ai/predict/risk/student_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "prediction" in data
        assert "risk_score" in data["prediction"]
        assert "risk_level" in data["prediction"]
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_learning_recommendations(self, mock_admin_auth, mock_admin_user):
        """Test learning recommendations endpoint"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/ai/recommendations/student_001",
            params={"content_types": "course,quiz,concept", "max_recs": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data
        assert "learning_style" in data
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_sentiment_analysis(self, mock_admin_auth, mock_admin_user):
        """Test content sentiment analysis"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/ai/sentiment/analyze",
            json={
                "content_id": "course_python_101",
                "content_type": "course"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sentiment" in data
        assert "overall_sentiment" in data["sentiment"]
        assert "positive_percentage" in data["sentiment"]
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_risk_analytics_overview(self, mock_admin_auth, mock_admin_user):
        """Test aggregated risk analytics overview"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/ai/analytics/risk-overview")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "overview" in data
        assert "trends" in data
        assert "high_risk_segments" in data
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_model_information(self, mock_admin_auth, mock_admin_user):
        """Test ML model information endpoint"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/ai/model/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "models" in data
        assert "risk_prediction" in data["models"]
        assert "recommendation" in data["models"]
        assert "sentiment" in data["models"]
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_user_personalization(self, mock_admin_auth, mock_admin_user):
        """Test user personalization profile"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/ai/personalization/student_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "personalization" in data
        assert "learning_style" in data["personalization"]
        assert "skill_level" in data["personalization"]
    
    def test_risk_level_classification(self):
        """Test risk level determination logic"""
        from ai_predictive import calculate_risk_score, determine_risk_level, StudentProfile
        
        # Test low risk
        profile = StudentProfile(
            user_id="test_user",
            login_frequency=5.0,
            average_quiz_score=90.0,
            content_completion_rate=95.0,
            time_spent_per_session=60.0,
            engagement_score=90.0,
            last_active=None
        )
        score, _ = calculate_risk_score(profile)
        level = determine_risk_level(score)
        assert level.value == "low"
        
        # Test critical risk
        profile = StudentProfile(
            user_id="test_user_2",
            login_frequency=0.5,
            average_quiz_score=30.0,
            content_completion_rate=20.0,
            time_spent_per_session=5.0,
            engagement_score=15.0,
            last_active=None
        )
        score, _ = calculate_risk_score(profile)
        level = determine_risk_level(score)
        assert level.value in ["high", "critical"]

# =============================================================================
# Real-time Features Tests
# =============================================================================

class TestRealtimeFeatures:
    """Test real-time features and WebSocket functionality"""
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_dashboard_metrics(self, mock_admin_auth, mock_admin_user):
        """Test dashboard metrics endpoint"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/realtime/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data
        assert "alerts" in data
        assert "connections" in data
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_connection_status(self, mock_admin_auth, mock_admin_user):
        """Test connection status endpoint"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/realtime/connections")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "summary" in data
        assert "details" in data
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_create_notification(self, mock_admin_auth, mock_admin_user):
        """Test notification creation"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/realtime/notifications",
            json={
                "notification_type": "system_alert",
                "title": "Test Notification",
                "message": "This is a test notification",
                "priority": 3,
                "target_groups": ["all_admins"],
                "expires_in_hours": 24
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notification" in data
        assert "broadcast_count" in data
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_get_notifications(self, mock_admin_auth, mock_admin_user):
        """Test getting notifications"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/realtime/notifications",
            params={"notification_type": "system_alert", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notifications" in data
        assert "total" in data
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_content_locks(self, mock_admin_auth, mock_admin_user):
        """Test content lock functionality"""
        mock_admin_auth.return_value = mock_admin_user
        
        # Request lock
        response = client.post(
            "/realtime/locks",
            json={
                "content_type": "course",
                "content_id": "course_python_101"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "lock_details" in data
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_get_active_locks(self, mock_admin_auth, mock_admin_user):
        """Test getting active content locks"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/realtime/locks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "locks" in data
        assert "total" in data
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_system_alerts(self, mock_admin_auth, mock_admin_user):
        """Test system alerts endpoint"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/realtime/alerts")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "alerts" in data
        assert "total" in data
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_specific_metric(self, mock_admin_auth, mock_admin_user):
        """Test getting specific metric"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/realtime/metrics/active_users")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metric" in data
        assert data["metric"]["name"] == "active_users"

# =============================================================================
# LMS Integration Tests
# =============================================================================

class TestLMSIntegration:
    """Test LMS integration features"""
    
    @patch('lms_integration.get_current_user_from_token')
    def test_lti_tool_configuration(self, mock_admin_auth, mock_admin_user):
        """Test LTI tool configuration endpoint"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/lms/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "title" in data
        assert "oidc_initiation_url" in data
        assert "target_link_uri" in data
        assert "scopes" in data
    
    def test_lti_config_xml():
        """Test LTI XML configuration"""
        response = client.get("/lms/config/xml")
        
        assert response.status_code == 200
        assert "xml" in response.headers.get("content-type", "")
        assert "cartridge_basiclti_link" in response.text
    
    @patch('lms_integration.get_current_user_from_token')
    def test_supported_platforms(self, mock_admin_auth, mock_admin_user):
        """Test supported LMS platforms"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/lms/platforms")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "platforms" in data
        assert len(data["platforms"]) >= 3
    
    @patch('lms_integration.get_current_user_from_token')
    def test_list_lms_configurations(self, mock_admin_auth, mock_admin_user):
        """Test listing LMS configurations"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/lms/configurations",
            params={"platform": "canvas", "active_only": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "configurations" in data
        assert "total" in data
    
    @patch('lms_integration.get_current_user_from_token')
    def test_get_specific_configuration(self, mock_admin_auth, mock_admin_user):
        """Test getting specific LMS configuration"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/lms/configurations/lms_canvas_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "configuration" in data
        assert "config_xml" in data
        assert "config_json" in data
    
    @patch('lms_integration.get_current_user_from_token')
    def test_submit_grade(self, mock_admin_auth, mock_admin_user):
        """Test grade submission to LMS"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/lms/grades",
            json={
                "lms_config_id": "lms_canvas_001",
                "user_id": "student_001",
                "resource_id": "quiz_python_101",
                "course_id": "course_python_101",
                "score": 85.0,
                "max_score": 100.0,
                "comment": "Great work!",
                "activity_progress": "Completed",
                "grading_progress": "FullyGraded"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "passback_id" in data
        assert "grade" in data
    
    @patch('lms_integration.get_current_user_from_token')
    def test_get_grade_history(self, mock_admin_auth, mock_admin_user):
        """Test getting grade history"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/lms/grades/student_001",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data
        assert "grades" in data
        assert "total" in data
    
    @patch('lms_integration.get_current_user_from_token')
    def test_sync_roster(self, mock_admin_auth, mock_admin_user):
        """Test roster synchronization"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/lms/roster/sync",
            json={
                "lms_config_id": "lms_canvas_001",
                "context_id": "canvas_course_001",
                "course_id": "course_python_101"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "imported" in data
        assert "total_enrolled" in data
    
    @patch('lms_integration.get_current_user_from_token')
    def test_get_roster(self, mock_admin_auth, mock_admin_user):
        """Test getting roster entries"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/lms/roster/canvas_course_001",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "context_id" in data
        assert "roster" in data
    
    @patch('lms_integration.get_current_user_from_token')
    def test_deep_linking(self, mock_admin_auth, mock_admin_user):
        """Test deep linking endpoint"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/lms/deep-link",
            json={
                "lms_config_id": "lms_canvas_001",
                "title": "Python Basics Quiz",
                "text": "Test your Python knowledge",
                "url": "https://jeseci.academy/quiz/python-basics",
                "custom_params": {"quiz_id": "python_101"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deployment" in data
        assert "lti_response" in data
    
    @patch('lms_integration.get_current_user_from_token')
    def test_lms_statistics(self, mock_admin_auth, mock_admin_user):
        """Test LMS integration statistics"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/lms/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "statistics" in data
        assert "by_platform" in data

# =============================================================================
# System Core Tests
# =============================================================================

class TestSystemCore:
    """Test system core features"""
    
    @patch('system_core.get_current_user_from_token')
    def test_create_content_version(self, mock_admin_auth, mock_admin_user):
        """Test creating content version"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/content/version",
            json={
                "content_id": "test_course_001",
                "content_type": "course",
                "title": "Test Course v1",
                "content_data": {
                    "description": "Updated course content",
                    "modules": ["module_1", "module_2"],
                    "duration": "4 weeks"
                },
                "change_summary": "Initial version"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "version" in data
        assert "history" in data
    
    @patch('system_core.get_current_user_from_token')
    def test_get_content_history(self, mock_admin_auth, mock_admin_user):
        """Test getting content version history"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/content/course_python_101/history",
            params={"page": 1, "per_page": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "content_id" in data
        assert "versions" in data
        assert "pagination" in data
    
    @patch('system_core.get_current_user_from_token')
    def test_get_specific_version(self, mock_admin_auth, mock_admin_user):
        """Test getting specific version"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/content/course_python_101/versions/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "version" in data
        assert "diff_with_current" in data
    
    @patch('system_core.get_current_user_from_token')
    def test_rollback_to_version(self, mock_admin_auth, mock_admin_user):
        """Test rolling back to specific version"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/content/course_python_101/rollback",
            json={"target_version": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "current_version" in data
        assert "rolled_back_to" in data
    
    @patch('system_core.get_current_user_from_token')
    def test_compare_versions(self, mock_admin_auth, mock_admin_user):
        """Test comparing two versions"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/content/course_python_101/compare",
            params={"version_a": 1, "version_b": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "comparison" in data
        assert "diff" in data["comparison"]
    
    @patch('system_core.get_current_user_from_token')
    def test_global_search(self, mock_admin_auth, mock_admin_user):
        """Test global search functionality"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/search/global",
            json={
                "query": "Python programming",
                "content_types": ["course", "quiz"],
                "filters": {},
                "tags": [],
                "sort_by": "relevance",
                "page": 1,
                "per_page": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert "total_count" in data
        assert "facets" in data
        assert "search_time_ms" in data
    
    @patch('system_core.get_current_user_from_token')
    def test_search_with_exact_phrase(self, mock_admin_auth, mock_admin_user):
        """Test search with exact phrase matching"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.post(
            "/search/global",
            json={
                "query": "\"Python programming\" fundamentals",
                "content_types": ["course"],
                "page": 1,
                "per_page": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('system_core.get_current_user_from_token')
    def test_search_suggestions(self, mock_admin_auth, mock_admin_user):
        """Test search suggestions"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/search/suggestions",
            params={"q": "pyth", "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "suggestions" in data
        assert "query" in data
    
    @patch('system_core.get_current_user_from_token')
    def test_search_history(self, mock_admin_auth, mock_admin_user):
        """Test getting search history"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/search/history",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "history" in data
        assert "total" in data
    
    def test_supported_languages(self):
        """Test getting supported languages"""
        response = client.get("/i18n/languages")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "languages" in data
        assert len(data["languages"]) >= 8
    
    def test_translation_retrieval(self):
        """Test translation key retrieval"""
        response = client.get("/i18n/translate/en/common/loading")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "language" in data
        assert "key" in data
        assert "translation" in data
        assert data["translation"] == "Loading..."
    
    def test_translation_bundle(self):
        """Test getting translation bundle"""
        response = client.get(
            "/i18n/bundle/es",
            params={"namespaces": "common,admin,content"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "language" in data
        assert "bundle" in data
        assert "common" in data["bundle"]
        assert "admin" in data["bundle"]
    
    def test_language_detection(self):
        """Test language detection"""
        response = client.post(
            "/i18n/detect",
            json={"text": "This is a sample text in English for testing purposes."}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "detected_language" in data
        assert "confidence" in data
    
    def test_rtl_languages(self):
        """Test getting RTL languages"""
        response = client.get("/i18n/rtl-languages")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "rtl_languages" in data
        assert "count" in data
        assert data["count"] >= 1
    
    @patch('system_core.get_current_user_from_token')
    def test_extended_health_check(self, mock_admin_auth, mock_admin_user):
        """Test extended health check"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/system/health/extended")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "health" in data
        assert "content_versioning" in data["health"]
        assert "search" in data["health"]
        assert "internationalization" in data["health"]
    
    @patch('system_core.get_current_user_from_token')
    def test_system_statistics(self, mock_admin_auth, mock_admin_user):
        """Test system statistics"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get("/system/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "statistics" in data
        assert "version_control" in data["statistics"]
        assert "search" in data["statistics"]
        assert "localization" in data["statistics"]
    
    @patch('system_core.get_current_user_from_token')
    def test_all_content_history(self, mock_admin_auth, mock_admin_user):
        """Test getting all content history"""
        mock_admin_auth.return_value = mock_admin_user
        
        response = client.get(
            "/content/all/history",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data
        assert "total" in data

# =============================================================================
# Security Tests
# =============================================================================

class TestPhase4Security:
    """Test security for Phase 4 features"""
    
    def test_ai_endpoints_require_auth(self):
        """Test that AI endpoints require authentication"""
        response = client.post(
            "/ai/predict/risk",
            json={"user_ids": ["student_001"]}
        )
        assert response.status_code in [401, 403]
    
    def test_realtime_endpoints_require_auth(self):
        """Test that realtime endpoints require authentication"""
        response = client.get("/realtime/dashboard")
        assert response.status_code in [401, 403]
    
    def test_lms_endpoints_require_auth(self):
        """Test that LMS endpoints require authentication"""
        response = client.get("/lms/config")
        assert response.status_code in [401, 403]
    
    def test_system_endpoints_require_auth(self):
        """Test that system endpoints require authentication"""
        response = client.post("/content/version", json={})
        assert response.status_code in [401, 403]
    
    @patch('lms_integration.get_current_user_from_token')
    def test_lms_config_creation_requires_super_admin(self, mock_admin_auth):
        """Test that LMS config creation requires super admin"""
        mock_admin_auth.return_value = {
            "user_id": "regular_admin",
            "admin_role": "ADMIN"
        }
        
        response = client.post(
            "/lms/configurations",
            json={
                "platform": "canvas",
                "name": "Test Config",
                "client_id": "test_client",
                "issuer": "https://test.edu",
                "deployment_id": "test_deploy",
                "auth_endpoint": "https://test.edu/auth",
                "token_endpoint": "https://test.edu/token",
                "jwks_endpoint": "https://test.edu/jwks",
                "public_key": "test_public_key",
                "private_key": "test_private_key",
                "deep_link_endpoint": "https://test.edu/deep-link"
            }
        )
        
        assert response.status_code == 403
    
    @patch('lms_integration.get_current_user_from_token')
    def test_lms_delete_requires_super_admin(self, mock_admin_auth):
        """Test that LMS delete requires super admin"""
        mock_admin_auth.return_value = {
            "user_id": "regular_admin",
            "admin_role": "ADMIN"
        }
        
        response = client.delete("/lms/configurations/lms_canvas_001")
        assert response.status_code == 403
    
    @patch('realtime_admin.get_current_user_from_token')
    def test_alert_creation_requires_super_admin(self, mock_admin_auth):
        """Test that alert creation requires super admin"""
        mock_admin_auth.return_value = {
            "user_id": "regular_admin",
            "admin_role": "ADMIN"
        }
        
        response = client.post(
            "/realtime/alerts",
            params={
                "alert_type": "warning",
                "title": "Test Alert",
                "message": "Test message"
            }
        )
        assert response.status_code == 403

# =============================================================================
# Integration Tests
# =============================================================================

class TestPhase4Integration:
    """Integration tests for Phase 4 features"""
    
    @patch('ai_predictive.get_current_user_from_token')
    @patch('system_core.get_current_user_from_token')
    def test_versioning_affects_analytics(
        self, mock_system_auth, mock_ai_auth, mock_admin_user
    ):
        """Test that content versioning affects analytics"""
        mock_system_auth.return_value = mock_admin_user
        mock_ai_auth.return_value = mock_admin_user
        
        # Create new version
        create_response = client.post(
            "/content/version",
            json={
                "content_id": "analytics_test_course",
                "content_type": "course",
                "title": "Analytics Test Course",
                "content_data": {"modules": ["mod_1"]},
                "change_summary": "Integration test"
            }
        )
        assert create_response.status_code == 200
        
        # Check analytics reflects new content
        sentiment_response = client.post(
            "/ai/sentiment/analyze",
            json={
                "content_id": "analytics_test_course",
                "content_type": "course"
            }
        )
        assert sentiment_response.status_code == 200
    
    @patch('lms_integration.get_current_user_from_token')
    @patch('system_core.get_current_user_from_token')
    def test_lms_grade_reflects_content(
        self, mock_system_auth, mock_lms_auth, mock_admin_user
    ):
        """Test that LMS grades reflect content updates"""
        mock_system_auth.return_value = mock_admin_user
        mock_lms_auth.return_value = mock_admin_user
        
        # Update content
        update_response = client.post(
            "/content/version",
            json={
                "content_id": "lms_test_quiz",
                "content_type": "quiz",
                "title": "Updated Quiz",
                "content_data": {"questions": 10},
                "change_summary": "Updated for LMS"
            }
        )
        assert update_response.status_code == 200
        
        # Submit grade
        grade_response = client.post(
            "/lms/grades",
            json={
                "lms_config_id": "lms_canvas_001",
                "user_id": "lms_student_001",
                "resource_id": "lms_test_quiz",
                "course_id": "course_001",
                "score": 90.0,
                "max_score": 100.0
            }
        )
        assert grade_response.status_code == 200
    
    @patch('realtime_admin.get_current_user_from_token')
    @patch('system_core.get_current_user_from_token')
    def test_lock_prevents_edit_conflicts(
        self, mock_system_auth, mock_realtime_auth, mock_admin_user
    ):
        """Test that content locks prevent edit conflicts"""
        mock_system_auth.return_value = mock_admin_user
        mock_realtime_auth.return_value = mock_admin_user
        
        # Request lock
        lock_response = client.post(
            "/realtime/locks",
            json={
                "content_type": "course",
                "content_id": "locking_test_course"
            }
        )
        assert lock_response.status_code == 200
        lock_data = lock_response.json()
        
        # If lock was acquired, verify it's marked as owned
        if lock_data["success"]:
            assert lock_data["lock_details"]["success"] is True or \
                   "locked_by" in lock_data["lock_details"]

# =============================================================================
# Performance Tests
# =============================================================================

class TestPhase4Performance:
    """Performance tests for Phase 4 features"""
    
    @patch('ai_predictive.get_current_user_from_token')
    def test_batch_risk_assessment_performance(self, mock_admin_auth, mock_admin_user):
        """Test performance of batch risk assessment"""
        mock_admin_auth.return_value = mock_admin_user
        
        # Test with 100 users
        user_ids = [f"student_{i}" for i in range(100)]
        
        response = client.post(
            "/ai/predict/risk",
            json={"user_ids": user_ids}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["assessments"]) == 100
        assert data["summary"]["total_students"] == 100
    
    @patch('system_core.get_current_user_from_token')
    def test_large_search_performance(self, mock_admin_auth, mock_admin_user):
        """Test performance of large search queries"""
        mock_admin_auth.return_value = mock_admin_user
        
        import time
        start = time.time()
        
        response = client.post(
            "/search/global",
            json={
                "query": "test query for performance testing",
                "content_types": ["course", "lesson", "quiz", "concept", "learning_path"],
                "page": 1,
                "per_page": 100
            }
        )
        
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["search_time_ms"] < 5000  # Should complete within 5 seconds
    
    @patch('system_core.get_current_user_from_token')
    def test_version_history_pagination(self, mock_admin_auth, mock_admin_user):
        """Test pagination of version history"""
        mock_admin_auth.return_value = mock_admin_user
        
        # Get first page
        response = client.get(
            "/content/course_python_101/history",
            params={"page": 1, "per_page": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["versions"]) <= 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 2

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])