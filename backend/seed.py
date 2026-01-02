#!/usr/bin/env python3
"""
Jeseci Smart Learning Academy - Database Seeder for Jac Language Concepts
This module seeds the database with Jac programming language concepts,
learning paths, and establishes relationships between them.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db_module
import datetime


# ==============================================================================
# Jac Language Concept Data
# ==============================================================================

jac_concepts_data = [
    {
        "name": "jac_programming_fundamentals",
        "display_name": "JAC Programming Fundamentals",
        "description": "Introduction to JAC programming language",
        "detailed_description": "JAC introduces Object-Spatial Programming",
        "category": "JAC Programming",
        "subcategory": "Introduction",
        "domain": "Computer Science",
        "difficulty_level": "beginner",
        "complexity_score": 6.0,
        "cognitive_load": 6.5,
        "key_terms": ["JAC", "OSP", "nodes", "walkers"],
        "synonyms": ["JAC Language"]
    },
    {
        "name": "jac_variables_data_types",
        "display_name": "JAC Variables and Data Types",
        "description": "Understanding JAC type system",
        "detailed_description": "JAC uses strong typing with annotations",
        "category": "JAC Programming",
        "subcategory": "Fundamentals",
        "domain": "Computer Science",
        "difficulty_level": "beginner",
        "complexity_score": 4.0,
        "cognitive_load": 4.5,
        "key_terms": ["variable", "type", "annotation"],
        "synonyms": ["data types"]
    },
    {
        "name": "jac_control_flow",
        "display_name": "JAC Control Flow",
        "description": "Mastering conditionals and loops",
        "detailed_description": "JAC provides traditional control flow structures",
        "category": "JAC Programming",
        "subcategory": "Fundamentals",
        "domain": "Computer Science",
        "difficulty_level": "beginner",
        "complexity_score": 5.0,
        "cognitive_load": 5.5,
        "key_terms": ["if", "else", "while", "for"],
        "synonyms": ["conditionals", "loops"]
    },
    {
        "name": "jac_functions",
        "display_name": "JAC Functions",
        "description": "Creating reusable code blocks",
        "detailed_description": "JAC functions use def keyword with type annotations",
        "category": "JAC Programming",
        "subcategory": "Fundamentals",
        "domain": "Computer Science",
        "difficulty_level": "beginner",
        "complexity_score": 5.5,
        "cognitive_load": 6.0,
        "key_terms": ["function", "parameter", "return"],
        "synonyms": ["method", "procedure"]
    },
    {
        "name": "jac_collections",
        "display_name": "JAC Collections",
        "description": "Working with lists and dictionaries",
        "detailed_description": "JAC supports lists and dicts with strong typing",
        "category": "JAC Programming",
        "subcategory": "Intermediate",
        "domain": "Computer Science",
        "difficulty_level": "intermediate",
        "complexity_score": 6.5,
        "cognitive_load": 7.0,
        "key_terms": ["list", "dict", "collection"],
        "synonyms": ["data structures"]
    },
    {
        "name": "jac_oop",
        "display_name": "JAC Object-Oriented Programming",
        "description": "Implementing classes and objects",
        "detailed_description": "JAC supports OOP with obj keyword",
        "category": "JAC Programming",
        "subcategory": "Intermediate",
        "domain": "Computer Science",
        "difficulty_level": "intermediate",
        "complexity_score": 7.0,
        "cognitive_load": 7.5,
        "key_terms": ["object", "class", "method", "obj"],
        "synonyms": ["OOP"]
    },
    {
        "name": "jac_object_spatial_programming",
        "display_name": "JAC Object-Spatial Programming",
        "description": "Understanding OSP paradigm",
        "detailed_description": "OSP moves computation to data",
        "category": "JAC Programming",
        "subcategory": "Advanced",
        "domain": "Computer Science",
        "difficulty_level": "advanced",
        "complexity_score": 8.5,
        "cognitive_load": 9.0,
        "key_terms": ["OSP", "node", "edge", "walker"],
        "synonyms": ["graph programming"]
    },
    {
        "name": "jac_nodes_edges",
        "display_name": "JAC Nodes and Edges",
        "description": "Creating nodes and edges",
        "detailed_description": "Nodes and edges form graph structures",
        "category": "JAC Programming",
        "subcategory": "Advanced",
        "domain": "Computer Science",
        "difficulty_level": "advanced",
        "complexity_score": 8.0,
        "cognitive_load": 8.5,
        "key_terms": ["node", "edge", "graph"],
        "synonyms": ["vertices", "links"]
    },
    {
        "name": "jac_walkers",
        "display_name": "JAC Walkers and Graph Traversal",
        "description": "Implementing walkers for traversal",
        "detailed_description": "Walkers traverse graphs performing tasks",
        "category": "JAC Programming",
        "subcategory": "Advanced",
        "domain": "Computer Science",
        "difficulty_level": "advanced",
        "complexity_score": 8.5,
        "cognitive_load": 9.0,
        "key_terms": ["walker", "spawn", "visit"],
        "synonyms": ["mobile agents"]
    },
    {
        "name": "jac_ai_integration",
        "display_name": "JAC AI Integration with byLLM",
        "description": "Integrating LLMs into JAC apps",
        "detailed_description": "JAC provides native AI integration",
        "category": "JAC Programming",
        "subcategory": "Expert",
        "domain": "Computer Science",
        "difficulty_level": "expert",
        "complexity_score": 9.0,
        "cognitive_load": 9.5,
        "key_terms": ["byLLM", "AI", "LLM"],
        "synonyms": ["AI integration"]
    },
    {
        "name": "jac_scale_agnostic_programming",
        "display_name": "JAC Scale-Agnostic Programming",
        "description": "Building scalable applications",
        "detailed_description": "JAC enables scale-agnostic programming",
        "category": "JAC Programming",
        "subcategory": "Expert",
        "domain": "Computer Science",
        "difficulty_level": "expert",
        "complexity_score": 9.0,
        "cognitive_load": 9.0,
        "key_terms": ["scale", "distributed", "persistence"],
        "synonyms": ["elastic programming"]
    }
]


# ==============================================================================
# Learning Path Data
# ==============================================================================

jac_learning_paths = [
    {
        "path_id": "jac_fundamentals_journey",
        "name": "JAC Programming Fundamentals Journey",
        "title": "JAC Programming Fundamentals Journey",
        "description": "Master essential JAC concepts",
        "category": "JAC Programming",
        "difficulty_level": "beginner",
        "estimated_duration": 40,
        "target_audience": "Beginner programmers",
        "concepts": ["jac_programming_fundamentals", "jac_variables_data_types", "jac_control_flow", "jac_functions"]
    },
    {
        "path_id": "jac_oop_collections_mastery",
        "name": "JAC OOP and Collections Mastery",
        "title": "JAC OOP and Collections Mastery",
        "description": "Advanced JAC with OOP and collections",
        "category": "JAC Programming",
        "difficulty_level": "intermediate",
        "estimated_duration": 35,
        "target_audience": "Intermediate programmers",
        "concepts": ["jac_collections", "jac_oop"]
    },
    {
        "path_id": "jac_osp_expert",
        "name": "JAC OSP Expert",
        "title": "JAC OSP Expert",
        "description": "Master OSP with nodes, edges, walkers",
        "category": "JAC Programming",
        "difficulty_level": "advanced",
        "estimated_duration": 50,
        "target_audience": "Advanced programmers",
        "concepts": ["jac_object_spatial_programming", "jac_nodes_edges", "jac_walkers"]
    },
    {
        "path_id": "jac_ai_expert",
        "name": "JAC AI Integration Expert",
        "title": "JAC AI Integration Expert",
        "description": "Expert JAC with AI integration",
        "category": "JAC Programming",
        "difficulty_level": "expert",
        "estimated_duration": 45,
        "target_audience": "Expert programmers",
        "concepts": ["jac_ai_integration", "jac_scale_agnostic_programming"]
    }
]


# ==============================================================================
# Course Data
# ==============================================================================

jac_courses_data = [
    {
        "course_id": "jac_fundamentals_course",
        "title": "JAC Programming Fundamentals",
        "description": "Master the basics of JAC programming including variables, data types, control flow, functions, and collections. Perfect for beginners starting their JAC journey.",
        "domain": "JAC Programming",
        "difficulty_level": "beginner",
        "estimated_duration": 240,
        "content_type": "interactive",
        "concepts": ["jac_programming_fundamentals", "jac_variables_data_types", "jac_control_flow", "jac_functions", "jac_collections"]
    },
    {
        "course_id": "jac_oop_course",
        "title": "JAC Object-Oriented Programming",
        "description": "Deep dive into JAC's object-oriented programming features including classes, objects, methods, and inheritance patterns.",
        "domain": "JAC Programming",
        "difficulty_level": "intermediate",
        "estimated_duration": 180,
        "content_type": "interactive",
        "concepts": ["jac_oop"]
    },
    {
        "course_id": "jac_osp_course",
        "title": "JAC Object-Spatial Programming (OSP)",
        "description": "Learn the revolutionary Object-Spatial Programming paradigm with nodes, edges, walkers, and graph traversal techniques.",
        "domain": "JAC Programming",
        "difficulty_level": "advanced",
        "estimated_duration": 300,
        "content_type": "interactive",
        "concepts": ["jac_object_spatial_programming", "jac_nodes_edges", "jac_walkers"]
    },
    {
        "course_id": "jac_ai_course",
        "title": "JAC AI Integration with byLLM",
        "description": "Integrate Large Language Models into your JAC applications using the byLLM module for AI-powered functionality.",
        "domain": "JAC Programming",
        "difficulty_level": "advanced",
        "estimated_duration": 240,
        "content_type": "interactive",
        "concepts": ["jac_ai_integration"]
    },
    {
        "course_id": "jac_scale_course",
        "title": "JAC Scale-Agnostic Programming",
        "description": "Build scalable, production-ready applications using JAC's scale-agnostic programming features and distributed computing concepts.",
        "domain": "JAC Programming",
        "difficulty_level": "expert",
        "estimated_duration": 270,
        "content_type": "interactive",
        "concepts": ["jac_scale_agnostic_programming"]
    }
]


# ==============================================================================
# Relationship Data
# ==============================================================================

jac_relationships = [
    # Hierarchy / Prerequisites
    {"from": "jac_programming_fundamentals", "to": "jac_variables_data_types", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_variables_data_types", "to": "jac_control_flow", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_control_flow", "to": "jac_functions", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_functions", "to": "jac_collections", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_collections", "to": "jac_oop", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_oop", "to": "jac_object_spatial_programming", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_object_spatial_programming", "to": "jac_nodes_edges", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_nodes_edges", "to": "jac_walkers", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_walkers", "to": "jac_ai_integration", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_ai_integration", "to": "jac_scale_agnostic_programming", "type": "PREREQUISITE", "strength": 1},
    
    # Related concepts
    {"from": "jac_control_flow", "to": "jac_functions", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_variables_data_types", "to": "jac_collections", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_oop", "to": "jac_collections", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_object_spatial_programming", "to": "jac_walkers", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_nodes_edges", "to": "jac_walkers", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_ai_integration", "to": "jac_walkers", "type": "RELATED_TO", "strength": 0.5},
    
    # Builds upon relationships
    {"from": "jac_oop", "to": "jac_object_spatial_programming", "type": "BUILDS_UPON", "strength": 1},
    {"from": "jac_nodes_edges", "to": "jac_ai_integration", "type": "BUILDS_UPON", "strength": 0.8},
    {"from": "jac_scale_agnostic_programming", "to": "jac_object_spatial_programming", "type": "BUILDS_UPON", "strength": 0.8}
]


# ==============================================================================
# Seeder Functions
# ==============================================================================

def create_constraints(manager):
    """Create Neo4j constraints"""
    constraint_queries = [
        "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE",
        "CREATE CONSTRAINT path_id_unique IF NOT EXISTS FOR (p:LearningPath) REQUIRE p.path_id IS UNIQUE"
    ]
    for cq in constraint_queries:
        try:
            manager.execute_query(cq, None)
        except Exception:
            pass  # Constraints may already exist


def seed_concepts_to_neo4j(manager, dry_run=False, verbose=True):
    """Seed concepts to Neo4j"""
    if dry_run:
        print("Dry run - concepts not seeded")
        return {"success": True, "concepts_created": 0}
    
    # Clear existing Jac concepts
    try:
        clear_query = "MATCH (c:Concept {category: 'JAC Programming'}) DETACH DELETE c"
        manager.execute_query(clear_query, None)
        if verbose:
            print("Cleared existing JAC concepts")
    except Exception as e:
        if verbose:
            print(f"Clear warning: {e}")
    
    concepts_created = 0
    concepts_skipped = 0
    
    for concept_data in jac_concepts_data:
        name = concept_data.get("name", "")
        display_name = concept_data.get("display_name", "")
        category = concept_data.get("category", "")
        subcategory = concept_data.get("subcategory", "")
        domain = concept_data.get("domain", "")
        difficulty_level = concept_data.get("difficulty_level", "")
        complexity_score = concept_data.get("complexity_score", 0)
        cognitive_load = concept_data.get("cognitive_load", 0)
        description = concept_data.get("description", "")
        detailed_description = concept_data.get("detailed_description", "")
        key_terms = concept_data.get("key_terms", [])
        synonyms = concept_data.get("synonyms", [])
        
        # Generate concept_id
        concept_id = "jac_" + name
        
        create_query = """
        MERGE (c:Concept {concept_id: $concept_id})
        SET c.name = $name,
            c.display_name = $display_name,
            c.category = $category,
            c.subcategory = $subcategory,
            c.domain = $domain,
            c.difficulty_level = $difficulty_level,
            c.complexity_score = $complexity_score,
            c.cognitive_load = $cognitive_load,
            c.description = $description,
            c.detailed_description = $detailed_description,
            c.key_terms = $key_terms,
            c.synonyms = $synonyms,
            c.created_at = datetime()
        """
        
        params = {
            "concept_id": concept_id,
            "name": name,
            "display_name": display_name,
            "category": category,
            "subcategory": subcategory,
            "domain": domain,
            "difficulty_level": difficulty_level,
            "complexity_score": complexity_score,
            "cognitive_load": cognitive_load,
            "description": description,
            "detailed_description": detailed_description,
            "key_terms": key_terms,
            "synonyms": synonyms
        }
        
        try:
            manager.execute_query(create_query, params)
            concepts_created += 1
            if verbose:
                print(f"Created concept: {display_name}")
        except Exception as e:
            concepts_skipped += 1
            if verbose:
                print(f"Failed to create: {display_name} - {e}")
    
    print(f"Concepts created: {concepts_created}")
    return {"success": True, "concepts_created": concepts_created}


def seed_paths_to_neo4j(manager, dry_run=False, verbose=True):
    """Seed learning paths to Neo4j"""
    if dry_run:
        print("Dry run - paths not seeded")
        return {"success": True, "paths_created": 0}
    
    # Clear existing learning paths
    try:
        clear_query = "MATCH (p:LearningPath {category: 'JAC Programming'}) DETACH DELETE p"
        manager.execute_query(clear_query, None)
        if verbose:
            print("Cleared existing JAC learning paths")
    except Exception as e:
        if verbose:
            print(f"Clear warning: {e}")
    
    paths_created = 0
    relationships_created = 0
    
    for path_data in jac_learning_paths:
        path_id = path_data.get("path_id", "")
        name = path_data.get("name", "")
        title = path_data.get("title", "")
        description = path_data.get("description", "")
        category = path_data.get("category", "")
        difficulty_level = path_data.get("difficulty_level", "")
        estimated_duration = path_data.get("estimated_duration", 0)
        target_audience = path_data.get("target_audience", "")
        concepts = path_data.get("concepts", [])
        
        concept_count = len(concepts)
        
        create_path_query = """
        MERGE (p:LearningPath {path_id: $path_id})
        SET p.name = $name,
            p.title = $title,
            p.description = $description,
            p.category = $category,
            p.difficulty = $difficulty_level,
            p.estimated_duration = $estimated_duration,
            p.target_audience = $target_audience,
            p.concept_count = $concept_count,
            p.created_at = datetime()
        """
        
        path_params = {
            "path_id": path_id,
            "name": name,
            "title": title,
            "description": description,
            "category": category,
            "difficulty_level": difficulty_level,
            "estimated_duration": estimated_duration,
            "target_audience": target_audience,
            "concept_count": concept_count
        }
        
        try:
            manager.execute_query(create_path_query, path_params)
            paths_created += 1
            if verbose:
                print(f"Created learning path: {title}")
            
            # Link concepts to path
            order = 1
            for concept_name in concepts:
                concept_id = "jac_" + concept_name
                
                link_query = """
                MATCH (p:LearningPath {path_id: $path_id})
                MATCH (c:Concept {name: $concept_name})
                MERGE (p)-[r:PathContains {order_index: $order, is_required: true, created_at: datetime()}]->(c)
                """
                
                link_params = {
                    "path_id": path_id,
                    "concept_name": concept_name,
                    "order": order
                }
                
                try:
                    manager.execute_query(link_query, link_params)
                    relationships_created += 1
                except Exception as e:
                    if verbose:
                        print(f"Failed to link concept: {concept_name} - {e}")
                order += 1
        except Exception as e:
            if verbose:
                print(f"Failed to create path: {title} - {e}")
    
    print(f"Paths created: {paths_created}")
    print(f"Path-concept relationships: {relationships_created}")
    return {"success": True, "paths_created": paths_created}


def seed_relationships_to_neo4j(manager, dry_run=False, verbose=True):
    """Seed relationships to Neo4j"""
    if dry_run:
        print("Dry run - relationships not seeded")
        return {"success": True, "relationships_created": 0}
    
    relationships_created = 0
    relationships_skipped = 0
    
    for rel in jac_relationships:
        from_name = rel.get("from", "")
        to_name = rel.get("to", "")
        rel_type = rel.get("type", "")
        strength = rel.get("strength", 0)
        
        rel_query = f"""
        MATCH (a:Concept {{name: $from_name}})
        MATCH (b:Concept {{name: $to_name}})
        MERGE (a)-[r:{rel_type} {{strength: $strength, created_at: datetime()}}]->(b)
        SET r.type = "{rel_type}"
        """
        
        params = {
            "from_name": from_name,
            "to_name": to_name,
            "type": rel_type,
            "strength": strength
        }
        
        try:
            manager.execute_query(rel_query, params)
            relationships_created += 1
            if verbose:
                print(f"Created: {from_name} --[{rel_type}]--> {to_name}")
        except Exception as e:
            relationships_skipped += 1
            if verbose:
                print(f"Failed: {from_name} --[{rel_type}]--> {to_name} - {e}")
    
    print(f"Relationships created: {relationships_created}")
    return {"success": True, "relationships_created": relationships_created}


# ==============================================================================
# PostgreSQL Seeding Functions
# ==============================================================================

def seed_paths_to_postgres(dry_run=False, verbose=True):
    """Seed learning paths to PostgreSQL"""
    if dry_run:
        print("Dry run - paths not seeded to PostgreSQL")
        return {"success": True, "paths_created": 0}
    
    try:
        pg_manager = db_module.get_postgres_manager()
    except Exception as e:
        if verbose:
            print(f"PostgreSQL not available: {e}")
        return {"success": False, "error": str(e)}
    
    paths_created = 0
    
    for path_data in jac_learning_paths:
        path_id = path_data.get("path_id", "")
        name = path_data.get("name", "")
        title = path_data.get("title", "")
        description = path_data.get("description", "")
        category = path_data.get("category", "")
        difficulty_level = path_data.get("difficulty_level", "")
        estimated_duration = path_data.get("estimated_duration", 0)
        target_audience = path_data.get("target_audience", "")
        concepts = path_data.get("concepts", [])
        
        # Check if path already exists
        check_query = "SELECT path_id FROM jeseci_academy.learning_paths WHERE path_id = %s"
        try:
            existing = pg_manager.execute_query(check_query, (path_id,))
            if existing:
                if verbose:
                    print(f"Path already exists: {title}")
                continue
        except Exception as e:
            if verbose:
                print(f"Check query warning: {e}")
        
        # Insert new path
        insert_query = """
        INSERT INTO jeseci_academy.learning_paths 
        (path_id, name, title, category, difficulty, estimated_duration, 
         target_audience, description, is_published, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
        """
        
        try:
            pg_manager.execute_query(insert_query, (
                path_id, name, title, category, difficulty_level,
                estimated_duration, target_audience, description
            ), fetch=False)
            paths_created += 1
            if verbose:
                print(f"Created path in PostgreSQL: {title}")
            
            # Link concepts to path in the junction table
            for i, concept_name in enumerate(concepts):
                concept_id = f"jac_{concept_name}"
                link_query = """
                INSERT INTO jeseci_academy.learning_path_concepts 
                (path_id, concept_id, sequence_order, is_required)
                VALUES (%s, %s, %s, true)
                ON CONFLICT (path_id, concept_id) DO NOTHING
                """
                try:
                    pg_manager.execute_query(link_query, (path_id, concept_id, i + 1), fetch=False)
                except Exception as e:
                    if verbose:
                        print(f"Failed to link concept: {concept_name} - {e}")
        except Exception as e:
            if verbose:
                print(f"Failed to create path: {title} - {e}")
    
    if verbose:
        print(f"PostgreSQL paths created: {paths_created}")
    return {"success": True, "paths_created": paths_created}


def seed_courses_to_postgres(dry_run=False, verbose=True):
    """Seed courses to PostgreSQL"""
    if dry_run:
        print("Dry run - courses not seeded to PostgreSQL")
        return {"success": True, "courses_created": 0}
    
    try:
        pg_manager = db_module.get_postgres_manager()
    except Exception as e:
        if verbose:
            print(f"PostgreSQL not available: {e}")
        return {"success": False, "error": str(e)}
    
    courses_created = 0
    
    for course_data in jac_courses_data:
        course_id = course_data.get("course_id", "")
        title = course_data.get("title", "")
        description = course_data.get("description", "")
        domain = course_data.get("domain", "")
        difficulty_level = course_data.get("difficulty_level", "")
        estimated_duration = course_data.get("estimated_duration", 0)
        content_type = course_data.get("content_type", "interactive")
        concepts = course_data.get("concepts", [])
        
        # Check if course already exists
        check_query = "SELECT course_id FROM jeseci_academy.courses WHERE course_id = %s"
        try:
            existing = pg_manager.execute_query(check_query, (course_id,))
            if existing:
                if verbose:
                    print(f"Course already exists: {title}")
                continue
        except Exception as e:
            if verbose:
                print(f"Check query warning (courses table may not exist): {e}")
            # Try creating the table if it doesn't exist
            try:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS jeseci_academy.courses (
                    course_id VARCHAR(100) PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    domain VARCHAR(100),
                    difficulty VARCHAR(50),
                    estimated_duration INTEGER,
                    content_type VARCHAR(50),
                    is_published BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
                """
                pg_manager.execute_query(create_table_query, (), fetch=False)
                if verbose:
                    print("Created courses table")
            except Exception as table_error:
                if verbose:
                    print(f"Could not create courses table: {table_error}")
        
        # Insert new course
        insert_query = """
        INSERT INTO jeseci_academy.courses 
        (course_id, title, description, domain, difficulty, estimated_duration, content_type, is_published, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW())
        """
        
        try:
            pg_manager.execute_query(insert_query, (
                course_id, title, description, domain, difficulty_level,
                estimated_duration, content_type
            ), fetch=False)
            courses_created += 1
            if verbose:
                print(f"Created course in PostgreSQL: {title}")
            
            # Link concepts to course if course_concepts table exists
            for i, concept_name in enumerate(concepts):
                concept_id = f"jac_{concept_name}" if not concept_name.startswith("jac_") else concept_name
                try:
                    link_query = """
                    INSERT INTO jeseci_academy.course_concepts 
                    (course_id, concept_id, order_index)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (course_id, concept_id) DO NOTHING
                    """
                    pg_manager.execute_query(link_query, (course_id, concept_id, i + 1), fetch=False)
                except Exception:
                    pass  # Junction table may not exist yet
        except Exception as e:
            if verbose:
                print(f"Failed to create course: {title} - {e}")
    
    if verbose:
        print(f"PostgreSQL courses created: {courses_created}")
    return {"success": True, "courses_created": courses_created}


# ==============================================================================
# Main Entry Point
# ==============================================================================

def run_seeder(mode="all", dry_run=False, verbose=True):
    """Run the database seeder"""
    print("=" * 70)
    print("Database Seeder for Jac Programming Language Concepts")
    print("=" * 70)
    print(f"Mode: {mode}")
    print(f"Dry Run: {dry_run}")
    print(f"Verbose: {verbose}")
    print("=" * 70)
    
    start_time = datetime.datetime.now()
    
    # Get Neo4j manager
    manager = db_module.get_neo4j_manager()
    
    # Create constraints
    if mode == "all" or mode == "concepts":
        create_constraints(manager)
    
    if mode == "all" or mode == "concepts":
        print("\nSeeding Concepts...")
        print("-" * 50)
        seed_concepts_to_neo4j(manager, dry_run, verbose)
    
    if mode == "all" or mode == "paths":
        print("\nSeeding Learning Paths...")
        print("-" * 50)
        seed_paths_to_neo4j(manager, dry_run, verbose)
        print("\nSeeding Learning Paths to PostgreSQL...")
        print("-" * 50)
        seed_paths_to_postgres(dry_run, verbose)
    
    if mode == "all" or mode == "courses":
        print("\nSeeding Courses to PostgreSQL...")
        print("-" * 50)
        seed_courses_to_postgres(dry_run, verbose)
    
    if mode == "all" or mode == "relationships":
        print("\nSeeding Relationships...")
        print("-" * 50)
        seed_relationships_to_neo4j(manager, dry_run, verbose)
    
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 70)
    print("Seeding Complete!")
    print("=" * 70)
    print(f"Duration: {duration} seconds")
    print("=" * 70)
    
    return {"success": True}


