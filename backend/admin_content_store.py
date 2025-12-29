# In-memory storage for admin content management (courses, concepts, learning paths)
# This module provides persistent storage for all content management operations

import json
import os
import threading
import datetime

# In-memory storage
courses_store = {}
concepts_store = {}
paths_store = {}
content_lock = threading.Lock()

# File paths for persistence
DATA_DIR = "data"
COURSES_FILE = os.path.join(DATA_DIR, "admin_courses.json")
CONCEPTS_FILE = os.path.join(DATA_DIR, "admin_concepts.json")
PATHS_FILE = os.path.join(DATA_DIR, "admin_paths.json")

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
# COURSES STORAGE
# ==============================================================================

def initialize_courses():
    """Initialize courses store with default data if empty"""
    global courses_store
    default_courses = {
        "jac_fundamentals": {
            "course_id": "jac_fundamentals",
            "title": "Jac Programming Fundamentals",
            "description": "Learn the basics of Jac programming language - variables, functions, and control flow",
            "domain": "Jac Language",
            "difficulty": "beginner",
            "content_type": "interactive",
            "created_at": "2025-12-01T10:00:00Z",
            "updated_at": None
        },
        "jac_osp_basics": {
            "course_id": "jac_osp_basics",
            "title": "Object-Spatial Programming Basics",
            "description": "Master the fundamentals of OSP with nodes, edges, and walkers",
            "domain": "Jac Language",
            "difficulty": "intermediate",
            "content_type": "interactive",
            "created_at": "2025-12-05T14:30:00Z",
            "updated_at": None
        }
    }
    courses_store = load_json_store(COURSES_FILE, default_courses)
    return courses_store

def get_all_courses():
    """Get all courses"""
    with content_lock:
        return list(courses_store.values())

def get_course_by_id(course_id):
    """Get a specific course by ID"""
    with content_lock:
        return courses_store.get(course_id)

def create_course(title, description, domain, difficulty, content_type="interactive"):
    """Create a new course"""
    global courses_store
    with content_lock:
        # Generate course ID
        course_id = "course_" + title.lower().replace(" ", "_").replace("-", "_")[0:20] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
        
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
        
        courses_store[course_id] = new_course
        save_json_store(COURSES_FILE, courses_store)
        
        return {"success": True, "course_id": course_id, "course": new_course}

def update_course(course_id, title="", description="", domain="", difficulty=""):
    """Update an existing course"""
    global courses_store
    with content_lock:
        if course_id not in courses_store:
            return {"success": False, "error": "Course not found"}
        
        course = courses_store[course_id]
        if title: course["title"] = title
        if description: course["description"] = description
        if domain: course["domain"] = domain
        if difficulty: course["difficulty"] = difficulty
        course["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        courses_store[course_id] = course
        save_json_store(COURSES_FILE, courses_store)
        
        return {"success": True, "course_id": course_id}

def delete_course(course_id):
    """Delete a course"""
    global courses_store
    with content_lock:
        if course_id not in courses_store:
            return {"success": False, "error": "Course not found"}
        
        del courses_store[course_id]
        save_json_store(COURSES_FILE, courses_store)
        
        return {"success": True, "course_id": course_id}

# ==============================================================================
# CONCEPTS STORAGE
# ==============================================================================

def initialize_concepts():
    """Initialize concepts store with default data if empty"""
    global concepts_store
    default_concepts = {
        "jac_variables": {
            "concept_id": "jac_variables",
            "name": "Variables and Data Types",
            "display_name": "Variables & Types",
            "category": "Programming Basics",
            "difficulty_level": "beginner",
            "domain": "Jac Language",
            "description": "Learn about variables and data types",
            "icon": "variable"
        },
        "jac_osp": {
            "concept_id": "jac_osp",
            "name": "Object-Spatial Programming",
            "display_name": "OSP Basics",
            "category": "Programming Paradigm",
            "difficulty_level": "intermediate",
            "domain": "Jac Language",
            "description": "Master Jac's unique graph-based programming",
            "icon": "graph"
        }
    }
    concepts_store = load_json_store(CONCEPTS_FILE, default_concepts)
    return concepts_store

def get_all_concepts():
    """Get all concepts"""
    with content_lock:
        return list(concepts_store.values())

def get_concept_by_id(concept_id):
    """Get a specific concept by ID"""
    with content_lock:
        return concepts_store.get(concept_id)

def create_concept(name, display_name, category, difficulty_level, domain, description="", icon=""):
    """Create a new concept"""
    global concepts_store
    with content_lock:
        # Generate concept ID
        concept_id = "concept_" + name.lower().replace(" ", "_").replace("-", "_")[0:20] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
        
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
        
        concepts_store[concept_id] = new_concept
        save_json_store(CONCEPTS_FILE, concepts_store)
        
        return {"success": True, "concept_id": concept_id, "concept": new_concept}

# ==============================================================================
# LEARNING PATHS STORAGE
# ==============================================================================

def initialize_paths():
    """Initialize learning paths store with default data if empty"""
    global paths_store
    default_paths = {
        "path_python": {
            "path_id": "path_python",
            "title": "Python Mastery",
            "description": "Master Python from fundamentals to advanced concepts",
            "courses": ["course_1", "course_2", "course_4"],
            "concepts": ["concept_oop", "concept_algo"],
            "difficulty": "beginner",
            "total_modules": 8,
            "duration": "8 weeks"
        }
    }
    paths_store = load_json_store(PATHS_FILE, default_paths)
    return paths_store

def get_all_paths():
    """Get all learning paths"""
    with content_lock:
        return list(paths_store.values())

def get_path_by_id(path_id):
    """Get a specific learning path by ID"""
    with content_lock:
        return paths_store.get(path_id)

def create_path(title, description, courses, concepts, difficulty, duration):
    """Create a new learning path"""
    global paths_store
    with content_lock:
        # Generate path ID
        path_id = "path_" + title.lower().replace(" ", "_").replace("-", "_")[0:15] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
        
        new_path = {
            "path_id": path_id,
            "title": title,
            "description": description,
            "courses": courses,
            "concepts": concepts,
            "difficulty": difficulty,
            "total_modules": len(courses) + len(concepts),
            "duration": duration
        }
        
        paths_store[path_id] = new_path
        save_json_store(PATHS_FILE, paths_store)
        
        return {"success": True, "path_id": path_id, "path": new_path}
