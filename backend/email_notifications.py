# Email notification module for Jaclang backend
# This module handles all email-related functionality

import os

# Try to import aiosmtplib for async email sending
try:
    from aiosmtplib import SMTP
    from email.message import EmailMessage
    HAS_AIOSMTPLIB = True
except ImportError:
    HAS_AIOSMTPLIB = False
    # Fallback to synchronous smtplib
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

# Import centralized logging configuration
from logger_config import logger

# Email configuration
SMTP_SERVER = os.getenv("SMTP_HOST", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
FROM_EMAIL = os.getenv("SMTP_FROM", os.getenv("FROM_EMAIL", "noreply@jeseci.com"))
EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD", os.getenv("EMAIL_PASSWORD", ""))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@jeseci.com")


async def _send_email_async(to_email: str, subject: str, body: str) -> dict:
    """
    Send email using aiosmtplib (async)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        
    Returns:
        dict with 'success' key
    """
    if not HAS_AIOSMTPLIB:
        raise ImportError("aiosmtplib is not installed")
    
    if not EMAIL_PASSWORD:
        logger.info(f"Email credentials not configured - email would be sent to: {to_email}")
        return {"success": True}
    
    try:
        msg = EmailMessage()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)
        
        # Create SSL context for secure connection
        import ssl
        context = ssl.create_default_context()
        
        # Send email using aiosmtplib with proper TLS handling
        async with SMTP(
            hostname=SMTP_SERVER, 
            port=SMTP_PORT, 
            timeout=30,
            validate_certs=True
        ) as smtp:
            # For port 587, we need to use STARTTLS properly
            # Gmail always supports STARTTLS on port 587
            try:
                await smtp.starttls(context=context)
            except Exception:
                # If starttls fails, connection might already be TLS
                pass
            
            await smtp.login(FROM_EMAIL, EMAIL_PASSWORD)
            await smtp.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return {"success": True}
        
    except Exception as error:
        logger.error(f"Failed to send email to {to_email}: {error}")
        return {"success": False, "error": str(error)}


def _send_email_sync(to_email: str, subject: str, body: str) -> dict:
    """
    Send email using smtplib (sync fallback)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        
    Returns:
        dict with 'success' key
    """
    if not EMAIL_PASSWORD:
        logger.info(f"Email credentials not configured - email would be sent to: {to_email}")
        return {"success": True}
    
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email using smtplib with proper TLS context
        import ssl
        context = ssl.create_default_context()
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()  # Re-EHLO after TLS upgrade
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return {"success": True}
        
    except Exception as error:
        logger.error(f"Failed to send email to {to_email}: {error}")
        return {"success": False, "error": str(error)}


async def send_contact_notification(contact_data: dict) -> dict:
    """
    Send email notification to admin about new contact form submission (async)
    
    Args:
        contact_data: Dictionary containing contact form data
        
    Returns:
        dict with 'success', 'method' keys
    """
    try:
        # Check if email is configured
        if not EMAIL_PASSWORD:
            logger.info("NEW CONTACT MESSAGE:")
            logger.info(f"Name: {contact_data['name']}")
            logger.info(f"Email: {contact_data['email']}")
            logger.info(f"Subject: {contact_data['subject']}")
            logger.info(f"Message: {contact_data['message']}")
            return {"success": True, "method": "console"}
        
        # Build email content
        subject = f"New Contact Form Submission: {contact_data['subject']}"
        body = f"""New contact form submission received.

Details:
- Name: {contact_data['name']}
- Email: {contact_data['email']}
- Phone: {contact_data.get('phone', 'N/A')}
- Reason: {contact_data.get('contact_reason', 'General')}
- Subject: {contact_data['subject']}
- Message ID: {contact_data['message_id']}
- Timestamp: {contact_data['timestamp']}

Message:
{contact_data['message']}

Please respond within 24 hours.
"""
        
        # Send email
        if HAS_AIOSMTPLIB:
            result = await _send_email_async(ADMIN_EMAIL, subject, body)
        else:
            result = _send_email_sync(ADMIN_EMAIL, subject, body)
        
        if result.get("success"):
            return {"success": True, "method": "email"}
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}
        
    except Exception as error:
        logger.error(f"Contact notification error: {error}")
        return {"success": False, "error": str(error)}


async def send_confirmation_email(contact_data: dict) -> dict:
    """
    Send confirmation email to the user who submitted the contact form (async)
    
    Args:
        contact_data: Dictionary containing contact form data
        
    Returns:
        dict with 'success', 'method' keys
    """
    try:
        # Check if email is configured
        if not EMAIL_PASSWORD:
            logger.info(f"Confirmation email would be sent to: {contact_data['email']}")
            return {"success": True, "method": "console"}
        
        # Build email content
        subject = "Thank you for contacting Jeseci Smart Learning Academy"
        body = f"""Dear {contact_data['name']},

Thank you for contacting Jeseci Smart Learning Academy!

We have received your message regarding: {contact_data['subject']}

Your message ID is: {contact_data['message_id']}
Submitted at: {contact_data['timestamp']}

Our team will review your inquiry and respond within 24 hours during business days.

Best regards,
The Jeseci Smart Learning Academy Team

---
This is an automated confirmation. Please do not reply to this email.
"""
        
        # Send email
        if HAS_AIOSMTPLIB:
            result = await _send_email_async(contact_data['email'], subject, body)
        else:
            result = _send_email_sync(contact_data['email'], subject, body)
        
        if result.get("success"):
            return {"success": True, "method": "email"}
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}
        
    except Exception as error:
        logger.error(f"Confirmation email error: {error}")
        return {"success": False, "error": str(error)}
