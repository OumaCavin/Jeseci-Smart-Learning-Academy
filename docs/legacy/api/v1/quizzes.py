"""
Quizzes API endpoints
Quiz management and assessment
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

from api.v1.auth import get_current_user
from config.database import get_db
from config.logging_config import get_logger
from database.models import User, Quiz, QuizAttempt, UserConceptProgress

# Get logger for this module
logger = get_logger(__name__)


# Router instance
router = APIRouter()


# Pydantic Models
class QuizStartRequest(BaseModel):
    """Request to start a quiz"""
    time_limit_override: Optional[int] = None


class QuizResponse(BaseModel):
    """Quiz submission response"""
    responses: Dict[str, Any]
    time_taken: int
    user_notes: Optional[str] = None


class QuizSubmission(BaseModel):
    """Quiz submission data"""
    quiz_id: str
    responses: Dict[str, Any]
    time_taken: int
    user_notes: Optional[str] = None


class QuizAttemptResponse(BaseModel):
    """Quiz attempt response data"""
    attempt_id: str
    quiz_title: str
    attempt_number: int
    status: str
    score: float
    max_score: float
    percentage: float
    passed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    time_taken: int
    feedback: Optional[Dict[str, Any]] = None


class QuizAnalytics(BaseModel):
    """Quiz analytics data"""
    total_attempts: int
    average_score: float
    best_score: float
    pass_rate: float
    completion_rate: float
    average_time: float
    difficulty_distribution: Dict[str, int]


@router.get("/")
async def get_quizzes(
    concept_id: Optional[str] = None,
    quiz_type: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available quizzes for user"""
    
    try:
        logger.info(f"📚 Fetching quizzes for user: {current_user.user_id}")
        
        # Build query with filters
        query = db.query(Quiz)
        
        if concept_id:
            query = query.filter(Quiz.concept_id == concept_id)
        
        if quiz_type:
            query = query.filter(Quiz.quiz_type == quiz_type)
        
        if difficulty_level:
            query = query.filter(Quiz.difficulty_level == difficulty_level)
        
        quizzes = query.order_by(Quiz.created_at.desc()).all()
        
        # Get user's progress for each concept to add completion status
        result = []
        for quiz in quizzes:
            # Get user's best attempt for this quiz
            best_attempt = db.query(QuizAttempt).filter(
                and_(
                    QuizAttempt.quiz_id == quiz.quiz_id,
                    QuizAttempt.user_id == current_user.user_id,
                    QuizAttempt.status == 'completed'
                )
            ).order_by(desc(QuizAttempt.percentage)).first()
            
            quiz_data = {
                "quiz_id": quiz.quiz_id,
                "title": quiz.title,
                "description": quiz.description,
                "concept_id": quiz.concept_id,
                "quiz_type": quiz.quiz_type,
                "difficulty_level": quiz.difficulty_level,
                "time_limit": quiz.time_limit,
                "max_attempts": quiz.max_attempts,
                "passing_score": quiz.passing_score,
                "question_count": len(quiz.questions) if quiz.questions else 0,
                "total_attempts": quiz.total_attempts,
                "average_score": quiz.average_score,
                "completion_rate": quiz.completion_rate,
                "created_at": quiz.created_at,
                "user_best_score": best_attempt.percentage if best_attempt else 0.0,
                "user_passed": best_attempt.passed if best_attempt else False,
                "attempts_used": db.query(func.count(QuizAttempt.attempt_id)).filter(
                    and_(
                        QuizAttempt.quiz_id == quiz.quiz_id,
                        QuizAttempt.user_id == current_user.user_id
                    )
                ).scalar() or 0
            }
            result.append(quiz_data)
        
        logger.info(f"✅ Found {len(result)} quizzes")
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"❌ Error fetching quizzes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quizzes: {str(e)}")


