#!/bin/bash

# Jeseci Smart Learning Academy - Setup Script
# This script sets up the development environment

echo "🎓 Setting up Jeseci Smart Learning Academy..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "💡 Please install Python 3.12 or later from: https://python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "🐍 Found Python: $PYTHON_VERSION"

# Check if uv is available (preferred)
if command -v uv &> /dev/null; then
    echo "✅ Using uv package manager"
    UV_CMD="uv"
elif command -v pip &> /dev/null; then
    echo "✅ Using pip package manager"
    UV_CMD="pip"
elif command -v pip3 &> /dev/null; then
    echo "✅ Using pip3 package manager"
    UV_CMD="pip3"
else
    echo "❌ No package manager found (uv, pip, or pip3)"
    echo "💡 Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or install pip with your Python installation"
    exit 1
fi

# Check if virtual environment exists and is valid
VENV_VALID=false
if [ -d "venv" ]; then
    if [ -f "venv/bin/python3" ] || [ -f "venv/bin/python" ]; then
        echo "📦 Found existing virtual environment"
        # Test if virtual environment works
        if source venv/bin/activate && python3 --version &> /dev/null; then
            VENV_VALID=true
            echo "✅ Virtual environment is valid"
        else
            echo "⚠️ Virtual environment is broken, recreating..."
            rm -rf venv
        fi
    else
        echo "⚠️ Virtual environment is incomplete, recreating..."
        rm -rf venv
    fi
fi

# Create virtual environment if needed
if [ "$VENV_VALID" = false ]; then
    echo "📦 Creating new virtual environment..."
    python3 -m venv venv
    
    if [ ! $? -eq 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "💡 Try installing python3-venv: sudo apt install python3-venv"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Install dependencies using the available package manager with better error handling
echo "📚 Installing dependencies..."

# Define standard PyPI index to avoid mirror issues
PYPI_INDEX="--index-url https://pypi.org/simple"

# Function to install from requirements file with timeout
install_from_requirements() {
    local cmd="$1"
    local req_file="$2"
    echo "📦 Installing from requirements file with timeout..."
    
    # Use timeout command to limit execution time
    if timeout 120 $cmd install -r "$req_file" $PYPI_INDEX; then
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo "⚠️ Installation timed out after 120 seconds"
        else
            echo "⚠️ Installation failed, trying individual packages..."
        fi
        # Fallback to individual package installation
        $cmd install jaclang>=0.9.3 jac-client>=0.2.3 $PYPI_INDEX
    fi
}

install_success=false

REQUIREMENTS_FILE="docs/pure-jac/requirements_pure_jac.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "✅ Found requirements file: $REQUIREMENTS_FILE"
    if [ "$UV_CMD" = "uv" ]; then
        if install_from_requirements "uv pip" "$REQUIREMENTS_FILE"; then
            install_success=true
        fi
    else
        if install_from_requirements "$UV_CMD" "$REQUIREMENTS_FILE"; then
            install_success=true
        fi
    fi
else
    echo "⚠️ Requirements file not found. Installing manually..."
    if [ "$UV_CMD" = "uv" ]; then
        if uv pip install jaclang>=0.9.3 jac-client>=0.2.3 $PYPI_INDEX; then
            install_success=true
        fi
    else
        if $UV_CMD install jaclang>=0.9.3 jac-client>=0.2.3 $PYPI_INDEX; then
            install_success=true
        fi
    fi
fi

if [ "$install_success" = false ]; then
    echo "❌ Failed to install jaclang packages"
    echo "💡 This might be due to network issues or firewall restrictions"
    echo "💡 Please try:"
    echo "   1. Check your internet connection"
    echo "   2. Install manually: uv pip install jaclang jac-client --index-url https://pypi.org/simple"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 STARTING THE APPLICATION - IMPORTANT INSTRUCTIONS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For the best development experience, run the backend and frontend"
echo "in SEPARATE terminals. This keeps logs clean and makes debugging easier."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 TERMINAL 1 - Backend API Server (Port 8000)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   # Run these commands in your FIRST terminal:"
echo ""
echo "   cd backend"
echo "   source ../venv/bin/activate"
echo "   jac serve app.jac"
echo ""
echo "   ✅ Backend will be available at: http://localhost:8000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 TERMINAL 2 - Frontend Application (Port 3000)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   # Run these commands in your SECOND terminal:"
echo ""
echo "   cd frontend"
echo "   npm start"
echo ""
echo "   ✅ Frontend will open automatically at: http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 QUICK START TIPS:"
echo ""
echo "   • The frontend is already built and configured"
echo "   • Make sure the backend is running before using the frontend"
echo "   • The backend provides REST APIs for authentication, courses, and progress"
echo "   • Check browser console (F12) for API request/response details"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "Happy coding! 🎓✨"
echo ""