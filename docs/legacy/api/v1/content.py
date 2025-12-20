"""
Concept Content API endpoints
Educational content management - lessons, exercises, reading materials
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel

from api.v1.auth import get_current_user
from config.database import get_db
from database.models import Concept, ConceptContent, UserContentProgress, User


# Pydantic models for content management
class ConceptContentCreate(BaseModel):
    concept_id: str
    title: str
    content_type: str  # lesson, exercise, reading, quiz, video, interactive
    content: str
    summary: Optional[str] = None
    learning_objectives: Optional[List[str]] = []
    multimedia_resources: Optional[List[dict]] = []
    external_links: Optional[List[dict]] = []
    code_examples: Optional[List[dict]] = []
    interactive_elements: Optional[List[dict]] = []
    difficulty_level: str
    estimated_duration: Optional[int] = 30
    prerequisites: Optional[List[str]] = []
    practice_questions: Optional[List[dict]] = []
    examples: Optional[List[dict]] = []
    exercises: Optional[List[dict]] = []
    author: Optional[str] = None


class ConceptContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    multimedia_resources: Optional[List[dict]] = None
    external_links: Optional[List[dict]] = None
    code_examples: Optional[List[dict]] = None
    interactive_elements: Optional[List[dict]] = None
    difficulty_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    practice_questions: Optional[List[dict]] = None
    examples: Optional[List[dict]] = None
    exercises: Optional[List[dict]] = None
    is_active: Optional[bool] = None
    version: Optional[str] = None


class ConceptContentResponse(BaseModel):
    content_id: str
    concept_id: str
    title: str
    content_type: str
    order_index: int
    content: str
    summary: Optional[str]
    learning_objectives: List[str]
    multimedia_resources: List[dict]
    external_links: List[dict]
    code_examples: List[dict]
    interactive_elements: List[dict]
    difficulty_level: str
    estimated_duration: int
    prerequisites: List[str]
    practice_questions: List[dict]
    examples: List[dict]
    exercises: List[dict]
    completion_rate: float
    average_score: float
    engagement_score: float
    completion_time: int
    content_quality_score: float
    version: str
    is_active: bool
    ai_generated: bool
    author: Optional[str]
    created_at: str
    updated_at: str


class UserContentProgressUpdate(BaseModel):
    progress_percent: Optional[float] = None
    time_spent: Optional[int] = None
    score: Optional[float] = None
    status: Optional[str] = None  # not_started, in_progress, completed, mastered
    notes: Optional[str] = None
    bookmarks: Optional[List[str]] = None
    difficulty_rating: Optional[float] = None


class UserContentProgressResponse(BaseModel):
    progress_id: str
    user_id: str
    content_id: str
    status: str
    progress_percent: float
    time_spent: int
    score: Optional[float]
    attempts: int
    best_score: float
    first_accessed: str
    last_accessed: str
    last_completed: Optional[str]
    notes: Optional[str]
    bookmarks: List[str]
    difficulty_rating: Optional[float]
    next_review: Optional[str]
    review_count: int


class ConceptContentList(BaseModel):
    concept_id: str
    content_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0


# Router instance
router = APIRouter()


@router.get("/concepts/{concept_id}", response_model=List[ConceptContentResponse])
async def get_concept_content(
    concept_id: str,
    content_type: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all educational content for a concept"""
    
    # Verify concept exists
    concept = db.query(Concept).filter(Concept.concept_id == concept_id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Concept not found"
        )
    
    # Build query
    query = db.query(ConceptContent).filter(ConceptContent.concept_id == concept_id)
    
    # Apply filters
    if content_type:
        query = query.filter(ConceptContent.content_type == content_type)
    
    if difficulty_level:
        query = query.filter(ConceptContent.difficulty_level == difficulty_level)
    
    # Get active content only
    query = query.filter(ConceptContent.is_active == True)
    
    # Order by order_index
    content_items = query.order_by(ConceptContent.order_index.asc()).offset(offset).limit(limit).all()
    
    return [
        ConceptContentResponse(
            content_id=str(item.content_id),
            concept_id=str(item.concept_id),
            title=item.title,
            content_type=item.content_type,
            order_index=item.order_index,
            content=item.content,
            summary=item.summary,
            learning_objectives=item.learning_objectives,
            multimedia_resources=item.multimedia_resources,
            external_links=item.external_links,
            code_examples=item.code_examples,
            interactive_elements=item.interactive_elements,
            difficulty_level=item.difficulty_level,
            estimated_duration=item.estimated_duration,
            prerequisites=item.prerequisites,
            practice_questions=item.practice_questions,
            examples=item.examples,
            exercises=item.exercises,
            completion_rate=item.completion_rate,
            average_score=item.average_score,
            engagement_score=item.engagement_score,
            completion_time=item.completion_time,
            content_quality_score=item.content_quality_score,
            version=item.version,
            is_active=item.is_active,
            ai_generated=item.ai_generated,
            author=item.author,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat()
        )
        for item in content_items
    ]


