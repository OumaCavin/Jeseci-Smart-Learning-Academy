#!/usr/bin/env python3
"""
Quick setup and startup script for Jeseci Smart Learning Companion
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run shell command and return result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True


def setup_development():
    """Setup development environment"""
    print("🔧 Setting up development environment...")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", cwd="backend"):
        return False
    
    # Setup database
    if not run_command("alembic upgrade head", cwd="backend"):
        return False
    
    print("✅ Development setup complete!")
    return True


def start_api():
    """Start the FastAPI development server"""
    print("🚀 Starting API server...")
    os.chdir("backend")
    os.execvp("uvicorn", ["uvicorn", "main:app", "--reload", "--port", "8000"])


def start_docker():
    """Start all services with Docker"""
    print("🐳 Starting services with Docker...")
    
    # Start services
    if not run_command("docker-compose up -d"):
        return False
    
    print("⏳ Waiting for services to be ready...")
    import time
    time.sleep(10)
    
    # Initialize database
    if not run_command("docker-compose exec api alembic upgrade head"):
        return False
    
    print("✅ All services started successfully!")
    print("📊 Services available at:")
    print("  - API: http://localhost:8000")
    print("  - API Docs: http://localhost:8000/docs")
    print("  - Neo4j: http://localhost:7474")
    
    return True


def stop_docker():
    """Stop all Docker services"""
    print("🛑 Stopping Docker services...")
    run_command("docker-compose down")


def check_health():
    """Check service health"""
    print("🏥 Checking service health...")
    try:
        import requests
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"📊 Database Connections: {data['database_connections']}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Jeseci Smart Learning Companion Setup")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup development environment")
    
    # Start API command
    start_parser = subparsers.add_parser("start", help="Start API server")
    
    # Docker commands
    docker_parser = subparsers.add_parser("docker", help="Docker operations")
    docker_subparsers = docker_parser.add_subparsers(dest="docker_command")
    
    docker_start = docker_subparsers.add_parser("start", help="Start with Docker")
    docker_stop = docker_subparsers.add_parser("stop", help="Stop Docker services")
    docker_restart = docker_subparsers.add_parser("restart", help="Restart Docker services")
    
    # Health check
    health_parser = subparsers.add_parser("health", help="Check service health")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "setup":
        setup_development()
    elif args.command == "start":
        start_api()
    elif args.command == "docker":
        if args.docker_command == "start":
            start_docker()
        elif args.docker_command == "stop":
            stop_docker()
        elif args.docker_command == "restart":
            stop_docker()
            start_docker()
        else:
            docker_parser.print_help()
    elif args.command == "health":
        check_health()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()