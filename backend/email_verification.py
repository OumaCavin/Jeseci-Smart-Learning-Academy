"""
Email Verification Module for Jeseci Smart Learning Academy

This module handles email verification functionality including:
- Verification token generation
- Sending verification emails
- Token validation and user verification
"""

import os
import secrets
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@jeseci.com")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@jeseci.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Token configuration
VERIFICATION_TOKEN_EXPIRE_HOURS = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_HOURS", 24))


def generate_verification_token() -> str:
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


def get_token_expiration() -> datetime:
    """Get the expiration time for a verification token"""
    return datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)


def send_verification_email(email: str, username: str, verification_token: str) -> dict:
    """
    Send email verification email to user
    
    Args:
        email: Recipient email address
        username: User's username
        verification_token: Unique verification token
        
    Returns:
        dict with 'success', 'method' keys
    """
    try:
        # Build verification link
        verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
        
        # Create email content
        subject = "Verify Your Email - Jeseci Smart Learning Academy"
        
        # Plain text body
        body = f"""Welcome to Jeseci Smart Learning Academy, {username}!

Thank you for creating an account. Please verify your email address to get started.

Click the link below to verify your email:
{verification_link}

This link will expire in {VERIFICATION_TOKEN_EXPIRE_HOURS} hours.

If you didn't create an account with us, please ignore this email.

Best regards,
The Jeseci Smart Learning Academy Team
"""
        
        # HTML body for better email client support
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Jeseci Smart Learning Academy</h1>
        </div>
        <div class="content">
            <h2>Welcome, {username}!</h2>
            <p>Thank you for creating an account with Jeseci Smart Learning Academy.</p>
            <p>Please verify your email address to get started with your learning journey.</p>
            <p style="text-align: center;">
                <a href="{verification_link}" class="button">Verify Email Address</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="background: #e5e7eb; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px;">{verification_link}</p>
            <p><strong>This link will expire in {VERIFICATION_TOKEN_EXPIRE_HOURS} hours.</strong></p>
        </div>
        <div class="footer">
            <p>If you didn't create an account with us, please ignore this email.</p>
            <p>© {datetime.now().year} Jeseci Smart Learning Academy. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        if not EMAIL_PASSWORD:
            logger.info(f"Email password not configured - verification email for {email}:")
            logger.info(f"Verification link: {verification_link}")
            return {"success": True, "method": "console"}
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, email, text)
        server.quit()
        
        logger.info(f"Verification email sent to {email}")
        return {"success": True, "method": "email"}
        
    except Exception as error:
        logger.error(f"Failed to send verification email to {email}: {error}")
        return {"success": False, "error": str(error)}


def send_welcome_email(email: str, username: str) -> dict:
    """
    Send welcome email after email is verified
    
    Args:
        email: Recipient email address
        username: User's username
        
    Returns:
        dict with 'success', 'method' keys
    """
    try:
        subject = "Welcome to Jeseci Smart Learning Academy!"
        
        body = f"""Welcome aboard, {username}!

Your email has been successfully verified. You now have full access to Jeseci Smart Learning Academy.

Getting Started:
1. Complete your profile
2. Explore our courses
3. Start learning!

If you have any questions, feel free to reach out to our support team.

Best regards,
The Jeseci Smart Learning Academy Team
"""
        
        if not EMAIL_PASSWORD:
            logger.info(f"Welcome email for {username} ({email}) - console mode")
            return {"success": True, "method": "console"}
        
        msg = MIMEText(body, 'plain')
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.sendmail(FROM_EMAIL, email, msg.as_string())
        server.quit()
        
        logger.info(f"Welcome email sent to {email}")
        return {"success": True, "method": "email"}
        
    except Exception as error:
        logger.error(f"Failed to send welcome email to {email}: {error}")
        return {"success": False, "error": str(error)}


def resend_verification_email(email: str) -> dict:
    """
    Resend verification email to a user
    
    Args:
        email: User's email address
        
    Returns:
        dict with 'success', 'message' keys
    """
    # Import here to avoid circular imports
    import psycopg2
    from psycopg2 import extras
    from dotenv import load_dotenv
    import os
    
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))
    
    # Database Schema Configuration
    DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")
    
    conn = None
    try:
        # Get database connection
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database=os.getenv("POSTGRES_DB", "jeseci_learning_academy"),
            user=os.getenv("POSTGRES_USER", "jeseci_academy_user"),
            password=os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
        )
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # Check if user exists and email is not verified
        cursor.execute(f"""
            SELECT user_id, username, is_email_verified 
            FROM {DB_SCHEMA}.users 
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
            UPDATE {DB_SCHEMA}.users 
            SET verification_token = %s, token_expires_at = %s
            WHERE email = %s
            RETURNING user_id, username
        """, (new_token, expires_at, email))
        updated_user = cursor.fetchone()
        conn.commit()
        
        # Send verification email
        email_result = send_verification_email(
            email=email,
            username=updated_user['username'],
            verification_token=new_token
        )
        
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
        if conn:
            conn.close()
