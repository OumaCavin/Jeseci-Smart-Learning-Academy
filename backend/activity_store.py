# Activity Store Module for User Activity Tracking
# This module handles all database operations for user activities and streaks

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

# Import database connection
from database import get_db_connection

# Database schema configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")

# Activity types enum
ACTIVITY_TYPES = [
    'LESSON_COMPLETED',
    'COURSE_STARTED',
    'COURSE_COMPLETED',
    'QUIZ_PASSED',
    'ACHIEVEMENT_EARNED',
    'STREAK_MILESTONE',
    'LOGIN',
    'CONTENT_VIEWED',
    'AI_GENERATED',
    'LEARNING_PATH_STARTED',
    'LEARNING_PATH_COMPLETED',
    'CONCEPT_MASTERED',
    'BADGE_EARNED'
]

# Activity type display configurations
ACTIVITY_CONFIG = {
    'LESSON_COMPLETED': {
        'icon': 'book-open',
        'color': 'blue',
        'title_template': 'Completed lesson: {name}',
        'xp': 10
    },
    'COURSE_STARTED': {
        'icon': 'play',
        'color': 'green',
        'title_template': 'Started course: {name}',
        'xp': 5
    },
    'COURSE_COMPLETED': {
        'icon': 'check-circle',
        'color': 'emerald',
        'title_template': 'Completed course: {name}',
        'xp': 50
    },
    'QUIZ_PASSED': {
        'icon': 'award',
        'color': 'yellow',
        'title_template': 'Passed quiz: {name} ({score}%)',
        'xp': 25
    },
    'ACHIEVEMENT_EARNED': {
        'icon': 'trophy',
        'color': 'amber',
        'title_template': 'Earned achievement: {name}',
        'xp': 100
    },
    'STREAK_MILESTONE': {
        'icon': 'flame',
        'color': 'orange',
        'title_template': '{days} day learning streak!',
        'xp': 20
    },
    'LOGIN': {
        'icon': 'user',
        'color': 'gray',
        'title_template': 'Logged in to Jeseci Academy',
        'xp': 1
    },
    'CONTENT_VIEWED': {
        'icon': 'eye',
        'color': 'indigo',
        'title_template': 'Viewed: {name}',
        'xp': 2
    },
    'AI_GENERATED': {
        'icon': 'bot',
        'color': 'purple',
        'title_template': 'AI generated: {name}',
        'xp': 5
    },
    'LEARNING_PATH_STARTED': {
        'icon': 'map',
        'color': 'cyan',
        'title_template': 'Started learning path: {name}',
        'xp': 10
    },
    'LEARNING_PATH_COMPLETED': {
        'icon': 'flag',
        'color': 'teal',
        'title_template': 'Completed learning path: {name}',
        'xp': 75
    },
    'CONCEPT_MASTERED': {
        'icon': 'lightbulb',
        'color': 'lime',
        'title_template': 'Mastered concept: {name}',
        'xp': 30
    },
    'BADGE_EARNED': {
        'icon': 'medal',
        'color': 'rose',
        'title_template': 'Earned badge: {name}',
        'xp': 50
    }
}


