#!/bin/bash
# Jeseci Smart Learning Academy - Git Commit and Push Script
# Execute this script in your local repository to commit and push changes

echo "=== Jeseci Smart Learning Academy - Git Operations ==="
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this script from your Jeseci Smart Learning Academy directory"
    exit 1
fi

echo "📋 Step 1: Configure git user"
git config user.name "OumaCavin"
git config user.email "cavin.otieno012@gmail.com"
echo "✅ Git user configured: OumaCavin (cavin.otieno012@gmail.com)"
echo ""

echo "📋 Step 2: Ensure main branch"
git branch -M main
echo "✅ Branch set to main"
echo ""

echo "📋 Step 3: Add remote origin (if not already added)"
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
    echo "✅ Remote origin added"
else
    echo "✅ Remote origin already configured"
fi
echo ""

echo "📋 Step 4: Stage all changes"
git add .
echo "✅ All changes staged"
echo ""

echo "📋 Step 5: Commit with descriptive message"
COMMIT_MSG="feat(cleanup): standardize codebase and update configurations

- Replace Chinese comments with English in browser files
- Update environment configuration with production-ready settings
- Standardize documentation with proper author attribution
- Ensure no MiniMax references in active code files
- Configure OpenAI, Gemini, and Google API integrations
- Update contact form with production email settings
- Maintain clean architecture and professional code standards"

git commit -m "$COMMIT_MSG"
if [ $? -eq 0 ]; then
    echo "✅ Changes committed successfully"
else
    echo "❌ Commit failed"
    exit 1
fi
echo ""

echo "📋 Step 6: Push to remote repository"
echo "🔐 Note: You may be prompted for your GitHub credentials"
echo "Use your personal access token when prompted for password"
echo ""
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS: Repository pushed to GitHub!"
    echo "📍 Repository: https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy"
    echo "🌐 Live Demo: https://4bi3nkqc7nxa.space.minimax.io"
else
    echo ""
    echo "❌ Push failed. Please check your credentials and try again."
    echo "💡 Make sure you have a valid GitHub personal access token"
    exit 1
fi

echo ""
echo "=== All Operations Completed ==="
echo "✅ Repository ready for development!"
echo "✅ Codebase standardized and production-ready"
echo "✅ All configurations updated and aligned"