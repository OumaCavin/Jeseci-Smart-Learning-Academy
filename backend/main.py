#!/usr/bin/env python3
"""
Jeseci Smart Learning Academy - FastAPI HTTP Server

This module provides HTTP REST API endpoints for the Jaclang walkers,
allowing the API to be accessed via web browsers and HTTP clients.

Author: Cavin Otieno
"""

import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import database and auth modules
import database as db_module
import user_auth as auth_module

# Initialize FastAPI app
app = FastAPI(
    title="Jeseci Smart Learning Academy API",
    description="HTTP REST API for the Jeseci Smart Learning Academy - Jaclang Backend",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Pydantic Models for HTTP API
# =============================================================================

class HealthResponse(BaseModel):
    service: str
    status: str
    version: str
    timestamp: str
    database_status: str
    ai_status: str
    architecture: str

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    learning_style: str = Field(default="visual")
    skill_level: str = Field(default="beginner")

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]
    message: str

class CourseResponse(BaseModel):
    success: bool
    courses: List[Dict[str, Any]]
    total: int

class LearningPathsResponse(BaseModel):
    success: bool
    paths: List[Dict[str, Any]]
    total: int
    categories: List[str]

class ConceptsResponse(BaseModel):
    success: bool
    concepts: List[Dict[str, Any]]
    total: int

class QuizzesResponse(BaseModel):
    success: bool
    quizzes: List[Dict[str, Any]]
    total: int

class ProgressResponse(BaseModel):
    user_id: str
    progress: Dict[str, Any]
    analytics: Dict[str, Any]
    learning_style: str
    skill_level: str
    recent_activity: List[Dict[str, Any]]

class UserProgressRequest(BaseModel):
    user_id: str

class SessionStartRequest(BaseModel):
    user_id: str
    module_id: str

class SessionEndRequest(BaseModel):
    session_id: str
    progress: float

class AIGenerateRequest(BaseModel):
    concept_name: str
    domain: str = "Computer Science"
    difficulty: str = "beginner"
    related_concepts: List[str] = []

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: List[int]

class AchievementsRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    message: str

class GraphConceptsResponse(BaseModel):
    success: bool
    concepts: List[Dict[str, Any]]
    count: int
    source: str

class GraphPathsResponse(BaseModel):
    success: bool
    paths: List[Dict[str, Any]]
    count: int
    source: str

class GraphRecommendationsResponse(BaseModel):
    success: bool
    user_id: str
    recommendations: List[Dict[str, Any]]
    count: int
    algorithm: str

# =============================================================================
# Core Endpoints
# =============================================================================

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Jeseci Smart Learning Academy API",
        "version": "7.0.0",
        "architecture": "Pure Jaclang Backend with FastAPI",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "core": ["/init", "/health"],
            "auth": ["/auth/register", "/auth/login"],
            "content": ["/courses", "/learning-paths", "/concepts", "/quizzes"],
            "progress": ["/progress", "/sessions/start", "/sessions/end"],
            "ai": ["/ai/generate", "/ai/chat"],
            "gamification": ["/achievements"],
            "graph": ["/graph/concepts", "/graph/paths", "/graph/recommendations"]
        }
    }

@app.get("/init", response_model=Dict[str, Any])
async def init():
    """Initialize and get API information"""
    return {
        "message": "Welcome to Jeseci Smart Learning Academy API!",
        "status": "initialized",
        "version": "7.0.0",
        "architecture": "Pure Jaclang Backend with FastAPI HTTP Server",
        "endpoints": {
            "health": "GET /health",
            "init": "GET /init",
            "auth": "POST /auth/register, POST /auth/login",
            "courses": "GET /courses",
            "progress": "POST /progress",
            "learning": "POST /sessions/start, POST /sessions/end",
            "ai": "POST /ai/generate",
            "analytics": "GET /analytics",
            "paths": "GET /learning-paths",
            "concepts": "GET /concepts",
            "quizzes": "GET /quizzes",
            "achievements": "POST /achievements",
            "chat": "POST /ai/chat"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    import datetime
    
    # Check OpenAI configuration
    api_key = os.getenv("OPENAI_API_KEY", "")
    ai_status = "available" if api_key else "fallback"
    
    return HealthResponse(
        service="Jeseci Smart Learning Academy API",
        status="healthy",
        version="7.0.0",
        timestamp=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        database_status="connected",
        ai_status=ai_status,
        architecture="Pure Jaclang Backend with FastAPI"
    )

# =============================================================================
# Authentication Endpoints
# =============================================================================

@app.post("/auth/register", response_model=Dict[str, Any])
async def register_user(request: UserCreateRequest):
    """Register a new user"""
    result = auth_module.register_user(
        request.username,
        request.email,
        request.password,
        request.first_name,
        request.last_name,
        request.learning_style,
        request.skill_level
    )
    
    if result['success']:
        return {
            "success": True,
            "user_id": result['user_id'],
            "username": result['username'],
            "email": result['email'],
            "message": result['message']
        }
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": result['error'],
                "code": result.get('code', 'ERROR'),
                "message": "User registration failed"
            }
        )

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(request: UserLoginRequest):
    """Authenticate user and return JWT token"""
    result = auth_module.authenticate_user(request.username, request.password)
    
    if result['success']:
        return TokenResponse(
            success=True,
            access_token=result['access_token'],
            token_type=result['token_type'],
            expires_in=result['expires_in'],
            user=result['user'],
            message=result['message']
        )
    else:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": result['error'],
                "code": result.get('code', 'ERROR'),
                "message": "Login failed"
            }
        )

