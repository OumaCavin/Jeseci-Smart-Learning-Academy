#!/bin/bash

# Jeseci Smart Learning Academy - Run Script
# This script starts the JAC application server with pure Jaclang frontend

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using Pure Jaclang 0.9.3 Architecture"

# Check if jac-client is installed
if ! python -c "import jac_client" 2>/dev/null; then
    echo "🐍 Installing jac-client (Python package)..."
    uv pip install jac-client
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Always rebuild the JAC application to ensure fresh compilation
echo "📦 Compiling JAC application with pure Jaclang frontend..."
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
echo "🌐 Pure Jaclang Frontend: http://localhost:8000/page/app"
echo "💡 Backend APIs: POST /walker/* endpoints"
echo ""
echo "Available API endpoints:"
echo "  POST /walker/health_check"
echo "  POST /walker/init"
echo "  POST /walker/concepts"
echo "  POST /walker/user_progress"
echo ""

echo "Architecture:"
echo "  ✅ Pure Jaclang 0.9.3"
echo "  ✅ No external React dependencies"
echo "  ✅ Native JSX compilation"
echo "  ✅ Auto-managed frontend dependencies"
echo ""

echo "Press Ctrl+C to stop the server"
echo ""

# Start the JAC server
jac serve app.jir