#!/bin/bash
echo "🚀 Starting Python/FastAPI Backend Server with Jaclang-compatible endpoints..."
echo "==========================================================================="
cd backend

# Check if virtual environment exists and activate it
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt -q
fi

# Start the FastAPI backend
echo "🌐 Starting server on http://0.0.0.0:8000"
echo "📚 API Documentation available at http://localhost:8000/docs"
python main.py
