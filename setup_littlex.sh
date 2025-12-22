#!/bin/bash

# ==============================================================================
# Jeseci Smart Learning Academy - LittleX Pattern Setup Script
# Sets up the decoupled React + Jaclang architecture
# ==============================================================================

echo "🎓 Setting up Jeseci Smart Learning Academy - LittleX Pattern"
echo "============================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

if ! command_exists uv; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

echo "✅ Prerequisites check completed"

# Setup Backend
echo ""
echo "🔧 Setting up Backend (Jaclang API)..."
echo "======================================"

cd backend

# Install Python dependencies
echo "📦 Installing Python dependencies..."
uv pip install jaclang --index-url https://pypi.org/simple

# Install Node.js dependencies for backend
echo "📦 Installing Node.js dependencies..."
npm install

# Create backend run script
cat > run_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Jaclang Backend Server..."
echo "====================================="
cd backend
jac serve app.jac
EOF

chmod +x run_backend.sh

echo "✅ Backend setup completed"

# Setup Frontend
echo ""
echo "⚛️  Setting up Frontend (React + TypeScript)..."
echo "=============================================="

cd ../frontend

# Install frontend dependencies
echo "📦 Installing React dependencies..."
npm install

# Create frontend run script
cat > run_frontend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting React Frontend Server..."
echo "===================================="
cd frontend
npm start
EOF

chmod +x run_frontend.sh

# Create a combined run script
cd ..
cat > run_littlex.sh << 'EOF'
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
EOF

chmod +x run_littlex.sh

echo "✅ Frontend setup completed"

# Create project documentation
cat > LITTLEX_SETUP_COMPLETE.md << 'EOF'
# Jeseci Smart Learning Academy - LittleX Pattern Setup Complete! 🎉

## Architecture Overview
This project now uses the **LittleX Pattern** - a proven, decoupled architecture:

- **Backend**: Pure Jaclang API server (port 8000)
- **Frontend**: React + TypeScript application (port 3000)
- **Communication**: REST API calls between frontend and backend

## Project Structure
```
/workspace/
├── backend/              # Jaclang API Backend
│   ├── app.jac          # Main Jaclang application
│   ├── package.json     # Backend dependencies
│   └── run_backend.sh   # Backend start script
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── App.tsx      # Main React application
│   │   ├── services/    # API service layer
│   │   └── ...
│   ├── package.json     # Frontend dependencies
│   └── run_frontend.sh  # Frontend start script
├── run_littlex.sh       # Start both servers
└── setup_littlex.sh     # Setup script (this file)
```

## Quick Start

### Option 1: Start Both Servers (Recommended)
```bash
./run_littlex.sh
```

### Option 2: Start Separately
```bash
# Terminal 1 - Backend
cd backend
./run_backend.sh

# Terminal 2 - Frontend
cd frontend
./run_frontend.sh
```

## Available Endpoints

### Backend API (http://localhost:8000)
- `GET /walker/init` - Welcome message
- `GET /walker/health_check` - Health status
- `POST /walker/user_create` - Register user
- `POST /walker/user_login` - Authenticate user
- `POST /walker/course_create` - Create course
- `POST /walker/learning_session_start` - Start learning session
- `POST /walker/learning_session_end` - End learning session
- `POST /walker/user_progress` - Get user progress
- `POST /walker/analytics_generate` - Generate analytics
- `POST /walker/ai_generate_content` - AI content generation

### Frontend App (http://localhost:3000)
- User registration and authentication
- Course management and enrollment
- Learning session tracking
- Progress monitoring and analytics
- AI-powered content generation

## Key Features Implemented

✅ **Decoupled Architecture**: Separate frontend and backend
✅ **Authentication**: User registration and login
✅ **Course Management**: Create and manage learning courses
✅ **Progress Tracking**: Monitor learning progress and analytics
✅ **AI Content Generation**: AI-powered educational content
✅ **Responsive Design**: Mobile-friendly React interface
✅ **RESTful API**: Clean API communication
✅ **Type Safety**: TypeScript for frontend development

## Legacy Integration
This implementation integrates key features from the legacy system:
- Authentication and user management
- Learning session management
- Progress tracking and analytics
- AI content generation capabilities
- Course and lesson management

## Next Steps
1. Start the application: `./run_littlex.sh`
2. Open http://localhost:3000 in your browser
3. Register a new account or login
4. Explore the courses and learning features
5. Test the AI content generation

## Troubleshooting
- If backend fails to start, check if port 8000 is available
- If frontend fails to start, check if port 3000 is available
- Ensure all dependencies are installed: `npm install` in both directories
- Check the console for any error messages

Happy Learning! 🎓✨
EOF

echo ""
echo "🎉 LittleX Pattern setup completed successfully!"
echo "================================================"
echo ""
echo "📋 Summary:"
echo "   ✅ Backend: Jaclang API server (port 8000)"
echo "   ✅ Frontend: React TypeScript app (port 3000)"
echo "   ✅ Integration: REST API communication"
echo "   ✅ Features: Auth, Courses, Progress, AI Generation"
echo ""
echo "🚀 To start the application:"
echo "   ./run_littlex.sh"
echo ""
echo "📖 See LITTLEX_SETUP_COMPLETE.md for detailed documentation"
echo ""
echo "Happy coding! 🎓✨"