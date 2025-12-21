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

# Install dependencies using the available package manager
echo "📚 Installing dependencies..."
if [ "$UV_CMD" = "uv" ]; then
    uv pip install jaclang>=0.9.3 jac-client>=0.2.3
else
    pip install jaclang>=0.9.3 jac-client>=0.2.3
fi

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "  ./run.sh"
echo ""
echo "📖 For more information, see README.md"