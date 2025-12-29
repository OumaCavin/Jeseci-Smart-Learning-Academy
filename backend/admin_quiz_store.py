# Admin quiz storage using PostgreSQL database
# Uses the existing Quiz model from SQLAlchemy

import os
import threading
import datetime
from typing import Optional

# Import database utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))
from database import get_postgres_manager

# In-memory cache for quick lookups
quizzes_cache = {}
quizzes_lock = threading.Lock()
cache_initialized = False

# ==============================================================================
# QUIZZES STORAGE (PostgreSQL)
# ==============================================================================

def initialize_quizzes():
    """Initialize quizzes from PostgreSQL"""
    global quizzes_cache, cache_initialized
    
    if cache_initialized:
        return quizzes_cache
    
    with quizzes_lock:
        if cache_initialized:
            return quizzes_cache
            
        pg_manager = get_postgres_manager()
        
        query = """
        SELECT quiz_id, title, description, concept_id, lesson_id, 
               passing_score, time_limit_minutes, max_attempts, is_published,
               created_at, updated_at
        FROM jeseci_academy.quizzes
        ORDER BY created_at DESC
        """
        
        result = pg_manager.execute_query(query)
        
        quizzes_cache = {}
        if result:
            for row in result:
                quiz_id = row.get('quiz_id')
                quizzes_cache[quiz_id] = {
                    "quiz_id": quiz_id,
                    "title": row.get('title'),
                    "description": row.get('description'),
                    "course_id": row.get('concept_id') or row.get('lesson_id'),
                    "difficulty": row.get('passing_score', 70) >= 70 and "intermediate" or "beginner",
                    "questions_count": 0,  # Would need QuizQuestion table for this
                    "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
                    "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None
                }
        
        cache_initialized = True
        return quizzes_cache

def get_all_quizzes():
    """Get all quizzes from PostgreSQL"""
    initialize_quizzes()
    with quizzes_lock:
        return list(quizzes_cache.values())

def get_quiz_by_id(quiz_id):
    """Get a specific quiz from PostgreSQL"""
    initialize_quizzes()
    with quizzes_lock:
        return quizzes_cache.get(quiz_id)

def create_quiz(title, description, course_id, difficulty):
    """Create a new quiz in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Generate quiz ID
    quiz_id = "quiz_" + title.lower().replace(" ", "_").replace("-", "_")[0:15] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
    
    # Determine passing score based on difficulty
    passing_score = 70 if difficulty == "beginner" else (80 if difficulty == "intermediate" else 90)
    
    insert_query = """
    INSERT INTO jeseci_academy.quizzes 
    (quiz_id, title, description, concept_id, passing_score, max_attempts, is_published, created_at)
    VALUES (%s, %s, %s, %s, %s, 3, true, NOW())
    """
    
    result = pg_manager.execute_query(insert_query, 
        (quiz_id, title, description, course_id or None, passing_score), fetch=False)
    
    if result or result is not None:
        # Invalidate cache
        global cache_initialized
        cache_initialized = False
        
        new_quiz = {
            "quiz_id": quiz_id,
            "title": title,
            "description": description,
            "course_id": course_id or None,
            "difficulty": difficulty,
            "questions_count": 0,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": None
        }
        return {"success": True, "quiz_id": quiz_id, "quiz": new_quiz}
    
    return {"success": False, "error": "Failed to create quiz"}

def update_quiz(quiz_id, title="", description="", difficulty=""):
    """Update an existing quiz in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Check if quiz exists
    check_query = "SELECT quiz_id FROM jeseci_academy.quizzes WHERE quiz_id = %s"
    existing = pg_manager.execute_query(check_query, (quiz_id,))
    
    if not existing:
        return {"success": False, "error": "Quiz not found"}
    
    # Build dynamic update
    updates = []
    params = [quiz_id]
    
    if title:
        updates.append("title = %s")
        params.append(title)
    if description:
        updates.append("description = %s")
        params.append(description)
    if difficulty:
        # Update passing score based on difficulty
        passing_score = 70 if difficulty == "beginner" else (80 if difficulty == "intermediate" else 90)
        updates.append("passing_score = %s")
        params.append(passing_score)
    
    if not updates:
        return {"success": True, "message": "No fields to update"}
    
    updates.append("updated_at = NOW()")
    
    update_query = f"""
    UPDATE jeseci_academy.quizzes 
    SET {', '.join(updates)}
    WHERE quiz_id = %s
    """
    
    result = pg_manager.execute_query(update_query, params, fetch=False)
    
    if result or result is not None:
        global cache_initialized
        cache_initialized = False
        return {"success": True, "quiz_id": quiz_id}
    
    return {"success": False, "error": "Failed to update quiz"}