@router.get("/content/{content_id}", response_model=ConceptContentResponse)
async def get_content_by_id(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""
    
    content = db.query(ConceptContent).filter(ConceptContent.content_id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return ConceptContentResponse(
        content_id=str(content.content_id),
        concept_id=str(content.concept_id),
        title=content.title,
        content_type=content.content_type,
        order_index=content.order_index,
        content=content.content,
        summary=content.summary,
        learning_objectives=content.learning_objectives,
        multimedia_resources=content.multimedia_resources,
        external_links=content.external_links,
        code_examples=content.code_examples,
        interactive_elements=content.interactive_elements,
        difficulty_level=content.difficulty_level,
        estimated_duration=content.estimated_duration,
        prerequisites=content.prerequisites,
        practice_questions=content.practice_questions,
        examples=content.examples,
        exercises=content.exercises,
        completion_rate=content.completion_rate,
        average_score=content.average_score,
        engagement_score=content.engagement_score,
        completion_time=content.completion_time,
        content_quality_score=content.content_quality_score,
        version=content.version,
        is_active=content.is_active,
        ai_generated=content.ai_generated,
        author=content.author,
        created_at=content.created_at.isoformat(),
        updated_at=content.updated_at.isoformat()
    )


@router.post("/content/{content_id}/progress", response_model=UserContentProgressResponse)
async def update_content_progress(
    content_id: str,
    progress_update: UserContentProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's progress on specific content"""
    
    # Check if content exists
    content = db.query(ConceptContent).filter(ConceptContent.content_id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Get or create user progress record
    progress = db.query(UserContentProgress).filter(
        and_(
            UserContentProgress.user_id == current_user.user_id,
            UserContentProgress.content_id == content_id
        )
    ).first()
    
    if not progress:
        progress = UserContentProgress(
            user_id=current_user.user_id,
            content_id=content_id,
            status=progress_update.status or "in_progress"
        )
        db.add(progress)
    else:
        # Update existing progress
        if progress_update.status:
            progress.status = progress_update.status
        if progress_update.progress_percent is not None:
            progress.progress_percent = progress_update.progress_percent
        if progress_update.time_spent is not None:
            progress.time_spent += progress_update.time_spent
        if progress_update.score is not None:
            progress.score = progress_update.score
            if progress_update.score > progress.best_score:
                progress.best_score = progress_update.score
        if progress_update.notes is not None:
            progress.notes = progress_update.notes
        if progress_update.bookmarks is not None:
            progress.bookmarks = progress_update.bookmarks
        if progress_update.difficulty_rating is not None:
            progress.difficulty_rating = progress_update.difficulty_rating
    
    # Update timestamps
    progress.last_accessed = datetime.utcnow()
    if progress_update.status == "completed" and not progress.last_completed:
        progress.last_completed = datetime.utcnow()
    
    progress.attempts += 1
    
    db.commit()
    db.refresh(progress)
    
    return UserContentProgressResponse(
        progress_id=str(progress.progress_id),
        user_id=str(progress.user_id),
        content_id=str(progress.content_id),
        status=progress.status,
        progress_percent=progress.progress_percent,
        time_spent=progress.time_spent,
        score=progress.score,
        attempts=progress.attempts,
        best_score=progress.best_score,
        first_accessed=progress.first_accessed.isoformat(),
        last_accessed=progress.last_accessed.isoformat(),
        last_completed=progress.last_completed.isoformat() if progress.last_completed else None,
        notes=progress.notes,
        bookmarks=progress.bookmarks,
        difficulty_rating=progress.difficulty_rating,
        next_review=progress.next_review.isoformat() if progress.next_review else None,
        review_count=progress.review_count
    )


@router.get("/content/{content_id}/progress", response_model=UserContentProgressResponse)
async def get_content_progress(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress on specific content"""
    
    progress = db.query(UserContentProgress).filter(
        and_(
            UserContentProgress.user_id == current_user.user_id,
            UserContentProgress.content_id == content_id
        )
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this content"
        )
    
    return UserContentProgressResponse(
        progress_id=str(progress.progress_id),
        user_id=str(progress.user_id),
        content_id=str(progress.content_id),
        status=progress.status,
        progress_percent=progress.progress_percent,
        time_spent=progress.time_spent,
        score=progress.score,
        attempts=progress.attempts,
        best_score=progress.best_score,
        first_accessed=progress.first_accessed.isoformat(),
        last_accessed=progress.last_accessed.isoformat(),
        last_completed=progress.last_completed.isoformat() if progress.last_completed else None,
        notes=progress.notes,
        bookmarks=progress.bookmarks,
        difficulty_rating=progress.difficulty_rating,
        next_review=progress.next_review.isoformat() if progress.next_review else None,
        review_count=progress.review_count
    )


@router.get("/concepts/{concept_id}/progress", response_model=List[UserContentProgressResponse])
async def get_concept_content_progress(
    concept_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress on all content for a concept"""
    
    # Get all content for the concept
    content_items = db.query(ConceptContent).filter(
        and_(
            ConceptContent.concept_id == concept_id,
            ConceptContent.is_active == True
        )
    ).all()
    
    content_ids = [str(item.content_id) for item in content_items]
    
    if not content_ids:
        return []
    
    # Get user progress for all content
    progress_records = db.query(UserContentProgress).filter(
        and_(
            UserContentProgress.user_id == current_user.user_id,
            UserContentProgress.content_id.in_(content_ids)
        )
    ).all()
    
    return [
        UserContentProgressResponse(
            progress_id=str(progress.progress_id),
            user_id=str(progress.user_id),
            content_id=str(progress.content_id),
            status=progress.status,
            progress_percent=progress.progress_percent,
            time_spent=progress.time_spent,
            score=progress.score,
            attempts=progress.attempts,
            best_score=progress.best_score,
            first_accessed=progress.first_accessed.isoformat(),
            last_accessed=progress.last_accessed.isoformat(),
            last_completed=progress.last_completed.isoformat() if progress.last_completed else None,
            notes=progress.notes,
            bookmarks=progress.bookmarks,
            difficulty_rating=progress.difficulty_rating,
            next_review=progress.next_review.isoformat() if progress.next_review else None,
            review_count=progress.review_count
        )
        for progress in progress_records
    ]


@router.post("/start-learning/{concept_id}")
async def start_learning_concept(
    concept_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start learning a concept - returns the first content piece to begin with"""
    
    # Get concept details
    concept = db.query(Concept).filter(Concept.concept_id == concept_id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Concept not found"
        )
    
    # Get the first content piece (typically a lesson)
    content = db.query(ConceptContent).filter(
        and_(
            ConceptContent.concept_id == concept_id,
            ConceptContent.content_type == "lesson",
            ConceptContent.is_active == True
        )
    ).order_by(ConceptContent.order_index.asc()).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No learning content available for this concept"
        )
    
    # Update or create user progress
    progress = db.query(UserContentProgress).filter(
        and_(
            UserContentProgress.user_id == current_user.user_id,
            UserContentProgress.content_id == str(content.content_id)
        )
    ).first()
    
    if not progress:
        progress = UserContentProgress(
            user_id=current_user.user_id,
            content_id=str(content.content_id),
            status="in_progress",
            progress_percent=0.0
        )
        db.add(progress)
    else:
        progress.status = "in_progress"
        progress.last_accessed = datetime.utcnow()
    
    db.commit()
    db.refresh(progress)
    
    return {
        "message": f"Started learning {concept.display_name}",
        "concept": {
            "id": str(concept.concept_id),
            "name": concept.display_name,
            "description": concept.description
        },
        "content": {
            "content_id": str(content.content_id),
            "title": content.title,
            "content_type": content.content_type,
            "summary": content.summary,
            "estimated_duration": content.estimated_duration,
            "learning_objectives": content.learning_objectives
        },
        "progress": {
            "status": progress.status,
            "progress_percent": progress.progress_percent,
            "time_spent": progress.time_spent
        }
    }


@router.get("/recommendations/{content_id}/next")
async def get_next_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the next recommended content piece after completing current one"""
    
    # Get current content
    current_content = db.query(ConceptContent).filter(ConceptContent.content_id == content_id).first()
    if not current_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Get next content in the same concept
    next_content = db.query(ConceptContent).filter(
        and_(
            ConceptContent.concept_id == str(current_content.concept_id),
            ConceptContent.order_index > current_content.order_index,
            ConceptContent.is_active == True
        )
    ).order_by(ConceptContent.order_index.asc()).first()
    
    if not next_content:
        return {
            "message": "You've completed all content for this concept!",
            "next_content": None,
            "recommendation": "Consider exploring related concepts or taking a quiz to test your knowledge."
        }
    
    return {
        "current_content": {
            "content_id": str(current_content.content_id),
            "title": current_content.title
        },
        "next_content": {
            "content_id": str(next_content.content_id),
            "title": next_content.title,
            "content_type": next_content.content_type,
            "summary": next_content.summary,
            "estimated_duration": next_content.estimated_duration
        },
        "recommendation": f"Next up: {next_content.title} ({next_content.content_type})"
    }