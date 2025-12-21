#!/bin/bash
# CORRECT Jaclang Application Runner
# Uses automatic Vite configuration from jac create_jac_app

set -e

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using CORRECT Jaclang 0.9.3 setup with automatic Vite configuration"

# Check Node.js dependencies
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build application
echo "🔨 Building JAC application..."
jac build ./app.jac

BUILD_EXIT_CODE=$?
if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "❌ FAILED TO COMPILE JAC APPLICATION"
    exit 1
fi

echo "✅ Compilation successful! Starting server..."
echo ""
echo "📍 Access the application at: http://localhost:8000"
echo "🌐 Frontend: http://localhost:8000/page/app"
echo "💡 Backend APIs: /walker/health_check, /walker/init, etc."
echo ""
echo "Press Ctrl+C to stop the server"

# Start server
jac serve app.jir