# Notification store module for managing user notifications
# This module handles all database operations for notifications

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

# Import database connection
from database import get_db_connection

# Database schema configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")

# Notification types enum
NOTIFICATION_TYPES = [
    'ACHIEVEMENT',
    'COURSE_MILESTONE',
    'CONTENT_UPDATE',
    'COMMUNITY_REPLY',
    'STREAK_REMINDER',
    'AI_RESPONSE',
    'SYSTEM_ANNOUNCEMENT'
]

# Default notification preferences
DEFAULT_PREFERENCES = {
    'email_enabled': True,
    'push_enabled': True,
    'types_config': {
        'ACHIEVEMENT': True,
        'COURSE_MILESTONE': True,
        'CONTENT_UPDATE': True,
        'COMMUNITY_REPLY': True,
        'STREAK_REMINDER': True,
        'AI_RESPONSE': True,
        'SYSTEM_ANNOUNCEMENT': True
    }
}


def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    link: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new notification for a user
    
    Args:
        user_id: The user's UUID
        notification_type: Type of notification (from NOTIFICATION_TYPES)
        title: Notification title
        message: Notification message body
        link: Optional URL to navigate to
        metadata: Optional additional context data
        
    Returns:
        dict with notification data including id
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Validate notification type
            if notification_type not in NOTIFICATION_TYPES:
                raise ValueError(f"Invalid notification type: {notification_type}")
            
            # Check if user has preferences and if this type is enabled
            cur.execute(
                """
                SELECT types_config FROM {}.notification_preferences 
                WHERE user_id = %s
                """.format(DB_SCHEMA),
                (user_id,)
            )
            pref_result = cur.fetchone()
            
            if pref_result:
                types_config = pref_result[0]
                if isinstance(types_config, str):
                    types_config = json.loads(types_config)
                if not types_config.get(notification_type, True):
                    # User has disabled this notification type
                    return {
                        'success': False,
                        'message': f'Notifications of type {notification_type} are disabled for this user'
                    }
            
            # Insert the notification
            notification_id = str(uuid.uuid4())
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            cur.execute(
                """
                INSERT INTO {}.notifications (
                    id, user_id, type, title, message, link, metadata
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id, created_at
                """.format(DB_SCHEMA),
                (
                    notification_id, user_id, notification_type,
                    title, message, link, metadata_json
                )
            )
            
            result = cur.fetchone()
            conn.commit()
            
            return {
                'success': True,
                'notification': {
                    'id': notification_id,
                    'user_id': user_id,
                    'type': notification_type,
                    'title': title,
                    'message': message,
                    'link': link,
                    'is_read': False,
                    'is_archived': False,
                    'metadata': metadata,
                    'created_at': result[1].isoformat() if result[1] else datetime.now().isoformat()
                }
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error creating notification: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()


def get_notifications(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    filter_type: Optional[str] = None,
    unread_only: bool = False
) -> Dict[str, Any]:
    """
    Get notifications for a user
    
    Args:
        user_id: The user's UUID
        limit: Maximum number of notifications to return
        offset: Number of notifications to skip
        filter_type: Optional type to filter by
        unread_only: If True, only return unread notifications
        
    Returns:
        dict with notifications list and metadata
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Build query
            base_query = """
                SELECT id, user_id, type, title, message, link, 
                       is_read, is_archived, metadata, created_at
                FROM {}.notifications
                WHERE user_id = %s AND is_archived = FALSE
            """.format(DB_SCHEMA)
            params = [user_id]
            
            if filter_type:
                base_query += " AND type = %s"
                params.append(filter_type)
            
            if unread_only:
                base_query += " AND is_read = FALSE"
            
            # Get total count
            count_query = "SELECT COUNT(*) " + base_query.replace("SELECT id, user_id, type, title, message, link, is_read, is_archived, metadata, created_at", "")
            cur.execute(count_query, params)
            total_count = cur.fetchone()[0]
            
            # Get unread count
            unread_query = "SELECT COUNT(*) FROM {}.notifications WHERE user_id = %s AND is_archived = FALSE AND is_read = FALSE".format(DB_SCHEMA)
            cur.execute(unread_query, (user_id,))
            unread_count = cur.fetchone()[0]
            
            # Add ordering and pagination
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(base_query, params)
            rows = cur.fetchall()
            
            notifications_list = []
            for row in rows:
                metadata = row[8]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                notifications_list.append({
                    'id': str(row[0]),
                    'user_id': str(row[1]),
                    'type': row[2],
                    'title': row[3],
                    'message': row[4],
                    'link': row[5],
                    'is_read': row[6],
                    'is_archived': row[7],
                    'metadata': metadata,
                    'created_at': row[9].isoformat() if row[9] else None
                })
            
            return {
                'success': True,
                'notifications': notifications_list,
                'total_count': total_count,
                'unread_count': unread_count,
                'has_more': (offset + len(notifications_list)) < total_count
            }
            
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return {
            'success': False,
            'error': str(e),
            'notifications': [],
            'total_count': 0,
            'unread_count': 0,
            'has_more': False
        }
    finally:
        conn.close()


def get_unread_count(user_id: str) -> Dict[str, Any]:
    """
    Get the count of unread notifications for a user
    
    Args:
        user_id: The user's UUID
        
    Returns:
        dict with unread_count
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM {}.notifications
                WHERE user_id = %s AND is_archived = FALSE AND is_read = FALSE
                """.format(DB_SCHEMA),
                (user_id,)
            )
            count = cur.fetchone()[0]
            
            return {
                'success': True,
                'unread_count': count
            }
            
    except Exception as e:
        print(f"Error fetching unread count: {e}")
        return {
            'success': False,
            'error': str(e),
            'unread_count': 0
        }
    finally:
        conn.close()


def mark_as_read(user_id: str, notification_ids: List[str]) -> Dict[str, Any]:
    """
    Mark one or more notifications as read
    
    Args:
        user_id: The user's UUID
        notification_ids: List of notification IDs to mark as read
        
    Returns:
        dict with success status and updated count
    """
    if not notification_ids:
        return {'success': True, 'updated_count': 0}
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Convert UUIDs to strings and ensure proper format
            id_list = [str(uuid.UUID(nid)) for nid in notification_ids]
            
            cur.execute(
                """
                UPDATE {}.notifications
                SET is_read = TRUE
                WHERE user_id = %s AND id = ANY(%s) AND is_read = FALSE
                """.format(DB_SCHEMA),
                (user_id, id_list)
            )
            
            updated_count = cur.rowcount
            conn.commit()
            
            return {
                'success': True,
                'updated_count': updated_count
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error marking notifications as read: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_count': 0
        }
    finally:
        conn.close()


def mark_all_as_read(user_id: str) -> Dict[str, Any]:
    """
    Mark all notifications as read for a user
    
    Args:
        user_id: The user's UUID
        
    Returns:
        dict with success status and updated count
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE {}.notifications
                SET is_read = TRUE
                WHERE user_id = %s AND is_read = FALSE
                """.format(DB_SCHEMA),
                (user_id,)
            )
            
            updated_count = cur.rowcount
            conn.commit()
            
            return {
                'success': True,
                'updated_count': updated_count
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error marking all notifications as read: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_count': 0
        }
    finally:
        conn.close()


def delete_notification(user_id: str, notification_id: str) -> Dict[str, Any]:
    """
    Soft delete a notification (mark as archived)
    
    Args:
        user_id: The user's UUID
        notification_id: The notification's UUID
        
    Returns:
        dict with success status
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE {}.notifications
                SET is_archived = TRUE
                WHERE user_id = %s AND id = %s
                """.format(DB_SCHEMA),
                (user_id, notification_id)
            )
            
            success = cur.rowcount > 0
            conn.commit()
            
            return {
                'success': success,
                'message': 'Notification deleted' if success else 'Notification not found'
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error deleting notification: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()


def get_notification_preferences(user_id: str) -> Dict[str, Any]:
    """
    Get notification preferences for a user
    
    Args:
        user_id: The user's UUID
        
    Returns:
        dict with notification preferences
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT email_enabled, push_enabled, types_config, created_at, updated_at
                FROM {}.notification_preferences
                WHERE user_id = %s
                """.format(DB_SCHEMA),
                (user_id,)
            )
            
            row = cur.fetchone()
            
            if row:
                types_config = row[2]
                if isinstance(types_config, str):
                    types_config = json.loads(types_config)
                
                return {
                    'success': True,
                    'preferences': {
                        'user_id': user_id,
                        'email_enabled': row[0],
                        'push_enabled': row[1],
                        'types_config': types_config,
                        'created_at': row[3].isoformat() if row[3] else None,
                        'updated_at': row[4].isoformat() if row[4] else None
                    }
                }
            else:
                # Return default preferences if none exist
                return {
                    'success': True,
                    'preferences': {
                        'user_id': user_id,
                        **DEFAULT_PREFERENCES,
                        'created_at': None,
                        'updated_at': None
                    }
                }
                
    except Exception as e:
        print(f"Error fetching notification preferences: {e}")
        return {
            'success': False,
            'error': str(e),
            'preferences': {**DEFAULT_PREFERENCES}
        }
    finally:
        conn.close()


def update_notification_preferences(
    user_id: str,
    email_enabled: Optional[bool] = None,
    push_enabled: Optional[bool] = None,
    types_config: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Update notification preferences for a user
    
    Args:
        user_id: The user's UUID
        email_enabled: Whether to enable email notifications
        push_enabled: Whether to enable push notifications
        types_config: Dict mapping notification types to enabled status
        
    Returns:
        dict with updated preferences
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Build dynamic update query
            update_fields = []
            params = []
            
            if email_enabled is not None:
                update_fields.append("email_enabled = %s")
                params.append(email_enabled)
            
            if push_enabled is not None:
                update_fields.append("push_enabled = %s")
                params.append(push_enabled)
            
            if types_config is not None:
                update_fields.append("types_config = %s")
                params.append(json.dumps(types_config))
            
            if not update_fields:
                return {
                    'success': True,
                    'message': 'No changes to update',
                    'preferences': get_notification_preferences(user_id).get('preferences', {})
                }
            
            params.append(user_id)
            
            # Upsert (update if exists, insert if not)
            cur.execute(
                f"""
                INSERT INTO {DB_SCHEMA}.notification_preferences (
                    user_id, email_enabled, push_enabled, types_config
                ) VALUES (
                    %s, 
                    COALESCE(%s, TRUE),
                    COALESCE(%s, TRUE),
                    COALESCE(%s, '{{"ACHIEVEMENT": true, "COURSE_MILESTONE": true, "CONTENT_UPDATE": true, "COMMUNITY_REPLY": true, "STREAK_REMINDER": true, "AI_RESPONSE": true, "SYSTEM_ANNOUNCEMENT": true}}'::jsonb)
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    email_enabled = COALESCE(EXCLUDED.email_enabled, {DB_SCHEMA}.notification_preferences.email_enabled),
                    push_enabled = COALESCE(EXCLUDED.push_enabled, {DB_SCHEMA}.notification_preferences.push_enabled),
                    types_config = COALESCE(EXCLUDED.types_config, {DB_SCHEMA}.notification_preferences.types_config)
                RETURNING user_id, email_enabled, push_enabled, types_config, created_at, updated_at
                """,
                params[:3] + [json.dumps(types_config) if types_config else None] + params[3:]
            )
            
            row = cur.fetchone()
            conn.commit()
            
            types_config_result = row[2]
            if isinstance(types_config_result, str):
                types_config_result = json.loads(types_config_result)
            
            return {
                'success': True,
                'message': 'Preferences updated successfully',
                'preferences': {
                    'user_id': str(row[0]),
                    'email_enabled': row[1],
                    'push_enabled': row[2],
                    'types_config': types_config_result,
                    'created_at': row[3].isoformat() if row[3] else None,
                    'updated_at': row[4].isoformat() if row[4] else None
                }
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error updating notification preferences: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()


def create_achievement_notification(
    user_id: str,
    achievement_name: str,
    achievement_description: str,
    badge_icon: Optional[str] = None,
    link: Optional[str] = '/achievements'
) -> Dict[str, Any]:
    """Helper to create an achievement notification"""
    return create_notification(
        user_id=user_id,
        notification_type='ACHIEVEMENT',
        title=f'Achievement Unlocked: {achievement_name}',
        message=achievement_description,
        link=link,
        metadata={'badge_icon': badge_icon, 'achievement_name': achievement_name}
    )


def create_streak_reminder_notification(
    user_id: str,
    current_streak: int,
    link: Optional[str] = '/dashboard'
) -> Dict[str, Any]:
    """Helper to create a streak reminder notification"""
    if current_streak == 1:
        message = "Start your learning streak today! Complete a lesson to begin."
    elif current_streak < 7:
        message = f"You're on a {current_streak}-day streak! Keep it up!"
    elif current_streak < 30:
        message = f"Amazing! {current_streak} days and counting. You're unstoppable!"
    else:
        message = f"Incredible! {current_streak} days straight. You're a true Jac master!"
    
    return create_notification(
        user_id=user_id,
        notification_type='STREAK_REMINDER',
        title='Learning Streak Alert',
        message=message,
        link=link,
        metadata={'current_streak': current_streak}
    )


def create_course_milestone_notification(
    user_id: str,
    course_name: str,
    milestone_name: str,
    progress_percent: int,
    link: Optional[str] = None
) -> Dict[str, Any]:
    """Helper to create a course milestone notification"""
    return create_notification(
        user_id=user_id,
        notification_type='COURSE_MILESTONE',
        title=f'Course Progress: {course_name}',
        message=f"Congratulations! You've reached the '{milestone_name}' milestone at {progress_percent}% completion.",
        link=link,
        metadata={
            'course_name': course_name,
            'milestone_name': milestone_name,
            'progress_percent': progress_percent
        }
    )
