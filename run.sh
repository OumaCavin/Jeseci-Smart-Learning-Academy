#!/bin/bash

# Jeseci Smart Learning Academy - Run Script
# This script starts the JAC application server with pure Jaclang frontend

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using Pure Jaclang 0.9.3 Architecture"

# Function to install jac-client
install_jac_client() {
    echo "🐍 Installing jac-client (Python package)..."
    if command -v uv &> /dev/null; then
        uv pip install jac-client
    elif command -v pip &> /dev/null; then
        pip install jac-client
    elif command -v pip3 &> /dev/null; then
        pip3 install jac-client
    else
        echo "❌ No package manager found (uv, pip, or pip3)"
        echo "💡 Please run ./setup.sh to install dependencies properly"
        exit 1
    fi
}

# Check if jac-client is installed (try system Python first)
if ! python3 -c "import jac_client" 2>/dev/null; then
    # Try with current environment
    if ! python -c "import jac_client" 2>/dev/null; then
        # Check if virtual environment exists
        if [ -d "venv" ] && [ -f "venv/bin/python3" ]; then
            echo "🔧 Activating virtual environment..."
            source venv/bin/activate
            if [ $? -ne 0 ]; then
                echo "❌ Failed to activate virtual environment"
                echo "💡 Please run ./setup.sh to recreate the environment"
                exit 1
            fi
            # Try installing in virtual environment
            install_jac_client
        else
            # No virtual environment, try installing system-wide or ask to setup
            echo "⚠️ No virtual environment found"
            echo "💡 Do you want to run setup.sh to create one? (y/n)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                bash ./setup.sh
                if [ $? -ne 0 ]; then
                    echo "❌ Setup failed. Please check the errors above."
                    exit 1
                fi
                # Try again after setup
                if ! python3 -c "import jac_client" 2>/dev/null; then
                    install_jac_client
                fi
            else
                echo "❌ jac-client is required. Please install it manually or run ./setup.sh"
                exit 1
            fi
        fi
    fi
fi

# Check if virtual environment exists and is valid
if [ -d "venv" ]; then
    if [ -f "venv/bin/python3" ]; then
        # Test if virtual environment works
        if source venv/bin/activate && python3 --version &> /dev/null; then
            echo "🔧 Activating virtual environment..."
            source venv/bin/activate
        else
            echo "⚠️ Virtual environment is broken"
            echo "💡 Please run ./setup.sh to recreate it"
            exit 1
        fi
    else
        echo "⚠️ Virtual environment is incomplete"
        echo "💡 Please run ./setup.sh to recreate it"
        exit 1
    fi
else
    echo "⚠️ No virtual environment found"
    echo "💡 Please run ./setup.sh to create one"
    exit 1
fi

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