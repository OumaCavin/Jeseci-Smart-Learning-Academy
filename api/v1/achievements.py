"""
Achievements API endpoints
User achievements and gamification
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
from pydantic import BaseModel

from api.v1.auth import get_current_user
from config.database import get_db
from config.logging_config import get_logger
from database.models import User, UserAchievement, UserConceptProgress, QuizAttempt

# Get logger for this module
logger = get_logger(__name__)


# Router instance
router = APIRouter()


# Achievement Definition Model
class AchievementDefinition(BaseModel):
    """Achievement definition for available achievements"""
    achievement_type: str
    achievement_name: str
    description: str
    badge_icon: str
    category: str
    requirements: Dict[str, Any]
    rarity: str  # common, uncommon, rare, epic, legendary


class UserAchievementResponse(BaseModel):
    """User achievement response data"""
    achievement_id: str
    achievement_type: str
    achievement_name: str
    description: str
    badge_icon: str
    category: str
    value: float
    target_value: float
    percentage: float
    earned_at: datetime
    is_completed: bool


class AchievementAnalytics(BaseModel):
    """Achievement analytics data"""
    total_achievements: int
    completed_achievements: int
    total_points: float
    category_breakdown: Dict[str, int]
    recent_achievements: List[Dict[str, Any]]
    next_achievements: List[Dict[str, Any]]


# Predefined achievement definitions
AVAILABLE_ACHIEVEMENTS = {
    # Learning Progress Achievements
    "first_concept_completion": {
        "achievement_type": "first_concept_completion",
        "achievement_name": "First Steps",
        "description": "Complete your first concept",
        "badge_icon": "🎯",
        "category": "milestone",
        "requirements": {"concepts_completed": 1},
        "rarity": "common"
    },
    "concept_master": {
        "achievement_type": "concept_master",
        "achievement_name": "Concept Master",
        "description": "Complete 10 concepts",
        "badge_icon": "📚",
        "category": "excellence",
        "requirements": {"concepts_completed": 10},
        "rarity": "uncommon"
    },
    "knowledge_seeker": {
        "achievement_type": "knowledge_seeker",
        "achievement_name": "Knowledge Seeker",
        "description": "Complete 25 concepts",
        "badge_icon": "🧠",
        "category": "excellence",
        "requirements": {"concepts_completed": 25},
        "rarity": "rare"
    },
    "learning_addict": {
        "achievement_type": "learning_addict",
        "achievement_name": "Learning Addict",
        "description": "Complete 50 concepts",
        "badge_icon": "🎓",
        "category": "excellence",
        "requirements": {"concepts_completed": 50},
        "rarity": "epic"
    },
    "wisdom_master": {
        "achievement_type": "wisdom_master",
        "achievement_name": "Wisdom Master",
        "description": "Complete 100 concepts",
        "badge_icon": "👑",
        "category": "excellence",
        "requirements": {"concepts_completed": 100},
        "rarity": "legendary"
    },
    
    # Time-based Achievements
    "time_investor": {
        "achievement_type": "time_investor",
        "achievement_name": "Time Investor",
        "description": "Spend 10 hours learning",
        "badge_icon": "⏰",
        "category": "dedication",
        "requirements": {"total_time_minutes": 600},
        "rarity": "common"
    },
    "marathon_learner": {
        "achievement_type": "marathon_learner",
        "achievement_name": "Marathon Learner",
        "description": "Spend 50 hours learning",
        "badge_icon": "🏃‍♂️",
        "category": "dedication",
        "requirements": {"total_time_minutes": 3000},
        "rarity": "uncommon"
    },
    "study_legend": {
        "achievement_type": "study_legend",
        "achievement_name": "Study Legend",
        "description": "Spend 100 hours learning",
        "badge_icon": "📖",
        "category": "dedication",
        "requirements": {"total_time_minutes": 6000},
        "rarity": "rare"
    },
    
    # Streak Achievements
    "consistent_learner": {
        "achievement_type": "consistent_learner",
        "achievement_name": "Consistent Learner",
        "description": "Maintain a 7-day learning streak",
        "badge_icon": "🔥",
        "category": "consistency",
        "requirements": {"learning_streak": 7},
        "rarity": "uncommon"
    },
    "dedication_champion": {
        "achievement_type": "dedication_champion",
        "achievement_name": "Dedication Champion",
        "description": "Maintain a 30-day learning streak",
        "badge_icon": "🏆",
        "category": "consistency",
        "requirements": {"learning_streak": 30},
        "rarity": "epic"
    },
    
    # Quiz Achievements
    "first_quiz_completion": {
        "achievement_type": "first_quiz_completion",
        "achievement_name": "Quiz Novice",
        "description": "Complete your first quiz",
        "badge_icon": "✅",
        "category": "assessment",
        "requirements": {"quizzes_completed": 1},
        "rarity": "common"
    },
    "quiz_master": {
        "achievement_type": "quiz_master",
        "achievement_name": "Quiz Master",
        "description": "Complete 20 quizzes",
        "badge_icon": "🎯",
        "category": "assessment",
        "requirements": {"quizzes_completed": 20},
        "rarity": "rare"
    },
    "perfect_scorer": {
        "achievement_type": "perfect_scorer",
        "achievement_name": "Perfect Scorer",
        "description": "Achieve a perfect score on any quiz",
        "badge_icon": "💯",
        "category": "assessment",
        "requirements": {"perfect_quiz_scores": 1},
        "rarity": "epic"
    },
    
    # Domain-specific Achievements
    "programming_pro": {
        "achievement_type": "programming_pro",
        "achievement_name": "Programming Pro",
        "description": "Complete 10 programming concepts",
        "badge_icon": "💻",
        "category": "domain",
        "requirements": {"domain_concepts": {"Programming": 10}},
        "rarity": "uncommon"
    },
    "data_scientist": {
        "achievement_type": "data_scientist",
        "achievement_name": "Data Scientist",
        "description": "Complete 10 data science concepts",
        "badge_icon": "📊",
        "category": "domain",
        "requirements": {"domain_concepts": {"Data Science": 10}},
        "rarity": "uncommon"
    }
}


@router.get("/")
async def get_user_achievements(
    category: Optional[str] = None,
    include_progress: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's achievements with optional filtering"""
    
    try:
        logger.info(f"🏆 Fetching achievements for user: {current_user.user_id}")
        
        # Build query
        query = db.query(UserAchievement).filter(UserAchievement.user_id == current_user.user_id)
        
        if category:
            query = query.filter(UserAchievement.category == category)
        
        achievements = query.order_by(desc(UserAchievement.earned_at)).all()
        
        result = []
        for achievement in achievements:
            achievement_data = {
                "achievement_id": achievement.achievement_id,
                "achievement_type": achievement.achievement_type,
                "achievement_name": achievement.achievement_name,
                "description": achievement.description,
                "badge_icon": achievement.badge_icon,
                "category": achievement.category,
                "value": achievement.value,
                "target_value": achievement.target_value,
                "percentage": achievement.percentage,
                "earned_at": achievement.earned_at,
                "is_completed": achievement.percentage >= 100.0
            }
            result.append(achievement_data)
        
        # Calculate analytics
        analytics = calculate_user_achievement_analytics(result)
        
        logger.info(f"✅ Found {len(result)} achievements")
        
        return {
            "success": True, 
            "data": {
                "achievements": result,
                "analytics": analytics if include_progress else None
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching user achievements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch achievements: {str(e)}")


@router.get("/available")
async def get_available_achievements(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available achievement definitions"""
    
    try:
        logger.info(f"🎯 Fetching available achievements")
        
        result = []
        for achievement_type, definition in AVAILABLE_ACHIEVEMENTS.items():
            if category and definition["category"] != category:
                continue
            
            # Check if user already has this achievement
            existing = db.query(UserAchievement).filter(
                and_(
                    UserAchievement.user_id == current_user.user_id,
                    UserAchievement.achievement_type == achievement_type
                )
            ).first()
            
            achievement_data = {
                **definition,
                "is_earned": existing is not None,
                "progress": existing.percentage if existing else 0.0,
                "current_value": existing.value if existing else 0.0
            }
            result.append(achievement_data)
        
        logger.info(f"✅ Found {len(result)} available achievements")
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"❌ Error fetching available achievements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch available achievements: {str(e)}")


@router.get("/analytics")
async def get_achievement_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive achievement analytics for user"""
    
    try:
        logger.info(f"📊 Calculating achievement analytics for user: {current_user.user_id}")
        
        # Get user achievements
        achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == current_user.user_id
        ).all()
        
        # Get user progress data for calculations
        concept_progress = db.query(UserConceptProgress).filter(
            UserConceptProgress.user_id == current_user.user_id
        ).all()
        
        quiz_attempts = db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.user_id == current_user.user_id,
                QuizAttempt.status == 'completed'
            )
        ).all()
        
        # Calculate user statistics
        user_stats = calculate_user_learning_stats(concept_progress, quiz_attempts)
        
        # Analyze achievement progress
        achievement_progress = analyze_achievement_progress(user_stats, achievements)
        
        analytics = {
            "total_achievements": len(achievements),
            "completed_achievements": sum(1 for a in achievements if a.percentage >= 100.0),
            "total_points": sum(a.value for a in achievements),
            "category_breakdown": calculate_category_breakdown(achievements),
            "recent_achievements": get_recent_achievements(achievements, 5),
            "next_achievements": get_next_achievable_achievements(achievement_progress, 5),
            "completion_percentage": (sum(1 for a in achievements if a.percentage >= 100.0) / len(AVAILABLE_ACHIEVEMENTS)) * 100 if AVAILABLE_ACHIEVEMENTS else 0,
            "user_statistics": user_stats,
            "achievement_progress": achievement_progress
        }
        
        logger.info(f"✅ Achievement analytics calculated")
        return {"success": True, "data": analytics}
        
    except Exception as e:
        logger.error(f"❌ Error calculating achievement analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate analytics: {str(e)}")


