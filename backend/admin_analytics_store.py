# Admin Analytics Store - Platform Analytics and Statistics
# This module provides comprehensive analytics data from the database

import threading
import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import get_db_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# In-memory storage for analytics (complements database data)
analytics_store = {}
analytics_lock = threading.Lock()

def initialize_analytics():
    """Initialize analytics store with empty data structures"""
    global analytics_store
    analytics_store = {
        "users": {},
        "learning": {},
        "content": {},
        "last_refreshed": None
    }
    return analytics_store

def get_user_analytics() -> Dict[str, Any]:
    """
    Get comprehensive user analytics data from database.
    
    Returns:
        Dictionary containing user statistics including total users,
        active users, growth trends, and engagement metrics.
    """
    with analytics_lock:
        try:
            if DATABASE_AVAILABLE:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Get total users count
                cursor.execute("SELECT COUNT(*) as total FROM users")
                total_users = cursor.fetchone()['total'] if cursor.fetchone() else 0
                
                # Get active users (logged in within last 7 days)
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) as active 
                    FROM user_sessions 
                    WHERE last_activity >= datetime('now', '-7 days')
                """)
                active_users = cursor.fetchone()['active'] if cursor.fetchone() else 0
                
                # Get new users per day for last 7 days
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM users
                    WHERE created_at >= datetime('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """)
                new_users_data = cursor.fetchall()
                
                # Build last 7 days data
                new_users = []
                user_growth = []
                for i in range(7):
                    date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                    count = 0
                    for row in new_users_data:
                        if row['date'] == date:
                            count = row['count']
                            break
                    new_users.append(count)
                    user_growth.append({
                        "date": date,
                        "count": count
                    })
                
                conn.close()
                
                return {
                    "total_users": total_users,
                    "active_users": active_users,
                    "new_users": new_users,
                    "user_growth": user_growth,
                    "success": True
                }
        except Exception as e:
            print(f"Database error in get_user_analytics: {e}")
        
        # Fallback: Return computed data from in-memory store
        data = analytics_store.get("users", {})
        return {
            "total_users": len(data.get("user_list", [])),
            "active_users": len([u for u in data.get("user_list", []) if u.get("is_active", False)]),
            "new_users": data.get("new_users", [0, 0, 0, 0, 0, 0, 0]),
            "user_growth": data.get("user_growth", []),
            "success": True
        }

def get_learning_analytics() -> Dict[str, Any]:
    """
    Get comprehensive learning analytics data from database.
    
    Returns:
        Dictionary containing learning statistics including total sessions,
        completed courses, average progress, and learning trends.
    """
    with analytics_lock:
        try:
            if DATABASE_AVAILABLE:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Get total learning sessions
                cursor.execute("SELECT COUNT(*) as total FROM learning_sessions")
                total_sessions = cursor.fetchone()['total'] if cursor.fetchone() else 0
                
                # Get completed courses count
                cursor.execute("""
                    SELECT COUNT(*) as completed 
                    FROM user_progress 
                    WHERE status = 'completed'
                """)
                completed_courses = cursor.fetchone()['completed'] if cursor.fetchone() else 0
                
                # Get average progress
                cursor.execute("""
                    SELECT AVG(progress_percent) as avg_progress 
                    FROM user_progress 
                    WHERE progress_percent > 0
                """)
                avg_progress_row = cursor.fetchone()
                average_progress = avg_progress_row['avg_progress'] if avg_progress_row and avg_progress_row['avg_progress'] else 0
                
                # Get learning trends for last 7 days
                cursor.execute("""
                    SELECT DATE(started_at) as date, COUNT(*) as sessions
                    FROM learning_sessions
                    WHERE started_at >= datetime('now', '-7 days')
                    GROUP BY DATE(started_at)
                    ORDER BY date DESC
                """)
                trends_data = cursor.fetchall()
                
                learning_trends = []
                for i in range(7):
                    date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                    sessions = 0
                    for row in trends_data:
                        if row['date'] == date:
                            sessions = row['sessions']
                            break
                    learning_trends.append({
                        "date": date,
                        "sessions": sessions
                    })
                
                conn.close()
                
                return {
                    "total_sessions": total_sessions,
                    "completed_courses": completed_courses,
                    "average_progress": round(average_progress, 2),
                    "learning_trends": learning_trends,
                    "success": True
                }
        except Exception as e:
            print(f"Database error in get_learning_analytics: {e}")
        
        # Fallback: Return computed data from in-memory store
        data = analytics_store.get("learning", {})
        return {
            "total_sessions": data.get("total_sessions", 0),
            "completed_courses": data.get("completed_courses", 0),
            "average_progress": data.get("average_progress", 0),
            "learning_trends": data.get("learning_trends", []),
            "success": True
        }

