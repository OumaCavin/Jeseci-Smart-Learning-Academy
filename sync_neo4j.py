import sys
import os
from neo4j import GraphDatabase
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import SessionLocal
from database.models.sqlite_models import Concept, LearningPath, LearningPathConcept

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j_secure_password_2024"

def get_db_connection():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return driver

def clear_graph(tx):
    print("🧹 Clearing existing graph data...")
    tx.run("MATCH (n) DETACH DELETE n")

def create_constraints(tx):
    print("🔒 Creating constraints...")
    # Ensure Concept IDs are unique
    tx.run("CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE")
    # Ensure Path IDs are unique
    tx.run("CREATE CONSTRAINT path_id_unique IF NOT EXISTS FOR (p:LearningPath) REQUIRE p.path_id IS UNIQUE")

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
           concept_id=concept.concept_id,
           name=concept.name,
           display_name=concept.display_name,
           category=concept.category,
           difficulty=concept.difficulty_level,
           domain=concept.domain,
           description=concept.description)
    print(f"   Created Node: {concept.display_name}")

def create_path_relationships(tx, path_name, sequences):
    """
    Creates a linked list of concepts for a learning path.
    sequences is a list of tuples: (concept_id, order)
    """
    # Sort by sequence order
    sorted_seq = sorted(sequences, key=lambda x: x[1])
    
    print(f"   🔗 Linking '{path_name}': {len(sorted_seq)} steps")
    
    for i in range(len(sorted_seq) - 1):
        curr_id = sorted_seq[i][0]
        next_id = sorted_seq[i+1][0]
        
        query = """
        MATCH (a:Concept {concept_id: $curr_id})
        MATCH (b:Concept {concept_id: $next_id})
        MERGE (a)-[r:NEXT_IN_PATH {path_name: $path_name}]->(b)
        """
        tx.run(query, curr_id=curr_id, next_id=next_id, path_name=path_name)

def sync_data():
    # 1. Connect to both DBs
    sql_db = SessionLocal()
    neo_driver = get_db_connection()
    
    try:
        print("🔄 Starting Sync: PostgreSQL -> Neo4j")
        
        with neo_driver.session() as session:
            # 2. Reset Graph
            session.execute_write(clear_graph)
            session.execute_write(create_constraints)
            
            # 3. Sync Concepts (Nodes)
            concepts = sql_db.query(Concept).all()
            print(f"\n📦 Found {len(concepts)} concepts in Postgres.")
            
            for concept in concepts:
                session.execute_write(create_concept_node, concept)
            
            # 4. Sync Learning Paths (Relationships)
            # We want to link concepts A->B->C based on the learning path order
            paths = sql_db.query(LearningPath).all()
            print(f"\n🛤️  Found {len(paths)} Learning Paths.")
            
            for path in paths:
                # Get all concepts for this path
                path_concepts = sql_db.query(LearningPathConcept).filter(
                    LearningPathConcept.path_id == path.path_id
                ).all()
                
                if path_concepts:
                    # Extract (concept_id, sequence_order) tuples
                    sequences = [(pc.concept_id, pc.sequence_order) for pc in path_concepts]
                    session.execute_write(create_path_relationships, path.name, sequences)
        
        print("\n✅ Sync Complete! Your graph is now populated.")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
    finally:
        sql_db.close()
        neo_driver.close()

if __name__ == "__main__":
    sync_data()