def delete_quiz(quiz_id):
    """Delete a quiz from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    check_query = "SELECT quiz_id FROM jeseci_academy.quizzes WHERE quiz_id = %s"
    existing = pg_manager.execute_query(check_query, (quiz_id,))
    
    if not existing:
        return {"success": False, "error": "Quiz not found"}
    
    delete_query = "DELETE FROM jeseci_academy.quizzes WHERE quiz_id = %s"
    result = pg_manager.execute_query(delete_query, (quiz_id,), fetch=False)
    
    if result or result is not None:
        global cache_initialized
        cache_initialized = False
        return {"success": True, "quiz_id": quiz_id}
    
    return {"success": False, "error": "Failed to delete quiz"}

def record_quiz_attempt(quiz_id, user_id, score, total_questions, correct_answers, time_taken_seconds):
    """Record a quiz attempt in PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Check if quiz exists
    check_query = "SELECT passing_score FROM jeseci_academy.quizzes WHERE quiz_id = %s"
    quiz_result = pg_manager.execute_query(check_query, (quiz_id,))
    
    if not quiz_result:
        return {"success": False, "error": "Quiz not found"}
    
    passing_score = quiz_result[0].get('passing_score', 70)
    is_passed = score >= passing_score
    
    # Insert attempt
    insert_query = """
    INSERT INTO jeseci_academy.quiz_attempts 
    (user_id, quiz_id, score, total_questions, correct_answers, time_taken_seconds, is_passed, started_at, completed_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    
    result = pg_manager.execute_query(insert_query, 
        (user_id, quiz_id, score, total_questions, correct_answers, time_taken_seconds, is_passed), fetch=False)
    
    if result or result is not None:
        return {"success": True, "attempt_id": quiz_id, "is_passed": is_passed}
    
    return {"success": False, "error": "Failed to record attempt"}

def get_quiz_analytics():
    """Get quiz analytics from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Get total quizzes
    count_query = "SELECT COUNT(*) as count FROM jeseci_academy.quizzes"
    count_result = pg_manager.execute_query(count_query)
    total_quizzes = count_result[0].get('count', 0) if count_result else 0
    
    # Get total attempts and average score
    attempts_query = """
    SELECT COUNT(*) as total_attempts, 
           AVG(score) as avg_score,
           SUM(CASE WHEN is_passed = true THEN 1 ELSE 0 END) as passed_count
    FROM jeseci_academy.quiz_attempts
    """
    attempts_result = pg_manager.execute_query(attempts_query)
    
    total_attempts = attempts_result[0].get('total_attempts', 0) if attempts_result else 0
    average_score = attempts_result[0].get('avg_score', 0) if attempts_result else 0
    passed_count = attempts_result[0].get('passed_count', 0) if attempts_result else 0
    
    # Calculate pass rate
    pass_rate = (passed_count / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        "total_quizzes": total_quizzes,
        "total_attempts": total_attempts,
        "average_score": round(average_score, 1) if average_score else 0,
        "pass_rate": round(pass_rate, 1)
    }