def get_content_analytics() -> Dict[str, Any]:
    """
    Get comprehensive content analytics data from database.
    
    Returns:
        Dictionary containing content statistics including total courses,
        total concepts, popular content, and difficulty distribution.
    """
    with analytics_lock:
        try:
            if DATABASE_AVAILABLE:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Get total courses
                cursor.execute("SELECT COUNT(*) as total FROM courses")
                total_courses = cursor.fetchone()['total'] if cursor.fetchone() else 0
                
                # Get total concepts
                cursor.execute("SELECT COUNT(*) as total FROM concepts")
                total_concepts = cursor.fetchone()['total'] if cursor.fetchone() else 0
                
                # Get content by difficulty
                cursor.execute("""
                    SELECT difficulty, COUNT(*) as count
                    FROM concepts
                    GROUP BY difficulty
                """)
                difficulty_data = cursor.fetchall()
                
                content_by_difficulty = {}
                for row in difficulty_data:
                    content_by_difficulty[row['difficulty']] = row['count']
                
                # Get popular content (most viewed)
                cursor.execute("""
                    SELECT cv.content_id, cv.content_type, c.title, COUNT(*) as views
                    FROM content_views cv
                    LEFT JOIN courses c ON cv.content_id = c.course_id
                    GROUP BY cv.content_id
                    ORDER BY views DESC
                    LIMIT 5
                """)
                popular_data = cursor.fetchall()
                
                popular_content = []
                for row in popular_data:
                    popular_content.append({
                        "title": row['title'] or row['content_id'],
                        "views": row['views'],
                        "type": row['content_type']
                    })
                
                conn.close()
                
                return {
                    "total_courses": total_courses,
                    "total_concepts": total_concepts,
                    "popular_content": popular_content,
                    "content_by_difficulty": content_by_difficulty,
                    "success": True
                }
        except Exception as e:
            print(f"Database error in get_content_analytics: {e}")
        
        # Fallback: Return computed data from in-memory store
        data = analytics_store.get("content", {})
        return {
            "total_courses": data.get("total_courses", 0),
            "total_concepts": data.get("total_concepts", 0),
            "popular_content": data.get("popular_content", []),
            "content_by_difficulty": data.get("content_by_difficulty", {}),
            "success": True
        }

