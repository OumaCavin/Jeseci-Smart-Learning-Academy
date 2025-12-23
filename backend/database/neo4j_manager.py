#!/usr/bin/env python3
"""
Neo4j Database Manager for Jeseci Smart Learning Academy

This module manages Neo4j graph database operations using labels and relationship
types to organize data within the single default database (Neo4j Community Edition).

Graph Structure:
- Node Labels: Concept, LearningPath, Lesson, User, Quiz, Achievement
- Relationship Types: CONTAINS, PREREQUISITE, BELONGS_TO, COMPLETED, EARNED

Author: Cavin Otieno
"""

import os
import sys
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', 'config', '.env'))


class Neo4jManager:
    """
    Manages Neo4j database operations for the learning platform.
    
    Uses labels and relationship types to organize data within the single
    Neo4j database (Community Edition compatible).
    """
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, 
                 password: Optional[str] = None, database: str = "neo4j"):
        """
        Initialize the Neo4j manager.
        
        Args:
            uri: Neo4j bolt URI (defaults to environment variable)
            user: Neo4j username (defaults to environment variable)
            password: Neo4j password (defaults to environment variable)
            database: Database name (always "neo4j" for Community Edition)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "neo4j_secure_password_2024")
        self.database = database  # Community Edition only supports "neo4j"
        self.driver = None
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password),
                max_connection_lifetime=int(os.getenv("NEO4J_MAX_CONNECTION_LIFETIME", "3600"))
            )
            # Verify connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            print(f"[✓] Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            print(f"[!] Neo4j connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close the Neo4j database connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Execute a single Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Optional query parameters
            
        Returns:
            Query result or None if error
        """
        if not self.driver:
            if not self.connect():
                return None
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                return result
        except Exception as e:
            print(f"[!] Neo4j query error: {e}")
            return None
    
    def execute_transaction(self, func):
        """
        Execute a transactional function.
        
        Args:
            func: Function that takes a session and returns result
            
        Returns:
            Transaction result
        """
        if not self.driver:
            if not self.connect():
                return None
        
        with self.driver.session(database=self.database) as session:
            return session.execute_write(func)
    
    def create_constraints(self) -> int:
        """
        Create constraints for the knowledge graph.
        
        Constraints ensure data integrity using labels.
        
        Returns:
            Number of constraints created
        """
        constraints = [
            # Concept constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
            
            # LearningPath constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:LearningPath) REQUIRE p.path_id IS UNIQUE",
            
            # Lesson constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Lesson) REQUIRE l.lesson_id IS UNIQUE",
            
            # User constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
            
            # Quiz constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (q:Quiz) REQUIRE q.quiz_id IS UNIQUE",
            
            # Achievement constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Achievement) REQUIRE a.achievement_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Badge) REQUIRE b.badge_id IS UNIQUE",
        ]
        
        success_count = 0
        for constraint in constraints:
            result = self.execute_query(constraint)
            if result is not None:
                success_count += 1
        
        return success_count
    
    def create_indexes(self) -> int:
        """
        Create indexes for improved query performance.
        
        Returns:
            Number of indexes created
        """
        indexes = [
            # Concept indexes
            "CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.category)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.difficulty_level)",
            
            # LearningPath indexes
            "CREATE INDEX IF NOT EXISTS FOR (p:LearningPath) ON (p.is_published)",
            "CREATE INDEX IF NOT EXISTS FOR (p:LearningPath) ON (p.difficulty)",
            
            # Lesson indexes
            "CREATE INDEX IF NOT EXISTS FOR (l:Lesson) ON (l.learning_path_id)",
            "CREATE INDEX IF NOT EXISTS FOR (l:Lesson) ON (l.is_published)",
            
            # User indexes
            "CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.is_active)",
        ]
        
        success_count = 0
        for index in indexes:
            result = self.execute_query(index)
            if result is not None:
                success_count += 1
        
        return success_count
    
    def clear_project_data(self) -> bool:
        """
        Clear all project-specific data using labels.
        
        This removes all nodes and relationships with project-specific labels
        without affecting other data in the database.
        
        Returns:
            True if successful, False otherwise
        """
        queries = [
            "MATCH (n:Concept) DETACH DELETE n",
            "MATCH (n:LearningPath) DETACH DELETE n",
            "MATCH (n:Lesson) DETACH DELETE n",
            "MATCH (n:Quiz) DETACH DELETE n",
            "MATCH (n:Achievement) DETACH DELETE n",
            "MATCH (n:Badge) DETACH DELETE n",
        ]
        
        for query in queries:
            result = self.execute_query(query)
            if result is None:
                return False
        
        return True
    
    def get_node_count(self, label: Optional[str] = None) -> int:
        """
        Get the count of nodes with a specific label.
        
        Args:
            label: Node label (e.g., "Concept", "LearningPath")
                   If None, counts all nodes
            
        Returns:
            Number of nodes
        """
        if not self.driver:
            if not self.connect():
                return 0
        
        if label:
            query = f"MATCH (n:{label}) RETURN count(n) AS count"
        else:
            query = "MATCH (n) RETURN count(n) AS count"
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            record = result.single()
            return record["count"] if record else 0
    
    def get_relationship_count(self) -> int:
        """
        Get the count of relationships in the database.
        
        Returns:
            Number of relationships
        """
        if not self.driver:
            if not self.connect():
                return 0
        
        with self.driver.session(database=self.database) as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
            record = result.single()
            return record["count"] if record else 0
    
    def verify_setup(self) -> Dict[str, Any]:
        """
        Verify the Neo4j setup is complete.
        
        Returns:
            Dictionary with setup verification results
        """
        return {
            "connected": self.driver is not None,
            "concept_count": self.get_node_count("Concept"),
            "learning_path_count": self.get_node_count("LearningPath"),
            "lesson_count": self.get_node_count("Lesson"),
            "user_count": self.get_node_count("User"),
            "relationship_count": self.get_relationship_count(),
        }


# Global Neo4j manager instance
neo4j_manager = Neo4jManager()


if __name__ == "__main__":
    # Test the Neo4j manager
    print("Testing Neo4j Manager...")
    
    if neo4j_manager.connect():
        print("\n[✓] Neo4j connection successful")
        
        # Create constraints
        constraint_count = neo4j_manager.create_constraints()
        print(f"[✓] Created {constraint_count} constraints")
        
        # Create indexes
        index_count = neo4j_manager.create_indexes()
        print(f"[✓] Created {index_count} indexes")
        
        # Verify setup
        setup = neo4j_manager.verify_setup()
        print(f"\n[✓] Setup verification: {setup}")
        
        neo4j_manager.disconnect()
        print("\n[✓] Neo4j manager test complete")
    else:
        print("\n[!] Failed to connect to Neo4j")
        sys.exit(1)