# =============================================================================
# Content Endpoints
# =============================================================================

@app.get("/courses", response_model=CourseResponse)
async def get_courses():
    """Get all available courses"""
    courses = [
        {
            "course_id": "course_1",
            "title": "Introduction to Programming",
            "description": "Learn the fundamentals of programming with Python",
            "domain": "Computer Science",
            "difficulty": "beginner",
            "content_type": "interactive"
        },
        {
            "course_id": "course_2",
            "title": "Data Structures",
            "description": "Master essential data structures and algorithms",
            "domain": "Computer Science",
            "difficulty": "intermediate",
            "content_type": "interactive"
        },
        {
            "course_id": "course_3",
            "title": "Object-Spatial Programming",
            "description": "Learn about nodes, walkers, and graph-based programming",
            "domain": "Computer Science",
            "difficulty": "advanced",
            "content_type": "interactive"
        },
        {
            "course_id": "course_4",
            "title": "Machine Learning Basics",
            "description": "Introduction to ML concepts and algorithms",
            "domain": "Computer Science",
            "difficulty": "intermediate",
            "content_type": "interactive"
        },
        {
            "course_id": "course_5",
            "title": "Web Development",
            "description": "Build modern web applications",
            "domain": "Computer Science",
            "difficulty": "beginner",
            "content_type": "interactive"
        }
    ]
    
    return CourseResponse(
        success=True,
        courses=courses,
        total=len(courses)
    )

@app.get("/learning-paths", response_model=LearningPathsResponse)
async def get_learning_paths():
    """Get all learning paths"""
    paths = [
        {
            "id": "path_python",
            "title": "Python Mastery",
            "description": "Master Python from fundamentals to advanced concepts",
            "courses": ["course_1", "course_2", "course_4"],
            "modules": [
                {"id": "mod_python_basics", "title": "Python Basics", "type": "lesson", "duration": "2 hours", "completed": True},
                {"id": "mod_variables", "title": "Variables and Data Types", "type": "lesson", "duration": "1.5 hours", "completed": True},
                {"id": "mod_control_flow", "title": "Control Flow", "type": "lesson", "duration": "2 hours", "completed": False}
            ],
            "total_modules": 8,
            "completed_modules": 2,
            "duration": "8 weeks",
            "estimated_hours": 20,
            "difficulty": "beginner",
            "progress": 25
        },
        {
            "id": "path_web",
            "title": "Full-Stack Web Development",
            "description": "Build modern, responsive web applications from scratch",
            "courses": ["course_5", "course_1"],
            "modules": [
                {"id": "mod_html_basics", "title": "HTML Fundamentals", "type": "lesson", "duration": "1.5 hours", "completed": True},
                {"id": "mod_css_styling", "title": "CSS Styling", "type": "lesson", "duration": "2 hours", "completed": True},
                {"id": "mod_css_layouts", "title": "CSS Layouts & Flexbox", "type": "lesson", "duration": "2 hours", "completed": True}
            ],
            "total_modules": 8,
            "completed_modules": 3,
            "duration": "10 weeks",
            "estimated_hours": 25,
            "difficulty": "beginner",
            "progress": 37
        },
        {
            "id": "path_jaclang",
            "title": "Jaclang & Graph Programming",
            "description": "Master the innovative Jaclang language with nodes, walkers, and graph-based programming paradigms",
            "courses": ["course_3", "course_2"],
            "modules": [
                {"id": "mod_graph_intro", "title": "Introduction to Graph Theory", "type": "lesson", "duration": "2 hours", "completed": True},
                {"id": "mod_nodes_basics", "title": "Nodes Basics", "type": "lesson", "duration": "2 hours", "completed": False}
            ],
            "total_modules": 8,
            "completed_modules": 1,
            "duration": "12 weeks",
            "estimated_hours": 30,
            "difficulty": "advanced",
            "progress": 12
        }
    ]
    
    return LearningPathsResponse(
        success=True,
        paths=paths,
        total=len(paths),
        categories=["programming", "web-development", "programming-languages", "data-science", "devops"]
    )

