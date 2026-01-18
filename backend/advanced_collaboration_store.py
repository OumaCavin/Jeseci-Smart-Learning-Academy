#!/usr/bin/env python3
"""
Advanced Collaboration Store Module

This module handles all business logic for advanced collaboration features including:
- Reputation and upvoting system
- Study groups with shared workspaces
- Mentorship connections
- Content moderation
- Peer review system
"""

import os
import sys
import uuid
import json
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger_config import logger
import psycopg2
from psycopg2 import extras

# Database configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


def get_db_connection():
    """Get database connection"""
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db = os.getenv("POSTGRES_DB", "jeseci_learning_academy")
    postgres_user = os.getenv("POSTGRES_USER", "jeseci_academy_user")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
    
    return psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        database=postgres_db,
        user=postgres_user,
        password=postgres_password
    )


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4().hex[:12])
    return f"{prefix}_{unique_id}" if prefix else unique_id


# ==============================================================================
# REPUTATION SYSTEM FUNCTIONS
# ==============================================================================

def get_user_reputation(user_id: int) -> Optional[Dict[str, Any]]:
    """Get reputation profile for a user"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.user_reputation WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()


def create_or_update_reputation(user_id: int, event_type: str, points_change: int, 
                                 target_user_id: Optional[int] = None,
                                 content_id: Optional[str] = None,
                                 content_type: Optional[str] = None,
                                 reason: Optional[str] = None) -> Dict[str, Any]:
    """Create a reputation event and update user reputation"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Create the reputation event
        event_id = generate_id("rep_evt")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.reputation_events 
            (event_id, user_id, event_type, points_change, target_user_id, content_id, content_type, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (event_id, user_id, event_type, points_change, target_user_id, content_id, content_type, reason))
        
        # Update or create user reputation
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.user_reputation (user_id, reputation_points, level)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id) DO UPDATE SET
                reputation_points = {{DB_SCHEMA}}.user_reputation.reputation_points + EXCLUDED.reputation_points,
                updated_at = CURRENT_TIMESTAMP
            RETURNING *
        """, (user_id, points_change))
        
        reputation = cursor.fetchone()
        
        # Update counters based on event type
        if event_type == 'upvote_received':
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.user_reputation SET total_upvotes_received = total_upvotes_received + 1
                WHERE user_id = %s
            """, (target_user_id,))
        elif event_type == 'downvote_received':
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.user_reputation SET total_downvotes_received = total_downvotes_received + 1
                WHERE user_id = %s
            """, (target_user_id,))
        elif event_type == 'answer_accepted':
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.user_reputation SET total_accepted_answers = total_accepted_answers + 1
                WHERE user_id = %s
            """, (target_user_id,))
        
        # Update level based on points
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.user_reputation SET
                level = CASE
                    WHEN reputation_points >= 10000 THEN 10
                    WHEN reputation_points >= 5000 THEN 9
                    WHEN reputation_points >= 2500 THEN 8
                    WHEN reputation_points >= 1000 THEN 7
                    WHEN reputation_points >= 500 THEN 6
                    WHEN reputation_points >= 250 THEN 5
                    WHEN reputation_points >= 100 THEN 4
                    WHEN reputation_points >= 50 THEN 3
                    WHEN reputation_points >= 25 THEN 2
                    ELSE 1
                END
            WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        
        return {
            "success": True,
            "event_id": event_id,
            "points_change": points_change,
            "message": f"Reputation event recorded: {event_type}"
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating reputation event: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def upvote_content(user_id: int, content_id: str, content_type: str, vote_type: int = 1) -> Dict[str, Any]:
    """Upvote or downvote content"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Check if already voted
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.content_upvotes 
            WHERE user_id = %s AND content_id = %s AND content_type = %s
        """, (user_id, content_id, content_type))
        existing_vote = cursor.fetchone()
        
        if existing_vote:
            if existing_vote['vote_type'] == vote_type:
                # Remove vote if clicking same button
                cursor.execute(f"""
                    DELETE FROM {{DB_SCHEMA}}.content_upvotes 
                    WHERE user_id = %s AND content_id = %s AND content_type = %s
                """, (user_id, content_id, content_type))
                vote_change = -vote_type
                action = "removed"
            else:
                # Change vote
                cursor.execute(f"""
                    UPDATE {{DB_SCHEMA}}.content_upvotes SET vote_type = %s
                    WHERE user_id = %s AND content_id = %s AND content_type = %s
                """, (vote_type, user_id, content_id, content_type))
                vote_change = 2 * vote_type
                action = "changed"
        else:
            # Create new vote
            upvote_id = generate_id("up")
            cursor.execute(f"""
                INSERT INTO {{DB_SCHEMA}}.content_upvotes (upvote_id, user_id, content_id, content_type, vote_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (upvote_id, user_id, content_id, content_type, vote_type))
            vote_change = vote_type
            action = "added"
        
        # Update like count on content
        if content_type == 'forum_post':
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.forum_posts SET like_count = like_count + %s
                WHERE post_id = %s
            """, (vote_change, content_id))
            # Get author
            cursor.execute(f"SELECT user_id FROM {{DB_SCHEMA}}.forum_posts WHERE post_id = %s", (content_id,))
            post = cursor.fetchone()
        elif content_type == 'forum_thread':
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.forum_threads SET like_count = like_count + %s
                WHERE thread_id = %s
            """, (vote_change, content_id))
            cursor.execute(f"SELECT user_id FROM {{DB_SCHEMA}}.forum_threads WHERE thread_id = %s", (content_id,))
            post = cursor.fetchone()
        elif content_type == 'content_comment':
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.content_comments SET like_count = like_count + %s
                WHERE comment_id = %s
            """, (vote_change, content_id))
            cursor.execute(f"SELECT user_id FROM {{DB_SCHEMA}}.content_comments WHERE comment_id = %s", (content_id,))
            post = cursor.fetchone()
        else:
            post = None
        
        # Award reputation points to content author
        if post and post['user_id'] != user_id:
            points = vote_type * 10  # 10 points per upvote
            create_or_update_reputation(
                user_id=post['user_id'],
                event_type='upvote_received' if vote_type > 0 else 'downvote_received',
                points_change=points,
                content_id=content_id,
                content_type=content_type
            )
        
        conn.commit()
        
        return {
            "success": True,
            "action": action,
            "vote_change": vote_change,
            "message": f"Vote {action} successfully"
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error upvoting content: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Get reputation leaderboard"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"""
            SELECT r.*, u.username, up.avatar_url
            FROM {{DB_SCHEMA}}.user_reputation r
            JOIN {{DB_SCHEMA}}.users u ON r.user_id = u.id
            LEFT JOIN {{DB_SCHEMA}}.user_profile up ON r.user_id = u.id
            ORDER BY r.reputation_points DESC
            LIMIT %s
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ==============================================================================
# STUDY GROUPS FUNCTIONS
# ==============================================================================

def create_study_group(name: str, description: str, created_by: int, 
                       learning_goal: Optional[str] = None,
                       target_topic: Optional[str] = None,
                       is_public: bool = True) -> Dict[str, Any]:
    """Create a new study group"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        group_id = generate_id("sg")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.study_groups 
            (group_id, name, description, learning_goal, target_topic, is_public, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (group_id, name, description, learning_goal, target_topic, is_public, created_by))
        
        group = cursor.fetchone()
        
        # Add creator as owner
        membership_id = generate_id("sgm")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.study_group_members 
            (membership_id, group_id, user_id, role)
            VALUES (%s, %s, %s, 'owner')
        """, (membership_id, group_id, created_by))
        
        conn.commit()
        
        return {"success": True, "group": dict(group)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating study group: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_study_groups(is_public: bool = True, topic: Optional[str] = None, 
                     limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Get list of study groups"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        query = f"""
            SELECT g.*, u.username as creator_name,
                   (SELECT COUNT(*) FROM {{DB_SCHEMA}}.study_group_members WHERE group_id = g.group_id) as member_count
            FROM {{DB_SCHEMA}}.study_groups g
            JOIN {{DB_SCHEMA}}.users u ON g.created_by = u.id
            WHERE g.is_active = TRUE AND g.is_public = %s
        """
        params = [is_public]
        
        if topic:
            query += " AND g.target_topic = %s"
            params.append(topic)
        
        query += f" ORDER BY g.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def join_study_group(group_id: str, user_id: int) -> Dict[str, Any]:
    """Join a study group"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Check if group exists and has space
        cursor.execute(f"SELECT * FROM {{DB_SCHEMA}}.study_groups WHERE group_id = %s AND is_active = TRUE", (group_id,))
        group = cursor.fetchone()
        
        if not group:
            return {"success": False, "error": "Study group not found"}
        
        if group['max_members'] <= 0:
            return {"success": False, "error": "Study group is full"}
        
        # Check if already a member
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.study_group_members WHERE group_id = %s AND user_id = %s
        """, (group_id, user_id))
        if cursor.fetchone():
            return {"success": False, "error": "Already a member of this group"}
        
        # Add member
        membership_id = generate_id("sgm")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.study_group_members (membership_id, group_id, user_id, role)
            VALUES (%s, %s, %s, 'member')
        """, (membership_id, group_id, user_id))
        
        conn.commit()
        
        return {"success": True, "message": "Successfully joined study group"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error joining study group: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def create_group_note(group_id: str, author_id: int, title: str, content: str, 
                      tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a shared note in a study group"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Verify membership
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.study_group_members WHERE group_id = %s AND user_id = %s
        """, (group_id, author_id))
        if not cursor.fetchone():
            return {"success": False, "error": "You must be a member to add notes"}
        
        note_id = generate_id("sgn")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.study_group_notes 
            (note_id, group_id, author_id, title, content, tags)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (note_id, group_id, author_id, title, content, tags or []))
        
        note = cursor.fetchone()
        conn.commit()
        
        return {"success": True, "note": dict(note)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating group note: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_group_notes(group_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get notes from a study group"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"""
            SELECT n.*, u.username as author_name
            FROM {{DB_SCHEMA}}.study_group_notes n
            JOIN {{DB_SCHEMA}}.users u ON n.author_id = u.id
            WHERE n.group_id = %s
            ORDER BY n.is_pinned DESC, n.created_at DESC
            LIMIT %s OFFSET %s
        """, (group_id, limit, offset))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def create_group_goal(group_id: str, title: str, description: Optional[str] = None,
                      target_completion_date: Optional[date] = None) -> Dict[str, Any]:
    """Create a group learning goal"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        goal_id = generate_id("sgg")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.study_group_goals 
            (goal_id, group_id, title, description, target_completion_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (goal_id, group_id, title, description, target_completion_date))
        
        goal = cursor.fetchone()
        conn.commit()
        
        return {"success": True, "goal": dict(goal)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating group goal: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_group_goals(group_id: str) -> List[Dict[str, Any]]:
    """Get all goals for a study group"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.study_group_goals 
            WHERE group_id = %s
            ORDER BY is_completed ASC, target_completion_date ASC
        """, (group_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def send_group_message(group_id: str, user_id: int, content: str, 
                       message_type: str = 'text', file_url: Optional[str] = None) -> Dict[str, Any]:
    """Send a message to group chat"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Verify membership
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.study_group_members WHERE group_id = %s AND user_id = %s
        """, (group_id, user_id))
        if not cursor.fetchone():
            return {"success": False, "error": "You must be a member to send messages"}
        
        message_id = generate_id("sgmsg")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.study_group_messages 
            (message_id, group_id, user_id, content, message_type, file_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (message_id, group_id, user_id, content, message_type, file_url))
        
        message = cursor.fetchone()
        
        # Update last active time for member
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.study_group_members SET last_active_at = CURRENT_TIMESTAMP
            WHERE group_id = %s AND user_id = %s
        """, (group_id, user_id))
        
        conn.commit()
        
        return {"success": True, "message": dict(message)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error sending group message: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_group_messages(group_id: str, limit: int = 50, before_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get messages from group chat"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        query = f"""
            SELECT m.*, u.username, up.avatar_url
            FROM {{DB_SCHEMA}}.study_group_messages m
            JOIN {{DB_SCHEMA}}.users u ON m.user_id = u.id
            LEFT JOIN {{DB_SCHEMA}}.user_profile up ON m.user_id = u.id
            WHERE m.group_id = %s
        """
        params = [group_id]
        
        if before_id:
            query += " AND m.message_id < %s"
            params.append(before_id)
        
        query += f" ORDER BY m.created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ==============================================================================
# MENTORSHIP SYSTEM FUNCTIONS
# ==============================================================================

def create_mentor_profile(user_id: int, expertise_areas: List[str], 
                          bio: Optional[str] = None,
                          years_experience: int = 0,
                          teaching_style: Optional[str] = None,
                          availability_hours: Optional[str] = None,
                          max_mentees: int = 3) -> Dict[str, Any]:
    """Create or update mentor profile"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.mentorship_profiles 
            (user_id, expertise_areas, bio, years_experience, teaching_style, availability_hours, max_mentees)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                expertise_areas = EXCLUDED.expertise_areas,
                bio = EXCLUDED.bio,
                years_experience = EXCLUDED.years_experience,
                teaching_style = EXCLUDED.teaching_style,
                availability_hours = EXCLUDED.availability_hours,
                max_mentees = EXCLUDED.max_mentees,
                updated_at = CURRENT_TIMESTAMP
            RETURNING *
        """, (user_id, expertise_areas, bio, years_experience, teaching_style, availability_hours, max_mentees))
        
        profile = cursor.fetchone()
        conn.commit()
        
        return {"success": True, "profile": dict(profile)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating mentor profile: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def search_mentors(expertise_areas: Optional[List[str]] = None,
                   is_available: bool = True,
                   limit: int = 20) -> List[Dict[str, Any]]:
    """Search for available mentors"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        query = f"""
            SELECT mp.*, u.username, up.first_name, up.last_name, up.avatar_url, up.bio as user_bio
            FROM {{DB_SCHEMA}}.mentorship_profiles mp
            JOIN {{DB_SCHEMA}}.users u ON mp.user_id = u.id
            LEFT JOIN {{DB_SCHEMA}}.user_profile up ON mp.user_id = u.id
            WHERE mp.is_available = %s AND u.is_active = TRUE
        """
        params = [is_available]
        
        if expertise_areas:
            query += " AND mp.expertise_areas && %s"
            params.append(expertise_areas)
        
        query += f" ORDER BY mp.average_rating DESC, mp.total_sessions_completed DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def request_mentorship(mentor_id: int, mentee_id: int, topic: str,
                       goals: Optional[str] = None,
                       preferred_schedule: Optional[str] = None,
                       message: Optional[str] = None) -> Dict[str, Any]:
    """Request mentorship from a mentor"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Check if mentor exists and is available
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.mentorship_profiles 
            WHERE user_id = %s AND is_available = TRUE
        """, (mentor_id,))
        mentor = cursor.fetchone()
        
        if not mentor:
            return {"success": False, "error": "Mentor not available"}
        
        if mentor['current_mentees_count'] >= mentor['max_mentees']:
            return {"success": False, "error": "Mentor has reached maximum mentees"}
        
        # Check for existing request
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.mentorship_requests 
            WHERE mentor_id = %s AND mentee_id = %s AND status IN ('pending', 'accepted')
        """, (mentor_id, mentee_id))
        if cursor.fetchone():
            return {"success": False, "error": "Active mentorship request already exists"}
        
        request_id = generate_id("msr")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.mentorship_requests 
            (request_id, mentor_id, mentee_id, topic, goals, preferred_schedule, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (request_id, mentor_id, mentee_id, topic, goals, preferred_schedule, message))
        
        request = cursor.fetchone()
        conn.commit()
        
        return {"success": True, "request": dict(request)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error requesting mentorship: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def respond_to_mentorship_request(request_id: str, status: str, 
                                  response_message: Optional[str] = None) -> Dict[str, Any]:
    """Respond to a mentorship request"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.mentorship_requests WHERE request_id = %s
        """, (request_id,))
        request = cursor.fetchone()
        
        if not request:
            return {"success": False, "error": "Request not found"}
        
        if request['status'] != 'pending':
            return {"success": False, "error": "Request already processed"}
        
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.mentorship_requests 
            SET status = %s, response_message = %s, responded_at = CURRENT_TIMESTAMP
            WHERE request_id = %s
            RETURNING *
        """, (status, response_message, request_id))
        
        # If accepted, update mentor's mentee count
        if status == 'accepted':
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.mentorship_profiles 
                SET current_mentees_count = current_mentees_count + 1
                WHERE user_id = %s
            """, (request['mentor_id'],))
        
        conn.commit()
        
        return {"success": True, "message": f"Request {status}"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error responding to mentorship request: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def schedule_mentorship_session(mentorship_id: int, scheduled_at: datetime,
                                duration_minutes: int = 60,
                                topic: Optional[str] = None) -> Dict[str, Any]:
    """Schedule a mentorship session"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Verify mentorship exists
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.mentorship_requests WHERE id = %s AND status = 'accepted'
        """, (mentorship_id,))
        mentorship = cursor.fetchone()
        
        if not mentorship:
            return {"success": False, "error": "Active mentorship not found"}
        
        session_id = generate_id("mss")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.mentorship_sessions 
            (session_id, mentorship_id, mentor_id, mentee_id, scheduled_at, duration_minutes, topic)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (session_id, mentorship_id, mentorship['mentor_id'], mentorship['mentee_id'], 
              scheduled_at, duration_minutes, topic))
        
        session = cursor.fetchone()
        conn.commit()
        
        return {"success": True, "session": dict(session)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error scheduling mentorship session: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def complete_mentorship_session(session_id: str, mentor_feedback: Optional[str] = None,
                                mentee_feedback: Optional[str] = None,
                                mentor_rating: Optional[int] = None,
                                mentee_rating: Optional[int] = None,
                                outcome: Optional[str] = None) -> Dict[str, Any]:
    """Complete a mentorship session with feedback"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.mentorship_sessions WHERE session_id = %s
        """, (session_id,))
        session = cursor.fetchone()
        
        if not session:
            return {"success": False, "error": "Session not found"}
        
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.mentorship_sessions 
            SET status = 'completed', ended_at = CURRENT_TIMESTAMP,
                mentor_feedback = %s, mentee_feedback = %s,
                mentor_rating = %s, mentee_rating = %s, outcome = %s
            WHERE session_id = %s
            RETURNING *
        """, (mentor_feedback, mentee_feedback, mentor_rating, mentee_rating, outcome, session_id))
        
        # Update mentor stats
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.mentorship_profiles 
            SET total_sessions_completed = total_sessions_completed + 1
            WHERE user_id = %s
        """, (session['mentor_id'],))
        
        # Update mentor rating
        if mentee_rating:
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.mentorship_profiles 
                SET average_rating = (
                    SELECT COALESCE(AVG(mentee_rating), 0)
                    FROM {{DB_SCHEMA}}.mentorship_sessions
                    WHERE mentor_id = %s AND mentee_rating IS NOT NULL
                )
                WHERE user_id = %s
            """, (session['mentor_id'], session['mentor_id']))
        
        # Award reputation points
        if session['mentor_id']:
            create_or_update_reputation(
                user_id=session['mentor_id'],
                event_type='mentorship_completed',
                points_change=50,
                reason="Completed mentorship session"
            )
        
        conn.commit()
        
        return {"success": True, "message": "Session completed successfully"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error completing mentorship session: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


# ==============================================================================
# MODERATION FUNCTIONS
# ==============================================================================

def report_content(reporter_id: int, content_id: str, content_type: str,
                   report_reason: str, additional_info: Optional[str] = None,
                   priority: str = 'normal') -> Dict[str, Any]:
    """Report content for moderation"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        report_id = generate_id("rep")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.content_reports 
            (report_id, reporter_id, content_id, content_type, report_reason, additional_info, priority)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (report_id, reporter_id, content_id, content_type, report_reason, additional_info, priority))
        
        report = cursor.fetchone()
        
        # Add to moderation queue
        queue_id = generate_id("mq")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.moderation_queue (queue_id, content_id, content_type, report_id, priority)
            VALUES (%s, %s, %s, %s, %s)
        """, (queue_id, content_id, content_type, report['id'], priority))
        
        conn.commit()
        
        return {"success": True, "report": dict(report)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error reporting content: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_moderation_queue(status: str = 'pending', priority: Optional[str] = None,
                         limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Get items from moderation queue"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        query = f"""
            SELECT q.*, r.report_reason, r.additional_info, r.reporter_id,
                   u.username as reporter_username
            FROM {{DB_SCHEMA}}.moderation_queue q
            LEFT JOIN {{DB_SCHEMA}}.content_reports r ON q.report_id = r.id
            LEFT JOIN {{DB_SCHEMA}}.users u ON r.reporter_id = u.id
            WHERE q.status = %s
        """
        params = [status]
        
        if priority:
            query += " AND q.priority = %s"
            params.append(priority)
        
        query += f" ORDER BY q.priority DESC, q.submitted_at ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def take_moderation_action(moderator_id: int, content_id: str, content_type: str,
                           action_type: str, reason: Optional[str] = None,
                           notes: Optional[str] = None) -> Dict[str, Any]:
    """Take moderation action on content"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        action_id = generate_id("ma")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.moderation_actions 
            (action_id, moderator_id, content_id, content_type, action_type, reason, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (action_id, moderator_id, content_id, content_type, action_type, reason, notes))
        
        # Update related queue item
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.moderation_queue 
            SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP,
                resolution_summary = %s
            WHERE content_id = %s AND status != 'resolved'
        """, (f"Action taken: {action_type}", content_id))
        
        # Update related reports
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.content_reports 
            SET status = 'resolved', reviewed_by = %s, reviewed_at = CURRENT_TIMESTAMP,
                resolution_notes = %s
            WHERE content_id = %s AND status = 'pending'
        """, (moderator_id, f"Action taken: {action_type}", content_id))
        
        # Perform the actual action on content (soft delete)
        if action_type == 'content_removed':
            if content_type == 'forum_post':
                cursor.execute(f"UPDATE {{DB_SCHEMA}}.forum_posts SET is_deleted = TRUE WHERE post_id = %s", (content_id,))
            elif content_type == 'forum_thread':
                cursor.execute(f"UPDATE {{DB_SCHEMA}}.forum_threads SET is_deleted = TRUE WHERE thread_id = %s", (content_id,))
            elif content_type == 'content_comment':
                cursor.execute(f"UPDATE {{DB_SCHEMA}}.content_comments SET is_deleted = TRUE WHERE comment_id = %s", (content_id,))
        
        conn.commit()
        
        return {"success": True, "action_id": action_id}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error taking moderation action: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_moderation_stats() -> Dict[str, Any]:
    """Get moderation statistics"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Pending reports
        cursor.execute(f"""
            SELECT COUNT(*) as count FROM {{DB_SCHEMA}}.content_reports WHERE status = 'pending'
        """)
        pending = cursor.fetchone()['count']
        
        # Reports by reason
        cursor.execute(f"""
            SELECT report_reason, COUNT(*) as count
            FROM {{DB_SCHEMA}}.content_reports
            GROUP BY report_reason
        """)
        by_reason = {row['report_reason']: row['count'] for row in cursor.fetchall()}
        
        # Recent actions
        cursor.execute(f"""
            SELECT COUNT(*) as count FROM {{DB_SCHEMA}}.moderation_actions 
            WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
        """)
        recent_actions = cursor.fetchone()['count']
        
        return {
            "pending_reports": pending,
            "reports_by_reason": by_reason,
            "recent_actions": recent_actions
        }
    finally:
        conn.close()


# ==============================================================================
# PEER REVIEW SYSTEM FUNCTIONS
# ==============================================================================

def create_peer_review_submission(user_id: int, title: str, description: str,
                                  content_type: str,
                                  related_content_id: Optional[str] = None,
                                  related_content_type: Optional[str] = None,
                                  max_reviewers: int = 2) -> Dict[str, Any]:
    """Create a submission for peer review"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        submission_id = generate_id("prs")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.peer_review_submissions 
            (submission_id, user_id, title, description, content_type, 
             related_content_id, related_content_type, max_reviewers)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (submission_id, user_id, title, description, content_type,
              related_content_id, related_content_type, max_reviewers))
        
        submission = cursor.fetchone()
        conn.commit()
        
        return {"success": True, "submission": dict(submission)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating peer review submission: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def assign_peer_reviewer(submission_id: str, reviewer_id: int,
                         deadline: Optional[date] = None) -> Dict[str, Any]:
    """Assign a reviewer to a submission"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Check submission exists and needs reviewers
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.peer_review_submissions 
            WHERE submission_id = %s AND status = 'open'
        """, (submission_id,))
        submission = cursor.fetchone()
        
        if not submission:
            return {"success": False, "error": "Submission not found or not open for review"}
        
        if submission['current_reviewers'] >= submission['max_reviewers']:
            return {"success": False, "error": "Maximum reviewers reached"}
        
        # Check if already assigned
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.peer_review_assignments 
            WHERE submission_id = %s AND reviewer_id = %s
        """, (submission_id, reviewer_id))
        if cursor.fetchone():
            return {"success": False, "error": "Already assigned as reviewer"}
        
        assignment_id = generate_id("pra")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.peer_review_assignments 
            (assignment_id, submission_id, reviewer_id, deadline)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (assignment_id, submission_id, reviewer_id, deadline))
        
        # Update submission reviewer count
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.peer_review_submissions 
            SET current_reviewers = current_reviewers + 1
            WHERE submission_id = %s
        """, (submission_id,))
        
        conn.commit()
        
        return {"success": True, "assignment_id": assignment_id}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error assigning peer reviewer: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def submit_peer_review(assignment_id: str, reviewer_id: int,
                       overall_rating: int, strengths: str,
                       improvements: str, comments: str) -> Dict[str, Any]:
    """Submit peer review feedback"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Get assignment
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.peer_review_assignments 
            WHERE assignment_id = %s AND reviewer_id = %s
        """, (assignment_id, reviewer_id))
        assignment = cursor.fetchone()
        
        if not assignment:
            return {"success": False, "error": "Assignment not found"}
        
        if assignment['status'] == 'completed':
            return {"success": False, "error": "Review already submitted"}
        
        feedback_id = generate_id("prf")
        cursor.execute(f"""
            INSERT INTO {{DB_SCHEMA}}.peer_review_feedback 
            (feedback_id, assignment_id, submission_id, reviewer_id, 
             overall_rating, strengths, improvements, comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (feedback_id, assignment_id, assignment['submission_id'], reviewer_id,
              overall_rating, strengths, improvements, comments))
        
        # Update assignment status
        cursor.execute(f"""
            UPDATE {{DB_SCHEMA}}.peer_review_assignments 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE assignment_id = %s
        """, (assignment_id,))
        
        # Check if all reviews are complete
        cursor.execute(f"""
            SELECT COUNT(*) as completed
            FROM {{DB_SCHEMA}}.peer_review_assignments
            WHERE submission_id = %s AND status = 'completed'
        """, (assignment['submission_id'],))
        completed_count = cursor.fetchone()['completed']
        
        cursor.execute(f"""
            SELECT * FROM {{DB_SCHEMA}}.peer_review_submissions WHERE submission_id = %s
        """, (assignment['submission_id'],))
        submission = cursor.fetchone()
        
        if completed_count >= submission['max_reviewers']:
            cursor.execute(f"""
                UPDATE {{DB_SCHEMA}}.peer_review_submissions 
                SET status = 'completed'
                WHERE submission_id = %s
            """, (assignment['submission_id'],))
        
        # Award reputation points to reviewer
        create_or_update_reputation(
            user_id=reviewer_id,
            event_type='peer_review_completed',
            points_change=25,
            reason="Completed peer review"
        )
        
        conn.commit()
        
        return {"success": True, "feedback_id": feedback_id}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error submitting peer review: {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_submission_reviews(submission_id: str) -> List[Dict[str, Any]]:
    """Get all reviews for a submission"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"""
            SELECT f.*, u.username, up.avatar_url
            FROM {{DB_SCHEMA}}.peer_review_feedback f
            JOIN {{DB_SCHEMA}}.users u ON f.reviewer_id = u.id
            LEFT JOIN {{DB_SCHEMA}}.user_profile up ON f.reviewer_id = u.id
            WHERE f.submission_id = %s
            ORDER BY f.created_at ASC
        """, (submission_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_my_submissions(user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get peer review submissions for user"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        query = f"""
            SELECT s.*, 
                   (SELECT COUNT(*) FROM {{DB_SCHEMA}}.peer_review_feedback WHERE submission_id = s.submission_id) as feedback_count
            FROM {{DB_SCHEMA}}.peer_review_submissions s
            WHERE s.user_id = %s
        """
        params = [user_id]
        
        if status:
            query += " AND s.status = %s"
            params.append(status)
        
        query += " ORDER BY s.created_at DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_my_review_assignments(user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get review assignments for user"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        query = f"""
            SELECT a.*, s.title as submission_title, s.description as submission_description,
                   u.username as author_username
            FROM {{DB_SCHEMA}}.peer_review_assignments a
            JOIN {{DB_SCHEMA}}.peer_review_submissions s ON a.submission_id = s.submission_id
            JOIN {{DB_SCHEMA}}.users u ON s.user_id = u.id
            WHERE a.reviewer_id = %s
        """
        params = [user_id]
        
        if status:
            query += " AND a.status = %s"
            params.append(status)
        
        query += " ORDER BY a.assigned_at DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_reviewers_for_submission(submission_id: str) -> List[Dict[str, Any]]:
    """Get all reviewers assigned to a submission"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"""
            SELECT a.*, u.username, u.email, up.avatar_url
            FROM {{DB_SCHEMA}}.peer_review_assignments a
            JOIN {{DB_SCHEMA}}.users u ON a.reviewer_id = u.id
            LEFT JOIN {{DB_SCHEMA}}.user_profile up ON u.id = up.user_id
            WHERE a.submission_id = %s
            ORDER BY a.assigned_at ASC
        """, (submission_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def check_user_has_submission(user_id: int, submission_id: str) -> bool:
    """Check if a user owns a submission"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 1 FROM {{DB_SCHEMA}}.peer_review_submissions
            WHERE user_id = %s AND submission_id = %s
        """, (user_id, submission_id))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def check_user_is_reviewer(user_id: int, submission_id: str) -> bool:
    """Check if a user is assigned as reviewer for a submission"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = "SELECT 1 FROM {}_peer_review_assignments WHERE reviewer_id = %s AND submission_id = %s".format(DB_SCHEMA)
        cursor.execute(sql, (user_id, submission_id))
        return cursor.fetchone() is not None
    finally:
        conn.close()
