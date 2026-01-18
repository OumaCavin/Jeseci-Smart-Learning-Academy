# Admin AI content storage using PostgreSQL database
# Uses AIGeneratedContent and AIUsageStats models for persistent storage

import os
import datetime
import logging
from typing import Optional, List, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

# Import database utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))
from database import get_postgres_manager


# ==============================================================================
# AI DOMAINS (fetched from database)
# ==============================================================================

def get_ai_domains():
    """Get available AI domains from database"""
    pg_manager = get_postgres_manager()
    
    try:
        query = """
        SELECT domain_id, name, slug, description, icon, color, is_active
        FROM jeseci_academy.domains
        WHERE is_active = true
        ORDER BY name ASC
        """
        
        result = pg_manager.execute_query(query)
        
        domains = []
        for row in result or []:
            domains.append({
                "id": row.get('domain_id'),
                "name": row.get('name'),
                "description": row.get('description') or f"{row.get('name')} learning materials",
                "icon": row.get('icon') or "📚",
                "color": row.get('color') or "#2563eb",
                "is_active": row.get('is_active', True)
            })
        
        return domains
    except Exception as e:
        logger.error(f"Error getting AI domains from database: {e}")
        # Fallback to empty list if database query fails
        return []


# ==============================================================================
# AI GENERATED CONTENT STORAGE
# ==============================================================================

