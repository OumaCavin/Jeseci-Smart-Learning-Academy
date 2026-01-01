"""
Content Views Tracking Module - Jeseci Smart Learning Academy

This module provides functionality to track and manage content views for analytics.
It records when users view courses, concepts, and learning paths, and provides
aggregated statistics for the admin analytics dashboard.

Features:
- Record individual content views with full metadata
- Track unique views per user/session
- Maintain aggregated summary tables for fast analytics queries
- Support for both authenticated and anonymous views

Author: MiniMax Agent
License: MIT License
"""

import os
import sys
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', '.env'))

import psycopg2
from psycopg2 import extras
from logger_config import logger

# Database configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


class ContentViewsStore:
    """
    Manages content view tracking and analytics data storage.

    This class provides thread-safe operations for recording content views
    and generating aggregated statistics for the analytics dashboard.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._connection = None
        self._init_connection()

    def _init_connection(self):
        """Initialize database connection"""
        try:
            postgres_host = os.getenv("POSTGRES_HOST", "localhost")
            postgres_port = os.getenv("POSTGRES_PORT", "5432")
            postgres_db = os.getenv("POSTGRES_DB", "jeseci_academy")
            postgres_user = os.getenv("POSTGRES_USER", "jeseci_admin")
            postgres_password = os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")

            self._connection = psycopg2.connect(
                host=postgres_host,
                port=postgres_port,
                database=postgres_db,
                user=postgres_user,
                password=postgres_password
            )
            self._connection.autocommit = False
            logger.info("ContentViewsStore: Database connection established")

        except Exception as e:
            logger.error(f"ContentViewsStore: Failed to connect to database: {e}")
            self._connection = None

    def _get_connection(self):
        """Get or recreate database connection"""
        if self._connection is None or self._connection.closed:
            self._init_connection()
        return self._connection

    def record_view(
        self,
        content_id: str,
        content_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        view_duration: int = 0,
        referrer_url: Optional[str] = None,
        device_type: str = "desktop",
        browser: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a content view event.

        Args:
            content_id: The ID of the content being viewed
            content_type: Type of content (course, concept, learning_path)
            user_id: User ID if authenticated, None for anonymous
            session_id: Session ID for tracking anonymous users
            ip_address: Client IP address
            user_agent: Client user agent string
            view_duration: Duration of view in seconds
            referrer_url: URL that referred to this content
            device_type: Type of device (desktop, mobile, tablet)
            browser: Browser name
            country_code: Country code from IP

        Returns:
            Dictionary containing view_id and success status
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return {"success": False, "error": "Database connection unavailable"}

            try:
                cursor = conn.cursor()

                view_id = str(uuid.uuid4())
                now = datetime.now()

                # Check if this is a unique view (first view by this user/session for this content today)
                is_unique = False
                if user_id:
                    # Check for existing view by this user today
                    cursor.execute(f"""
                        SELECT id FROM {DB_SCHEMA}.content_views
                        WHERE content_id = %s AND user_id = %s
                        AND viewed_at > %s
                    """, (content_id, user_id, now - timedelta(days=1)))
                    if cursor.fetchone() is None:
                        is_unique = True
                elif session_id:
                    # Check for existing view by this session today
                    cursor.execute(f"""
                        SELECT id FROM {DB_SCHEMA}.content_views
                        WHERE content_id = %s AND session_id = %s
                        AND viewed_at > %s
                    """, (content_id, session_id, now - timedelta(days=1)))
                    if cursor.fetchone() is None:
                        is_unique = True

                # Insert the view record
                cursor.execute(f"""
                    INSERT INTO {DB_SCHEMA}.content_views (
                        view_id, content_id, content_type, user_id, session_id,
                        ip_address, user_agent, viewed_at, view_duration,
                        referrer_url, device_type, browser, country_code, is_unique_view
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    view_id, content_id, content_type, user_id, session_id,
                    ip_address, user_agent, now, view_duration,
                    referrer_url, device_type, browser, country_code, is_unique
                ))

                # Update or insert into summary table
                cursor.execute(f"""
                    INSERT INTO {DB_SCHEMA}.content_views_summary (
                        content_id, content_type, total_views, unique_views,
                        total_view_duration, last_viewed_at,
                        views_today, views_this_week, views_this_month
                    ) VALUES (
                        %s, %s, 1, %s, %s, %s, 1, 1, 1
                    )
                    ON CONFLICT (content_id, content_type) DO UPDATE SET
                        total_views = {DB_SCHEMA}.content_views_summary.total_views + 1,
                        unique_views = {DB_SCHEMA}.content_views_summary.unique_views + %s,
                        total_view_duration = {DB_SCHEMA}.content_views_summary.total_view_duration + %s,
                        last_viewed_at = %s,
                        views_today = {DB_SCHEMA}.content_views_summary.views_today + 1,
                        views_this_week = {DB_SCHEMA}.content_views_summary.views_this_week + 1,
                        views_this_month = {DB_SCHEMA}.content_views_summary.views_this_month + 1,
                        updated_at = %s
                """, (
                    content_id, content_type,
                    1 if is_unique else 0,
                    view_duration,
                    now,
                    1 if is_unique else 0,
                    view_duration,
                    now,
                    now
                ))

                conn.commit()

                logger.debug(f"Recorded view: {view_id} for {content_type}:{content_id}")

                return {
                    "success": True,
                    "view_id": view_id,
                    "is_unique_view": is_unique
                }

            except Exception as e:
                logger.error(f"Error recording view: {e}")
                conn.rollback()
                return {"success": False, "error": str(e)}

    def get_content_views(
        self,
        content_id: str,
        content_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get view records for a specific content item.

        Args:
            content_id: The content ID to get views for
            content_type: Optional filter by content type
            limit: Maximum number of records to return

        Returns:
            List of view records
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return []

            try:
                cursor = conn.cursor()

                if content_type:
                    cursor.execute(f"""
                        SELECT view_id, content_id, content_type, user_id, session_id,
                               ip_address, viewed_at, view_duration, device_type, browser
                        FROM {DB_SCHEMA}.content_views
                        WHERE content_id = %s AND content_type = %s
                        ORDER BY viewed_at DESC
                        LIMIT %s
                    """, (content_id, content_type, limit))
                else:
                    cursor.execute(f"""
                        SELECT view_id, content_id, content_type, user_id, session_id,
                               ip_address, viewed_at, view_duration, device_type, browser
                        FROM {DB_SCHEMA}.content_views
                        WHERE content_id = %s
                        ORDER BY viewed_at DESC
                        LIMIT %s
                    """, (content_id, limit))

                rows = cursor.fetchall()
                views = []
                for row in rows:
                    views.append({
                        "view_id": row[0],
                        "content_id": row[1],
                        "content_type": row[2],
                        "user_id": row[3],
                        "session_id": row[4],
                        "ip_address": row[5],
                        "viewed_at": row[6].isoformat() if row[6] else None,
                        "view_duration": row[7],
                        "device_type": row[8],
                        "browser": row[9]
                    })

                return views

            except Exception as e:
                logger.error(f"Error getting content views: {e}")
                return []

    def get_popular_content(
        self,
        content_type: str,
        limit: int = 10,
        period: str = "all_time"
    ) -> List[Dict[str, Any]]:
        """
        Get the most popular content based on views.

        Args:
            content_type: Type of content to filter (course, concept, learning_path)
            limit: Maximum number of items to return
            period: Time period (today, week, month, all_time)

        Returns:
            List of popular content items with view counts
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return []

            try:
                cursor = conn.cursor()

                # First update the period aggregations
                self._update_period_aggregations(cursor)

                # Query based on period
                if period == "today":
                    cursor.execute(f"""
                        SELECT content_id, content_type, total_views, unique_views,
                               last_viewed_at, views_today
                        FROM {DB_SCHEMA}.content_views_summary
                        WHERE content_type = %s AND views_today > 0
                        ORDER BY views_today DESC
                        LIMIT %s
                    """, (content_type, limit))
                elif period == "week":
                    cursor.execute(f"""
                        SELECT content_id, content_type, total_views, unique_views,
                               last_viewed_at, views_this_week
                        FROM {DB_SCHEMA}.content_views_summary
                        WHERE content_type = %s AND views_this_week > 0
                        ORDER BY views_this_week DESC
                        LIMIT %s
                    """, (content_type, limit))
                elif period == "month":
                    cursor.execute(f"""
                        SELECT content_id, content_type, total_views, unique_views,
                               last_viewed_at, views_this_month
                        FROM {DB_SCHEMA}.content_views_summary
                        WHERE content_type = %s AND views_this_month > 0
                        ORDER BY views_this_month DESC
                        LIMIT %s
                    """, (content_type, limit))
                else:
                    cursor.execute(f"""
                        SELECT content_id, content_type, total_views, unique_views,
                               last_viewed_at
                        FROM {DB_SCHEMA}.content_views_summary
                        WHERE content_type = %s
                        ORDER BY total_views DESC
                        LIMIT %s
                    """, (content_type, limit))

                rows = cursor.fetchall()
                popular = []
                for row in rows:
                    period_views = row[5] if len(row) > 5 else row[2]
                    popular.append({
                        "content_id": row[0],
                        "content_type": row[1],
                        "views": row[2],
                        "unique_views": row[3],
                        "last_viewed_at": row[4].isoformat() if row[4] else None,
                        f"views_in_period": period_views
                    })

                return popular

            except Exception as e:
                logger.error(f"Error getting popular content: {e}")
                return []

    def _update_period_aggregations(self, cursor):
        """Update the daily/weekly/monthly view aggregations"""
        try:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)

            # Reset daily counter if it's a new day
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.content_views_summary
                SET views_today = 0
                WHERE updated_at::date < %s
            """, (today,))

            # Reset weekly counter if it's a new week
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.content_views_summary
                SET views_this_week = 0
                WHERE updated_at < %s
            """, (week_start,))

            # Reset monthly counter if it's a new month
            cursor.execute(f"""
                UPDATE {DB_SCHEMA}.content_views_summary
                SET views_this_month = 0
                WHERE updated_at < %s
            """, (month_start,))

        except Exception as e:
            logger.error(f"Error updating period aggregations: {e}")

    def get_content_view_stats(
        self,
        content_id: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Get detailed view statistics for a specific content item.

        Args:
            content_id: The content ID
            content_type: Type of content

        Returns:
            Dictionary with view statistics
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return {}

            try:
                cursor = conn.cursor()

                # Get summary stats
                cursor.execute(f"""
                    SELECT total_views, unique_views, total_view_duration,
                           last_viewed_at, views_today, views_this_week, views_this_month
                    FROM {DB_SCHEMA}.content_views_summary
                    WHERE content_id = %s AND content_type = %s
                """, (content_id, content_type))

                row = cursor.fetchone()
                if row is None:
                    return {
                        "content_id": content_id,
                        "content_type": content_type,
                        "total_views": 0,
                        "unique_views": 0,
                        "average_view_duration": 0,
                        "views_today": 0,
                        "views_this_week": 0,
                        "views_this_month": 0
                    }

                total_views = row[0]
                unique_views = row[1]
                total_duration = row[2]

                return {
                    "content_id": content_id,
                    "content_type": content_type,
                    "total_views": total_views,
                    "unique_views": unique_views,
                    "average_view_duration": round(total_duration / max(total_views, 1), 2),
                    "views_today": row[4],
                    "views_this_week": row[5],
                    "views_this_month": row[6],
                    "last_viewed_at": row[3].isoformat() if row[3] else None
                }

            except Exception as e:
                logger.error(f"Error getting content view stats: {e}")
                return {}

    def get_all_content_view_summary(self) -> List[Dict[str, Any]]:
        """
        Get aggregated view summary for all content.

        Returns:
            List of all content with their view statistics
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return []

            try:
                cursor = conn.cursor()

                self._update_period_aggregations(cursor)
                conn.commit()

                cursor.execute(f"""
                    SELECT content_id, content_type, total_views, unique_views,
                           total_view_duration, last_viewed_at
                    FROM {DB_SCHEMA}.content_views_summary
                    ORDER BY total_views DESC
                """)

                rows = cursor.fetchall()
                summary = []
                for row in rows:
                    total_views = row[2]
                    total_duration = row[4]
                    summary.append({
                        "content_id": row[0],
                        "content_type": row[1],
                        "total_views": total_views,
                        "unique_views": row[3],
                        "average_view_duration": round(total_duration / max(total_views, 1), 2),
                        "last_viewed_at": row[5].isoformat() if row[5] else None
                    })

                return summary

            except Exception as e:
                logger.error(f"Error getting all content view summary: {e}")
                return []

    def close(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("ContentViewsStore: Database connection closed")


# Global instance for use across the application
content_views_store = ContentViewsStore()


def record_content_view(
    content_id: str,
    content_type: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to record a content view.

    Args:
        content_id: The ID of the content being viewed
        content_type: Type of content (course, concept, learning_path)
        user_id: User ID if authenticated
        session_id: Session ID for anonymous users
        **kwargs: Additional view metadata

    Returns:
        Dictionary containing view_id and success status
    """
    return content_views_store.record_view(
        content_id=content_id,
        content_type=content_type,
        user_id=user_id,
        session_id=session_id or str(uuid.uuid4()),
        **kwargs
    )


def get_popular_content(
    content_type: str,
    limit: int = 10,
    period: str = "all_time"
) -> List[Dict[str, Any]]:
    """
    Get popular content based on view counts.

    Args:
        content_type: Type of content to filter
        limit: Maximum items to return
        period: Time period for views

    Returns:
        List of popular content items
    """
    return content_views_store.get_popular_content(
        content_type=content_type,
        limit=limit,
        period=period
    )


def get_all_views_summary() -> List[Dict[str, Any]]:
    """
    Get view summary for all content.

    Returns:
        List of all content with view statistics
    """
    return content_views_store.get_all_content_view_summary()
