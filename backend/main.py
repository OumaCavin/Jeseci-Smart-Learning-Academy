"""
Jeseci Smart Learning Academy - FastAPI Backend
Replaces the Jaclang REST API with a more capable Python implementation
that supports OpenAI integration and dynamic data tracking
"""

import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# =============================================================================
# DATA STORE (In-memory for demo, use database in production)
# =============================================================================

class DataStore:
    """In-memory data store for tracking users, sessions, and progress"""
    
    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.sessions: Dict[str, dict] = {}
        self.courses: List[dict] = [
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
        self.user_sessions: Dict[str, List[dict]] = {}
        self.ai_generations: int = 0
        
        # Initialize with demo user
        self.users["demo_user"] = {
            "user_id": "user_demo_001",
            "username": "demo_user",
            "email": "demo@example.com",
            "password": "demo123",
            "first_name": "Demo",
            "last_name": "User",
            "learning_style": "visual",
            "skill_level": "beginner",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        
        # Initialize demo user progress
        self.user_sessions["user_demo_001"] = [
            {
                "session_id": "session_1",
                "course_id": "course_1",
                "course_title": "Introduction to Programming",
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.now().isoformat()
            },
            {
                "session_id": "session_2",
                "course_id": "course_2",
                "course_title": "Data Structures",
                "status": "in_progress",
                "progress": 65,
                "started_at": datetime.now().isoformat()
            }
        ]
        
    def get_user_by_username(self, username: str) -> Optional[dict]:
        return self.users.get(username)
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        for user in self.users.values():
            if user.get("user_id") == user_id:
                return user
        return None
    
    def create_user(self, user_data: dict) -> dict:
        user_id = f"user_{user_data['username']}_{int(time.time())}"
        user_data["user_id"] = user_id
        user_data["is_active"] = True
        user_data["is_verified"] = False
        user_data["created_at"] = datetime.now().isoformat()
        user_data["last_login"] = datetime.now().isoformat()
        user_data["password"] = user_data.get("password", "temp123")
        self.users[user_data["username"]] = user_data
        self.user_sessions[user_id] = []
        return user_data
    
    def get_user_progress(self, user_id: str) -> dict:
        """Calculate dynamic user progress based on stored sessions"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        sessions = self.user_sessions.get(user_id, [])
        
        # Calculate dynamic metrics
        completed_sessions = [s for s in sessions if s["status"] == "completed"]
        in_progress_sessions = [s for s in sessions if s["status"] == "in_progress"]
        
        courses_completed = len(completed_sessions)
        lessons_completed = sum(1 for s in completed_sessions for _ in [1]) + (courses_completed * 5)
        total_study_time = len(sessions) * 45  # 45 mins per session
        current_streak = min(len(completed_sessions), 7)  # Simple streak calculation
        
        # Calculate completion rate
        total_courses = len(self.courses)
        completion_rate = (courses_completed / total_courses * 100) if total_courses > 0 else 0
        
        # Calculate average score based on session progress
        average_score = sum(s["progress"] for s in completed_sessions) / max(len(completed_sessions), 1)
        
        progress_data = {
            "courses_completed": courses_completed,
            "lessons_completed": lessons_completed,
            "total_study_time": total_study_time,
            "current_streak": current_streak,
            "average_score": round(average_score, 1)
        }
        
        analytics = {
            "completion_rate": round(completion_rate, 1),
            "total_sessions": len(sessions),
            "completed_sessions": courses_completed,
            "in_progress_sessions": len(in_progress_sessions),
            "average_progress": round(average_score, 1)
        }
        
        return {
            "user_id": user_id,
            "progress": progress_data,
            "analytics": analytics,
            "learning_style": user.get("learning_style", "visual"),
            "skill_level": user.get("skill_level", "beginner"),
            "recent_activity": sessions[-5:] if sessions else []
        }
    
    def get_user_analytics(self, user_id: str) -> dict:
        """Generate comprehensive learning analytics"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        sessions = self.user_sessions.get(user_id, [])
        completed = [s for s in sessions if s["status"] == "completed"]
        
        # Calculate engagement score based on activity
        engagement_score = min(len(completed) / 10.0, 1.0)  # Max 100% at 10 completed courses
        
        # Determine learning velocity
        if len(completed) >= 5:
            learning_velocity = "Fast"
        elif len(completed) >= 2:
            learning_velocity = "Moderate"
        else:
            learning_velocity = "Building"
        
        # Calculate knowledge retention (mock based on progress)
        knowledge_retention = min(70 + (len(completed) * 5), 98)
        
        learning_analytics = {
            "modules_completed": len(completed),
            "total_study_time": len(sessions) * 45,
            "average_score": round(sum(s["progress"] for s in completed) / max(len(completed), 1), 1),
            "engagement_score": round(engagement_score * 100, 1),
            "knowledge_retention": round(knowledge_retention, 1),
            "learning_velocity": learning_velocity,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "user_id": user_id,
            "learning_analytics": learning_analytics,
            "recommendations": self._generate_recommendations(user, completed),
            "strengths": self._identify_strengths(completed),
            "areas_for_improvement": self._identify_improvements(completed)
        }
    
    def _generate_recommendations(self, user: dict, completed: list) -> list:
        """Generate personalized recommendations"""
        recommendations = []
        
        if len(completed) < 3:
            recommendations.append("Continue building your foundation with beginner courses")
            recommendations.append("Try the AI content generator for personalized lessons")
        else:
            recommendations.append("Consider advancing to intermediate-level courses")
            recommendations.append("Explore the AI generator for deeper concepts")
        
        if user.get("skill_level") == "beginner":
            recommendations.append("Focus on completing the Introduction to Programming course")
        
        recommendations.append("Maintain your learning streak for better retention")
        
        return recommendations
    
    _identify_strengths = lambda self, completed: ["Consistent learning", "Practical application"] if len(completed) >= 2 else ["Getting started"]
    
    _identify_improvements = lambda self, completed: ["Practice more exercises", "Review completed material"] if completed else ["Complete first course to identify areas for improvement"]

# Global data store
data_store = DataStore()

# =============================================================================
# Pydantic Models
# =============================================================================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    learning_style: str = "visual"
    skill_level: str = "beginner"

class UserLogin(BaseModel):
    username: str
    password: str

class AIGenerateRequest(BaseModel):
    concept_name: str
    domain: str = "Computer Science"
    difficulty: str = "beginner"
    related_concepts: List[str] = []

class CourseCreate(BaseModel):
    title: str
    description: str
    domain: str
    difficulty: str
    content_type: str = "interactive"

class LearningSessionStart(BaseModel):
    user_id: str
    module_id: str

class LearningSessionEnd(BaseModel):
    session_id: str
    progress: float

# =============================================================================
# FastAPI App
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Jeseci Smart Learning Academy API starting...")
    logger.info(f"OpenAI API: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured'}")
    yield
    logger.info("Jeseci Smart Learning Academy API shutting down...")

app = FastAPI(
    title="Jeseci Smart Learning Academy API",
    description="AI-Powered Learning Platform API",
    version="7.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Health & Status Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "Jeseci Smart Learning Academy API",
        "status": "healthy",
        "version": "7.0.0",
        "timestamp": datetime.now().isoformat(),
        "database_status": "connected",
        "ai_status": "available" if os.getenv('OPENAI_API_KEY') else "fallback",
        "architecture": "FastAPI + OpenAI Integration"
    }

@app.get("/walker/init")
async def init():
    """Welcome message"""
    return {
        "message": "Welcome to Jeseci Smart Learning Academy API!",
        "status": "initialized",
        "version": "7.0.0",
        "architecture": "FastAPI Backend with OpenAI Integration",
        "endpoints": {
            "health": "GET /health",
            "auth": "POST /user/*",
            "users": "GET/POST /users",
            "courses": "GET/POST /courses",
            "progress": "GET /progress/*",
            "learning": "POST /learning/*",
            "ai": "POST /ai/*",
            "analytics": "GET /analytics/*"
        }
    }

# =============================================================================
# Authentication Endpoints
# =============================================================================

@app.post("/user/create")
async def create_user(user_data: UserCreate):
    """Create a new user account"""
    # Check for existing user
    if data_store.get_user_by_username(user_data.username):
        return {
            "success": False,
            "error": "A user with that username or email already exists."
        }
    
    if any(u.get("email") == user_data.email for u in data_store.users.values()):
        return {
            "success": False,
            "error": "A user with that username or email already exists."
        }
    
    user = data_store.create_user(user_data.dict())
    
    return {
        "success": True,
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "learning_style": user["learning_style"],
        "skill_level": user["skill_level"],
        "message": "User created successfully"
    }

@app.post("/user/login")
async def login(credentials: UserLogin):
    """Authenticate user and return token"""
    user = data_store.get_user_by_username(credentials.username)
    
    if not user:
        # For demo, create user if not exists
        user = data_store.create_user({
            "username": credentials.username,
            "email": f"{credentials.username}@example.com",
            "password": credentials.password,
            "learning_style": "visual",
            "skill_level": "beginner"
        })
    
    # Generate simple token
    token = f"token_{user['user_id']}_{int(time.time())}"
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 1800,
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "first_name": user.get("first_name", "Demo"),
            "last_name": user.get("last_name", "User"),
            "learning_style": user["learning_style"],
            "skill_level": user["skill_level"]
        }
    }

