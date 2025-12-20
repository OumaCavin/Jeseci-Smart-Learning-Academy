#!/usr/bin/env python3
"""
API Mock Test - Demonstrates Dual-Write Pattern
This simulates the API responses for testing purposes
"""

import json
from datetime import datetime

def simulate_api_responses():
    """Simulate the expected API responses for dual-write testing"""
    
    print("🚀 DUAL-WRITE API SIMULATION")
    print("=" * 60)
    
    # 1. Authentication Response
    print("\n1️⃣  AUTHENTICATION REQUEST")
    print("POST /api/v1/auth/login")
    auth_request = {
        "username": "cavin_admin",
        "password": "secure_password_123"
    }
    print(f"Request: {json.dumps(auth_request, indent=2)}")
    
    auth_response = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "cavin_admin",
            "email": "cavin@jeseci.com",
            "first_name": "Cavin",
            "last_name": "Otieno"
        }
    }
    print(f"Response: {json.dumps(auth_response, indent=2)}")
    
    # 2. Concept Creation Requests
    concepts = [
        {
            "name": "machine_learning",
            "display_name": "Machine Learning",
            "description": "A subset of artificial intelligence that enables computers to learn...",
            "category": "Artificial Intelligence",
            "subcategory": "Machine Learning", 
            "domain": "Computer Science",
            "difficulty_level": "advanced",
            "complexity_score": 9.0,
            "cognitive_load": 9.2,
            "key_terms": ["algorithm", "training data", "model", "prediction"]
        },
        {
            "name": "data_structures",
            "display_name": "Data Structures", 
            "description": "Specialized formats for organizing, storing, and managing data...",
            "category": "Programming Fundamentals",
            "subcategory": "Data Management",
            "domain": "Computer Science", 
            "difficulty_level": "intermediate",
            "complexity_score": 6.8,
            "cognitive_load": 7.5,
            "key_terms": ["array", "linked list", "stack", "queue", "tree"]
        },
        {
            "name": "web_development",
            "display_name": "Web Development",
            "description": "The process of creating websites and web applications...", 
            "category": "Software Development",
            "subcategory": "Web Technologies",
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 5.5,
            "cognitive_load": 6.0,
            "key_terms": ["HTML", "CSS", "JavaScript", "frontend", "backend"]
        }
    ]
    
    for i, concept in enumerate(concepts, 1):
        print(f"\n{i}️⃣  CONCEPT CREATION REQUEST")
        print(f"POST /api/v1/concepts/")
        print(f"Request: {json.dumps(concept, indent=2)}")
        
        # Simulate successful dual-write response
        concept_response = {
            "concept_id": f"concept-{i}-uuid",
            "name": concept["name"],
            "display_name": concept["display_name"], 
            "description": concept["description"],
            "category": concept["category"],
            "subcategory": concept.get("subcategory"),
            "domain": concept["domain"],
            "difficulty_level": concept["difficulty_level"],
            "complexity_score": concept["complexity_score"],
            "cognitive_load": concept["cognitive_load"],
            "key_terms": concept["key_terms"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        print(f"Response: {json.dumps(concept_response, indent=2)}")
        print("✅ Dual-write completed: PostgreSQL + Neo4j")
    
    # 3. Verification Requests
    print(f"\n4️⃣  VERIFICATION REQUESTS")
    
    # Get all concepts
    print("\nGET /api/v1/concepts/")
    concepts_response = {
        "concepts": [
            {
                "concept_id": "concept-1-uuid",
                "name": "machine_learning",
                "display_name": "Machine Learning",
                "category": "Artificial Intelligence",
                "domain": "Computer Science", 
                "difficulty_level": "advanced"
            },
            {
                "concept_id": "concept-2-uuid", 
                "name": "data_structures",
                "display_name": "Data Structures",
                "category": "Programming Fundamentals",
                "domain": "Computer Science",
                "difficulty_level": "intermediate"
            },
            {
                "concept_id": "concept-3-uuid",
                "name": "web_development", 
                "display_name": "Web Development",
                "category": "Software Development",
                "domain": "Computer Science",
                "difficulty_level": "beginner"
            }
        ],
        "total": 3,
        "page": 1,
        "limit": 20
    }
    print(f"Response: {json.dumps(concepts_response, indent=2)}")
    
    print(f"\n" + "=" * 60)
    print("🎉 DUAL-WRITE SIMULATION COMPLETE!")
    print("\nExpected behavior:")
    print("✅ 3 concepts created in PostgreSQL")
    print("✅ 3 concept nodes created in Neo4j")
    print("✅ Frontend can fetch and display all concepts")
    print("✅ Both databases remain synchronized")

if __name__ == "__main__":
    simulate_api_responses()