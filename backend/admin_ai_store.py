# In-memory storage for admin AI content management
# This module provides persistent storage for AI-generated content and domains

import json
import os
import threading
import datetime

# In-memory storage
ai_content_store = {}
ai_stats = {}
ai_lock = threading.Lock()

# File path for persistence
DATA_DIR = "data"
AI_CONTENT_FILE = os.path.join(DATA_DIR, "admin_ai_content.json")
AI_STATS_FILE = os.path.join(DATA_DIR, "admin_ai_stats.json")

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json_store(filepath, default_data):
    """Load data from JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return default_data

def save_json_store(filepath, data):
    """Save data to JSON file"""
    try:
        ensure_data_dir()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# ==============================================================================
# AI DOMAINS (static reference data - doesn't need persistence)
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

def initialize_ai_content():
    """Initialize AI content store with default data if empty"""
    global ai_content_store
    default_content = {
        "ai_001": {
            "content_id": "ai_001",
            "concept_name": "Variables and Data Types",
            "domain": "Jac Language",
            "difficulty": "beginner",
            "content": "AI-generated content...",
            "related_concepts": ["Type Annotations", "Strings"],
            "generated_at": "2025-12-29T11:10:57Z",
            "generated_by": "user_cavin_78a5d49f",
            "model": "mock"
        }
    }
    ai_content_store = load_json_store(AI_CONTENT_FILE, default_content)
    
    # Initialize stats
    global ai_stats
    ai_stats = {
        "total_generations": 156,
        "total_tokens_used": 1250000,
        "domains_used": {"Computer Science": 85, "Mathematics": 45, "Physics": 26, "Jac Language": 30}
    }
    
    return ai_content_store

def get_all_ai_content():
    """Get all AI generated content"""
    with ai_lock:
        return list(ai_content_store.values())

def save_ai_content(concept_name, domain, difficulty, content, generated_by, related_concepts=None):
    """Save AI generated content"""
    global ai_content_store, ai_stats
    with ai_lock:
        content_id = "ai_" + str(int(datetime.datetime.now().timestamp()))
        
        new_content = {
            "content_id": content_id,
            "concept_name": concept_name,
            "domain": domain,
            "difficulty": difficulty,
            "content": content,
            "related_concepts": related_concepts or [],
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generated_by": generated_by,
            "model": "openai"  # or "mock" if no API key
        }
        
        ai_content_store[content_id] = new_content
        save_json_store(AI_CONTENT_FILE, ai_content_store)
        
        # Update stats
        ai_stats["total_generations"] = ai_stats.get("total_generations", 0) + 1
        
        # Track domain usage
        if domain in ai_stats.get("domains_used", {}):
            ai_stats["domains_used"][domain] += 1
        else:
            ai_stats["domains_used"][domain] = 1
        
        return {"success": True, "content_id": content_id, "content": new_content}

def get_ai_stats():
    """Get AI usage statistics"""
    with ai_lock:
        # Get recent generations
        recent = sorted(ai_content_store.values(), key=lambda x: x.get("generated_at", ""), reverse=True)[:10]
        
        return {
            "total_generations": ai_stats.get("total_generations", 0),
            "total_tokens_used": ai_stats.get("total_tokens_used", 0),
            "domains_used": ai_stats.get("domains_used", {}),
            "recent_generations": recent
        }
