# In-memory storage for admin analytics
# This module provides persistent storage for platform analytics

import json
import os
import threading
import datetime

# In-memory storage
analytics_store = {}
analytics_lock = threading.Lock()

# File path for persistence
DATA_DIR = "data"
ANALYTICS_FILE = os.path.join(DATA_DIR, "admin_analytics.json")

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json_store(filepath, default_data):
    """Load data from JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return default_data

def save_json_store(filepath, data):
    """Save data to JSON file"""
    try:
        ensure_data_dir()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# ==============================================================================
# ANALYTICS STORAGE
# ==============================================================================

def initialize_analytics():
    """Initialize analytics store with default data"""
    global analytics_store
    default_analytics = {
        "users": {
            "total_users": 156,
            "active_users": 142,
            "new_users_by_day": [12, 15, 18, 22, 19, 25, 30]
        },
        "learning": {
            "total_sessions": 1250,
            "completed_courses": 89,
            "average_progress": 72.5
        },
        "content": {
            "total_courses": 12,
            "total_concepts": 48,
            "popular_content": [
                {"title": "Variables and Data Types", "views": 1250},
                {"title": "Object-Spatial Programming", "views": 980},
                {"title": "Walker Functions", "views": 875}
            ],
            "content_by_difficulty": {
                "beginner": 15,
                "intermediate": 25,
                "advanced": 8
            }
        },
        "last_refreshed": None
    }
    analytics_store = load_json_store(ANALYTICS_FILE, default_analytics)
    return analytics_store

def get_user_analytics():
    """Get user analytics data"""
    with analytics_lock:
        data = analytics_store.get("users", {})
        total = data.get("total_users", 0)
        active = data.get("active_users", 0)
        new_users = data.get("new_users_by_day", [])
        
        # Generate growth trend
        user_growth = []
        base_count = total - sum(new_users)
        for i, daily_new in enumerate(new_users):
            base_count += daily_new
            date = (datetime.datetime.now() - datetime.timedelta(days=len(new_users) - i - 1)).strftime("%Y-%m-%d")
            user_growth.append({"date": date, "count": base_count})
        
        return {
            "total_users": total,
            "active_users": active,
            "new_users": new_users,
            "user_growth": user_growth
        }

def get_learning_analytics():
    """Get learning analytics data"""
    with analytics_lock:
        data = analytics_store.get("learning", {})
        total_sessions = data.get("total_sessions", 0)
        completed_courses = data.get("completed_courses", 0)
        avg_progress = data.get("average_progress", 0)
        
        # Generate learning trends
        learning_trends = []
        base_sessions = total_sessions - 40
        for i in range(7):
            base_sessions += 5 + (i * 3)
            date = (datetime.datetime.now() - datetime.timedelta(days=6 - i)).strftime("%Y-%m-%d")
            learning_trends.append({"date": date, "sessions": base_sessions})
        
        return {
            "total_sessions": total_sessions,
            "completed_courses": completed_courses,
            "average_progress": avg_progress,
            "learning_trends": learning_trends
        }

def get_content_analytics():
    """Get content analytics data"""
    with analytics_lock:
        data = analytics_store.get("content", {})
        
        return {
            "total_courses": data.get("total_courses", 0),
            "total_concepts": data.get("total_concepts", 0),
            "popular_content": data.get("popular_content", []),
            "content_by_difficulty": data.get("content_by_difficulty", {})
        }

def refresh_analytics():
    """Refresh analytics cache"""
    with analytics_lock:
        analytics_store["last_refreshed"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        save_json_store(ANALYTICS_FILE, analytics_store)
        return {"success": True, "refreshed_at": analytics_store["last_refreshed"]}

def record_user_activity(user_id, activity_type):
    """Record a user activity for analytics"""
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
        
        save_json_store(ANALYTICS_FILE, analytics_store)

def record_course_completion(course_id, user_id, score):
    """Record a course completion"""
    with analytics_lock:
        if "completions" not in analytics_store:
            analytics_store["completions"] = []
        
        analytics_store["completions"].append({
            "course_id": course_id,
            "user_id": user_id,
            "score": score,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        
        # Update counts
        data = analytics_store.get("learning", {})
        data["completed_courses"] = data.get("completed_courses", 0) + 1
        analytics_store["learning"] = data
        
        save_json_store(ANALYTICS_FILE, analytics_store)
