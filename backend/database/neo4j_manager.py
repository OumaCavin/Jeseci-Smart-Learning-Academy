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
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'config', '.env'))


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
    
    # def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    #     """
    #     Execute a single Cypher query.
        
    #     Args:
    #         query: Cypher query string
    #         parameters: Optional query parameters
            
    #     Returns:
    #         Query result or None if error
    #     """
    #     if not self.driver:
    #         if not self.connect():
    #             return None
        
    #     try:
    #         with self.driver.session(database=self.database) as session:
    #             result = session.run(query, parameters)
    #             return result
    #     except Exception as e:
    #         print(f"[!] Neo4j query error: {e}")
    #         return None
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results as a list of dictionaries.
        Used by Admin Content Store.
        """
        if not self.driver:
            if not self.connect():
                raise ConnectionError("Could not connect to Neo4j database")

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            print(f"[!] Neo4j execute_query error: {e}")
            return []

    def execute_write(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a write transaction and return results.
        Used by Admin Content Store.
        """
        if not self.driver:
            if not self.connect():
                raise ConnectionError("Could not connect to Neo4j database")

        try:
            with self.driver.session(database=self.database) as session:
                # Use execute_write to manage the transaction automatically
                result = session.execute_write(
                    lambda tx: tx.run(query, parameters or {}).data()
                )
                return result
        except Exception as e:
            print(f"[!] Neo4j execute_write error: {e}")
            return []
            
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
    
    # =============================================================================
    # User Sync Methods
    # =============================================================================
    
    def sync_user_to_graph(self, user_id: int, username: str, email: str, 
                           first_name: str = "", last_name: str = "",
                           skill_level: str = "beginner", 
                           learning_style: str = "visual",
                           is_admin: bool = False, admin_role: str = "student") -> bool:
        """
        Create or update a User node in Neo4j graph.
        
        Args:
            user_id: PostgreSQL user.id (INTEGER) - converted to string for Neo4j
            username: Unique username
            email: User email
            first_name: First name
            last_name: Last name
            skill_level: User's skill level
            learning_style: User's learning style
            is_admin: Whether user is admin
            admin_role: Admin role level
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MERGE (u:User {user_id: toString($user_id)})
        SET u.username = $username,
            u.email = $email,
            u.first_name = $first_name,
            u.last_name = $last_name,
            u.skill_level = $skill_level,
            u.learning_style = $learning_style,
            u.is_admin = $is_admin,
            u.admin_role = $admin_role,
            u.updated_at = datetime()
        RETURN u
        """
        parameters = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "skill_level": skill_level,
            "learning_style": learning_style,
            "is_admin": is_admin,
            "admin_role": admin_role
        }
        
        result = self.execute_query(query, parameters)
        return result is not None
    
    def sync_user_concept_progress(self, user_id: int, concept_id: str, 
                                    progress_percent: int, mastery_level: int,
                                    completed: bool = False) -> bool:
        """
        Create or update relationship between User and Concept showing progress.
        
        Args:
            user_id: PostgreSQL user.id
            concept_id: Concept identifier
            progress_percent: Progress percentage (0-100)
            mastery_level: Mastery level (0-5)
            completed: Whether concept is completed
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (u:User {user_id: toString($user_id)})
        MERGE (c:Concept {concept_id: $concept_id})
        MERGE (u)-[r:COMPLETED_CONCEPT]->(c)
        SET r.progress_percent = $progress_percent,
            r.mastery_level = $mastery_level,
            r.completed = $completed,
            r.last_accessed = datetime(),
            r.updated_at = datetime()
        RETURN r
        """
        parameters = {
            "user_id": user_id,
            "concept_id": concept_id,
            "progress_percent": progress_percent,
            "mastery_level": mastery_level,
            "completed": completed
        }
        
        result = self.execute_query(query, parameters)
        return result is not None
    
    def sync_user_learning_path(self, user_id: int, path_id: str, 
                                 progress_percent: float = 0.0) -> bool:
        """
        Create relationship between User and LearningPath.
        
        Args:
            user_id: PostgreSQL user.id
            path_id: Learning path identifier
            progress_percent: Progress percentage
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (u:User {user_id: toString($user_id)})
        MERGE (p:LearningPath {path_id: $path_id})
        MERGE (u)-[r:ENROLLED_IN]->(p)
        SET r.progress_percent = $progress_percent,
            r.enrolled_at = datetime(),
            r.updated_at = datetime()
        RETURN r
        """
        parameters = {
            "user_id": user_id,
            "path_id": path_id,
            "progress_percent": progress_percent
        }
        
        result = self.execute_query(query, parameters)
        return result is not None
    
    def sync_user_quiz_attempt(self, user_id: int, quiz_id: str, 
                               score: int, passed: bool) -> bool:
        """
        Create relationship for quiz attempt.
        
        Args:
            user_id: PostgreSQL user.id
            quiz_id: Quiz identifier
            score: Quiz score
            passed: Whether quiz was passed
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (u:User {user_id: toString($user_id)})
        MERGE (q:Quiz {quiz_id: $quiz_id})
        MERGE (u)-[r:ATTEMPTED_QUIZ]->(q)
        SET r.score = $score,
            r.passed = $passed,
            r.attempted_at = datetime()
        RETURN r
        """
        parameters = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "score": score,
            "passed": passed
        }
        
        result = self.execute_query(query, parameters)
        return result is not None
    
    def sync_user_achievement(self, user_id: int, achievement_id: str) -> bool:
        """
        Create EARNED relationship when user earns an achievement.
        
        Args:
            user_id: PostgreSQL user.id
            achievement_id: Achievement identifier
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (u:User {user_id: toString($user_id)})
        MERGE (a:Achievement {achievement_id: $achievement_id})
        MERGE (u)-[r:EARNED]->(a)
        SET r.earned_at = datetime()
        RETURN r
        """
        parameters = {
            "user_id": user_id,
            "achievement_id": achievement_id
        }
        
        result = self.execute_query(query, parameters)
        return result is not None
    
    def find_similar_users(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Find users with similar learning patterns using Neo4j graph traversal.
        
        Args:
            user_id: The user to find similar users for
            limit: Maximum number of similar users to return
            
        Returns:
            List of similar users with similarity score
        """
        query = """
        MATCH (target:User {user_id: toString($user_id)})-[:COMPLETED_CONCEPT]->(c:Concept)
        WITH target, collect(c.concept_id) AS target_concepts
        MATCH (other:User)-[:COMPLETED_CONCEPT]->(c:Concept)
        WHERE other.user_id <> target.user_id
        WITH target, other, target_concepts, collect(c.concept_id) AS other_concepts
        WITH target, other, 
             size([x IN target_concepts WHERE x IN other_concepts]) AS intersection,
             size(target_concepts) + size(other_concepts) - size([x IN target_concepts WHERE x IN other_concepts]) AS union_size
        WITH other, 
             toFloat(intersection) / toFloat(union_size) AS similarity
        WHERE similarity > 0
        RETURN other.user_id AS user_id,
               other.username AS username,
               other.skill_level AS skill_level,
               other.learning_style AS learning_style,
               similarity
        ORDER BY similarity DESC
        LIMIT $limit
        """
        parameters = {"user_id": user_id, "limit": limit}
        
        if not self.driver:
            if not self.connect():
                return []
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                return [{"user_id": record["user_id"], 
                         "username": record["username"],
                         "skill_level": record["skill_level"],
                         "learning_style": record["learning_style"],
                         "similarity": record["similarity"]} 
                        for record in result]
        except Exception as e:
            print(f"[!] Neo4j similarity query error: {e}")
            return []
    
    def find_users_same_learning_path(self, user_id: int, path_id: str) -> List[Dict]:
        """
        Find other users enrolled in the same learning path.
        
        Args:
            user_id: The user to find peers for
            path_id: Learning path identifier
            
        Returns:
            List of users in the same learning path
        """
        query = """
        MATCH (target:User {user_id: toString($user_id)})-[:ENROLLED_IN]->(p:LearningPath {path_id: $path_id})
        MATCH (other:User)-[:ENROLLED_IN]->(p)
        WHERE other.user_id <> target.user_id
        RETURN other.user_id AS user_id,
               other.username AS username,
               other.skill_level AS skill_level
        ORDER BY other.username
        """
        parameters = {"user_id": user_id, "path_id": path_id}
        
        if not self.driver:
            if not self.connect():
                return []
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                return [{"user_id": record["user_id"], 
                         "username": record["username"],
                         "skill_level": record["skill_level"]} 
                        for record in result]
        except Exception as e:
            print(f"[!] Neo4j peer query error: {e}")
            return []
    
    def delete_user_from_graph(self, user_id: int) -> bool:
        """
        Remove a User node and all their relationships from Neo4j.
        
        Args:
            user_id: PostgreSQL user.id to remove
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (u:User {user_id: toString($user_id)})
        DETACH DELETE u
        """
        result = self.execute_query(query, {"user_id": user_id})
        return result is not None


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
