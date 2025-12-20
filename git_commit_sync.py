#!/usr/bin/env python3
"""
Git commit and push script for sync_neo4j.py
This script commits and pushes the Neo4j sync script to GitHub
"""

import subprocess
import sys
import os

def run_git_command(cmd, description):
    """Run a git command and handle errors"""
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def main():
    """Main function to commit and push sync_neo4j.py"""
    print("🚀 Starting git operations for sync_neo4j.py...")
    
    # Change to workspace directory
    os.chdir('/workspace')
    
    # Check if sync_neo4j.py exists
    if not os.path.exists('sync_neo4j.py'):
        print("❌ sync_neo4j.py not found!")
        return False
    
    # Run git operations
    commands = [
        ("git add sync_neo4j.py", "Adding sync_neo4j.py to git"),
        ("git commit -m 'Add sync_neo4j.py script for Neo4j graph database synchronization'", "Committing sync script"),
        ("git push", "Pushing to GitHub")
    ]
    
    for cmd, description in commands:
        if not run_git_command(cmd, description):
            return False
    
    print("🎉 All git operations completed successfully!")
    print("📋 Next steps:")
    print("   1. Pull latest changes on your local machine: git pull")
    print("   2. Run the sync script: python sync_neo4j.py")
    print("   3. Your Neo4j database will be populated with JAC concepts")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)