@app.get("/concepts", response_model=ConceptsResponse)
async def get_concepts():
    """Get all educational concepts"""
    concepts = [
        {
            "id": "concept_oop",
            "name": "Object-Oriented Programming",
            "description": "Learn about classes, inheritance, and polymorphism",
            "domain": "Computer Science",
            "difficulty": "intermediate",
            "icon": "building",
            "related_concepts": ["Design Patterns", "SOLID Principles", "UML"]
        },
        {
            "id": "concept_graphs",
            "name": "Graph Theory",
            "description": "Understanding nodes, edges, and graph algorithms",
            "domain": "Computer Science",
            "difficulty": "intermediate",
            "icon": "graph",
            "related_concepts": ["Tree Structures", "Pathfinding", "Network Analysis"]
        },
        {
            "id": "concept_recursion",
            "name": "Recursion",
            "description": "Functions that call themselves to solve problems",
            "domain": "Computer Science",
            "difficulty": "intermediate",
            "icon": "recursive",
            "related_concepts": ["Base Cases", "Stack Overflow", "Dynamic Programming"]
        },
        {
            "id": "concept_ai",
            "name": "Machine Learning Basics",
            "description": "Introduction to supervised and unsupervised learning",
            "domain": "Computer Science",
            "difficulty": "intermediate",
            "icon": "brain",
            "related_concepts": ["Neural Networks", "Feature Engineering", "Model Training"]
        },
        {
            "id": "concept_algo",
            "name": "Algorithm Design",
            "description": "Creating efficient solutions to computational problems",
            "domain": "Computer Science",
            "difficulty": "advanced",
            "icon": "lightning",
            "related_concepts": ["Big O Notation", "Divide and Conquer", "Greedy Algorithms"]
        }
    ]
    
    return ConceptsResponse(
        success=True,
        concepts=concepts,
        total=len(concepts)
    )

@app.get("/quizzes", response_model=QuizzesResponse)
async def get_quizzes():
    """Get all available quizzes"""
    quizzes = [
        {
            "id": "quiz_python_basics",
            "title": "Python Basics Quiz",
            "description": "Test your understanding of Python fundamentals",
            "questions": [
                {
                    "id": "q1",
                    "question": "What is the output of print(type([]))?",
                    "options": ["<class 'array'>", "<class 'list'>", "<class 'tuple'>", "<class 'dict'>"],
                    "correct_answer": 1,
                    "explanation": "[] creates a list in Python"
                },
                {
                    "id": "q2",
                    "question": "Which keyword is used to create a function in Python?",
                    "options": ["function", "def", "func", "define"],
                    "correct_answer": 1,
                    "explanation": "def keyword is used to define functions"
                }
            ],
            "difficulty": "beginner",
            "estimated_time": 5,
            "completed": False,
            "score": None
        },
        {
            "id": "quiz_oop",
            "title": "Object-Oriented Programming Quiz",
            "description": "Test your OOP knowledge",
            "questions": [
                {
                    "id": "q1",
                    "question": "What does 'OOP' stand for?",
                    "options": ["Object-Oriented Programming", "Object-Optional Programming", "Oriented Object Programming", "Object Oriented Process"],
                    "correct_answer": 0,
                    "explanation": "OOP stands for Object-Oriented Programming"
                }
            ],
            "difficulty": "intermediate",
            "estimated_time": 10,
            "completed": False,
            "score": None
        }
    ]
    
    return QuizzesResponse(
        success=True,
        quizzes=quizzes,
        total=len(quizzes)
    )

# =============================================================================
# Progress & Sessions
# =============================================================================

