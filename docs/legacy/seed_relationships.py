import requests

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "cavin_admin"
PASSWORD = "secure_password_123"

# Define the logical links between concepts
# Format: (Source Concept, Relationship Type, Target Concept)
RELATIONSHIPS = [
    # Hierarchy relationships
    ("machine_learning", "PART_OF", "computer_science"),
    ("data_structures", "PART_OF", "computer_science"), 
    ("web_development", "PART_OF", "computer_science"),
    ("object_oriented_programming", "PART_OF", "programming"),
    
    # Dependencies (Prerequisites)
    ("machine_learning", "PREREQUISITE", "data_structures"),
    ("data_structures", "PREREQUISITE", "programming"),
    ("web_development", "PREREQUISITE", "programming"),
    ("object_oriented_programming", "PREREQUISITE", "data_structures"),
    
    # Related concepts (can be learned in parallel)
    ("web_development", "RELATED_TO", "data_structures"),
    ("machine_learning", "RELATED_TO", "object_oriented_programming"),
    ("programming", "RELATED_TO", "computer_science"),
    
    # Advanced relationships
    ("machine_learning", "BUILDS_UPON", "programming"),
    ("data_structures", "BUILDS_UPON", "programming"),
    ("web_development", "BUILDS_UPON", "programming"),
]

def seed_relationships():
    print("🚀 Seeding Knowledge Graph Relationships...")
    print("=" * 60)

    # 1. Login
    print("🔐 Authenticating...")
    auth_resp = requests.post(f"{API_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
    if auth_resp.status_code != 200:
        print(f"❌ Login failed: {auth_resp.text}")
        return
    
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")

    # 2. Get Concepts and build lookup map
    print("\n🔍 Fetching concepts...")
    try:
        concepts_resp = requests.get(f"{API_URL}/concepts/", headers=headers)
        if concepts_resp.status_code != 200:
            print(f"❌ Failed to fetch concepts: {concepts_resp.text}")
            return
            
        all_concepts = concepts_resp.json()
        if isinstance(all_concepts, dict) and 'concepts' in all_concepts:
            all_concepts = all_concepts['concepts']
            
        print(f"✅ Found {len(all_concepts)} concepts")
    except Exception as e:
        print(f"❌ Error fetching concepts: {e}")
        return
    
    # Build concept name to ID map
    concept_map = {}
    for concept in all_concepts:
        concept_map[concept["name"]] = concept["concept_id"]
        print(f"   📝 {concept['name']} -> {concept['concept_id']}")

    print(f"\n🔗 Creating {len(RELATIONSHIPS)} relationships...")
    successful_links = 0
    failed_links = 0

    # 3. Create Relationships
    for source_name, rel_type, target_name in RELATIONSHIPS:
        source_id = concept_map.get(source_name)
        target_id = concept_map.get(target_name)

        if not source_id or not target_id:
            print(f"⚠️  Skipping {source_name} --[{rel_type}]--> {target_name}")
            print(f"    Missing: {source_name if not source_id else ''} {target_name if not target_id else ''}")
            failed_links += 1
            continue

        print(f"🔗 Linking: {source_name} --[{rel_type}]--> {target_name}")
        
        try:
            resp = requests.post(
                f"{API_URL}/concepts/{source_id}/relations",
                json={
                    "target_concept_id": target_id,
                    "relationship_type": rel_type
                },
                headers=headers
            )
            
            if resp.status_code == 200:
                print("   ✅ Success")
                successful_links += 1
            else:
                print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
                failed_links += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_links += 1

    print("\n" + "=" * 60)
    print(f"🎉 RELATIONSHIP SEEDING COMPLETE!")
    print(f"   ✅ Successful links: {successful_links}")
    print(f"   ⚠️  Failed/skipped links: {failed_links}")
    
    if successful_links > 0:
        print(f"\n🔍 Verify in Neo4j Browser:")
        print(f"   MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name LIMIT 10")
        print(f"\n🌐 Your knowledge graph is now connected!")
    else:
        print(f"\n⚠️  No relationships created. Check concept names and API availability.")

if __name__ == "__main__":
    seed_relationships()