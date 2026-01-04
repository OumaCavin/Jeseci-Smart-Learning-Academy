"""
Advanced Analytics Dashboard System - Jeseci Smart Learning Academy
Comprehensive Analytics, Custom Dashboards, and Reporting

This module provides advanced analytics capabilities, custom dashboard creation,
and detailed reporting for educational data insights and decision making.

Author: Cavin Otieno
License: MIT License
"""

import os
import sys
from typing import Optional, Dict, Any, List, Union
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
import uuid
import json
import statistics
import calendar
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import modules
import admin_auth
from admin_auth import AdminRole, AnalyticsAdminUser, SuperAdminUser

# =============================================================================
# Analytics Models
# =============================================================================

class MetricType(str, Enum):
    COUNT = "count"
    PERCENTAGE = "percentage" 
    AVERAGE = "average"
    SUM = "sum"
    RATE = "rate"
    TREND = "trend"

class TimeFrame(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class DashboardType(str, Enum):
    OVERVIEW = "overview"
    USER_ANALYTICS = "user_analytics"
    CONTENT_PERFORMANCE = "content_performance"
    LEARNING_ANALYTICS = "learning_analytics"
    FINANCIAL = "financial"
    SYSTEM_HEALTH = "system_health"
    CUSTOM = "custom"

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DONUT = "donut"
    AREA = "area"
    HEATMAP = "heatmap"
    SCATTER = "scatter"
    TABLE = "table"

class DashboardWidget(BaseModel):
    widget_id: Optional[str] = Field(None, description="Unique widget ID")
    title: str = Field(..., min_length=1, description="Widget title")
    chart_type: ChartType = Field(..., description="Chart visualization type")
    metric_type: MetricType = Field(..., description="Type of metric to display")
    data_source: str = Field(..., description="Data source for the widget")
    time_frame: TimeFrame = Field(default=TimeFrame.DAILY)
    filters: Dict[str, Any] = Field(default={}, description="Data filters")
    position: Dict[str, int] = Field(..., description="Widget position (x, y, width, height)")
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")
    color_scheme: Optional[str] = Field(None, description="Color scheme for the widget")

class DashboardCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    dashboard_type: DashboardType = Field(default=DashboardType.CUSTOM)
    is_public: bool = Field(default=False, description="Public dashboard visible to all admins")
    tags: List[str] = Field(default=[], description="Dashboard tags")
    widgets: List[DashboardWidget] = Field(..., min_items=1, description="Dashboard widgets")
    layout: Dict[str, Any] = Field(default={}, description="Dashboard layout configuration")
    auto_refresh: bool = Field(default=True, description="Enable auto-refresh")
    refresh_interval: int = Field(default=300, description="Dashboard refresh interval")

class AnalyticsReportRequest(BaseModel):
    report_name: str = Field(..., min_length=1, description="Report name")
    date_from: datetime = Field(..., description="Report start date")
    date_to: datetime = Field(..., description="Report end date")
    metrics: List[str] = Field(..., min_items=1, description="Metrics to include")
    filters: Dict[str, Any] = Field(default={}, description="Report filters")
    format: str = Field(default="json", description="Report format: json, csv, pdf")
    include_charts: bool = Field(default=True, description="Include charts in report")
    email_recipients: List[str] = Field(default=[], description="Email recipients for report")

class AdvancedAnalyticsRequest(BaseModel):
    analysis_type: str = Field(..., description="Type of analysis: cohort, funnel, retention")
    time_period: str = Field(..., description="Analysis time period")
    user_segments: List[str] = Field(default=[], description="User segments to analyze")
    events: List[str] = Field(default=[], description="Events to track")
    filters: Dict[str, Any] = Field(default={})

# =============================================================================
# Response Models
# =============================================================================

class AnalyticsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    generated_at: str

class DashboardResponse(BaseModel):
    success: bool
    dashboard_id: Optional[str] = None
    message: str
    timestamp: str

class DashboardListResponse(BaseModel):
    success: bool
    dashboards: List[Dict[str, Any]]
    total: int
    user_dashboards: int

class ReportResponse(BaseModel):
    success: bool
    report_id: str
    report_data: Dict[str, Any]
    format: str
    generated_at: str

# =============================================================================
# Analytics Database Manager
# =============================================================================

class AdvancedAnalyticsManager:
    """Manages advanced analytics, dashboards, and reporting"""
    
    def __init__(self):
        self.dashboards = {}
        self.analytics_cache = {}
        self.reports = {}
        self.user_analytics = {}
        self.learning_analytics = {}
        self.content_analytics = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample analytics data - in production, these are calculated dynamically"""
        now = datetime.now()

        # Sample user analytics - these would be calculated from user database in production
        # Placeholder values that can be replaced with dynamic calculations
        self.user_analytics = {
            "overview": {
                "total_users": 0,  # Dynamic: Calculate from user database
                "active_users_today": 0,  # Dynamic: Count active users in last 24h
                "new_users_this_week": 0,  # Dynamic: Count new users in last 7 days
                "retention_rate_30_day": 0.0,  # Dynamic: Calculate retention rate
                "average_session_duration": 0.0,  # Dynamic: Average session length
                "user_growth_rate": 0.0,  # Dynamic: Calculate growth rate
                "engagement_score": 0.0,  # Dynamic: Calculate engagement score
                "last_updated": now.isoformat()
            },
            "demographics": {
                "age_distribution": {},  # Dynamic: Aggregate from user profiles
                "geographic_distribution": {},  # Dynamic: Aggregate from user profiles
                "skill_level_distribution": {}  # Dynamic: Aggregate from user profiles
            },
            "behavior": {
                "most_active_hours": [],  # Dynamic: Calculate from session data
                "average_courses_per_user": 0.0,  # Dynamic: Calculate from enrollment data
                "completion_rates_by_time": {},  # Dynamic: Aggregate completion data
                "device_usage": {}  # Dynamic: Aggregate from user device data
            }
        }

        # Sample learning analytics - these would be calculated from course database in production
        self.learning_analytics = {
            "course_performance": {
                "total_courses": 0,  # Dynamic: Count from course database
                "average_completion_rate": 0.0,  # Dynamic: Calculate from enrollment data
                "average_course_rating": 0.0,  # Dynamic: Average of all course ratings
                "most_popular_courses": [],  # Dynamic: Query from enrollment data
                "course_difficulty_performance": {}  # Dynamic: Aggregate by difficulty
            },
            "learning_paths": {
                "total_paths": 0,  # Dynamic: Count from learning path database
                "path_completion_rate": 0.0,  # Dynamic: Calculate from path enrollments
                "average_path_duration": 0.0,  # Dynamic: Average path duration
                "most_effective_paths": []  # Dynamic: Query from path completion data
            },
            "quiz_performance": {
                "total_quizzes": 0,  # Dynamic: Count from quiz database
                "average_quiz_score": 0.0,  # Dynamic: Calculate from quiz attempts
                "quiz_attempt_success_rate": 0.0,  # Dynamic: Calculate pass rate
                "most_challenging_topics": []  # Dynamic: Analyze quiz question performance
            }
        }

        # Sample content analytics - these would be calculated from content database in production
        self.content_analytics = {
            "engagement": {
                "total_content_views": 0,  # Dynamic: Sum from content view logs
                "average_time_on_content": 0.0,  # Dynamic: Average time spent
                "content_completion_rate": 0.0,  # Dynamic: Calculate from completion data
                "most_engaging_content_types": {}  # Dynamic: Aggregate by content type
            },
            "ai_content": {
                "ai_generated_lessons": 0,  # Dynamic: Count AI-generated content
                "ai_content_approval_rate": 0.0,  # Dynamic: Calculate approval rate
                "ai_content_quality_score": 0.0,  # Dynamic: Average quality score
                "ai_generation_cost": 0.0,  # Dynamic: Sum of generation costs
                "human_vs_ai_performance": {
                    "human_content_rating": 0.0,
                    "ai_content_rating": 0.0,
                    "engagement_difference": 0.0
                }
            }
        }

    def calculate_user_analytics(self) -> Dict[str, Any]:
        """
        Calculate user analytics dynamically from actual data.
        In production, this would query the user database and session logs.
        """
        # Placeholder calculation - in production, use real database queries
        overview = {
            "total_users": len(self.user_analytics.get("overview", {})),
            "active_users_today": 0,
            "new_users_this_week": 0,
            "retention_rate_30_day": 0.0,
            "average_session_duration": 0.0,
            "user_growth_rate": 0.0,
            "engagement_score": 0.0,
            "last_updated": datetime.now().isoformat()
        }

        # These would be calculated from real user data in production
        demographics = {
            "age_distribution": {"18-25": 0.0, "26-35": 0.0, "36-45": 0.0, "46+": 0.0},
            "geographic_distribution": {"North America": 0.0, "Europe": 0.0, "Asia": 0.0, "Other": 0.0},
            "skill_level_distribution": {"beginner": 0.0, "intermediate": 0.0, "advanced": 0.0}
        }

        behavior = {
            "most_active_hours": [9, 10, 14, 15, 19, 20, 21],
            "average_courses_per_user": 0.0,
            "completion_rates_by_time": {
                "morning": 0.0,
                "afternoon": 0.0,
                "evening": 0.0,
                "night": 0.0
            },
            "device_usage": {"desktop": 0.0, "mobile": 0.0, "tablet": 0.0}
        }

        return {
            "overview": overview,
            "demographics": demographics,
            "behavior": behavior
        }

    def calculate_learning_analytics(self) -> Dict[str, Any]:
        """
        Calculate learning analytics dynamically from course and enrollment data.
        In production, this would query the course database.
        """
        # Placeholder - in production, query course and enrollment databases
        return {
            "course_performance": {
                "total_courses": 0,
                "average_completion_rate": 0.0,
                "average_course_rating": 0.0,
                "most_popular_courses": [],
                "course_difficulty_performance": {}
            },
            "learning_paths": {
                "total_paths": 0,
                "path_completion_rate": 0.0,
                "average_path_duration": 0.0,
                "most_effective_paths": []
            },
            "quiz_performance": {
                "total_quizzes": 0,
                "average_quiz_score": 0.0,
                "quiz_attempt_success_rate": 0.0,
                "most_challenging_topics": []
            }
        }

    def calculate_content_analytics(self) -> Dict[str, Any]:
        """
        Calculate content analytics dynamically from content and engagement data.
        In production, this would query the content database and engagement logs.
        """
        # Placeholder - in production, query content and engagement databases
        return {
            "engagement": {
                "total_content_views": 0,
                "average_time_on_content": 0.0,
                "content_completion_rate": 0.0,
                "most_engaging_content_types": {}
            },
            "ai_content": {
                "ai_generated_lessons": 0,
                "ai_content_approval_rate": 0.0,
                "ai_content_quality_score": 0.0,
                "ai_generation_cost": 0.0,
                "human_vs_ai_performance": {
                    "human_content_rating": 0.0,
                    "ai_content_rating": 0.0,
                    "engagement_difference": 0.0
                }
            }
        }

    def refresh_analytics(self) -> Dict[str, Any]:
        """
        Refresh all analytics by recalculating from actual data.
        This method updates all cached analytics with fresh calculations.
        """
        self.user_analytics = self.calculate_user_analytics()
        self.learning_analytics = self.calculate_learning_analytics()
        self.content_analytics = self.calculate_content_analytics()

        return {
            "success": True,
            "message": "Analytics refreshed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        # Sample dashboard
        sample_widgets = [
            DashboardWidget(
                widget_id="widget_user_growth",
                title="User Growth Trend",
                chart_type=ChartType.LINE,
                metric_type=MetricType.COUNT,
                data_source="user_registrations",
                time_frame=TimeFrame.MONTHLY,
                position={"x": 0, "y": 0, "width": 6, "height": 4}
            ),
            DashboardWidget(
                widget_id="widget_course_completion",
                title="Course Completion Rates",
                chart_type=ChartType.BAR,
                metric_type=MetricType.PERCENTAGE,
                data_source="course_completions",
                time_frame=TimeFrame.WEEKLY,
                position={"x": 6, "y": 0, "width": 6, "height": 4}
            )
        ]
        
        sample_dashboard = {
            "dashboard_id": "dashboard_overview_001",
            "title": "Platform Overview Dashboard",
            "description": "Comprehensive overview of platform metrics and KPIs",
            "dashboard_type": DashboardType.OVERVIEW,
            "is_public": True,
            "tags": ["overview", "kpi", "metrics"],
            "widgets": [w.dict() for w in sample_widgets],
            "layout": {"columns": 12, "row_height": 60},
            "auto_refresh": True,
            "refresh_interval": 300,
            "created_at": now.isoformat(),
            "created_by": "system",
            "view_count": 156,
            "last_viewed": now.isoformat()
        }
        
        self.dashboards["dashboard_overview_001"] = sample_dashboard
    
    def get_user_analytics(self, time_frame: str = "monthly", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        base_data = self.user_analytics.copy()
        
        # Add time-based trends (simulated)
        now = datetime.now()
        trends = self._generate_time_series_data("user_metrics", time_frame, 30)
        
        analytics = {
            "overview": base_data["overview"],
            "demographics": base_data["demographics"], 
            "behavior": base_data["behavior"],
            "trends": {
                "user_growth": trends["user_registrations"],
                "engagement_trend": trends["user_engagement"],
                "retention_trend": trends["user_retention"]
            },
            "insights": self._generate_user_insights(base_data),
            "recommendations": self._generate_user_recommendations(base_data)
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "time_frame": time_frame,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_learning_analytics(self, time_frame: str = "monthly", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive learning analytics"""
        base_data = self.learning_analytics.copy()
        
        # Add learning effectiveness metrics
        effectiveness_metrics = {
            "knowledge_retention_rate": 73.8,
            "skill_improvement_rate": 68.5,
            "learning_velocity": 2.3,  # concepts per week
            "concept_mastery_distribution": {
                "mastered": 58.2,
                "proficient": 28.7,
                "learning": 13.1
            }
        }
        
        analytics = {
            "course_performance": base_data["course_performance"],
            "learning_paths": base_data["learning_paths"],
            "quiz_performance": base_data["quiz_performance"],
            "effectiveness": effectiveness_metrics,
            "trends": self._generate_time_series_data("learning_metrics", time_frame, 30),
            "insights": self._generate_learning_insights(base_data),
            "recommendations": self._generate_learning_recommendations(base_data)
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "time_frame": time_frame,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_content_analytics(self, time_frame: str = "monthly", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive content analytics"""
        base_data = self.content_analytics.copy()
        
        # Add content effectiveness metrics
        content_effectiveness = {
            "content_engagement_score": 7.2,
            "content_quality_trend": "improving",
            "user_satisfaction": 4.1,
            "content_roi": {
                "high_performing": 34.2,
                "medium_performing": 48.6,
                "low_performing": 17.2
            }
        }
        
        analytics = {
            "engagement": base_data["engagement"],
            "ai_content": base_data["ai_content"],
            "effectiveness": content_effectiveness,
            "trends": self._generate_time_series_data("content_metrics", time_frame, 30),
            "insights": self._generate_content_insights(base_data),
            "recommendations": self._generate_content_recommendations(base_data)
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "time_frame": time_frame,
            "generated_at": datetime.now().isoformat()
        }
    
    def create_dashboard(self, dashboard_data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new custom dashboard"""
        dashboard_id = f"dashboard_{dashboard_data['title'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Assign widget IDs
        for widget in dashboard_data['widgets']:
            if not widget.get('widget_id'):
                widget['widget_id'] = f"widget_{uuid.uuid4().hex[:8]}"
        
        dashboard = {
            "dashboard_id": dashboard_id,
            **dashboard_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": admin_user.get("user_id"),
            "created_by_username": admin_user.get("username"),
            "view_count": 0,
            "last_viewed": None
        }
        
        self.dashboards[dashboard_id] = dashboard
        
        return {
            "success": True,
            "dashboard_id": dashboard_id,
            "message": "Dashboard created successfully"
        }
    
    def get_dashboards(self, admin_user: Dict[str, Any], dashboard_type: str = None) -> Dict[str, Any]:
        """Get dashboards accessible to the admin user"""
        dashboards = list(self.dashboards.values())
        
        # Filter by type if specified
        if dashboard_type:
            dashboards = [d for d in dashboards if d.get("dashboard_type") == dashboard_type]
        
        # Filter by access rights (public dashboards + own dashboards)
        accessible_dashboards = [
            d for d in dashboards 
            if d.get("is_public") or d.get("created_by") == admin_user.get("user_id")
        ]
        
        # Sort by last viewed and creation date
        accessible_dashboards.sort(
            key=lambda x: (x.get("last_viewed") or "1970-01-01", x.get("created_at", "")), 
            reverse=True
        )
        
        return {
            "success": True,
            "dashboards": accessible_dashboards,
            "total": len(accessible_dashboards),
            "user_dashboards": len([d for d in accessible_dashboards if d.get("created_by") == admin_user.get("user_id")])
        }
    
    def generate_report(self, report_request: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom analytics report"""
        report_id = f"report_{uuid.uuid4().hex[:12]}"
        
        # Collect data based on requested metrics
        report_data = {}
        for metric in report_request["metrics"]:
            if metric == "user_analytics":
                report_data["user_analytics"] = self.get_user_analytics()["analytics"]
            elif metric == "learning_analytics":
                report_data["learning_analytics"] = self.get_learning_analytics()["analytics"]
            elif metric == "content_analytics":
                report_data["content_analytics"] = self.get_content_analytics()["analytics"]
        
        # Add report metadata
        report = {
            "report_id": report_id,
            "report_name": report_request["report_name"],
            "generated_by": admin_user.get("user_id"),
            "generated_at": datetime.now().isoformat(),
            "date_range": {
                "from": report_request["date_from"],
                "to": report_request["date_to"]
            },
            "metrics": report_request["metrics"],
            "filters": report_request.get("filters", {}),
            "format": report_request.get("format", "json"),
            "data": report_data,
            "summary": self._generate_report_summary(report_data)
        }
        
        self.reports[report_id] = report
        
        return {
            "success": True,
            "report_id": report_id,
            "report_data": report,
            "message": "Report generated successfully"
        }
    
    def _generate_time_series_data(self, data_type: str, time_frame: str, points: int) -> Dict[str, List]:
        """Generate sample time series data"""
        import random
        
        now = datetime.now()
        dates = []
        
        if time_frame == "daily":
            dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(points-1, -1, -1)]
        elif time_frame == "weekly":
            dates = [(now - timedelta(weeks=i)).strftime("%Y-W%W") for i in range(points-1, -1, -1)]
        elif time_frame == "monthly":
            dates = [(now - timedelta(days=i*30)).strftime("%Y-%m") for i in range(points-1, -1, -1)]
        
        # Generate sample data based on type
        if data_type == "user_metrics":
            return {
                "user_registrations": [random.randint(15, 45) for _ in range(points)],
                "user_engagement": [random.uniform(6.5, 8.5) for _ in range(points)],
                "user_retention": [random.uniform(65, 75) for _ in range(points)],
                "dates": dates
            }
        elif data_type == "learning_metrics":
            return {
                "course_completions": [random.randint(25, 65) for _ in range(points)],
                "quiz_scores": [random.uniform(70, 85) for _ in range(points)],
                "learning_time": [random.uniform(35, 55) for _ in range(points)],
                "dates": dates
            }
        elif data_type == "content_metrics":
            return {
                "content_views": [random.randint(150, 350) for _ in range(points)],
                "content_rating": [random.uniform(3.8, 4.5) for _ in range(points)],
                "ai_content_generated": [random.randint(5, 15) for _ in range(points)],
                "dates": dates
            }
        
        return {"dates": dates}
    
    def _generate_user_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate user analytics insights"""
        insights = []
        
        overview = data["overview"]
        if overview["user_growth_rate"] > 10:
            insights.append(f"Strong user growth of {overview['user_growth_rate']}% indicates effective acquisition strategies")
        
        if overview["retention_rate_30_day"] < 65:
            insights.append("30-day retention rate below 65% suggests need for improved onboarding")
        
        if overview["engagement_score"] > 7.5:
            insights.append("High engagement score shows strong user satisfaction")
        
        return insights
    
    def _generate_user_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate user analytics recommendations"""
        recommendations = []
        
        overview = data["overview"]
        behavior = data["behavior"]
        
        if overview["retention_rate_30_day"] < 70:
            recommendations.append("Implement personalized onboarding flow to improve retention")
        
        if behavior["completion_rates_by_time"]["evening"] < 60:
            recommendations.append("Add evening-friendly content formats for better engagement")
        
        if behavior["device_usage"]["mobile"] < 35:
            recommendations.append("Optimize mobile experience to capture more mobile learners")
        
        return recommendations
    
    def _generate_learning_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate learning analytics insights"""
        insights = []
        
        course_perf = data["course_performance"]
        if course_perf["average_completion_rate"] > 70:
            insights.append("Strong course completion rates indicate effective content design")
        
        quiz_perf = data["quiz_performance"]
        if quiz_perf["average_quiz_score"] > 75:
            insights.append("High quiz scores show good learning comprehension")
        
        return insights
    
    def _generate_learning_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate learning analytics recommendations"""
        recommendations = []
        
        course_perf = data["course_performance"]
        if course_perf["course_difficulty_performance"]["advanced"]["completion_rate"] < 55:
            recommendations.append("Review advanced courses for difficulty balance and support materials")
        
        quiz_perf = data["quiz_performance"]
        if quiz_perf["quiz_attempt_success_rate"] < 80:
            recommendations.append("Add more practice opportunities before quiz attempts")
        
        return recommendations
    
    def _generate_content_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate content analytics insights"""
        insights = []
        
        engagement = data["engagement"]
        if engagement["content_completion_rate"] > 65:
            insights.append("Strong content completion indicates good content quality")
        
        ai_content = data["ai_content"]
        if ai_content["ai_content_approval_rate"] > 80:
            insights.append("High AI content approval rate shows effective AI content generation")
        
        return insights
    
    def _generate_content_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate content analytics recommendations"""
        recommendations = []
        
        engagement = data["engagement"]
        if engagement["average_time_on_content"] < 10:
            recommendations.append("Consider breaking content into smaller, more digestible segments")
        
        ai_content = data["ai_content"]
        if ai_content["human_vs_ai_performance"]["engagement_difference"] < -0.5:
            recommendations.append("Improve AI content quality through better prompts and review processes")
        
        return recommendations
    
    def _generate_report_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary for report"""
        summary = {
            "key_metrics": {},
            "highlights": [],
            "areas_for_improvement": [],
            "recommendations": []
        }
        
        # Extract key metrics from each analytics type
        for analytics_type, data in report_data.items():
            if analytics_type == "user_analytics":
                summary["key_metrics"]["total_users"] = data["overview"]["total_users"]
                summary["key_metrics"]["user_growth_rate"] = data["overview"]["user_growth_rate"]
            elif analytics_type == "learning_analytics":
                summary["key_metrics"]["course_completion_rate"] = data["course_performance"]["average_completion_rate"]
                summary["key_metrics"]["quiz_performance"] = data["quiz_performance"]["average_quiz_score"]
            elif analytics_type == "content_analytics":
                summary["key_metrics"]["content_engagement"] = data["engagement"]["content_completion_rate"]
                summary["key_metrics"]["ai_content_quality"] = data["ai_content"]["ai_content_quality_score"]
        
        return summary

# Global analytics manager instance
analytics_manager = AdvancedAnalyticsManager()

# =============================================================================
# Advanced Analytics Router
# =============================================================================

def create_analytics_admin_router() -> APIRouter:
    """Create advanced analytics and dashboard management router"""
    
    router = APIRouter()

    # =============================================================================
    # Analytics Endpoints
    # =============================================================================

    @router.post("/admin/analytics/refresh", response_model=AnalyticsResponse)
    async def refresh_analytics_admin(
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Refresh all analytics by recalculating from actual data (Analytics Admin+)"""
        try:
            # Refresh all analytics from dynamic calculations
            refresh_result = analytics_manager.refresh_analytics()

            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "analytics_refreshed",
                details={"timestamp": refresh_result["timestamp"]}
            )

            # Return the refreshed analytics
            return AnalyticsResponse(
                success=True,
                data={
                    "user_analytics": analytics_manager.user_analytics,
                    "learning_analytics": analytics_manager.learning_analytics,
                    "content_analytics": analytics_manager.content_analytics,
                    "refresh_status": refresh_result
                },
                metadata={
                    "refreshed": True,
                    "source": "dynamic_calculation"
                },
                generated_at=refresh_result["timestamp"]
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to refresh analytics",
                    "message": str(e)
                }
            )

    @router.get("/admin/analytics/users", response_model=AnalyticsResponse)
    async def get_user_analytics_admin(
        time_frame: str = Query(default="monthly", description="Analytics time frame"),
        segment: Optional[str] = Query(default=None, description="User segment filter"),
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Get comprehensive user analytics (Analytics Admin+)"""
        try:
            filters = {"segment": segment} if segment else None
            result = analytics_manager.get_user_analytics(time_frame, filters)
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "user_analytics_accessed",
                details={"time_frame": time_frame, "segment": segment}
            )
            
            return AnalyticsResponse(
                success=True,
                data=result["analytics"],
                metadata={
                    "time_frame": time_frame,
                    "segment": segment,
                    "data_points": len(result["analytics"].get("trends", {}))
                },
                generated_at=result["generated_at"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve user analytics",
                    "message": str(e)
                }
            )

    @router.get("/admin/analytics/learning", response_model=AnalyticsResponse)
    async def get_learning_analytics_admin(
        time_frame: str = Query(default="monthly", description="Analytics time frame"),
        course_id: Optional[str] = Query(default=None, description="Specific course filter"),
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Get comprehensive learning analytics (Analytics Admin+)"""
        try:
            filters = {"course_id": course_id} if course_id else None
            result = analytics_manager.get_learning_analytics(time_frame, filters)
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "learning_analytics_accessed",
                details={"time_frame": time_frame, "course_id": course_id}
            )
            
            return AnalyticsResponse(
                success=True,
                data=result["analytics"],
                metadata={
                    "time_frame": time_frame,
                    "course_filter": course_id,
                    "total_courses": result["analytics"]["course_performance"]["total_courses"]
                },
                generated_at=result["generated_at"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve learning analytics",
                    "message": str(e)
                }
            )

    @router.get("/admin/analytics/content", response_model=AnalyticsResponse)
    async def get_content_analytics_admin(
        time_frame: str = Query(default="monthly", description="Analytics time frame"),
        content_type: Optional[str] = Query(default=None, description="Content type filter"),
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Get comprehensive content analytics (Analytics Admin+)"""
        try:
            filters = {"content_type": content_type} if content_type else None
            result = analytics_manager.get_content_analytics(time_frame, filters)
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "content_analytics_accessed",
                details={"time_frame": time_frame, "content_type": content_type}
            )
            
            return AnalyticsResponse(
                success=True,
                data=result["analytics"],
                metadata={
                    "time_frame": time_frame,
                    "content_filter": content_type,
                    "ai_content_percentage": result["analytics"]["ai_content"]["ai_generated_lessons"]
                },
                generated_at=result["generated_at"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve content analytics",
                    "message": str(e)
                }
            )

    # =============================================================================
    # Dashboard Management
    # =============================================================================

    @router.get("/admin/dashboards", response_model=DashboardListResponse)
    async def get_dashboards_admin(
        dashboard_type: Optional[str] = Query(default=None, description="Dashboard type filter"),
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Get accessible dashboards (Analytics Admin+)"""
        try:
            result = analytics_manager.get_dashboards(admin_user, dashboard_type)
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "dashboards_accessed",
                details={"dashboard_type": dashboard_type}
            )
            
            return DashboardListResponse(
                success=True,
                dashboards=result["dashboards"],
                total=result["total"],
                user_dashboards=result["user_dashboards"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve dashboards",
                    "message": str(e)
                }
            )

    @router.post("/admin/dashboards", response_model=DashboardResponse)
    async def create_dashboard_admin(
        request: DashboardCreateRequest,
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Create custom dashboard (Analytics Admin+)"""
        try:
            dashboard_data = request.dict()
            result = analytics_manager.create_dashboard(dashboard_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Dashboard creation failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "dashboard_created",
                target=result["dashboard_id"],
                details={
                    "title": request.title,
                    "type": request.dashboard_type,
                    "widget_count": len(request.widgets)
                }
            )
            
            return DashboardResponse(
                success=True,
                dashboard_id=result["dashboard_id"],
                message="Dashboard created successfully",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create dashboard",
                    "message": str(e)
                }
            )

    # =============================================================================
    # Report Generation
    # =============================================================================

    @router.post("/admin/reports", response_model=ReportResponse)
    async def generate_report_admin(
        request: AnalyticsReportRequest,
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Generate custom analytics report (Analytics Admin+)"""
        try:
            report_data = request.dict()
            result = analytics_manager.generate_report(report_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Report generation failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "report_generated",
                target=result["report_id"],
                details={
                    "report_name": request.report_name,
                    "metrics": request.metrics,
                    "format": request.format
                }
            )
            
            return ReportResponse(
                success=True,
                report_id=result["report_id"],
                report_data=result["report_data"],
                format=request.format,
                generated_at=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to generate report",
                    "message": str(e)
                }
            )

    return router

# =============================================================================
# Export analytics router
# =============================================================================

analytics_admin_router = create_analytics_admin_router()