"""
Database Connection Manager for Jeseci Smart Learning Academy

This module provides database connection utilities for PostgreSQL and Neo4j.
It handles connection pooling, session management, and provides clean
interfaces for database operations.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

import psycopg2
from psycopg2 import pool, extras
from neo4j import GraphDatabase

# Import centralized logging configuration
from logger_config import logger

# Database schema configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")

# Import testimonial functions from testimonials_store
from testimonials_store import get_approved_testimonials as sync_get_approved_testimonials


class DatabaseConfig:
    """Database configuration holder"""
    
    def __init__(self):
        # PostgreSQL Configuration
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", 5432))
        self.postgres_db = os.getenv("POSTGRES_DB", "jeseci_learning_academy")
        self.postgres_user = os.getenv("POSTGRES_USER", "jeseci_academy_user")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
        self.postgres_pool_size = int(os.getenv("POSTGRES_POOL_SIZE", 5))
        self.postgres_max_overflow = int(os.getenv("POSTGRES_MAX_OVERFLOW", 10))
        
        # Neo4j Configuration
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "neo4j_secure_password_2024")
        self.neo4j_database = os.getenv("NEO4J_DATABASE", "jeseci_academy")
        
    def get_postgres_connection_string(self):
        """Build PostgreSQL connection string from components"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def __repr__(self):
        return f"DatabaseConfig(postgres={self.postgres_host}:{self.postgres_port}/{self.postgres_db}, neo4j={self.neo4j_uri})"


