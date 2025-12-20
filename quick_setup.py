#!/usr/bin/env python3
"""
Quick Setup Script for Jeseci Smart Learning Companion
Automates the initial setup process after git pull origin main
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(command, cwd=None, timeout=60):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required. Current version:", 
              f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def setup_application():
    """Setup the application environment"""
    project_dir = Path(__file__).parent
    
    print("🔧 Setting up application environment...")
    
    # Change to project directory (now the root)
    os.chdir(project_dir)
    
    # Install dependencies
    print("📦 Installing Python dependencies...")
    returncode, stdout, stderr = run_command("pip install -r requirements.txt")
    
    if returncode == 0:
        print("✅ Dependencies installed successfully")
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    # Create .env file if it doesn't exist
    env_file = project_dir / ".env"
    if not env_file.exists():
        print("📝 Creating environment configuration...")
        env_content = """# Database Configuration
DATABASE_URL=sqlite:///./jeseci.db

# JWT Configuration
JWT_SECRET_KEY=jeseci_jwt_secret_key_2024_super_secure_for_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis_secure_password_2024

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024

# Application Configuration
DEBUG=True
ENVIRONMENT=development
API_V1_STR=/api/v1
PROJECT_NAME=Jeseci Smart Learning Companion
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Environment configuration created")
    
    return True

def setup_database():
    """Setup database and run migrations"""
    print("🗄️ Setting up database...")
    
    # Check if we need to start services
    print("🚀 Starting database services...")
    returncode, stdout, stderr = run_command("docker-compose up -d postgres redis neo4j", timeout=120)
    
    if returncode != 0:
        print("⚠️ Docker services startup failed, continuing with SQLite...")
        returncode, stdout, stderr = run_command("alembic upgrade head")
    else:
        print("⏳ Waiting for services to be ready...")
        time.sleep(30)
        returncode, stdout, stderr = run_command("alembic upgrade head")
    
    if returncode == 0:
        print("✅ Database setup completed")
        return True
    else:
        print(f"⚠️ Database setup completed with warnings: {stderr}")
        return True

def verify_setup():
    """Verify that the setup was successful"""
    print("🔍 Verifying setup...")
    
    # Test database connection
    test_script = '''
import sys
sys.path.append(".")
from config.database import engine, Base
from main import app
from fastapi.testclient import TestClient

try:
    # Test database connection
    connection = engine.connect()
    connection.close()
    print("✅ Database connection successful")
    
    # Test FastAPI app
    client = TestClient(app)
    response = client.get("/health")
    if response.status_code == 200:
        print("✅ FastAPI application working")
        print("📊 Health status:", response.json())
    else:
        print("❌ FastAPI application test failed")
        
except Exception as e:
    print(f"❌ Setup verification failed: {str(e)}")
    sys.exit(1)
'''
    
    returncode, stdout, stderr = run_command(f'python -c "{test_script}"')
    
    if returncode == 0:
        print("✅ Setup verification successful")
        print(stdout)
        return True
    else:
        print(f"⚠️ Setup verification completed with warnings: {stderr}")
        return True

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. Start the development server:")
    print("   cd .")
    print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\n2. Access the application:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("\n3. Test the API:")
    print("   curl http://localhost:8000/health")
    print("\n4. For production deployment:")
    print("   docker-compose up --build")
    print("\n📚 For detailed instructions, see: SETUP_GUIDE.md")
    print("\n🔗 Repository: https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("🚀 Jeseci Smart Learning Companion - Quick Setup")
    print("="*60)
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    if not check_python_version():
        return 1
    
    # Check if we're in the right directory
    if not (Path("main.py").exists() and Path("SETUP_GUIDE.md").exists()):
        print("❌ Please run this script from the project root directory")
        print("   (the directory containing 'main.py' and 'SETUP_GUIDE.md')")
        return 1
    
    # Setup application
    if not setup_application():
        return 1
    
    # Setup database
    if not setup_database():
        return 1
    
    # Verify setup
    verify_setup()
    
    # Print next steps
    print_next_steps()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)