@router.get("/{quiz_id}")
async def get_quiz_details(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed quiz information"""
    
    try:
        logger.info(f"📋 Fetching quiz details: {quiz_id}")
        
        quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Get user's attempt history for this quiz
        attempts = db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.user_id == current_user.user_id
            )
        ).order_by(desc(QuizAttempt.attempt_number)).all()
        
        # Calculate user statistics
        completed_attempts = [a for a in attempts if a.status == 'completed']
        best_score = max([a.percentage for a in completed_attempts]) if completed_attempts else 0.0
        attempts_used = len(attempts)
        
        quiz_data = {
            "quiz_id": quiz.quiz_id,
            "title": quiz.title,
            "description": quiz.description,
            "concept_id": quiz.concept_id,
            "quiz_type": quiz.quiz_type,
            "difficulty_level": quiz.difficulty_level,
            "questions": quiz.questions,
            "time_limit": quiz.time_limit,
            "max_attempts": quiz.max_attempts,
            "passing_score": quiz.passing_score,
            "randomize_questions": quiz.randomize_questions,
            "show_correct_answers": quiz.show_correct_answers,
            "allow_review": quiz.allow_review,
            "created_at": quiz.created_at,
            "user_statistics": {
                "attempts_used": attempts_used,
                "best_score": best_score,
                "can_attempt": attempts_used < quiz.max_attempts,
                "recent_attempts": [
                    {
                        "attempt_number": a.attempt_number,
                        "percentage": a.percentage,
                        "passed": a.passed,
                        "completed_at": a.completed_at,
                        "time_taken": a.time_taken
                    }
                    for a in attempts[:3]  # Last 3 attempts
                ]
            }
        }
        
        logger.info(f"✅ Quiz details retrieved successfully")
        return {"success": True, "data": quiz_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching quiz details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz details: {str(e)}")


@router.post("/{quiz_id}/start")
async def start_quiz(
    quiz_id: str,
    request: QuizStartRequest = QuizStartRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new quiz attempt"""
    
    try:
        logger.info(f"🚀 Starting quiz: {quiz_id} for user: {current_user.user_id}")
        
        # Get quiz
        quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Check attempt limits
        attempts_used = db.query(func.count(QuizAttempt.attempt_id)).filter(
            and_(
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.user_id == current_user.user_id
            )
        ).scalar() or 0
        
        if attempts_used >= quiz.max_attempts:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum attempts ({quiz.max_attempts}) reached for this quiz"
            )
        
        # Create new attempt
        attempt_number = attempts_used + 1
        
        new_attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=current_user.user_id,
            attempt_number=attempt_number,
            status="in_progress",
            time_taken=0
        )
        
        db.add(new_attempt)
        db.commit()
        db.refresh(new_attempt)
        
        # Update quiz statistics
        quiz.total_attempts += 1
        db.commit()
        
        logger.info(f"✅ Quiz attempt created: {new_attempt.attempt_id}")
        
        return {
            "success": True,
            "data": {
                "attempt_id": new_attempt.attempt_id,
                "quiz_title": quiz.title,
                "attempt_number": attempt_number,
                "time_limit": request.time_limit_override or quiz.time_limit,
                "questions": quiz.questions if not quiz.randomize_questions else quiz.questions[:],
                "started_at": new_attempt.started_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error starting quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start quiz: {str(e)}")


@router.post("/attempts/{attempt_id}/submit")
async def submit_quiz_attempt(
    attempt_id: str,
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quiz attempt with responses and calculate score"""
    
    try:
        logger.info(f"📝 Submitting quiz attempt: {attempt_id}")
        
        # Get attempt
        attempt = db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.attempt_id == attempt_id,
                QuizAttempt.user_id == current_user.user_id
            )
        ).first()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="Quiz attempt not found")
        
        if attempt.status == 'completed':
            raise HTTPException(status_code=400, detail="Quiz attempt already submitted")
        
        # Get quiz for scoring
        quiz = db.query(Quiz).filter(Quiz.quiz_id == attempt.quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Associated quiz not found")
        
        # Calculate score
        score, max_score, percentage, passed = calculate_quiz_score(
            submission.responses, quiz.questions, quiz.passing_score
        )
        
        # Update attempt
        attempt.status = 'completed'
        attempt.responses = submission.responses
        attempt.time_taken = submission.time_taken
        attempt.score = score
        attempt.max_score = max_score
        attempt.percentage = percentage
        attempt.passed = passed
        attempt.completed_at = datetime.utcnow()
        
        # Update quiz statistics
        update_quiz_statistics(quiz, db)
        
        db.commit()
        
        # Award achievements if passed
        if passed:
            await award_quiz_achievements(current_user.user_id, quiz, db)
        
        logger.info(f"✅ Quiz attempt submitted: {attempt_id}, Score: {percentage:.1%}")
        
        return {
            "success": True,
            "data": {
                "attempt_id": attempt.attempt_id,
                "score": score,
                "max_score": max_score,
                "percentage": percentage,
                "passed": passed,
                "time_taken": submission.time_taken,
                "completed_at": attempt.completed_at,
                "feedback": generate_quiz_feedback(quiz, submission.responses, percentage)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error submitting quiz attempt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit quiz attempt: {str(e)}")


@router.get("/attempts/{attempt_id}")
async def get_quiz_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz attempt details"""
    
    try:
        attempt = db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.attempt_id == attempt_id,
                QuizAttempt.user_id == current_user.user_id
            )
        ).first()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="Quiz attempt not found")
        
        quiz = db.query(Quiz).filter(Quiz.quiz_id == attempt.quiz_id).first()
        
        attempt_data = {
            "attempt_id": attempt.attempt_id,
            "quiz_title": quiz.title if quiz else "Unknown Quiz",
            "attempt_number": attempt.attempt_number,
            "status": attempt.status,
            "score": attempt.score,
            "max_score": attempt.max_score,
            "percentage": attempt.percentage,
            "passed": attempt.passed,
            "started_at": attempt.started_at,
            "completed_at": attempt.completed_at,
            "time_taken": attempt.time_taken,
            "responses": attempt.responses,
            "feedback": attempt.feedback,
            "user_notes": attempt.responses.get('user_notes') if attempt.responses else None
        }
        
        return {"success": True, "data": attempt_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching quiz attempt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz attempt: {str(e)}")


@router.get("/attempts/user/{user_id}")
async def get_user_quiz_attempts(
    user_id: str,
    quiz_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's quiz attempts"""
    
    try:
        # Check if user can access these attempts
        if user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
        
        if quiz_id:
            query = query.filter(QuizAttempt.quiz_id == quiz_id)
        
        if status_filter:
            query = query.filter(QuizAttempt.status == status_filter)
        
        attempts = query.order_by(desc(QuizAttempt.started_at)).limit(limit).all()
        
        # Get quiz titles
        quiz_ids = [a.quiz_id for a in attempts]
        quizzes = db.query(Quiz).filter(Quiz.quiz_id.in_(quiz_ids)).all()
        quiz_map = {q.quiz_id: q.title for q in quizzes}
        
        result = []
        for attempt in attempts:
            result.append({
                "attempt_id": attempt.attempt_id,
                "quiz_title": quiz_map.get(attempt.quiz_id, "Unknown Quiz"),
                "attempt_number": attempt.attempt_number,
                "status": attempt.status,
                "score": attempt.score,
                "max_score": attempt.max_score,
                "percentage": attempt.percentage,
                "passed": attempt.passed,
                "started_at": attempt.started_at,
                "completed_at": attempt.completed_at,
                "time_taken": attempt.time_taken
            })
        
        return {"success": True, "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching user quiz attempts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz attempts: {str(e)}")


@router.get("/analytics/{quiz_id}")
async def get_quiz_analytics(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz analytics and statistics"""
    
    try:
        quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
        completed_attempts = [a for a in attempts if a.status == 'completed']
        
        if not completed_attempts:
            return {"success": True, "data": {"message": "No completed attempts yet"}}
        
        # Calculate statistics
        total_attempts = len(completed_attempts)
        scores = [a.percentage for a in completed_attempts]
        times = [a.time_taken for a in completed_attempts if a.time_taken]
        
        analytics = {
            "total_attempts": total_attempts,
            "average_score": sum(scores) / len(scores),
            "best_score": max(scores),
            "pass_rate": sum(1 for s in scores if s >= quiz.passing_score) / len(scores),
            "completion_rate": len(completed_attempts) / len(attempts) if attempts else 0,
            "average_time": sum(times) / len(times) if times else 0,
            "difficulty_distribution": {
                "easy": sum(1 for a in completed_attempts if a.difficulty_rating and a.difficulty_rating <= 3),
                "medium": sum(1 for a in completed_attempts if a.difficulty_rating and 3 < a.difficulty_rating <= 7),
                "hard": sum(1 for a in completed_attempts if a.difficulty_rating and a.difficulty_rating > 7)
            }
        }
        
        return {"success": True, "data": analytics}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching quiz analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz analytics: {str(e)}")


# Helper Functions
def calculate_quiz_score(responses: Dict[str, Any], questions: List[Dict], passing_score: float):
    """Calculate quiz score based on responses and correct answers"""
    
    if not questions or not responses:
        return 0.0, 1.0, 0.0, False
    
    score = 0.0
    max_score = len(questions)
    
    for question in questions:
        question_id = question.get('id')
        correct_answer = question.get('correct_answer')
        user_answer = responses.get(question_id)
        
        if user_answer == correct_answer:
            score += 1.0
    
    percentage = score / max_score if max_score > 0 else 0.0
    passed = percentage >= passing_score
    
    return score, max_score, percentage, passed


def update_quiz_statistics(quiz: Quiz, db: Session):
    """Update quiz aggregate statistics"""
    
    attempts = db.query(QuizAttempt).filter(
        and_(
            QuizAttempt.quiz_id == quiz.quiz_id,
            QuizAttempt.status == 'completed'
        )
    ).all()
    
    if attempts:
        quiz.average_score = sum(a.percentage for a in attempts) / len(attempts)
        quiz.completion_rate = sum(1 for a in attempts if a.passed) / len(attempts)


async def award_quiz_achievements(user_id: str, quiz: Quiz, db: Session):
    """Award achievements based on quiz performance"""
    
    try:
        # Import here to avoid circular import
        from database.models import UserAchievement
        
        # Get user's attempts for this quiz
        attempts = db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.quiz_id == quiz.quiz_id,
                QuizAttempt.user_id == user_id,
                QuizAttempt.status == 'completed'
            )
        ).all()
        
        if not attempts:
            return
        
        # Achievement: First Quiz Completion
        first_quiz = db.query(UserAchievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_type == 'first_quiz_completion'
            )
        ).first()
        
        if not first_quiz:
            achievement = UserAchievement(
                user_id=user_id,
                achievement_type='first_quiz_completion',
                achievement_name='First Steps',
                description='Completed your first quiz!',
                badge_icon='🎯',
                category='milestone',
                value=1.0,
                target_value=1.0,
                percentage=100.0
            )
            db.add(achievement)
        
        # Achievement: Perfect Score
        if any(a.percentage == 1.0 for a in attempts):
            perfect_score = db.query(UserAchievement).filter(
                and_(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_type == 'perfect_score'
                )
            ).first()
            
            if not perfect_score:
                achievement = UserAchievement(
                    user_id=user_id,
                    achievement_type='perfect_score',
                    achievement_name='Perfectionist',
                    description='Achieved a perfect score on a quiz',
                    badge_icon='🏆',
                    category='excellence',
                    value=1.0,
                    target_value=1.0,
                    percentage=100.0
                )
                db.add(achievement)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Error awarding quiz achievements: {str(e)}")


def generate_quiz_feedback(quiz: Quiz, responses: Dict[str, Any], percentage: float) -> Dict[str, Any]:
    """Generate personalized feedback for quiz attempt"""
    
    feedback = {
        "overall": "",
        "strengths": [],
        "improvements": [],
        "suggestions": []
    }
    
    # Overall feedback
    if percentage >= 0.9:
        feedback["overall"] = "Excellent work! You have mastered this concept."
    elif percentage >= 0.8:
        feedback["overall"] = "Great job! You have a solid understanding of the material."
    elif percentage >= 0.7:
        feedback["overall"] = "Good effort! Review the areas where you had difficulty."
    else:
        feedback["overall"] = "Keep studying! Consider reviewing the concept materials."
    
    # Generate specific feedback based on questions
    if quiz.questions and responses:
        for question in quiz.questions:
            question_id = question.get('id')
            is_correct = responses.get(question_id) == question.get('correct_answer')
            
            if not is_correct:
                feedback["improvements"].append(f"Review: {question.get('topic', 'this topic')}")
            else:
                feedback["strengths"].append(f"Strong understanding of: {question.get('topic', 'this topic')}")
    
    # Suggestions
    if percentage < 0.8:
        feedback["suggestions"].append("Review the concept materials before attempting again")
        feedback["suggestions"].append("Consider using the learning path for this topic")
    
    return feedback