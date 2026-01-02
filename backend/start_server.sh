#!/bin/bash

# Jeseci Smart Learning Academy - Custom Backend Server Startup Script
# This script starts the Jaclang server with CORS fix for PUT method support

echo "🚀 Starting Jeseci Smart Learning Academy Backend Server..."
echo "📋 Using custom server with CORS fix for PUT method support"

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "../.venv" ]; then
    echo "✅ Found virtual environment"
else
    echo "⚠️ Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

# Activate virtual environment
source ../.venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "🐍 Python version: $(python3 --version)"
echo ""

# Start the custom server with CORS fix
echo "🌐 Starting custom Jaclang server on port 8000..."
echo "🔧 CORS methods: GET, POST, PUT, DELETE, OPTIONS"
echo ""

# Use the custom server script instead of direct jac serve
python3 custom_jac_server.py

echo "🛑 Server stopped"
