# Email notification module for Jaclang backend
# This module handles all email-related functionality

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_contact_notification(contact_data):
    """Send email notification to admin about new contact form submission"""
    try:
        # Get email configuration from environment
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        admin_email = os.getenv("ADMIN_EMAIL", "admin@jeseci.com")
        from_email = os.getenv("FROM_EMAIL", "noreply@jeseci.com")
        email_password = os.getenv("EMAIL_PASSWORD", "")

        if not email_password:
            print("Email password not configured - using console output")
            print("NEW CONTACT MESSAGE:")
            print("Name:", contact_data['name'])
            print("Email:", contact_data['email'])
            print("Subject:", contact_data['subject'])
            print("Message:", contact_data['message'])
            return {"success": True, "method": "console"}

        # Create email content
        subject = "New Contact Form Submission: " + contact_data['subject']

        # Build body as simple single-line string
        body = ("New contact form submission received. Message ID: " + contact_data['message_id'] +
                ". Name: " + contact_data['name'] + ". Email: " + contact_data['email'] +
                ". Phone: " + contact_data['phone'] + ". Reason: " + contact_data['contact_reason'] +
                ". Subject: " + contact_data['subject'] + ". Message: " + contact_data['message'] +
                ". Timestamp: " + contact_data['timestamp'] + ". Please respond within 24 hours.")

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = admin_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, email_password)
        text = msg.as_string()
        server.sendmail(from_email, admin_email, text)
        server.quit()

        return {"success": True, "method": "email"}

    except Exception as error:
        print("Email notification error:", error)
        return {"success": False, "error": str(error)}


def send_confirmation_email(contact_data):
    """Send confirmation email to the user who submitted the contact form"""
    try:
        # Get email configuration
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        from_email = os.getenv("FROM_EMAIL", "noreply@jeseci.com")
        email_password = os.getenv("EMAIL_PASSWORD", "")

        if not email_password:
            print("Confirmation email password not configured")
            return {"success": False, "method": "console"}

        # Create confirmation email content
        subject = "Thank you for contacting Jeseci Smart Learning Academy"

        # Build body as simple single-line string
        body = ("Dear " + contact_data['name'] + ". Thank you for contacting Jeseci Smart Learning Academy! " +
                "We have received your message regarding: " + contact_data['subject'] + ". " +
                "Message ID: " + contact_data['message_id'] + ". Submitted: " + contact_data['timestamp'] + ". " +
                "Our team will review your inquiry and respond within 24 hours during business days. " +
                "Best regards, The Jeseci Smart Learning Academy Team. " +
                "This is an automated confirmation. Please do not reply to this email.")

        # Create and send email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = contact_data['email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, email_password)
        text = msg.as_string()
        server.sendmail(from_email, contact_data['email'], text)
        server.quit()

        return {"success": True, "method": "email"}

    except Exception as error:
        print("Confirmation email error:", error)
        return {"success": False, "error": str(error)}
