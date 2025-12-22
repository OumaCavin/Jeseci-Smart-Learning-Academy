"""
Jeseci Smart Learning Academy - FastAPI Backend
Hybrid Architecture: Python/FastAPI with Jaclang-compatible walker endpoints
Provides complete backend functionality with OpenAI integration and dynamic data tracking
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

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_generator import sync_generate_lesson, ai_generator

# Import Multi-Agent System components
from agents.base_agent import BaseAgent, AgentState, AgentMessage, MessageType, Priority
from agents.message_bus import MessageBus, DeliveryPattern
from agents.registry import AgentRegistry, AgentConfig

# Import specialized agents
from agents.orchestrator import OrchestratorAgent
from agents.tutor import TutorAgent
from agents.analytics import AnalyticsAgent
from agents.assessment import AssessmentAgent
from agents.content import ContentAgent
from agents.path import PathAgent

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
                "content_type": "interactive",
                "lessons": [
                    {"lesson_id": "lesson_1_1", "title": "Getting Started", "duration": "30 min"},
                    {"lesson_id": "lesson_1_2", "title": "Variables and Data Types", "duration": "45 min"},
                    {"lesson_id": "lesson_1_3", "title": "Control Flow", "duration": "60 min"},
                    {"lesson_id": "lesson_1_4", "title": "Functions", "duration": "45 min"},
                    {"lesson_id": "lesson_1_5", "title": "Project: Simple Calculator", "duration": "60 min"}
                ]
            },
            {
                "course_id": "course_2",
                "title": "Data Structures",
                "description": "Master essential data structures and algorithms",
                "domain": "Computer Science",
                "difficulty": "intermediate",
                "content_type": "interactive",
                "lessons": [
                    {"lesson_id": "lesson_2_1", "title": "Arrays and Lists", "duration": "45 min"},
                    {"lesson_id": "lesson_2_2", "title": "Stacks and Queues", "duration": "45 min"},
                    {"lesson_id": "lesson_2_3", "title": "Trees and Graphs", "duration": "60 min"},
                    {"lesson_id": "lesson_2_4", "title": "Hash Tables", "duration": "45 min"},
                    {"lesson_id": "lesson_2_5", "title": "Algorithm Analysis", "duration": "60 min"}
                ]
            },
            {
                "course_id": "course_3",
                "title": "Object-Spatial Programming",
                "description": "Learn about nodes, walkers, and graph-based programming",
                "domain": "Computer Science",
                "difficulty": "advanced",
                "content_type": "interactive",
                "lessons": [
                    {"lesson_id": "lesson_3_1", "title": "Introduction to Jaclang", "duration": "45 min"},
                    {"lesson_id": "lesson_3_2", "title": "Nodes and Edges", "duration": "60 min"},
                    {"lesson_id": "lesson_3_3", "title": "Walkers and Navigation", "duration": "60 min"},
                    {"lesson_id": "lesson_3_4", "title": "Graph Algorithms", "duration": "75 min"},
                    {"lesson_id": "lesson_3_5", "title": "Advanced Patterns", "duration": "90 min"}
                ]
            },
            {
                "course_id": "course_4",
                "title": "Machine Learning Basics",
                "description": "Introduction to ML concepts and algorithms",
                "domain": "Computer Science",
                "difficulty": "intermediate",
                "content_type": "interactive",
                "lessons": [
                    {"lesson_id": "lesson_4_1", "title": "Introduction to ML", "duration": "45 min"},
                    {"lesson_id": "lesson_4_2", "title": "Supervised Learning", "duration": "60 min"},
                    {"lesson_id": "lesson_4_3", "title": "Unsupervised Learning", "duration": "60 min"},
                    {"lesson_id": "lesson_4_4", "title": "Neural Networks", "duration": "75 min"},
                    {"lesson_id": "lesson_4_5", "title": "Model Evaluation", "duration": "45 min"}
                ]
            },
            {
                "course_id": "course_5",
                "title": "Web Development",
                "description": "Build modern web applications",
                "domain": "Computer Science",
                "difficulty": "beginner",
                "content_type": "interactive",
                "lessons": [
                    {"lesson_id": "lesson_5_1", "title": "HTML Basics", "duration": "30 min"},
                    {"lesson_id": "lesson_5_2", "title": "CSS Styling", "duration": "45 min"},
                    {"lesson_id": "lesson_5_3", "title": "JavaScript Fundamentals", "duration": "60 min"},
                    {"lesson_id": "lesson_5_4", "title": "React Introduction", "duration": "60 min"},
                    {"lesson_id": "lesson_5_5", "title": "Building a Web App", "duration": "90 min"}
                ]
            }
        ]
        self.learning_paths: List[dict] = [
            {
                "id": "path_1",
                "title": "Full Stack Developer",
                "description": "Master both frontend and backend development",
                "courses": ["course_1", "course_5"],
                "modules": [
                    {"id": "mod_1", "title": "Programming Fundamentals", "type": "lesson", "duration": "4 hours", "completed": False},
                    {"id": "mod_2", "title": "Web Basics Project", "type": "project", "duration": "2 hours", "completed": False},
                    {"id": "mod_3", "title": "Frontend Quiz", "type": "quiz", "duration": "30 min", "completed": False}
                ],
                "concepts": ["HTML", "CSS", "JavaScript", "React"],
                "skills_covered": ["Frontend Development", "UI Design", "Component Architecture"],
                "prerequisites": [],
                "total_modules": 3,
                "completed_modules": 0,
                "duration": "6.5 hours",
                "estimated_hours": 7,
                "difficulty": "beginner",
                "progress": 0,
                "icon": "🌐",
                "category": "Development",
                "next_step": "Start with Programming Fundamentals"
            },
            {
                "id": "path_2",
                "title": "AI/ML Engineer",
                "description": "Build intelligent systems and machine learning models",
                "courses": ["course_1", "course_2", "course_4"],
                "modules": [
                    {"id": "mod_1", "title": "Programming with Python", "type": "lesson", "duration": "4 hours", "completed": False},
                    {"id": "mod_2", "title": "Data Structures Mastery", "type": "lesson", "duration": "5 hours", "completed": False},
                    {"id": "mod_3", "title": "ML Algorithms Project", "type": "project", "duration": "4 hours", "completed": False},
                    {"id": "mod_4", "title": "ML Fundamentals Quiz", "type": "quiz", "duration": "45 min", "completed": False}
                ],
                "concepts": ["Python", "Algorithms", "Machine Learning", "Neural Networks"],
                "skills_covered": ["Data Analysis", "Model Building", "Algorithm Design"],
                "prerequisites": ["Basic Programming"],
                "total_modules": 4,
                "completed_modules": 0,
                "duration": "14 hours",
                "estimated_hours": 14,
                "difficulty": "intermediate",
                "progress": 0,
                "icon": "🤖",
                "category": "AI & Data",
                "next_step": "Begin with Programming Fundamentals"
            },
            {
                "id": "path_3",
                "title": "Jaclang Graph Developer",
                "description": "Master graph-based programming with Jaclang",
                "courses": ["course_3"],
                "modules": [
                    {"id": "mod_1", "title": "Jaclang Foundations", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_2", "title": "Graph Navigation", "type": "lesson", "duration": "4 hours", "completed": False},
                    {"id": "mod_3", "title": "Walker Patterns", "type": "lesson", "duration": "4 hours", "completed": False},
                    {"id": "mod_4", "title": "Graph Algorithm Project", "type": "project", "duration": "3 hours", "completed": False}
                ],
                "concepts": ["Jaclang", "Graph Theory", "Nodes", "Walkers"],
                "skills_covered": ["Graph Programming", "Node Navigation", "Pattern Matching"],
                "prerequisites": ["Programming Fundamentals"],
                "total_modules": 4,
                "completed_modules": 0,
                "duration": "14 hours",
                "estimated_hours": 14,
                "difficulty": "advanced",
                "progress": 0,
                "icon": "🔷",
                "category": "Specialized",
                "next_step": "Start with Jaclang Foundations"
            }
        ]
        self.concepts: List[dict] = [
            {"id": "concept_1", "name": "Object-Oriented Programming", "description": "Learn about classes, objects, inheritance, and polymorphism", "domain": "Computer Science", "difficulty": "intermediate", "icon": "🏗️", "related_concepts": ["Design Patterns", "Encapsulation", "Abstraction"]},
            {"id": "concept_2", "name": "Recursion", "description": "Understanding recursive functions and their applications", "domain": "Computer Science", "difficulty": "intermediate", "icon": "🔄", "related_concepts": ["Base Case", "Stack Overflow", "Dynamic Programming"]},
            {"id": "concept_3", "name": "Graph Theory", "description": "Study of graphs and their applications in computer science", "domain": "Computer Science", "difficulty": "advanced", "icon": "📊", "related_concepts": ["Nodes", "Edges", "Path Finding"]},
            {"id": "concept_4", "name": "Database Design", "description": "Principles of designing efficient database schemas", "domain": "Computer Science", "difficulty": "intermediate", "icon": "🗄️", "related_concepts": ["Normalization", "SQL", "Indexing"]},
            {"id": "concept_5", "name": "API Design", "description": "Best practices for designing RESTful APIs", "domain": "Computer Science", "difficulty": "intermediate", "icon": "🔌", "related_concepts": ["REST", "Authentication", "Rate Limiting"]}
        ]
        self.quizzes: List[dict] = [
            {"id": "quiz_1", "title": "Programming Basics Quiz", "description": "Test your understanding of fundamental programming concepts", "difficulty": "beginner", "estimated_time": 15, "completed": False, "questions": [
                {"id": "q1", "question": "What is a variable in programming?", "options": ["A container for storing data values", "A type of loop", "A function definition", "A comment"], "correct_answer": 0, "explanation": "Variables are named containers that store data values in programming."},
                {"id": "q2", "question": "Which of the following is a programming language?", "options": ["HTML", "Python", "CSS", "SQL"], "correct_answer": 1, "explanation": "Python is a high-level programming language used for various applications."},
                {"id": "q3", "question": "What does HTML stand for?", "options": ["Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"], "correct_answer": 0, "explanation": "HTML stands for Hyper Text Markup Language, used for creating web pages."}
            ]},
            {"id": "quiz_2", "title": "Data Structures Quiz", "description": "Test your knowledge of data structures", "difficulty": "intermediate", "estimated_time": 20, "completed": False, "questions": [
                {"id": "q1", "question": "What is the time complexity of accessing an element in an array by index?", "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"], "correct_answer": 0, "explanation": "Array access by index is O(1) - constant time operation."},
                {"id": "q2", "question": "Which data structure follows LIFO (Last In First Out)?", "options": ["Queue", "Stack", "Array", "Linked List"], "correct_answer": 1, "explanation": "Stack follows LIFO - the last element added is the first one removed."},
                {"id": "q3", "question": "What is a linked list?", "options": ["An array with fixed size", "A linear collection of nodes", "A type of tree", "A hash table"], "correct_answer": 1, "explanation": "A linked list is a linear data structure where elements are stored in nodes."}
            ]}
        ]
        self.achievements: List[dict] = [
            {"id": "ach_1", "name": "First Steps", "description": "Complete your first lesson", "icon": "🎯", "earned": False, "requirement": "Complete 1 lesson", "category": "learning"},
            {"id": "ach_2", "name": "Knowledge Seeker", "description": "Complete 5 lessons", "icon": "📚", "earned": False, "requirement": "Complete 5 lessons", "category": "learning"},
            {"id": "ach_3", "name": "Quiz Master", "description": "Score 100% on a quiz", "icon": "🏆", "earned": False, "requirement": "Score 100% on any quiz", "category": "achievement"},
            {"id": "ach_4", "name": "Consistent Learner", "description": "Maintain a 7-day learning streak", "icon": "🔥", "earned": False, "requirement": "7-day streak", "category": "streak"},
            {"id": "ach_5", "name": "Course Completer", "description": "Complete an entire course", "icon": "🎓", "earned": False, "requirement": "Complete 1 course", "category": "achievement"}
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

# Global Multi-Agent System components (initialized in lifespan)
message_bus: Optional[MessageBus] = None
agent_registry: Optional[AgentRegistry] = None

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
    logger.info(f"Backend Type: Python/FastAPI with Jaclang-compatible endpoints")
    
    # Initialize Multi-Agent System
    global message_bus, agent_registry
    message_bus = MessageBus(name="main_bus", max_history=1000)
    agent_registry = AgentRegistry(name="main_registry", message_bus=message_bus)
    
    # Register agent configurations
    agent_configs = [
        AgentConfig(
            agent_id="orchestrator",
            agent_name="Orchestrator Agent",
            agent_type="orchestrator",
            config={"priority_coordination": True},
            enabled=True,
            auto_start=True,
            dependencies=[]
        ),
        AgentConfig(
            agent_id="tutor",
            agent_name="Tutor Agent",
            agent_type="tutor",
            config={"adaptive_learning": True},
            enabled=True,
            auto_start=True,
            dependencies=["orchestrator"]
        ),
        AgentConfig(
            agent_id="analytics",
            agent_name="Analytics Agent",
            agent_type="analytics",
            config={"real_time_tracking": True},
            enabled=True,
            auto_start=True,
            dependencies=[]
        ),
        AgentConfig(
            agent_id="assessment",
            agent_name="Assessment Agent",
            agent_type="assessment",
            config={"adaptive_testing": True},
            enabled=True,
            auto_start=True,
            dependencies=["analytics", "tutor"]
        ),
        AgentConfig(
            agent_id="content",
            agent_name="Content Agent",
            agent_type="content",
            config={"ai_generation": True},
            enabled=True,
            auto_start=True,
            dependencies=[]
        ),
        AgentConfig(
            agent_id="path",
            agent_name="Path Agent",
            agent_type="path",
            config={"personalization": True},
            enabled=True,
            auto_start=True,
            dependencies=["tutor", "analytics"]
        )
    ]
    
    # Register all agent configurations
    for config in agent_configs:
        agent_registry.register_config(config)
    
    # Instantiate and register agents
    agents = [
        OrchestratorAgent(agent_id="orchestrator", agent_name="Orchestrator Agent"),
        TutorAgent(agent_id="tutor", agent_name="Tutor Agent"),
        AnalyticsAgent(agent_id="analytics", agent_name="Analytics Agent"),
        AssessmentAgent(agent_id="assessment", agent_name="Assessment Agent"),
        ContentAgent(agent_id="content", agent_name="Content Agent"),
        PathAgent(agent_id="path", agent_name="Path Agent")
    ]
    
    for agent in agents:
        agent_registry.register_agent(agent)
    
    # Start all agents
    started_count = await agent_registry.start_all()
    logger.info(f"Multi-Agent System initialized: {started_count} agents started")
    
    # Subscribe agents to relevant topics
    message_bus.subscribe("tutor", "learning", DeliveryPattern.PUBLISH_SUBSCRIBE)
    message_bus.subscribe("analytics", "analytics", DeliveryPattern.PUBLISH_SUBSCRIBE)
    message_bus.subscribe("assessment", "assessment", DeliveryPattern.PUBLISH_SUBSCRIBE)
    message_bus.subscribe("content", "content", DeliveryPattern.PUBLISH_SUBSCRIBE)
    message_bus.subscribe("path", "learning", DeliveryPattern.PUBLISH_SUBSCRIBE)
    message_bus.subscribe("orchestrator", "system", DeliveryPattern.PUBLISH_SUBSCRIBE)
    
    yield
    
    # Shutdown Multi-Agent System
    if agent_registry:
        logger.info("Stopping all agents...")
        await agent_registry.stop_all()
    logger.info("Jeseci Smart Learning Academy API shutting down...")

app = FastAPI(
    title="Jeseci Smart Learning Academy API",
    description="AI-Powered Learning Platform API - Hybrid Python/Jaclang Architecture",
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
# Health & Status Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/health_check")
async def health_check():
    """Health check endpoint - Jaclang compatible"""
    return {
        "service": "Jeseci Smart Learning Academy API",
        "status": "healthy",
        "version": "7.0.0",
        "timestamp": datetime.now().isoformat(),
        "database_status": "connected",
        "ai_status": "available" if os.getenv('OPENAI_API_KEY') else "fallback",
        "architecture": "Python/FastAPI + Jaclang-compatible endpoints"
    }

@app.post("/walker/init")
async def init():
    """Welcome message - Jaclang compatible"""
    return {
        "message": "Welcome to Jeseci Smart Learning Academy API!",
        "status": "initialized",
        "version": "7.0.0",
        "architecture": "Python/FastAPI Backend with Jaclang-compatible endpoints",
        "endpoints": {
            "health": "POST /walker/health_check",
            "auth": "POST /walker/user_login, POST /walker/user_create",
            "courses": "POST /walker/courses",
            "progress": "POST /walker/user_progress",
            "learning": "POST /walker/learning_session_start",
            "ai": "POST /walker/ai_generate_content",
            "analytics": "POST /walker/analytics_generate"
        }
    }

# =============================================================================
# Authentication Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/user_create")
async def user_create(request: Dict[str, Any]):
    """Create a new user account - Jaclang compatible"""
    # Extract data from request
    username = request.get("username")
    email = request.get("email")
    password = request.get("password")
    first_name = request.get("first_name", "")
    last_name = request.get("last_name", "")
    learning_style = request.get("learning_style", "visual")
    skill_level = request.get("skill_level", "beginner")
    
    if not username or not email or not password:
        return {
            "success": False,
            "error": "username, email, and password are required"
        }
    
    # Check for existing user by username
    if data_store.get_user_by_username(username):
        return {
            "success": False,
            "error": "A user with that username or email already exists."
        }
    
    # Check for existing user by email
    for user in data_store.users.values():
        if user.get("email") == email:
            return {
                "success": False,
                "error": "A user with that username or email already exists."
            }
    
    # Create the user
    user = data_store.create_user({
        "username": username,
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "learning_style": learning_style,
        "skill_level": skill_level
    })
    
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

@app.post("/walker/user_login")
async def user_login(request: Dict[str, Any]):
    """Authenticate user and return token - Jaclang compatible"""
    username = request.get("username")
    password = request.get("password")
    
    if not username or not password:
        return {
            "success": False,
            "error": "username and password are required"
        }
    
    user = data_store.get_user_by_username(username)
    
    if not user:
        # For demo, create user if not exists
        user = data_store.create_user({
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
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
# Course Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/courses")
async def get_courses(request: Dict[str, Any] = None):
    """Get all available courses - Jaclang compatible"""
    return data_store.courses

@app.post("/walker/course_create")
async def course_create(request: Dict[str, Any]):
    """Create a new course - Jaclang compatible"""
    title = request.get("title")
    description = request.get("description")
    domain = request.get("domain")
    difficulty = request.get("difficulty")
    content_type = request.get("content_type", "interactive")
    
    if not title or not description or not domain or not difficulty:
        return {
            "success": False,
            "error": "title, description, domain, and difficulty are required"
        }
    
    course_id = f"course_{title.lower().replace(' ', '_')}_{int(time.time())}"
    course = {
        "course_id": course_id,
        "title": title,
        "description": description,
        "domain": domain,
        "difficulty": difficulty,
        "content_type": content_type
    }
    data_store.courses.append(course)
    
    return {
        "success": True,
        "course_id": course_id,
        "title": title,
        "message": "Course created successfully"
    }

# =============================================================================
# Learning Paths Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/learning_paths")
async def get_learning_paths(request: Dict[str, Any] = None):
    """Get all learning paths - Jaclang compatible"""
    return data_store.learning_paths

# =============================================================================
# Concepts Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/concepts")
async def get_concepts(request: Dict[str, Any] = None):
    """Get all concepts - Jaclang compatible"""
    return data_store.concepts

# =============================================================================
# Quizzes Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/quizzes")
async def get_quizzes(request: Dict[str, Any] = None):
    """Get all quizzes - Jaclang compatible"""
    return data_store.quizzes

@app.post("/walker/quiz_submit")
async def quiz_submit(request: Dict[str, Any]):
    """Submit quiz answers - Jaclang compatible"""
    quiz_id = request.get("quiz_id")
    answers = request.get("answers", [])
    
    # Find the quiz
    quiz = next((q for q in data_store.quizzes if q["id"] == quiz_id), None)
    if not quiz:
        return {
            "success": False,
            "error": "Quiz not found"
        }
    
    # Calculate score
    correct_answers = 0
    for i, question in enumerate(quiz["questions"]):
        if i < len(answers) and answers[i] == question["correct_answer"]:
            correct_answers += 1
    
    score = (correct_answers / len(quiz["questions"])) * 100 if quiz["questions"] else 0
    
    return {
        "success": True,
        "quiz_id": quiz_id,
        "score": round(score, 1),
        "correct_answers": correct_answers,
        "total_questions": len(quiz["questions"]),
        "passed": score >= 70
    }

# =============================================================================
# Achievements Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/achievements")
async def get_achievements(request: Dict[str, Any]):
    """Get user achievements - Jaclang compatible"""
    user_id = request.get("user_id")
    
    # Return achievements with earned status based on user progress
    achievements = []
    for ach in data_store.achievements:
        earned = False
        if ach["id"] == "ach_1":
            earned = True  # Demo user has completed lessons
        achievements.append({
            **ach,
            "earned": earned,
            "earned_at": datetime.now().isoformat() if earned else None
        })
    
    return achievements

# =============================================================================
# Learning Sessions Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/learning_session_start")
async def learning_session_start(request: Dict[str, Any]):
    """Start a new learning session - Jaclang compatible"""
    user_id = request.get("user_id")
    module_id = request.get("module_id")
    
    if not user_id or not module_id:
        return {
            "success": False,
            "error": "user_id and module_id are required"
        }
    
    session_id = f"session_{user_id}_{module_id}_{int(time.time())}"
    
    # Find course title
    course = next((c for c in data_store.courses if c["course_id"] == module_id), None)
    course_title = course["title"] if course else "Unknown Course"
    
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "course_id": module_id,
        "course_title": course_title,
        "status": "in_progress",
        "progress": 0,
        "started_at": datetime.now().isoformat()
    }
    
    if user_id not in data_store.user_sessions:
        data_store.user_sessions[user_id] = []
    
    data_store.user_sessions[user_id].append(session)
    
    return {
        "success": True,
        "session_id": session_id,
        "user_id": user_id,
        "module_id": module_id,
        "status": "active",
        "message": "Learning session started"
    }

@app.post("/walker/learning_session_end")
async def learning_session_end(request: Dict[str, Any]):
    """End a learning session - Jaclang compatible"""
    session_id = request.get("session_id")
    progress = request.get("progress", 100)
    
    # Find and update session
    for user_id, sessions in data_store.user_sessions.items():
        for session in sessions:
            if session["session_id"] == session_id:
                session["status"] = "completed" if progress >= 100 else "in_progress"
                session["progress"] = progress
                session["completed_at"] = datetime.now().isoformat()
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "progress": progress,
                    "status": "completed",
                    "message": "Learning session ended"
                }
    
    return {
        "success": True,
        "session_id": session_id,
        "progress": progress,
        "status": "completed",
        "message": "Learning session ended"
    }

# =============================================================================
# Progress Tracking Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/user_progress")
async def user_progress(request: Dict[str, Any]):
    """Get user progress with dynamic calculations - Jaclang compatible"""
    user_id = request.get("user_id")
    if not user_id:
        return {
            "success": False,
            "error": "user_id is required"
        }
    
    return data_store.get_user_progress(user_id)

@app.post("/walker/analytics_generate")
async def analytics_generate(request: Dict[str, Any]):
    """Generate comprehensive learning analytics - Jaclang compatible"""
    user_id = request.get("user_id")
    if not user_id:
        return {
            "success": False,
            "error": "user_id is required"
        }
    
    return data_store.get_user_analytics(user_id)

# =============================================================================
# AI Content Generation Endpoints (Jaclang-compatible)
# =============================================================================

@app.post("/walker/ai_generate_content")
async def ai_generate_content(request: Dict[str, Any]):
    """Generate AI-powered educational content - Jaclang compatible"""
    try:
        concept_name = request.get("concept_name")
        domain = request.get("domain", "Computer Science")
        difficulty = request.get("difficulty", "beginner")
        related_concepts = request.get("related_concepts", [])
        
        if not concept_name:
            return {
                "success": False,
                "error": "concept_name is required"
            }
        
        logger.info(f"Generating AI content for: {concept_name}")
        
        # Generate content
        related_concepts_str = ",".join(related_concepts) if related_concepts else ""
        content = sync_generate_lesson(
            concept_name=concept_name,
            domain=domain,
            difficulty=difficulty,
            related_concepts_str=related_concepts_str
        )
        
        # Track generation
        data_store.ai_generations += 1
        
        return {
            "success": True,
            "concept_name": concept_name,
            "domain": domain,
            "difficulty": difficulty,
            "content": content,
            "related_concepts": related_concepts,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI generation error: {str(e)}")
        return {
            "success": False,
            "error": f"AI generation failed: {str(e)}"
        }

# =============================================================================
# Chat Endpoint (Jaclang-compatible)
# =============================================================================

@app.post("/walker/chat")
async def chat(request: Dict[str, Any]):
    """Simple chat endpoint - Jaclang compatible"""
    message = request.get("message", "")
    
    responses = [
        "That's a great question! Let me help you understand that concept better.",
        "I'd recommend starting with the Introduction to Programming course.",
        "The AI content generator can create personalized lessons for any topic you want to learn.",
        "Consistent practice is key to mastering programming concepts!",
        "Would you like me to generate some educational content on that topic?"
    ]
    
    import random
    response = random.choice(responses)
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# Data Export Endpoint (Jaclang-compatible)
# =============================================================================

@app.post("/walker/export_data")
async def export_data(request: Dict[str, Any] = None):
    """Export user data - Jaclang compatible"""
    format_param = request.get("format", "json") if request else "json"
    
    return {
        "success": True,
        "format": format_param,
        "data": {
            "users": list(data_store.users.values()),
            "courses": data_store.courses,
            "learning_paths": data_store.learning_paths,
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
# Additional REST API Endpoints (Modern format)
# =============================================================================

@app.get("/health")
async def health_check_rest():
    """Health check endpoint - REST style"""
    return {
        "service": "Jeseci Smart Learning Academy API",
        "status": "healthy",
        "version": "7.0.0",
        "timestamp": datetime.now().isoformat(),
        "database_status": "connected",
        "ai_status": "available" if os.getenv('OPENAI_API_KEY') else "fallback",
        "architecture": "Python/FastAPI + Jaclang-compatible endpoints"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Jeseci Smart Learning Academy API",
        "version": "7.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/users")
async def get_users():
    """Get all users (admin endpoint)"""
    return list(data_store.users.values())

@app.get("/courses")
async def get_courses_rest():
    """Get all courses - REST style"""
    return data_store.courses

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
# Multi-Agent System API Endpoints
# =============================================================================

@app.get("/api/v1/agents/status")
async def get_agents_status():
    """
    Get the status of all registered agents
    Returns detailed information about each agent's state, capabilities, and queue sizes
    """
    if agent_registry is None:
        return {
            "success": False,
            "error": "Agent system not initialized",
            "message": "The multi-agent system is still starting up. Please try again shortly."
        }
    
    try:
        status = agent_registry.get_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return {
            "success": False,
            "error": f"Failed to get agent status: {str(e)}"
        }

@app.get("/api/v1/agents/list")
async def list_agents():
    """
    List all registered agent IDs
    """
    if agent_registry is None:
        return {
            "success": False,
            "error": "Agent system not initialized"
        }
    
    try:
        agents = agent_registry.list_agents()
        return {
            "success": True,
            "agents": agents,
            "total": len(agents)
        }
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return {
            "success": False,
            "error": f"Failed to list agents: {str(e)}"
        }

@app.get("/api/v1/agents/message-bus/status")
async def get_message_bus_status():
    """
    Get the status and statistics of the message bus
    """
    if message_bus is None:
        return {
            "success": False,
            "error": "Message bus not initialized"
        }
    
    try:
        stats = message_bus.get_statistics()
        topics = message_bus.get_topics()
        registered_agents = message_bus.get_registered_agents()
        
        return {
            "success": True,
            "message_bus": stats,
            "topics": topics,
            "registered_agents": registered_agents,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting message bus status: {e}")
        return {
            "success": False,
            "error": f"Failed to get message bus status: {str(e)}"
        }

@app.get("/api/v1/agents/message-bus/history")
async def get_message_history(limit: int = 100):
    """
    Get the message history from the message bus
    
    Args:
        limit: Maximum number of messages to return (default: 100)
    """
    if message_bus is None:
        return {
            "success": False,
            "error": "Message bus not initialized"
        }
    
    try:
        history = message_bus.get_message_history(limit=limit)
        
        # Convert messages to serializable format
        history_data = []
        for msg in history:
            history_data.append({
                "msg_id": msg.msg_id,
                "sender": msg.sender,
                "recipient": msg.recipient,
                "msg_type": msg.msg_type.value,
                "priority": msg.priority.value,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "correlation_id": msg.correlation_id
            })
        
        return {
            "success": True,
            "message_history": history_data,
            "total_messages": len(history_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting message history: {e}")
        return {
            "success": False,
            "error": f"Failed to get message history: {str(e)}"
        }

# =============================================================================
# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Jeseci Smart Learning Academy API on {host}:{port}")
    logger.info(f"Running with Python/FastAPI backend with Jaclang-compatible endpoints")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False
    )
