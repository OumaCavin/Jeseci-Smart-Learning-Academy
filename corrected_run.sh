#!/bin/bash
# CORRECTED Jaclang Application Runner
# Uses correct setup (NO fake npm packages)

set -e

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using CORRECTED Jaclang setup (no fake npm dependencies)"

# Check for required tools
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.12+."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm (comes with Node.js)."
    exit 1
fi

# Check if jac-client is installed
if ! python -c "import jac_client" 2>/dev/null; then
    echo "🐍 Installing jac-client (Python package)..."
    uv pip install jac-client
fi

# Install minimal Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing minimal Node.js dependencies..."
    npm install
fi

# Build application
echo "🔨 Building JAC application..."
jac build ./app.jac

BUILD_EXIT_CODE=$?
if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "❌ FAILED TO COMPILE JAC APPLICATION"
    echo "📋 This might be due to syntax errors in app.jac"
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