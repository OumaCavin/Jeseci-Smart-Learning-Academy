"""
Progress tracking API endpoints
User progress monitoring and analytics
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

from api.v1.auth import get_current_user
from config.database import get_db
from config.logging_config import get_logger
from database.models import User, UserConceptProgress, Concept

# Get logger for this module
logger = get_logger(__name__)


# Router instance
router = APIRouter()


class ProgressUpdateRequest(BaseModel):
    """Request model for updating concept progress"""
    time_spent_minutes: int = 0
    progress_percent: int = 0
    status: str = "in_progress"  # not_started, in_progress, completed
    user_notes: Optional[str] = None


@router.get("/")
async def get_progress_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full dashboard progress stats (Matches Frontend Expectations)"""
    
    # 1. Fetch User's Progress Records
    progress_records = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == current_user.user_id
    ).all()
    
    logger.info(f"📊 Found {len(progress_records)} progress records for user: {current_user.user_id}")
    
    # 2. Calculate Aggregates
    total_concepts = len(progress_records)
    completed = sum(1 for p in progress_records if p.status == 'completed')
    total_minutes = sum((p.time_spent_minutes or 0) for p in progress_records)
    
    # Avoid division by zero
    completion_rate = round((completed / total_concepts * 100) if total_concepts > 0 else 0)
    
    # Simple Streak Logic (Check if accessed today)
    # In production, check consecutive days in an activity log table
    streak = 1 if total_minutes > 0 else 0

    # 3. Format Recent Activity
    # Get top 5 most recently accessed
    recent_records = sorted(progress_records, key=lambda x: x.last_accessed, reverse=True)[:5]
    
    recent_activity = []
    
    # Helper to get concept names efficiently
    concept_ids = [p.concept_id for p in recent_records]
    if concept_ids:
        concepts = db.query(Concept).filter(Concept.concept_id.in_(concept_ids)).all()
        concept_map = {c.concept_id: c.display_name for c in concepts}
    else:
        concept_map = {}

    for p in recent_records:
        concept_name = concept_map.get(p.concept_id, "Unknown Concept")
        # Calculate time ago
        time_diff = datetime.utcnow() - p.last_accessed
        if time_diff.days > 0:
            time_str = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = time_diff.seconds // 60
            time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            
        recent_activity.append({
            "date": p.last_accessed.strftime("%Y-%m-%d"),
            "activity": f"Studied {concept_name}",
            "time": time_str
        })

    # 4. Concept Progress List
    # Get all available concepts to show "Not Started" ones too
    all_concepts = db.query(Concept).all()
    
    # Create a map of progress
    progress_map = {p.concept_id: p for p in progress_records}
    
    concept_list = []
    for concept in all_concepts:
        p = progress_map.get(concept.concept_id)
        if p:
            concept_list.append({
                "name": concept.display_name,
                "progress": p.progress_percent or 0,
                "status": p.status
            })
        else:
            concept_list.append({
                "name": concept.display_name,
                "progress": 0,
                "status": "not_started"
            })

    return {
        "overall_stats": {
            "total_concepts_learned": completed,
            "total_time_spent": round(total_minutes / 60, 1),
            "learning_streak": streak,
            "completion_rate": completion_rate
        },
        "recent_activity": recent_activity,
        "concept_progress": concept_list,  # Return full list for dashboard
        "concept_progress_summary": {
            "total_items": len(concept_list),
            "displaying": min(10, len(concept_list)),  # Show up to 10 items
            "has_more": len(concept_list) > 10
        },
        "weekly_goals": {
            "target": 5, 
            "completed": round(total_minutes / 60, 1),
            "remaining_days": 7 - datetime.today().weekday()
        }
    }


@router.post("/concepts/{concept_id}/update")
async def update_concept_progress(
    concept_id: str,
    progress_data: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress for a specific concept"""
    
    logger.info(f"🔄 Updating progress for concept: {concept_id}")
    logger.debug(f"📊 Update data received: {progress_data}")
    
    # Check if concept exists first
    concept = db.query(Concept).filter(Concept.concept_id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # Find existing record or create new one
    progress = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == current_user.user_id,
        UserConceptProgress.concept_id == concept_id
    ).first()
    
    if not progress:
        progress = UserConceptProgress(
            user_id=current_user.user_id,
            concept_id=concept_id,
            time_spent_minutes=0,
            status="not_started"
        )
        db.add(progress)
    
    # Update fields
    current_time_spent = progress.time_spent_minutes or 0
    progress.time_spent_minutes = current_time_spent + progress_data.time_spent_minutes
    
    # Handle None progress_percent (new records or empty database fields)
    current_progress = progress.progress_percent or 0
    progress.progress_percent = max(current_progress, progress_data.progress_percent)  # Don't regress
    
    progress.status = progress_data.status
    progress.user_notes = progress_data.user_notes
    progress.last_accessed = datetime.utcnow()
    
    db.commit()
    db.refresh(progress)
    
    logger.info(f"✅ Progress updated successfully: {progress.status}, time_spent_minutes: {progress.time_spent_minutes}")
    
    return {
        "message": "Progress updated successfully", 
        "current_progress": progress.progress_percent,
        "status": progress.status
    }


@router.get("/concepts/{concept_id}")
async def get_concept_progress(
    concept_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress for specific concept"""
    
    progress = db.query(UserConceptProgress).filter(
        UserConceptProgress.user_id == current_user.user_id,
        UserConceptProgress.concept_id == concept_id
    ).first()
    
    if not progress:
        return {
            "concept_id": concept_id,
            "progress_percent": 0,
            "status": "not_started",
            "time_spent_minutes": 0,
            "last_accessed": None
        }
    
    return {
        "concept_id": concept_id,
        "progress_percent": progress.progress_percent,
        "status": progress.status,
        "time_spent_minutes": progress.time_spent_minutes,
        "last_accessed": progress.last_accessed.isoformat(),
        "user_notes": progress.user_notes
    }


@router.get("/overview")
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's overall progress overview"""
    return await get_progress_dashboard(current_user, db)