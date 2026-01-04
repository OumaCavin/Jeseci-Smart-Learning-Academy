"""
Password Reset Module for Jeseci Smart Learning Academy

This module handles password reset functionality including:
- Password reset token generation
- Sending password reset emails
- Token validation and password reset
- Token cleanup and expiration management

Author: Cavin Otieno
License: MIT License
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
import psycopg2
from psycopg2 import pool, extras

# Import centralized logging configuration
from logger_config import logger

# Email configuration
SMTP_SERVER = os.getenv("SMTP_HOST", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
FROM_EMAIL = os.getenv("SMTP_FROM", os.getenv("FROM_EMAIL", "noreply@jeseci.com"))
EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD", os.getenv("EMAIL_PASSWORD", ""))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Token configuration
RESET_TOKEN_EXPIRE_HOURS = int(os.getenv("RESET_TOKEN_EXPIRE_HOURS", 1))


class PasswordResetManager:
    """
    Manages password reset operations with PostgreSQL.
    
    Provides secure password reset functionality with time-limited
    tokens sent via email.
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
            PasswordResetManager._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            logger.info(f"Password reset PostgreSQL pool initialized: {config['host']}:{config['port']}/{config['database']}")
            self._ensure_tables()
        except Exception as e:
            logger.error(f"Failed to initialize password reset PostgreSQL pool: {e}")
            PasswordResetManager._pool = None
    
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
        if PasswordResetManager._pool is None:
            self._initialize_pool()
        if PasswordResetManager._pool:
            return PasswordResetManager._pool.getconn()
        return None
    
    def _return_connection(self, conn):
        """Return a connection to the pool"""
        if conn and PasswordResetManager._pool:
            PasswordResetManager._pool.putconn(conn)
    
    def _ensure_tables(self):
        """Ensure the password reset tokens table exists"""
        conn = self._get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                schema = os.getenv("DB_SCHEMA", "jeseci_academy")
                
                # Create password reset tokens table
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.password_reset_tokens (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES {schema}.users(id) ON DELETE CASCADE,
                        token VARCHAR(128) NOT NULL UNIQUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        is_used BOOLEAN DEFAULT FALSE,
                        ip_address VARCHAR(50),
                        user_agent TEXT
                    )
                """)
                
                # Add is_used column if it doesn't exist (for existing tables)
                try:
                    cursor.execute(f"""
                        ALTER TABLE {schema}.password_reset_tokens
                        ADD COLUMN IF NOT EXISTS is_used BOOLEAN DEFAULT FALSE
                    """)
                except Exception as e:
                    logger.debug(f"is_used column might already exist: {e}")
                
                # Create index for faster token lookups
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_password_reset_token
                    ON {schema}.password_reset_tokens (token)
                """)
                
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_password_reset_user
                    ON {schema}.password_reset_tokens (user_id)
                """)
                
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_password_reset_expires
                    ON {schema}.password_reset_tokens (expires_at)
                """)
                
                conn.commit()
                cursor.close()
                logger.info("Password reset tokens table ensured")
            except Exception as e:
                logger.error(f"Failed to create password reset tokens table: {e}")
            finally:
                self._return_connection(conn)
    
    def generate_reset_token(self, user_id: int) -> str:
        """Generate a secure password reset token for a user"""
        return secrets.token_urlsafe(32)
    
    def get_token_expiration(self) -> datetime:
        """Get the expiration time for a reset token"""
        return datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    
    def create_reset_request(self, email: str, ip_address: str = None, user_agent: str = None) -> dict:
        """
        Create a password reset request for a given email
        
        Args:
            email: User's email address
            ip_address: Client IP address (optional)
            user_agent: Client user agent (optional)
            
        Returns:
            dict with success status and message
        """
        conn = self._get_connection()
        if not conn:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            schema = os.getenv("DB_SCHEMA", "jeseci_academy")
            
            # Find user by email
            cursor.execute(f"""
                SELECT id, username FROM {schema}.users WHERE email = %s
            """, (email,))
            
            user = cursor.fetchone()
            
            if not user:
                # Return success even if user not found to prevent email enumeration
                return {
                    "success": True,
                    "message": "If an account with that email exists, a password reset link has been sent"
                }
            
            user_id, username = user
            
            # Generate reset token
            token = self.generate_reset_token(user_id)
            expires_at = self.get_token_expiration()
            
            # Invalidate any existing unused tokens for this user
            cursor.execute(f"""
                UPDATE {schema}.password_reset_tokens
                SET is_used = TRUE
                WHERE user_id = %s AND is_used = FALSE
            """, (user_id,))
            
            # Store new reset token
            cursor.execute(f"""
                INSERT INTO {schema}.password_reset_tokens
                (user_id, token, expires_at, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, token, expires_at, ip_address, user_agent))
            
            conn.commit()
            cursor.close()
            
            # Send reset email (best effort - email failure should not fail the request)
            reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
            try:
                send_password_reset_email(email, username, reset_link)
            except Exception as email_error:
                # Log email failure but don't fail the request
                logger.error(f"Failed to send password reset email: {email_error}")
                logger.info(f"Password reset link for {email}: {reset_link}")
            
            logger.info(f"Password reset token created for user {username} (ID: {user_id})")
            
            return {
                "success": True,
                "message": "If an account with that email exists, a password reset link has been sent"
            }
            
        except Exception as e:
            logger.error(f"Failed to create password reset request: {e}")
            return {"success": False, "error": "Failed to process request: " + str(e)}
        finally:
            self._return_connection(conn)
    
    def validate_reset_token(self, token: str) -> dict:
        """
        Validate a password reset token
        
        Args:
            token: The reset token to validate
            
        Returns:
            dict with validation status and user info if valid
        """
        conn = self._get_connection()
        if not conn:
            return {"valid": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            schema = os.getenv("DB_SCHEMA", "jeseci_academy")
            
            # Find valid (not used, not expired) token
            cursor.execute(f"""
                SELECT t.id, t.user_id, u.username, u.email, t.created_at, t.expires_at
                FROM {schema}.password_reset_tokens t
                JOIN {schema}.users u ON t.user_id = u.id
                WHERE t.token = %s
                AND t.is_used = FALSE
                AND t.expires_at > NOW()
            """, (token,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return {"valid": False, "error": "Invalid or expired reset token"}
            
            token_id, user_id, username, email, created_at, expires_at = result
            
            return {
                "valid": True,
                "user_id": user_id,
                "username": username,
                "email": email,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to validate reset token: {e}")
            return {"valid": False, "error": "Token validation failed"}
        finally:
            self._return_connection(conn)
    
    def reset_password(self, token: str, new_password: str) -> dict:
        """
        Reset a user's password using a valid reset token
        
        Args:
            token: The reset token
            new_password: The new password (plain text, will be hashed)
            
        Returns:
            dict with success status and message
        """
        # First validate the token
        validation = self.validate_reset_token(token)
        if not validation.get("valid"):
            return {"success": False, "error": validation.get("error", "Invalid token")}
        
        user_id = validation["user_id"]
        conn = self._get_connection()
        
        if not conn:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            schema = os.getenv("DB_SCHEMA", "jeseci_academy")
            
            # Hash the new password
            password_hash = hash_password(new_password)
            
            # Update user's password
            cursor.execute(f"""
                UPDATE {schema}.users
                SET password_hash = %s, updated_at = NOW()
                WHERE id = %s
            """, (password_hash, user_id))
            
            # Mark token as used
            cursor.execute(f"""
                UPDATE {schema}.password_reset_tokens
                SET is_used = TRUE
                WHERE token = %s
            """, (token,))
            
            # Invalidate all other unused tokens for this user
            cursor.execute(f"""
                UPDATE {schema}.password_reset_tokens
                SET is_used = TRUE
                WHERE user_id = %s AND is_used = FALSE AND token != %s
            """, (user_id, token))
            
            conn.commit()
            cursor.close()
            
            logger.info(f"Password reset completed for user ID: {user_id}")
            
            return {
                "success": True,
                "message": "Password has been reset successfully. You can now login with your new password."
            }
            
        except Exception as e:
            logger.error(f"Failed to reset password: {e}")
            return {"success": False, "error": "Failed to reset password"}
        finally:
            self._return_connection(conn)
    
    def cleanup_expired_tokens(self) -> dict:
        """
        Clean up expired reset tokens from the database
        
        Returns:
            dict with number of deleted tokens
        """
        conn = self._get_connection()
        if not conn:
            return {"deleted": 0}
        
        try:
            cursor = conn.cursor()
            schema = os.getenv("DB_SCHEMA", "jeseci_academy")
            
            cursor.execute(f"""
                DELETE FROM {schema}.password_reset_tokens
                WHERE expires_at < NOW() OR is_used = TRUE
            """)
            
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired/used reset tokens")
            
            return {"deleted": deleted_count}
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens: {e}")
            return {"deleted": 0}
        finally:
            self._return_connection(conn)


# Singleton instance
reset_manager = PasswordResetManager()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    import bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    import bcrypt
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def send_password_reset_email(email: str, username: str, reset_link: str) -> bool:
    """
    Send a password reset email to the user
    
    Args:
        email: Recipient email address
        username: User's username
        reset_link: Password reset link
        
    Returns:
        bool indicating success
    """
    # Try to use aiosmtplib for async email sending
    try:
        from aiosmtplib import SMTP
        from email.message import EmailMessage
        HAS_AIOSMTPLIB = True
    except ImportError:
        HAS_AIOSMTPLIB = False
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
    
    current_year = datetime.now().year
    
    # Plain text body
    plain_body = f"""Hello {username},

We received a request to reset your password for Jeseci Smart Learning Academy.

Click the link below to reset your password:
{reset_link}

This link will expire in {RESET_TOKEN_EXPIRE_HOURS} hour(s).

If you didn't request this password reset, please ignore this email or contact support if you have concerns.

Best regards,
The Jeseci Smart Learning Academy Team
"""
    
    # HTML body
    html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
        .button {{ display: inline-block; background: #ef4444; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset Request</h1>
        </div>
        <div class="content">
            <h2>Hello, {username}!</h2>
            <p>We received a request to reset your password for Jeseci Smart Learning Academy.</p>
            <p style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="background: #e5e7eb; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px;">{reset_link}</p>
            <div class="warning">
                <p><strong>This link will expire in {RESET_TOKEN_EXPIRE_HOURS} hour(s).</strong></p>
                <p>If you didn't request this password reset, please ignore this email.</p>
            </div>
        </div>
        <div class="footer">
            <p>© {current_year} Jeseci Smart Learning Academy. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    
    if HAS_AIOSMTPLIB:
        # Async email sending (would need to be called from async context)
        logger.warning("Async email sending not implemented in password_reset.py")
        logger.info(f"Password reset email would be sent to {email}")
        logger.info(f"Reset link: {reset_link}")
        return True
    else:
        # Synchronous email sending
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Password Reset Request - Jeseci Smart Learning Academy"
            msg['From'] = FROM_EMAIL
            msg['To'] = email
            
            part1 = MIMEText(plain_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(FROM_EMAIL, EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            # Log the email content for development
            logger.info(f"Password reset link for {email}: {reset_link}")
            return False


# Module-level functions for use by Jaclang walkers

def create_password_reset_request(email: str, ip_address: str = None, user_agent: str = None) -> dict:
    """Create a password reset request for the given email"""
    return reset_manager.create_reset_request(email, ip_address, user_agent)


def validate_password_reset_token(token: str) -> dict:
    """Validate a password reset token"""
    return reset_manager.validate_reset_token(token)


def reset_user_password(token: str, new_password: str) -> dict:
    """Reset a user's password using a valid token"""
    return reset_manager.reset_password(token, new_password)


def cleanup_expired_reset_tokens() -> dict:
    """Clean up expired reset tokens"""
    return reset_manager.cleanup_expired_tokens()