@app.post("/progress", response_model=ProgressResponse)
async def get_user_progress(request: UserProgressRequest):
    """Get user progress"""
    progress_data = {
        "progress": {
            "courses_completed": 3,
            "lessons_completed": 15,
            "total_study_time": 450,
            "current_streak": 5,
            "average_score": 85.5
        },
        "analytics": {
            "completion_rate": 60.0,
            "total_sessions": 10,
            "completed_sessions": 3,
            "in_progress_sessions": 7,
            "average_progress": 72.0
        },
        "learning_style": "visual",
        "skill_level": "intermediate",
        "recent_activity": [
            {"action": "Completed lesson", "item": "Variables and Data Types", "time": "2025-12-22T10:30:00Z"},
            {"action": "Started course", "item": "Data Structures", "time": "2025-12-22T09:15:00Z"}
        ]
    }
    
    return ProgressResponse(
        user_id=request.user_id,
        progress=progress_data["progress"],
        analytics=progress_data["analytics"],
        learning_style=progress_data["learning_style"],
        skill_level=progress_data["skill_level"],
        recent_activity=progress_data["recent_activity"]
    )

@app.post("/sessions/start", response_model=Dict[str, Any])
async def start_learning_session(request: SessionStartRequest):
    """Start a new learning session"""
    import datetime
    session_id = "session_" + request.user_id + "_" + request.module_id + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    return {
        "success": True,
        "session_id": session_id,
        "user_id": request.user_id,
        "module_id": request.module_id,
        "status": "active",
        "message": "Learning session started"
    }

@app.post("/sessions/end", response_model=Dict[str, Any])
async def end_learning_session(request: SessionEndRequest):
    """End a learning session"""
    return {
        "success": True,
        "session_id": request.session_id,
        "progress": request.progress,
        "status": "completed",
        "message": "Learning session ended"
    }

# =============================================================================
# AI Endpoints
# =============================================================================

@app.post("/ai/generate", response_model=Dict[str, Any])
async def generate_ai_content(request: AIGenerateRequest):
    """Generate AI-powered learning content"""
    import datetime
    
    return {
        "success": True,
        "concept_name": request.concept_name,
        "domain": request.domain,
        "difficulty": request.difficulty,
        "content": f"AI-generated content for {request.concept_name}. This lesson covers fundamental concepts and provides hands-on examples.",
        "related_concepts": request.related_concepts,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "ai_generator"
    }

