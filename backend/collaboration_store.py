"""
Collaboration Store Module for Jeseci Smart Learning Academy

This module handles all database operations for collaboration and community features
including user connections, discussion forums, and content comments.
"""

import os
import sys
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env'))

from logger_config import logger
import psycopg2
from psycopg2 import extras

# Database configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


def get_db_connection():
    """Create a database connection"""
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


class CollaborationStore:
    """Store class for collaboration and community features"""
    
    def __init__(self):
        self.conn = None
    
    def _get_connection(self):
        """Get database connection, creating if necessary"""
        if not self.conn or self.conn.closed:
            self.conn = get_db_connection()
        return self.conn
    
    def _close_connection(self):
        """Close the database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None
    
    def generate_id(self, prefix: str) -> str:
        """Generate a unique ID with prefix"""
        return f"{prefix}_{uuid.uuid4().hex[:16]}"
    
    # =========================================================================
    # User Connection Methods
    # =========================================================================
    
    def create_connection(self, user_id: int, connected_user_id: int) -> Dict[str, Any]:
        """Create a new connection request between two users"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if connection already exists
            cursor.execute(f"""
                SELECT id, status FROM {DB_SCHEMA}.user_connections
                WHERE (user_id = %s AND connected_user_id = %s)
                   OR (user_id = %s AND connected_user_id = %s)
            """, (user_id, connected_user_id, connected_user_id, user_id))
            
            existing = cursor.fetchone()
            if existing:
                return {
                    "success": False,
                    "error": "Connection already exists",
                    "status": existing[1]
                }
            
            # Check if users exist
            cursor.execute(f"SELECT id, username, first_name FROM {DB_SCHEMA}.users WHERE id = %s", (connected_user_id,))
            target_user = cursor.fetchone()
            if not target_user:
                return {"success": False, "error": "User not found"}
            
            connection_id = self.generate_id("conn")
            
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.user_connections 
                (connection_id, user_id, connected_user_id, status)
                VALUES (%s, %s, %s, 'pending')
                RETURNING id, created_at
            """, (connection_id, user_id, connected_user_id))
            
            result = cursor.fetchone()
            conn.commit()
            
            return {
                "success": True,
                "connection_id": connection_id,
                "status": "pending",
                "connected_user_id": connected_user_id,
                "created_at": result[1].isoformat()
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating connection: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    def respond_to_connection(self, connection_id: str, user_id: int, action: str) -> Dict[str, Any]:
        """Accept or reject a connection request"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Find the connection request where user is the recipient
            cursor.execute(f"""
                SELECT id, user_id, connected_user_id, status 
                FROM {DB_SCHEMA}.user_connections
                WHERE connection_id = %s AND connected_user_id = %s AND status = 'pending'
            """, (connection_id, user_id))
            
            connection = cursor.fetchone()
            if not connection:
                return {"success": False, "error": "Connection request not found"}
            
            new_status = 'accepted' if action == 'accept' else 'rejected'
            
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.user_connections
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING updated_at
            """, (new_status, connection[0]))
            
            conn.commit()
            
            # Log activity for accepted connections
            if new_status == 'accepted':
                self.log_activity(connection[1], 'friend_joined', 
                    f"You and {connection[2]} are now connected")
            
            return {
                "success": True,
                "connection_id": connection_id,
                "status": new_status
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Error responding to connection: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    def get_user_connections(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all connections for a user"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            query = f"""
                SELECT 
                    uc.connection_id,
                    uc.status,
                    uc.created_at,
                    uc.updated_at,
                    u.id as connected_user_id,
                    u.username,
                    u.email,
                    up.first_name,
                    up.last_name,
                    up.avatar_url
                FROM {DB_SCHEMA}.user_connections uc
                JOIN {DB_SCHEMA}.users u ON u.id = uc.connected_user_id
                LEFT JOIN {DB_SCHEMA}.user_profile up ON up.user_id = u.id
                WHERE uc.user_id = %s
            """
            params = [user_id]
            
            if status:
                query += " AND uc.status = %s"
                params.append(status)
            
            query += " ORDER BY uc.updated_at DESC"
            
            cursor.execute(query, params)
            
            connections = []
            for row in cursor.fetchall():
                connections.append({
                    "connection_id": row[0],
                    "status": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "updated_at": row[3].isoformat() if row[3] else None,
                    "user": {
                        "user_id": row[4],
                        "username": row[5],
                        "email": row[6],
                        "first_name": row[7],
                        "last_name": row[8],
                        "avatar_url": row[9]
                    }
                })
            
            return connections
        except Exception as e:
            logger.error(f"Error getting user connections: {e}")
            return []
        finally:
            self._close_connection()
    
    def get_connection_requests(self, user_id: int) -> List[Dict[str, Any]]:
        """Get pending connection requests for a user"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT 
                    uc.connection_id,
                    uc.created_at,
                    u.id as requester_id,
                    u.username,
                    u.email,
                    up.first_name,
                    up.last_name,
                    up.avatar_url
                FROM {DB_SCHEMA}.user_connections uc
                JOIN {DB_SCHEMA}.users u ON u.id = uc.user_id
                LEFT JOIN {DB_SCHEMA}.user_profile up ON up.user_id = u.id
                WHERE uc.connected_user_id = %s AND uc.status = 'pending'
                ORDER BY uc.created_at DESC
            """, (user_id,))
            
            requests = []
            for row in cursor.fetchall():
                requests.append({
                    "connection_id": row[0],
                    "created_at": row[1].isoformat() if row[1] else None,
                    "requester": {
                        "user_id": row[2],
                        "username": row[3],
                        "email": row[4],
                        "first_name": row[5],
                        "last_name": row[6],
                        "avatar_url": row[7]
                    }
                })
            
            return requests
        except Exception as e:
            logger.error(f"Error getting connection requests: {e}")
            return []
        finally:
            self._close_connection()
    
    def remove_connection(self, connection_id: str, user_id: int) -> Dict[str, Any]:
        """Soft remove a connection"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if the user_connections table has audit columns
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = %s AND table_name = 'user_connections'
                AND column_name IN ('is_deleted', 'deleted_at', 'deleted_by')
            """, (DB_SCHEMA,))
            
            audit_columns = [row[0] for row in cursor.fetchall()]
            
            if 'is_deleted' in audit_columns:
                # Use soft delete
                cursor.execute(f"""
                    UPDATE {DB_SCHEMA}.user_connections
                    SET is_deleted = TRUE,
                        deleted_at = CURRENT_TIMESTAMP,
                        deleted_by = %s
                    WHERE connection_id = %s AND 
                          (user_id = %s OR connected_user_id = %s)
                    RETURNING id
                """, (user_id, connection_id, user_id, user_id))
            else:
                # Fallback to hard delete if audit columns don't exist
                cursor.execute(f"""
                    DELETE FROM {DB_SCHEMA}.user_connections
                    WHERE connection_id = %s AND 
                          (user_id = %s OR connected_user_id = %s)
                    RETURNING id
                """, (connection_id, user_id, user_id))
            
            if cursor.fetchone():
                conn.commit()
                return {"success": True, "message": "Connection removed"}
            else:
                return {"success": False, "error": "Connection not found"}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error removing connection: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    def search_users(self, user_id: int, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for users to connect with"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get users excluding self and existing connections
            cursor.execute(f"""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    up.first_name,
                    up.last_name,
                    up.avatar_url
                FROM {DB_SCHEMA}.users u
                LEFT JOIN {DB_SCHEMA}.user_profile up ON up.user_id = u.id
                WHERE u.id != %s 
                  AND u.is_active = TRUE
                  AND (u.username ILIKE %s OR u.email ILIKE %s OR 
                       up.first_name ILIKE %s OR up.last_name ILIKE %s)
                LIMIT %s
            """, (user_id, f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "first_name": row[3],
                    "last_name": row[4],
                    "avatar_url": row[5]
                })
            
            return users
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
        finally:
            self._close_connection()
    
    # =========================================================================
    # Forum Methods
    # =========================================================================
    
    def get_forums(self) -> List[Dict[str, Any]]:
        """Get all active forums"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT 
                    f.forum_id,
                    f.name,
                    f.description,
                    f.category,
                    f.icon,
                    f.sort_order,
                    COUNT(DISTINCT ft.thread_id) as thread_count,
                    COUNT(DISTINCT fp.post_id) as post_count,
                    MAX(ft.created_at) as last_activity
                FROM {DB_SCHEMA}.forums f
                LEFT JOIN {DB_SCHEMA}.forum_threads ft ON ft.forum_id = f.forum_id
                LEFT JOIN {DB_SCHEMA}.forum_posts fp ON fp.thread_id = ft.thread_id
                WHERE f.is_active = TRUE
                GROUP BY f.id
                ORDER BY f.sort_order ASC
            """)
            
            forums = []
            for row in cursor.fetchall():
                forums.append({
                    "forum_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "category": row[3],
                    "icon": row[4],
                    "thread_count": row[6],
                    "post_count": row[7],
                    "last_activity": row[8].isoformat() if row[8] else None
                })
            
            return forums
        except Exception as e:
            logger.error(f"Error getting forums: {e}")
            return []
        finally:
            self._close_connection()
    
    def create_thread(self, forum_id: str, user_id: int, title: str, content: str) -> Dict[str, Any]:
        """Create a new forum thread with initial post"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Verify forum exists and is active
            cursor.execute(f"SELECT forum_id, name FROM {DB_SCHEMA}.forums WHERE forum_id = %s AND is_active = TRUE", (forum_id,))
            forum = cursor.fetchone()
            if not forum:
                return {"success": False, "error": "Forum not found"}
            
            thread_id = self.generate_id("thread")
            
            # Create thread
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.forum_threads 
                (thread_id, forum_id, user_id, title, content)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING created_at
            """, (thread_id, forum_id, user_id, title, content))
            
            # Create initial post
            post_id = self.generate_id("post")
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.forum_posts 
                (post_id, thread_id, user_id, content)
                VALUES (%s, %s, %s, %s)
            """, (post_id, thread_id, user_id, content))
            
            conn.commit()
            
            return {
                "success": True,
                "thread_id": thread_id,
                "forum_id": forum_id,
                "title": title,
                "created_at": cursor.fetchone()[0].isoformat()
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating thread: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    def get_threads(self, forum_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get threads for a forum with pagination"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {DB_SCHEMA}.forum_threads WHERE forum_id = %s", (forum_id,))
            total_count = cursor.fetchone()[0]
            
            # Get threads
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT 
                    ft.thread_id,
                    ft.title,
                    ft.view_count,
                    ft.reply_count,
                    ft.is_pinned,
                    ft.is_locked,
                    ft.created_at,
                    ft.updated_at,
                    u.username,
                    up.first_name,
                    up.last_name
                FROM {DB_SCHEMA}.forum_threads ft
                JOIN {DB_SCHEMA}.users u ON u.id = ft.user_id
                LEFT JOIN {DB_SCHEMA}.user_profile up ON up.user_id = u.id
                WHERE ft.forum_id = %s
                ORDER BY ft.is_pinned DESC, ft.updated_at DESC
                LIMIT %s OFFSET %s
            """, (forum_id, limit, offset))
            
            threads = []
            for row in cursor.fetchall():
                threads.append({
                    "thread_id": row[0],
                    "title": row[1],
                    "view_count": row[2],
                    "reply_count": row[3],
                    "is_pinned": row[4],
                    "is_locked": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                    "updated_at": row[7].isoformat() if row[7] else None,
                    "author": {
                        "username": row[8],
                        "first_name": row[9],
                        "last_name": row[10]
                    }
                })
            
            return {
                "success": True,
                "threads": threads,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "total_pages": (total_count + limit - 1) // limit
                }
            }
        except Exception as e:
            logger.error(f"Error getting threads: {e}")
            return {"success": False, "error": str(e), "threads": [], "pagination": {}}
        finally:
            self._close_connection()
    
    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a single thread with all posts"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get thread
            cursor.execute(f"""
                SELECT 
                    ft.thread_id,
                    ft.title,
                    ft.content,
                    ft.forum_id,
                    ft.view_count,
                    ft.is_pinned,
                    ft.is_locked,
                    ft.created_at,
                    ft.updated_at,
                    u.username,
                    up.first_name,
                    up.last_name,
                    f.name as forum_name
                FROM {DB_SCHEMA}.forum_threads ft
                JOIN {DB_SCHEMA}.users u ON u.id = ft.user_id
                LEFT JOIN {DB_SCHEMA}.user_profile up ON up.user_id = u.id
                JOIN {DB_SCHEMA}.forums f ON f.forum_id = ft.forum_id
                WHERE ft.thread_id = %s
            """, (thread_id,))
            
            thread = cursor.fetchone()
            if not thread:
                return None
            
            # Increment view count
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.forum_threads
                SET view_count = view_count + 1
                WHERE thread_id = %s
            """, (thread_id,))
            
            # Get posts
            cursor.execute(f"""
                SELECT 
                    fp.post_id,
                    fp.content,
                    fp.like_count,
                    fp.is_accepted_answer,
                    fp.created_at,
                    fp.updated_at,
                    u.username,
                    up.first_name,
                    up.last_name,
                    up.avatar_url
                FROM {DB_SCHEMA}.forum_posts fp
                JOIN {DB_SCHEMA}.users u ON u.id = fp.user_id
                LEFT JOIN {DB_SCHEMA}.user_profile up ON up.user_id = u.id
                WHERE fp.thread_id = %s
                ORDER BY fp.created_at ASC
            """, (thread_id,))
            
            posts = []
            for row in cursor.fetchall():
                posts.append({
                    "post_id": row[0],
                    "content": row[1],
                    "like_count": row[2],
                    "is_accepted_answer": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None,
                    "author": {
                        "username": row[6],
                        "first_name": row[7],
                        "last_name": row[8],
                        "avatar_url": row[9]
                    }
                })
            
            conn.commit()
            
            return {
                "thread_id": thread[0],
                "title": thread[1],
                "content": thread[2],
                "forum_id": thread[3],
                "view_count": thread[4] + 1,
                "is_pinned": thread[5],
                "is_locked": thread[6],
                "created_at": thread[7].isoformat() if thread[7] else None,
                "updated_at": thread[8].isoformat() if thread[8] else None,
                "author": {
                    "username": thread[9],
                    "first_name": thread[10],
                    "last_name": thread[11]
                },
                "forum_name": thread[12],
                "posts": posts
            }
        except Exception as e:
            logger.error(f"Error getting thread: {e}")
            return None
        finally:
            self._close_connection()
    
    def create_post(self, thread_id: str, user_id: int, content: str, parent_post_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a reply post in a thread"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Verify thread exists and is not locked
            cursor.execute(f"SELECT is_locked, forum_id FROM {DB_SCHEMA}.forum_threads WHERE thread_id = %s", (thread_id,))
            thread = cursor.fetchone()
            if not thread:
                return {"success": False, "error": "Thread not found"}
            if thread[0]:
                return {"success": False, "error": "Thread is locked"}
            
            post_id = self.generate_id("post")
            
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.forum_posts 
                (post_id, thread_id, user_id, parent_post_id, content)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING created_at
            """, (post_id, thread_id, user_id, parent_post_id, content))
            
            # Update thread reply count and last reply time
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.forum_threads
                SET reply_count = reply_count + 1,
                    last_reply_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE thread_id = %s
            """, (thread_id,))
            
            conn.commit()
            
            return {
                "success": True,
                "post_id": post_id,
                "thread_id": thread_id,
                "created_at": cursor.fetchone()[0].isoformat()
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating post: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    def like_post(self, post_id: str, user_id: int) -> Dict[str, Any]:
        """Toggle like on a forum post"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if user already liked
            # For simplicity, we'll just increment/decrement
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.forum_posts
                SET like_count = like_count + 1
                WHERE post_id = %s
                RETURNING like_count
            """, (post_id,))
            
            result = cursor.fetchone()
            if result:
                conn.commit()
                return {"success": True, "like_count": result[0]}
            else:
                return {"success": False, "error": "Post not found"}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error liking post: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    # =========================================================================
    # Content Comment Methods
    # =========================================================================
    
    def add_comment(self, user_id: int, content_id: str, content_type: str, 
                   content: str, parent_comment_id: Optional[str] = None) -> Dict[str, Any]:
        """Add a comment to content (lesson, course, etc.)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            comment_id = self.generate_id("comment")
            
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.content_comments 
                (comment_id, user_id, content_id, content_type, parent_comment_id, content)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING created_at
            """, (comment_id, user_id, content_id, content_type, parent_comment_id, content))
            
            conn.commit()
            
            return {
                "success": True,
                "comment_id": comment_id,
                "content_id": content_id,
                "content_type": content_type,
                "created_at": cursor.fetchone()[0].isoformat()
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding comment: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    def get_content_comments(self, content_id: str, content_type: str, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get comments for content"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute(f"""
                SELECT COUNT(*) FROM {DB_SCHEMA}.content_comments
                WHERE content_id = %s AND content_type = %s
            """, (content_id, content_type))
            total_count = cursor.fetchone()[0]
            
            # Get comments
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT 
                    cc.comment_id,
                    cc.content,
                    cc.like_count,
                    cc.parent_comment_id,
                    cc.created_at,
                    cc.updated_at,
                    u.username,
                    up.first_name,
                    up.last_name,
                    up.avatar_url
                FROM {DB_SCHEMA}.content_comments cc
                JOIN {DB_SCHEMA}.users u ON u.id = cc.user_id
                LEFT JOIN {DB_SCHEMA}.user_profile up ON up.user_id = u.id
                WHERE cc.content_id = %s AND cc.content_type = %s
                ORDER BY cc.created_at DESC
                LIMIT %s OFFSET %s
            """, (content_id, content_type, limit, offset))
            
            comments = []
            for row in cursor.fetchall():
                comments.append({
                    "comment_id": row[0],
                    "content": row[1],
                    "like_count": row[2],
                    "parent_comment_id": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None,
                    "author": {
                        "username": row[6],
                        "first_name": row[7],
                        "last_name": row[8],
                        "avatar_url": row[9]
                    }
                })
            
            return {
                "success": True,
                "comments": comments,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count
                }
            }
        except Exception as e:
            logger.error(f"Error getting content comments: {e}")
            return {"success": False, "error": str(e), "comments": [], "pagination": {}}
        finally:
            self._close_connection()
    
    def like_comment(self, comment_id: str) -> Dict[str, Any]:
        """Toggle like on a comment"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.content_comments
                SET like_count = like_count + 1
                WHERE comment_id = %s
                RETURNING like_count
            """, (comment_id,))
            
            result = cursor.fetchone()
            if result:
                conn.commit()
                return {"success": True, "like_count": result[0]}
            else:
                return {"success": False, "error": "Comment not found"}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error liking comment: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self._close_connection()
    
    # =========================================================================
    # Activity Logging
    # =========================================================================
    
    def log_activity(self, user_id: int, activity_type: str, description: str, 
                    metadata: Optional[Dict] = None) -> bool:
        """Log a user activity"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            from activity_store import ActivityStore
            activity_store = ActivityStore()
            activity_store.log_activity(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                metadata=metadata
            )
            
            return True
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
        finally:
            self._close_connection()


# Module-level instance for easy access
collaboration_store = CollaborationStore()


if __name__ == "__main__":
    # Test the collaboration store
    store = CollaborationStore()
    
    print("Testing Collaboration Store...")
    print(f"Database: {DB_SCHEMA}")
    print("Connection test:", "Success" if store._get_connection() else "Failed")
