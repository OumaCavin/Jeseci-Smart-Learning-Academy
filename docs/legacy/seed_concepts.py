import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "cavin_admin"
PASSWORD = "secure_password_123"

# Your Data
concepts_data = {
  "machine_learning": {
    "name": "machine_learning",
    "display_name": "Machine Learning",
    "description": "A subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
    "detailed_description": "Machine Learning is a powerful branch of artificial intelligence that focuses on building systems that can learn from and make predictions or decisions based on data...",
    "category": "Artificial Intelligence",
    "subcategory": "Machine Learning",
    "domain": "Computer Science",
    "difficulty_level": "advanced",
    "complexity_score": 9.0,
    "cognitive_load": 9.2,
    "key_terms": ["algorithm", "training data", "model", "prediction", "feature", "label", "supervised learning", "unsupervised learning", "neural network", "gradient descent", "overfitting"],
    "synonyms": ["ML", "Statistical Learning", "Pattern Recognition"],
    "learning_objectives": ["Understand the difference between supervised, unsupervised, and reinforcement learning", "Learn to prepare and preprocess data", "Implement basic algorithms", "Evaluate model performance", "Apply ML to solve problems"],
    "practical_applications": ["Email spam detection", "Recommendation systems", "Image recognition", "NLP", "Fraud detection"],
    "real_world_examples": ["Netflix recommendation engine", "Google Photos tagging", "Amazon pricing", "Spotify playlists", "Tesla autopilot"],
    "common_misconceptions": ["ML can solve anything", "Complex models are always better", "ML replaces humans", "Data quality doesn't matter", "All ML is the same"]
  },
  "data_structures": {
    "name": "data_structures",
    "display_name": "Data Structures",
    "description": "Specialized formats for organizing, storing, and managing data efficiently in computer systems.",
    "detailed_description": "Data structures are fundamental building blocks in computer science that define how data is organized, stored, and manipulated within a program...",
    "category": "Programming Fundamentals",
    "subcategory": "Data Management",
    "domain": "Computer Science",
    "difficulty_level": "intermediate",
    "complexity_score": 6.8,
    "cognitive_load": 7.5,
    "key_terms": ["array", "linked list", "stack", "queue", "tree", "graph", "hash table", "heap", "binary search", "traversal", "complexity"],
    "synonyms": ["Data Organization", "Information Structures", "Data Models"],
    "learning_objectives": ["Compare data structures", "Implement from scratch", "Analyze complexity", "Choose appropriate structures", "Understand impact on efficiency"],
    "practical_applications": ["Database indexing", "Memory management", "Network routing", "Compilers", "Game development"],
    "real_world_examples": ["Browser history (Stack)", "Print job management (Queue)", "File directories (Tree)", "Social networks (Graph)", "Database indexes (B-trees)"],
    "common_misconceptions": ["Arrays always faster", "Complex always better", "All have same complexity", "Only for CS theory", "Must implement from scratch"]
  },
  "web_development": {
    "name": "web_development",
    "display_name": "Web Development",
    "description": "The process of creating websites and web applications using various technologies and frameworks.",
    "detailed_description": "Web development encompasses the entire process of building websites and web applications...",
    "category": "Software Development",
    "subcategory": "Web Technologies",
    "domain": "Computer Science",
    "difficulty_level": "beginner",
    "complexity_score": 5.5,
    "cognitive_load": 6.0,
    "key_terms": ["HTML", "CSS", "JavaScript", "frontend", "backend", "responsive design", "API", "framework", "database", "server", "client"],
    "synonyms": ["Website Development", "Web Application Development", "Frontend/Backend"],
    "learning_objectives": ["Build responsive sites", "Understand client-server", "Create interactive UI", "Integrate APIs", "Deploy apps"],
    "practical_applications": ["E-commerce", "Social media", "Online learning", "Corporate portals", "Productivity tools"],
    "real_world_examples": ["Amazon", "Facebook", "Google", "Netflix", "Airbnb"],
    "common_misconceptions": ["Only about looks", "Must know everything first", "Web dev is dying", "Backend/Frontend are separate", "Mobile replacing web"]
  }
}

def seed_database():
    print("🚀 Starting Database Seed...")

    # 1. Login to get Token
    print("🔐 Authenticating...")
    auth_resp = requests.post(f"{API_URL}/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if auth_resp.status_code != 200:
        print(f"❌ Login failed: {auth_resp.text}")
        return

    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated successfully!")

    # 2. Iterate and Create Concepts
    for key, data in concepts_data.items():
        print(f"\n📤 Processing: {data['display_name']}...")
        
        # Check if exists first (optional, but good practice)
        check = requests.get(f"{API_URL}/concepts/", params={"query": data['name']}, headers=headers)
        
        # Simple create call
        resp = requests.post(f"{API_URL}/concepts/", json=data, headers=headers)
        
        if resp.status_code in [200, 201]:
            print(f"   ✅ Created in Postgres & Neo4j")
            print(f"   🆔 ID: {resp.json()['concept_id']}")
        elif resp.status_code == 400 and "already exists" in resp.text:
            print(f"   ⚠️  Skipping (Already exists)")
        else:
            print(f"   ❌ Failed: {resp.text}")

    print("\n✨ Seeding Complete!")

if __name__ == "__main__":
    seed_database()