class PostgresConnectionManager:
    """
    PostgreSQL connection manager with connection pooling.
    
    Provides thread-safe database connections for PostgreSQL operations.
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        config = DatabaseConfig()
        try:
            PostgresConnectionManager._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=config.postgres_pool_size + config.postgres_max_overflow,
                host=config.postgres_host,
                port=config.postgres_port,
                database=config.postgres_db,
                user=config.postgres_user,
                password=config.postgres_password
            )
            logger.info(f"PostgreSQL connection pool initialized: {config.postgres_host}:{config.postgres_port}/{config.postgres_db}")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")
            PostgresConnectionManager._pool = None
    
    def get_connection(self):
        """Get a connection from the pool"""
        if PostgresConnectionManager._pool is None:
            self._initialize_pool()
        if PostgresConnectionManager._pool:
            return PostgresConnectionManager._pool.getconn()
        return None
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if PostgresConnectionManager._pool and conn:
            PostgresConnectionManager._pool.putconn(conn)
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and optionally fetch results"""
        conn = self.get_connection()
        if conn is None:
            logger.error("No PostgreSQL connection available")
            return None
        
        try:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                # Convert to list of dicts
                return [dict(row) for row in result]
            else:
                conn.commit()
                return {"status": "success", "rows_affected": cursor.rowcount}
        except Exception as e:
            logger.error(f"PostgreSQL query error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            self.return_connection(conn)
    
    def execute_many(self, query, params_list):
        """Execute a query with multiple parameter sets"""
        conn = self.get_connection()
        if conn is None:
            logger.error("No PostgreSQL connection available")
            return None
        
        try:
            cursor = conn.cursor()
            extras.execute_batch(cursor, query, params_list)
            conn.commit()
            return {"status": "success"}
        except Exception as e:
            logger.error(f"PostgreSQL batch execution error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            self.return_connection(conn)
    
    def close(self):
        """Close all connections in the pool"""
        if PostgresConnectionManager._pool:
            PostgresConnectionManager._pool.closeall()
            PostgresConnectionManager._pool = None
            logger.info("PostgreSQL connection pool closed")
    
    def test_connection(self):
        """Test the database connection"""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                self.return_connection(conn)
                return True
            except Exception as e:
                logger.error(f"PostgreSQL connection test failed: {e}")
                self.return_connection(conn)
        return False


class Neo4jConnectionManager:
    """
    Neo4j connection manager for graph database operations.
    
    Provides connection management for Neo4j graph operations including
    concept relationships, learning paths, and recommendations.
    """
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize_driver(self):
        """Initialize the Neo4j driver"""
        config = DatabaseConfig()
        try:
            Neo4jConnectionManager._driver = GraphDatabase.driver(
                config.neo4j_uri,
                auth=(config.neo4j_user, config.neo4j_password)
            )
            logger.info(f"Neo4j driver initialized: {config.neo4j_uri}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            Neo4jConnectionManager._driver = None
    
    def get_session(self):
        """Get a Neo4j session"""
        if Neo4jConnectionManager._driver is None:
            self._initialize_driver()
        if Neo4jConnectionManager._driver:
            return Neo4jConnectionManager._driver.session()
        return None
    
    def execute_query(self, query, parameters=None):
        """Execute a Cypher query"""
        session = self.get_session()
        if session is None:
            logger.error("No Neo4j session available")
            return None
        
        try:
            result = session.run(query, parameters)
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def execute_write(self, query, parameters=None):
        """Execute a write operation (auto-commits)"""
        session = self.get_session()
        if session is None:
            logger.error("No Neo4j session available")
            return None
        
        try:
            result = session.execute_write(lambda tx: tx.run(query, parameters))
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Neo4j write error: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def close(self):
        """Close the Neo4j driver"""
        if Neo4jConnectionManager._driver:
            Neo4jConnectionManager._driver.close()
            Neo4jConnectionManager._driver = None
            logger.info("Neo4j driver closed")
    
    def test_connection(self):
        """Test the Neo4j connection"""
        try:
            session = self.get_session()
            if session:
                result = session.run("RETURN 1 AS test")
                record = result.single()
                session.close()
                return record["test"] == 1
        except Exception as e:
            logger.error(f"Neo4j connection test failed: {e}")
        return False


class DualWriteManager:
    """
    Manages dual-write operations to both PostgreSQL and Neo4j.
    
    Ensures data consistency across both databases for concepts,
    learning paths, and user progress data.
    """
    
    def __init__(self):
        self.pg_manager = PostgresConnectionManager()
        self.neo4j_manager = Neo4jConnectionManager()
    
    def sync_concept_to_neo4j(self, concept_id: str, name: str, display_name: str, 
                               category: str, difficulty_level: str, description: str = ""):
        """
        Sync a concept to Neo4j graph.
        
        Creates or updates a Concept node in Neo4j with all metadata.
        """
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
        """
        Create a relationship between two concepts in Neo4j.
        
        Types: PREREQUISITE, RELATED_TO, PART_OF, BUILDS_UPON
        """
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
        """
        Get personalized learning recommendations from Neo4j.
        
        Uses graph traversal to find concepts that depend on completed ones.
        """
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
        """
        Get a subgraph of related concepts.
        
        Returns the concept and its neighbors up to specified depth.
        """
        query = f"""
        MATCH path = (c:Concept {{concept_id: $concept_id}})-[*1..{depth}]-(related:Concept)
        WITH c, collect(DISTINCT related) as neighbors
        RETURN c,
               [n IN neighbors | {{id: n.concept_id, name: n.name, 
                   display_name: n.display_name, category: n.category}}] as related
        """
        
        return self.neo4j_manager.execute_query(query, {"concept_id": concept_id})


# Global instances for easy access
postgres_manager = PostgresConnectionManager()
neo4j_manager = Neo4jConnectionManager()
dual_write_manager = DualWriteManager()


def get_db_connection():
    """Get a PostgreSQL database connection from the pool
    
    Returns a connection object that can be used for database operations.
    Caller must return the connection to the pool after use.
    """
    return postgres_manager.get_connection()


def get_postgres_manager():
    """Get the PostgreSQL connection manager instance"""
    return postgres_manager


def get_neo4j_manager():
    """Get the Neo4j connection manager instance"""
    return neo4j_manager


def get_dual_write_manager():
    """Get the dual-write manager instance"""
    return dual_write_manager


def close_all_connections():
    """Close all database connections"""
    postgres_manager.close()
    neo4j_manager.close()


def test_all_connections():
    """Test all database connections"""
    results = {
        "postgresql": postgres_manager.test_connection(),
        "neo4j": neo4j_manager.test_connection()
    }
    return results


# Testimonial functions
def get_approved_testimonials(limit: int = 6, featured_only: bool = False) -> dict:
    """
    Get approved testimonials from the database

    Args:
        limit: Maximum number of testimonials to return
        featured_only: If True, only return featured testimonials

    Returns:
        Dict with success status, testimonials list, and total count
    """
    return sync_get_approved_testimonials(limit, featured_only)
