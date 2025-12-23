"""
User Authentication Module for Jeseci Smart Learning Academy

This module handles PostgreSQL-based user registration and login operations
with secure password hashing using bcrypt and JWT token generation.

Author: Cavin Otieno
License: MIT License
"""

import os
import psycopg2
from psycopg2 import pool, extras
import bcrypt
import jwt
from datetime import datetime, timedelta
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jeseci_secret_key_change_in_production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))


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
            self._ensure_tables()
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
            'password': os.getenv("POSTGRES_PASSWORD", "secure_password_123")
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
    
    def _ensure_tables(self):
        """Create users table if it doesn't exist"""
        conn = self._get_connection()
        if conn is None:
            logger.error("Cannot create users table: no database connection")
            return
        
        try:
            cursor = conn.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(64) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                learning_style VARCHAR(50) DEFAULT 'visual',
                skill_level VARCHAR(50) DEFAULT 'beginner',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            """
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("Users table ensured in PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to create users table: {e}")
            if conn:
                conn.rollback()
        finally:
            self._return_connection(conn)
    
    def register_user(self, username: str, email: str, password: str, 
                      first_name: str = "", last_name: str = "",
                      learning_style: str = "visual", skill_level: str = "beginner") -> dict:
        """
        Register a new user with bcrypt password hashing.
        
        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name
            learning_style: User's preferred learning style
            skill_level: User's skill level
            
        Returns:
            dict with 'success', 'user_id', and 'message' keys
        """
        conn = self._get_connection()
        if conn is None:
            return {"success": False, "error": "Database connection failed", "user_id": None}
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            # Check if user already exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s OR email = %s", (username, email))
            existing = cursor.fetchone()
            if existing:
                return {"success": False, "error": "Username or email already exists", "user_id": None, "code": "CONFLICT"}
            
            # Generate unique user_id
            user_id = f"user_{username}_{uuid.uuid4().hex[:8]}"
            
            # Hash password with bcrypt
            salt = bcrypt.gensalt(rounds=12)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            # Insert new user
            insert_query = """
            INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, learning_style, skill_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            cursor.execute(insert_query, (user_id, username, email, password_hash, first_name, last_name, learning_style, skill_level))
            conn.commit()
            
            logger.info(f"User registered successfully: {user_id}")
            return {
                "success": True, 
                "user_id": user_id, 
                "username": username,
                "email": email,
                "message": "User created successfully"
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
            
            # Find user by username or email
            cursor.execute(
                "SELECT user_id, username, email, password_hash, first_name, last_name, learning_style, skill_level, is_active FROM users WHERE (username = %s OR email = %s) AND is_active = TRUE",
                (username, username)
            )
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "error": "Invalid credentials", "code": "UNAUTHORIZED", "token": None}
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {"success": False, "error": "Invalid credentials", "code": "UNAUTHORIZED", "token": None}
            
            # Generate JWT token
            user_id = user['user_id']
            token_payload = {
                "user_id": user_id,
                "username": user['username'],
                "email": user['email'],
                "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
                "iat": datetime.utcnow()
            }
            token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            
            # Update last login
            update_query = "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE user_id = %s"
            cursor.execute(update_query, (user_id,))
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
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "learning_style": user['learning_style'],
                    "skill_level": user['skill_level']
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
                "SELECT user_id, username, email, first_name, last_name, learning_style, skill_level, created_at FROM users WHERE user_id = %s AND is_active = TRUE",
                (user_id,)
            )
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
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
                  learning_style: str = "visual", skill_level: str = "beginner") -> dict:
    """Wrapper function for Jaclang integration"""
    return auth_manager.register_user(username, email, password, first_name, last_name, learning_style, skill_level)


def authenticate_user(username: str, password: str) -> dict:
    """Wrapper function for Jaclang integration"""
    return auth_manager.authenticate_user(username, password)


def get_user_by_id(user_id: str) -> dict:
    """Wrapper function for Jaclang integration"""
    return auth_manager.get_user_by_id(user_id)
