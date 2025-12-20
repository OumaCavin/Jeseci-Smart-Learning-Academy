"""
User management API endpoints
CRUD operations for users and their preferences
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, EmailStr

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from api.v1.auth import get_current_user
from config.database import get_db
from database.models import User, UserLearningPreferences


# Pydantic models
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    learning_style: Optional[str] = None
    skill_level: Optional[str] = None
    bio: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    content_type_preferences: Optional[List[str]] = None
    difficulty_preferences: Optional[dict] = None
    subject_preferences: Optional[List[str]] = None
    study_time_preferences: Optional[dict] = None
    session_length_preferences: Optional[int] = None
    interaction_preferences: Optional[dict] = None
    feedback_preferences: Optional[dict] = None
    accessibility_needs: Optional[dict] = None
    personalization_settings: Optional[dict] = None


class UserPreferencesResponse(BaseModel):
    preference_id: str
    user_id: str
    content_type_preferences: List[str]
    difficulty_preferences: dict
    subject_preferences: List[str]
    study_time_preferences: dict
    session_length_preferences: int
    interaction_preferences: dict
    feedback_preferences: dict
    accessibility_needs: dict
    personalization_settings: dict
    created_at: str
    updated_at: str


class UserStats(BaseModel):
    total_sessions: int
    total_concepts_learned: int
    average_mastery_score: float
    current_streak: int
    total_time_spent: int  # in minutes
    achievements_earned: int


# Router instance
router = APIRouter()


@router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's full profile"""
    return {
        "user_id": str(current_user.user_id),
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "profile_picture": current_user.profile_picture,
        "bio": current_user.bio,
        "learning_style": current_user.learning_style,
        "skill_level": current_user.skill_level,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }


@router.put("/profile")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully", "user": {
        "user_id": str(current_user.user_id),
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "bio": current_user.bio,
        "learning_style": current_user.learning_style,
        "skill_level": current_user.skill_level,
        "updated_at": current_user.updated_at
    }}


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's learning preferences"""
    
    preferences = db.query(UserLearningPreferences).filter(
        UserLearningPreferences.user_id == current_user.user_id
    ).first()
    
    if not preferences:
        # Create default preferences if they don't exist
        preferences = UserLearningPreferences(
            user_id=current_user.user_id,
            content_type_preferences=["text", "interactive"],
            difficulty_preferences={"preferred": current_user.skill_level or "beginner"},
            subject_preferences=[],
            study_time_preferences={"preferred_time": "morning", "duration": 30},
            session_length_preferences=30
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return UserPreferencesResponse(
        preference_id=str(preferences.preference_id),
        user_id=str(preferences.user_id),
        content_type_preferences=preferences.content_type_preferences,
        difficulty_preferences=preferences.difficulty_preferences,
        subject_preferences=preferences.subject_preferences,
        study_time_preferences=preferences.study_time_preferences,
        session_length_preferences=preferences.session_length_preferences,
        interaction_preferences=preferences.interaction_preferences,
        feedback_preferences=preferences.feedback_preferences,
        accessibility_needs=preferences.accessibility_needs,
        personalization_settings=preferences.personalization_settings,
        created_at=preferences.created_at.isoformat(),
        updated_at=preferences.updated_at.isoformat()
    )


@router.put("/preferences")
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's learning preferences"""
    
    preferences = db.query(UserLearningPreferences).filter(
        UserLearningPreferences.user_id == current_user.user_id
    ).first()
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    
    # Update preference fields
    update_data = preferences_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)
    
    preferences.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preferences)
    
    return {
        "message": "Preferences updated successfully",
        "preferences": {
            "preference_id": str(preferences.preference_id),
            "content_type_preferences": preferences.content_type_preferences,
            "difficulty_preferences": preferences.difficulty_preferences,
            "subject_preferences": preferences.subject_preferences,
            "study_time_preferences": preferences.study_time_preferences,
            "session_length_preferences": preferences.session_length_preferences,
            "interaction_preferences": preferences.interaction_preferences,
            "feedback_preferences": preferences.feedback_preferences,
            "accessibility_needs": preferences.accessibility_needs,
            "personalization_settings": preferences.personalization_settings,
            "updated_at": preferences.updated_at
        }
    }


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's learning statistics"""
    
    # Import here to avoid circular imports
    from database.models import LearningSession, UserProgress, UserAchievement
    
    # Calculate statistics
    total_sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.user_id
    ).count()
    
    concepts_learned = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.user_id,
            UserProgress.mastery_level >= 0.8
        )
    ).count()
    
    # Average mastery score
    avg_mastery = db.query(UserProgress.mastery_level).filter(
        UserProgress.user_id == current_user.user_id
    ).all()
    
    average_mastery_score = (
        sum([m[0] for m in avg_mastery]) / len(avg_mastery)
        if avg_mastery else 0.0
    )
    
    # Current streak (simplified - could be more sophisticated)
    current_streak = 3  # Placeholder - would calculate based on recent activity
    
    # Total time spent (in minutes)
    total_time = db.query(LearningSession.total_duration).filter(
        LearningSession.user_id == current_user.user_id
    ).all()
    
    total_time_spent = sum([t[0] for t in total_time]) // 60 if total_time else 0
    
    # Achievements earned
    achievements_earned = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.user_id
    ).count()
    
    return UserStats(
        total_sessions=total_sessions,
        total_concepts_learned=concepts_learned,
        average_mastery_score=round(average_mastery_score, 2),
        current_streak=current_streak,
        total_time_spent=total_time_spent,
        achievements_earned=achievements_earned
    )


@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account (soft delete - deactivate)"""
    
    # Soft delete - deactivate user instead of hard delete
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Account deactivated successfully"}


@router.post("/reactivate")
async def reactivate_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate deactivated user account"""
    
    current_user.is_active = True
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Account reactivated successfully"}