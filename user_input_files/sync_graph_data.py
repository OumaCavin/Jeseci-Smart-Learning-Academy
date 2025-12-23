import requests
from neo4j import GraphDatabase

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "cavin_admin"
PASSWORD = "secure_password_123"

# Define Learning Paths and their Concepts for Neo4j Graph
GRAPH_PATHS = [
    {
        "title": "Mastering Computer Science",
        "difficulty": "Advanced", 
        "category": "Computer Science",
        "estimated_hours": 120,
        "contains": ["machine_learning", "data_structures", "object_oriented_programming"]
    },
    {
        "title": "Web Development Fundamentals",
        "difficulty": "Beginner",
        "category": "Web Development", 
        "estimated_hours": 80,
        "contains": ["web_development", "data_structures"]
    },
    {
        "title": "Programming Essentials",
        "difficulty": "Beginner",
        "category": "Programming",
        "estimated_hours": 60,
        "contains": ["object_oriented_programming", "data_structures"]
    },
    {
        "title": "Data Science Track",
        "difficulty": "Advanced",
        "category": "Data Science",
        "estimated_hours": 100,
        "contains": ["machine_learning", "data_structures", "web_development"]
    }
]

def sync_learning_paths_to_neo4j():
    """Sync learning paths to Neo4j as graph nodes with CONTAINS relationships"""
    print("🚀 Syncing Learning Paths to Neo4j Graph...")
    print("=" * 60)

    # 1. Login and get authentication
    print("🔐 Authenticating...")
    try:
        auth_resp = requests.post(f"{API_URL}/auth/login", 
                                 json={"username": USERNAME, "password": PASSWORD})
        if auth_resp.status_code != 200:
            print(f"❌ Authentication failed: {auth_resp.text}")
            return False
            
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful!")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

    # 2. Get Concept IDs for lookup
    print("\n🔍 Resolving concept IDs...")
    try:
        concepts_resp = requests.get(f"{API_URL}/concepts/", headers=headers)
        if concepts_resp.status_code != 200:
            print(f"❌ Failed to fetch concepts: {concepts_resp.text}")
            return False
            
        concepts_data = concepts_resp.json()
        concepts = concepts_data.get('concepts', concepts_data)
        concept_map = {c["name"]: c["concept_id"] for c in concepts}
        
        print(f"✅ Resolved {len(concept_map)} concept IDs")
        for name, cid in concept_map.items():
            print(f"   📝 {name} -> {cid}")
    except Exception as e:
        print(f"❌ Error fetching concepts: {e}")
        return False

    # 3. Sync to Neo4j
    print(f"\n🌐 Connecting to Neo4j...")
    try:
        URI = "bolt://localhost:7687"
        AUTH = ("neo4j", "neo4j_secure_password_2024")

        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                print("✅ Neo4j connection established!")
                
                # Clear existing learning paths (optional - comment out if you want to preserve)
                print("\n🧹 Clearing existing LearningPath nodes...")
                session.run("MATCH (lp:LearningPath) DETACH DELETE lp")
                
                successful_paths = 0
                total_concepts_linked = 0
                
                # Create Learning Path nodes and relationships
                for path in GRAPH_PATHS:
                    print(f"\n📦 Creating Learning Path: {path['title']}")
                    
                    # A. Create the Learning Path Node
                    query_create_path = """
                    MERGE (lp:LearningPath {title: $title})
                    SET lp.difficulty = $difficulty,
                        lp.category = $category,
                        lp.estimated_hours = $estimated_hours,
                        lp.created_at = datetime()
                    RETURN lp.title, lp.difficulty
                    """
                    
                    result = session.run(query_create_path, 
                                       title=path['title'], 
                                       difficulty=path['difficulty'],
                                       category=path['category'],
                                       estimated_hours=path['estimated_hours'])
                    
                    path_record = result.single()
                    if path_record:
                        print(f"   ✅ Created: {path_record['lp.title']} ({path_record['lp.difficulty']})")
                        
                        # B. Link Path to Concepts
                        concepts_linked = 0
                        for concept_name in path['contains']:
                            concept_id = concept_map.get(concept_name)
                            if concept_id:
                                print(f"   🔗 Linking -> {concept_name}")
                                
                                query_link = """
                                MATCH (lp:LearningPath {title: $title})
                                MATCH (c:Concept {concept_id: $cid})
                                MERGE (lp)-[:CONTAINS {sequence_order: $order}]->(c)
                                """
                                session.run(query_link, 
                                          title=path['title'], 
                                          cid=concept_id,
                                          order=path['contains'].index(concept_name) + 1)
                                concepts_linked += 1
                            else:
                                print(f"   ⚠️  Concept not found: {concept_name}")
                        
                        print(f"   📊 Linked {concepts_linked} concepts")
                        total_concepts_linked += concepts_linked
                        successful_paths += 1
                    else:
                        print(f"   ❌ Failed to create path: {path['title']}")
                
                print("\n" + "=" * 60)
                print("🎉 LEARNING PATHS SYNC COMPLETE!")
                print(f"   ✅ Learning paths created: {successful_paths}")
                print(f"   🔗 Total concept links: {total_concepts_linked}")
                print(f"   📋 Average concepts per path: {total_concepts_linked/successful_paths if successful_paths > 0 else 0:.1f}")
                
                # Verify the sync
                print("\n🔍 Verifying sync in Neo4j...")
                verify_query = """
                MATCH (lp:LearningPath)-[r:CONTAINS]->(c:Concept)
                RETURN lp.title, lp.difficulty, c.name as concept_name, r.sequence_order
                ORDER BY lp.title, r.sequence_order
                """
                
                verify_result = session.run(verify_query)
                records = list(verify_result)
                
                if records:
                    print(f"✅ Verified {len(records)} path-concept relationships:")
                    for record in records:
                        print(f"   {record['lp.title']} -> {record['concept_name']} (order: {record['r.sequence_order']})")
                else:
                    print("⚠️  No relationships found - check sync")
                
                return True
                
    except Exception as e:
        print(f"❌ Neo4j sync error: {e}")
        return False

