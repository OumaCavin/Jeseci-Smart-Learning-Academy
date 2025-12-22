#!/bin/bash
# Jeseci Smart Learning Companion - Virtual Environment Setup
# Author: Cavin Otieno
# Date: December 13, 2025

set -e  # Exit on any error

echo "🚀 Setting up Jeseci Smart Learning Companion Virtual Environment..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if file exists
file_exists() {
    [ -f "$1" ]
}

# Function to check if directory exists
dir_exists() {
    [ -d "$1" ]
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Python 3 is available
if ! command_exists python3; then
    echo "❌ Error: python3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📋 Found Python version: $python_version"

# Check if Git is available
if ! command_exists git; then
    echo "⚠️  Warning: git is not installed. You may need it for repository operations."
fi

# Check if pip is available
if ! command_exists pip; then
    echo "❌ Error: pip is not available. Please ensure pip is installed with Python."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Step 1: Create virtual environment (only if it doesn't exist)
echo ""
echo "📦 Setting up virtual environment..."

if dir_exists "venv"; then
    echo "⚠️  Virtual environment 'venv' already exists."
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
        echo "📦 Creating new virtual environment..."
        python3 -m venv venv
    else
        echo "⏭️  Skipping virtual environment creation."
    fi
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Verify virtual environment was created
if ! dir_exists "venv"; then
    echo "❌ Error: Failed to create virtual environment."
    exit 1
fi

echo "✅ Virtual environment ready!"

# Step 2: Activate virtual environment
echo ""
echo "⚡ Activating virtual environment..."

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated!"
else
    echo "❌ Error: Virtual environment activation script not found."
    exit 1
fi

# Verify activation
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Error: Failed to activate virtual environment."
    exit 1
fi

echo "🔍 Current virtual environment: $VIRTUAL_ENV"

# Step 3: Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."

if command_exists pip; then
    pip install --upgrade pip
    echo "✅ Pip upgraded successfully!"
else
    echo "❌ Error: pip command not available in virtual environment."
    exit 1
fi

# Step 4: Install Python dependencies
echo ""
echo "📚 Installing Python dependencies..."

if file_exists "requirements.txt"; then
    echo "📄 Found requirements.txt, installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Error: requirements.txt not found. Please ensure you're in the project root directory."
    exit 1
fi

# Step 5: Install JAC language specifically
echo ""
echo "🔧 Installing JAC language runtime..."

echo "🔍 Checking if jaclang is already installed..."
if pip show jaclang >/dev/null 2>&1; then
    echo "📦 Updating existing jaclang installation..."
    pip install --upgrade "jaclang>=0.9.3"
else
    echo "📦 Installing jaclang..."
    pip install "jaclang>=0.9.3"
fi

echo "✅ JAC language installed successfully!"

# Step 6: Verify installations
echo ""
echo "✅ Verifying installations..."

echo "🐍 Python version:"
python --version

echo ""
echo "📦 Installed packages verification:"
echo "   - jaclang: $(pip show jaclang 2>/dev/null | grep Version | cut -d' ' -f2 || echo 'Not found')"
echo "   - fastapi: $(pip show fastapi 2>/dev/null | grep Version | cut -d' ' -f2 || echo 'Not found')"
echo "   - sqlalchemy: $(pip show sqlalchemy 2>/dev/null | grep Version | cut -d' ' -f2 || echo 'Not found')"
echo "   - cryptography: $(pip show cryptography 2>/dev/null | grep Version | cut -d' ' -f2 || echo 'Not found')"

# Step 7: Test JAC installation
echo ""
echo "🧪 Testing JAC installation..."
if command -v jac >/dev/null 2>&1; then
    echo "✅ JAC command is available!"
    jac --version
else
    echo "⚠️  Warning: JAC command not found in PATH. You may need to restart your shell."
fi

# Final status
echo ""
echo "🎉 Virtual environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate environment: source venv/bin/activate"
echo "   2. Run JAC application: jac serve app.jac"
echo "   3. Run FastAPI server: uvicorn main:app --reload"
echo ""
echo "💡 To activate the environment in future sessions:"
echo "   source venv/bin/activate"
echo ""
echo "🌐 Access points (when running):"
echo "   - JAC Application: http://localhost:8000"
echo "   - FastAPI Docs: http://localhost:8000/docs"
echo ""
echo "✅ Setup completed successfully!"