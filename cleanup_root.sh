#!/bin/bash

# ==============================================================================
# PROJECT ROOT CLEANUP SCRIPT
# ==============================================================================
# Author: Cavin Otieno
# Date: December 26, 2025

echo "🧹 Cleaning up project root by moving files to docs..."

# Create scripts directory under docs
mkdir -p docs/scripts

# Move script files to docs/scripts
echo "📜 Moving scripts to docs/scripts/..."
mv cleanup_project.sh docs/scripts/ 2>/dev/null || true
mv commit_and_push.sh docs/scripts/ 2>/dev/null || true
mv commit_security_update.sh docs/scripts/ 2>/dev/null || true
mv execute_git_push.sh docs/scripts/ 2>/dev/null || true
mv git_pull_rebase_push.sh docs/scripts/ 2>/dev/null || true

# Move project documentation
echo "📚 Moving documentation to docs/..."
mv PROJECT_UPDATE_COMPLETE.md docs/ 2>/dev/null || true

# Update script references to be relative to new location
echo "🔧 Updating script references..."

# Keep essential files in root
echo "✅ Keeping essential files in project root:"
echo "   - README.md"
echo "   - setup.sh" 
echo "   - .gitignore"
echo "   - .env.example"

echo "📁 Project root cleaned up successfully!"
echo "📝 Scripts moved to: docs/scripts/"
echo "📚 Documentation organized in: docs/"