def log_activity(
    user_id: str,
    activity_type: str,
    title: str,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    xp_earned: Optional[int] = None
) -> Dict[str, Any]:
    """
    Log a new user activity
    
    Args:
        user_id: The user's UUID
        activity_type: Type of activity (from ACTIVITY_TYPES)
        title: Activity title
        description: Optional detailed description
        metadata: Optional additional context data
        xp_earned: Optional XP points earned
        
    Returns:
        dict with activity data including id
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Resolve numeric ID from string UUID
            cur.execute(f"SELECT id FROM {DB_SCHEMA}.users WHERE user_id = %s", (user_id,))
            user_res = cur.fetchone()
            if not user_res:
                return {'success': False, 'error': 'User not found'}
            user_numeric_id = user_res[0]
            
            # Validate activity type
            if activity_type not in ACTIVITY_TYPES:
                raise ValueError(f"Invalid activity type: {activity_type}")
            
            # Get XP from config if not provided
            if xp_earned is None:
                xp_earned = ACTIVITY_CONFIG.get(activity_type, {}).get('xp', 0)
            
            # Insert the activity
            activity_id = str(uuid.uuid4())
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            cur.execute(
                f"""
                INSERT INTO {DB_SCHEMA}.user_activities (
                    id, user_id, activity_type, title, description, metadata, points_earned
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id, created_at
                """,
                (
                    activity_id, user_numeric_id, activity_type,
                    title, description, metadata_json, xp_earned
                )
            )
            
            result = cur.fetchone()
            conn.commit()
            
            # Update streak if applicable
            if activity_type in ['LESSON_COMPLETED', 'CONTENT_VIEWED', 'QUIZ_PASSED']:
                update_streak(user_id, activity_type)
            
            return {
                'success': True,
                'activity': {
                    'id': activity_id,
                    'user_id': user_id,
                    'type': activity_type,
                    'title': title,
                    'description': description,
                    'metadata': metadata,
                    'xp_earned': xp_earned,
                    'created_at': result[1].isoformat() if result[1] else datetime.now().isoformat()
                }
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error logging activity: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()


def get_user_activities(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    activity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get activities for a user with pagination and filtering
    
    Args:
        user_id: The user's UUID
        limit: Maximum number of activities to return
        offset: Number of activities to skip
        activity_type: Optional type filter
        start_date: Optional start date filter (ISO format)
        end_date: Optional end date filter (ISO format)
        
    Returns:
        dict with activities list and metadata
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Resolve numeric ID from string UUID
            cur.execute(f"SELECT id FROM {DB_SCHEMA}.users WHERE user_id = %s", (user_id,))
            user_res = cur.fetchone()
            if not user_res:
                return {
                    'success': False,
                    'error': 'User not found',
                    'activities': [],
                    'total_count': 0,
                    'has_more': False
                }
            user_numeric_id = user_res[0]
            
            # Build query - JOIN users table to filter by string UUID but select from activities
            base_query = f"""
                SELECT a.id, u.user_id, a.activity_type, a.title, a.description,
                       a.meta_data, a.points_earned, a.created_at
                FROM {DB_SCHEMA}.user_activities a
                JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                WHERE u.user_id = %s
            """
            params = [user_id]
            
            if activity_type:
                base_query += " AND activity_type = %s"
                params.append(activity_type)
            
            if start_date:
                base_query += " AND created_at >= %s"
                params.append(start_date)
            
            if end_date:
                base_query += " AND created_at <= %s"
                params.append(end_date)
            
            # Get total count
            # Fix: Use split to safely get everything after the first SELECT columns
            # This avoids issues with multi-line strings in the base_query
            from_clause = base_query.split("FROM", 1)[1]
            count_query = "SELECT COUNT(*) FROM" + from_clause
            cur.execute(count_query, params)
            total_count = cur.fetchone()[0]
            
            # Add ordering and pagination
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(base_query, params)
            rows = cur.fetchall()
            
            activities = []
            for row in rows:
                metadata = row[5]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                activities.append({
                    'id': str(row[0]),
                    'user_id': str(row[1]),
                    'type': row[2],
                    'title': row[3],
                    'description': row[4],
                    'metadata': metadata,
                    'xp_earned': row[6],
                    'created_at': row[7].isoformat() if row[7] else None,
                    'config': ACTIVITY_CONFIG.get(row[2], {})
                })
            
            return {
                'success': True,
                'activities': activities,
                'total_count': total_count,
                'has_more': (offset + len(activities)) < total_count
            }
            
    except Exception as e:
        print(f"Error fetching activities: {e}")
        return {
            'success': False,
            'error': str(e),
            'activities': [],
            'total_count': 0,
            'has_more': False
        }
    finally:
        conn.close()


def get_activity_summary(user_id: str, timeframe: str = 'week') -> Dict[str, Any]:
    """
    Get activity summary statistics for a user
    
    Args:
        user_id: The user's UUID
        timeframe: 'day', 'week', 'month', or 'all'
        
    Returns:
        dict with activity statistics
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Resolve numeric ID from string UUID
            cur.execute(f"SELECT id FROM {DB_SCHEMA}.users WHERE user_id = %s", (user_id,))
            user_res = cur.fetchone()
            if not user_res:
                return {
                    'success': False,
                    'error': 'User not found',
                    'summary': {
                        'total_activities': 0,
                        'today_activities': 0,
                        'total_xp_earned': 0,
                        'activities_by_type': {},
                        'timeframe': timeframe
                    }
                }
            user_numeric_id = user_res[0]
            
            # Calculate date filter
            now = datetime.now()
            if timeframe == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif timeframe == 'week':
                start_date = now - timedelta(days=7)
            elif timeframe == 'month':
                start_date = now - timedelta(days=30)
            else:
                start_date = None
            
            # Get activity counts by type
            if start_date:
                cur.execute(
                    f"""
                    SELECT a.activity_type, COUNT(*) as count
                    FROM {DB_SCHEMA}.user_activities a
                    JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                    WHERE u.user_id = %s AND a.created_at >= %s
                    GROUP BY a.activity_type
                    ORDER BY count DESC
                    """,
                    (user_id, start_date)
                )
            else:
                cur.execute(
                    f"""
                    SELECT a.activity_type, COUNT(*) as count
                    FROM {DB_SCHEMA}.user_activities a
                    JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                    WHERE u.user_id = %s
                    GROUP BY a.activity_type
                    ORDER BY count DESC
                    """,
                    (user_id,)
                )
            
            type_counts = {row[0]: row[1] for row in cur.fetchall()}
            
            # Get total XP earned
            if start_date:
                cur.execute(
                    f"""
                    SELECT COALESCE(SUM(a.points_earned), 0) as total_xp
                    FROM {DB_SCHEMA}.user_activities a
                    JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                    WHERE u.user_id = %s AND a.created_at >= %s
                    """,
                    (user_id, start_date)
                )
            else:
                cur.execute(
                    f"""
                    SELECT COALESCE(SUM(a.points_earned), 0) as total_xp
                    FROM {DB_SCHEMA}.user_activities a
                    JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                    WHERE u.user_id = %s
                    """,
                    (user_id,)
                )
            
            total_xp = cur.fetchone()[0]
            
            # Get activity counts
            cur.execute(
                f"""
                SELECT COUNT(*) as total_activities
                FROM {DB_SCHEMA}.user_activities a
                JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                WHERE u.user_id = %s
                """,
                (user_id,)
            )
            total_activities = cur.fetchone()[0]
            
            # Get today's activities
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            cur.execute(
                f"""
                SELECT COUNT(*) as today_activities
                FROM {DB_SCHEMA}.user_activities a
                JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                WHERE u.user_id = %s AND a.created_at >= %s
                """,
                (user_id, today_start)
            )
            today_activities = cur.fetchone()[0]
            
            return {
                'success': True,
                'summary': {
                    'total_activities': total_activities,
                    'today_activities': today_activities,
                    'total_xp_earned': total_xp,
                    'activities_by_type': type_counts,
                    'timeframe': timeframe
                }
            }
            
    except Exception as e:
        print(f"Error fetching activity summary: {e}")
        return {
            'success': False,
            'error': str(e),
            'summary': {
                'total_activities': 0,
                'today_activities': 0,
                'total_xp_earned': 0,
                'activities_by_type': {},
                'timeframe': timeframe
            }
        }
    finally:
        conn.close()


def get_activity_streak(user_id: str) -> Dict[str, Any]:
    """
    Get learning streak data for a user
    
    Args:
        user_id: The user's UUID
        
    Returns:
        dict with streak information
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Resolve numeric ID from string UUID
            cur.execute(f"SELECT id FROM {DB_SCHEMA}.users WHERE user_id = %s", (user_id,))
            user_res = cur.fetchone()
            if not user_res:
                return {
                    'success': False,
                    'error': 'User not found',
                    'streak': {
                        'current_streak': 0,
                        'longest_streak': 0,
                        'last_activity_date': None,
                        'streak_start_date': None
                    }
                }
            user_numeric_id = user_res[0]
            
            # Get current streak from activities
            cur.execute(
                f"""
                SELECT DISTINCT DATE(a.created_at) as activity_date
                FROM {DB_SCHEMA}.user_activities a
                JOIN {DB_SCHEMA}.users u ON a.user_id = u.id
                WHERE u.user_id = %s AND a.activity_type IN ('LESSON_COMPLETED', 'CONTENT_VIEWED', 'QUIZ_PASSED')
                ORDER BY activity_date DESC
                """,
                (user_id,)
            )
            
            activity_dates = [row[0] for row in cur.fetchall()]
            
            if not activity_dates:
                return {
                    'success': True,
                    'streak': {
                        'current_streak': 0,
                        'longest_streak': 0,
                        'last_activity_date': None,
                        'streak_start_date': None
                    }
                }
            
            # Calculate current streak
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            current_streak = 0
            last_activity = None
            
            # Check if there's activity today or yesterday to maintain streak
            if activity_dates:
                last_activity = activity_dates[0]
                if last_activity == today or last_activity == yesterday:
                    # Calculate consecutive days
                    current_streak = 1
                    for i in range(1, len(activity_dates)):
                        expected_date = last_activity - timedelta(days=i)
                        if activity_dates[i] == expected_date:
                            current_streak += 1
                        else:
                            break
            
            # Calculate longest streak
            longest_streak = 1
            temp_streak = 1
            for i in range(1, len(activity_dates)):
                if activity_dates[i] == activity_dates[i-1] - timedelta(days=1):
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
            
            # Get streak from database (use numeric_id for user_activity_streaks)
            cur.execute(
                f"""
                SELECT current_streak, longest_streak, last_activity_date, streak_start_date
                FROM {DB_SCHEMA}.user_activity_streaks
                WHERE user_id = %s AND streak_type = 'LESSON_COMPLETED'
                """,
                (user_numeric_id,)
            )
            
            db_streak = cur.fetchone()
            
            if db_streak and db_streak[0]:
                # Update if we have a higher current streak
                current_streak = max(current_streak, db_streak[0])
                longest_streak = max(longest_streak, db_streak[1] or 0)
                
                # Update database (use numeric_id)
                cur.execute(
                    f"""
                    UPDATE {DB_SCHEMA}.user_activity_streaks
                    SET current_streak = %s, longest_streak = %s, 
                        last_activity_date = %s, updated_at = NOW()
                    WHERE user_id = %s AND streak_type = 'LESSON_COMPLETED'
                    """,
                    (current_streak, longest_streak, last_activity, user_numeric_id)
                )
            else:
                # Create new streak record (use numeric_id)
                cur.execute(
                    f"""
                    INSERT INTO {DB_SCHEMA}.user_activity_streaks (
                        user_id, streak_type, current_streak, longest_streak, 
                        last_activity_date, streak_start_date
                    ) VALUES (
                        %s, 'LESSON_COMPLETED', %s, %s, %s, %s
                    )
                    ON CONFLICT (user_id, streak_type) DO UPDATE SET
                        current_streak = EXCLUDED.current_streak,
                        longest_streak = EXCLUDED.longest_streak,
                        last_activity_date = EXCLUDED.last_activity_date
                    """,
                    (user_numeric_id, current_streak, longest_streak, last_activity, last_activity)
                )
            
            conn.commit()
            
            return {
                'success': True,
                'streak': {
                    'current_streak': current_streak,
                    'longest_streak': longest_streak,
                    'last_activity_date': last_activity.isoformat() if last_activity else None,
                    'streak_start_date': last_activity.isoformat() if last_activity and current_streak == 1 else None
                }
            }
            
    except Exception as e:
        print(f"Error fetching activity streak: {e}")
        return {
            'success': False,
            'error': str(e),
            'streak': {
                'current_streak': 0,
                'longest_streak': 0,
                'last_activity_date': None,
                'streak_start_date': None
            }
        }
    finally:
        conn.close()


def update_streak(user_id: str, activity_type: str) -> Dict[str, Any]:
    """
    Update streak data when user completes an activity
    
    Args:
        user_id: The user's UUID
        activity_type: Type of activity completed
        
    Returns:
        dict with updated streak info
    """
    if activity_type not in ['LESSON_COMPLETED', 'CONTENT_VIEWED', 'QUIZ_PASSED']:
        return {'success': True, 'message': 'Activity type does not affect streak'}
    
    return get_activity_streak(user_id)


def delete_user_activities(user_id: str, older_than_days: int = 365) -> Dict[str, Any]:
    """
    Delete old activities (for data cleanup)
    
    Args:
        user_id: The user's UUID
        older_than_days: Delete activities older than this many days
        
    Returns:
        dict with deletion count
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Resolve numeric ID from string UUID
            cur.execute(f"SELECT id FROM {DB_SCHEMA}.users WHERE user_id = %s", (user_id,))
            user_res = cur.fetchone()
            if not user_res:
                return {
                    'success': False,
                    'error': 'User not found',
                    'deleted_count': 0
                }
            user_numeric_id = user_res[0]
            
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
            cur.execute(
                f"""
                DELETE FROM {DB_SCHEMA}.user_activities
                WHERE user_id = %s AND created_at < %s
                """,
                (user_numeric_id, cutoff_date)
            )
            
            deleted_count = cur.rowcount
            conn.commit()
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'message': f'Deleted {deleted_count} activities older than {older_than_days} days'
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error deleting activities: {e}")
        return {
            'success': False,
            'error': str(e),
            'deleted_count': 0
        }
    finally:
        conn.close()


# Helper functions for common activity logging

def log_lesson_completed(
    user_id: str,
    lesson_name: str,
    lesson_id: str,
    course_name: Optional[str] = None,
    course_id: Optional[str] = None
) -> Dict[str, Any]:
    """Log a lesson completion"""
    title = f"Completed lesson: {lesson_name}"
    description = f"Great job completing {lesson_name}" + (f" in {course_name}" if course_name else "!")
    
    return log_activity(
        user_id=user_id,
        activity_type='LESSON_COMPLETED',
        title=title,
        description=description,
        metadata={
            'lesson_name': lesson_name,
            'lesson_id': lesson_id,
            'course_name': course_name,
            'course_id': course_id
        },
        xp_earned=10
    )


def log_course_started(
    user_id: str,
    course_name: str,
    course_id: str
) -> Dict[str, Any]:
    """Log a course start"""
    return log_activity(
        user_id=user_id,
        activity_type='COURSE_STARTED',
        title=f"Started course: {course_name}",
        description=f"You've begun your journey through {course_name}",
        metadata={
            'course_name': course_name,
            'course_id': course_id
        },
        xp_earned=5
    )


def log_quiz_passed(
    user_id: str,
    quiz_name: str,
    quiz_id: str,
    score: int,
    passing_score: int = 70
) -> Dict[str, Any]:
    """Log a quiz pass"""
    return log_activity(
        user_id=user_id,
        activity_type='QUIZ_PASSED',
        title=f"Passed quiz: {quiz_name} ({score}%)",
        description=f"Excellent work! You scored {score}% on {quiz_name}",
        metadata={
            'quiz_name': quiz_name,
            'quiz_id': quiz_id,
            'score': score,
            'passing_score': passing_score,
            'passed': score >= passing_score
        },
        xp_earned=25
    )


def log_achievement_earned(
    user_id: str,
    achievement_name: str,
    achievement_id: str,
    badge_icon: Optional[str] = None
) -> Dict[str, Any]:
    """Log an achievement"""
    return log_activity(
        user_id=user_id,
        activity_type='ACHIEVEMENT_EARNED',
        title=f"Earned achievement: {achievement_name}",
        description=f"Congratulations! You've unlocked the {achievement_name} achievement",
        metadata={
            'achievement_name': achievement_name,
            'achievement_id': achievement_id,
            'badge_icon': badge_icon
        },
        xp_earned=100
    )


def log_login(user_id: str) -> Dict[str, Any]:
    """Log a user login"""
    return log_activity(
        user_id=user_id,
        activity_type='LOGIN',
        title="Logged in to Jeseci Academy",
        description="Welcome back! Ready to continue learning?",
        xp_earned=1
    )


def log_content_viewed(
    user_id: str,
    content_name: str,
    content_id: str,
    content_type: str
) -> Dict[str, Any]:
    """Log content view"""
    return log_activity(
        user_id=user_id,
        activity_type='CONTENT_VIEWED',
        title=f"Viewed: {content_name}",
        metadata={
            'content_name': content_name,
            'content_id': content_id,
            'content_type': content_type
        },
        xp_earned=2
    )


# =============================================================================
# NEW FUNCTIONS FOR DASHBOARD INTEGRATION
# =============================================================================

def get_recent_activity(
    user_id: str,
    limit: int = 20,
    activity_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent user activities - Wrapper for get_user_activities
    
    This function provides compatibility with the walker expectations.
    
    Args:
        user_id: The user's UUID
        limit: Maximum number of activities to return
        activity_type: Optional type filter
        
    Returns:
        dict with activities list and metadata
    """
    result = get_user_activities(
        user_id=user_id,
        limit=limit,
        offset=0,
        activity_type=activity_type
    )
    
    # Transform activity types to frontend-compatible format
    if result.get('success') and 'activities' in result:
        result['activities'] = _transform_activities_for_frontend(result['activities'])
    
    return result


def get_learning_streak(user_id: str) -> Dict[str, Any]:
    """
    Get learning streak for a user
    
    Wrapper function that provides the expected return format for the walker.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        dict with streak information
    """
    result = get_activity_streak(user_id)
    
    if result.get('success'):
        return {
            'success': True,
            'streak': result.get('streak', {}),
            'current_streak': result.get('streak', {}).get('current_streak', 0),
            'longest_streak': result.get('streak', {}).get('longest_streak', 0),
            'last_activity_date': result.get('streak', {}).get('last_activity_date'),
            'streak_start_date': result.get('streak', {}).get('streak_start_date')
        }
    
    return result


def get_dashboard_metrics(user_id: str) -> Dict[str, Any]:
    """
    Get dashboard metrics for a user
    
    Returns comprehensive metrics for the user dashboard including:
    - total_study_time: Total study time in minutes
    - lessons_completed: Number of completed lessons
    - courses_completed: Number of completed courses
    - current_streak: Current learning streak in days
    - average_quiz_score: Average quiz score
    - achievements_earned: Number of achievements earned
    - xp_earned: Total experience points
    
    Args:
        user_id: The user's UUID
        
    Returns:
        dict with dashboard metrics
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Resolve numeric ID from string UUID
            cur.execute(f"SELECT id FROM {DB_SCHEMA}.users WHERE user_id = %s", (user_id,))
            user_res = cur.fetchone()
            if not user_res:
                return {
                    'success': False,
                    'error': 'User not found',
                    'metrics': None
                }
            user_numeric_id = user_res[0]
            
            # Get total study time from learning sessions
            cur.execute(
                f"""
                SELECT COALESCE(SUM(duration_seconds), 0) 
                FROM {DB_SCHEMA}.learning_sessions
                WHERE user_id = %s
                """,
                (user_numeric_id,)
            )
            total_seconds = cur.fetchone()[0] or 0
            total_study_time = round(total_seconds / 60, 2)  # Convert to minutes
            
            # Get lessons completed
            cur.execute(
                f"""
                SELECT COUNT(*) 
                FROM {DB_SCHEMA}.user_lesson_progress
                WHERE user_id = %s AND is_completed = true
                """,
                (user_numeric_id,)
            )
            lessons_completed = cur.fetchone()[0] or 0
            
            # Get courses/learning paths completed
            cur.execute(
                f"""
                SELECT COUNT(*) 
                FROM {DB_SCHEMA}.user_learning_paths
                WHERE user_id = %s AND progress_percent >= 100
                """,
                (user_numeric_id,)
            )
            courses_completed = cur.fetchone()[0] or 0
            
            # Get average quiz score
            cur.execute(
                f"""
                SELECT AVG(score) 
                FROM {DB_SCHEMA}.quiz_attempts
                WHERE user_id = %s AND score IS NOT NULL
                """,
                (user_numeric_id,)
            )
            avg_score_result = cur.fetchone()[0]
            average_quiz_score = round(avg_score_result, 1) if avg_score_result else 0
            
            # Get achievements earned
            cur.execute(
                f"""
                SELECT COUNT(*) 
                FROM {DB_SCHEMA}.user_achievements
                WHERE user_id = %s
                """,
                (user_numeric_id,)
            )
            achievements_earned = cur.fetchone()[0] or 0
            
            # Get total XP earned
            cur.execute(
                f"""
                SELECT COALESCE(SUM(points_earned), 0) 
                FROM {DB_SCHEMA}.user_activities
                WHERE user_id = %s
                """,
                (user_numeric_id,)
            )
            xp_earned = cur.fetchone()[0] or 0
            
            # Get current streak
            streak_result = get_activity_streak(user_id)
            current_streak = streak_result.get('streak', {}).get('current_streak', 0)
            
            return {
                'success': True,
                'metrics': {
                    'total_study_time': total_study_time,
                    'lessons_completed': lessons_completed,
                    'courses_completed': courses_completed,
                    'current_streak': current_streak,
                    'average_quiz_score': average_quiz_score,
                    'achievements_earned': achievements_earned,
                    'xp_earned': xp_earned,
                    'last_active': datetime.now().isoformat()
                }
            }

    except Exception as e:
        print(f"Error fetching dashboard metrics: {e}")
        return {
            'success': False,
            'error': str(e),
            'metrics': None
        }
    finally:
        conn.close()


def update_learning_preferences(user_id: str, learning_style: str = None, skill_level: str = None,
                                 daily_goal_minutes: int = None, preferred_difficulty: str = None,
                                 preferred_content_type: str = None, dark_mode: bool = None,
                                 auto_play_videos: bool = None) -> Dict[str, Any]:
    """
    Update user's learning preferences in the database

    Args:
        user_id: The user's UUID
        learning_style: Preferred learning style (visual, auditory, kinesthetic, reading)
        skill_level: Current skill level (beginner, intermediate, advanced)
        daily_goal_minutes: Daily learning goal in minutes
        preferred_difficulty: Preferred content difficulty
        preferred_content_type: Preferred content type (text, video, interactive, mixed)
        dark_mode: Whether dark mode is enabled
        auto_play_videos: Whether videos should auto-play

    Returns:
        Dict with success status and updated preferences
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Check if preferences exist
        cursor.execute(f"""
            SELECT user_id FROM {DB_SCHEMA}.learning_preferences WHERE user_id = %s
        """, (user_id,))
        existing = cursor.fetchone()

        # Build dynamic update
        updates = []
        params = []

        if learning_style is not None:
            updates.append("learning_style = %s")
            params.append(learning_style)
        if skill_level is not None:
            updates.append("skill_level = %s")
            params.append(skill_level)
        if daily_goal_minutes is not None:
            updates.append("daily_goal_minutes = %s")
            params.append(daily_goal_minutes)
        if preferred_difficulty is not None:
            updates.append("preferred_difficulty = %s")
            params.append(preferred_difficulty)
        if preferred_content_type is not None:
            updates.append("preferred_content_type = %s")
            params.append(preferred_content_type)
        if dark_mode is not None:
            updates.append("dark_mode = %s")
            params.append(dark_mode)
        if auto_play_videos is not None:
            updates.append("auto_play_videos = %s")
            params.append(auto_play_videos)

        if not updates:
            # No preferences to update, just return current
            cursor.execute(f"""
                SELECT * FROM {DB_SCHEMA}.learning_preferences WHERE user_id = %s
            """, (user_id,))
            prefs = cursor.fetchone()
            return {'success': True, 'preferences': prefs}

        params.append(user_id)

        if existing:
            # Update existing preferences
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.learning_preferences
                SET {', '.join(updates)},
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                RETURNING *
            """, params)
        else:
            # Insert new preferences
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.learning_preferences
                (user_id, learning_style, skill_level, daily_goal_minutes, preferred_difficulty,
                 preferred_content_type, dark_mode, auto_play_videos)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (user_id,
                  learning_style or 'visual',
                  skill_level or 'beginner',
                  daily_goal_minutes or 30,
                  preferred_difficulty or 'intermediate',
                  preferred_content_type or 'mixed',
                  dark_mode or False,
                  auto_play_videos or True))

        preferences = cursor.fetchone()
        conn.commit()

        print(f"Learning preferences updated for user: {user_id}")
        return {'success': True, 'preferences': preferences}

    except Exception as e:
        print(f"Error updating learning preferences: {e}")
        conn.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()


