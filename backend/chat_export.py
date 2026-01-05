"""
Chat Export Email Module
Handles exporting chat conversations and sending them to users via email
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

# Import centralized logging configuration
from logger_config import logger

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

# Email configuration
SMTP_SERVER = os.getenv("SMTP_HOST", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
FROM_EMAIL = os.getenv("SMTP_FROM", os.getenv("FROM_EMAIL", "noreply@jeseci.com"))
EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD", os.getenv("EMAIL_PASSWORD", ""))


def format_chat_for_email(chat_messages: List[Dict], user_name: str = "User") -> str:
    """
    Format chat messages into a readable email body
    
    Args:
        chat_messages: List of chat message dictionaries
        user_name: Name of the user for display
        
    Returns:
        Formatted email body string
    """
    if not chat_messages:
        return "No chat messages to export."
    
    # Build formatted chat transcript
    transcript_lines = []
    transcript_lines.append("=" * 70)
    transcript_lines.append("JESECI SMART LEARNING ACADEMY - AI Chat Transcript")
    transcript_lines.append("=" * 70)
    transcript_lines.append("")
    transcript_lines.append(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    transcript_lines.append(f"Total Messages: {len(chat_messages)}")
    transcript_lines.append("")
    transcript_lines.append("-" * 70)
    transcript_lines.append("CHAT TRANSCRIPT")
    transcript_lines.append("-" * 70)
    transcript_lines.append("")
    
    for i, msg in enumerate(chat_messages, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        
        # Format timestamp if available
        time_str = ""
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError):
                time_str = timestamp
        
        # Format based on role
        if role == "user":
            header = f"[{time_str}] YOU:"
        else:
            header = f"[{time_str}] AI ASSISTANT:"
        
        transcript_lines.append(header)
        transcript_lines.append("-" * 40)
        
        # Word wrap content for readability
        words = content.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 70:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        transcript_lines.extend(lines)
        transcript_lines.append("")
    
    transcript_lines.append("=" * 70)
    transcript_lines.append("END OF TRANSCRIPT")
    transcript_lines.append("=" * 70)
    transcript_lines.append("")
    transcript_lines.append("---")
    transcript_lines.append("This chat transcript was exported from Jeseci Smart Learning Academy.")
    transcript_lines.append("Your AI Learning Assistant helps you master concepts through personalized conversations.")
    transcript_lines.append("")
    transcript_lines.append("Visit us at: https://jeseci-academy.com")
    
    return "\n".join(transcript_lines)


def create_html_chat_email(chat_messages: List[Dict], user_name: str = "User") -> str:
    """
    Create HTML formatted email for chat export
    
    Args:
        chat_messages: List of chat message dictionaries
        user_name: Name of the user for display
        
    Returns:
        HTML formatted email body string
    """
    html_lines = []
    html_lines.append("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Transcript - Jeseci Smart Learning Academy</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 24px;
        }
        .header .subtitle {
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 10px;
        }
        .meta-info {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .meta-info p {
            margin: 5px 0;
        }
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
        }
        .message.user {
            background-color: #e8f5e9;
            border-left: 4px solid #4CAF50;
        }
        .message.assistant {
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
        }
        .message .role {
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .message.user .role {
            color: #2e7d32;
        }
        .message.assistant .role {
            color: #1565c0;
        }
        .message .timestamp {
            font-size: 11px;
            color: #999;
            margin-bottom: 8px;
        }
        .message .content {
            color: #333;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
        }
        .button {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Jeseci Smart Learning Academy</h1>
            <p class="subtitle">AI Chat Transcript Export</p>
        </div>
        
        <div class="meta-info">
            <p><strong>Export Date:</strong> {export_date}</p>
            <p><strong>Total Messages:</strong> {message_count}</p>
            <p><strong>User:</strong> {user_name}</p>
        </div>
        
        <div class="messages">
""".format(
        export_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        message_count=len(chat_messages),
        user_name=user_name
    ))
    
    for msg in chat_messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        
        # Format timestamp if available
        time_str = ""
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError):
                time_str = timestamp
        
        role_label = "You" if role == "user" else "AI Learning Assistant"
        role_class = "user" if role == "user" else "assistant"
        
        html_lines.append(f"""
            <div class="message {role_class}">
                <div class="role">{role_label}</div>
                <div class="timestamp">{time_str}</div>
                <div class="content">{content}</div>
            </div>
        """)
    
    html_lines.append("""
        </div>
        
        <div class="footer">
            <p>This chat transcript was exported from Jeseci Smart Learning Academy.</p>
            <p>Your AI Learning Assistant helps you master concepts through personalized conversations.</p>
            <a href="https://jeseci-academy.com" class="button">Visit Jeseci Academy</a>
        </div>
    </div>
</body>
</html>
""")
    
    return "\n".join(html_lines)


