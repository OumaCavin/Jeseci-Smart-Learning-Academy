"""
Admin Dashboard Statistics Store - Jeseci Smart Learning Academy
Database queries and business logic for admin dashboard statistics

This module provides comprehensive statistics calculations for the admin dashboard
including user metrics, content statistics, activity data, and week-over-week comparisons.

Author: Jeseci Development Team
License: MIT License
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import centralized logging configuration
from logger_config import logger


class AdminDashboardStats:
    """Admin dashboard statistics calculator using raw SQL queries"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv("POSTGRES_HOST", "localhost"),
            'port': int(os.getenv("POSTGRES_PORT", 5432)),
            'database': os.getenv("POSTGRES_DB", "jeseci_learning_academy"),
            'user': os.getenv("POSTGRES_USER", "jeseci_academy_user"),
            'password': os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
        }
        self.schema = os.getenv("DB_SCHEMA", "jeseci_academy")
    
    def _get_connection(self):
        """Get a database connection"""
        import psycopg2
        return psycopg2.connect(**self.db_config)
    
    def _execute_query(self, query: str, params: tuple = None) -> List:
        """Execute a query and return results"""
        conn = None
        try:
            conn = self._get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Calculate user statistics including totals and week-over-week growth
        
        Returns:
            Dictionary containing:
            - total_users: Total number of registered users
            - active_users: Number of active users
            - new_users_this_week: New users registered in last 7 days
            - new_users_last_week: New users registered in the week before
            - week_over_week_change: Percentage change
        """
        try:
            # Total users count
            query = f"SELECT COUNT(*) FROM {self.schema}.users"
            result = self._execute_query(query)
            total_users = result[0][0] if result else 0
            
            # Active users (logged in within last 30 days)
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.users 
                WHERE last_login_at >= NOW() - INTERVAL '30 days'
            """
            result = self._execute_query(query)
            active_users = result[0][0] if result else 0
            
            # New users this week (last 7 days)
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.users 
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """
            result = self._execute_query(query)
            new_users_this_week = result[0][0] if result else 0
            
            # New users last week (7-14 days ago)
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.users 
                WHERE created_at >= NOW() - INTERVAL '14 days' 
                AND created_at < NOW() - INTERVAL '7 days'
            """
            result = self._execute_query(query)
            new_users_last_week = result[0][0] if result else 0
            
            # Calculate week-over-week percentage change
            if new_users_last_week > 0:
                week_over_week_change = round(
                    ((new_users_this_week - new_users_last_week) / new_users_last_week) * 100, 1
                )
            elif new_users_this_week > 0:
                week_over_week_change = 100.0  # New metric showing growth from zero
            else:
                week_over_week_change = 0.0
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "new_users_this_week": new_users_this_week,
                "new_users_last_week": new_users_last_week,
                "week_over_week_change": week_over_week_change
            }
            
        except Exception as e:
            logger.error(f"Error calculating user statistics: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "new_users_this_week": 0,
                "new_users_last_week": 0,
                "week_over_week_change": 0.0
            }
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """
        Calculate content statistics
        
        Returns:
            Dictionary containing content metrics and week-over-week comparison
        """
        try:
            # Total concepts
            query = f"SELECT COUNT(*) FROM {self.schema}.concepts"
            result = self._execute_query(query)
            total_concepts = result[0][0] if result else 0
            
            # Total learning paths
            query = f"SELECT COUNT(*) FROM {self.schema}.learning_paths"
            result = self._execute_query(query)
            total_learning_paths = result[0][0] if result else 0
            
            # Total lessons
            query = f"SELECT COUNT(*) FROM {self.schema}.lessons"
            result = self._execute_query(query)
            total_lessons = result[0][0] if result else 0
            
            # Published concepts (have lesson content)
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.concepts 
                WHERE lesson_content IS NOT NULL
            """
            result = self._execute_query(query)
            published_concepts = result[0][0] if result else 0
            
            # Published paths
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.learning_paths 
                WHERE is_published = true
            """
            result = self._execute_query(query)
            published_paths = result[0][0] if result else 0
            
            # Published lessons
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.lessons 
                WHERE is_published = true
            """
            result = self._execute_query(query)
            published_lessons = result[0][0] if result else 0
            
            # Content items (total concepts + lessons + paths)
            content_items = total_concepts + total_lessons + total_learning_paths
            
            # Week-over-week new content
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.concepts 
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """
            result = self._execute_query(query)
            new_content_this_week = result[0][0] if result else 0
            
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.concepts 
                WHERE created_at >= NOW() - INTERVAL '14 days' 
                AND created_at < NOW() - INTERVAL '7 days'
            """
            result = self._execute_query(query)
            new_content_last_week = result[0][0] if result else 0
            
            if new_content_last_week > 0:
                content_change = round(
                    ((new_content_this_week - new_content_last_week) / new_content_last_week) * 100, 1
                )
            elif new_content_this_week > 0:
                content_change = 100.0
            else:
                content_change = 0.0
            
            return {
                "total_concepts": total_concepts,
                "total_learning_paths": total_learning_paths,
                "total_lessons": total_lessons,
                "published_concepts": published_concepts,
                "published_paths": published_paths,
                "published_lessons": published_lessons,
                "content_items": content_items,
                "new_content_this_week": new_content_this_week,
                "content_change": content_change
            }
            
        except Exception as e:
            logger.error(f"Error calculating content statistics: {e}")
            return {
                "total_concepts": 0,
                "total_learning_paths": 0,
                "total_lessons": 0,
                "published_concepts": 0,
                "published_paths": 0,
                "published_lessons": 0,
                "content_items": 0,
                "new_content_this_week": 0,
                "content_change": 0.0
            }
    
    def get_activity_statistics(self) -> Dict[str, Any]:
        """
        Calculate activity statistics based on learning sessions
        
        Returns:
            Dictionary containing activity metrics
        """
        try:
            # Today's sessions
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.learning_sessions 
                WHERE start_time >= CURRENT_DATE
            """
            result = self._execute_query(query)
            daily_activity = result[0][0] if result else 0
            
            # This week's sessions
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.learning_sessions 
                WHERE start_time >= NOW() - INTERVAL '7 days'
            """
            result = self._execute_query(query)
            weekly_sessions = result[0][0] if result else 0
            
            # Last week's sessions for comparison
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.learning_sessions 
                WHERE start_time >= NOW() - INTERVAL '14 days' 
                AND start_time < NOW() - INTERVAL '7 days'
            """
            result = self._execute_query(query)
            last_week_sessions = result[0][0] if result else 0
            
            # Average session duration
            query = f"""
                SELECT AVG(duration_seconds) FROM {self.schema}.learning_sessions 
                WHERE duration_seconds IS NOT NULL
            """
            result = self._execute_query(query)
            avg_duration = result[0][0] if result and result[0][0] else 0
            
            # Unique users active this week
            query = f"""
                SELECT COUNT(DISTINCT user_id) FROM {self.schema}.learning_sessions 
                WHERE start_time >= NOW() - INTERVAL '7 days'
            """
            result = self._execute_query(query)
            active_users_this_week = result[0][0] if result else 0
            
            # Calculate change
            if last_week_sessions > 0:
                activity_change = round(
                    ((weekly_sessions - last_week_sessions) / last_week_sessions) * 100, 1
                )
            elif weekly_sessions > 0:
                activity_change = 100.0
            else:
                activity_change = 0.0
            
            return {
                "daily_activity": daily_activity,
                "weekly_sessions": weekly_sessions,
                "active_users_this_week": active_users_this_week,
                "avg_session_duration_seconds": round(float(avg_duration), 0) if avg_duration else 0,
                "last_week_sessions": last_week_sessions,
                "activity_change": activity_change
            }
            
        except Exception as e:
            logger.error(f"Error calculating activity statistics: {e}")
            return {
                "daily_activity": 0,
                "weekly_sessions": 0,
                "active_users_this_week": 0,
                "avg_session_duration_seconds": 0,
                "last_week_sessions": 0,
                "activity_change": 0.0
            }
    
    def get_issue_statistics(self) -> Dict[str, Any]:
        """
        Calculate issue and error statistics
        
        Returns:
            Dictionary containing issue metrics
        """
        try:
            # This would typically check system logs or error tracking
            # For now, returning placeholder structure
            
            return {
                "pending_issues": 0,
                "critical_issues": 0,
                "resolved_this_week": 0,
                "issue_change": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating issue statistics: {e}")
            return {
                "pending_issues": 0,
                "critical_issues": 0,
                "resolved_this_week": 0,
                "issue_change": 0.0
            }
    
    def get_learning_progress_statistics(self) -> Dict[str, Any]:
        """
        Calculate learning progress statistics
        
        Returns:
            Dictionary containing progress metrics
        """
        try:
            # Completed concepts
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.user_concept_progress 
                WHERE completed_at IS NOT NULL
            """
            result = self._execute_query(query)
            completed_concepts = result[0][0] if result else 0
            
            # In-progress concepts
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.user_concept_progress 
                WHERE completed_at IS NULL AND progress_percent > 0
            """
            result = self._execute_query(query)
            in_progress_concepts = result[0][0] if result else 0
            
            # Quiz completion rate
            query = f"SELECT COUNT(*) FROM {self.schema}.quiz_attempts"
            result = self._execute_query(query)
            total_attempts = result[0][0] if result else 0
            
            query = f"""
                SELECT COUNT(*) FROM {self.schema}.quiz_attempts 
                WHERE is_passed = true
            """
            result = self._execute_query(query)
            passed_attempts = result[0][0] if result else 0
            
            quiz_pass_rate = round((passed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0
            
            # Average progress
            query = f"""
                SELECT AVG(progress_percent) FROM {self.schema}.user_concept_progress 
                WHERE progress_percent > 0
            """
            result = self._execute_query(query)
            avg_progress = result[0][0] if result and result[0][0] else 0
            
            return {
                "completed_concepts": completed_concepts,
                "in_progress_concepts": in_progress_concepts,
                "quiz_pass_rate": quiz_pass_rate,
                "avg_progress_percent": round(float(avg_progress), 1) if avg_progress else 0,
                "total_attempts": total_attempts
            }
            
        except Exception as e:
            logger.error(f"Error calculating learning progress statistics: {e}")
            return {
                "completed_concepts": 0,
                "in_progress_concepts": 0,
                "quiz_pass_rate": 0,
                "avg_progress_percent": 0,
                "total_attempts": 0
            }
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard overview statistics
        
        Returns:
            Complete dashboard statistics for admin overview
        """
        user_stats = self.get_user_statistics()
        content_stats = self.get_content_statistics()
        activity_stats = self.get_activity_statistics()
        issue_stats = self.get_issue_statistics()
        progress_stats = self.get_learning_progress_statistics()
        
        return {
            "users": {
                "total_users": user_stats["total_users"],
                "active_users": user_stats["active_users"],
                "new_this_week": user_stats["new_users_this_week"],
                "week_over_week_change": user_stats["week_over_week_change"]
            },
            "content": {
                "total_items": content_stats["content_items"],
                "concepts": content_stats["total_concepts"],
                "learning_paths": content_stats["total_learning_paths"],
                "lessons": content_stats["total_lessons"],
                "new_this_week": content_stats["new_content_this_week"],
                "content_change": content_stats["content_change"]
            },
            "activity": {
                "daily_activity": activity_stats["daily_activity"],
                "weekly_sessions": activity_stats["weekly_sessions"],
                "active_users": activity_stats["active_users_this_week"],
                "avg_session_duration": activity_stats["avg_session_duration_seconds"],
                "activity_change": activity_stats["activity_change"]
            },
            "issues": {
                "pending": issue_stats["pending_issues"],
                "critical": issue_stats["critical_issues"],
                "resolved_this_week": issue_stats["resolved_this_week"],
                "issue_change": issue_stats["issue_change"]
            },
            "progress": {
                "completed_concepts": progress_stats["completed_concepts"],
                "in_progress": progress_stats["in_progress_concepts"],
                "quiz_pass_rate": progress_stats["quiz_pass_rate"],
                "avg_progress": progress_stats["avg_progress_percent"]
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_trend_data(self, metric: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical trend data for a specific metric
        
        Args:
            metric: The metric to track (users, activity)
            days: Number of days of history to retrieve
            
        Returns:
            List of daily data points
        """
        trend_data = []
        
        try:
            if metric == "users":
                # Get daily user registrations for the last N days
                for i in range(days):
                    day_start = datetime.now(timezone.utc) - timedelta(days=days - i)
                    day_end = day_start + timedelta(days=1)
                    
                    query = f"""
                        SELECT COUNT(*) FROM {self.schema}.users 
                        WHERE created_at >= %s AND created_at < %s
                    """
                    result = self._execute_query(query, (day_start, day_end))
                    count = result[0][0] if result else 0
                    
                    trend_data.append({
                        "date": day_start.strftime("%Y-%m-%d"),
                        "value": count
                    })
            
            elif metric == "activity":
                # Get daily sessions
                for i in range(days):
                    day_start = datetime.now(timezone.utc) - timedelta(days=days - i)
                    day_end = day_start + timedelta(days=1)
                    
                    query = f"""
                        SELECT COUNT(*) FROM {self.schema}.learning_sessions 
                        WHERE start_time >= %s AND start_time < %s
                    """
                    result = self._execute_query(query, (day_start, day_end))
                    count = result[0][0] if result else 0
                    
                    trend_data.append({
                        "date": day_start.strftime("%Y-%m-%d"),
                        "value": count
                    })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating trend data for {metric}: {e}")
            return []


# Convenience function for getting dashboard stats
def get_admin_dashboard_stats() -> Dict[str, Any]:
    """
    Get complete admin dashboard statistics
    
    Returns:
        Comprehensive dashboard statistics
    """
    stats_calculator = AdminDashboardStats()
    return stats_calculator.get_dashboard_overview()


def get_metric_trend(metric: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get trend data for a specific metric
    
    Args:
        metric: The metric to track
        days: Number of days of history
        
    Returns:
        Trend data points
    """
    stats_calculator = AdminDashboardStats()
    return stats_calculator.get_trend_data(metric, days)