def seed_status():
    """Check seeder status"""
    manager = db_module.get_neo4j_manager()
    
    # Count concepts
    concept_query = "MATCH (c:Concept {category: 'JAC Programming'}) RETURN count(c) AS count"
    concept_result = manager.execute_query(concept_query, None)
    jac_concepts_count = concept_result[0]['count'] if concept_result else 0
    
    # Count learning paths
    path_query = "MATCH (p:LearningPath {category: 'JAC Programming'}) RETURN count(p) AS count"
    path_result = manager.execute_query(path_query, None)
    jac_paths_count = path_result[0]['count'] if path_result else 0
    
    # Count relationships
    rel_query = """
    MATCH (a:Concept)-[r:PREREQUISITE|RELATED_TO|BUILDS_UPON]->(b:Concept)
    WHERE a.category = 'JAC Programming' OR b.category = 'JAC Programming'
    RETURN count(r) AS count
    """
    rel_result = manager.execute_query(rel_query, None)
    jac_rels_count = rel_result[0]['count'] if rel_result else 0
    
    print(f"JAC Concepts: {jac_concepts_count}")
    print(f"JAC Learning Paths: {jac_paths_count}")
    print(f"JAC Relationships: {jac_rels_count}")
    
    return {"success": True, "jac_concepts": jac_concepts_count, "jac_learning_paths": jac_paths_count, "jac_relationships": jac_rels_count}