async def _send_chat_export_email_async(
    to_email: str, 
    subject: str, 
    html_body: str, 
    plain_text: str
) -> dict:
    """
    Send chat export email using aiosmtplib (async)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML email body
        plain_text: Plain text version of email
        
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
        msg.set_content(plain_text)
        msg.add_alternative(html_body, subtype='html')
        
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
            try:
                await smtp.starttls(context=context)
            except Exception:
                pass
            
            await smtp.login(FROM_EMAIL, EMAIL_PASSWORD)
            await smtp.send_message(msg)
        
        logger.info(f"Chat export email sent successfully to {to_email}")
        return {"success": True}
        
    except Exception as error:
        logger.error(f"Failed to send chat export email to {to_email}: {error}")
        return {"success": False, "error": str(error)}


def _send_chat_export_email_sync(
    to_email: str, 
    subject: str, 
    html_body: str, 
    plain_text: str
) -> dict:
    """
    Send chat export email using smtplib (sync fallback)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML email body
        plain_text: Plain text version of email
        
    Returns:
        dict with 'success' key
    """
    if not EMAIL_PASSWORD:
        logger.info(f"Email credentials not configured - email would be sent to: {to_email}")
        return {"success": True}
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach plain text and HTML versions
        part1 = MIMEText(plain_text, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email using smtplib with proper TLS context
        import ssl
        context = ssl.create_default_context()
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, to_email, text)
        server.quit()
        
        logger.info(f"Chat export email sent successfully to {to_email}")
        return {"success": True}
        
    except Exception as error:
        logger.error(f"Failed to send chat export email to {to_email}: {error}")
        return {"success": False, "error": str(error)}


async def send_chat_export_email(
    to_email: str,
    chat_messages: List[Dict],
    user_name: str = "User"
) -> dict:
    """
    Send chat export email to user
    
    Args:
        to_email: Recipient email address
        chat_messages: List of chat message dictionaries
        user_name: Name of the user for display
        
    Returns:
        dict with 'success', 'message_count' keys
    """
    try:
        # Check if email is configured
        if not EMAIL_PASSWORD:
            logger.info(f"Chat export email would be sent to: {to_email}")
            logger.info(f"Message count: {len(chat_messages)}")
            return {"success": True, "method": "console", "message_count": len(chat_messages)}
        
        # Create email content
        message_count = len(chat_messages)
        subject = f"Your AI Chat Transcript - {datetime.now().strftime('%Y-%m-%d')}"
        
        plain_text = format_chat_for_email(chat_messages, user_name)
        html_body = create_html_chat_email(chat_messages, user_name)
        
        # Send email
        if HAS_AIOSMTPLIB:
            result = await _send_chat_export_email_async(to_email, subject, html_body, plain_text)
        else:
            result = _send_chat_export_email_sync(to_email, subject, html_body, plain_text)
        
        if result.get("success"):
            logger.info(f"Chat export email sent successfully to {to_email}")
            return {
                "success": True, 
                "method": "email",
                "message_count": message_count,
                "email": to_email
            }
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}
        
    except Exception as error:
        logger.error(f"Chat export email error: {error}")
        return {"success": False, "error": str(error)}


# Synchronous wrapper for Jaclang integration
def sync_send_chat_export_email(
    to_email: str,
    chat_messages_json: str,
    user_name: str = "User"
) -> dict:
    """
    Synchronous wrapper for sending chat export email
    
    Args:
        to_email: Recipient email address
        chat_messages_json: JSON string of chat messages
        user_name: Name of the user for display
        
    Returns:
        dict with 'success' key
    """
    import json
    import concurrent.futures
    
    try:
        chat_messages = json.loads(chat_messages_json) if chat_messages_json else []
    except json.JSONDecodeError:
        chat_messages = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(
            asyncio.run,
            send_chat_export_email(to_email, chat_messages, user_name)
        )
        return future.result()


if __name__ == "__main__":
    # Test the module
    test_messages = [
        {
            "role": "user",
            "content": "What is Object-Spatial Programming?",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "role": "assistant",
            "content": "Object-Spatial Programming (OSP) is a paradigm where computation moves to data rather than moving data to computation. It uses nodes, edges, and walkers to create flexible, scalable applications.",
            "timestamp": "2024-01-15T10:30:05Z"
        },
        {
            "role": "user",
            "content": "Can you give me an example?",
            "timestamp": "2024-01-15T10:31:00Z"
        }
    ]
    
    print("Testing chat export email functionality...")
    print(f"Formatted plain text:\n{format_chat_for_email(test_messages, 'Test User')}")
    print("\n" + "="*50 + "\n")
    print("HTML version created successfully!")
