#!/bin/bash

# Jeseci Smart Learning Academy - Run Script
# Decoupled Architecture: React Frontend + Jaclang Backend API

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using Decoupled Architecture (React + Jaclang)"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        wait $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if backend jaclang is available
if ! command -v jac &> /dev/null; then
    if [ -d "venv" ]; then
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
    fi
fi

if ! command -v jac &> /dev/null; then
    echo "❌ jac command not found. Please run: bash setup.sh first"
    exit 1
fi

echo "✅ Environment check passed."
echo ""

# Function to check if a port is in use
port_in_use() {
    netstat -tuln 2>/dev/null | grep -q ":$1 " || lsof -i :$1 2>/dev/null | grep -q LISTEN
}

# Kill any existing processes on ports 8000 and 3000
echo "🔍 Checking for existing processes..."

if port_in_use 8000; then
    echo "⚠️ Port 8000 is in use. Attempting to free it..."
    fuser -k 8000/tcp 2>/dev/null || pkill -f "jac serve" 2>/dev/null || true
    sleep 2
fi

if port_in_use 3000; then
    echo "⚠️ Port 3000 is in use. Attempting to free it..."
    fuser -k 3000/tcp 2>/dev/null || pkill -f "react-scripts" 2>/dev/null || true
    sleep 2
fi

echo "✅ Ports are ready."
echo ""

# Start backend in background
echo "🔧 Starting Jaclang Backend Server..."
echo "====================================="
(
    cd backend
    jac serve app.jac
) &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
BACKEND_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8000/walker/health_check >/dev/null 2>&1; then
        BACKEND_READY=true
        break
    fi
    sleep 1
    echo "   Waiting... ($i/30)"
done

if [ "$BACKEND_READY" = true ]; then
    echo "✅ Backend is ready at http://localhost:8000"
else
    echo "⚠️ Backend may not have started properly. Check the logs above."
fi

echo ""

# Start frontend in background
echo "⚛️  Starting React Frontend Server..."
echo "====================================="
(
    cd frontend
    npm start
) &
FRONTEND_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Both servers are starting!"
echo ""
echo "📍 Backend API:  http://localhost:8000"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 TIPS:"
echo "   • Keep both terminals running or use Ctrl+C to stop"
echo "   • The frontend will automatically open in your browser"
echo "   • Backend provides REST APIs for:"
echo "     - POST /walker/user_create (Register)"
echo "     - POST /walker/user_login (Login)"
echo "     - POST /walker/course_create"
echo "     - POST /walker/user_progress"
echo "     - POST /walker/ai_generate_content"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
