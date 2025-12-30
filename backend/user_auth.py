"""
User Authentication Module for Jeseci Smart Learning Academy

This module handles PostgreSQL-based user registration and login operations
with secure password hashing using bcrypt and JWT token generation.

Author: Cavin Otieno
License: MIT License
"""

import os
import asyncio
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

import psycopg2
from psycopg2 import pool, extras
import bcrypt
import jwt
from datetime import datetime, timedelta
import uuid
from email_verification import (
    generate_verification_token,
    get_token_expiration,
    send_verification_email,
    send_welcome_email
)
from backend.database.neo4j_manager import Neo4jManager
from backend.database.initialize_database import initialize_database

# Import centralized logging configuration
from logger_config import logger

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jeseci_secret_key_change_in_production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 5))

# Database Schema Configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


class UserAuthManager:
    """
    Manages user authentication operations with PostgreSQL.
    
    Provides secure user registration with bcrypt password hashing
    and JWT-based authentication for login sessions.
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.schema = DB_SCHEMA
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Initialize the PostgreSQL connection pool"""
        config = self._get_db_config()
        try:
            UserAuthManager._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            logger.info(f"User auth PostgreSQL pool initialized: {config['host']}:{config['port']}/{config['database']}")
            
            # Initialize all database tables using the centralized script
            try:
                initialize_database()
            except Exception as init_error:
                logger.error(f"Failed to initialize database tables: {init_error}")
        except Exception as e:
            logger.error(f"Failed to initialize user auth PostgreSQL pool: {e}")
            UserAuthManager._pool = None
    
    def _get_db_config(self):
        """Get database configuration from environment"""
        return {
            'host': os.getenv("POSTGRES_HOST", "localhost"),
            'port': int(os.getenv("POSTGRES_PORT", 5432)),
            'database': os.getenv("POSTGRES_DB", "jeseci_learning_academy"),
            'user': os.getenv("POSTGRES_USER", "jeseci_academy_user"),
            'password': os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
        }
    
    def _get_connection(self):
        """Get a connection from the pool"""
        if UserAuthManager._pool is None:
            self._initialize_pool()
        if UserAuthManager._pool:
            return UserAuthManager._pool.getconn()
        return None
    
    def _return_connection(self, conn):
        """Return a connection to the pool"""
        if UserAuthManager._pool and conn:
            UserAuthManager._pool.putconn(conn)
    
    def register_user(self, username: str, email: str, password: str, 
                      first_name: str = "", last_name: str = "",
                      learning_style: str = "visual", skill_level: str = "beginner",
                      is_admin: bool = False, admin_role: str = "student",
                      skip_verification: bool = False,
                      daily_goal_minutes: int = 30,
                      notifications_enabled: bool = True,
                      email_reminders: bool = True,
                      dark_mode: bool = False,
                      auto_play_videos: bool = True) -> dict:
        """
        Register a new user with bcrypt password hashing and email verification.
        
        Creates records in:
        - users table (authentication fields)
        - user_profile table (extended user information)
        - user_learning_preferences table (learning preferences)
        
        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name
            learning_style: User's preferred learning style
            skill_level: User's skill level
            is_admin: Whether user has admin privileges (default: False)
            admin_role: Admin role level (student, admin, super_admin)
            skip_verification: Skip email verification (for admin-created users)
            daily_goal_minutes: Daily learning goal in minutes (default: 30)
            notifications_enabled: Enable push notifications (default: True)
            email_reminders: Enable email reminders (default: True)
            dark_mode: Enable dark mode UI (default: False)
            auto_play_videos: Auto-play video content (default: True)
            
        Returns:
            dict with 'success', 'user_id', 'requires_verification', and 'message' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed", "user_id": None}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # Check if user already exists
            cursor.execute(f"SELECT id, user_id FROM {self.schema}.users WHERE username = %s OR email = %s", (username, email))
            existing = cursor.fetchone()
            if existing:
                return {"success": False, "error": "Username or email already exists", "user_id": None, "code": "CONFLICT"}
            
            # Generate unique user_id (auto-generated string identifier)
            user_id = f"user_{username}_{uuid.uuid4().hex[:8]}"
            
            # Hash password with bcrypt
            salt = bcrypt.gensalt(rounds=12)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            # Generate verification token if not skipped
            verification_token = None
            token_expires_at = None
            is_email_verified = skip_verification  # Skip verification for admin-created users
            
            if not skip_verification:
                verification_token = generate_verification_token()
                token_expires_at = get_token_expiration()
            
            # Insert into users table (only auth fields)
            current_time = datetime.now()
            insert_user_query = f"""
            INSERT INTO {self.schema}.users (user_id, username, email, password_hash, 
                             is_active, is_admin, admin_role, is_email_verified, verification_token, 
                             token_expires_at, created_at, updated_at, last_login_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id
            """
            cursor.execute(insert_user_query, (user_id, username, email, password_hash, 
                                               True, is_admin, admin_role,
                                               is_email_verified, verification_token, 
                                               token_expires_at, current_time, current_time, None))
            result = cursor.fetchone()
            user_db_id = result['id']  # INTEGER primary key
            
            # Insert into user_profile table (links via users.id)
            insert_profile_query = f"""
            INSERT INTO {self.schema}.user_profile (user_id, first_name, last_name, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """
            cursor.execute(insert_profile_query, (user_db_id, first_name, last_name, current_time, current_time))
            profile_result = cursor.fetchone()
            
            # Insert into user_learning_preferences table (links via users.id)
            insert_preferences_query = f"""
            INSERT INTO {self.schema}.user_learning_preferences 
                (user_id, preferred_difficulty, preferred_content_type, daily_goal_minutes, 
                 notifications_enabled, email_reminders, dark_mode, auto_play_videos, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            cursor.execute(insert_preferences_query, (user_db_id, skill_level, learning_style,
                                                       daily_goal_minutes, notifications_enabled, 
                                                       email_reminders, dark_mode, auto_play_videos,
                                                       current_time, current_time))
            
            # Commit transaction only after all INSERTs succeed
            conn.commit()
            
            # Sync user to Neo4j graph for relationship queries
            try:
                neo4j_manager = Neo4jManager()
                if neo4j_manager.connect():
                    neo4j_manager.sync_user_to_graph(
                        user_id=user_db_id,
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        skill_level=skill_level,
                        learning_style=learning_style,
                        is_admin=is_admin,
                        admin_role=admin_role
                    )
                    logger.info(f"User synced to Neo4j graph: {user_id}")
                    neo4j_manager.disconnect()
            except Exception as neo4j_error:
                logger.warning(f"Failed to sync user to Neo4j: {neo4j_error}")
            
            # Send verification email if not skipped
            requires_verification = False
            if not skip_verification:
                email_result = asyncio.run(send_verification_email(
                    email=email,
                    username=username,
                    verification_token=verification_token
                ))
                requires_verification = True
                logger.info(f"Verification email sent to {email}: {email_result.get('method', 'unknown')}")
            
            role_msg = f" with {admin_role} privileges" if is_admin else ""
            action_msg = "verification required" if requires_verification else "created and ready to use"
            logger.info(f"User registered successfully: {user_id}{role_msg} - {action_msg}")
            
            return {
                "success": True, 
                "user_id": user_id, 
                "username": username,
                "email": email,
                "is_admin": is_admin,
                "admin_role": admin_role,
                "requires_verification": requires_verification,
                "is_email_verified": is_email_verified,
                "message": f"User created successfully{role_msg}. {'Please check your email to verify your account.' if requires_verification else 'Account is ready to use.'}"
            }
            
        except Exception as e:
            logger.error(f"User registration error: {e}")
            if conn:
                conn.rollback()
            return {"success": False, "error": str(e), "user_id": None}
        finally:
            self._return_connection(conn)
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            dict with 'success', 'token', 'user_data', and 'message' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed", "token": None}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # Find user by username or email (only auth fields from users table)
            cursor.execute(
                f"SELECT id, user_id, username, email, password_hash, is_active, is_admin, admin_role, is_email_verified FROM {self.schema}.users WHERE (username = %s OR email = %s) AND is_active = TRUE",
                (username, username)
            )
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "error": "Invalid credentials", "code": "UNAUTHORIZED", "token": None}
            
            # Check if email is verified
            if not user.get('is_email_verified', False):
                return {
                    "success": False, 
                    "error": "Please verify your email before logging in", 
                    "code": "EMAIL_NOT_VERIFIED", 
                    "token": None,
                    "email": user['email']
                }
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {"success": False, "error": "Invalid credentials", "code": "UNAUTHORIZED", "token": None}
            
            # Fetch profile from user_profile table (links via users.id)
            cursor.execute(
                f"SELECT first_name, last_name, bio, avatar_url, timezone, language FROM {self.schema}.user_profile WHERE user_id = %s",
                (user['id'],)
            )
            profile = cursor.fetchone()
            
            # Fetch preferences from user_learning_preferences table (links via users.id)
            cursor.execute(
                f"SELECT daily_goal_minutes, preferred_difficulty, preferred_content_type, notifications_enabled, email_reminders, dark_mode, auto_play_videos FROM {self.schema}.user_learning_preferences WHERE user_id = %s",
                (user['id'],)
            )
            preferences = cursor.fetchone()
            
            # Generate JWT token
            user_id = user['user_id']
            token_payload = {
                "user_id": user_id,
                "username": user['username'],
                "email": user['email'],
                "is_admin": user.get('is_admin', False),
                "admin_role": user.get('admin_role', 'student'),
                "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
                "iat": datetime.utcnow()
            }
            token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            
            # Update last login
            update_query = f"UPDATE {self.schema}.users SET last_login_at = CURRENT_TIMESTAMP WHERE id = %s"
            cursor.execute(update_query, (user['id'],))
            conn.commit()
            
            logger.info(f"User authenticated successfully: {user_id}")
            return {
                "success": True,
                "access_token": token,
                "token_type": "bearer",
                "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "user_id": user_id,
                    "username": user['username'],
                    "email": user['email'],
                    "is_admin": user.get('is_admin', False),
                    "admin_role": user.get('admin_role', 'student'),
                    "is_email_verified": user.get('is_email_verified', False),
                    "profile": dict(profile) if profile else {},
                    "preferences": dict(preferences) if preferences else {}
                },
                "message": "Login successful"
            }
            
        except Exception as e:
            logger.error(f"User authentication error: {e}")
            return {"success": False, "error": str(e), "token": None}
        finally:
            self._return_connection(conn)
    
    def get_user_by_id(self, user_id: str) -> dict:
        """Get user data by user_id"""
        conn = self._get_connection()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(
                f"SELECT id, user_id, username, email, first_name, last_name, learning_style, skill_level, created_at, is_admin, admin_role FROM {self.schema}.users WHERE id = %s AND is_active = TRUE",
                (user_id,)
            )
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
        finally:
            self._return_connection(conn)
    
    def validate_jwt_token(self, token: str) -> dict:
        """
        Validate JWT token and return user data.
        
        Args:
            token: JWT token string
            
        Returns:
            dict with user data if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return {
                "valid": True,
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "is_admin": payload.get("is_admin", False),
                "admin_role": payload.get("admin_role", "student"),
                "exp": payload.get("exp")
            }
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return {"valid": False, "error": "Invalid token"}
    
    def get_all_users(self, limit: int = 100, offset: int = 0, 
                      include_inactive: bool = False, admin_only: bool = False) -> dict:
        """
        Get all users (admin-only operation).
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            include_inactive: Include inactive users
            admin_only: Only return admin users
            
        Returns:
            dict with 'success', 'users', 'total' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed", "users": []}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if not include_inactive:
                where_conditions.append("is_active = %s")
                params.append(True)
            
            if admin_only:
                where_conditions.append("is_admin = %s")
                params.append(True)
            
            where_clause = " AND ".join(where_conditions)
            where_clause = f"WHERE {where_clause}" if where_conditions else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM {self.schema}.users {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Get users with pagination
            users_query = f"""
            SELECT user_id, username, email, first_name, last_name, learning_style, 
                   skill_level, created_at, last_login_at, is_active, is_admin, admin_role
            FROM {self.schema}.users 
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cursor.execute(users_query, params)
            users = cursor.fetchall()
            
            # Convert to list of dicts
            user_list = []
            for user in users:
                user_dict = dict(user)
                # Convert datetime to ISO string
                if user_dict.get('created_at'):
                    user_dict['created_at'] = user_dict['created_at'].isoformat()
                if user_dict.get('last_login_at'):
                    user_dict['last_login_at'] = user_dict['last_login_at'].isoformat()
                user_list.append(user_dict)
            
            logger.info(f"Retrieved {len(user_list)} users from database")
            return {
                "success": True,
                "users": user_list,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Get all users error: {e}")
            return {"success": False, "error": str(e), "users": []}
        finally:
            self._return_connection(conn)
    
    def update_user_admin_status(self, user_id: str, is_admin: bool, 
                                admin_role: str = "student") -> dict:
        """
        Update user admin status (super admin only operation).
        
        Args:
            user_id: User ID to update
            is_admin: Admin status
            admin_role: Admin role (student, admin, super_admin)
            
        Returns:
            dict with 'success', 'message' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # First get the integer id from the string user_id
            cursor.execute(f"SELECT id FROM {self.schema}.users WHERE user_id = %s", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
            
            user_db_id = user_row['id']
            
            # Check if user exists
            cursor.execute(f"SELECT id FROM {self.schema}.users WHERE id = %s", (user_db_id,))
            existing = cursor.fetchone()
            if not existing:
                return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
            
            # Update admin status
            update_query = f"""
            UPDATE {self.schema}.users 
            SET is_admin = %s, admin_role = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING user_id, username, is_admin, admin_role
            """
            cursor.execute(update_query, (is_admin, admin_role, user_db_id))
            updated_user = cursor.fetchone()
            conn.commit()
            
            action = "granted" if is_admin else "revoked"
            logger.info(f"Admin privileges {action} for user: {user_id} (role: {admin_role})")
            return {
                "success": True,
                "user_id": updated_user['user_id'],
                "username": updated_user['username'],
                "is_admin": updated_user['is_admin'],
                "admin_role": updated_user['admin_role'],
                "message": f"Admin privileges {action} successfully"
            }
            
        except Exception as e:
            logger.error(f"Update admin status error: {e}")
            if conn:
                conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            self._return_connection(conn)
    
    def suspend_user(self, user_id: str, suspended: bool = True) -> dict:
        """
        Suspend or unsuspend a user account (admin operation).
        
        Args:
            user_id: User ID to suspend/unsuspend
            suspended: True to suspend, False to unsuspend
            
        Returns:
            dict with 'success', 'message' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # First get the integer id from the string user_id
            cursor.execute(f"SELECT id, username FROM {self.schema}.users WHERE user_id = %s", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
            
            user_db_id = user_row['id']
            existing_username = user_row['username']
            
            # Check if user exists
            cursor.execute(f"SELECT id, username FROM {self.schema}.users WHERE id = %s", (user_db_id,))
            existing = cursor.fetchone()
            if not existing:
                return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
            
            # Update user status
            is_active = not suspended
            update_query = f"""
            UPDATE {self.schema}.users 
            SET is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING user_id, username, is_active
            """
            cursor.execute(update_query, (is_active, user_db_id))
            updated_user = cursor.fetchone()
            conn.commit()
            
            action = "suspended" if suspended else "activated"
            logger.info(f"User {action}: {existing_username} ({user_id})")
            return {
                "success": True,
                "user_id": updated_user['user_id'],
                "username": updated_user['username'],
                "is_active": updated_user['is_active'],
                "message": f"User {action} successfully"
            }
            
        except Exception as e:
            logger.error(f"Suspend user error: {e}")
            if conn:
                conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            self._return_connection(conn)
    
    def verify_email(self, verification_token: str) -> dict:
        """
        Verify a user's email using the verification token.
        
        Args:
            verification_token: The verification token from the email link
            
        Returns:
            dict with 'success', 'message' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # Find user with this verification token
            cursor.execute(f"""
                SELECT id, user_id, username, email, token_expires_at, is_email_verified 
                FROM {self.schema}.users 
                WHERE verification_token = %s
            """, (verification_token,))
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "error": "Invalid verification token", "code": "INVALID_TOKEN"}
            
            # Check if already verified
            if user.get('is_email_verified', False):
                return {"success": True, "message": "Email is already verified", "code": "ALREADY_VERIFIED"}
            
            # Check if token has expired
            if user.get('token_expires_at') and user['token_expires_at'] < datetime.utcnow():
                return {
                    "success": False, 
                    "error": "Verification token has expired. Please request a new verification email.",
                    "code": "TOKEN_EXPIRED",
                    "email": user['email']
                }
            
            # Update user to verified
            cursor.execute(f"""
                UPDATE {self.schema}.users 
                SET is_email_verified = TRUE, 
                    verification_token = NULL, 
                    token_expires_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING user_id, username, email
            """, (user['id'],))
            updated_user = cursor.fetchone()
            conn.commit()
            
            logger.info(f"Email verified successfully for user: {updated_user['username']}")

            # Send welcome email (non-blocking - don't fail verification if email fails)
            try:
                welcome_result = asyncio.run(send_welcome_email(email=updated_user['email'], username=updated_user['username']))
                if welcome_result.get('success'):
                    logger.info(f"Welcome email sent successfully to {updated_user['email']}")
                else:
                    logger.warning(f"Welcome email failed to send to {updated_user['email']}: {welcome_result.get('error')}")
            except Exception as welcome_error:
                logger.error(f"Exception sending welcome email to {updated_user['email']}: {welcome_error}")

            return {
                "success": True,
                "message": "Email verified successfully! Welcome to Jeseci Smart Learning Academy.",
                "user_id": updated_user['user_id'],
                "username": updated_user['username']
            }
            
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            if conn:
                conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            self._return_connection(conn)
    
    def resend_verification_email(self, email: str) -> dict:
        """
        Resend verification email to a user.
        
        Args:
            email: User's email address
            
        Returns:
            dict with 'success', 'message' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # Check if user exists and email is not verified
            cursor.execute(f"""
                SELECT user_id, username, is_email_verified 
                FROM {self.schema}.users 
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "error": "User not found", "code": "NOT_FOUND"}
            
            if user.get('is_email_verified', False):
                return {"success": False, "error": "Email is already verified", "code": "ALREADY_VERIFIED"}
            
            # Generate new verification token
            new_token = generate_verification_token()
            expires_at = get_token_expiration()
            
            # Update user's verification token
            cursor.execute(f"""
                UPDATE {self.schema}.users 
                SET verification_token = %s, token_expires_at = %s, updated_at = CURRENT_TIMESTAMP
                WHERE email = %s
                RETURNING user_id, username
            """, (new_token, expires_at, email))
            updated_user = cursor.fetchone()
            conn.commit()
            
            # Send verification email
            email_result = asyncio.run(send_verification_email(
                email=email,
                username=updated_user['username'],
                verification_token=new_token
            ))
            
            logger.info(f"Verification email resent to {email}")
            
            return {
                "success": True,
                "message": "Verification email sent successfully",
                "method": email_result.get("method", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Resend verification email error: {e}")
            if conn:
                conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            self._return_connection(conn)
    
    def get_user_verification_status(self, user_id: str) -> dict:
        """
        Get user's email verification status.
        
        Args:
            user_id: User ID
            
        Returns:
            dict with verification status
        """
        conn = self._get_connection()
        if conn is None:
            return {"is_verified": False}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # First get the integer id from the string user_id
            cursor.execute(f"SELECT id FROM {self.schema}.users WHERE user_id = %s", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                return {"is_verified": False}
            
            user_db_id = user_row['id']
            
            cursor.execute(f"""
                SELECT is_email_verified, verification_token, token_expires_at
                FROM {self.schema}.users 
                WHERE id = %s
            """, (user_db_id,))
            user = cursor.fetchone()
            
            if not user:
                return {"is_verified": False}
            
            return {
                "is_verified": user.get('is_email_verified', False),
                "has_pending_token": user.get('verification_token') is not None,
                "token_expires_at": user.get('token_expires_at').isoformat() if user.get('token_expires_at') else None
            }
            
        except Exception as e:
            logger.error(f"Get verification status error: {e}")
            return {"is_verified": False}
        finally:
            self._return_connection(conn)
    
    def close(self):
        """Close all connections"""
        if UserAuthManager._pool:
            UserAuthManager._pool.closeall()
            UserAuthManager._pool = None
            logger.info("User auth connection pool closed")


# Global instance
auth_manager = UserAuthManager()


def register_user(username: str, email: str, password: str, 
                  first_name: str = "", last_name: str = "",
                  learning_style: str = "visual", skill_level: str = "beginner",
                  is_admin: bool = False, admin_role: str = "student",
                  skip_verification: bool = False,
                  daily_goal_minutes: int = 30,
                  notifications_enabled: bool = True,
                  email_reminders: bool = True,
                  dark_mode: bool = False,
                  auto_play_videos: bool = True) -> dict:
    """Wrapper function for Jaclang integration"""
    return auth_manager.register_user(username, email, password, first_name, last_name, 
                                    learning_style, skill_level, is_admin, admin_role,
                                    skip_verification, daily_goal_minutes, notifications_enabled,
                                    email_reminders, dark_mode, auto_play_videos)


def authenticate_user(username: str, password: str) -> dict:
    """Wrapper function for Jaclang integration"""
    return auth_manager.authenticate_user(username, password)


def verify_email(verification_token: str) -> dict:
    """Wrapper function for email verification"""
    return auth_manager.verify_email(verification_token)


def resend_verification_email(email: str) -> dict:
    """Wrapper function for resending verification email"""
    return auth_manager.resend_verification_email(email)


def get_user_verification_status(user_id: str) -> dict:
    """Wrapper function for getting user verification status"""
    return auth_manager.get_user_verification_status(user_id)


def get_user_by_id(user_id: str) -> dict:
    """Wrapper function for Jaclang integration"""
    return auth_manager.get_user_by_id(user_id)


# =============================================================================
# Admin Functions - Wrapper functions for admin operations
# =============================================================================

def validate_jwt_token(token: str) -> dict:
    """Wrapper function for JWT token validation"""
    return auth_manager.validate_jwt_token(token)


def get_all_users(limit: int = 100, offset: int = 0, 
                  include_inactive: bool = False, admin_only: bool = False) -> dict:
    """Wrapper function for getting all users (admin only)"""
    return auth_manager.get_all_users(limit, offset, include_inactive, admin_only)


def update_user_admin_status(user_id: str, is_admin: bool, admin_role: str = "student") -> dict:
    """Wrapper function for updating user admin status (super admin only)"""
    return auth_manager.update_user_admin_status(user_id, is_admin, admin_role)


def suspend_user(user_id: str, suspended: bool = True) -> dict:
    """Wrapper function for suspending/unsuspending users (admin only)"""
    return auth_manager.suspend_user(user_id, suspended)