@router.post("/check-achievements")
async def check_and_award_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check for new achievements and award them"""
    
    try:
        logger.info(f"🔍 Checking achievements for user: {current_user.user_id}")
        
        # Get current user data
        concept_progress = db.query(UserConceptProgress).filter(
            UserConceptProgress.user_id == current_user.user_id
        ).all()
        
        quiz_attempts = db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.user_id == current_user.user_id,
                QuizAttempt.status == 'completed'
            )
        ).all()
        
        # Calculate user statistics
        user_stats = calculate_user_learning_stats(concept_progress, quiz_attempts)
        
        # Check for new achievements
        new_achievements = []
        existing_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == current_user.user_id
        ).all()
        
        existing_types = {a.achievement_type for a in existing_achievements}
        
        for achievement_type, definition in AVAILABLE_ACHIEVEMENTS.items():
            if achievement_type in existing_types:
                continue  # Already earned
            
            progress = check_achievement_progress(definition, user_stats)
            
            if progress >= 100.0:
                # Award new achievement
                achievement = UserAchievement(
                    user_id=current_user.user_id,
                    achievement_type=achievement_type,
                    achievement_name=definition["achievement_name"],
                    description=definition["description"],
                    badge_icon=definition["badge_icon"],
                    category=definition["category"],
                    value=min(progress, definition["requirements"].get("target_value", 1.0)),
                    target_value=definition["requirements"].get("target_value", 1.0),
                    percentage=progress,
                    earned_at=datetime.utcnow()
                )
                
                db.add(achievement)
                new_achievements.append({
                    "achievement_type": achievement_type,
                    "achievement_name": definition["achievement_name"],
                    "description": definition["description"],
                    "badge_icon": definition["badge_icon"],
                    "category": definition["category"]
                })
        
        if new_achievements:
            db.commit()
            logger.info(f"✅ Awarded {len(new_achievements)} new achievements")
        
        return {
            "success": True,
            "data": {
                "new_achievements": new_achievements,
                "checked_count": len(AVAILABLE_ACHIEVEMENTS),
                "current_stats": user_stats
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error checking achievements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check achievements: {str(e)}")


@router.get("/leaderboard")
async def get_achievement_leaderboard(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get achievement leaderboard (users with most achievements)"""
    
    try:
        logger.info(f"🏆 Fetching achievement leaderboard")
        
        # Get user achievement counts
        user_stats = db.query(
            UserAchievement.user_id,
            func.count(UserAchievement.achievement_id).label('achievement_count'),
            func.sum(UserAchievement.value).label('total_points')
        ).group_by(UserAchievement.user_id).order_by(
            desc('achievement_count'),
            desc('total_points')
        ).limit(limit).all()
        
        # Get user details for top performers
        result = []
        for i, (user_id, count, points) in enumerate(user_stats):
            # Get user info (this would need to join with users table)
            user = db.query(User).filter(User.user_id == user_id).first()
            
            result.append({
                "rank": i + 1,
                "user_id": user_id,
                "username": user.username if user else "Unknown User",
                "achievement_count": count,
                "total_points": float(points) if points else 0.0,
                "is_current_user": user_id == current_user.user_id
            })
        
        # Find current user's rank
        user_rank = None
        for i, user_data in enumerate(result):
            if user_data["user_id"] == current_user.user_id:
                user_rank = i + 1
                break
        
        return {
            "success": True,
            "data": {
                "leaderboard": result,
                "current_user_rank": user_rank,
                "total_users": len(user_stats)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leaderboard: {str(e)}")


# Helper Functions
def calculate_user_achievement_analytics(achievements: List[UserAchievement]):
    """Calculate achievement analytics from user achievements"""
    
    if not achievements:
        return {
            "total_achievements": 0,
            "completed_achievements": 0,
            "total_points": 0,
            "completion_percentage": 0,
            "category_breakdown": {},
            "recent_achievements": [],
            "next_achievements": []
        }
    
    completed = [a for a in achievements if a.percentage >= 100.0]
    
    analytics = {
        "total_achievements": len(achievements),
        "completed_achievements": len(completed),
        "total_points": sum(a.value for a in achievements),
        "completion_percentage": (len(completed) / len(AVAILABLE_ACHIEVEMENTS)) * 100,
        "category_breakdown": calculate_category_breakdown(achievements),
        "recent_achievements": get_recent_achievements(achievements, 3)
    }
    
    return analytics


def calculate_category_breakdown(achievements: List[UserAchievement]) -> Dict[str, int]:
    """Calculate breakdown of achievements by category"""
    
    breakdown = {}
    for achievement in achievements:
        category = achievement.category
        if category in breakdown:
            breakdown[category] += 1
        else:
            breakdown[category] = 1
    
    return breakdown


def get_recent_achievements(achievements: List[UserAchievement], limit: int) -> List[Dict[str, Any]]:
    """Get recent achievements sorted by earned date"""
    
    sorted_achievements = sorted(achievements, key=lambda a: a.earned_at, reverse=True)
    
    return [
        {
            "achievement_name": a.achievement_name,
            "badge_icon": a.badge_icon,
            "category": a.category,
            "earned_at": a.earned_at
        }
        for a in sorted_achievements[:limit]
    ]


def calculate_user_learning_stats(concept_progress: List[UserConceptProgress], quiz_attempts: List[QuizAttempt]):
    """Calculate user learning statistics for achievement checking"""
    
    # Concept statistics
    completed_concepts = [p for p in concept_progress if p.status == 'completed']
    total_time_minutes = sum((p.time_spent_minutes or 0) for p in concept_progress)
    
    # Domain statistics
    domain_stats = {}
    for progress in completed_concepts:
        # This would need to join with concepts table to get domain
        # For now, we'll simulate it
        domain = "General"  # Placeholder
        if domain in domain_stats:
            domain_stats[domain] += 1
        else:
            domain_stats[domain] = 1
    
    # Quiz statistics
    quiz_completed = len(quiz_attempts)
    perfect_scores = sum(1 for q in quiz_attempts if q.percentage == 1.0)
    
    # Calculate learning streak (simplified)
    # This would need more complex logic to calculate actual streak
    learning_streak = 0  # Placeholder
    
    stats = {
        "concepts_completed": len(completed_concepts),
        "total_time_minutes": total_time_minutes,
        "learning_streak": learning_streak,
        "quizzes_completed": quiz_completed,
        "perfect_quiz_scores": perfect_scores,
        "domain_concepts": domain_stats
    }
    
    return stats


def check_achievement_progress(definition: Dict[str, Any], user_stats: Dict[str, Any]) -> float:
    """Check if user meets achievement requirements and return progress percentage"""
    
    requirements = definition.get("requirements", {})
    progress = 0.0
    
    for req_key, req_value in requirements.items():
        if req_key in user_stats:
            user_value = user_stats[req_key]
            
            if isinstance(req_value, dict):
                # Handle complex requirements like domain_concepts
                if req_key == "domain_concepts":
                    domain_req = req_value
                    domain_progress = 0
                    for domain, required_count in domain_req.items():
                        if domain in user_value:
                            domain_progress += min(user_value[domain] / required_count, 1.0)
                    progress = max(progress, domain_progress / len(domain_req))
            else:
                # Handle simple numeric requirements
                if req_value > 0:
                    progress = max(progress, min(user_value / req_value, 1.0))
    
    return progress * 100.0


def analyze_achievement_progress(user_stats: Dict[str, Any], existing_achievements: List[UserAchievement]):
    """Analyze current progress towards all achievements"""
    
    progress_data = {}
    existing_types = {a.achievement_type for a in existing_achievements}
    
    for achievement_type, definition in AVAILABLE_ACHIEVEMENTS.items():
        if achievement_type in existing_types:
            continue  # Already earned
        
        progress = check_achievement_progress(definition, user_stats)
        progress_data[achievement_type] = {
            "achievement_name": definition["achievement_name"],
            "progress": progress,
            "category": definition["category"],
            "rarity": definition["rarity"]
        }
    
    return progress_data


def get_next_achievable_achievements(progress_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    """Get next achievements user can achieve"""
    
    # Sort by progress (highest first) and filter those with >0 progress
    sorted_achievements = sorted(
        [(k, v) for k, v in progress_data.items() if v["progress"] > 0],
        key=lambda x: x[1]["progress"],
        reverse=True
    )
    
    return [
        {
            "achievement_type": achievement_type,
            "achievement_name": data["achievement_name"],
            "progress": data["progress"],
            "category": data["category"],
            "rarity": data["rarity"]
        }
        for achievement_type, data in sorted_achievements[:limit]
    ]