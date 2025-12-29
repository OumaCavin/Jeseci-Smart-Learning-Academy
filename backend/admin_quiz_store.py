# In-memory storage for admin quiz management
# This module provides persistent storage for quiz management operations

import json
import os
import threading
import datetime

# In-memory storage
quizzes_store = {}
quizzes_lock = threading.Lock()

# File path for persistence
DATA_DIR = "data"
QUIZZES_FILE = os.path.join(DATA_DIR, "admin_quizzes.json")

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
# QUIZZES STORAGE
# ==============================================================================

def initialize_quizzes():
    """Initialize quizzes store with default data if empty"""
    global quizzes_store
    default_quizzes = {
        "quiz_python_basics": {
            "quiz_id": "quiz_python_basics",
            "title": "Python Basics Quiz",
            "description": "Test your understanding of Python fundamentals",
            "course_id": "course_python",
            "difficulty": "beginner",
            "questions_count": 5,
            "created_at": "2025-12-10T10:00:00Z",
            "updated_at": None,
            "attempts_count": 0,
            "total_score": 0
        },
        "quiz_oop": {
            "quiz_id": "quiz_oop",
            "title": "Object-Oriented Programming Quiz",
            "description": "Test your OOP knowledge",
            "course_id": "course_oop",
            "difficulty": "intermediate",
            "questions_count": 10,
            "created_at": "2025-12-12T14:30:00Z",
            "updated_at": None,
            "attempts_count": 0,
            "total_score": 0
        }
    }
    quizzes_store = load_json_store(QUIZZES_FILE, default_quizzes)
    return quizzes_store

def get_all_quizzes():
    """Get all quizzes"""
    with quizzes_lock:
        return list(quizzes_store.values())

def get_quiz_by_id(quiz_id):
    """Get a specific quiz by ID"""
    with quizzes_lock:
        return quizzes_store.get(quiz_id)

def create_quiz(title, description, course_id, difficulty):
    """Create a new quiz"""
    global quizzes_store
    with quizzes_lock:
        # Generate quiz ID
        quiz_id = "quiz_" + title.lower().replace(" ", "_").replace("-", "_")[0:15] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
        
        new_quiz = {
            "quiz_id": quiz_id,
            "title": title,
            "description": description,
            "course_id": course_id or None,
            "difficulty": difficulty,
            "questions_count": 0,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": None,
            "attempts_count": 0,
            "total_score": 0
        }
        
        quizzes_store[quiz_id] = new_quiz
        save_json_store(QUIZZES_FILE, quizzes_store)
        
        return {"success": True, "quiz_id": quiz_id, "quiz": new_quiz}

def update_quiz(quiz_id, title="", description="", difficulty=""):
    """Update an existing quiz"""
    global quizzes_store
    with quizzes_lock:
        if quiz_id not in quizzes_store:
            return {"success": False, "error": "Quiz not found"}
        
        quiz = quizzes_store[quiz_id]
        if title: quiz["title"] = title
        if description: quiz["description"] = description
        if difficulty: quiz["difficulty"] = difficulty
        quiz["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        quizzes_store[quiz_id] = quiz
        save_json_store(QUIZZES_FILE, quizzes_store)
        
        return {"success": True, "quiz_id": quiz_id}

def delete_quiz(quiz_id):
    """Delete a quiz"""
    global quizzes_store
    with quizzes_lock:
        if quiz_id not in quizzes_store:
            return {"success": False, "error": "Quiz not found"}
        
        del quizzes_store[quiz_id]
        save_json_store(QUIZZES_FILE, quizzes_store)
        
        return {"success": True, "quiz_id": quiz_id}

def record_quiz_attempt(quiz_id, score):
    """Record a quiz attempt for analytics"""
    global quizzes_store
    with quizzes_lock:
        if quiz_id not in quizzes_store:
            return
        
        quiz = quizzes_store[quiz_id]
        quiz["attempts_count"] = quiz.get("attempts_count", 0) + 1
        quiz["total_score"] = quiz.get("total_score", 0) + score
        quizzes_store[quiz_id] = quiz
        save_json_store(QUIZZES_FILE, quizzes_store)

def get_quiz_analytics():
    """Get quiz analytics data"""
    with quizzes_lock:
        quizzes = list(quizzes_store.values())
        total_quizzes = len(quizzes)
        total_attempts = sum(q.get("attempts_count", 0) for q in quizzes)
        
        # Calculate average score
        total_scores = sum(q.get("total_score", 0) for q in quizzes)
        average_score = total_scores / total_attempts if total_attempts > 0 else 0
        
        # Calculate pass rate (assuming pass is 70%)
        passed_count = sum(1 for q in quizzes if q.get("total_score", 0) / max(q.get("attempts_count", 1), 1) >= 70)
        pass_rate = (passed_count / total_quizzes * 100) if total_quizzes > 0 else 0
        
        return {
            "total_quizzes": total_quizzes,
            "total_attempts": total_attempts,
            "average_score": round(average_score, 1),
            "pass_rate": round(pass_rate, 1)
        }
