#!/usr/bin/env python3
"""
Simple Neo4j sync script - runs independently
"""
import os
import sys
from neo4j import GraphDatabase
from sqlalchemy.orm import Session
from config.database import SessionLocal
from database.models.sqlite_models import Concept, LearningPath, LearningPathConcept

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j_secure_password_2024"

def get_neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def clear_graph(tx):
    print("🧹 Clearing existing graph data...")
    tx.run("MATCH (n) DETACH DELETE n")

def create_constraints(tx):
    print("🔒 Creating constraints...")
    tx.run("CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE")

def create_concept_node(tx, concept):
    query = """
    MERGE (c:Concept {concept_id: $concept_id})
    SET c.name = $name,
        c.display_name = $display_name,
        c.category = $category,
        c.difficulty = $difficulty,
        c.domain = $domain,
        c.description = $description
    """
    tx.run(query, 
           concept_id=str(concept.concept_id),
           name=concept.name,
           display_name=concept.display_name,
           category=concept.category,
           difficulty=concept.difficulty_level,
           domain=concept.domain,
           description=concept.description)
    print(f"   ✅ Created Node: {concept.display_name}")

def create_path_relationships(tx, path_name, sequences):
    sorted_seq = sorted(sequences, key=lambda x: x[1])
    print(f"   🔗 Linking '{path_name}': {len(sorted_seq)} concepts")
    
    for i in range(len(sorted_seq) - 1):
        curr_id = sorted_seq[i][0]
        next_id = sorted_seq[i+1][0]
        
        query = """
        MATCH (a:Concept {concept_id: $curr_id})
        MATCH (b:Concept {concept_id: $next_id})
        MERGE (a)-[r:NEXT_IN_PATH {path_name: $path_name}]->(b)
        """
        tx.run(query, curr_id=curr_id, next_id=next_id, path_name=path_name)

if __name__ == "__main__":
    print("🔄 Starting Neo4j Sync...")
    
    # Connect to databases
    sql_db = SessionLocal()
    neo_driver = get_neo4j_driver()
    
    try:
        with neo_driver.session() as session:
            # Clear and setup graph
            session.execute_write(clear_graph)
            session.execute_write(create_constraints)
            
            # Sync concepts
            concepts = sql_db.query(Concept).all()
            print(f"\n📦 Syncing {len(concepts)} concepts to Neo4j...")
            
            for concept in concepts:
                session.execute_write(create_concept_node, concept)
            
            # Sync learning paths
            paths = sql_db.query(LearningPath).all()
            print(f"\n🛤️  Syncing {len(paths)} learning paths...")
            
            for path in paths:
                path_concepts = sql_db.query(LearningPathConcept).filter(
                    LearningPathConcept.path_id == path.path_id
                ).all()
                
                if path_concepts:
                    sequences = [(pc.concept_id, pc.sequence_order) for pc in path_concepts]
                    session.execute_write(create_path_relationships, path.name, sequences)
        
        print("\n✅ Neo4j Sync Complete!")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sql_db.close()
        neo_driver.close()