def sync_user_progress_to_neo4j():
    """Sync user progress to Neo4j as relationships"""
    print("\n🚀 Syncing User Progress to Neo4j...")
    print("=" * 50)

    # 1. Get user progress from API
    try:
        auth_resp = requests.post(f"{API_URL}/auth/login", 
                                 json={"username": USERNAME, "password": PASSWORD})
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        progress_resp = requests.get(f"{API_URL}/progress/", headers=headers)
        if progress_resp.status_code != 200:
            print(f"❌ Failed to fetch progress: {progress_resp.text}")
            return False
            
        progress_data = progress_resp.json()
        concept_progress = progress_data.get('concept_progress', [])
        
        print(f"✅ Found {len(concept_progress)} concept progress records")
        
    except Exception as e:
        print(f"❌ Error fetching progress: {e}")
        return False

    # 2. Sync to Neo4j
    try:
        URI = "bolt://localhost:7687"
        AUTH = ("neo4j", "neo4j_secure_password_2024")

        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                print("✅ Connected to Neo4j for user progress sync")
                
                # Clear existing user relationships
                print("🧹 Clearing existing user relationships...")
                session.run("MATCH (u:User)-[r]->(:Concept) DELETE r")
                
                # Create User node and relationships
                user_id = "cavin_admin"  # From our test user
                
                query_create_user = """
                MERGE (u:User {username: $username})
                SET u.first_name = 'Cavin',
                    u.last_name = 'Otieno',
                    u.created_at = datetime()
                RETURN u.username
                """
                
                session.run(query_create_user, username=user_id)
                print(f"✅ Created/updated user: {user_id}")
                
                # Create progress relationships
                for progress in concept_progress:
                    if progress['status'] in ['completed', 'in_progress']:
                        concept_name = progress['name'].lower().replace(' ', '_')
                        
                        print(f"🔗 Creating relationship: {user_id} --[{progress['status']}]--> {concept_name}")
                        
                        query_progress_rel = """
                        MATCH (u:User {username: $username})
                        MATCH (c:Concept {name: $concept_name})
                        MERGE (u)-[r:HAS_PROGRESS {status: $status, progress_percent: $progress}]->(c)
                        SET r.updated_at = datetime()
                        RETURN u.username, type(r), c.name
                        """
                        
                        session.run(query_progress_rel,
                                  username=user_id,
                                  concept_name=concept_name,
                                  status=progress['status'],
                                  progress=progress['progress'])
                
                # Verify user progress sync
                verify_user_query = """
                MATCH (u:User {username: $username})-[r:HAS_PROGRESS]->(c:Concept)
                RETURN u.username, type(r), c.name, r.progress_percent, r.status
                ORDER BY r.progress_percent DESC
                """
                
                verify_result = session.run(verify_user_query, username=user_id)
                user_records = list(verify_result)
                
                print(f"\n✅ Verified {len(user_records)} user progress relationships:")
                for record in user_records:
                    print(f"   {record['u.username']} --[{record['r.status']}]--> {record['c.name']} ({record['r.progress_percent']}%)")
                
                return True
                
    except Exception as e:
        print(f"❌ User progress sync error: {e}")
        return False

