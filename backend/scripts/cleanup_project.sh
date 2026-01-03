#!/bin/bash

# ==============================================================================
# PROJECT CLEANUP SCRIPT - Jeseci Smart Learning Academy
# ==============================================================================
# Removes unnecessary files from git tracking and cleans project structure
# Author: Cavin Otieno
# Date: December 26, 2025

echo "🧹 Cleaning up Jeseci Smart Learning Academy project..."

# Remove files that shouldn't be tracked
echo "📁 Removing unnecessary files from git tracking..."

# Remove workspace and temporary files
git rm --cached workspace.json 2>/dev/null || true
git rm -r --cached user_input_files/ 2>/dev/null || true
git rm -r --cached browser/ 2>/dev/null || true
git rm -r --cached tmp/ 2>/dev/null || true
git rm -r --cached venv/ 2>/dev/null || true

# Remove build artifacts
git rm -r --cached frontend/dist/ 2>/dev/null || true
git rm -r --cached backend/dist/ 2>/dev/null || true

# Remove JAC compiled files
find . -name "*.jir" -type f | xargs git rm --cached 2>/dev/null || true

# Remove any log files that might be tracked
find . -name "*.log" -type f | xargs git rm --cached 2>/dev/null || true

# Remove any .env files (keep .env.example)
find . -name ".env" -not -name ".env.example" -type f | xargs git rm --cached 2>/dev/null || true

echo "✅ Cleanup completed!"
echo "📝 Files removed from git tracking (if they existed):"
echo "   - workspace.json"
echo "   - user_input_files/"
echo "   - browser/"
echo "   - tmp/"
echo "   - venv/"
echo "   - frontend/dist/"
echo "   - backend/dist/"
echo "   - *.jir (JAC compiled files)"
echo "   - *.log (log files)"
echo "   - .env files (excluding .env.example)"

echo ""
echo "🎯 Next steps:"
echo "   1. Review git status: git status"
echo "   2. Add updated files: git add ."
echo "   3. Commit changes: git commit -m 'docs: update README and clean project structure'"
echo "   4. Push to remote: git push"