#!/bin/bash

# Jeseci Smart Learning Academy - Run Script
# Architecture: React Frontend + FastAPI Backend with OpenAI Integration

echo "🎓 Starting Jeseci Smart Learning Academy..."
echo "📋 Using FastAPI Backend with OpenAI Integration"

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

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Please install Python 3.8+ first"
    exit 1
fi

echo "✅ Python available."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ No virtual environment found. Using system Python."
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
cd backend
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Check if OpenAI API key is configured
if [ -f "../.env" ]; then
    if grep -q "OPENAI_API_KEY=sk-" "../.env"; then
        echo "✅ OpenAI API key configured."
    else
        echo "⚠️ OpenAI API key not found in .env file. AI features will use fallback templates."
    fi
fi

cd ..
echo ""

# Function to check if a port is in use
port_in_use() {
    netstat -tuln 2>/dev/null | grep -q ":$1 " || lsof -i :$1 2>/dev/null | grep -q LISTEN
}

# Kill any existing processes on ports 8000 and 3000
echo "🔍 Checking for existing processes..."

if port_in_use 8000; then
    echo "⚠️ Port 8000 is in use. Attempting to free it..."
    fuser -k 8000/tcp 2>/dev/null || pkill -f "uvicorn" 2>/dev/null || pkill -f "python.*main.py" 2>/dev/null || true
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
echo "🔧 Starting FastAPI Backend Server..."
echo "======================================"
(
    cd backend
    python3 main.py
) &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
BACKEND_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
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
echo "💡 FEATURES:"
echo "   • AI Content Generation with OpenAI GPT-4o-mini"
echo "   • Dynamic User Progress Tracking"
echo "   • Real-time Analytics Dashboard"
echo "   • Personalized Recommendations"
echo ""
echo "📡 API Endpoints:"
echo "   • POST /user/create (Register)"
echo "   • POST /user/login (Login)"
echo "   • GET /courses (List Courses)"
echo "   • POST /user/progress (Get Progress)"
echo "   • POST /ai/generate/content (Generate AI Content)"
echo "   • POST /analytics/generate (Get Analytics)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