def demonstrate_graph_power():
    """Demonstrate the power of graph queries"""
    print("\n🧠 Demonstrating Graph Query Power...")
    print("=" * 50)

    try:
        URI = "bolt://localhost:7687"
        AUTH = ("neo4j", "neo4j_secure_password_2024")

        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                
                # Query 1: Show all paths that contain Machine Learning
                print("📋 Query 1: All learning paths that contain 'Machine Learning'")
                query1 = """
                MATCH (lp:LearningPath)-[:CONTAINS]->(c:Concept)
                WHERE c.name CONTAINS 'machine_learning'
                RETURN lp.title, lp.difficulty, c.name as concept
                """
                
                result1 = session.run(query1)
                records1 = list(result1)
                
                if records1:
                    print("   ✅ Results:")
                    for record in records1:
                        print(f"      📚 {record['lp.title']} -> {record['concept']}")
                else:
                    print("   ⚠️  No paths found containing Machine Learning")
                
                # Query 2: Show shared concepts between paths
                print("\n🔗 Query 2: Concepts shared between multiple paths")
                query2 = """
                MATCH (c:Concept)<-[:CONTAINS]-(lp:LearningPath)
                WITH c, collect(lp.title) as paths, count(lp) as path_count
                WHERE path_count > 1
                RETURN c.name, paths, path_count
                ORDER BY path_count DESC
                """
                
                result2 = session.run(query2)
                records2 = list(result2)
                
                if records2:
                    print("   ✅ Results:")
                    for record in records2:
                        print(f"      🔄 {record['c.name']} appears in {record['path_count']} paths: {', '.join(record['paths'])}")
                else:
                    print("   ⚠️  No shared concepts found")
                
                # Query 3: User learning journey
                print("\n👤 Query 3: User's learning journey and recommendations")
                query3 = """
                MATCH (u:User {username: 'cavin_admin'})-[r:HAS_PROGRESS]->(c:Concept)
                OPTIONAL MATCH (c)<-[:CONTAINS]-(lp:LearningPath)
                RETURN u.username, c.name as concept, r.status, r.progress_percent, 
                       collect(lp.title) as available_in_paths
                ORDER BY r.progress_percent DESC
                """
                
                result3 = session.run(query3)
                records3 = list(result3)
                
                if records3:
                    print("   ✅ User's Learning Status:")
                    for record in records3:
                        paths_str = ', '.join([p for p in record['available_in_paths'] if p]) if record['available_in_paths'] else "No paths"
                        print(f"      📖 {record['concept']}: {record['r.status']} ({record['r.progress_percent']}%) - Available in: {paths_str}")
                else:
                    print("   ⚠️  No user progress found")
                
                print("\n🎯 This is the power of Neo4j - complex relationships with simple queries!")
                
    except Exception as e:
        print(f"❌ Graph demonstration error: {e}")

def main():
    """Main function to sync all graph data"""
    print("🧠 POLYGLOT PERSISTENCE - GRAPH SYNC")
    print("Syncing graph-worthy data to Neo4j...")
    print("=" * 60)
    
    # Step 1: Sync Learning Paths
    if sync_learning_paths_to_neo4j():
        print("\n✅ Learning paths synced successfully!")
    else:
        print("\n❌ Learning paths sync failed!")
        return False
    
    # Step 2: Sync User Progress
    if sync_user_progress_to_neo4j():
        print("\n✅ User progress synced successfully!")
    else:
        print("\n❌ User progress sync failed!")
        return False
    
    # Step 3: Demonstrate graph power
    demonstrate_graph_power()
    
    print("\n" + "=" * 60)
    print("🎉 GRAPH SYNC COMPLETE!")
    print("\n🌐 Your Neo4j browser queries:")
    print("   # Show all paths and their concepts")
    print("   MATCH (lp:LearningPath)-[:CONTAINS]->(c:Concept) RETURN lp, c")
    print("")
    print("   # Show user's learning journey")
    print("   MATCH (u:User {username: 'cavin_admin'})-[r:HAS_PROGRESS]->(c:Concept) RETURN u, r, c")
    print("")
    print("   # Find paths containing specific concept")
    print("   MATCH (lp:LearningPath)-[:CONTAINS]->(c:Concept {name: 'machine_learning'}) RETURN lp")
    
    return True

if __name__ == "__main__":
    main()