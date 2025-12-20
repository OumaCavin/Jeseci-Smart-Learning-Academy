#!/bin/bash

# Jeseci Smart Learning Academy - Setup Script
# This script sets up the development environment

echo "🎓 Setting up Jeseci Smart Learning Academy..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install JAC and dependencies
echo "📚 Installing dependencies..."
pip install jaclang>=0.9.3 jac-client>=0.2.3

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "  ./run.sh"
echo ""
echo "📖 For more information, see README.md"