"""
Quiz and Assessment Management System - Jeseci Smart Learning Academy
Advanced Quiz Builder, Assessment Administration, and Analytics

This module provides comprehensive quiz creation, management, and analytics
for educational assessments with automated grading and detailed reporting.

Author: Cavin Otieno
License: MIT License
"""

import os
import sys
from typing import Optional, Dict, Any, List, Union
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
import uuid
import json
import statistics
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import modules
import admin_auth
from admin_auth import AdminRole, ContentAdminUser, AnalyticsAdminUser, SuperAdminUser

# =============================================================================
# Quiz Management Models
# =============================================================================

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODING = "coding"
    MATCHING = "matching"

class QuizDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class QuizStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"

class GradingType(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"

class QuizQuestion(BaseModel):
    question_id: Optional[str] = Field(None, description="Unique question ID")
    question_type: QuestionType = Field(..., description="Type of question")
    question_text: str = Field(..., min_length=1, description="Question content")
    options: Optional[List[str]] = Field(None, description="Answer options for multiple choice")
    correct_answers: List[Union[str, int]] = Field(..., description="Correct answer(s)")
    points: float = Field(default=1.0, ge=0, description="Points for correct answer")
    explanation: Optional[str] = Field(None, description="Explanation for the answer")
    hints: Optional[List[str]] = Field(None, description="Hints for the question")
    tags: List[str] = Field(default=[], description="Question tags/categories")
    difficulty: QuizDifficulty = Field(default=QuizDifficulty.INTERMEDIATE)
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    
    @validator('options')
    def validate_options(cls, v, values):
        question_type = values.get('question_type')
        if question_type == QuestionType.MULTIPLE_CHOICE and (not v or len(v) < 2):
            raise ValueError('Multiple choice questions must have at least 2 options')
        return v

class QuizCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    concept_id: Optional[str] = Field(None, description="Associated concept ID")
    course_id: Optional[str] = Field(None, description="Associated course ID")
    difficulty: QuizDifficulty = Field(default=QuizDifficulty.INTERMEDIATE)
    time_limit: Optional[int] = Field(None, description="Total quiz time limit in minutes")
    passing_score: float = Field(default=70.0, ge=0, le=100, description="Passing score percentage")
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum attempts allowed")
    randomize_questions: bool = Field(default=False, description="Randomize question order")
    randomize_options: bool = Field(default=False, description="Randomize answer options")
    show_results: bool = Field(default=True, description="Show results after completion")
    show_correct_answers: bool = Field(default=True, description="Show correct answers")
    grading_type: GradingType = Field(default=GradingType.AUTOMATIC)
    questions: List[QuizQuestion] = Field(..., min_items=1, description="Quiz questions")
    tags: List[str] = Field(default=[], description="Quiz tags")
    prerequisites: List[str] = Field(default=[], description="Prerequisite quiz IDs")
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v:
            raise ValueError('Quiz must have at least one question')
        return v

class QuizUpdateRequest(BaseModel):
    quiz_id: str = Field(..., description="Quiz ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    difficulty: Optional[QuizDifficulty] = Field(None)
    time_limit: Optional[int] = Field(None)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[QuizStatus] = Field(None)
    questions: Optional[List[QuizQuestion]] = Field(None)
    tags: Optional[List[str]] = Field(None)

class QuestionBankCreateRequest(BaseModel):
    category: str = Field(..., min_length=1, description="Question category")
    domain: Optional[str] = Field(None, description="Subject domain (optional - will be auto-detected)")
    questions: List[QuizQuestion] = Field(..., min_items=1, description="Questions to add")
    tags: List[str] = Field(default=[], description="Category tags")

class QuizAttemptSubmission(BaseModel):
    quiz_id: str = Field(..., description="Quiz ID")
    user_id: str = Field(..., description="User ID taking the quiz")
    answers: Dict[str, Any] = Field(..., description="User answers by question ID")
    start_time: datetime = Field(..., description="Quiz start time")
    end_time: datetime = Field(..., description="Quiz end time")

class QuizAnalyticsRequest(BaseModel):
    quiz_id: Optional[str] = Field(None, description="Specific quiz ID")
    date_from: Optional[datetime] = Field(None, description="Start date for analytics")
    date_to: Optional[datetime] = Field(None, description="End date for analytics")
    user_group: Optional[str] = Field(None, description="User group filter")

# =============================================================================
# Response Models
# =============================================================================

class QuizResponse(BaseModel):
    success: bool
    quiz_id: Optional[str] = None
    message: str
    timestamp: str

class QuizListResponse(BaseModel):
    success: bool
    quizzes: List[Dict[str, Any]]
    total: int
    filters: Dict[str, Any]
    statistics: Dict[str, Any]

class QuizAnalyticsResponse(BaseModel):
    success: bool
    quiz_id: Optional[str] = None
    analytics: Dict[str, Any]
    period: str
    generated_at: str

class QuestionBankResponse(BaseModel):
    success: bool
    category: str
    questions_added: int
    message: str

# =============================================================================
# Quiz Management Database
# =============================================================================

class QuizManager:
    """Manages quiz creation, administration, and analytics"""

    # Domain mapping for dynamic domain detection based on concept keywords
    DOMAIN_KEYWORDS = {
        "jac": "Jac Programming",
        "node": "Jac Programming",
        "walker": "Jac Programming",
        "edge": "Jac Programming",
        "osp": "Jac Programming",
        "graph": "Jac Programming",
        "python": "Jac Programming",
        "programming": "Jac Programming",
        "algorithm": "Jac Programming",
        "software": "Jac Programming",
        "computer": "Jac Programming",
    }

    def __init__(self):
        self.quizzes_db = {}
        self.question_bank = {}
        self.quiz_attempts = {}
        self.quiz_analytics = {}
        self._init_sample_data()

    def get_domain_for_category(self, category: str, provided_domain: Optional[str] = None) -> str:
        """
        Dynamically determine the domain for a quiz category.
        If domain is provided, use it. Otherwise, detect from category name.
        Falls back to Jac Programming as default since this is a Jac-focused platform.
        """
        if provided_domain:
            return provided_domain

        # Normalize category name for matching
        category_lower = category.lower()

        # Check keyword mappings
        for keyword, domain in self.DOMAIN_KEYWORDS.items():
            if keyword in category_lower:
                return domain

        # Default to Jac Programming platform domain
        return "Jac Programming"

    def get_available_domains(self) -> List[str]:
        """Get list of available domains from the system"""
        return list(set(self.DOMAIN_KEYWORDS.values())) + ["Jac Programming"]

    def _init_sample_data(self):
        """Initialize with sample quizzes and question bank for Jac programming curriculum"""
        now = datetime.now()

        # Sample quiz questions for Jaclang concepts
        sample_questions = [
            QuizQuestion(
                question_id="q1_jac_nodes",
                question_type=QuestionType.MULTIPLE_CHOICE,
                question_text="What is the correct syntax to declare a node with a string attribute in Jac?",
                options=["node person has name: str;", "create person(name: str)", "person.name = str", "var person = new str()"],
                correct_answers=[0],
                points=1.0,
                explanation="In Jac, nodes are declared using the 'node' keyword with 'has' for attributes: node person has name: str;",
                tags=["jac", "nodes", "syntax"],
                difficulty=QuizDifficulty.BEGINNER
            ),
            QuizQuestion(
                question_id="q2_jac_walkers",
                question_type=QuestionType.TRUE_FALSE,
                question_text="Walkers in Jaclang are autonomous agents that traverse node graphs.",
                correct_answers=[True],
                points=1.0,
                explanation="Walkers are fundamental to Jac's Object-Spatial Programming model, serving as agents that navigate and perform actions on graph structures",
                tags=["jac", "walkers", "osp"],
                difficulty=QuizDifficulty.BEGINNER
            ),
            QuizQuestion(
                question_id="q3_jac_edges",
                question_type=QuestionType.MULTIPLE_CHOICE,
                question_text="Which keyword is used to define relationships between nodes in Jac?",
                options=["link", "connect", "edge", "relationship"],
                correct_answers=[2],
                points=1.0,
                explanation="The 'edge' keyword is used in Jac to define connections between nodes, establishing the graph structure that walkers traverse",
                tags=["jac", "edges", "graph"],
                difficulty=QuizDifficulty.INTERMEDIATE
            )
        ]

        # Sample quiz
        sample_quiz = {
            "quiz_id": "quiz_jac_fundamentals_001",
            "title": "Jaclang Fundamentals Quiz",
            "description": "Test your understanding of Jaclang basics including nodes, walkers, edges, and Object-Spatial Programming concepts",
            "concept_id": "concept_jac_fundamentals",
            "course_id": "course_jac_fundamentals",
            "difficulty": QuizDifficulty.BEGINNER,
            "time_limit": 30,
            "passing_score": 75.0,
            "max_attempts": 3,
            "randomize_questions": False,
            "randomize_options": True,
            "show_results": True,
            "show_correct_answers": True,
            "grading_type": GradingType.AUTOMATIC,
            "questions": [q.dict() for q in sample_questions],
            "tags": ["jaclang", "fundamentals", "beginner", "nodes", "walkers"],
            "prerequisites": [],
            "status": QuizStatus.PUBLISHED,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "created_by": "system",
            "total_points": 3.0,
            "question_count": 3
        }

        self.quizzes_db["quiz_jac_fundamentals_001"] = sample_quiz

        # Sample question bank
        self.question_bank = {
            "Jaclang Fundamentals": {
                "category": "Jaclang Fundamentals",
                "domain": "Jac Programming",
                "questions": [q.dict() for q in sample_questions],
                "tags": ["jaclang", "basics", "osp", "nodes", "walkers"],
                "created_at": now.isoformat(),
                "question_count": len(sample_questions)
            }
        }

        # Sample quiz attempts
        self.quiz_attempts = {
            "attempt_001": {
                "attempt_id": "attempt_001",
                "quiz_id": "quiz_jac_fundamentals_001",
                "user_id": "user_student_123",
                "answers": {"q1_jac_nodes": 0, "q2_jac_walkers": True, "q3_jac_edges": 2},
                "score": 100.0,
                "points_earned": 3.0,
                "total_points": 3.0,
                "passed": True,
                "start_time": (now - timedelta(hours=1)).isoformat(),
                "end_time": (now - timedelta(minutes=55)).isoformat(),
                "time_taken": 300,
                "attempt_number": 1,
                "graded_at": (now - timedelta(minutes=55)).isoformat()
            }
        }

        # Sample analytics - these would be calculated from quiz attempts in production
        self.quiz_analytics = {
            "quiz_jac_fundamentals_001": {
                "quiz_id": "quiz_jac_fundamentals_001",
                "total_attempts": 0,  # Dynamic: Count from quiz_attempts database
                "total_completions": 0,  # Dynamic: Count completed attempts
                "completion_rate": 0.0,  # Dynamic: Calculate from attempts
                "average_score": 0.0,  # Dynamic: Average of all attempt scores
                "pass_rate": 0.0,  # Dynamic: Calculate pass rate
                "average_time": 0,  # Dynamic: Average time spent
                "question_analytics": {},  # Dynamic: Aggregate per question
                "difficulty_distribution": {},  # Dynamic: Calculate from feedback
                "last_updated": now.isoformat()
            }
        }

    def calculate_quiz_analytics(self, quiz_id: str) -> Dict[str, Any]:
        """
        Calculate quiz analytics dynamically from actual quiz attempt data.
        In production, this would query the quiz attempts database.
        """
        if quiz_id not in self.quiz_analytics:
            return {
                "quiz_id": quiz_id,
                "total_attempts": 0,
                "total_completions": 0,
                "completion_rate": 0.0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "average_time": 0,
                "question_analytics": {},
                "difficulty_distribution": {},
                "last_updated": datetime.now().isoformat()
            }

        # Get attempts for this quiz
        attempts = [a for a in self.quiz_attempts.values() if a.get("quiz_id") == quiz_id]

        if not attempts:
            return self.quiz_analytics[quiz_id]

        # Calculate statistics from actual attempts
        completions = [a for a in attempts if a.get("passed", False)]
        scores = [a.get("score", 0) for a in completions]
        times = [a.get("time_taken", 0) for a in attempts]

        total_attempts = len(attempts)
        total_completions = len(completions)
        completion_rate = (total_completions / total_attempts * 100) if total_attempts > 0 else 0.0
        average_score = sum(scores) / len(scores) if scores else 0.0
        pass_rate = (total_completions / total_attempts * 100) if total_attempts > 0 else 0.0
        average_time = sum(times) / len(times) if times else 0

        return {
            "quiz_id": quiz_id,
            "total_attempts": total_attempts,
            "total_completions": total_completions,
            "completion_rate": round(completion_rate, 1),
            "average_score": round(average_score, 1),
            "pass_rate": round(pass_rate, 1),
            "average_time": int(average_time),
            "question_analytics": self.quiz_analytics[quiz_id].get("question_analytics", {}),
            "difficulty_distribution": self.quiz_analytics[quiz_id].get("difficulty_distribution", {}),
            "last_updated": datetime.now().isoformat()
        }

    def refresh_quiz_analytics(self, quiz_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Refresh quiz analytics by recalculating from actual data.
        If quiz_id is None, refresh all quiz analytics.
        """
        if quiz_id:
            if quiz_id in self.quiz_analytics:
                self.quiz_analytics[quiz_id] = self.calculate_quiz_analytics(quiz_id)
            return {"success": True, "quiz_id": quiz_id}
        else:
            # Refresh all quizzes
            for qid in self.quiz_analytics:
                self.quiz_analytics[qid] = self.calculate_quiz_analytics(qid)
            return {"success": True, "refreshed_all": True}
    
    def create_quiz(self, quiz_data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quiz"""
        quiz_id = f"quiz_{quiz_data['title'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Calculate total points
        total_points = sum(q['points'] for q in quiz_data['questions'])
        
        # Assign question IDs if not provided
        for i, question in enumerate(quiz_data['questions']):
            if not question.get('question_id'):
                question['question_id'] = f"{quiz_id}_q{i+1}"
        
        quiz = {
            "quiz_id": quiz_id,
            **quiz_data,
            "status": QuizStatus.DRAFT,
            "total_points": total_points,
            "question_count": len(quiz_data['questions']),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": admin_user.get("user_id"),
            "created_by_username": admin_user.get("username")
        }
        
        self.quizzes_db[quiz_id] = quiz
        
        return {
            "success": True,
            "quiz_id": quiz_id,
            "message": "Quiz created successfully"
        }
    
    def update_quiz(self, quiz_id: str, updates: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing quiz"""
        if quiz_id not in self.quizzes_db:
            return {
                "success": False,
                "error": "Quiz not found",
                "code": "NOT_FOUND"
            }
        
        quiz = self.quizzes_db[quiz_id]
        
        # Update fields
        for field, value in updates.items():
            if value is not None and field != "quiz_id":
                quiz[field] = value
        
        # Recalculate total points if questions were updated
        if 'questions' in updates and updates['questions']:
            quiz['total_points'] = sum(q['points'] for q in updates['questions'])
            quiz['question_count'] = len(updates['questions'])
        
        quiz["updated_at"] = datetime.now().isoformat()
        quiz["last_updated_by"] = admin_user.get("user_id")
        
        return {
            "success": True,
            "quiz_id": quiz_id,
            "message": "Quiz updated successfully"
        }
    
    def get_quizzes(self, limit: int = 50, offset: int = 0, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get quizzes with filtering"""
        quizzes = list(self.quizzes_db.values())
        
        # Apply filters
        if filters:
            if filters.get("status"):
                quizzes = [q for q in quizzes if q.get("status") == filters["status"]]
            if filters.get("difficulty"):
                quizzes = [q for q in quizzes if q.get("difficulty") == filters["difficulty"]]
            if filters.get("concept_id"):
                quizzes = [q for q in quizzes if q.get("concept_id") == filters["concept_id"]]
            if filters.get("course_id"):
                quizzes = [q for q in quizzes if q.get("course_id") == filters["course_id"]]
            if filters.get("search"):
                search_term = filters["search"].lower()
                quizzes = [
                    q for q in quizzes 
                    if search_term in q.get("title", "").lower() or 
                       search_term in q.get("description", "").lower()
                ]
        
        # Sort by creation date (newest first)
        quizzes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Statistics
        total = len(quizzes)
        status_counts = {}
        difficulty_counts = {}
        
        for quiz in quizzes:
            status = quiz.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            difficulty = quiz.get("difficulty", "unknown")
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        # Apply pagination
        paginated_quizzes = quizzes[offset:offset + limit]
        
        return {
            "success": True,
            "quizzes": paginated_quizzes,
            "total": total,
            "statistics": {
                "status_distribution": status_counts,
                "difficulty_distribution": difficulty_counts,
                "average_questions": statistics.mean([q.get("question_count", 0) for q in quizzes]) if quizzes else 0,
                "total_points_available": sum(q.get("total_points", 0) for q in quizzes)
            }
        }
    
    def add_to_question_bank(self, bank_data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Add questions to the question bank"""
        category = bank_data["category"]
        
        # Assign question IDs
        for i, question in enumerate(bank_data["questions"]):
            if not question.get("question_id"):
                question["question_id"] = f"bank_{category.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        if category in self.question_bank:
            # Add to existing category
            existing = self.question_bank[category]
            existing["questions"].extend(bank_data["questions"])
            existing["question_count"] = len(existing["questions"])
            existing["updated_at"] = datetime.now().isoformat()
        else:
            # Create new category
            self.question_bank[category] = {
                "category": category,
                "domain": bank_data.get("domain", "Computer Science"),
                "questions": bank_data["questions"],
                "tags": bank_data.get("tags", []),
                "created_at": datetime.now().isoformat(),
                "created_by": admin_user.get("user_id"),
                "question_count": len(bank_data["questions"])
            }
        
        return {
            "success": True,
            "category": category,
            "questions_added": len(bank_data["questions"]),
            "message": f"Added {len(bank_data['questions'])} questions to {category}"
        }
    
    def get_quiz_analytics(self, quiz_id: str = None, date_range: tuple = None) -> Dict[str, Any]:
        """Get comprehensive quiz analytics"""
        if quiz_id:
            # Analytics for specific quiz
            if quiz_id not in self.quiz_analytics:
                return {
                    "success": False,
                    "error": "Analytics not found for this quiz"
                }
            
            analytics = self.quiz_analytics[quiz_id].copy()
            
            # Add detailed insights
            analytics["insights"] = {
                "performance_level": "good" if analytics["average_score"] >= 75 else "needs_improvement",
                "difficulty_assessment": self._assess_quiz_difficulty(analytics),
                "question_improvements": self._suggest_question_improvements(analytics),
                "completion_trend": "stable"  # Would calculate from historical data
            }
            
            return {
                "success": True,
                "quiz_id": quiz_id,
                "analytics": analytics
            }
        else:
            # Overall analytics across all quizzes
            all_analytics = list(self.quiz_analytics.values())
            
            if not all_analytics:
                return {
                    "success": True,
                    "analytics": {
                        "total_quizzes": 0,
                        "total_attempts": 0,
                        "overall_metrics": {}
                    }
                }
            
            overall_analytics = {
                "total_quizzes": len(self.quizzes_db),
                "total_attempts": sum(a["total_attempts"] for a in all_analytics),
                "average_completion_rate": statistics.mean([a["completion_rate"] for a in all_analytics]),
                "average_score": statistics.mean([a["average_score"] for a in all_analytics]),
                "average_pass_rate": statistics.mean([a["pass_rate"] for a in all_analytics]),
                "quiz_performance_distribution": {
                    "high_performing": len([a for a in all_analytics if a["average_score"] >= 85]),
                    "medium_performing": len([a for a in all_analytics if 70 <= a["average_score"] < 85]),
                    "low_performing": len([a for a in all_analytics if a["average_score"] < 70])
                },
                "popular_quizzes": sorted(all_analytics, key=lambda x: x["total_attempts"], reverse=True)[:5]
            }
            
            return {
                "success": True,
                "analytics": overall_analytics
            }
    
    def _assess_quiz_difficulty(self, analytics: Dict[str, Any]) -> str:
        """Assess quiz difficulty based on analytics"""
        avg_score = analytics["average_score"]
        completion_rate = analytics["completion_rate"]
        
        if avg_score >= 85 and completion_rate >= 90:
            return "too_easy"
        elif avg_score <= 60 or completion_rate <= 70:
            return "too_hard"
        else:
            return "appropriate"
    
    def _suggest_question_improvements(self, analytics: Dict[str, Any]) -> List[str]:
        """Suggest improvements based on question analytics"""
        suggestions = []
        
        question_analytics = analytics.get("question_analytics", {})
        for q_id, q_data in question_analytics.items():
            if q_data["correct_rate"] < 50:
                suggestions.append(f"Question {q_id}: Very low success rate ({q_data['correct_rate']}%) - consider rewording or providing hints")
            elif q_data["correct_rate"] > 95:
                suggestions.append(f"Question {q_id}: Very high success rate ({q_data['correct_rate']}%) - consider increasing difficulty")
            
            if q_data["average_time"] > 120:  # More than 2 minutes
                suggestions.append(f"Question {q_id}: Taking too long to answer - consider simplifying")
        
        return suggestions

# Global quiz manager instance
quiz_manager = QuizManager()

# =============================================================================
# Quiz Management Router
# =============================================================================

def create_quiz_admin_router() -> APIRouter:
    """Create quiz and assessment management router"""
    
    router = APIRouter()

    # =============================================================================
    # Quiz Management Endpoints
    # =============================================================================

    @router.get("/admin/quizzes", response_model=QuizListResponse)
    async def get_quizzes_admin(
        limit: int = Query(default=50, le=100, description="Maximum quizzes to return"),
        offset: int = Query(default=0, ge=0, description="Number of quizzes to skip"),
        status: Optional[QuizStatus] = Query(default=None, description="Filter by status"),
        difficulty: Optional[QuizDifficulty] = Query(default=None, description="Filter by difficulty"),
        concept_id: Optional[str] = Query(default=None, description="Filter by concept"),
        course_id: Optional[str] = Query(default=None, description="Filter by course"),
        search: Optional[str] = Query(default=None, description="Search title/description"),
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Get all quizzes with filtering (Content Admin+)"""
        try:
            filters = {
                "status": status,
                "difficulty": difficulty,
                "concept_id": concept_id,
                "course_id": course_id,
                "search": search
            }
            
            result = quiz_manager.get_quizzes(limit, offset, filters)
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "quizzes_list_accessed",
                details={
                    "filters": {k: v for k, v in filters.items() if v is not None},
                    "results_count": len(result["quizzes"])
                }
            )
            
            return QuizListResponse(
                success=True,
                quizzes=result["quizzes"],
                total=result["total"],
                filters=filters,
                statistics=result["statistics"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve quizzes",
                    "message": str(e)
                }
            )

    @router.post("/admin/quizzes", response_model=QuizResponse)
    async def create_quiz_admin(
        request: QuizCreateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Create a new quiz (Content Admin+)"""
        try:
            quiz_data = request.dict()
            result = quiz_manager.create_quiz(quiz_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Quiz creation failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "quiz_created",
                target=result["quiz_id"],
                details={
                    "title": request.title,
                    "difficulty": request.difficulty,
                    "question_count": len(request.questions),
                    "total_points": sum(q.points for q in request.questions)
                }
            )
            
            return QuizResponse(
                success=True,
                quiz_id=result["quiz_id"],
                message="Quiz created successfully",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create quiz",
                    "message": str(e)
                }
            )

    @router.put("/admin/quizzes", response_model=QuizResponse)
    async def update_quiz_admin(
        request: QuizUpdateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Update an existing quiz (Content Admin+)"""
        try:
            updates = {k: v for k, v in request.dict().items() if v is not None and k != "quiz_id"}
            result = quiz_manager.update_quiz(request.quiz_id, updates, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=404 if result.get("code") == "NOT_FOUND" else 400,
                    detail={
                        "error": "Quiz update failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "quiz_updated",
                target=request.quiz_id,
                details={"updates": list(updates.keys())}
            )
            
            return QuizResponse(
                success=True,
                quiz_id=request.quiz_id,
                message="Quiz updated successfully",
                timestamp=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to update quiz",
                    "message": str(e)
                }
            )

    # =============================================================================
    # Question Bank Management
    # =============================================================================

    @router.post("/admin/question-bank", response_model=QuestionBankResponse)
    async def add_to_question_bank_admin(
        request: QuestionBankCreateRequest,
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Add questions to the question bank (Content Admin+)"""
        try:
            bank_data = request.dict()
            result = quiz_manager.add_to_question_bank(bank_data, admin_user)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Question bank update failed",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "question_bank_updated",
                target=request.category,
                details={
                    "questions_added": result["questions_added"],
                    "domain": request.domain
                }
            )
            
            return QuestionBankResponse(
                success=True,
                category=result["category"],
                questions_added=result["questions_added"],
                message=result["message"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to update question bank",
                    "message": str(e)
                }
            )

    @router.get("/admin/question-bank")
    async def get_question_bank_admin(
        category: Optional[str] = Query(default=None, description="Specific category"),
        admin_user: Dict[str, Any] = ContentAdminUser
    ):
        """Get question bank categories and questions (Content Admin+)"""
        try:
            if category:
                if category not in quiz_manager.question_bank:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": "Category not found"}
                    )
                
                result = quiz_manager.question_bank[category]
            else:
                result = {
                    "categories": list(quiz_manager.question_bank.keys()),
                    "question_bank": quiz_manager.question_bank,
                    "total_questions": sum(
                        cat["question_count"] for cat in quiz_manager.question_bank.values()
                    )
                }
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "question_bank_accessed",
                details={"category": category or "all"}
            )
            
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve question bank",
                    "message": str(e)
                }
            )

    # =============================================================================
    # Quiz Analytics
    # =============================================================================

    @router.get("/admin/quiz-analytics", response_model=QuizAnalyticsResponse)
    async def get_quiz_analytics_admin(
        quiz_id: Optional[str] = Query(default=None, description="Specific quiz ID"),
        period: str = Query(default="all", description="Analytics period"),
        admin_user: Dict[str, Any] = AnalyticsAdminUser
    ):
        """Get comprehensive quiz analytics (Analytics Admin+)"""
        try:
            result = quiz_manager.get_quiz_analytics(quiz_id)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Analytics not available",
                        "message": result.get("error")
                    }
                )
            
            # Log admin action
            admin_auth.log_admin_action(
                admin_user, "quiz_analytics_accessed",
                target=quiz_id or "all_quizzes",
                details={"period": period}
            )
            
            return QuizAnalyticsResponse(
                success=True,
                quiz_id=quiz_id,
                analytics=result["analytics"],
                period=period,
                generated_at=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve quiz analytics",
                    "message": str(e)
                }
            )

    return quiz_app

# =============================================================================
# Export quiz router
# =============================================================================

quiz_admin_router = create_quiz_admin_router()