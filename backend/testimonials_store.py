"""
Testimonials Store Module
Handles database operations for user testimonials/reviews
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

# Import centralized logging configuration
from logger_config import logger

# Database configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


class TestimonialsStore:
    """Database operations for testimonials"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv("POSTGRES_HOST", "localhost"),
            'port': int(os.getenv("POSTGRES_PORT", 5432)),
            'database': os.getenv("POSTGRES_DB", "jeseci_learning_academy"),
            'user': os.getenv("POSTGRES_USER", "jeseci_academy_user"),
            'password': os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
        }
    
    def _get_connection(self):
        """Get a database connection"""
        import psycopg2
        return psycopg2.connect(**self.db_config)
    
    def get_approved_testimonials(self, limit: int = 6, featured_only: bool = False) -> Dict:
        """
        Fetch approved testimonials from the database
        
        Args:
            limit: Maximum number of testimonials to return
            featured_only: If True, only return featured testimonials
            
        Returns:
            Dict with success status, testimonials list, and total count
        """
        conn = None
        try:
            conn = self._get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Build query based on parameters
            if featured_only:
                query = f"""
                    SELECT id, author_name, author_role, author_avatar, content, rating, created_at
                    FROM {DB_SCHEMA}.testimonials
                    WHERE is_approved = true AND is_featured = true
                    ORDER BY created_at DESC
                    LIMIT %s
                """
            else:
                query = f"""
                    SELECT id, author_name, author_role, author_avatar, content, rating, created_at
                    FROM {DB_SCHEMA}.testimonials
                    WHERE is_approved = true
                    ORDER BY is_featured DESC, created_at DESC
                    LIMIT %s
                """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            testimonials = []
            for row in rows:
                testimonials.append({
                    "id": row[0],
                    "author_name": row[1],
                    "author_role": row[2],
                    "author_avatar": row[3] or "",
                    "content": row[4],
                    "rating": row[5],
                    "created_at": row[6].isoformat() if row[6] else ""
                })
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {DB_SCHEMA}.testimonials WHERE is_approved = true")
            total_count = cursor.fetchone()[0]
            
            logger.info(f"Retrieved {len(testimonials)} testimonials from database")
            
            return {
                "success": True,
                "testimonials": testimonials,
                "total_count": total_count
            }
            
        except Exception as error:
            logger.error(f"Error fetching testimonials: {error}")
            return {
                "success": False,
                "error": str(error),
                "testimonials": [],
                "total_count": 0
            }
        finally:
            if conn:
                conn.close()
    
    def create_testimonial(
        self, 
        user_id: str, 
        content: str, 
        rating: int,
        student_name: str,
        student_role: str = "Student"
    ) -> Dict:
        """
        Create a new testimonial (requires approval before being visible)
        
        Args:
            user_id: ID of the user submitting the testimonial
            content: Testimonial text content
            rating: Rating (1-5)
            student_name: Name to display
            student_role: Role/title to display
            
        Returns:
            Dict with success status and new testimonial ID
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"""
                INSERT INTO {DB_SCHEMA}.testimonials 
                (user_id, student_name, student_role, content, rating, is_approved, created_at)
                VALUES (%s, %s, %s, %s, %s, false, %s)
                RETURNING id
            """
            
            cursor.execute(query, (
                user_id if user_id else None,
                student_name,
                student_role,
                content,
                rating,
                datetime.now()
            ))
            
            testimonial_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Created testimonial ID: {testimonial_id}")
            
            return {
                "success": True,
                "id": testimonial_id,
                "message": "Testimonial submitted for approval"
            }
            
        except Exception as error:
            logger.error(f"Error creating testimonial: {error}")
            return {
                "success": False,
                "error": str(error)
            }
        finally:
            if conn:
                conn.close()
    
    def approve_testimonial(self, testimonial_id: int, approved: bool = True) -> Dict:
        """
        Approve or reject a testimonial
        
        Args:
            testimonial_id: ID of the testimonial
            approved: True to approve, False to reject
            
        Returns:
            Dict with success status
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"""
                UPDATE {DB_SCHEMA}.testimonials
                SET is_approved = %s, updated_at = %s
                WHERE id = %s
                RETURNING id
            """
            
            cursor.execute(query, (approved, datetime.now(), testimonial_id))
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Testimonial {testimonial_id} {'approved' if approved else 'rejected'}")
                return {
                    "success": True,
                    "message": f"Testimonial {'approved' if approved else 'rejected'} successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Testimonial not found"
                }
                
        except Exception as error:
            logger.error(f"Error updating testimonial: {error}")
            return {
                "success": False,
                "error": str(error)
            }
        finally:
            if conn:
                conn.close()
    
    def delete_testimonial(self, testimonial_id: int) -> Dict:
        """
        Delete a testimonial from the database
        
        Args:
            testimonial_id: ID of the testimonial to delete
            
        Returns:
            Dict with success status
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"""
                UPDATE {DB_SCHEMA}.testimonials
                SET is_deleted = TRUE, updated_at = %s
                WHERE id = %s
                RETURNING id
            """
            
            cursor.execute(query, (datetime.now(), testimonial_id))
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Deleted testimonial {testimonial_id}")
                return {
                    "success": True,
                    "message": "Testimonial deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Testimonial not found"
                }
                
        except Exception as error:
            logger.error(f"Error deleting testimonial: {error}")
            return {
                "success": False,
                "error": str(error)
            }
        finally:
            if conn:
                conn.close()
    
    def get_pending_testimonials(self) -> Dict:
        """
        Get testimonials awaiting approval (for admin dashboard)
        
        Returns:
            Dict with success status and pending testimonials list
        """
        conn = None
        try:
            conn = self._get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            
            query = f"""
                SELECT id, student_name, student_role, content, rating, created_at
                FROM {DB_SCHEMA}.testimonials
                WHERE is_approved = false
                ORDER BY created_at ASC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            testimonials = []
            for row in rows:
                testimonials.append({
                    "id": row[0],
                    "student_name": row[1],
                    "student_role": row[2],
                    "content": row[3],
                    "rating": row[4],
                    "created_at": row[5].isoformat() if row[5] else ""
                })
            
            return {
                "success": True,
                "testimonials": testimonials,
                "count": len(testimonials)
            }
            
        except Exception as error:
            logger.error(f"Error fetching pending testimonials: {error}")
            return {
                "success": False,
                "error": str(error),
                "testimonials": [],
                "count": 0
            }
        finally:
            if conn:
                conn.close()


