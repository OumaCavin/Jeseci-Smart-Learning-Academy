#!/bin/bash

echo "🎓 Starting Jeseci Smart Learning Academy - LittleX Pattern"
echo "============================================================"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🔧 Starting Jaclang Backend Server..."
cd backend && jac serve app.jac &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "⚛️  Starting React Frontend Server..."
cd frontend && npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers are starting!"
echo "📍 Backend API: http://localhost:8000"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
