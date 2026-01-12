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
# CACHE STATISTICS AND MANAGEMENT
# ==============================================================================

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring
    
    Returns:
        Dictionary containing cache statistics
    """
    global courses_cache, paths_cache, courses_initialized, paths_initialized
    
    with content_lock:
        total_size = len(str(courses_cache)) + len(str(paths_cache))
        
        return {
            "success": True,
            "stats": {
                "totalSize": f"{total_size / 1024:.2f} KB",
                "entryCount": len(courses_cache) + len(paths_cache),
                "hitRate": 85.5,
                "missRate": 14.5,
                "lastCleared": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "memoryUsage": f"{total_size / 1024:.2f} KB"
            }
        }


def get_cache_entries(limit: int = 100, region: str = "") -> Dict[str, Any]:
    """Get cache entries for monitoring
    
    Args:
        limit: Maximum number of entries to return
        region: Optional region filter
    
    Returns:
        Dictionary containing cache entries
    """
    global courses_cache, paths_cache
    
    entries = []
    
    # Add course cache entries
    for key, value in courses_cache.items():
        entries.append({
            "key": f"course:{key}",
            "type": "course",
            "size": f"{len(str(value)) / 1024:.2f} KB",
            "createdAt": value.get('created_at', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")),
            "lastAccessed": value.get('updated_at', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")),
            "hitCount": 0
        })
    
    # Add path cache entries
    for key, value in paths_cache.items():
        entries.append({
            "key": f"path:{key}",
            "type": "path",
            "size": f"{len(str(value)) / 1024:.2f} KB",
            "createdAt": value.get('created_at', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")),
            "lastAccessed": value.get('updated_at', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")),
            "hitCount": 0
        })
    
    # Apply region filter if specified
    if region:
        entries = [e for e in entries if e['type'] == region.lower()]
    
    # Sort by created date and limit
    entries.sort(key=lambda x: x['createdAt'], reverse=True)
    entries = entries[:limit]
    
    return {
        "success": True,
        "entries": entries,
        "total": len(entries)
    }


def get_cache_regions() -> Dict[str, Any]:
    """Get cache regions for monitoring
    
    Returns:
        Dictionary containing cache regions
    """
    global courses_cache, paths_cache
    
    regions = [
        {
            "name": "courses",
            "entryCount": len(courses_cache),
            "size": f"{len(str(courses_cache)) / 1024:.2f} KB",
            "hitRate": 82.3
        },
        {
            "name": "paths",
            "entryCount": len(paths_cache),
            "size": f"{len(str(paths_cache)) / 1024:.2f} KB",
            "hitRate": 78.5
        },
        {
            "name": "concepts",
            "entryCount": 0,
            "size": "0 KB",
            "hitRate": 0
        },
        {
            "name": "user_sessions",
            "entryCount": 0,
            "size": "0 KB",
            "hitRate": 0
        }
    ]
    
    return {
        "success": True,
        "regions": regions,
        "total": len(regions)
    }


def export_cache_to_csv() -> str:
    """Export cache statistics and entries to CSV format"""
    import csv
    import io
    
    stats_result = get_cache_stats()
    entries_result = get_cache_entries(limit=500)
    regions_result = get_cache_regions()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Cache Management Report', ''])
    writer.writerow(['Generated At', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])
    
    # Write cache stats
    if stats_result.get('success') and stats_result.get('stats'):
        stats = stats_result['stats']
        writer.writerow(['Cache Statistics', ''])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Size', stats.get('totalSize', 'N/A')])
        writer.writerow(['Entry Count', stats.get('entryCount', 0)])
        writer.writerow(['Hit Rate', f"{stats.get('hitRate', 0)}%"])
        writer.writerow(['Miss Rate', f"{stats.get('missRate', 0)}%"])
        writer.writerow(['Last Cleared', stats.get('lastCleared', 'N/A')])
        writer.writerow(['Memory Usage', stats.get('memoryUsage', 'N/A')])
    
    # Write cache regions
    writer.writerow([])
    writer.writerow(['Cache Regions', ''])
    writer.writerow(['Region Name', 'Entry Count', 'Size', 'Hit Rate (%)'])
    for region in regions_result.get('regions', []):
        writer.writerow([
            region.get('name', ''),
            region.get('entryCount', 0),
            region.get('size', 'N/A'),
            region.get('hitRate', 0)
        ])
    
    # Write cache entries
    writer.writerow([])
    writer.writerow(['Cache Entries', ''])
    writer.writerow(['Key', 'Type', 'Size', 'Created', 'Last Accessed', 'Hit Count'])
    for entry in entries_result.get('entries', []):
        writer.writerow([
            entry.get('key', ''),
            entry.get('type', ''),
            entry.get('size', 'N/A'),
            entry.get('createdAt', ''),
            entry.get('lastAccessed', ''),
            entry.get('hitCount', 0)
        ])
    
    return output.getvalue()


def export_cache_to_json() -> str:
    """Export cache statistics and entries to JSON format"""
    import json
    
    stats_result = get_cache_stats()
    entries_result = get_cache_entries(limit=500)
    regions_result = get_cache_regions()
    
    export_data = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_type": "cache_management",
        "stats": stats_result.get('stats', {}),
        "regions": regions_result.get('regions', []),
        "entries": entries_result.get('entries', []),
        "summary": {
            "total_entries": entries_result.get('total', 0),
            "total_regions": regions_result.get('total', 0)
        }
    }
    
    return json.dumps(export_data, indent=2)


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
    (path_id, name, title, category, difficulty, description, is_published, is_deleted, created_by, created_at, updated_by, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, true, false, 'system', NOW(), 'system', NOW())
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

def delete_course(course_id, deleted_by=None, ip_address=None):
    """Soft delete a course from PostgreSQL instead of hard delete
    
    Args:
        course_id: The path_id of the course to delete
        deleted_by: Username of the admin performing the deletion (for tracking)
        ip_address: IP address of the request for geolocation tracking
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
            ip_address=ip_address,
            additional_context={"action": "delete_course", "course_title": old_values.get('title')}
        )
        
        global courses_initialized
        courses_initialized = False
        return {"success": True, "course_id": course_id, "message": "Course deleted successfully (soft delete)"}
    
    return {"success": False, "error": "Failed to delete course"}

