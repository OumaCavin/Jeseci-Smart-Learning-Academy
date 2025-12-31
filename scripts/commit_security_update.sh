#!/bin/bash

# ==============================================================================
# SECURITY UPDATE COMMIT SCRIPT
# ==============================================================================
# Author: Cavin Otieno  
# Date: December 26, 2025

echo "🔐 Updating session timeout for enhanced security..."

# Configure git user for this repository
git config user.name "OumaCavin"
git config user.email "cavin@example.com"

# Stage security-related changes
echo "📝 Staging security updates..."
git add backend/user_auth.py
git add frontend/src/contexts/AuthContext.tsx
git add .env.example
git add README.md

# Show what will be committed
echo "📋 Files being updated:"
git diff --cached --name-status

# Commit the security updates
git commit -m "security: reduce session timeout to 5 minutes for enhanced security

- Change JWT token expiration from 30 minutes to 5 minutes
- Update backend JWT_ACCESS_TOKEN_EXPIRE_MINUTES default to 5 minutes  
- Fix .env.example to use correct JWT environment variable names
- Update README.md to document security settings and session timeout
- Add security-focused logging in frontend auth context
- Improve session management for better security posture

This reduces the window of exposure if a session token is compromised
while maintaining good user experience for active users."

echo "✅ Security update committed!"

# Push to remote
echo "🚀 Pushing security updates to remote..."
git push origin main

echo "🔐 Session timeout updated to 5 minutes for enhanced security!"