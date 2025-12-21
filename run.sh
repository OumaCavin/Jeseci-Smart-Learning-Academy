#!/bin/bash

# Jeseci Smart Learning Academy - Run Script
# This script starts the JAC application server with React JSX frontend

echo "🎓 Starting Jeseci Smart Learning Academy..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if the compiled JAC file exists
if [ ! -f "app.jir" ]; then
    echo "📦 Compiling JAC application with React JSX frontend..."
    jac build app.jac
    if [ $? -ne 0 ]; then
        echo "❌ Failed to compile JAC application."
        exit 1
    fi
fi

echo "🚀 Starting JAC server..."
echo "📍 Access the application at: http://localhost:8000"
echo "🌐 React JSX frontend: http://localhost:8000/page/app"
echo "💡 HTML API backup: POST /function/serve_html"
echo ""
echo "Available API endpoints:"
echo "  POST /walker/welcome"
echo "  POST /walker/health_check"
echo "  POST /walker/concepts"
echo "  POST /walker/user_progress"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the JAC server
jac serve app.jir