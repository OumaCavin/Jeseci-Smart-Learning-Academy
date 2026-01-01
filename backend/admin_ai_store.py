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
# AI DOMAINS (static reference data - doesn't need database storage)
# ==============================================================================

def get_ai_domains():
    """Get available AI domains"""
    return [
        {"id": "cs", "name": "Computer Science", "description": "CS fundamentals", "course_count": 5},
        {"id": "math", "name": "Mathematics", "description": "Math topics", "course_count": 3},
        {"id": "physics", "name": "Physics", "description": "Physics concepts", "course_count": 4},
        {"id": "jac", "name": "Jac Language", "description": "Jac programming language", "course_count": 6},
        {"id": "programming", "name": "General Programming", "description": "Programming concepts", "course_count": 8}
    ]


# ==============================================================================
# AI GENERATED CONTENT STORAGE
# ==============================================================================

def get_all_ai_content() -> List[Dict[str, Any]]:
    """Get all AI generated content from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    try:
        query = """
        SELECT content_id, concept_name, domain, difficulty, content, 
               related_concepts, generated_by, model, tokens_used, generated_at
        FROM jeseci_academy.ai_generated_content
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
     generated_by, model, tokens_used, generated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
    count_query = "SELECT COUNT(*) as total FROM jeseci_academy.ai_generated_content"
    try:
        count_result = pg_manager.execute_query(count_query)
        total_generations = count_result[0].get('total') if count_result else 0
    except Exception as e:
        logger.error(f"Error getting AI content count: {e}")
        total_generations = 0
    
    # Get total tokens used
    tokens_query = "SELECT COALESCE(SUM(tokens_used), 0) as total_tokens FROM jeseci_academy.ai_generated_content"
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
            INSERT INTO jeseci_academy.ai_usage_stats (stat_type, stat_key, stat_value, updated_at)
            VALUES ('domain_usage', %s, 1, NOW())
            """
            try:
                pg_manager.execute_query(insert_query, (domain,), fetch=False)
            except Exception as e:
                logger.error(f"Error inserting AI domain stats: {e}")


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
        # Insert some sample AI generated content
        sample_content = {
            "ai_001": {
                "concept_name": "Variables and Data Types",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "content": "AI-generated content...",
                "related_concepts": ["Type Annotations", "Strings"],
                "generated_by": "user_cavin_78a5d49f",
                "model": "openai"
            }
        }
        
        for content_id, content_data in sample_content.items():
            timestamp = str(int(datetime.datetime.now().timestamp()))
            actual_content_id = f"ai_{timestamp}_{content_id.split('_')[1]}"
            
            insert_query = """
            INSERT INTO jeseci_academy.ai_generated_content 
            (content_id, concept_name, domain, difficulty, content, related_concepts, 
             generated_by, model, tokens_used, generated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
