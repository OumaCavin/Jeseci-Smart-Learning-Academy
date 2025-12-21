#!/bin/bash
# Complete development script for Jaclang + Vite setup
# This script handles the full build and serve process

set -e  # Exit on any error

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Environment: Local Development with Vite + Jaclang"

# Check Node.js and npm
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18.19.0 or later."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | sed 's/v//')
REQUIRED_VERSION="18.19.0"

if ! npm list vite &> /dev/null 2>&1; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || echo "⚠️ Virtual environment not found, continuing with system Python"

echo "📦 Installing Vite dependencies..."
npm install vite @vitejs/plugin-react @jac-client/utils

echo "🔨 Building frontend with Vite..."
npm run build

echo "🔧 Compiling JAC application..."
jac build ./app.jac

BUILD_EXIT_CODE=$?
if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "❌ FAILED TO COMPILE JAC APPLICATION"
    exit 1
fi

echo "✅ Compilation successful! Starting servers..."
echo "📍 Frontend (Vite): http://localhost:3000"
echo "📍 Backend (Jac): http://localhost:8000"
echo "🌐 Integrated App: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Start both servers concurrently
npm run full-dev