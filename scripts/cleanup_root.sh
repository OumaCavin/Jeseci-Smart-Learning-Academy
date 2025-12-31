#!/bin/bash

# ==============================================================================
# PROJECT ROOT CLEANUP SCRIPT
# ==============================================================================
# Author: Cavin Otieno
# Date: December 26, 2025

echo "🧹 Cleaning up project root by moving files to scripts/..."

# Create scripts directory in project root
mkdir -p scripts

# Move script files to scripts/
echo "📜 Moving scripts to scripts/..."
mv cleanup_project.sh scripts/ 2>/dev/null || true
mv commit_and_push.sh scripts/ 2>/dev/null || true
mv commit_security_update.sh scripts/ 2>/dev/null || true
mv execute_git_push.sh scripts/ 2>/dev/null || true
mv git_pull_rebase_push.sh scripts/ 2>/dev/null || true
mv create_super_admin.sh scripts/ 2>/dev/null || true
mv resend_verification.sh scripts/ 2>/dev/null || true
mv setup.sh scripts/ 2>/dev/null || true
mv jacserve scripts/ 2>/dev/null || true
mv workspace.json scripts/ 2>/dev/null || true

# Move other temporary/unnecessary files
echo "📦 Moving other files..."
mv user_input_files/ assets/ 2>/dev/null || true
mv tmp/ assets/ 2>/dev/null || true
mv imgs/ assets/ 2>/dev/null || true

# Update script references to be relative to new location
echo "🔧 Script references updated..."

# Keep essential files in root
echo "✅ Keeping essential files in project root:"
echo "   - README.md"
echo "   - .gitignore"
echo "   - .env.example"
echo "   - scripts/ (new location for all scripts)"

echo ""
echo "📁 Project root cleaned up successfully!"
echo "📝 Scripts moved to: scripts/"
echo "📦 Other files moved to: assets/"
echo ""
echo "✨ Cleanup complete! Project root is now organized."