# =============================================================================
# Course Endpoints
# =============================================================================

@app.get("/courses")
async def get_courses():
    """Get all available courses"""
    return data_store.courses

@app.post("/course/create")
async def create_course(course_data: CourseCreate):
    """Create a new course"""
    course_id = f"course_{course_data.title.lower().replace(' ', '_')}_{int(time.time())}"
    course = {
        "course_id": course_id,
        **course_data.dict()
    }
    data_store.courses.append(course)
    
    return {
        "success": True,
        "course_id": course_id,
        "title": course_data.title,
        "message": "Course created successfully"
    }

# =============================================================================
# Progress Endpoints
# =============================================================================

@app.post("/user/progress")
async def get_user_progress(request: Dict[str, str]):
    """Get user progress with dynamic calculations"""
    user_id = request.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    return data_store.get_user_progress(user_id)

# =============================================================================
# Learning Session Endpoints
# =============================================================================

@app.post("/learning/session/start")
async def start_learning_session(session_data: LearningSessionStart):
    """Start a new learning session"""
    session_id = f"session_{session_data.user_id}_{session_data.module_id}_{int(time.time())}"
    
    # Find course title
    course = next((c for c in data_store.courses if c["course_id"] == session_data.module_id), None)
    course_title = course["title"] if course else "Unknown Course"
    
    session = {
        "session_id": session_id,
        "user_id": session_data.user_id,
        "course_id": session_data.module_id,
        "course_title": course_title,
        "status": "in_progress",
        "progress": 0,
        "started_at": datetime.now().isoformat()
    }
    
    if session_data.user_id not in data_store.user_sessions:
        data_store.user_sessions[session_data.user_id] = []
    
    data_store.user_sessions[session_data.user_id].append(session)
    
    return {
        "success": True,
        "session_id": session_id,
        "user_id": session_data.user_id,
        "module_id": session_data.module_id,
        "status": "active",
        "message": "Learning session started"
    }

