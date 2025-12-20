#!/usr/bin/env python3
"""
Direct Dual-Write Test Script
This script directly tests the PostgreSQL and Neo4j connections
and demonstrates the dual-write pattern.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_postgresql_connection():
    """Test PostgreSQL connection and create a sample concept"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="jeseci_learning_academy", 
            user="jeseci_user",
            password="secure_password_123"
        )
        
        print("✅ PostgreSQL connection successful!")
        
        # Test creating a concept directly
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Insert test concept
        test_concept = {
            "name": "test_dual_write",
            "display_name": "Test Dual Write Concept",
            "description": "Testing dual-write functionality between PostgreSQL and Neo4j",
            "category": "Testing",
            "domain": "Development",
            "difficulty_level": "beginner"
        }
        
        insert_query = """
        INSERT INTO concepts (
            name, display_name, description, category, domain, difficulty_level
        ) VALUES (%(name)s, %(display_name)s, %(description)s, %(category)s, %(domain)s, %(difficulty_level)s)
        ON CONFLICT (name) DO NOTHING
        RETURNING concept_id
        """
        
        cursor.execute(insert_query, test_concept)
        result = cursor.fetchone()
        
        if result:
            concept_id = result['concept_id']
            print(f"✅ Concept created in PostgreSQL with ID: {concept_id}")
            conn.commit()
        else:
            concept_id = cursor.execute("SELECT concept_id FROM concepts WHERE name = %s", (test_concept["name"],))
            concept_id = cursor.fetchone()['concept_id']
            print(f"⚠️  Concept already exists in PostgreSQL with ID: {concept_id}")
        
        cursor.close()
        conn.close()
        return concept_id
        
    except Exception as e:
        print(f"❌ PostgreSQL test failed: {e}")
        return None

def test_neo4j_connection():
    """Test Neo4j connection and create a sample node"""
    try:
        from neo4j import GraphDatabase
        
        # Connect to Neo4j
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "neo4j_secure_password_2024")
        )
        
        print("✅ Neo4j connection successful!")
        
        with driver.session() as session:
            # Test creating a concept node
            test_query = """
            MERGE (c:Concept {name: $name})
            ON CREATE SET c.created_at = datetime()
            SET c.display_name = $display_name,
                c.description = $description,
                c.category = $category
            RETURN c
            """
            
            test_data = {
                "name": "test_dual_write",
                "display_name": "Test Dual Write Concept",
                "description": "Testing dual-write functionality between PostgreSQL and Neo4j",
                "category": "Testing"
            }
            
            result = session.run(test_query, test_data)
            record = result.single()
            
            if record:
                print(f"✅ Concept node created in Neo4j: {record['c']['name']}")
            else:
                print("⚠️  Concept node already exists in Neo4j")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Neo4j test failed: {e}")
        return False

def demonstrate_dual_write():
    """Demonstrate the dual-write pattern"""
    print("🚀 Starting Dual-Write Test")
    print("=" * 50)
    
    # Test PostgreSQL
    print("\n1️⃣  Testing PostgreSQL...")
    pg_result = test_postgresql_connection()
    
    # Test Neo4j
    print("\n2️⃣  Testing Neo4j...")
    neo4j_result = test_neo4j_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DUAL-WRITE TEST SUMMARY:")
    print(f"   PostgreSQL: {'✅ Connected' if pg_result else '❌ Failed'}")
    print(f"   Neo4j:      {'✅ Connected' if neo4j_result else '❌ Failed'}")
    
    if pg_result and neo4j_result:
        print("\n🎉 DUAL-WRITE ARCHITECTURE READY!")
        print("   Both databases are accessible and functional.")
        print("   Your API can successfully orchestrate writes to both PostgreSQL and Neo4j.")
    else:
        print("\n⚠️  Some database connections failed.")
        print("   Check database services and connection details.")

if __name__ == "__main__":
    demonstrate_dual_write()