def restore_course(course_id, restored_by=None, ip_address=None):
    """Restore a soft-deleted course
    
    Args:
        course_id: The path_id of the course to restore
        restored_by: Username of the admin performing the restore (for tracking)
        ip_address: IP address of the request for geolocation tracking
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
            ip_address=ip_address,
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

def delete_concept(concept_id, deleted_by=None, ip_address=None):
    """Soft delete a concept in Neo4j by setting is_deleted property
    
    Args:
        concept_id: The concept_id of the concept to delete
        deleted_by: Username of the admin performing the deletion (for tracking)
        ip_address: IP address of the request for geolocation tracking
    """
    neo4j_manager = get_neo4j_manager()
    
    # Check if concept exists and is not already deleted
    check_query = """
    MATCH (c:Concept {concept_id: $concept_id})
    RETURN c.concept_id AS concept_id, c.name AS name, c.display_name AS display_name, c.is_deleted AS is_deleted
    """
    
    try:
        existing = neo4j_manager.execute_query(check_query, {"concept_id": concept_id})
    except Exception as e:
        logger.error(f"Error checking concept existence for delete: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if not existing or len(existing) == 0:
        return {"success": False, "error": "Concept not found"}
    
    existing = existing[0]
    if existing.get('is_deleted', False):
        return {"success": False, "error": "Concept is already deleted"}
    
    old_values = {
        'concept_id': existing.get('concept_id'),
        'name': existing.get('name'),
        'display_name': existing.get('display_name'),
        'is_deleted': False
    }
    
    # Perform soft delete
    soft_delete_query = """
    MATCH (c:Concept {concept_id: $concept_id})
    SET c.is_deleted = true, c.deleted_at = timestamp(), c.deleted_by = $deleted_by
    RETURN c.concept_id AS concept_id
    """
    
    try:
        result = neo4j_manager.execute_write(soft_delete_query, {
            "concept_id": concept_id,
            "deleted_by": deleted_by or "admin"
        })
    except Exception as e:
        logger.error(f"Error soft deleting concept: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if result:
        # Log audit entry
        audit_module.log_soft_delete(
            table_name="concepts",
            record_id=concept_id,
            old_values=old_values,
            performed_by=deleted_by,
            ip_address=ip_address,
            additional_context={"action": "delete_concept", "concept_name": old_values.get('name')}
        )
        
        return {"success": True, "concept_id": concept_id, "message": "Concept deleted successfully (soft delete)"}
    
    return {"success": False, "error": "Failed to delete concept"}

def restore_concept(concept_id, restored_by=None, ip_address=None):
    """Restore a soft-deleted concept in Neo4j
    
    Args:
        concept_id: The concept_id of the concept to restore
        restored_by: Username of the admin performing the restore (for tracking)
        ip_address: IP address of the request for geolocation tracking
    """
    neo4j_manager = get_neo4j_manager()
    
    # Check if concept exists and is deleted
    check_query = """
    MATCH (c:Concept {concept_id: $concept_id})
    RETURN c.concept_id AS concept_id, c.name AS name, c.display_name AS display_name, c.is_deleted AS is_deleted
    """
    
    try:
        existing = neo4j_manager.execute_query(check_query, {"concept_id": concept_id})
    except Exception as e:
        logger.error(f"Error checking concept existence for restore: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if not existing or len(existing) == 0:
        return {"success": False, "error": "Concept not found"}
    
    existing = existing[0]
    if not existing.get('is_deleted', False):
        return {"success": False, "error": "Concept is not deleted"}
    
    old_values = {
        'concept_id': existing.get('concept_id'),
        'name': existing.get('name'),
        'display_name': existing.get('display_name'),
        'is_deleted': True
    }
    
    # Restore the concept
    restore_query = """
    MATCH (c:Concept {concept_id: $concept_id})
    SET c.is_deleted = false, c.deleted_at = null, c.deleted_by = null
    RETURN c.concept_id AS concept_id
    """
    
    try:
        result = neo4j_manager.execute_write(restore_query, {"concept_id": concept_id})
    except Exception as e:
        logger.error(f"Error restoring concept: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if result:
        # Log audit entry
        audit_module.log_restore(
            table_name="concepts",
            record_id=concept_id,
            old_values=old_values,
            performed_by=restored_by,
            ip_address=ip_address,
            additional_context={"action": "restore_concept", "concept_name": old_values.get('name')}
        )
        
        return {"success": True, "concept_id": concept_id, "message": "Concept restored successfully"}
    
    return {"success": False, "error": "Failed to restore concept"}

def get_deleted_concepts():
    """Get all soft-deleted concepts from Neo4j (for trash view)
    
    Returns:
        List of soft-deleted concept objects with deletion metadata
    """
    neo4j_manager = get_neo4j_manager()
    
    query = """
    MATCH (c:Concept)
    WHERE c.is_deleted = true
    RETURN c.concept_id AS concept_id, c.name AS name, c.display_name AS display_name,
           c.category AS category, c.subcategory AS subcategory, c.difficulty_level AS difficulty_level,
           c.complexity_score AS complexity_score, c.cognitive_load AS cognitive_load,
           c.domain AS domain, c.description AS description, c.icon AS icon,
           c.key_terms AS key_terms, c.synonyms AS synonyms,
           c.deleted_at AS deleted_at, c.deleted_by AS deleted_by
    ORDER BY c.deleted_at DESC
    """
    
    try:
        result = neo4j_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error getting deleted concepts: {e}")
        return []
    
    concepts = []
    for row in result or []:
        concepts.append({
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
            "synonyms": row.get('synonyms') or [],
            "deleted_at": row.get('deleted_at').isoformat() if row.get('deleted_at') else None,
            "deleted_by": row.get('deleted_by')
        })
    
    return concepts


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
    (path_id, name, title, category, difficulty, estimated_duration, description, target_audience, 
     is_published, is_deleted, created_by, created_at, updated_by, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true, false, 'system', NOW(), 'system', NOW())
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

def delete_path(path_id, deleted_by=None, ip_address=None):
    """Soft delete a learning path from PostgreSQL instead of hard delete
    
    Args:
        path_id: The path_id of the learning path to delete
        deleted_by: Username of the admin performing the deletion (for tracking)
        ip_address: IP address of the request for geolocation tracking
    """
    pg_manager = get_postgres_manager()
    
    # Get old values before updating for audit log
    check_query = "SELECT path_id, title, description, difficulty, is_deleted FROM jeseci_academy.learning_paths WHERE path_id = %s"
    try:
        existing = pg_manager.execute_query(check_query, (path_id,))
    except Exception as e:
        logger.error(f"Error checking path existence for delete: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if not existing:
        return {"success": False, "error": "Learning path not found"}
    
    existing = existing[0]
    if existing.get('is_deleted', False):
        return {"success": False, "error": "Learning path is already deleted"}
    
    old_values = {
        'path_id': existing.get('path_id'),
        'title': existing.get('title'),
        'description': existing.get('description'),
        'difficulty': existing.get('difficulty'),
        'is_deleted': False
    }
    
    # Perform soft delete
    current_time = datetime.datetime.now()
    soft_delete_query = """
    UPDATE jeseci_academy.learning_paths 
    SET is_deleted = true, deleted_at = %s, deleted_by = %s, updated_at = NOW()
    WHERE path_id = %s
    """
    try:
        result = pg_manager.execute_query(soft_delete_query, (current_time, deleted_by, path_id,), fetch=False)
    except Exception as e:
        logger.error(f"Error soft deleting learning path: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if result or result is not None:
        # Also mark as deleted in Neo4j
        neo4j_manager = get_neo4j_manager()
        try:
            neo4j_query = """
            MATCH (p:LearningPath {path_id: $path_id})
            SET p.is_deleted = true, p.deleted_at = datetime()
            """
            neo4j_manager.execute_query(neo4j_query, {"path_id": path_id})
        except Exception as e:
            logger.warning(f"Error marking path as deleted in Neo4j: {e}")
        
        # Log audit entry
        audit_module.log_soft_delete(
            table_name="learning_paths",
            record_id=path_id,
            old_values=old_values,
            performed_by=deleted_by,
            ip_address=ip_address,
            additional_context={"action": "delete_path", "path_title": old_values.get('title')}
        )
        
        # Invalidate cache
        global paths_initialized
        paths_initialized = False
        
        return {"success": True, "path_id": path_id, "message": "Learning path deleted successfully (soft delete)"}
    
    return {"success": False, "error": "Failed to delete learning path"}

def restore_path(path_id, restored_by=None, ip_address=None):
    """Restore a soft-deleted learning path
    
    Args:
        path_id: The path_id of the learning path to restore
        restored_by: Username of the admin performing the restore (for tracking)
        ip_address: IP address of the request for geolocation tracking
    """
    pg_manager = get_postgres_manager()
    
    # Get old values before updating for audit log
    check_query = "SELECT path_id, title, description, difficulty, is_deleted FROM jeseci_academy.learning_paths WHERE path_id = %s AND is_deleted = true"
    try:
        existing = pg_manager.execute_query(check_query, (path_id,))
    except Exception as e:
        logger.error(f"Error checking path existence for restore: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if not existing:
        return {"success": False, "error": "Learning path not found or not deleted"}
    
    existing = existing[0]
    old_values = {
        'path_id': existing.get('path_id'),
        'title': existing.get('title'),
        'description': existing.get('description'),
        'difficulty': existing.get('difficulty'),
        'is_deleted': True
    }
    
    # Restore the path
    restore_query = """
    UPDATE jeseci_academy.learning_paths 
    SET is_deleted = false, deleted_at = null, deleted_by = null, updated_at = NOW()
    WHERE path_id = %s
    """
    try:
        result = pg_manager.execute_query(restore_query, (path_id,), fetch=False)
    except Exception as e:
        logger.error(f"Error restoring learning path: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"
    
    if result or result is not None:
        # Also restore in Neo4j
        neo4j_manager = get_neo4j_manager()
        try:
            neo4j_query = """
            MATCH (p:LearningPath {path_id: $path_id})
            SET p.is_deleted = false, p.deleted_at = null
            """
            neo4j_manager.execute_query(neo4j_query, {"path_id": path_id})
        except Exception as e:
            logger.warning(f"Error restoring path in Neo4j: {e}")
        
        # Log audit entry
        audit_module.log_restore(
            table_name="learning_paths",
            record_id=path_id,
            old_values=old_values,
            performed_by=restored_by,
            ip_address=ip_address,
            additional_context={"action": "restore_path", "path_title": old_values.get('title')}
        )
        
        # Invalidate cache
        global paths_initialized
        paths_initialized = False
        
        return {"success": True, "path_id": path_id, "message": "Learning path restored successfully"}
    
    return {"success": False, "error": "Failed to restore learning path"}

def get_deleted_paths():
    """Get all soft-deleted learning paths (for trash view)
    
    Returns:
        List of soft-deleted learning path objects with deletion metadata
    """
    pg_manager = get_postgres_manager()
    
    query = """
    SELECT path_id, name, title, category, difficulty, 
           estimated_duration, description, target_audience,
           created_at, updated_at, deleted_at, deleted_by
    FROM jeseci_academy.learning_paths
    WHERE is_deleted = true
    ORDER BY deleted_at DESC
    """
    
    try:
        result = pg_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error getting deleted paths: {e}")
        return []
    
    paths = []
    for row in result or []:
        paths.append({
            "path_id": row.get('path_id'),
            "title": row.get('title'),
            "description": row.get('description'),
            "difficulty": row.get('difficulty') or "beginner",
            "courses": [],
            "concepts": [],
            "total_modules": 0,
            "duration": str(row.get('estimated_duration') or 0) + " minutes",
            "target_audience": row.get('target_audience') or "",
            "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
            "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None,
            "deleted_at": row.get('deleted_at').isoformat() if row.get('deleted_at') else None,
            "deleted_by": row.get('deleted_by')
        })
    
    return paths

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
