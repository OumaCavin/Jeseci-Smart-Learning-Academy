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

# Always rebuild the JAC application to ensure fresh compilation
echo "📦 Compiling JAC application with React JSX frontend..."
echo "⏳ This ensures all syntax errors are caught before starting..."
echo ""

jac build ./app.jac
BUILD_EXIT_CODE=$?

echo ""

if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "❌ FAILED TO COMPILE JAC APPLICATION"
    echo "🔧 Please fix the syntax errors above and try again"
    echo ""
    echo "💡 Quick fixes:"
    echo "   - Check for missing colons (:) in has declarations"
    echo "   - Verify walker syntax with 'with entry' blocks"
    echo "   - Ensure proper indentation and brackets"
    echo ""
    exit 1
fi

echo "✅ Compilation successful! Starting server..."
echo ""

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