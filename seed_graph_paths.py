"""
Seed Graph Learning Paths
Syncs learning paths to Neo4j graph database with our current concepts
"""

import requests

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "cavin_admin"
PASSWORD = "secure_password_123"

# Define Paths and their Concepts (Updated to match our current database)
GRAPH_PATHS = [
    {
        "title": "Programming Fundamentals Journey",
        "difficulty": "Beginner",
        "category": "Computer Science",
        "contains": ["variables", "arrays"]
    },
    {
        "title": "Web Development Essentials",
        "difficulty": "Beginner", 
        "category": "Computer Science",
        "contains": ["html_basics", "variables"]
    },
    {
        "title": "Mathematics for Programming",
        "difficulty": "Intermediate",
        "category": "Mathematics",
        "contains": ["linear_equations", "variables"]
    },
    {
        "title": "Science & Technology Integration",
        "difficulty": "Intermediate",
        "category": "Life Sciences",
        "contains": ["photosynthesis", "linear_equations"]
    }
]

def seed_graph_paths():
    print("🚀 Syncing Learning Paths to Neo4j...")
    print("=" * 60)

    try:
        # 1. Login
        print("🔐 Authenticating...")
        auth_resp = requests.post(f"{API_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
        if auth_resp.status_code != 200:
            print(f"❌ Authentication failed: {auth_resp.status_code}")
            return False
            
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful!")

        # 2. Get Concept IDs for lookup
        print("\n🔍 Resolving concept IDs...")
        all_concepts = requests.get(f"{API_URL}/concepts/", headers=headers).json()
        concept_map = {c["name"]: c["concept_id"] for c in all_concepts}
        print(f"📚 Found {len(concept_map)} concepts")
        
        for name, cid in concept_map.items():
            print(f"   • {name}: {cid[:8]}...")

        # 3. Create Path Nodes & Links in Neo4j
        print("\n🕸️  Creating Learning Paths in Neo4j...")
        
        try:
            from neo4j import GraphDatabase
            
            # Neo4j Config
            URI = "bolt://localhost:7687"
            AUTH = ("neo4j", "neo4j_secure_password_2024")

            with GraphDatabase.driver(URI, auth=AUTH) as driver:
                with driver.session() as session:
                    
                    for path in GRAPH_PATHS:
                        print(f"\n📦 Creating Path: {path['title']}")
                        
                        # A. Create the Learning Path Node
                        query_path = """
                        MERGE (lp:LearningPath {title: $title})
                        SET lp.difficulty = $difficulty,
                            lp.category = $category,
                            lp.created_at = datetime()
                        RETURN lp.title as title
                        """
                        result = session.run(query_path, 
                                           title=path['title'], 
                                           difficulty=path['difficulty'], 
                                           category=path['category'])
                        created_title = result.single()['title']
                        print(f"   ✅ Created Learning Path: {created_title}")

                        # B. Link Path -> Concepts
                        for concept_name in path['contains']:
                            concept_id = concept_map.get(concept_name)
                            if concept_id:
                                print(f"   🔗 Linking -> {concept_name}")
                                query_link = """
                                MATCH (lp:LearningPath {title: $title})
                                MATCH (c:Concept {concept_id: $cid})
                                MERGE (lp)-[:CONTAINS]->(c)
                                RETURN c.name as concept_name
                                """
                                result = session.run(query_link, title=path['title'], cid=concept_id)
                                linked_concept = result.single()['concept_name']
                                print(f"      ✅ Linked: {linked_concept}")
                            else:
                                print(f"   ⚠️  Concept not found: {concept_name}")

        except ImportError:
            print("❌ Neo4j driver not available. Installing...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "neo4j"])
            
            # Retry with installed driver
            from neo4j import GraphDatabase
            with GraphDatabase.driver(URI, auth=AUTH) as driver:
                with driver.session() as session:
                    # Repeat the path creation logic
                    for path in GRAPH_PATHS:
                        print(f"\n📦 Creating Path: {path['title']}")
                        
                        query_path = """
                        MERGE (lp:LearningPath {title: $title})
                        SET lp.difficulty = $difficulty,
                            lp.category = $category,
                            lp.created_at = datetime()
                        RETURN lp.title as title
                        """
                        result = session.run(query_path, 
                                           title=path['title'], 
                                           difficulty=path['difficulty'], 
                                           category=path['category'])
                        created_title = result.single()['title']
                        print(f"   ✅ Created Learning Path: {created_title}")

                        for concept_name in path['contains']:
                            concept_id = concept_map.get(concept_name)
                            if concept_id:
                                print(f"   🔗 Linking -> {concept_name}")
                                query_link = """
                                MATCH (lp:LearningPath {title: $title})
                                MATCH (c:Concept {concept_id: $cid})
                                MERGE (lp)-[:CONTAINS]->(c)
                                RETURN c.name as concept_name
                                """
                                result = session.run(query_link, title=path['title'], cid=concept_id)
                                linked_concept = result.single()['concept_name']
                                print(f"      ✅ Linked: {linked_concept}")
                            else:
                                print(f"   ⚠️  Concept not found: {concept_name}")

        except Exception as e:
            print(f"❌ Neo4j connection error: {e}")
            print("💡 Make sure Neo4j is running on bolt://localhost:7687")
            print("💡 Or run: docker run -p 7687:7687 -p 7474:7474 neo4j")
            return False

        print("\n" + "=" * 60)
        print("✅ Graph Paths Synced Successfully!")
        print(f"🎯 Created {len(GRAPH_PATHS)} learning paths")
        
        # Show summary
        total_links = sum(len(path['contains']) for path in GRAPH_PATHS)
        print(f"🔗 Created {total_links} path-concept relationships")
        
        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Start the API server first: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = seed_graph_paths()
    if success:
        print("\n🌟 Learning Paths are now available in Neo4j!")
        print("🔍 View in Neo4j Browser: http://localhost:7474")
    else:
        print("\n⚠️  Seeding incomplete. Check errors above.")