def seed_reset(verbose=True):
    """Reset all Jac data"""
    print("=" * 70)
    print("Resetting Jac Database Seeder Data")
    print("=" * 70)
    
    manager = db_module.get_neo4j_manager()
    
    # Clear relationships first
    rel_query = """
    MATCH (a:Concept)-[r:PREREQUISITE|RELATED_TO|BUILDS_UPON|PathContains]->(b:Concept)
    WHERE a.category = 'JAC Programming' OR b.category = 'JAC Programming'
    DELETE r
    """
    try:
        manager.execute_query(rel_query, None)
        if verbose:
            print("Cleared JAC relationships")
    except Exception as e:
        if verbose:
            print(f"Relationship clear warning: {e}")
    
    # Clear learning paths
    path_query = "MATCH (p:LearningPath {category: 'JAC Programming'}) DETACH DELETE p"
    try:
        manager.execute_query(path_query, None)
        if verbose:
            print("Cleared JAC learning paths")
    except Exception as e:
        if verbose:
            print(f"Path clear warning: {e}")
    
    # Clear concepts
    concept_query = "MATCH (c:Concept {category: 'JAC Programming'}) DETACH DELETE c"
    try:
        manager.execute_query(concept_query, None)
        if verbose:
            print("Cleared JAC concepts")
    except Exception as e:
        if verbose:
            print(f"Concept clear warning: {e}")
    
    print("\nReset complete! All JAC data has been cleared.")
    return {"success": True}


