#!/bin/bash
# Jeseci Smart Learning Academy - Resend Verification Email Script
# This script sends a new verification email to a user

# Set PYTHONPATH to enable absolute imports
export PYTHONPATH=.

# Check if .env file exists (DO NOT manually export - let Python handle it)
if [ ! -f "backend/config/.env" ]; then
    echo "✗ Error: backend/config/.env file not found!"
    echo "Please make sure the .env file exists."
    exit 1
fi

echo "✓ Configuration file found: backend/config/.env"
echo "  (Environment variables will be loaded by Python)"
echo ""

# Interactive input for email
read -p "Enter the email address: " EMAIL
while [ -z "$EMAIL" ]; do
    echo "Email address cannot be empty!"
    read -p "Enter the email address: " EMAIL
done

echo ""
echo "=================================================="
echo "   RESEND VERIFICATION EMAIL"
echo "=================================================="
echo "   Email: $EMAIL"
echo "=================================================="
echo ""

read -p "Send verification email? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Sending verification email..."
echo "  Email to send: $EMAIL"
echo "  URL: http://localhost:8000/auth/resend-verification"
echo ""

# Run the resend verification script
# Python will load .env file directly from the correct path
python -c "
import os
import sys

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'backend', 'config', '.env'))

import requests

email = '''$EMAIL'''
print(f'Python received email: [{email}]')
url = 'http://localhost:8000/auth/resend-verification'

try:
    payload = {'email': email}
    print(f'Request payload: {payload}')
    response = requests.post(url, json=payload)
    print(f'Response status: {response.status_code}')
    print(f'Response body: {response.text}')
    data = response.json()
    
    if response.status_code == 200:
        print('✅ ' + data.get('message', 'Verification email sent successfully!'))
        if data.get('method') == 'console':
            print('   Note: Emails are being printed to console (SMTP not configured)')
        else:
            print('   Check your inbox at: ' + email)
    else:
        error = data.get('error', 'Unknown error')
        code = data.get('code', '')
        print('❌ Failed: ' + error)
        if code == 'NOT_FOUND':
            print('   The email address is not registered.')
        elif code == 'ALREADY_VERIFIED':
            print('   This email is already verified. You can log in.')
        elif code == 'MISSING_EMAIL':
            print('   Please provide an email address.')
        
except requests.exceptions.ConnectionError:
    print('❌ Error: Cannot connect to backend server.')
    print('   Make sure the server is running: bash ./jacserve')
except Exception as e:
    print('❌ Error: ' + str(e))
"

echo ""
echo "Done."