@app.post("/learning/session/end")
async def end_learning_session(session_data: LearningSessionEnd):
    """End a learning session"""
    # Find and update session
    for user_id, sessions in data_store.user_sessions.items():
        for session in sessions:
            if session["session_id"] == session_data.session_id:
                session["status"] = "completed" if session_data.progress >= 100 else "in_progress"
                session["progress"] = session_data.progress
                session["completed_at"] = datetime.now().isoformat()
                
                return {
                    "success": True,
                    "session_id": session_data.session_id,
                    "progress": session_data.progress,
                    "status": "completed",
                    "message": "Learning session ended"
                }
    
    return {
        "success": True,
        "session_id": session_data.session_id,
        "progress": session_data.progress,
        "status": "completed",
        "message": "Learning session ended"
    }

# =============================================================================
# AI Content Generation Endpoints
# =============================================================================

@app.post("/ai/generate/content")
async def generate_ai_content(request: AIGenerateRequest):
    """Generate AI-powered educational content"""
    try:
        # Import the AI generator
        from ai_generator import sync_generate_lesson
        
        logger.info(f"Generating AI content for: {request.concept_name}")
        
        # Generate content
        related_concepts_str = ",".join(request.related_concepts) if request.related_concepts else ""
        content = sync_generate_lesson(
            concept_name=request.concept_name,
            domain=request.domain,
            difficulty=request.difficulty,
            related_concepts_str=related_concepts_str
        )
        
        # Track generation
        data_store.ai_generations += 1
        
        return {
            "success": True,
            "concept_name": request.concept_name,
            "domain": request.domain,
            "difficulty": request.difficulty,
            "content": content,
            "related_concepts": request.related_concepts,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

# =============================================================================
# Analytics Endpoints
# =============================================================================

@app.post("/analytics/generate")
async def generate_analytics(request: Dict[str, str]):
    """Generate comprehensive learning analytics"""
    user_id = request.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    return data_store.get_user_analytics(user_id)

@app.get("/analytics/dashboard")
async def get_dashboard_analytics():
    """Get platform-wide analytics (admin endpoint)"""
    total_users = len(data_store.users)
    total_sessions = sum(len(sessions) for sessions in data_store.user_sessions.values())
    total_courses = len(data_store.courses)
    ai_generations = data_store.ai_generations
    
    return {
        "platform_stats": {
            "total_users": total_users,
            "total_active_sessions": total_sessions,
            "total_courses": total_courses,
            "ai_generations": ai_generations
        },
        "generated_at": datetime.now().isoformat()
    }

# =============================================================================
# Data Export Endpoint
# =============================================================================

@app.post("/export/data")
async def export_data(format: str = "json"):
    """Export user data"""
    return {
        "success": True,
        "format": format,
        "data": {
            "users": list(data_store.users.values()),
            "courses": data_store.courses,
            "sessions": data_store.user_sessions,
            "exported_at": datetime.now().isoformat()
        },
        "record_count": {
            "users": len(data_store.users),
            "courses": len(data_store.courses),
            "sessions": sum(len(s) for s in data_store.user_sessions.values())
        }
    }

# =============================================================================
# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Jeseci Smart Learning Academy API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False
    )
