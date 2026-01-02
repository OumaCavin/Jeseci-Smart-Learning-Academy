# Admin content storage using PostgreSQL and Neo4j databases
# - Courses stored in PostgreSQL (LearningPath model)
# - Concepts stored in Neo4j (graph relationships and prerequisites)
# - Learning paths use both PostgreSQL and Neo4j

import os
import threading
import datetime
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Import database utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))
from database import get_postgres_manager, get_neo4j_manager
import audit_logger as audit_module

# In-memory cache for PostgreSQL data
courses_cache = {}
paths_cache = {}
content_lock = threading.Lock()
courses_initialized = False
paths_initialized = False

def clear_content_cache():
    """Clear all content caches to force fresh database queries"""
    global courses_cache, paths_cache, courses_initialized, paths_initialized
    
    with content_lock:
        courses_cache = {}
        paths_cache = {}
        courses_initialized = False
        paths_initialized = False
    
    return {"success": True, "message": "Content caches cleared"}

# ==============================================================================
# COURSES STORAGE (PostgreSQL - LearningPath model)
# ==============================================================================

def initialize_courses():
    """Initialize courses from PostgreSQL"""
    global courses_cache, courses_initialized
    
    if courses_initialized:
        return courses_cache
    
    with content_lock:
        if courses_initialized:
            return courses_cache
            
        pg_manager = get_postgres_manager()
        
        try:
            query = """
            SELECT path_id, name, title, category, difficulty, 
                   estimated_duration, description, is_published, created_at, updated_at
            FROM jeseci_academy.learning_paths
            WHERE is_deleted = false
            ORDER BY created_at DESC
            """
            
            result = pg_manager.execute_query(query)
            
            courses_cache = {}
            if result:
                for row in result:
                    path_id = row.get('path_id')
                    courses_cache[path_id] = {
                        "course_id": path_id,
                        "title": row.get('title'),
                        "description": row.get('description'),
                        "domain": row.get('category') or "",
                        "difficulty": row.get('difficulty') or "beginner",
                        "content_type": "interactive",
                        "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
                        "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None
                    }
            
            courses_initialized = True
            return courses_cache
        except Exception as e:
            logger.error(f"Error initializing courses: {e}")
            courses_initialized = False
            return {}

def get_all_courses():
    """Get all courses from PostgreSQL"""
    initialize_courses()
    with content_lock:
        return list(courses_cache.values())

def get_course_by_id(course_id):
    """Get a specific course from PostgreSQL"""
    initialize_courses()
    with content_lock:
        return courses_cache.get(course_id)

