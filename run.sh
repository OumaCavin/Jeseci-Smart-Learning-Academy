#!/bin/bash

# Jeseci Smart Learning Academy - Run Script
# This script starts the JAC application server with pure Jaclang frontend

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using Pure Jaclang 0.9.3 Architecture"

# Function to install jac-client
install_jaclang() {
    echo "🐍 Installing jaclang and jac-client (Python packages)..."
    
    # Check if requirements file exists
    REQUIREMENTS_FILE="docs/pure-jac/requirements_pure_jac.txt"
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        echo "⚠️ Requirements file not found: $REQUIREMENTS_FILE"
        echo "📦 Installing core jaclang packages manually..."
        # Fallback to manual installation
        if command -v uv &> /dev/null; then
            uv pip install jaclang>=0.9.3 jac-client>=0.2.3
        elif command -v pip &> /dev/null; then
            timeout 60 pip install jaclang>=0.9.3 jac-client>=0.2.3 --timeout 30 --retries 3
        elif command -v pip3 &> /dev/null; then
            timeout 60 pip3 install jaclang>=0.9.3 jac-client>=0.2.3 --timeout 30 --retries 3
        fi
        return $?
    else
        echo "✅ Found requirements file: $REQUIREMENTS_FILE"
        
        # Function to install from requirements file with timeout
        install_from_requirements() {
            local cmd="$1"
            local req_file="$2"
            echo "📦 Installing from requirements file with timeout..."
            
            # Use timeout command to limit execution time
            if timeout 60 $cmd install -r "$req_file"; then
                return 0
            else
                local exit_code=$?
                if [ $exit_code -eq 124 ]; then
                    echo "⚠️ Installation timed out after 60 seconds"
                else
                    echo "⚠️ Installation failed, trying individual packages..."
                fi
                # Fallback to individual package installation
                $cmd install jaclang>=0.9.3 jac-client>=0.2.3
            fi
        }
        
        local success=false
        
        if command -v uv &> /dev/null; then
            echo "✅ Using uv package manager"
            if install_from_requirements "uv pip" "$REQUIREMENTS_FILE"; then
                success=true
            fi
        elif command -v pip &> /dev/null; then
            echo "✅ Using pip package manager"
            if install_from_requirements "pip" "$REQUIREMENTS_FILE"; then
                success=true
            fi
        elif command -v pip3 &> /dev/null; then
            echo "✅ Using pip3 package manager"
            if install_from_requirements "pip3" "$REQUIREMENTS_FILE"; then
                success=true
            fi
        fi
        
        if [ "$success" = false ]; then
            echo "❌ Failed to install jaclang packages due to network issues"
            echo "💡 Possible solutions:"
            echo "   1. Check your internet connection"
            echo "   2. Try using a different PyPI mirror"
            echo "   3. Install manually: pip install jaclang jac-client"
            echo "   4. Run: bash ./setup.sh (which has better error handling)"
            return 1
        fi
    fi
    
    return 0
}

# Check if jac command is available (most important)
if ! command -v jac &> /dev/null; then
    echo "⚠️ jac command not found"
    
    # Check if jaclang is installed in Python
    if ! python3 -c "import jaclang" 2>/dev/null; then
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
            if ! install_jaclang; then
                exit 1
            fi
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
                if ! command -v jac &> /dev/null; then
                    install_jaclang
                fi
            else
                echo "❌ jaclang is required. Please install it manually or run ./setup.sh"
                echo "💡 Manual installation: pip install jaclang jac-client"
                exit 1
            fi
        fi
    else
        # jaclang is installed but jac command not found - add to PATH
        echo "🔧 jaclang found but jac command not in PATH"
        JAC_PATH=$(python3 -c "import jaclang; import os; print(os.path.dirname(jaclang.__file__))" 2>/dev/null)
        if [ -n "$JAC_PATH" ] && [ -d "$JAC_PATH/bin" ]; then
            export PATH="$JAC_PATH/bin:$PATH"
            echo "✅ Added jaclang bin to PATH"
        fi
    fi
fi

# Final check for jac command
if ! command -v jac &> /dev/null; then
    echo "❌ jac command still not found after installation attempts"
    echo "💡 Please run: bash ./setup.sh to properly install jaclang"
    exit 1
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

# Final check for jac command before serving
if ! command -v jac &> /dev/null; then
    echo "❌ jac command not found - installation may have failed"
    echo "💡 Please run: bash ./setup.sh to properly install jaclang"
    echo "💡 Or try manually: pip install jaclang jac-client"
    exit 1
fi

# Start the JAC server
jac serve app.jir