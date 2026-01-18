import smtplib
import os

# Hardcode your credentials here just for this test to rule out .env parsing issues
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "cavin.otieno012@gmail.com"
SMTP_PASSWORD = "jspbrldxspmhusrb"  # Your 16-char App Password

try:
    print(f"Connecting to {SMTP_HOST}:{SMTP_PORT}...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    
    print(f"Attempting login as {SMTP_USER}...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("✅ SUCCESS! Credentials are valid.")
    server.quit()
except Exception as e:
    print(f"❌ FAILURE: {e}")
