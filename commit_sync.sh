#!/bin/bash

# Kill any running FastAPI processes
pkill -f "uvicorn" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Add sync_neo4j.py to git
git add sync_neo4j.py

# Commit the changes
git commit -m "Add sync_neo4j.py script for Neo4j graph database synchronization"

# Push to GitHub
git push

echo "Sync script committed and pushed successfully!"