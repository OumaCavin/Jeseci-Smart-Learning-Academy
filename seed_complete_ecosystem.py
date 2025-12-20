#!/usr/bin/env python3
"""
Complete Database Seeding Orchestrator
Runs all seeding scripts in the correct order to build a complete learning ecosystem
"""

import subprocess
import sys
import time
import requests
from datetime import datetime

def run_script(script_name, description):
    """Run a seeding script with proper error handling"""
    print(f"\n🚀 Running {description}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd='/workspace/jeseci-smart-learning-companion')
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed!")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def check_backend_health():
    """Check if the FastAPI backend is running"""
    print("🔍 Checking backend health...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy and running!")
            return True
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend is not running or not accessible")
        print("💡 Start the backend with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False

def verify_seeding_results():
    """Verify that seeding was successful by checking API endpoints"""
    print("\n🔍 Verifying seeding results...")
    
    try:
        # Login
        auth_resp = requests.post("http://127.0.0.1:8000/api/v1/auth/login", 
                                 json={"username": "cavin_admin", "password": "secure_password_123"})
        if auth_resp.status_code != 200:
            print("❌ Cannot verify - login failed")
            return False
            
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check concepts
        concepts_resp = requests.get("http://127.0.0.1:8000/api/v1/concepts/", headers=headers)
        if concepts_resp.status_code == 200:
            concepts_data = concepts_resp.json()
            concepts = concepts_data.get('concepts', concepts_data)
            print(f"✅ Found {len(concepts)} concepts in database")
        else:
            print("❌ Cannot fetch concepts")
            return False
            
        # Check progress
        progress_resp = requests.get("http://127.0.0.1:8000/api/v1/progress/", headers=headers)
        if progress_resp.status_code == 200:
            progress_data = progress_resp.json()
            stats = progress_data.get('overall_stats', {})
            print(f"✅ Progress tracking active:")
            print(f"   • Concepts learned: {stats.get('total_concepts_learned', 0)}")
            print(f"   • Time spent: {stats.get('total_time_spent', 0)} hours")
            print(f"   • Completion rate: {stats.get('completion_rate', 0)}%")
        else:
            print("❌ Cannot fetch progress data")
            return False
            
        # Check learning paths
        paths_resp = requests.get("http://127.0.0.1:8000/api/v1/learning-paths/", headers=headers)
        if paths_resp.status_code == 200:
            paths = paths_resp.json()
            print(f"✅ Generated {len(paths)} learning paths")
        else:
            print("❌ Cannot fetch learning paths")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main orchestration function"""
    print("🎯 JESECI SMART LEARNING COMPANION")
    print("Complete Database Seeding Orchestrator")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check backend health
    if not check_backend_health():
        print("\n❌ Cannot proceed without running backend")
        print("💡 Start backend first, then run this script again")
        return False
    
    # Step 2: Run seeding scripts in order
    scripts = [
        ("seed_concepts.py", "Concept Seeding"),
        ("seed_relationships.py", "Knowledge Graph Relationships"),
        ("seed_progress.py", "User Progress Simulation")
    ]
    
    success_count = 0
    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
            time.sleep(2)  # Brief pause between scripts
        else:
            print(f"\n⚠️  {description} failed, but continuing...")
    
    # Step 3: Verify results
    if success_count > 0:
        if verify_seeding_results():
            print("\n" + "=" * 60)
            print("🎉 COMPLETE ECOSYSTEM READY!")
            print("\n🌐 Frontend Access:")
            print("   URL: http://localhost:8080")
            print("   Login: cavin_admin / secure_password_123")
            
            print("\n📊 What you'll see:")
            print("   ✅ Dashboard with real progress statistics")
            print("   ✅ Progress page with detailed analytics")
            print("   ✅ Learning paths based on your concepts")
            print("   ✅ Connected knowledge graph relationships")
            
            print("\n🔍 Database Verification Commands:")
            print("   PostgreSQL: psql -h localhost -U jeseci_user -d jeseci_learning_companion")
            print("   Neo4j: cypher-shell -u neo4j -p neo4j_secure_password_2024")
            print("   Neo4j Query: MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name LIMIT 10")
            
            return True
        else:
            print("\n⚠️  Seeding completed but verification failed")
            return False
    else:
        print("\n❌ No seeding scripts completed successfully")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)