#!/bin/bash
# Git Setup Script for Jeseci Smart Learning Academy
# Author: Cavin Otieno
# Date: December 13, 2025

echo "🚀 Setting up Git repository..."

# Navigate to project directory
cd /workspace/jeseci-smart-learning-academy

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📂 Initializing Git repository..."
    git init
fi

# Configure Git user
echo "👤 Setting Git user configuration..."
git config user.name "OumaCavin"
git config user.email "cavin@example.com"

# Set main branch
echo "🌿 Setting main branch..."
git branch -M main

# Add remote origin
echo "🔗 Adding remote origin..."
git remote remove origin 2>/dev/null || true
git remote add origin https://[YOUR_TOKEN]@github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git

echo "✅ Git setup complete!"
echo "📝 Next steps:"
echo "   1. git add ."
echo "   2. git commit -m 'feat: initial project setup with JAC framework'"
echo "   3. git push -u origin main"