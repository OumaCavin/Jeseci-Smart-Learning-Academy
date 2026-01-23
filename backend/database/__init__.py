"""
Database Initialization and Export
Connects the fixed PostgresManager and Neo4jManager to the rest of the app.
"""
import os
import sys
import logging

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# --- CRITICAL: Import the FIXED managers from the separate files ---
# This pulls in the type-casting fix for Postgres and transaction handling for Neo4j
from .postgres_manager import PostgresManager, get_postgres_manager
from .neo4j_manager import Neo4jManager, neo4j_manager

# Set up logging
logger = logging.getLogger(__name__)
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")

# =============================================================================
# Dual Write Manager (Syncs Postgres <-> Neo4j)
# =============================================================================
class DualWriteManager:
    """
    Manages dual-write operations to both PostgreSQL and Neo4j.
    Uses the robust singleton instances from the separate modules.
    """
    
    def __init__(self):
        self.pg_manager = get_postgres_manager()
        self.neo4j_manager = neo4j_manager
    
    def sync_concept_to_neo4j(self, concept_id: str, name: str, display_name: str, 
                               category: str, difficulty_level: str, description: str = ""):
        query = """
        MERGE (c:Concept {concept_id: $concept_id})
        SET c.name = $name,
            c.display_name = $display_name,
            c.category = $category,
            c.difficulty_level = $difficulty_level,
            c.description = $description,
            c.updated_at = timestamp()
        RETURN c
        """
        return self.neo4j_manager.execute_write(query, {
            "concept_id": concept_id,
            "name": name,
            "display_name": display_name,
            "category": category,
            "difficulty_level": difficulty_level,
            "description": description
        })
    
    def create_concept_relationship(self, source_id: str, target_id: str, 
                                     relationship_type: str, strength: int = 1):
        query = f"""
        MATCH (a:Concept {{concept_id: $source_id}})
        MATCH (b:Concept {{concept_id: $target_id}})
        MERGE (a)-[r:{relationship_type}]->(b)
        SET r.strength = $strength,
            r.created_at = timestamp()
        RETURN a.name, type(r), b.name
        """
        return self.neo4j_manager.execute_write(query, {
            "source_id": source_id,
            "target_id": target_id,
            "strength": strength
        })
    
    def get_learning_recommendations(self, user_id: str, completed_concept_ids: list, limit: int = 5):
        query = """
        MATCH (c:Concept)
        WHERE NOT c.concept_id IN $completed_ids
        OPTIONAL MATCH (c)-[:PREREQUISITE|RELATED_TO]->(prereq:Concept)
        WITH c, COUNT(prereq) as prereq_count
        WHERE prereq_count = 0 OR prereq_count <= 2
        RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
               c.category AS category, c.difficulty_level AS difficulty,
               c.description AS description
        LIMIT $limit
        """
        return self.neo4j_manager.execute_query(query, {
            "completed_ids": completed_concept_ids,
            "limit": limit
        })

    def get_concept_graph(self, concept_id: str, depth: int = 2):
        query = f"""
        MATCH path = (c:Concept {{concept_id: $concept_id}})-[*1..{depth}]-(related:Concept)
        WITH c, collect(DISTINCT related) as neighbors
        RETURN c,
               [n IN neighbors | {{id: n.concept_id, name: n.name, 
                   display_name: n.display_name, category: n.category}}] as related
        """
        return self.neo4j_manager.execute_query(query, {"concept_id": concept_id})

# Create global instance
dual_write_manager = DualWriteManager()

# =============================================================================
# Global Accessor Functions (Backward Compatibility)
# =============================================================================

# Alias the new classes to match old names if needed
PostgresConnectionManager = PostgresManager
Neo4jConnectionManager = Neo4jManager

def get_db_connection():
    """Get a raw connection from the pool"""
    return get_postgres_manager().get_connection()

def get_dual_write_manager():
    return dual_write_manager

def get_neo4j_manager():
    return neo4j_manager

# =============================================================================
# Database Migration Management
# =============================================================================
def run_database_migrations():
    """Run pending SQL migrations"""
    import re
    
    # Path handling to find migrations folder relative to this file
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    
    if not os.path.exists(migrations_dir):
        logger.warning(f"Migrations directory not found at {migrations_dir}")
        return False
    
    migration_files = sorted([
        f for f in os.listdir(migrations_dir) 
        if f.endswith('.sql') and re.match(r'^\d+_', f)
    ])
    
    pg_manager = get_postgres_manager()
    conn = pg_manager.get_connection()
    
    try:
        cursor = conn.cursor()
        # Create migrations table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
        cursor.execute(f"SELECT migration_name FROM {DB_SCHEMA}.schema_migrations")
        executed = {row[0] for row in cursor.fetchall()}
        
        migrations_run = 0
        for migration_file in migration_files:
            if migration_file not in executed:
                logger.info(f"Running migration: {migration_file}")
                with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                    sql = f.read()
                cursor.execute(sql)
                cursor.execute(f"INSERT INTO {DB_SCHEMA}.schema_migrations (migration_name) VALUES (%s)", (migration_file,))
                conn.commit()
                migrations_run += 1
                
        if migrations_run > 0:
            logger.info(f"Completed {migrations_run} migration(s)")
        else:
            logger.info("No pending migrations - database is up to date")
        
        return True
    except Exception as e:
        logger.error(f"Migration error: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: pg_manager.return_connection(conn)

# Testimonials functionality (Preserving your existing import)
try:
    from testimonials_store import sync_get_approved_testimonials
    def get_approved_testimonials(limit: int = 6, featured_only: bool = False) -> dict:
        return sync_get_approved_testimonials(limit, featured_only)
except ImportError:
    logger.warning("Could not import testimonials_store")

# Export everything
__all__ = [
    'PostgresManager', 'get_postgres_manager', 
    'Neo4jManager', 'neo4j_manager',
    'DualWriteManager', 'dual_write_manager',
    'get_db_connection', 'run_database_migrations'
]

# Auto-run migrations on startup
# ==============================================================================
# ⚠️ CRITICAL: DO NOT UNCOMMENT THE LINES BELOW
# ⚠️ Auto-running migrations here causes a race condition where migrations run
# ⚠️ before the 'users' table is created by initialize_database.py.
# ==============================================================================

# try:
#     run_database_migrations()
# except Exception as e:
#     logger.warning(f"Initial migration attempt deferred: {e}")
