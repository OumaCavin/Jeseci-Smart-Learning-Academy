#!/bin/bash

# Jeseci Smart Learning Academy - Setup Script
# This script sets up the development environment for Pure Jaclang backend

echo "🎓 Setting up Jeseci Smart Learning Academy..."
echo "📋 Architecture: React Frontend + Pure Jaclang Backend"

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
echo "📚 Installing backend dependencies..."

# Define standard PyPI index to avoid mirror issues
PYPI_INDEX="--index-url https://pypi.org/simple"

install_success=false

REQUIREMENTS_FILE="backend/pyproject.toml"
BACKEND_DIR="backend"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "✅ Found dependencies file: $REQUIREMENTS_FILE"
    if [ "$UV_CMD" = "uv" ]; then
        if uv pip install -e "$BACKEND_DIR" $PYPI_INDEX 2>&1; then
            install_success=true
        fi
    else
        if $UV_CMD install -e "$BACKEND_DIR" $PYPI_INDEX 2>&1; then
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

# Install frontend dependencies
echo ""
echo "📦 Setting up frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        echo "📦 Installing npm packages..."
        npm install 2>&1 | tail -5
    fi
    cd ..
else
    echo "⚠️ Frontend directory not found, skipping npm setup"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 CONFIGURE OPENAI API KEY:"
echo ""
echo "   1. Get your API key from: https://platform.openai.com/api-keys"
echo "   2. Edit the .env file and add:"
echo "      OPENAI_API_KEY=sk-your_actual_api_key_here"
echo ""
echo "🚀 START THE APPLICATION:"
echo ""
echo "   jac serve backend/app.jac"
echo ""
echo "📍 Backend API:  http://localhost:8000"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 FEATURES:"
echo "   • Pure Jaclang Backend (Single Language Stack)"
echo "   • AI Content Generation (OpenAI or Fallback Templates)"
echo "   • Dynamic User Progress Tracking"
echo "   • Real-time Analytics Dashboard"
echo "   • Personalized Recommendations"
echo ""
echo "💡 To start the application:"
echo "   • Run: jac serve backend/app.jac"
echo "   • This starts the Jaclang backend API server on port 8000"
echo "   • The frontend (running separately) will connect to this API"
echo ""
echo "Happy coding! 🎓✨"
