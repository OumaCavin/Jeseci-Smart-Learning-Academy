#!/bin/bash

# Jeseci Smart Learning Academy - Setup Script
# This script sets up the development environment for FastAPI backend

echo "🎓 Setting up Jeseci Smart Learning Academy..."
echo "📋 Architecture: React Frontend + FastAPI Backend + OpenAI Integration"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "💡 Please install Python 3.8 or later from: https://python.org"
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

# Function to install from requirements file with timeout
install_from_requirements() {
    local cmd="$1"
    local req_file="$2"
    echo "📦 Installing from requirements file: $req_file"
    
    # Use timeout command to limit execution time
    if timeout 180 $cmd install -r "$req_file" $PYPI_INDEX 2>&1; then
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo "⚠️ Installation timed out after 180 seconds"
        else
            echo "⚠️ Installation failed, trying individual packages..."
        fi
        # Fallback to individual package installation
        $cmd install fastapi>=0.104.0 uvicorn>=0.24.0 $PYPI_INDEX
    fi
}

install_success=false

# Install from backend requirements file
REQUIREMENTS_FILE="backend/requirements.txt"
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
    echo "❌ Requirements file not found: $REQUIREMENTS_FILE"
    exit 1
fi

if [ "$install_success" = false ]; then
    echo "❌ Failed to install backend packages"
    echo "💡 This might be due to network issues or firewall restrictions"
    echo "💡 Please try:"
    echo "   1. Check your internet connection"
    echo "   2. Install manually: cd backend && pip install -r requirements.txt"
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
echo "   bash run.sh"
echo ""
echo "📍 Backend API:  http://localhost:8000"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 FEATURES:"
echo "   • AI Content Generation with OpenAI GPT-4o-mini"
echo "   • Dynamic User Progress Tracking"
echo "   • Real-time Analytics Dashboard"
echo "   • Personalized Recommendations"
echo ""
echo "💡 The run.sh script will:"
echo "   • Check and free ports 8000 and 3000 if needed"
echo "   • Start the FastAPI backend server"
echo "   • Start the React frontend server"
echo "   • Both servers run in a single terminal"
echo ""
echo "Happy coding! 🎓✨"
