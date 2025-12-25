#!/bin/bash

# Execute git operations with professional commit messages
# Following the style of commit 9e6e8e2: fix: Add analytics data validation and optional chaining

# Configure git
git config user.name "OumaCavin"
git config user.email "cavin@example.com"

# Ensure we're on main branch  
git branch -M main

# Pull latest changes with rebase
echo "Pulling latest changes with rebase..."
git pull --rebase origin main

# Clean project
echo "Cleaning project structure..."
./cleanup_project.sh 2>/dev/null || true

# Stage changes
echo "Staging changes..."
git add .

# Create commit with professional message following 9e6e8e2 style
echo "Creating professional commit..."
git commit -m "docs: update README and add comprehensive defensive programming documentation

- Update README.md to reflect current React + JAC hybrid architecture
- Add comprehensive frontend defensive patterns implementation guide  
- Create architectural diagrams showing error handling flows
- Document zero-crash implementation with code examples
- Add .env.example template with correct JWT configuration variables
- Update project structure documentation to match actual codebase
- Replace Matrix Agent references with proper Cavin Otieno authorship
- Add detailed API documentation and developer setup instructions"

# Create security update commit
git add backend/user_auth.py frontend/src/contexts/AuthContext.tsx
git commit -m "security: reduce session timeout to 5 minutes for enhanced security

- Change JWT token expiration from 30 minutes to 5 minutes
- Update backend JWT_ACCESS_TOKEN_EXPIRE_MINUTES default value
- Add security-focused session logging in frontend auth context
- Fix JWT environment variable naming in .env.example
- Improve session management for better security posture"

# Push all commits to remote
echo "Pushing to remote repository..."
git push origin main

echo "✅ Successfully pushed all changes with professional commit messages!"
echo "Recent commits:"
git log --oneline -3