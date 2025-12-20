# Jeseci Smart Learning Academy - Setup Guide

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.9+**
- **Git**
- **Docker & Docker Compose** (for PostgreSQL/Redis/Neo4j)
- **pip** or **uv** (Python package manager)

## Quick Setup After Git Pull

### 1. Clone and Pull Latest Changes

```bash
# If not already cloned
git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
cd Jeseci-Smart-Learning-Academy

# Pull latest changes
git pull origin main
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Navigate to backend directory
cd .

# OPTION 1: Automated Python 3.12 compatibility fix (Recommended)
python ../fix_python312_compatibility.py

# OPTION 2: Manual installation
pip install -r requirements.txt

# OR if using uv
uv pip install -r requirements.txt
```

#### Python 3.12 Compatibility Note

If you're using **Python 3.12** and encounter installation errors related to `distutils` or numpy build failures, use the automated fix script:

```bash
python ../fix_python312_compatibility.py
```

This script will:
- Install required build dependencies
- Fix numpy compatibility issues 
- Create proper `pyproject.toml` configuration
- Handle binary package installations to avoid source builds

#### Environment Configuration

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Update `.env` file with your configuration:**
```bash
# Database Configuration
DATABASE_URL=sqlite:///./jeseci.db  # For development
# Or PostgreSQL for production:
# DATABASE_URL=postgresql://jeseci_user:jeseci_secure_password_2024@localhost:5432/jeseci_learning_companion

# JWT Configuration
JWT_SECRET_KEY=jeseci_jwt_secret_key_2024_super_secure_for_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Redis Configuration (for caching)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis_secure_password_2024

# Neo4j Configuration (for knowledge graphs)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024

# Application Configuration
DEBUG=True
ENVIRONMENT=development
API_V1_STR=/api/v1
PROJECT_NAME=Jeseci Smart Learning Companion
```

### 3. Database Setup

#### Option A: SQLite (Development)
```bash
# Run database migrations
alembic upgrade head

# Check database connection
python -c "from main import app; from config.database import get_db; print('Database connected successfully')"
```

#### Option B: PostgreSQL (Production)
```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres redis neo4j

# Wait for services to be ready (30 seconds)
sleep 30

# Run database migrations
alembic upgrade head

# Check database connection
python -c "from main import app; from config.database import get_db; print('Database connected successfully')"
```

### 4. Start the Application

#### Development Mode
```bash
# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode with Docker
```bash
# Build and start all services
docker-compose up --build

# Or run only backend
docker-compose up --build backend
```

### 5. Verify Setup

#### Check Health Status
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-10T02:42:36Z"
}
```

#### Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Architecture Overview

### Backend Structure
```

├── main.py                    # FastAPI application entry point
├── config/
│   └── database.py           # Database configuration
├── database/
│   └── models/               # SQLAlchemy models
├── api/
│   └── v1/                   # API route handlers
├── migrations/               # Alembic migrations
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
└── README.md               # Backend documentation
```

### Key Features
- **Authentication**: JWT-based user authentication
- **User Management**: Profile and preferences management
- **Knowledge Graph**: Concept and relationship management
- **Learning Paths**: Structured learning progression
- **Progress Tracking**: User learning analytics
- **Assessment**: Quiz and achievement system
- **Analytics**: Learning insights and reporting

## Database Schema

### Core Tables
- `users` - User accounts and profiles
- `concepts` - Knowledge concepts
- `learning_paths` - Structured learning routes
- `user_progress` - Learning progress tracking
- `quizzes` - Assessment questions
- `user_achievements` - Gamification system

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/preferences` - Get learning preferences

### Learning
- `GET /api/v1/concepts` - List all concepts
- `POST /api/v1/concepts` - Create new concept
- `GET /api/v1/learning-paths` - Get learning paths
- `POST /api/v1/learning-paths` - Create learning path

### Progress
- `GET /api/v1/progress` - Get user progress
- `POST /api/v1/progress` - Update progress
- `GET /api/v1/achievements` - Get user achievements

### Analytics
- `GET /api/v1/analytics/dashboard` - Learning analytics
- `GET /api/v1/analytics/performance` - Performance metrics

## Development Workflow

### Running Tests
```bash
# Backend tests
cd .
pytest

# Run with coverage
pytest --cov=.
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Deployment

### Production Docker Deployment
```bash
# Build production images
docker-compose -f docker-compose.yml up --build -d

# Scale services
docker-compose up --scale backend=3 -d

# Check logs
docker-compose logs -f
```

### Environment Variables for Production
```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=False
export DATABASE_URL=postgresql://user:password@postgres:5432/dbname
export JWT_SECRET_KEY=your-super-secure-secret-key
```

## Troubleshooting

### Common Issues

1. **Python 3.12 Installation Error (distutils/numpy)**
   ```bash
   # Error: ModuleNotFoundError: No module named 'distutils'
   # Solution: Use the compatibility fix script
   python fix_python312_compatibility.py
   
   # Or manual fix:
   pip install --upgrade setuptools wheel pip
   pip install numpy pandas --only-binary=numpy,pandas
   ```

2. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd .
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

5. **Permission Errors**
   ```bash
   # Fix file permissions
   chmod +x setup.py
   chmod +x scripts/*.py
   chmod +x fix_python312_compatibility.py
   ```

## Support

For additional support:
- Check the backend README.md for detailed documentation
- Review API documentation at `/docs`
- Check application logs for error details

---

**Last Updated**: 2025-12-10 02:42:36  
**Version**: 1.0.0  
**Author**: Cavin Otieno