def get_all_ai_content() -> List[Dict[str, Any]]:
    """Get all non-deleted AI generated content from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    try:
        query = """
        SELECT content_id, concept_name, domain, difficulty, content, 
               related_concepts, generated_by, model, tokens_used, generated_at
        FROM jeseci_academy.ai_generated_content
        WHERE is_deleted = false
        ORDER BY generated_at DESC
        """
        
        result = pg_manager.execute_query(query)
        
        content_list = []
        for row in result or []:
            content_list.append({
                "content_id": row.get('content_id'),
                "concept_name": row.get('concept_name'),
                "domain": row.get('domain'),
                "difficulty": row.get('difficulty'),
                "content": row.get('content'),
                "related_concepts": row.get('related_concepts'),
                "generated_by": row.get('generated_by'),
                "model": row.get('model') or "openai",
                "tokens_used": row.get('tokens_used'),
                "generated_at": row.get('generated_at').isoformat() if row.get('generated_at') else None
            })
        
        return content_list
    except Exception as e:
        logger.error(f"Error getting all AI content: {e}")
        return []


def save_ai_content(concept_name: str, domain: str, difficulty: str, content: str, 
                   generated_by: str, related_concepts: Optional[List[str]] = None,
                   tokens_used: Optional[int] = None, model: str = "openai") -> Dict[str, Any]:
    """Save AI generated content to PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Generate unique content ID
    timestamp = str(int(datetime.datetime.now().timestamp()))
    content_id = f"ai_{timestamp}"
    
    # Convert related_concepts to JSON format for storage
    related_concepts_json = related_concepts if related_concepts else []
    
    # Insert new AI generated content
    insert_query = """
    INSERT INTO jeseci_academy.ai_generated_content 
    (content_id, concept_name, domain, difficulty, content, related_concepts, 
     generated_by, model, tokens_used, is_deleted, created_by, created_at, updated_by, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, false, 'system', NOW(), 'system', NOW())
    """
    
    try:
        result = pg_manager.execute_query(insert_query, 
            (content_id, concept_name, domain, difficulty, content, 
             related_concepts_json, generated_by, model, tokens_used), fetch=False)
    except Exception as e:
        logger.error(f"Error saving AI content: {e}")
        return {"success": False, "error": f"Database error: {str(e)}", "content_id": None, "content": None}
    
    if result or result is not None:
        # Update stats
        update_ai_stats(domain, tokens_used)
        
        new_content = {
            "content_id": content_id,
            "concept_name": concept_name,
            "domain": domain,
            "difficulty": difficulty,
            "content": content,
            "related_concepts": related_concepts_json,
            "generated_by": generated_by,
            "model": model,
            "tokens_used": tokens_used,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        return {"success": True, "content_id": content_id, "content": new_content}
    
    return {"success": False, "error": "Failed to save AI content", "content_id": None, "content": None}


def get_ai_stats() -> Dict[str, Any]:
    """Get AI usage statistics from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Get total generations count
    count_query = "SELECT COUNT(*) as total FROM jeseci_academy.ai_generated_content WHERE is_deleted = false"
    try:
        count_result = pg_manager.execute_query(count_query)
        total_generations = count_result[0].get('total') if count_result else 0
    except Exception as e:
        logger.error(f"Error getting AI content count: {e}")
        total_generations = 0
    
    # Get total tokens used
    tokens_query = "SELECT COALESCE(SUM(tokens_used), 0) as total_tokens FROM jeseci_academy.ai_generated_content WHERE is_deleted = false"
    try:
        tokens_result = pg_manager.execute_query(tokens_query)
        total_tokens = tokens_result[0].get('total_tokens') if tokens_result else 0
    except Exception as e:
        logger.error(f"Error getting AI tokens count: {e}")
        total_tokens = 0
    
    # Get domain usage breakdown
    domain_query = """
    SELECT domain, COUNT(*) as count 
    FROM jeseci_academy.ai_generated_content 
    WHERE domain IS NOT NULL
    GROUP BY domain
    ORDER BY count DESC
    """
    try:
        domain_result = pg_manager.execute_query(domain_query)
    except Exception as e:
        logger.error(f"Error getting AI domain usage: {e}")
        domain_result = None
    
    domains_used = {}
    for row in domain_result or []:
        domain_name = row.get('domain')
        count = row.get('count')
        if domain_name:
            domains_used[domain_name] = count
    
    # Get recent generations (last 10)
    recent_query = """
    SELECT content_id, concept_name, domain, difficulty, model, generated_at
    FROM jeseci_academy.ai_generated_content
    WHERE is_deleted = false
    ORDER BY generated_at DESC
    LIMIT 10
    """
    try:
        recent_result = pg_manager.execute_query(recent_query)
    except Exception as e:
        logger.error(f"Error getting recent AI generations: {e}")
        recent_result = None
    
    recent_generations = []
    for row in recent_result or []:
        recent_generations.append({
            "content_id": row.get('content_id'),
            "concept_name": row.get('concept_name'),
            "domain": row.get('domain'),
            "difficulty": row.get('difficulty'),
            "model": row.get('model'),
            "generated_at": row.get('generated_at').isoformat() if row.get('generated_at') else None
        })
    
    return {
        "total_generations": total_generations,
        "total_tokens_used": total_tokens,
        "domains_used": domains_used,
        "recent_generations": recent_generations
    }


def update_ai_stats(domain: Optional[str], tokens_used: Optional[int]) -> None:
    """Update AI usage statistics in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Update total generations count
    # Note: This is a simple approach - for production, consider using aggregate functions
    # or maintaining a separate stats table that gets updated via triggers
    
    # Update domain usage if domain is provided
    if domain:
        # Check if domain entry exists
        check_query = """
        SELECT id FROM jeseci_academy.ai_usage_stats 
        WHERE stat_type = 'domain_usage' AND stat_key = %s
        """
        try:
            existing = pg_manager.execute_query(check_query, (domain,))
        except Exception as e:
            logger.error(f"Error checking AI domain stats: {e}")
            return
        
        if existing:
            # Update existing entry
            update_query = """
            UPDATE jeseci_academy.ai_usage_stats 
            SET stat_value = stat_value + 1, updated_at = NOW()
            WHERE stat_type = 'domain_usage' AND stat_key = %s
            """
            try:
                pg_manager.execute_query(update_query, (domain,), fetch=False)
            except Exception as e:
                logger.error(f"Error updating AI domain stats: {e}")
        else:
            # Insert new entry
            insert_query = """
            INSERT INTO jeseci_academy.ai_usage_stats (stat_type, stat_key, stat_value, is_deleted, created_by, created_at, updated_by, updated_at)
            VALUES ('domain_usage', %s, 1, false, 'system', NOW(), 'system', NOW())
            """
            try:
                pg_manager.execute_query(insert_query, (domain,), fetch=False)
            except Exception as e:
                logger.error(f"Error inserting AI domain stats: {e}")


def delete_ai_content(content_id: str, deleted_by: Optional[str] = None, ip_address: Optional[str] = None) -> Dict[str, Any]:
    """Soft delete AI generated content from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Check if content exists
    check_query = "SELECT content_id, concept_name, is_deleted FROM jeseci_academy.ai_generated_content WHERE content_id = %s"
    try:
        existing = pg_manager.execute_query(check_query, (content_id,))
    except Exception as e:
        logger.error(f"Error checking AI content existence for delete: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if not existing:
        return {"success": False, "error": "AI content not found"}
    
    existing = existing[0]
    
    # Check if already deleted
    if existing.get('is_deleted', False):
        return {"success": False, "error": "Content already deleted"}
    
    old_values = {
        'content_id': existing.get('content_id'),
        'concept_name': existing.get('concept_name'),
        'is_deleted': False
    }
    
    # Soft delete - update is_deleted flag
    delete_query = """
    UPDATE jeseci_academy.ai_generated_content 
    SET is_deleted = true, deleted_at = NOW(), deleted_by = %s, updated_at = NOW()
    WHERE content_id = %s
    """
    try:
        result = pg_manager.execute_query(delete_query, (deleted_by or 'system', content_id,), fetch=False)
    except Exception as e:
        logger.error(f"Error deleting AI content: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        # Log audit entry if audit module exists
        try:
            import audit_logger as audit_module
            audit_module.log_soft_delete(
                table_name="ai_generated_content",
                record_id=content_id,
                old_values=old_values,
                performed_by=deleted_by,
                ip_address=ip_address,
                additional_context={"action": "delete_ai_content", "concept_name": old_values.get('concept_name')}
            )
        except:
            pass  # Audit logging is optional
        
        return {"success": True, "content_id": content_id, "message": "AI content deleted successfully (soft delete)"}
    
    return {"success": False, "error": "Failed to delete AI content"}


def restore_ai_content(content_id: str, restored_by: Optional[str] = None, ip_address: Optional[str] = None) -> Dict[str, Any]:
    """Restore soft-deleted AI generated content"""
    pg_manager = get_postgres_manager()
    
    # Get old values before updating for audit log
    check_query = "SELECT content_id, concept_name, domain, is_deleted FROM jeseci_academy.ai_generated_content WHERE content_id = %s AND is_deleted = true"
    try:
        existing = pg_manager.execute_query(check_query, (content_id,))
    except Exception as e:
        logger.error(f"Error checking AI content existence for restore: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if not existing:
        return {"success": False, "error": "Content not found or not deleted"}
    
    existing = existing[0]
    old_values = {
        'content_id': existing.get('content_id'),
        'concept_name': existing.get('concept_name'),
        'domain': existing.get('domain'),
        'is_deleted': True
    }
    
    # Restore the content
    restore_query = """
    UPDATE jeseci_academy.ai_generated_content 
    SET is_deleted = false, deleted_at = null, deleted_by = null, updated_at = NOW()
    WHERE content_id = %s
    """
    try:
        result = pg_manager.execute_query(restore_query, (content_id,), fetch=False)
    except Exception as e:
        logger.error(f"Error restoring AI content: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        # Log audit entry if audit module exists
        try:
            import audit_logger as audit_module
            audit_module.log_restore(
                table_name="ai_generated_content",
                record_id=content_id,
                old_values=old_values,
                performed_by=restored_by,
                ip_address=ip_address,
                additional_context={"action": "restore_ai_content", "concept_name": old_values.get('concept_name')}
            )
        except:
            pass  # Audit logging is optional
        
        return {"success": True, "content_id": content_id, "message": "AI content restored successfully"}
    
    return {"success": False, "error": "Failed to restore AI content"}


def get_deleted_ai_content() -> List[Dict[str, Any]]:
    """Get all soft-deleted AI generated content (for trash view)"""
    pg_manager = get_postgres_manager()
    
    query = """
    SELECT content_id, concept_name, domain, difficulty, content, 
           related_concepts, generated_by, model, tokens_used, generated_at,
           deleted_at, deleted_by
    FROM jeseci_academy.ai_generated_content
    WHERE is_deleted = true
    ORDER BY deleted_at DESC
    """
    
    try:
        result = pg_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error getting deleted AI content: {e}")
        return []
    
    content_list = []
    for row in result or []:
        content_list.append({
            "content_id": row.get('content_id'),
            "concept_name": row.get('concept_name'),
            "domain": row.get('domain'),
            "difficulty": row.get('difficulty'),
            "content": row.get('content'),
            "related_concepts": row.get('related_concepts'),
            "generated_by": row.get('generated_by'),
            "model": row.get('model') or "openai",
            "tokens_used": row.get('tokens_used'),
            "generated_at": row.get('generated_at').isoformat() if row.get('generated_at') else None,
            "deleted_at": row.get('deleted_at').isoformat() if row.get('deleted_at') else None,
            "deleted_by": row.get('deleted_by')
        })
    
    return content_list


def export_ai_content_to_csv() -> str:
    """Export all AI generated content (active and deleted) to CSV format"""
    import csv
    import io
    
    pg_manager = get_postgres_manager()
    
    query = """
    SELECT content_id, concept_name, domain, difficulty, content, 
           related_concepts, generated_by, model, tokens_used, generated_at,
           is_deleted, deleted_at, deleted_by
    FROM jeseci_academy.ai_generated_content
    ORDER BY generated_at DESC
    """
    
    try:
        result = pg_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error exporting AI content: {e}")
        return ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'content_id', 'concept_name', 'domain', 'difficulty', 'content',
        'related_concepts', 'generated_by', 'model', 'tokens_used', 'generated_at',
        'is_deleted', 'deleted_at', 'deleted_by'
    ])
    
    # Write data rows
    for row in result or []:
        related_concepts = row.get('related_concepts')
        related_concepts_str = ','.join(related_concepts) if isinstance(related_concepts, list) else str(related_concepts)
        
        writer.writerow([
            row.get('content_id', ''),
            row.get('concept_name', ''),
            row.get('domain', ''),
            row.get('difficulty', ''),
            row.get('content', '')[:1000] if row.get('content') else '',  # Truncate long content
            related_concepts_str,
            row.get('generated_by', ''),
            row.get('model', ''),
            row.get('tokens_used', ''),
            row.get('generated_at', ''),
            row.get('is_deleted', ''),
            row.get('deleted_at', ''),
            row.get('deleted_by', '')
        ])
    
    return output.getvalue()


def export_ai_content_to_json() -> str:
    """Export all AI generated content (active and deleted) to JSON format"""
    import json
    
    pg_manager = get_postgres_manager()
    
    query = """
    SELECT content_id, concept_name, domain, difficulty, content, 
           related_concepts, generated_by, model, tokens_used, generated_at,
           is_deleted, deleted_at, deleted_by
    FROM jeseci_academy.ai_generated_content
    ORDER BY generated_at DESC
    """
    
    try:
        result = pg_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error exporting AI content: {e}")
        return json.dumps({"error": str(e)})
    
    content_list = []
    for row in result or []:
        content_list.append({
            "content_id": row.get('content_id'),
            "concept_name": row.get('concept_name'),
            "domain": row.get('domain'),
            "difficulty": row.get('difficulty'),
            "content": row.get('content'),
            "related_concepts": row.get('related_concepts'),
            "generated_by": row.get('generated_by'),
            "model": row.get('model') or "openai",
            "tokens_used": row.get('tokens_used'),
            "generated_at": row.get('generated_at').isoformat() if row.get('generated_at') else None,
            "is_deleted": row.get('is_deleted'),
            "deleted_at": row.get('deleted_at').isoformat() if row.get('deleted_at') else None,
            "deleted_by": row.get('deleted_by')
        })
    
    return json.dumps({"ai_content": content_list, "total": len(content_list)}, indent=2)


def initialize_ai_content() -> Dict[str, Any]:
    """Initialize AI store with default data if needed"""
    # Check if there are any existing AI generated content
    pg_manager = get_postgres_manager()
    
    check_query = "SELECT COUNT(*) as count FROM jeseci_academy.ai_generated_content"
    try:
        result = pg_manager.execute_query(check_query)
        count = result[0].get('count') if result else 0
    except Exception as e:
        logger.error(f"Error checking AI store initialization: {e}")
        return {"initialized": False, "error": str(e)}
    
    if count == 0:
        # Insert comprehensive sample AI generated content
        sample_content = [
            {
                "concept_name": "Variables and Data Types",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "content": "# Variables and Data Types\n\n## Overview\nIn Jac, variables are containers for storing data values. Unlike traditional languages, Jac uses type inference for simple assignments and explicit type annotations for complex scenarios.\n\n## Key Concepts\n\n### 1. Variable Declaration\n```jac\n# Simple type inference\nname = \"Hello World\";  # Automatically inferred as string\ncount = 42;            # Automatically inferred as integer\n\n# Explicit type annotation\nage: int = 25;\nprice: float = 19.99;\nis_active: bool = True;\n```\n\n### 2. Data Types\n- **Strings**: Text data enclosed in quotes\n- **Integers**: Whole numbers without decimals\n- **Floats**: Numbers with decimal points\n- **Booleans**: True or False values\n- **Lists**: Ordered collections of items\n- **Dictionaries**: Key-value pairs\n\n## Examples\n```jac\n# Working with strings\nmessage = \"Welcome to Jac!\";\nuppercase = message.upper();  // \"WELCOME TO JAC!\"\n\n# Working with numbers\nradius = 5;\narea = 3.14159 * radius * radius;\n```\n\n## Practice Exercises\n1. Create variables for your name, age, and height\n2. Convert a string to uppercase and print it\n3. Calculate the area of a circle with radius 10\n\n## Summary\nVariables in Jac are flexible and powerful. Use type inference for simple cases and explicit annotations for complex scenarios.",
                "related_concepts": ["Type Annotations", "Strings", "Numbers"],
                "generated_by": "system",
                "model": "openai"
            },
            {
                "concept_name": "Object-Spatial Programming",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "content": "# Object-Spatial Programming (OSP)\n\n## Overview\nObject-Spatial Programming (OSP) is Jac's unique paradigm that combines object-oriented programming with graph-based spatial relationships.\n\n## Key Concepts\n\n### 1. Nodes and Edges\n```jac\n# Creating nodes\nnode user_node {\n    has user_id: int;\n    has username: str;\n}\n\n# Creating edges with spatial relationships\nedge knows {\n    has relationship_type: str;\n    has strength: float;\n}\n```\n\n### 2. Walkers\nWalkers are mobile agents that traverse the graph:\n```jac\nwalker NetworkAnalyzer {\n    can init with entry {\n        report {\"message\": \"Starting network analysis\"};\n    }\n    \n    can visit with node_entry {\n        report {\"current_node\": here().id};\n    }\n}\n```\n\n### 3. Spatial Relationships\n- **Neighbors**: Connected nodes\n- **Paths**: Sequences of edges\n- **Subgraphs**: Subsets of the graph\n\n## Examples\n```jac\n# Build a simple graph\ngraph social_network {\n    user_a --knows--> user_b;\n    user_b --knows--> user_c;\n}\n```\n\n## Practice Exercises\n1. Create a node for a Product with attributes\n2. Build an edge relationship between two nodes\n3. Write a walker that traverses all connected nodes\n\n## Summary\nOSP enables powerful graph-based programming where nodes and edges represent real-world relationships.",
                "related_concepts": ["Nodes", "Edges", "Walkers", "Graph Theory"],
                "generated_by": "system",
                "model": "openai"
            },
            {
                "concept_name": "Functions and Parameters",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "content": "# Functions and Parameters\n\n## Overview\nFunctions in Jac are reusable blocks of code that perform specific tasks. They can accept parameters and return values.\n\n## Key Concepts\n\n### 1. Basic Function Definition\n```jac\ncan greet(name: str) -> str {\n    return f\"Hello, {name}!\";\n}\n\n# Calling the function\nmessage = greet(\"World\");  // \"Hello, World!\"\n```\n\n### 2. Default Parameters\n```jac\ncan calculate_area(radius: float, pi: float = 3.14159) -> float {\n    return pi * radius * radius;\n}\n\narea1 = calculate_area(5);      // Uses default pi\narea2 = calculate_area(5, 3.14); // Uses custom pi\n```\n\n### 3. Multiple Parameters\n```jac\ncan create_user(username: str, email: str, age: int = 18) -> dict {\n    return {\n        \"username\": username,\n        \"email\": email,\n        \"age\": age\n    };\n}\n```\n\n## Examples\n```jac\n# Recursive function\ncan factorial(n: int) -> int {\n    if n <= 1 {\n        return 1;\n    }\n    return n * factorial(n - 1);\n}\n```\n\n## Practice Exercises\n1. Write a function to check if a number is even\n2. Create a function that reverses a string\n3. Write a recursive function to calculate Fibonacci numbers\n\n## Summary\nFunctions are essential for writing modular, maintainable code in Jac.",
                "related_concepts": ["Variables", "Type Annotations", "Control Flow"],
                "generated_by": "system",
                "model": "openai"
            },
            {
                "concept_name": "Control Flow and Loops",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "content": "# Control Flow and Loops\n\n## Overview\nControl flow statements in Jac allow you to control the execution order of code based on conditions and iterate over collections.\n\n## Key Concepts\n\n### 1. Conditional Statements\n```jac\n# If-else\nage = 18;\nif age >= 18 {\n    status = \"Adult\";\n} else {\n    status = \"Minor\";\n}\n\n# Else-if chain\nscore = 85;\nif score >= 90 {\n    grade = \"A\";\n} elif score >= 80 {\n    grade = \"B\";\n} elif score >= 70 {\n    grade = \"C\";\n} else {\n    grade = \"F\";\n}\n```\n\n### 2. For Loops\n```jac\n# Iterate over a list\nnumbers = [1, 2, 3, 4, 5];\nfor num in numbers {\n    print(num * 2);\n}\n\n# Iterate with index\nfor i, num in enumerate(numbers) {\n    print(f\"Index {i}: {num}\");\n}\n```\n\n### 3. While Loops\n```jac\ncounter = 0;\nwhile counter < 5 {\n    print(counter);\n    counter += 1;\n}\n```\n\n## Examples\n```jac\n# Break and continue\nfor i in range(10) {\n    if i == 3 {\n        continue;  // Skip iteration\n    }\n    if i == 7 {\n        break;     // Exit loop\n    }\n    print(i);\n}\n```\n\n## Practice Exercises\n1. Write a loop to print all even numbers from 1 to 20\n2. Use nested loops to create a multiplication table\n3. Write a program that counts the number of vowels in a string\n\n## Summary\nMastering control flow is essential for writing dynamic and responsive code.",
                "related_concepts": ["Variables", "Expressions", "Functions"],
                "generated_by": "system",
                "model": "openai"
            },
            {
                "concept_name": "Python Data Structures",
                "domain": "Python",
                "difficulty": "beginner",
                "content": "# Python Data Structures\n\n## Overview\nPython provides several built-in data structures for organizing and storing data efficiently.\n\n## Key Concepts\n\n### 1. Lists\n```python\n# Creating lists\nnumbers = [1, 2, 3, 4, 5]\nmixed = [1, \"hello\", 3.14, True]\n\n# List operations\nnumbers.append(6)           # Add to end\nnumbers.insert(0, 0)        # Insert at position\nnumbers.remove(3)           # Remove first occurrence\nnumbers.pop()               # Remove and return last\nnumbers.sort()              # Sort in place\n```\n\n### 2. Dictionaries\n```python\n# Creating dictionaries\nperson = {\n    \"name\": \"John\",\n    \"age\": 30,\n    \"city\": \"New York\"\n}\n\n# Accessing values\nprint(person[\"name\"])  # John\nprint(person.get(\"email\", \"N/A\"))  # N/A (safe access)\n\n# Adding and modifying\nperson[\"email\"] = \"john@example.com\"\nperson[\"age\"] = 31\n```\n\n### 3. Tuples and Sets\n```python\n# Tuples (immutable)\ncoordinates = (10, 20)\nx, y = coordinates  # Unpacking\n\n# Sets (unique elements)\nunique_numbers = {1, 2, 3, 3, 4}  # {1, 2, 3, 4}\n```\n\n## Examples\n```python\n# List comprehension\nsquares = [x**2 for x in range(10)]\n\n# Dictionary comprehension\nsquare_dict = {x: x**2 for x in range(5)}\n```\n\n## Practice Exercises\n1. Create a dictionary of 5 countries and their capitals\n2. Write a program to find the most common element in a list\n3. Use list comprehension to filter even numbers\n\n## Summary\nUnderstanding data structures is fundamental to writing efficient Python code.",
                "related_concepts": ["Variables", "Loops", "Functions"],
                "generated_by": "system",
                "model": "openai"
            }
        ]
        
        for content_data in sample_content:
            timestamp = str(int(datetime.datetime.now().timestamp()))
            actual_content_id = f"ai_{timestamp}_{content_data['concept_name'].split()[0].lower()}"
            
            insert_query = """
            INSERT INTO jeseci_academy.ai_generated_content 
            (content_id, concept_name, domain, difficulty, content, related_concepts, 
             generated_by, model, tokens_used, is_deleted, created_by, created_at, updated_by, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, false, 'system', NOW(), 'system', NOW())
            """
            
            try:
                pg_manager.execute_query(insert_query, 
                    (actual_content_id, content_data['concept_name'], content_data['domain'], 
                     content_data['difficulty'], content_data['content'], 
                     content_data['related_concepts'], content_data['generated_by'], 
                     content_data['model'], 100), fetch=False)
            except Exception as e:
                logger.error(f"Error inserting sample AI content: {e}")
    
    return {"initialized": True}
