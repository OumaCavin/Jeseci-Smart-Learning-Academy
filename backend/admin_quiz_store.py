# Admin quiz storage using PostgreSQL database
# Uses the existing Quiz model from SQLAlchemy

import os
import threading
import datetime
import logging
from typing import Optional, Dict, Any, List

# Set up logging
logger = logging.getLogger(__name__)

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
        
        try:
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
        except Exception as e:
            logger.error(f"Error initializing quizzes: {e}")
            cache_initialized = False
            return {}

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
    (quiz_id, title, description, concept_id, lesson_id, passing_score, max_attempts, is_published, 
     time_limit_minutes, is_deleted, created_by, created_at, updated_by, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, 3, true, %s, false, 'system', NOW(), 'system', NOW())
    """
    
    try:
        result = pg_manager.execute_query(insert_query, 
            (quiz_id, title, description, course_id or None, None, passing_score, 30), fetch=False)
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
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
    try:
        existing = pg_manager.execute_query(check_query, (quiz_id,))
    except Exception as e:
        logger.error(f"Error checking quiz existence: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
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
    
    try:
        result = pg_manager.execute_query(update_query, params, fetch=False)
    except Exception as e:
        logger.error(f"Error updating quiz: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        global cache_initialized
        cache_initialized = False
        return {"success": True, "quiz_id": quiz_id}
    
    return {"success": False, "error": "Failed to update quiz"}

def delete_quiz(quiz_id):
    """Delete a quiz from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    check_query = "SELECT quiz_id FROM jeseci_academy.quizzes WHERE quiz_id = %s"
    try:
        existing = pg_manager.execute_query(check_query, (quiz_id,))
    except Exception as e:
        logger.error(f"Error checking quiz existence for delete: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if not existing:
        return {"success": False, "error": "Quiz not found"}
    
    delete_query = "DELETE FROM jeseci_academy.quizzes WHERE quiz_id = %s"
    try:
        result = pg_manager.execute_query(delete_query, (quiz_id,), fetch=False)
    except Exception as e:
        logger.error(f"Error deleting quiz: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
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
    try:
        quiz_result = pg_manager.execute_query(check_query, (quiz_id,))
    except Exception as e:
        logger.error(f"Error checking quiz existence for attempt: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
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
    
    try:
        result = pg_manager.execute_query(insert_query, 
            (user_id, quiz_id, score, total_questions, correct_answers, time_taken_seconds, is_passed), fetch=False)
    except Exception as e:
        logger.error(f"Error recording quiz attempt: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        return {"success": True, "attempt_id": quiz_id, "is_passed": is_passed}
    
    return {"success": False, "error": "Failed to record attempt"}

def get_quiz_analytics():
    """Get quiz analytics from PostgreSQL"""
    pg_manager = get_postgres_manager()
    
    # Get total quizzes
    count_query = "SELECT COUNT(*) as count FROM jeseci_academy.quizzes"
    try:
        count_result = pg_manager.execute_query(count_query)
        total_quizzes = count_result[0].get('count', 0) if count_result else 0
    except Exception as e:
        logger.error(f"Error getting quiz count: {e}")
        total_quizzes = 0
    
    # Get total attempts and average score
    attempts_query = """
    SELECT COUNT(*) as total_attempts, 
           AVG(score) as avg_score,
           SUM(CASE WHEN is_passed = true THEN 1 ELSE 0 END) as passed_count
    FROM jeseci_academy.quiz_attempts
    """
    try:
        attempts_result = pg_manager.execute_query(attempts_query)
    except Exception as e:
        logger.error(f"Error getting quiz attempts: {e}")
        attempts_result = None
    
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


# ==============================================================================
# AI QUIZ GENERATION
# ==============================================================================

def generate_ai_quiz(topic: str, difficulty: str, question_count: int = 5) -> Dict[str, Any]:
    """
    Generate a quiz using OpenAI API
    
    Args:
        topic: The topic/concept for the quiz
        difficulty: Difficulty level (beginner, intermediate, advanced, expert)
        question_count: Number of questions to generate
        
    Returns:
        Generated quiz with questions, options, and answers
    """
    import os
    import aiohttp
    import json
    
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key or api_key.startswith("sk-proj-placeholder"):
        # Return a sample quiz for demo purposes
        return _generate_sample_quiz(topic, difficulty, question_count)
    
    async def _call_openai():
        prompt = f"""
        You are an expert quiz creator for the JAC programming language. 
        Create a multiple-choice quiz about "{topic}" at {difficulty} level.
        
        Generate {question_count} multiple-choice questions. Each question should have:
        - A clear, concise question
        - 4 answer options (A, B, C, D)
        - The correct answer index (0-3)
        - A brief explanation of why the answer is correct
        
        Return the response as a valid JSON object with this structure:
        {{
            "title": "Quiz title",
            "description": "Brief description",
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Why this is correct"
                }}
            ]
        }}
        
        Make questions challenging but fair for {difficulty} level. 
        Focus on practical knowledge and understanding.
        """
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are an expert educational quiz creator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with session.post("https://api.openai.com/v1/chat/completions", 
                                  headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    # Parse JSON from response
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:-3]
                    elif content.startswith("```"):
                        content = content[3:-3]
                    return json.loads(content)
                else:
                    error_data = await response.json()
                    raise Exception(f"OpenAI API error: {error_data.get('error', {}).get('message', 'Unknown error')}")
    
    import asyncio
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            quiz_data = loop.run_until_complete(_call_openai())
        finally:
            loop.close()
        
        return {
            "success": True,
            "quiz": quiz_data,
            "topic": topic,
            "difficulty": difficulty,
            "question_count": len(quiz_data.get("questions", []))
        }
        
    except Exception as e:
        logger.error(f"Error generating AI quiz: {e}")
        # Fallback to sample quiz
        return _generate_sample_quiz(topic, difficulty, question_count)


def _generate_sample_quiz(topic: str, difficulty: str, question_count: int) -> Dict[str, Any]:
    """Generate a sample quiz for demo/fallback purposes"""
    
    # Sample questions for different JAC topics
    sample_questions = {
        "jac_programming_fundamentals": [
            {
                "question": "What does JAC stand for in the JAC programming language?",
                "options": ["Java Application Controller", "Just Another Compiler", "Jac is not an acronym", "Jump and Calculate"],
                "correct_answer": 2,
                "explanation": "JAC is not an acronym; it's simply the name of the programming language."
            },
            {
                "question": "Which keyword is used to define a function in JAC?",
                "options": ["function", "def", "func", "define"],
                "correct_answer": 1,
                "explanation": "In JAC, functions are defined using the 'def' keyword with type annotations."
            },
            {
                "question": "What is the primary paradigm of JAC?",
                "options": ["Object-Oriented Programming", "Functional Programming", "Object-Spatial Programming", "Procedural Programming"],
                "correct_answer": 2,
                "explanation": "JAC's primary paradigm is Object-Spatial Programming (OSP), which moves computation to data."
            }
        ],
        "jac_variables_data_types": [
            {
                "question": "How do you declare a typed variable in JAC?",
                "options": ["var x: int = 5", "int x = 5", "let x: int = 5", "x: int = 5"],
                "correct_answer": 0,
                "explanation": "JAC uses the 'var' keyword with type annotations: var x: int = 5"
            },
            {
                "question": "What annotation is used for type hints in JAC?",
                "options": [": int", ":: int", "-> int", "# int"],
                "correct_answer": 0,
                "explanation": "JAC uses colon notation for type annotations: variable_name: type"
            }
        ],
        "jac_control_flow": [
            {
                "question": "Which statement is used for conditional branching in JAC?",
                "options": ["switch", "if-else", "cond", "both if-else and cond"],
                "correct_answer": 3,
                "explanation": "JAC supports traditional if-else statements and the 'cond' statement for multiple conditions."
            },
            {
                "question": "What loop construct is used for iteration in JAC?",
                "options": ["for", "while", "iterate", "both for and while"],
                "correct_answer": 3,
                "explanation": "JAC supports both 'for' loops (for counting) and 'while' loops (for conditional iteration)."
            }
        ],
        "jac_oop": [
            {
                "question": "Which keyword is used to define a class in JAC?",
                "options": ["class", "obj", "object", "struct"],
                "correct_answer": 1,
                "explanation": "In JAC, classes are defined using the 'obj' keyword, not 'class'."
            },
            {
                "question": "What is the relationship between objects and nodes in JAC OSP?",
                "options": ["Objects are nodes", "Objects contain nodes", "Objects and nodes are unrelated", "Nodes are a type of object"],
                "correct_answer": 0,
                "explanation": "In JAC's Object-Spatial Programming, objects are essentially nodes in a graph structure."
            }
        ],
        "jac_walkers": [
            {
                "question": "What is a walker in JAC?",
                "options": ["A function that walks through arrays", "A mobile agent that traverses graphs", "A type of loop", "A data structure"],
                "correct_answer": 1,
                "explanation": "Walkers are mobile agents that traverse graph structures (nodes and edges) performing computations."
            },
            {
                "question": "Which keyword is used to spawn a walker in JAC?",
                "options": ["new", "spawn", "create", "run"],
                "correct_answer": 1,
                "explanation": "The 'spawn' keyword is used to create and activate walker instances in JAC."
            }
        ],
        "jac_ai_integration": [
            {
                "question": "What module provides AI integration in JAC?",
                "options": ["ai_module", "byLLM", "openai", "ai_integration"],
                "correct_answer": 1,
                "explanation": "JAC uses the 'byLLM' module for integrating Large Language Models into applications."
            },
            {
                "question": "How can you call an LLM in JAC code?",
                "options": ["llm_call()", "byLLM.invoke()", "ai.generate()", "openai.ChatCompletion"],
                "correct_answer": 1,
                "explanation": "The byLLM module provides methods like 'invoke()' for calling Large Language Models."
            }
        ]
    }
    
    # Map topic to question set
    topic_key = topic.lower().replace(" ", "_").replace("-", "_")
    questions = sample_questions.get(topic_key, [
        {
            "question": f"What is a key concept in {topic}?",
            "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
            "correct_answer": 0,
            "explanation": "This is a sample question about the topic."
        }
    ])
    
    # Select questions based on requested count
    selected_questions = questions[:min(question_count, len(questions))]
    
    # Pad with generic questions if needed
    while len(selected_questions) < question_count:
        selected_questions.append({
            "question": f"What is an important aspect of {topic}?",
            "options": ["Aspect A", "Aspect B", "Aspect C", "Aspect D"],
            "correct_answer": 0,
            "explanation": "This is a sample question about the topic."
        })
    
    return {
        "success": True,
        "quiz": {
            "title": f"{topic.title()} Quiz",
            "description": f"Test your knowledge of {topic} at {difficulty} level",
            "questions": selected_questions
        },
        "topic": topic,
        "difficulty": difficulty,
        "question_count": len(selected_questions),
        "is_sample": True
    }


def save_ai_generated_quiz(quiz_data: Dict[str, Any], topic: str, difficulty: str) -> Dict[str, Any]:
    """
    Save an AI-generated quiz to the database
    
    Args:
        quiz_data: The generated quiz data from generate_ai_quiz
        topic: The topic of the quiz
        difficulty: The difficulty level
        
    Returns:
        The created quiz object
    """
    pg_manager = get_postgres_manager()
    
    # Extract quiz info
    title = quiz_data.get("title", f"{topic} Quiz")
    description = quiz_data.get("description", f"Quiz on {topic}")
    questions = quiz_data.get("questions", [])
    
    # Generate quiz ID
    quiz_id = "quiz_" + topic.lower().replace(" ", "_").replace("-", "_")[0:15] + "_" + str(int(datetime.datetime.now().timestamp()))[0:8]
    
    # Determine passing score based on difficulty
    passing_score = 70 if difficulty == "beginner" else (80 if difficulty == "intermediate" else 90)
    
    # Insert quiz
    insert_query = """
    INSERT INTO jeseci_academy.quizzes 
    (quiz_id, title, description, concept_id, passing_score, max_attempts, is_published, 
     time_limit_minutes, is_deleted, created_by, created_at, updated_by, updated_at)
    VALUES (%s, %s, %s, %s, %s, 3, true, 30, false, 'system', NOW(), 'system', NOW())
    """
    
    try:
        result = pg_manager.execute_query(insert_query, 
            (quiz_id, title, description, topic, passing_score), fetch=False)
    except Exception as e:
        logger.error(f"Error saving AI quiz: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if result or result is not None:
        # Invalidate cache
        global cache_initialized
        cache_initialized = False
        
        # Save questions to quiz_questions table if it exists
        for i, q in enumerate(questions):
            try:
                question_id = f"{quiz_id}_q{i+1}"
                question_query = """
                INSERT INTO jeseci_academy.quiz_questions
                (question_id, quiz_id, question, options, correct_answer, explanation, order_index, points)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                ON CONFLICT (question_id) DO NOTHING
                """
                pg_manager.execute_query(question_query, (
                    question_id, quiz_id, q.get("question"),
                    q.get("options", []), q.get("correct_answer", 0),
                    q.get("explanation", ""), i + 1
                ), fetch=False)
            except Exception as e:
                logger.warning(f"Could not save question: {e}")
        
        new_quiz = {
            "quiz_id": quiz_id,
            "title": title,
            "description": description,
            "topic": topic,
            "difficulty": difficulty,
            "questions_count": len(questions),
            "passing_score": passing_score,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        return {"success": True, "quiz_id": quiz_id, "quiz": new_quiz}
    
    return {"success": False, "error": "Failed to save AI quiz"}
