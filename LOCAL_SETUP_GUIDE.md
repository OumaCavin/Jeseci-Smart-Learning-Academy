# 🚀 Running Jeseci Smart Learning Companion Locally

## Prerequisites

Before setting up the project, ensure you have the following installed on your machine:

### Required Software
- **Python 3.9 or higher** (Python 3.12+ recommended for latest features)
- **Git** (for cloning the repository)
- **pip** (Python package manager) or **uv** (faster alternative)
- **Docker & Docker Compose** (optional, for PostgreSQL/Redis/Neo4j)

### Check Your Python Version
```bash
python --version
# or
python3 --version
```

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git

# Navigate to the project directory
cd Jeseci-Smart-Learning-Academy

# Check the current branch
git status
```

## Step 2: Choose Your Setup Method

### Option A: Automated Setup (Recommended)

Run the automated setup script that handles everything automatically:

```bash
# Make the script executable (if needed)
chmod +x quick_setup.py

# Run the automated setup
python quick_setup.py
```

**What this script does:**
- ✅ Checks Python version compatibility
- ✅ Installs all Python dependencies
- ✅ Sets up environment configuration
- ✅ Handles Python 3.12 compatibility issues
- ✅ Creates database and runs migrations
- ✅ Verifies the setup is working

### Option B: Manual Setup

If you prefer manual setup or the automated script doesn't work:

#### 2.1: Install Dependencies

**For Python 3.12 users (if you get distutils errors):**
```bash
# Run the compatibility fix script
python fix_python312_compatibility.py
```

**For all users:**
```bash
# Install all dependencies
pip install -r requirements.txt

# OR if using uv
uv pip install -r requirements.txt
```

#### 2.2: Environment Configuration

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```bash
# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./jeseci.db

# JWT Configuration
JWT_SECRET_KEY=jeseci_jwt_secret_key_2024_super_secure_for_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Redis Configuration (optional for development)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis_secure_password_2024

# Neo4j Configuration (optional for development)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024

# Application Configuration
DEBUG=True
ENVIRONMENT=development
API_V1_STR=/api/v1
PROJECT_NAME=Jeseci Smart Learning Companion
```

## Step 3: Database Setup

### Option A: SQLite (Development - Recommended)
```bash
# Run database migrations
alembic upgrade head

# Verify database connection
python -c "from main import app; from config.database import get_db; print('Database connected successfully')"
```

### Option B: PostgreSQL (Production)
```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres redis neo4j

# Wait for services to be ready (30 seconds)
sleep 30

# Run database migrations
alembic upgrade head
```

## Step 4: Run the Application

### Development Mode
```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# OR using Python directly
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
# Build and start with Docker
docker-compose up --build
```

## Step 5: Access the Application

Once the server is running, you can access the application at:

### 🌐 Web Interfaces
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 📡 API Endpoints
You can test the API using the documentation interface or with curl:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Get API documentation
curl http://localhost:8000/openapi.json
```

## Troubleshooting

### Common Issues and Solutions

#### 1. **Python 3.12 Installation Error**
```bash
# Error: ModuleNotFoundError: No module named 'distutils'
# Solution: Use the compatibility fix script
python fix_python312_compatibility.py
```

#### 2. **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

#### 3. **Database Connection Error**
```bash
# Check if migrations ran successfully
alembic current
alembic history

# Re-run migrations if needed
alembic upgrade head
```

#### 4. **Import Errors**
```bash
# Ensure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 5. **Permission Errors**
```bash
# Fix file permissions
chmod +x quick_setup.py
chmod +x fix_python312_compatibility.py
```

### Python Version Compatibility

| Python Version | Status | Notes |
|---------------|--------|-------|
| 3.9           | ✅ Supported | Minimum required version |
| 3.10          | ✅ Supported | Fully compatible |
| 3.11          | ✅ Supported | Fully compatible |
| 3.12          | ✅ Supported | Use compatibility fix script |

## Project Structure

```
Jeseci-Smart-Learning-Academy/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── config/             # Configuration files
│   ├── database/           # Database models and migrations
│   ├── api/                # API routes
│   └── requirements.txt    # Python dependencies
├── SETUP_GUIDE.md         # Detailed setup guide
├── quick_setup.py         # Automated setup script
├── fix_python312_compatibility.py  # Python 3.12 fix
└── README.md              # Project documentation
```

## Next Steps

Once the application is running:

1. **Explore API Documentation**: Visit http://localhost:8000/docs
2. **Test Endpoints**: Use the interactive API documentation
3. **Set Up Frontend**: The project includes JAC language frontend components
4. **Configure Production**: Switch to PostgreSQL for production use

## Getting Help

- **Documentation**: Check SETUP_GUIDE.md for detailed information
- **API Docs**: Visit http://localhost:8000/docs for API reference
- **Repository**: https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy

---

**Author**: Cavin Otieno  
**Last Updated**: 2025-12-13 19:17:26  
**Python Version**: 3.9+ (3.12+ recommended)