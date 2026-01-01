# In-memory storage for admin analytics
# This module provides transient storage for platform analytics

import threading
import datetime

# In-memory storage (no persistence - real data comes from databases)
analytics_store = {}
analytics_lock = threading.Lock()

def initialize_analytics():
    """Initialize analytics store with empty data"""
    global analytics_store
    analytics_store = {
        "users": {},
        "learning": {},
        "last_refreshed": None
    }
    return analytics_store

def get_user_analytics():
    """
    Get user analytics data.
    Note: For real user statistics, query the database directly.
    This function provides a placeholder structure.
    """
    with analytics_lock:
        data = analytics_store.get("users", {})
        
        # Return placeholder data - for real user counts, query database
        return {
            "total_users": 0,
            "active_users": 0,
            "new_users": [],
            "user_growth": [],
            "note": "For real user statistics, query the database directly"
        }

def get_learning_analytics():
    """
    Get learning analytics data.
    Note: For real learning statistics, query the database directly.
    This function provides a placeholder structure.
    """
    with analytics_lock:
        data = analytics_store.get("learning", {})
        
        # Return placeholder data - for real learning stats, query database
        return {
            "total_sessions": 0,
            "completed_courses": 0,
            "average_progress": 0,
            "learning_trends": [],
            "note": "For real learning statistics, query the database directly"
        }

def get_content_analytics():
    """
    DEPRECATED: Content analytics now query databases directly.
    Use admin_analytics_content walker for real content statistics.
    """
    return {
        "total_courses": 0,
        "total_concepts": 0,
        "popular_content": [],
        "content_by_difficulty": {},
        "deprecated": True,
        "message": "Use /walker/admin_analytics_content endpoint for real content statistics"
    }

def refresh_analytics():
    """Refresh analytics timestamp"""
    with analytics_lock:
        analytics_store["last_refreshed"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        return {"success": True, "refreshed_at": analytics_store["last_refreshed"]}

def record_user_activity(user_id, activity_type):
    """Record a user activity for analytics (in-memory only)"""
    with analytics_lock:
        if "activity_log" not in analytics_store:
            analytics_store["activity_log"] = []
        
        analytics_store["activity_log"].append({
            "user_id": user_id,
            "activity_type": activity_type,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        
        # Keep only last 1000 activities
        if len(analytics_store["activity_log"]) > 1000:
            analytics_store["activity_log"] = analytics_store["activity_log"][-1000:]

def record_course_completion(course_id, user_id, score):
    """Record a course completion (in-memory only)"""
    with analytics_lock:
        if "completions" not in analytics_store:
            analytics_store["completions"] = []
        
        analytics_store["completions"].append({
            "course_id": course_id,
            "user_id": user_id,
            "score": score,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
