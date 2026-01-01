"""
Domain Management Module - Jeseci Smart Learning Academy

This module provides functionality to manage learning domains for content categorization.
It handles CRUD operations for domains, which are used to organize and categorize
courses, concepts, and learning materials across the platform.

Features:
- Create, read, update, and delete domains
- Domain activation and deactivation
- Slug generation for SEO-friendly URLs
- Bulk domain operations
- Domain statistics and content counts

Author: Cavin Otieno
License: MIT License
"""

import os
import sys
import uuid
import threading
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', '.env'))

import psycopg2
from psycopg2 import extras
from logger_config import logger

# Database configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


class DomainStore:
    """
    Manages domain data storage and operations for the learning platform.

    This class provides thread-safe operations for managing learning domains,
    which are used to categorize and organize educational content. Domains
    serve as high-level categories that help users navigate and discover
    relevant learning materials.

    Attributes:
        _lock: Reentrant lock for thread-safe operations
        _connection: PostgreSQL database connection
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
            logger.info("DomainStore: Database connection established")

        except Exception as e:
            logger.error(f"DomainStore: Failed to connect to database: {e}")
            self._connection = None

    def _get_connection(self):
        """Get or recreate database connection"""
        if self._connection is None or self._connection.closed:
            self._init_connection()
        return self._connection

    def _generate_slug(self, name: str) -> str:
        """
        Generate a URL-friendly slug from a domain name.

        Args:
            name: The domain name to convert to a slug

        Returns:
            A URL-friendly slug string
        """
        # Convert to lowercase and replace spaces with hyphens
        slug = name.lower().strip()
        slug = re.sub(r'\s+', '-', slug)
        # Remove special characters, keeping only alphanumeric and hyphens
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        # Remove consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def _generate_domain_id(self) -> str:
        """Generate a unique domain ID"""
        return f"domain_{uuid.uuid4().hex[:12]}"

    def create_domain(
        self,
        name: str,
        description: Optional[str] = None,
        icon: str = "📚",
        color: str = "#2563eb",
        is_active: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new domain in the database.

        Args:
            name: The display name of the domain
            description: Optional detailed description of the domain
            icon: Emoji or icon identifier for the domain
            color: Hex color code for visual representation
            is_active: Whether the domain is active and visible

        Returns:
            Dictionary containing the created domain data or error information
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return {"success": False, "error": "Database connection unavailable"}

            try:
                cursor = conn.cursor()

                # Generate unique domain_id and slug
                domain_id = self._generate_domain_id()
                base_slug = self._generate_slug(name)

                # Ensure slug is unique
                slug = base_slug
                counter = 1
                while True:
                    cursor.execute(f"""
                        SELECT id FROM {DB_SCHEMA}.domains
                        WHERE slug = %s
                    """, (slug,))
                    if cursor.fetchone() is None:
                        break
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                now = datetime.now()

                # Insert the domain record
                cursor.execute(f"""
                    INSERT INTO {DB_SCHEMA}.domains (
                        domain_id, name, slug, description, icon, color,
                        is_active, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    domain_id, name, slug, description, icon, color,
                    is_active, now, now
                ))

                conn.commit()

                logger.info(f"Created domain: {name} ({domain_id})")

                return {
                    "success": True,
                    "domain_id": domain_id,
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "icon": icon,
                    "color": color,
                    "is_active": is_active,
                    "created_at": now.isoformat()
                }

            except Exception as e:
                logger.error(f"Error creating domain: {e}")
                conn.rollback()
                return {"success": False, "error": str(e)}

    def get_domain_by_id(self, domain_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a domain by its unique domain_id.

        Args:
            domain_id: The unique identifier of the domain

        Returns:
            Dictionary containing the domain data, or None if not found
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return None

            try:
                cursor = conn.cursor()

                cursor.execute(f"""
                    SELECT domain_id, name, slug, description, icon, color,
                           is_active, created_at, updated_at
                    FROM {DB_SCHEMA}.domains
                    WHERE domain_id = %s
                """, (domain_id,))

                row = cursor.fetchone()
                if row is None:
                    return None

                return {
                    "domain_id": row[0],
                    "name": row[1],
                    "slug": row[2],
                    "description": row[3],
                    "icon": row[4],
                    "color": row[5],
                    "is_active": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None
                }

            except Exception as e:
                logger.error(f"Error getting domain by ID: {e}")
                return None

    def get_domain_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a domain by its name (case-insensitive).

        Args:
            name: The name of the domain to find

        Returns:
            Dictionary containing the domain data, or None if not found
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return None

            try:
                cursor = conn.cursor()

                cursor.execute(f"""
                    SELECT domain_id, name, slug, description, icon, color,
                           is_active, created_at, updated_at
                    FROM {DB_SCHEMA}.domains
                    WHERE LOWER(name) = LOWER(%s)
                """, (name,))

                row = cursor.fetchone()
                if row is None:
                    return None

                return {
                    "domain_id": row[0],
                    "name": row[1],
                    "slug": row[2],
                    "description": row[3],
                    "icon": row[4],
                    "color": row[5],
                    "is_active": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None
                }

            except Exception as e:
                logger.error(f"Error getting domain by name: {e}")
                return None

    def get_all_domains(
        self,
        include_inactive: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all domains with optional filtering and pagination.

        Args:
            include_inactive: Whether to include inactive domains
            limit: Maximum number of domains to return
            offset: Number of domains to skip for pagination

        Returns:
            List of domain dictionaries
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return []

            try:
                cursor = conn.cursor()

                if include_inactive:
                    cursor.execute(f"""
                        SELECT domain_id, name, slug, description, icon, color,
                               is_active, created_at, updated_at
                        FROM {DB_SCHEMA}.domains
                        ORDER BY name ASC
                        LIMIT %s OFFSET %s
                    """, (limit, offset))
                else:
                    cursor.execute(f"""
                        SELECT domain_id, name, slug, description, icon, color,
                               is_active, created_at, updated_at
                        FROM {DB_SCHEMA}.domains
                        WHERE is_active = TRUE
                        ORDER BY name ASC
                        LIMIT %s OFFSET %s
                    """, (limit, offset))

                rows = cursor.fetchall()
                domains = []
                for row in rows:
                    domains.append({
                        "domain_id": row[0],
                        "name": row[1],
                        "slug": row[2],
                        "description": row[3],
                        "icon": row[4],
                        "color": row[5],
                        "is_active": row[6],
                        "created_at": row[7].isoformat() if row[7] else None,
                        "updated_at": row[8].isoformat() if row[8] else None
                    })

                return domains

            except Exception as e:
                logger.error(f"Error getting all domains: {e}")
                return []

    def get_domain_count(self, include_inactive: bool = False) -> int:
        """
        Get the total count of domains.

        Args:
            include_inactive: Whether to include inactive domains in count

        Returns:
            Total number of domains
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return 0

            try:
                cursor = conn.cursor()

                if include_inactive:
                    cursor.execute(f"SELECT COUNT(*) FROM {DB_SCHEMA}.domains")
                else:
                    cursor.execute(f"SELECT COUNT(*) FROM {DB_SCHEMA}.domains WHERE is_active = TRUE")

                result = cursor.fetchone()
                return result[0] if result else 0

            except Exception as e:
                logger.error(f"Error counting domains: {e}")
                return 0

    def update_domain(
        self,
        domain_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update an existing domain's information.

        Args:
            domain_id: The unique identifier of the domain to update
            name: New name for the domain (optional)
            description: New description for the domain (optional)
            icon: New icon for the domain (optional)
            color: New color for the domain (optional)
            is_active: New active status for the domain (optional)

        Returns:
            Dictionary containing the updated domain data or error information
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return {"success": False, "error": "Database connection unavailable"}

            try:
                cursor = conn.cursor()

                # Check if domain exists
                cursor.execute(f"""
                    SELECT domain_id FROM {DB_SCHEMA}.domains
                    WHERE domain_id = %s
                """, (domain_id,))
                if cursor.fetchone() is None:
                    return {"success": False, "error": "Domain not found"}

                # Build dynamic update query
                updates = []
                params = []

                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                    # Update slug if name changes
                    slug = self._generate_slug(name)
                    # Ensure slug uniqueness
                    base_slug = slug
                    counter = 1
                    while True:
                        cursor.execute(f"""
                            SELECT id FROM {DB_SCHEMA}.domains
                            WHERE slug = %s AND domain_id != %s
                        """, (slug, domain_id))
                        if cursor.fetchone() is None:
                            break
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    updates.append("slug = %s")
                    params.append(slug)

                if description is not None:
                    updates.append("description = %s")
                    params.append(description)

                if icon is not None:
                    updates.append("icon = %s")
                    params.append(icon)

                if color is not None:
                    updates.append("color = %s")
                    params.append(color)

                if is_active is not None:
                    updates.append("is_active = %s")
                    params.append(is_active)

                if not updates:
                    return {"success": False, "error": "No fields to update"}

                updates.append("updated_at = %s")
                params.append(datetime.now())

                # Add domain_id to params
                params.append(domain_id)

                query = f"""
                    UPDATE {DB_SCHEMA}.domains
                    SET {', '.join(updates)}
                    WHERE domain_id = %s
                """

                cursor.execute(query, params)
                conn.commit()

                # Return updated domain
                return self.get_domain_by_id(domain_id)

            except Exception as e:
                logger.error(f"Error updating domain: {e}")
                conn.rollback()
                return {"success": False, "error": str(e)}

    def deactivate_domain(self, domain_id: str) -> Dict[str, Any]:
        """
        Deactivate a domain (soft delete).

        Args:
            domain_id: The unique identifier of the domain to deactivate

        Returns:
            Dictionary containing the deactivated domain data or error information
        """
        return self.update_domain(domain_id, is_active=False)

    def activate_domain(self, domain_id: str) -> Dict[str, Any]:
        """
        Activate a previously deactivated domain.

        Args:
            domain_id: The unique identifier of the domain to activate

        Returns:
            Dictionary containing the activated domain data or error information
        """
        return self.update_domain(domain_id, is_active=True)

    def delete_domain(self, domain_id: str) -> Dict[str, Any]:
        """
        Permanently delete a domain from the database.

        Args:
            domain_id: The unique identifier of the domain to delete

        Returns:
            Dictionary containing success status or error information
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return {"success": False, "error": "Database connection unavailable"}

            try:
                cursor = conn.cursor()

                # Check if domain exists
                cursor.execute(f"""
                    SELECT domain_id, name FROM {DB_SCHEMA}.domains
                    WHERE domain_id = %s
                """, (domain_id,))
                row = cursor.fetchone()
                if row is None:
                    return {"success": False, "error": "Domain not found"}

                domain_name = row[1]

                # Delete the domain
                cursor.execute(f"""
                    DELETE FROM {DB_SCHEMA}.domains
                    WHERE domain_id = %s
                """, (domain_id,))

                conn.commit()

                logger.info(f"Deleted domain: {domain_name} ({domain_id})")

                return {
                    "success": True,
                    "message": f"Domain '{domain_name}' has been permanently deleted",
                    "domain_id": domain_id
                }

            except Exception as e:
                logger.error(f"Error deleting domain: {e}")
                conn.rollback()
                return {"success": False, "error": str(e)}

    def search_domains(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search domains by name or description.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching domain dictionaries
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return []

            try:
                cursor = conn.cursor()

                search_pattern = f"%{query}%"

                cursor.execute(f"""
                    SELECT domain_id, name, slug, description, icon, color,
                           is_active, created_at, updated_at
                    FROM {DB_SCHEMA}.domains
                    WHERE (LOWER(name) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s))
                          AND is_active = TRUE
                    ORDER BY name ASC
                    LIMIT %s
                """, (search_pattern, search_pattern, limit))

                rows = cursor.fetchall()
                domains = []
                for row in rows:
                    domains.append({
                        "domain_id": row[0],
                        "name": row[1],
                        "slug": row[2],
                        "description": row[3],
                        "icon": row[4],
                        "color": row[5],
                        "is_active": row[6],
                        "created_at": row[7].isoformat() if row[7] else None,
                        "updated_at": row[8].isoformat() if row[8] else None
                    })

                return domains

            except Exception as e:
                logger.error(f"Error searching domains: {e}")
                return []

    def get_domain_stats(self, domain_id: str) -> Dict[str, Any]:
        """
        Get statistics and content counts for a domain.

        Args:
            domain_id: The unique identifier of the domain

        Returns:
            Dictionary containing domain statistics
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return {}

            try:
                cursor = conn.cursor()

                # Get basic domain info
                domain = self.get_domain_by_id(domain_id)
                if domain is None:
                    return {}

                # Count concepts in this domain
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {DB_SCHEMA}.concepts
                    WHERE domain = %s
                """, (domain.get('name'),))
                concept_count = cursor.fetchone()[0]

                # Count learning paths in this domain
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {DB_SCHEMA}.learning_paths
                    WHERE category = %s
                """, (domain.get('name'),))
                path_count = cursor.fetchone()[0]

                return {
                    "domain_id": domain_id,
                    "name": domain.get("name"),
                    "concept_count": concept_count,
                    "learning_path_count": path_count,
                    "total_content": concept_count + path_count
                }

            except Exception as e:
                logger.error(f"Error getting domain stats: {e}")
                return {}

    def bulk_create_domains(
        self,
        domains: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple domains in a single transaction.

        Args:
            domains: List of domain data dictionaries

        Returns:
            Dictionary containing success count, created domains, and errors
        """
        with self._lock:
            conn = self._get_connection()
            if conn is None:
                return {"success": False, "error": "Database connection unavailable"}

            try:
                cursor = conn.cursor()

                created = []
                errors = []
                now = datetime.now()

                for domain_data in domains:
                    try:
                        # Generate unique domain_id and slug
                        domain_id = self._generate_domain_id()
                        name = domain_data.get("name")
                        base_slug = self._generate_slug(name)

                        # Ensure slug is unique
                        slug = base_slug
                        counter = 1
                        while True:
                            cursor.execute(f"""
                                SELECT id FROM {DB_SCHEMA}.domains
                                WHERE slug = %s
                            """, (slug,))
                            if cursor.fetchone() is None:
                                break
                            slug = f"{base_slug}-{counter}"
                            counter += 1

                        description = domain_data.get("description")
                        icon = domain_data.get("icon", "📚")
                        color = domain_data.get("color", "#2563eb")
                        is_active = domain_data.get("is_active", True)

                        cursor.execute(f"""
                            INSERT INTO {DB_SCHEMA}.domains (
                                domain_id, name, slug, description, icon, color,
                                is_active, created_at, updated_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """, (
                            domain_id, name, slug, description, icon, color,
                            is_active, now, now
                        ))

                        created.append({
                            "domain_id": domain_id,
                            "name": name,
                            "slug": slug
                        })

                    except Exception as e:
                        errors.append({
                            "data": domain_data,
                            "error": str(e)
                        })

                conn.commit()

                logger.info(f"Bulk created {len(created)} domains")

                return {
                    "success": True,
                    "created_count": len(created),
                    "error_count": len(errors),
                    "created_domains": created,
                    "errors": errors
                }

            except Exception as e:
                logger.error(f"Error in bulk domain creation: {e}")
                conn.rollback()
                return {"success": False, "error": str(e)}

    def close(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("DomainStore: Database connection closed")


# Global instance for use across the application
domain_store = DomainStore()


def create_domain(
    name: str,
    description: Optional[str] = None,
    icon: str = "📚",
    color: str = "#2563eb",
    is_active: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to create a new domain.

    Args:
        name: The display name of the domain
        description: Optional detailed description of the domain
        icon: Emoji or icon identifier for the domain
        color: Hex color code for visual representation
        is_active: Whether the domain is active and visible

    Returns:
        Dictionary containing the created domain data or error information
    """
    return domain_store.create_domain(
        name=name,
        description=description,
        icon=icon,
        color=color,
        is_active=is_active
    )


def get_domain_by_id(domain_id: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get a domain by its ID.

    Args:
        domain_id: The unique identifier of the domain

    Returns:
        Dictionary containing the domain data, or None if not found
    """
    return domain_store.get_domain_by_id(domain_id)


def get_all_domains(
    include_inactive: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Convenience function to get all domains.

    Args:
        include_inactive: Whether to include inactive domains
        limit: Maximum number of domains to return
        offset: Number of domains to skip for pagination

    Returns:
        List of domain dictionaries
    """
    return domain_store.get_all_domains(
        include_inactive=include_inactive,
        limit=limit,
        offset=offset
    )


def update_domain(
    domain_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Convenience function to update a domain.

    Args:
        domain_id: The unique identifier of the domain to update
        name: New name for the domain (optional)
        description: New description for the domain (optional)
        icon: New icon for the domain (optional)
        color: New color for the domain (optional)
        is_active: New active status for the domain (optional)

    Returns:
        Dictionary containing the updated domain data or error information
    """
    return domain_store.update_domain(
        domain_id=domain_id,
        name=name,
        description=description,
        icon=icon,
        color=color,
        is_active=is_active
    )


def delete_domain(domain_id: str) -> Dict[str, Any]:
    """
    Convenience function to delete a domain.

    Args:
        domain_id: The unique identifier of the domain to delete

    Returns:
        Dictionary containing success status or error information
    """
    return domain_store.delete_domain(domain_id)


def search_domains(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Convenience function to search domains.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        List of matching domain dictionaries
    """
    return domain_store.search_domains(query=query, limit=limit)