def get_execution_metrics(user_id: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """
    Get code execution metrics for analytics visualization.
    
    Args:
        user_id: Optional user ID to filter by
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
    
    Returns:
        Dictionary containing execution statistics and trends.
    """
    with analytics_lock:
        try:
            if DATABASE_AVAILABLE:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Build query with optional filters
                query = """
                    SELECT 
                        language,
                        COUNT(*) as total_runs,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
                        AVG(execution_time_ms) as avg_runtime_ms
                    FROM code_executions
                """
                params = []
                conditions = []
                
                if user_id:
                    conditions.append("user_id = ?")
                    params.append(user_id)
                if start_date:
                    conditions.append("created_at >= ?")
                    params.append(start_date)
                if end_date:
                    conditions.append("created_at <= ?")
                    params.append(end_date)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " GROUP BY language"
                
                cursor.execute(query, params)
                exec_data = cursor.fetchall()
                
                conn.close()
                
                return {
                    "success": True,
                    "executions": [
                        {
                            "language": row['language'],
                            "total_runs": row['total_runs'],
                            "successful_runs": row['successful_runs'],
                            "failed_runs": row['failed_runs'],
                            "success_rate": row['successful_runs'] / max(row['total_runs'], 1),
                            "avg_runtime_ms": row['avg_runtime_ms'] or 0
                        }
                        for row in exec_data
                    ]
                }
        except Exception as e:
            print(f"Database error in get_execution_metrics: {e}")
        
        # Fallback return
        return {
            "success": True,
            "executions": [],
            "message": "Using fallback data"
        }

def get_engagement_metrics(user_id: str = None, cohort_id: str = None) -> Dict[str, Any]:
    """
    Get user engagement metrics.
    
    Args:
        user_id: Optional user ID to filter by
        cohort_id: Optional cohort ID to filter by
    
    Returns:
        Dictionary containing engagement statistics.
    """
    with analytics_lock:
        try:
            if DATABASE_AVAILABLE:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Get daily active users
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) as count
                    FROM user_sessions
                    WHERE DATE(last_activity) = DATE('now')
                """)
                daily_active = cursor.fetchone()['count'] if cursor.fetchone() else 0
                
                # Get weekly active users
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) as count
                    FROM user_sessions
                    WHERE last_activity >= datetime('now', '-7 days')
                """)
                weekly_active = cursor.fetchone()['count'] if cursor.fetchone() else 0
                
                # Get monthly active users
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) as count
                    FROM user_sessions
                    WHERE last_activity >= datetime('now', '-30 days')
                """)
                monthly_active = cursor.fetchone()['count'] if cursor.fetchone() else 0
                
                # Get average session duration
                cursor.execute("""
                    SELECT AVG(TIMESTAMPDIFF(SECOND, login_time, logout_time)) as avg_duration
                    FROM user_sessions
                    WHERE logout_time IS NOT NULL
                """)
                avg_duration_row = cursor.fetchone()
                avg_session_duration = avg_duration_row['avg_duration'] if avg_duration_row and avg_duration_row['avg_duration'] else 0
                
                conn.close()
                
                return {
                    "success": True,
                    "daily_active_users": daily_active,
                    "weekly_active_users": weekly_active,
                    "monthly_active_users": monthly_active,
                    "avg_session_duration": avg_session_duration
                }
        except Exception as e:
            print(f"Database error in get_engagement_metrics: {e}")
        
        return {
            "success": True,
            "daily_active_users": 0,
            "weekly_active_users": 0,
            "monthly_active_users": 0,
            "avg_session_duration": 0
        }

def get_student_performance(cohort_id: str = None, course_id: str = None) -> Dict[str, Any]:
    """
    Get student performance metrics.
    
    Args:
        cohort_id: Optional cohort ID to filter by
        course_id: Optional course ID to filter by
    
    Returns:
        Dictionary containing student performance statistics.
    """
    with analytics_lock:
        try:
            if DATABASE_AVAILABLE:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Get student performance data
                query = """
                    SELECT 
                        up.user_id,
                        u.username,
                        u.first_name,
                        u.last_name,
                        AVG(up.progress_percent) as avg_score,
                        COUNT(CASE WHEN up.status = 'completed' THEN 1 END) as completed_courses,
                        MAX(up.last_activity) as last_active
                    FROM user_progress up
                    JOIN users u ON up.user_id = u.user_id
                """
                params = []
                conditions = []
                
                if cohort_id:
                    conditions.append("up.cohort_id = ?")
                    params.append(cohort_id)
                if course_id:
                    conditions.append("up.course_id = ?")
                    params.append(course_id)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " GROUP BY up.user_id, u.username, u.first_name, u.last_name"
                
                cursor.execute(query, params)
                performance_data = cursor.fetchall()
                
                conn.close()
                
                students = []
                for row in performance_data:
                    avg_score = row['avg_score'] or 0
                    risk_level = 'high' if avg_score < 50 else 'medium' if avg_score < 75 else 'low'
                    students.append({
                        "user_id": row['user_id'],
                        "user_name": f"{row['first_name'] or ''} {row['last_name'] or ''}".strip() or row['username'],
                        "avg_score": round(avg_score, 2),
                        "completed_courses": row['completed_courses'],
                        "risk_level": risk_level,
                        "last_active": row['last_active']
                    })
                
                return {
                    "success": True,
                    "students": students,
                    "total_students": len(students)
                }
        except Exception as e:
            print(f"Database error in get_student_performance: {e}")
        
        return {
            "success": True,
            "students": [],
            "total_students": 0
        }

def refresh_analytics() -> Dict[str, Any]:
    """Refresh analytics timestamp and clear cache"""
    with analytics_lock:
        analytics_store["last_refreshed"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "success": True, 
            "refreshed_at": analytics_store["last_refreshed"]
        }

def record_user_activity(user_id: str, activity_type: str, details: Dict = None):
    """Record a user activity for analytics"""
    with analytics_lock:
        if "activity_log" not in analytics_store:
            analytics_store["activity_log"] = []
        
        analytics_store["activity_log"].append({
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details or {},
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        
        # Keep only last 1000 activities
        if len(analytics_store["activity_log"]) > 1000:
            analytics_store["activity_log"] = analytics_store["activity_log"][-1000:]

def record_course_completion(course_id: str, user_id: str, score: float):
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

def get_activity_data(user_id: str = None, days: int = 30) -> Dict[str, Any]:
    """
    Get activity data for heatmap visualization.
    
    Args:
        user_id: Optional user ID to filter by
        days: Number of days of data to return
    
    Returns:
        Dictionary containing daily activity counts.
    """
    with analytics_lock:
        try:
            if DATABASE_AVAILABLE:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Get activity counts per day
                cursor.execute(f"""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM user_activities
                    WHERE created_at >= datetime('now', '-{days} days')
                """)
                activity_data = cursor.fetchall()
                
                conn.close()
                
                return {
                    "success": True,
                    "activity": [
                        {
                            "date": row['date'],
                            "value": row['count']
                        }
                        for row in activity_data
                    ]
                }
        except Exception as e:
            print(f"Database error in get_activity_data: {e}")
        
        # Fallback: Generate mock data
        activity = []
        for i in range(days):
            date = (datetime.datetime.now() - datetime.timedelta(days=days-i-1)).strftime('%Y-%m-%d')
            activity.append({
                "date": date,
                "value": 0
            })
        
        return {
            "success": True,
            "activity": activity
        }


def export_analytics_to_csv() -> str:
    """Export all analytics data to CSV format"""
    import csv
    import io
    
    # Get all analytics data
    user_analytics = get_user_analytics()
    learning_analytics = get_learning_analytics()
    content_analytics = get_content_analytics()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Category', 'Metric', 'Value'])
    
    # Write user analytics
    writer.writerow(['User Analytics', 'Total Users', user_analytics.get('total_users', 0)])
    writer.writerow(['User Analytics', 'Active Users', user_analytics.get('active_users', 0)])
    
    # Write user growth data
    writer.writerow([])
    writer.writerow(['User Growth', 'Date', 'New Users'])
    for item in user_analytics.get('user_growth', []):
        writer.writerow(['User Growth', item.get('date', ''), item.get('count', 0)])
    
    # Write learning analytics
    writer.writerow([])
    writer.writerow(['Learning Analytics', 'Total Sessions', learning_analytics.get('total_sessions', 0)])
    writer.writerow(['Learning Analytics', 'Completed Courses', learning_analytics.get('completed_courses', 0)])
    writer.writerow(['Learning Analytics', 'Average Progress (%)', learning_analytics.get('average_progress', 0)])
    
    # Write learning trends
    writer.writerow([])
    writer.writerow(['Learning Trends', 'Date', 'Sessions'])
    for item in learning_analytics.get('learning_trends', []):
        writer.writerow(['Learning Trends', item.get('date', ''), item.get('sessions', 0)])
    
    # Write content analytics
    writer.writerow([])
    writer.writerow(['Content Analytics', 'Total Courses', content_analytics.get('total_courses', 0)])
    writer.writerow(['Content Analytics', 'Total Concepts', content_analytics.get('total_concepts', 0)])
    
    # Write content by difficulty
    writer.writerow([])
    writer.writerow(['Content by Difficulty', 'Difficulty', 'Count'])
    for difficulty, count in content_analytics.get('content_by_difficulty', {}).items():
        writer.writerow(['Content by Difficulty', difficulty, count])
    
    # Write popular content
    writer.writerow([])
    writer.writerow(['Popular Content', 'Title', 'Views'])
    for item in content_analytics.get('popular_content', []):
        writer.writerow(['Popular Content', item.get('title', ''), item.get('views', 0)])
    
    return output.getvalue()


def export_analytics_to_json() -> str:
    """Export all analytics data to JSON format"""
    import json
    
    # Get all analytics data
    user_analytics = get_user_analytics()
    learning_analytics = get_learning_analytics()
    content_analytics = get_content_analytics()
    
    export_data = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_analytics": user_analytics,
        "learning_analytics": learning_analytics,
        "content_analytics": content_analytics,
        "summary": {
            "total_users": user_analytics.get('total_users', 0),
            "active_users": user_analytics.get('active_users', 0),
            "total_sessions": learning_analytics.get('total_sessions', 0),
            "completed_courses": learning_analytics.get('completed_courses', 0),
            "average_progress": learning_analytics.get('average_progress', 0),
            "total_courses": content_analytics.get('total_courses', 0),
            "total_concepts": content_analytics.get('total_concepts', 0)
        }
    }
    
    return json.dumps(export_data, indent=2)
