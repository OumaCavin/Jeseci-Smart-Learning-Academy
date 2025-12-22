#!/usr/bin/env python3
"""
Python 3.12 Compatibility Fix for Jeseci Smart Learning Companion
This script resolves dependency issues when installing requirements on Python 3.12
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.minor < 9):
        print("❌ Python 3.9+ is required. Current version:", 
              f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_build_dependencies():
    """Install build dependencies for Python 3.12"""
    print("🔧 Installing build dependencies for Python 3.12...")
    
    # Install setuptools and wheel for build support
    commands = [
        "pip install --upgrade setuptools wheel",
        "pip install --upgrade pip",
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {cmd} completed successfully")
        else:
            print(f"⚠️ {cmd} completed with warnings: {result.stderr}")
    
    return True

def fix_numpy_compatibility():
    """Fix numpy compatibility issues for Python 3.12"""
    print("🔧 Fixing numpy compatibility...")
    
    # Try to install a compatible numpy version first
    compatible_commands = [
        "pip install 'numpy>=1.26.0' --only-binary=numpy",
        "pip install 'pandas>=2.1.0' --only-binary=all",
    ]
    
    for cmd in compatible_commands:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {cmd} completed successfully")
        else:
            print(f"⚠️ {cmd} failed: {result.stderr}")
    
    return True

def install_requirements():
    """Install requirements with compatibility fixes"""
    print("📦 Installing requirements.txt...")
    
    # Install with --only-binary flag to avoid source builds
    cmd = "pip install -r requirements.txt --only-binary=numpy,pandas,torch,transformers"
    
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    
    if result.returncode == 0:
        print("✅ Requirements installed successfully!")
        return True
    else:
        print(f"❌ Requirements installation failed:")
        print(f"Error: {result.stderr}")
        
        # Try alternative installation method
        print("\n🔄 Trying alternative installation method...")
        alt_cmd = "pip install -r requirements.txt --prefer-binary"
        alt_result = subprocess.run(alt_cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if alt_result.returncode == 0:
            print("✅ Alternative installation successful!")
            return True
        else:
            print(f"❌ Alternative installation also failed: {alt_result.stderr}")
            return False

def create_pyproject_toml():
    """Create pyproject.toml for better dependency management"""
    print("📝 Creating pyproject.toml for better dependency management...")
    
    project_dir = Path(__file__).parent
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "jeseci-backend"
version = "1.0.0"
description = "Backend API for Jeseci Smart Learning Companion"
authors = [{name = "Cavin Otieno", email = "cavin.otieno@example.com"}]
readme = "README.md"
requires-python = ">=3.9"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "fastapi==0.124.0",
    "uvicorn[standard]==0.38.0",
    "starlette==0.50.0",
    "sqlalchemy==2.0.44",
    "alembic==1.17.2",
    "psycopg2-binary==2.9.11",
    "redis==7.1.0",
    "neo4j==6.0.3",
    "PyJWT==2.9.0",
    "cryptography==41.0.8",
    "passlib[bcrypt]==1.7.4",
    "python-jose[cryptography]==3.3.0",
    "pydantic==2.12.5",
    "pydantic-settings==2.0.3",
    "marshmallow==3.20.0",
    "httpx==0.27.2",
    "requests==2.31.0",
    "aiohttp==3.8.0",
    "pandas==2.1.4",
    "numpy==1.26.2",
    "python-dotenv==1.2.1",
    "click==8.1.0",
    "pytest==7.4.0",
    "pytest-asyncio==0.21.0",
    "pytest-cov==4.1.0",
    "black==23.7.0",
    "isort==5.13.2",
    "flake8==6.1.0",
    "prometheus-client==0.17.0",
    "structlog==23.1.0",
    "python-multipart==0.0.9",
    "email-validator==2.1.0",
    "pytz==2023.3",
    "python-dateutil==2.8.2",
    "openai==1.12.0",
    "transformers==4.36.0",
    "torch==2.1.2",
    "gunicorn==21.2.0",
    "slowapi==0.1.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "isort>=5.13.2",
    "flake8>=6.1.0",
    "mypy>=1.6.0",
]

[tool.setuptools]
packages = ["."]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""
    
    pyproject_path = project_dir / "pyproject.toml"
    with open(pyproject_path, 'w') as f:
        f.write(pyproject_content)
    
    print(f"✅ Created {pyproject_path}")
    return True

def main():
    """Main function to fix Python 3.12 compatibility issues"""
    print("🚀 Python 3.12 Compatibility Fix for Jeseci Smart Learning Companion")
    print("="*70)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check if we're in the right directory
    project_dir = Path(__file__).parent
    if not (project_dir / "main.py").exists():
        print("❌ Project directory not found!")
        print("Please run this script from the project root directory")
        return 1
    
    # Change to project directory
    os.chdir(project_dir)
    
    # Install build dependencies
    install_build_dependencies()
    
    # Fix numpy compatibility
    fix_numpy_compatibility()
    
    # Create pyproject.toml for better dependency management
    create_pyproject_toml()
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Installation failed. Please try manual installation:")
        print("pip install --upgrade pip setuptools wheel")
        print("pip install -r requirements.txt --only-binary=numpy,pandas")
        return 1
    
    print("\n" + "="*70)
    print("✅ Python 3.12 compatibility fix completed successfully!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("1. Run database migrations:")
    print("   alembic upgrade head")
    print("\n2. Start the development server:")
    print("   uvicorn main:app --reload")
    print("\n3. Access the application:")
    print("   http://localhost:8000/docs")
    print("\n🔗 Repository: https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy")
    print("="*70)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)