@app.post("/ai/chat", response_model=Dict[str, Any])
async def chat_with_ai(request: ChatRequest):
    """Chat with the AI tutor"""
    import datetime
    
    responses = [
        "That's a great question! Let me explain...",
        "I understand what you're asking. Here's my perspective...",
        "Based on your learning history, I'd recommend focusing on...",
        "Great thinking! This concept relates to...",
        "Let me break this down for you in simple terms..."
    ]
    
    response_text = responses[0] + "\n\nWould you like me to elaborate on any specific aspect of this topic?"
    
    return {
        "success": True,
        "response": response_text,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

# =============================================================================
# Gamification Endpoints
# =============================================================================

@app.post("/achievements", response_model=Dict[str, Any])
async def get_achievements(request: AchievementsRequest):
    """Get user achievements"""
    import datetime
    
    all_achievements = [
        {
            "id": "first_course",
            "name": "First Steps",
            "description": "Complete your first course",
            "icon": "target",
            "earned": True,
            "earned_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "requirement": "Complete 1 course",
            "category": "learning"
        },
        {
            "id": "course_master",
            "name": "Course Master",
            "description": "Complete 5 courses",
            "icon": "trophy",
            "earned": False,
            "earned_at": None,
            "requirement": "Complete 5 courses",
            "category": "learning"
        },
        {
            "id": "streak_week",
            "name": "Week Warrior",
            "description": "Maintain a 7-day learning streak",
            "icon": "fire",
            "earned": False,
            "earned_at": None,
            "requirement": "7-day learning streak",
            "category": "consistency"
        }
    ]
    
    return {
        "success": True,
        "achievements": all_achievements,
        "total": len(all_achievements),
        "earned_count": 1,
        "total_points": 100
    }

# =============================================================================
# Graph Database Endpoints
# =============================================================================

@app.get("/graph/concepts", response_model=GraphConceptsResponse)
async def get_graph_concepts():
    """Get concepts from Neo4j graph database"""
    manager = db_module.get_neo4j_manager()
    
    query = """
    MATCH (c:Concept)
    RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
           c.category AS category, c.difficulty AS difficulty,
           c.description AS description, c.estimated_duration AS duration,
           c.prerequisites_count AS prereq_count
    ORDER BY c.name
    """
    
    result = manager.execute_query(query, None)
    
    # Convert result to list of dicts
    concepts = []
    if result:
        for record in result:
            concepts.append({
                "id": record.get("id", ""),
                "name": record.get("name", ""),
                "display_name": record.get("display_name", ""),
                "category": record.get("category", ""),
                "difficulty": record.get("difficulty", ""),
                "description": record.get("description", ""),
                "duration": record.get("duration", 0),
                "prereq_count": record.get("prereq_count", 0)
            })
    
    return GraphConceptsResponse(
        success=True,
        concepts=concepts,
        count=len(concepts),
        source="graph_database"
    )

@app.get("/graph/paths", response_model=GraphPathsResponse)
async def get_graph_paths():
    """Get learning paths from Neo4j graph database"""
    manager = db_module.get_neo4j_manager()
    
    query = """
    MATCH (p:LearningPath)
    OPTIONAL MATCH (p)-[:PathContains]->(c:Concept)
    WITH p, count(c) AS concept_count
    RETURN p.path_id AS id, p.name AS name, p.title AS title, p.description AS description,
           p.difficulty AS difficulty, p.estimated_duration AS duration,
           p.concept_count AS total_concepts, concept_count
    ORDER BY p.name
    """
    
    result = manager.execute_query(query, None)
    
    # Convert result to list of dicts
    paths = []
    if result:
        for record in result:
            paths.append({
                "id": record.get("id", ""),
                "name": record.get("name", ""),
                "title": record.get("title", ""),
                "description": record.get("description", ""),
                "difficulty": record.get("difficulty", ""),
                "duration": record.get("duration", 0),
                "total_concepts": record.get("total_concepts", 0)
            })
    
    return GraphPathsResponse(
        success=True,
        paths=paths,
        count=len(paths),
        source="graph_database"
    )

@app.get("/graph/recommendations/{user_id}", response_model=GraphRecommendationsResponse)
async def get_graph_recommendations(user_id: str, limit: int = Query(default=5, le=20)):
    """Get personalized recommendations from Neo4j"""
    manager = db_module.get_neo4j_manager()
    
    query = """
    MATCH (u:User {user_id: $user_id})
    MATCH (c:Concept)
    WHERE NOT (u)-[:Completed]->(c)
    OPTIONAL MATCH (c)-[:PREREQUISITE]->(prereq:Concept)
    WITH c, collect(DISTINCT prereq.concept_id) AS prereqs
    WHERE all(prereq IN prereqs WHERE (u)-[:Completed]->(:Concept {concept_id: prereq}))
    RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
           c.category AS category, c.difficulty AS difficulty,
           c.estimated_duration AS duration, size(prereqs) AS prereq_count
    LIMIT $limit
    """
    
    result = manager.execute_query(query, {"user_id": user_id, "limit": limit})
    
    # Convert result to list of dicts
    recommendations = []
    if result:
        for record in result:
            recommendations.append({
                "id": record.get("id", ""),
                "name": record.get("name", ""),
                "display_name": record.get("display_name", ""),
                "category": record.get("category", ""),
                "difficulty": record.get("difficulty", ""),
                "duration": record.get("duration", 0),
                "prereq_count": record.get("prereq_count", 0)
            })
    
    return GraphRecommendationsResponse(
        success=True,
        user_id=user_id,
        recommendations=recommendations,
        count=len(recommendations),
        algorithm="prerequisite_based"
    )

@app.get("/graph/stats", response_model=Dict[str, Any])
async def get_graph_stats():
    """Get graph database statistics"""
    manager = db_module.get_neo4j_manager()
    
    concept_count = manager.execute_query("MATCH (c:Concept) RETURN count(c) AS count", None)
    user_count = manager.execute_query("MATCH (u:User) RETURN count(u) AS count", None)
    path_count = manager.execute_query("MATCH (p:LearningPath) RETURN count(p) AS count", None)
    rel_count = manager.execute_query("MATCH ()-[r:PREREQUISITE]->() RETURN count(r) AS count", None)
    
    return {
        "success": True,
        "graph_stats": {
            "concepts": concept_count[0]['count'] if concept_count else 0,
            "users": user_count[0]['count'] if user_count else 0,
            "learning_paths": path_count[0]['count'] if path_count else 0,
            "prerequisite_relationships": rel_count[0]['count'] if rel_count else 0
        }
    }

# =============================================================================
# Database Health Endpoints
# =============================================================================

@app.get("/db/health", response_model=Dict[str, Any])
async def check_database_health():
    """Check database connections"""
    result = db_module.test_all_connections()
    
    return {
        "postgresql": result.get('postgresql', False),
        "neo4j": result.get('neo4j', False),
        "status": "healthy" if result.get('postgresql') else "degraded"
    }

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