def _transform_activities_for_frontend(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform backend activity types to frontend-compatible formats
    
    Maps backend activity types (e.g., 'LESSON_COMPLETED') to frontend 
    activity types (e.g., 'execution', 'user', 'sync', etc.)
    
    Args:
        activities: List of activity dictionaries from backend
        
    Returns:
        List of transformed activities with frontend-compatible types
    """
    # Mapping from backend activity types to frontend types
    ACTIVITY_TYPE_MAP = {
        'LESSON_COMPLETED': 'execution',
        'COURSE_STARTED': 'user',
        'COURSE_COMPLETED': 'user',
        'QUIZ_PASSED': 'execution',
        'ACHIEVEMENT_EARNED': 'collaboration',
        'STREAK_MILESTONE': 'user',
        'LOGIN': 'system',
        'CONTENT_VIEWED': 'execution',
        'AI_GENERATED': 'system',
        'LEARNING_PATH_STARTED': 'user',
        'LEARNING_PATH_COMPLETED': 'user',
        'CONCEPT_MASTERED': 'execution',
        'BADGE_EARNED': 'collaboration'
    }
    
    transformed = []
    for activity in activities:
        backend_type = activity.get('type', '')
        frontend_type = ACTIVITY_TYPE_MAP.get(backend_type, 'system')
        
        # Create frontend-compatible activity item
        transformed_activity = {
            'id': activity.get('id', ''),
            'type': frontend_type,
            'title': activity.get('title', ''),
            'description': activity.get('description', ''),
            'timestamp': activity.get('created_at', ''),
            'userId': activity.get('user_id', ''),
            'userName': activity.get('userName', ''),
            'status': 'success',
            'metadata': activity.get('metadata', {}),
            'priority': 'medium'
        }
        transformed.append(transformed_activity)
    
    return transformed