# Global instance
testimonials_store = TestimonialsStore()


# Synchronous wrapper functions for Jaclang integration
def sync_get_approved_testimonials(limit: int = 6, featured_only: bool = False) -> dict:
    """
    Synchronous wrapper for getting approved testimonials
    
    Args:
        limit: Maximum number of testimonials
        featured_only: Only featured testimonials
        
    Returns:
        Dict with testimonials data
    """
    return testimonials_store.get_approved_testimonials(limit, featured_only)


def sync_create_testimonial(
    user_id: str, 
    content: str, 
    rating: int,
    student_name: str,
    student_role: str = "Student"
) -> dict:
    """
    Synchronous wrapper for creating a testimonial
    
    Returns:
        Dict with success status and testimonial ID
    """
    return testimonials_store.create_testimonial(
        user_id, content, rating, student_name, student_role
    )


def sync_approve_testimonial(testimonial_id: int, approved: bool = True) -> dict:
    """
    Synchronous wrapper for approving/rejecting a testimonial
    
    Returns:
        Dict with success status
    """
    return testimonials_store.approve_testimonial(testimonial_id, approved)


def sync_delete_testimonial(testimonial_id: int) -> dict:
    """
    Synchronous wrapper for deleting a testimonial
    
    Returns:
        Dict with success status
    """
    return testimonials_store.delete_testimonial(testimonial_id)


def sync_get_pending_testimonials() -> dict:
    """
    Synchronous wrapper for getting pending testimonials
    
    Returns:
        Dict with pending testimonials
    """
    return testimonials_store.get_pending_testimonials()


if __name__ == "__main__":
    # Test the module
    print("Testing testimonials store...")
    
    # Test fetching testimonials
    result = testimonials_store.get_approved_testimonials(limit=3)
    print(f"Fetched {len(result.get('testimonials', []))} testimonials")
    print(f"Total available: {result.get('total_count', 0)}")
    
    # Test creating a testimonial
    create_result = testimonials_store.create_testimonial(
        user_id="test_user",
        content="This is a test testimonial for the Jeseci Academy platform.",
        rating=5,
        student_name="Test User",
        student_role="Beta Tester"
    )
    print(f"Created testimonial: {create_result}")