def create_course(title, description, domain, difficulty, content_type="interactive"):
    """Create a new course in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Generate course ID
    course_id = "course_" + title.lower().replace(" ", "_").replace("-", "_")[0:20] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
    name = title.lower().replace(" ", "_").replace("-", "_")
    
    insert_query = """
    INSERT INTO jeseci_academy.learning_paths 
    (path_id, name, title, category, difficulty, description, is_published, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, true, NOW())
    """
    
    try:
        result = pg_manager.execute_query(insert_query, 
            (course_id, name, title, domain, difficulty, description), fetch=False)
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        # Invalidate cache
        global courses_initialized
        courses_initialized = False
        
        new_course = {
            "course_id": course_id,
            "title": title,
            "description": description,
            "domain": domain,
            "difficulty": difficulty,
            "content_type": content_type,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": None
        }
        return {"success": True, "course_id": course_id, "course": new_course}
    
    return {"success": False, "error": "Failed to create course"}

def update_course(course_id, title="", description="", domain="", difficulty=""):
    """Update an existing course in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Check if course exists
    check_query = "SELECT path_id FROM jeseci_academy.learning_paths WHERE path_id = %s"
    try:
        existing = pg_manager.execute_query(check_query, (course_id,))
    except Exception as e:
        logger.error(f"Error checking course existence: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if not existing:
        return {"success": False, "error": "Course not found"}
    
    # Build dynamic update
    updates = []
    params = []
    
    if title:
        updates.append("title = %s")
        params.append(title)
    if description:
        updates.append("description = %s")
        params.append(description)
    if domain:
        updates.append("category = %s")
        params.append(domain)
    if difficulty:
        updates.append("difficulty = %s")
        params.append(difficulty)
    
    if not updates:
        return {"success": True, "message": "No fields to update"}
    
    updates.append("updated_at = NOW()")
    params.append(course_id)
    
    update_query = f"""
    UPDATE jeseci_academy.learning_paths 
    SET {', '.join(updates)}
    WHERE path_id = %s
    """
    
    try:
        result = pg_manager.execute_query(update_query, params, fetch=False)
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        global courses_initialized
        courses_initialized = False
        return {"success": True, "course_id": course_id}
    
    return {"success": False, "error": "Failed to update course"}

def delete_course(course_id, deleted_by=None):
    """Soft delete a course from PostgreSQL instead of hard delete
    
    Args:
        course_id: The path_id of the course to delete
        deleted_by: Username of the admin performing the deletion (for tracking)
    """
    pg_manager = get_postgres_manager()
    
    # Get old values before updating for audit log
    check_query = "SELECT path_id, title, description, category, difficulty, is_deleted FROM jeseci_academy.learning_paths WHERE path_id = %s"
    try:
        existing = pg_manager.execute_query(check_query, (course_id,))
    except Exception as e:
        logger.error(f"Error checking course existence for delete: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if not existing:
        return {"success": False, "error": "Course not found"}
    
    old_values = {
        'path_id': existing[0]['path_id'],
        'title': existing[0]['title'],
        'description': existing[0]['description'],
        'category': existing[0]['category'],
        'difficulty': existing[0]['difficulty'],
        'is_deleted': existing[0]['is_deleted']
    }
    
    # Perform soft delete instead of hard delete
    current_time = datetime.datetime.now()
    soft_delete_query = """
    UPDATE jeseci_academy.learning_paths 
    SET is_deleted = true, deleted_at = %s, deleted_by = %s, updated_at = NOW()
    WHERE path_id = %s
    """
    try:
        result = pg_manager.execute_query(soft_delete_query, (current_time, deleted_by, course_id,), fetch=False)
    except Exception as e:
        logger.error(f"Error soft deleting course: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        # Log audit entry
        audit_module.log_soft_delete(
            table_name="learning_paths",
            record_id=course_id,
            old_values=old_values,
            performed_by=deleted_by,
            additional_context={"action": "delete_course", "course_title": old_values.get('title')}
        )
        
        global courses_initialized
        courses_initialized = False
        return {"success": True, "course_id": course_id, "message": "Course deleted successfully (soft delete)"}
    
    return {"success": False, "error": "Failed to delete course"}

def restore_course(course_id, restored_by=None):
    """Restore a soft-deleted course
    
    Args:
        course_id: The path_id of the course to restore
        restored_by: Username of the admin performing the restore (for tracking)
    """
    pg_manager = get_postgres_manager()
    
    # Get old values before updating for audit log
    check_query = "SELECT path_id, title, description, category, difficulty, is_deleted FROM jeseci_academy.learning_paths WHERE path_id = %s AND is_deleted = true"
    try:
        existing = pg_manager.execute_query(check_query, (course_id,))
    except Exception as e:
        logger.error(f"Error checking course existence for restore: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if not existing:
        return {"success": False, "error": "Course not found or not deleted"}
    
    old_values = {
        'path_id': existing[0]['path_id'],
        'title': existing[0]['title'],
        'description': existing[0]['description'],
        'category': existing[0]['category'],
        'difficulty': existing[0]['difficulty'],
        'is_deleted': existing[0]['is_deleted']
    }
    
    # Restore the course
    restore_query = """
    UPDATE jeseci_academy.learning_paths 
    SET is_deleted = false, deleted_at = null, deleted_by = null, updated_at = NOW()
    WHERE path_id = %s
    """
    try:
        result = pg_manager.execute_query(restore_query, (course_id,), fetch=False)
    except Exception as e:
        logger.error(f"Error restoring course: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        # Log audit entry
        audit_module.log_restore(
            table_name="learning_paths",
            record_id=course_id,
            old_values=old_values,
            performed_by=restored_by,
            additional_context={"action": "restore_course", "course_title": old_values.get('title')}
        )
        
        global courses_initialized
        courses_initialized = False
        return {"success": True, "course_id": course_id, "message": "Course restored successfully"}
    
    return {"success": False, "error": "Failed to restore course"}

def get_deleted_courses():
    """Get all soft-deleted courses (for trash view)
    
    Returns:
        List of soft-deleted course objects with deletion metadata
    """
    pg_manager = get_postgres_manager()
    
    query = """
    SELECT path_id, name, title, category, difficulty, 
           estimated_duration, description, is_published, created_at, 
           updated_at, deleted_at, deleted_by
    FROM jeseci_academy.learning_paths
    WHERE is_deleted = true
    ORDER BY deleted_at DESC
    """
    
    try:
        result = pg_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error getting deleted courses: {e}")
        return []
    
    courses = []
    for row in result or []:
        courses.append({
            "course_id": row.get('path_id'),
            "title": row.get('title'),
            "description": row.get('description'),
            "domain": row.get('category') or "",
            "difficulty": row.get('difficulty') or "beginner",
            "content_type": "interactive",
            "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
            "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None,
            "deleted_at": row.get('deleted_at').isoformat() if row.get('deleted_at') else None,
            "deleted_by": row.get('deleted_by')
        })
    
    return courses

# ==============================================================================
# CONCEPTS STORAGE (Neo4j - Graph relationships)
# ==============================================================================

def initialize_concepts():
    """Initialize concepts from Neo4j graph database"""
    neo4j_manager = get_neo4j_manager()
    
    try:
        query = """
        MATCH (c:Concept)
        RETURN c.concept_id AS concept_id, c.name AS name, c.display_name AS display_name,
               c.category AS category, c.subcategory AS subcategory, c.difficulty_level AS difficulty_level,
               c.complexity_score AS complexity_score, c.cognitive_load AS cognitive_load,
               c.domain AS domain, c.description AS description, c.icon AS icon,
               c.key_terms AS key_terms, c.synonyms AS synonyms
        ORDER BY c.name
        """
        
        result = neo4j_manager.execute_query(query)
        
        concepts = {}
        if result:
            for row in result:
                concept_id = row.get('concept_id')
                concepts[concept_id] = {
                    "concept_id": concept_id,
                    "name": row.get('name'),
                    "display_name": row.get('display_name') or row.get('name'),
                    "category": row.get('category') or "",
                    "subcategory": row.get('subcategory') or "",
                    "difficulty_level": row.get('difficulty_level') or "beginner",
                    "complexity_score": row.get('complexity_score') or 0,
                    "cognitive_load": row.get('cognitive_load') or 0,
                    "domain": row.get('domain') or "",
                    "description": row.get('description') or "",
                    "icon": row.get('icon') or "default",
                    "key_terms": row.get('key_terms') or [],
                    "synonyms": row.get('synonyms') or []
                }
        
        return concepts
    except Exception as e:
        logger.error(f"Error initializing concepts: {e}")
        return {}

def get_all_concepts():
    """Get all concepts from Neo4j as a list"""
    concepts_dict = initialize_concepts()
    return list(concepts_dict.values())

def get_concept_by_id(concept_id):
    """Get a specific concept from Neo4j"""
    neo4j_manager = get_neo4j_manager()
    
    try:
        query = """
        MATCH (c:Concept {concept_id: $concept_id})
        RETURN c.concept_id AS concept_id, c.name AS name, c.display_name AS display_name,
               c.category AS category, c.subcategory AS subcategory, c.difficulty_level AS difficulty_level,
               c.complexity_score AS complexity_score, c.cognitive_load AS cognitive_load,
               c.domain AS domain, c.description AS description, c.icon AS icon,
               c.key_terms AS key_terms, c.synonyms AS synonyms
        """
        
        result = neo4j_manager.execute_query(query, {"concept_id": concept_id})
        
        if result and len(result) > 0:
            row = result[0]
            return {
                "concept_id": row.get('concept_id'),
                "name": row.get('name'),
                "display_name": row.get('display_name') or row.get('name'),
                "category": row.get('category') or "",
                "subcategory": row.get('subcategory') or "",
                "difficulty_level": row.get('difficulty_level') or "beginner",
                "complexity_score": row.get('complexity_score') or 0,
                "cognitive_load": row.get('cognitive_load') or 0,
                "domain": row.get('domain') or "",
                "description": row.get('description') or "",
                "icon": row.get('icon') or "default",
                "key_terms": row.get('key_terms') or [],
                "synonyms": row.get('synonyms') or []
            }
        
        return None
    except Exception as e:
        logger.error(f"Error getting concept by ID: {e}")
        return None

def create_concept(name, display_name, category, difficulty_level, domain, description="", icon=""):
    """Create a new concept in Neo4j"""
    neo4j_manager = get_neo4j_manager()
    
    # Generate concept ID
    concept_id = "concept_" + name.lower().replace(" ", "_").replace("-", "_")[0:20] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
    
    query = """
    MERGE (c:Concept {concept_id: $concept_id})
    SET c.name = $name,
        c.display_name = $display_name,
        c.category = $category,
        c.difficulty_level = $difficulty_level,
        c.domain = $domain,
        c.description = $description,
        c.icon = $icon,
        c.created_at = timestamp()
    RETURN c.concept_id AS concept_id
    """
    
    try:
        result = neo4j_manager.execute_write(query, {
            "concept_id": concept_id,
            "name": name,
            "display_name": display_name or name,
            "category": category,
            "difficulty_level": difficulty_level,
            "domain": domain,
            "description": description,
            "icon": icon or "default"
        })
    except Exception as e:
        logger.error(f"Error creating concept: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result:
        new_concept = {
            "concept_id": concept_id,
            "name": name,
            "display_name": display_name or name,
            "category": category,
            "difficulty_level": difficulty_level,
            "domain": domain,
            "description": description,
            "icon": icon or "default"
        }
        return {"success": True, "concept_id": concept_id, "concept": new_concept}
    
    return {"success": False, "error": "Failed to create concept"}

def get_concept_relationships(concept_id):
    """Get all relationships for a concept from Neo4j"""
    neo4j_manager = get_neo4j_manager()
    
    try:
        query = """
        MATCH (c:Concept {concept_id: $concept_id})
        OPTIONAL MATCH (c)-[r:PREREQUISITE]->(prereq:Concept)
        OPTIONAL MATCH (c)-[:RELATED_TO]->(related:Concept)
        OPTIONAL MATCH (c)<-[:PREREQUISITE]-(depends:Concept)
        RETURN c,
               collect(DISTINCT {id: prereq.concept_id, name: prereq.name, type: 'prerequisite'}) AS prerequisites,
               collect(DISTINCT {id: related.concept_id, name: related.name, type: 'related'}) AS related,
               collect(DISTINCT {id: depends.concept_id, name: depends.name, type: 'depends_on'}) AS depends_on
        """
        
        result = neo4j_manager.execute_query(query, {"concept_id": concept_id})
        
        if result and len(result) > 0:
            return {
                "prerequisites": result[0].get('prerequisites', []),
                "related": result[0].get('related', []),
                "depends_on": result[0].get('depends_on', [])
            }
        
        return {"prerequisites": [], "related": [], "depends_on": []}
    except Exception as e:
        logger.error(f"Error getting concept relationships: {e}")
        return {"prerequisites": [], "related": [], "depends_on": []}

def add_concept_relationship(source_id, target_id, relationship_type, strength=1):
    """Add a relationship between two concepts in Neo4j"""
    neo4j_manager = get_neo4j_manager()
    
    valid_types = ['PREREQUISITE', 'RELATED_TO', 'PART_OF', 'BUILDS_UPON']
    if relationship_type.upper() not in valid_types:
        return {"success": False, "error": f"Invalid relationship type. Valid types: {valid_types}"}
    
    query = f"""
    MATCH (a:Concept {{concept_id: $source_id}})
    MATCH (b:Concept {{concept_id: $target_id}})
    MERGE (a)-[r:{relationship_type.upper()}]->(b)
    SET r.strength = $strength, r.created_at = timestamp()
    RETURN a.name, type(r), b.name
    """
    
    try:
        result = neo4j_manager.execute_write(query, {
            "source_id": source_id,
            "target_id": target_id,
            "strength": strength
        })
    except Exception as e:
        logger.error(f"Error adding concept relationship: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result:
        return {"success": True, "message": f"Relationship {relationship_type} created"}
    
    return {"success": False, "error": "Failed to create relationship"}


def delete_concept_relationship(source_id, target_id, relationship_type):
    """Delete a relationship between two concepts in Neo4j"""
    neo4j_manager = get_neo4j_manager()
    
    valid_types = ['PREREQUISITE', 'RELATED_TO', 'PART_OF', 'BUILDS_UPON']
    if relationship_type.upper() not in valid_types:
        return {"success": False, "error": f"Invalid relationship type. Valid types: {valid_types}"}
    
    query = f"""
    MATCH (a:Concept {{concept_id: $source_id}})-[r:{relationship_type.upper()}]->(b:Concept {{concept_id: $target_id}})
    DELETE r
    RETURN COUNT(r) as deleted_count
    """
    
    try:
        result = neo4j_manager.execute_write(query, {
            "source_id": source_id,
            "target_id": target_id
        })
        
        deleted = result[0].get('deleted_count', 0) if result else 0
        
        if deleted > 0:
            return {"success": True, "message": f"Relationship deleted"}
        else:
            return {"success": False, "error": "Relationship not found"}
            
    except Exception as e:
        logger.error(f"Error deleting concept relationship: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}


def get_all_concept_relationships():
    """Get all concept relationships from Neo4j"""
    neo4j_manager = get_neo4j_manager()
    
    query = """
    MATCH (a:Concept)-[r:PREREQUISITE|RELATED_TO|PART_OF|BUILDS_UPON]->(b:Concept)
    RETURN a.concept_id as source_id, a.name as source_name, a.display_name as source_display,
           b.concept_id as target_id, b.name as target_name, b.display_name as target_display,
           type(r) as relationship_type, r.strength as strength
    ORDER BY a.name, type(r)
    """
    
    try:
        result = neo4j_manager.execute_query(query)
        
        relationships = []
        for row in result or []:
            relationships.append({
                "source_id": row.get('source_id'),
                "source_name": row.get('source_name'),
                "source_display": row.get('source_display') or row.get('source_name'),
                "target_id": row.get('target_id'),
                "target_name": row.get('target_name'),
                "target_display": row.get('target_display') or row.get('target_name'),
                "relationship_type": row.get('relationship_type'),
                "strength": row.get('strength', 1)
            })
        
        return {"success": True, "relationships": relationships}
        
    except Exception as e:
        logger.error(f"Error getting all relationships: {e}")
        return {"success": False, "error": str(e), "relationships": []}


# ==============================================================================
# LEARNING PATHS STORAGE (PostgreSQL + Neo4j)
# ==============================================================================

def initialize_paths():
    """Initialize learning paths from PostgreSQL"""
    global paths_cache, paths_initialized
    
    if paths_initialized:
        return paths_cache
    
    with content_lock:
        if paths_initialized:
            return paths_cache
            
        pg_manager = get_postgres_manager()
        
        # Query without concept_count since it doesn't exist in the schema
        # We'll get concept_count from a separate count query if needed
        try:
            query = """
            SELECT path_id, name, title, category, difficulty, 
                   estimated_duration, description, created_at,
                   target_audience
            FROM jeseci_academy.learning_paths
            WHERE is_deleted = false
            ORDER BY created_at DESC
            """
            
            result = pg_manager.execute_query(query)
            
            paths_cache = {}
            if result:
                for row in result:
                    path_id = row.get('path_id')
                    paths_cache[path_id] = {
                        "path_id": path_id,
                        "title": row.get('title'),
                        "description": row.get('description'),
                        "courses": [],
                        "concepts": [],
                        "difficulty": row.get('difficulty') or "beginner",
                        "total_modules": 0,  # Default since concept_count column doesn't exist
                        "duration": str(row.get('estimated_duration') or 0) + " minutes",
                        "target_audience": row.get('target_audience') or "",
                        "concept_count": 0  # Default since concept_count column doesn't exist
                    }
            
            paths_initialized = True
            return paths_cache
        except Exception as e:
            logger.error(f"Error initializing paths: {e}")
            paths_initialized = False
            return {}

def get_all_paths():
    """Get all learning paths"""
    initialize_paths()
    with content_lock:
        return list(paths_cache.values())

def get_path_by_id(path_id):
    """Get a specific learning path"""
    initialize_paths()
    with content_lock:
        return paths_cache.get(path_id)

def create_path(title, description, courses, concepts, difficulty, duration, target_audience=""):
    """Create a new learning path in both PostgreSQL and Neo4j"""
    pg_manager = get_postgres_manager()
    neo4j_manager = get_neo4j_manager()
    
    # Generate path ID
    path_id = "path_" + title.lower().replace(" ", "_").replace("-", "_")[0:15] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
    name = title.lower().replace(" ", "_").replace("-", "_")
    
    # Parse duration to integer (minutes)
    duration_minutes = 0
    try:
        if "week" in duration.lower():
            weeks = int(duration.lower().replace("weeks", "").replace("week", "").strip())
            duration_minutes = weeks * 7 * 24 * 60
        elif "hour" in duration.lower():
            hours = int(duration.lower().replace("hours", "").replace("hour", "").strip())
            duration_minutes = hours * 60
        else:
            duration_minutes = int(duration)
    except:
        duration_minutes = 480  # Default 8 hours
    
    # Insert into PostgreSQL
    insert_query = """
    INSERT INTO jeseci_academy.learning_paths 
    (path_id, name, title, category, difficulty, estimated_duration, description, target_audience, is_published, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true, NOW())
    """
    
    pg_result = None
    try:
        pg_result = pg_manager.execute_query(insert_query, 
            (path_id, name, title, "Learning Path", difficulty, duration_minutes, description, target_audience), fetch=False)
    except Exception as e:
        logger.error(f"Error creating learning path in PostgreSQL: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    # Also create node in Neo4j for graph relationships
    neo4j_success = True
    try:
        create_path_query = """
        MERGE (p:LearningPath {path_id: $path_id})
        SET p.name = $name,
            p.title = $title,
            p.description = $description,
            p.category = 'Learning Path',
            p.difficulty = $difficulty,
            p.estimated_duration = $estimated_duration,
            p.target_audience = $target_audience,
            p.created_at = datetime()
        """
        
        neo4j_manager.execute_query(create_path_query, {
            "path_id": path_id,
            "name": name,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "estimated_duration": duration_minutes,
            "target_audience": target_audience
        })
        
        # Link concepts to path in Neo4j
        for i, concept_name in enumerate(concepts or []):
            concept_id = f"jac_{concept_name}" if not concept_name.startswith("jac_") else concept_name
            
            link_query = """
            MATCH (p:LearningPath {path_id: $path_id})
            MATCH (c:Concept {name: $concept_name})
            MERGE (p)-[r:PathContains {order_index: $order, is_required: true, created_at: datetime()}]->(c)
            """
            
            try:
                neo4j_manager.execute_query(link_query, {
                    "path_id": path_id,
                    "concept_name": concept_name,
                    "order": i + 1
                })
            except Exception as e:
                logger.warning(f"Could not link concept {concept_name} to path: {e}")
                
    except Exception as e:
        logger.error(f"Error creating learning path in Neo4j: {e}")
        neo4j_success = False
    
    if pg_result or pg_result is not None:
        # Invalidate cache
        global paths_initialized
        paths_initialized = False
        
        new_path = {
            "path_id": path_id,
            "title": title,
            "description": description,
            "courses": courses,
            "concepts": concepts,
            "difficulty": difficulty,
            "total_modules": len(courses or []) + len(concepts or []),
            "duration": duration,
            "target_audience": target_audience,
            "neo4j_synced": neo4j_success
        }
        return {"success": True, "path_id": path_id, "path": new_path}
    
    return {"success": False, "error": "Failed to create learning path"}

def get_recommended_concepts(user_id, completed_concept_ids, limit=5):
    """Get personalized learning recommendations from Neo4j"""
    neo4j_manager = get_neo4j_manager()
    
    query = """
    MATCH (c:Concept)
    WHERE NOT c.concept_id IN $completed_ids
    OPTIONAL MATCH (c)-[:PREREQUISITE|RELATED_TO]->(prereq:Concept)
    WITH c, COUNT(prereq) as prereq_count
    WHERE prereq_count = 0 OR prereq_count <= 2
    RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
           c.category AS category, c.difficulty_level AS difficulty_level, c.description AS description
    LIMIT $limit
    """
    
    try:
        result = neo4j_manager.execute_query(query, {
            "completed_ids": completed_concept_ids or [],
            "limit": limit
        })
    except Exception as e:
        logger.error(f"Error getting recommended concepts: {e}")
        return []
    
    recommendations = []
    for row in result or []:
        recommendations.append({
            "concept_id": row.get('id'),
            "name": row.get('name'),
            "display_name": row.get('display_name'),
            "category": row.get('category'),
            "difficulty": row.get('difficulty_level'),
            "description": row.get('description')
        })
    
    return recommendations