# ==============================================================================
# CLI Interface
# ==============================================================================

def parse_args():
    """Parse command line arguments"""
    mode = "all"
    dry_run = False
    verbose = True
    
    args = sys.argv[1:]
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["--mode", "-m"]:
            if i + 1 < len(args):
                mode = args[i + 1]
                i += 2
                continue
        elif arg in ["--verbose", "-v"]:
            verbose = True
        elif arg in ["--quiet", "-q"]:
            verbose = False
        elif arg in ["--dry-run", "-d"]:
            dry_run = True
        elif arg in ["--help", "-h"]:
            print("Usage: python backend/seed.py [options]")
            print("Options:")
            print("  --mode, -m <mode>  Seeding mode: concepts, paths, relationships, all (default: all)")
            print("  --verbose, -v      Enable verbose output")
            print("  --quiet, -q        Disable verbose output")
            print("  --dry-run, -d      Show what would be done without making changes")
            print("  --help, -h         Show this help message")
            print("")
            print("Examples:")
            print("  python backend/seed.py                    # Seed all data")
            print("  python backend/seed.py --mode concepts    # Seed only concepts")
            print("  python backend/seed.py --dry-run          # Preview seeding")
            sys.exit(0)
        i += 1
    
    return mode, dry_run, verbose


if __name__ == "__main__":
    mode, dry_run, verbose = parse_args()
    run_seeder(mode=mode, dry_run=dry_run, verbose=verbose)
