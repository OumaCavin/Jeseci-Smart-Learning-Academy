#!/usr/bin/env python3
"""
Updated Complete Seeding Orchestrator
Includes graph data sync for polyglot persistence
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
                # Show key output lines
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:  # Show last 5 lines
                    if line.strip():
                        print(f"   {line}")
            return True
        else:
            print(f"❌ {description} failed!")
            if result.stderr:
                print("Error:")
                print(result.stderr)
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

def check_neo4j_health():
    """Check if Neo4j is accessible"""
    print("🔍 Checking Neo4j connectivity...")
    
    try:
        from neo4j import GraphDatabase
        
        URI = "bolt://localhost:7687"
        AUTH = ("neo4j", "neo4j_secure_password_2024")
        
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                if result.single()["test"] == 1:
                    print("✅ Neo4j is accessible!")
                    return True
                    
    except Exception as e:
        print(f"❌ Neo4j not accessible: {e}")
        print("💡 Start Neo4j and ensure it's running on bolt://localhost:7687")
        return False

def verify_polyglot_sync():
    """Verify that both SQL and Graph data are properly synced"""
    print("\n🔍 Verifying Polyglot Persistence Sync...")
    
    try:
        # Login
        auth_resp = requests.post("http://127.0.0.1:8000/api/v1/auth/login", 
                                 json={"username": "cavin_admin", "password": "secure_password_123"})
        if auth_resp.status_code != 200:
            print("❌ Cannot verify - login failed")
            return False
            
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check PostgreSQL data
        concepts_resp = requests.get("http://127.0.0.1:8000/api/v1/concepts/", headers=headers)
        if concepts_resp.status_code == 200:
            concepts_data = concepts_resp.json()
            concepts = concepts_data.get('concepts', concepts_data)
            print(f"✅ PostgreSQL: {len(concepts)} concepts available")
        else:
            print("❌ PostgreSQL: Cannot fetch concepts")
            return False
            
        # Check Neo4j data
        from neo4j import GraphDatabase
        URI = "bolt://localhost:7687"
        AUTH = ("neo4j", "neo4j_secure_password_2024")
        
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                # Check concept nodes
                concept_result = session.run("MATCH (c:Concept) RETURN count(c) as count")
                concept_count = concept_result.single()["count"]
                print(f"✅ Neo4j: {concept_count} concept nodes")
                
                # Check relationships
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                rel_count = rel_result.single()["count"]
                print(f"✅ Neo4j: {rel_count} relationships")
                
                # Check learning paths
                path_result = session.run("MATCH (lp:LearningPath) RETURN count(lp) as count")
                path_count = path_result.single()["count"]
                print(f"✅ Neo4j: {path_count} learning path nodes")
                
                # Check user relationships
                user_rel_result = session.run("MATCH (u:User)-[r]->() RETURN count(r) as count")
                user_rel_count = user_rel_result.single()["count"]
                print(f"✅ Neo4j: {user_rel_count} user relationships")
        
        return True
        
    except Exception as e:
        print(f"❌ Polyglot verification failed: {e}")
        return False

def demonstrate_graph_queries():
    """Run sample graph queries to demonstrate polyglot power"""
    print("\n🧠 Demonstrating Polyglot Persistence Power...")
    
    try:
        from neo4j import GraphDatabase
        URI = "bolt://localhost:7687"
        AUTH = ("neo4j", "neo4j_secure_password_2024")
        
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                
                print("\n📊 Query 1: Learning paths by category")
                query1 = """
                MATCH (lp:LearningPath)
                RETURN lp.category, lp.title, lp.difficulty, lp.estimated_hours
                ORDER BY lp.category, lp.title
                """
                result1 = session.run(query1)
                for record in result1:
                    print(f"   📚 {record['lp.category']}: {record['lp.title']} ({record['lp.difficulty']}, {record['lp.estimated_hours']}h)")
                
                print("\n🔗 Query 2: Concept usage across paths")
                query2 = """
                MATCH (c:Concept)<-[:CONTAINS]-(lp:LearningPath)
                WITH c, collect(lp.title) as paths, count(lp) as usage_count
                RETURN c.name, usage_count, paths
                ORDER BY usage_count DESC
                """
                result2 = session.run(query2)
                for record in result2:
                    print(f"   🔄 {record['c.name']}: used in {record['usage_count']} paths - {', '.join(record['paths'])}")
                
                print("\n👤 Query 3: User learning analytics")
                query3 = """
                MATCH (u:User {username: 'cavin_admin'})-[r:HAS_PROGRESS]->(c:Concept)
                WITH u, 
                     sum(CASE WHEN r.status = 'completed' THEN 1 ELSE 0 END) as completed,
                     sum(CASE WHEN r.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                     avg(r.progress_percent) as avg_progress
                RETURN u.username, completed, in_progress, round(avg_progress, 1) as avg_progress_percent
                """
                result3 = session.run(query3)
                record = result3.single()
                if record:
                    print(f"   📈 User: {record['u.username']}")
                    print(f"      Completed concepts: {record['completed']}")
                    print(f"      In progress: {record['in_progress']}")
                    print(f"      Average progress: {record['avg_progress_percent']}%")
                
    except Exception as e:
        print(f"❌ Graph query demonstration failed: {e}")

def main():
    """Main orchestration function for complete polyglot seeding"""
    print("🎯 JESECI SMART LEARNING COMPANION")
    print("Complete Polyglot Persistence Seeding")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 Seeding Strategy:")
    print("   🐘 PostgreSQL: Structured data (concepts, users, progress)")
    print("   🕸️  Neo4j: Graph data (relationships, paths, user journey)")
    print("   🧠 Polyglot: Best of both databases!")
    
    # Step 1: Check all services
    backend_ok = check_backend_health()
    neo4j_ok = check_neo4j_health()
    
    if not backend_ok or not neo4j_ok:
        print("\n❌ Cannot proceed - missing required services")
        return False
    
    # Step 2: Run seeding scripts in order
    scripts = [
        ("seed_concepts.py", "SQL Concepts Seeding"),
        ("seed_relationships.py", "Graph Relationships Seeding"),
        ("seed_progress.py", "SQL Progress Seeding"),
        ("sync_graph_data.py", "Graph Data Synchronization")
    ]
    
    success_count = 0
    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
            time.sleep(2)  # Brief pause between scripts
        else:
            print(f"\n⚠️  {description} failed, but continuing...")
    
    # Step 3: Verify polyglot sync
    if success_count > 0:
        if verify_polyglot_sync():
            demonstrate_graph_queries()
            
            print("\n" + "=" * 70)
            print("🎉 COMPLETE POLYGLOT ECOSYSTEM READY!")
            print("\n🌐 Frontend Access:")
            print("   URL: http://localhost:8080")
            print("   Login: cavin_admin / secure_password_123")
            
            print("\n📊 What you'll see:")
            print("   ✅ Dashboard with real SQL-driven progress statistics")
            print("   ✅ Progress page with detailed SQL analytics")
            print("   ✅ Learning paths generated from Neo4j graph structure")
            print("   ✅ Connected knowledge graph in Neo4j with traversal power")
            print("   ✅ User learning journey tracked in both databases")
            
            print("\n🧠 Polyglot Persistence Benefits:")
            print("   • PostgreSQL: Fast queries on structured progress data")
            print("   • Neo4j: Complex relationship traversal and recommendations")
            print("   • Graph queries: 'Find all paths containing Machine Learning'")
            print("   • SQL queries: 'Show user completion rates'")
            
            print("\n🔍 Neo4j Browser Queries to Try:")
            print("   MATCH (lp:LearningPath)-[:CONTAINS]->(c:Concept) RETURN lp, c")
            print("   MATCH (u:User {username: 'cavin_admin'})-[r:HAS_PROGRESS]->(c:Concept) RETURN u, r, c")
            print("   MATCH (c:Concept)<-[:CONTAINS]-(lp:LearningPath) WHERE lp.difficulty = 'Advanced' RETURN lp")
            
            return True
        else:
            print("\n⚠️  Seeding completed but polyglot verification failed")
            return False
    else:
        print("\n❌ No seeding scripts completed successfully")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)