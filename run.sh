#!/bin/bash

# Jeseci Smart Learning Academy - Run Script
# This script starts the JAC application server with pure Jaclang frontend

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using Pure Jaclang 0.9.3 Architecture"

# Force standard PyPI to avoid mirror timeouts
PYPI_INDEX="--index-url https://pypi.org/simple"

# Function to install jac-client
install_jaclang() {
    echo "🐍 Installing jaclang and jac-client (Python packages)..."
    
    if command -v uv &> /dev/null; then
        uv pip install jaclang>=0.9.3 jac-client>=0.2.3 $PYPI_INDEX
    elif command -v pip &> /dev/null; then
        pip install jaclang>=0.9.3 jac-client>=0.2.3 $PYPI_INDEX
    elif command -v pip3 &> /dev/null; then
        pip3 install jaclang>=0.9.3 jac-client>=0.2.3 $PYPI_INDEX
    fi
    
    return $?
}

# Check if jac command is available (most important)
if ! command -v jac &> /dev/null; then
    echo "⚠️ jac command not found"
    
    # Check if virtual environment exists
    if [ -d "venv" ] && [ -f "venv/bin/python3" ]; then
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
        
        # Try installing in virtual environment if activation didn't fix it
        if ! command -v jac &> /dev/null; then
             install_jaclang
        fi
    else
        echo "⚠️ No virtual environment found. Running setup..."
        bash ./setup.sh
        source venv/bin/activate
    fi
fi

# Final check for jac command
if ! command -v jac &> /dev/null; then
    echo "❌ jac command still not found."
    echo "💡 Please run: pip install jaclang jac-client"
    exit 1
fi

echo "✅ Environment check passed."
echo ""

# Build frontend before serving
echo "🏗️ Building frontend..."
if [ -f "package.json" ]; then
    if command -v npm &> /dev/null; then
        echo "📦 Installing frontend dependencies..."
        npm install
        
        echo "🔨 Compiling frontend..."
        npm run compile
        
        echo "✅ Frontend build completed successfully!"
    else
        echo "⚠️ npm not found - frontend build skipped"
        echo "💡 Install Node.js and npm for frontend compilation"
    fi
else
    echo "⚠️ package.json not found - frontend build skipped"
fi

echo ""
echo "🚀 Starting JAC server..."
echo "📍 Access the application at: http://localhost:8000"
echo "🌐 Pure Jaclang Frontend: http://localhost:8000/page/app"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the JAC server
jac serve app.jac