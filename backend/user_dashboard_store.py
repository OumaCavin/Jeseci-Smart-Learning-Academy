"""
User Dashboard Store - Database Operations for User Dashboard

This module handles all database operations for the user dashboard,
including progress tracking, learning analytics, courses, achievements,
and quizzes. It uses SQLAlchemy ORM for database interactions.

Author: Cavin Otieno
License: MIT License
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session, joinedload
import json

from backend.config.database import SessionLocal
from backend.database.models import (
    User, UserProfile, UserLearningPreference,
    UserConceptProgress, UserLearningPath, UserLessonProgress, LearningSession,
    Concept, LearningPath, Lesson, LearningPathConcept,
    Quiz, QuizAttempt,
    Achievement, UserAchievement, Badge, UserBadge
)


class UserDashboardStore:
    """Store class for user dashboard database operations"""
    
    def __init__(self):
        """Initialize the user dashboard store"""
        self.session = SessionLocal()
    
    def close(self):
        """Close the database session"""
        if self.session:
            self.session.close()
    
    def _get_or_create_session(self) -> Session:
        """Get or create a database session"""
        if not self.session or not self.session.is_active:
            self.session = SessionLocal()
        return self.session
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id string"""
        try:
            session = self._get_or_create_session()
            user = session.query(User).filter(User.user_id == user_id).first()
            return user
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def get_user_internal_id(self, user_id: str) -> Optional[int]:
        """Get user's internal ID from user_id string"""
        user = self.get_user_by_id(user_id)
        return user.id if user else None
    
    # =============================================================================
    # Progress Tracking
    # =============================================================================
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user progress data
        
        Returns:
            Dictionary containing:
            - courses_completed: Number of completed learning paths
            - lessons_completed: Number of completed lessons
            - concepts_completed: Number of concepts with 100% progress
            - total_study_time: Total study time in minutes
            - current_streak: Current learning streak in days
            - average_score: Average quiz score
            - concept_progress: Per-concept progress details
            - path_progress: Per-learning-path progress details
        """
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get completed lessons count
            completed_lessons = session.query(func.count(UserLessonProgress.id)).filter(
                and_(
                    UserLessonProgress.user_id == user.id,
                    UserLessonProgress.is_completed == True
                )
            ).scalar() or 0
            
            # Get completed concepts count
            completed_concepts = session.query(func.count(UserConceptProgress.id)).filter(
                and_(
                    UserConceptProgress.user_id == user.id,
                    UserConceptProgress.progress_percent >= 100
                )
            ).scalar() or 0
            
            # Get completed learning paths count
            completed_paths = session.query(func.count(UserLearningPath.id)).filter(
                and_(
                    UserLearningPath.user_id == user.id,
                    UserLearningPath.progress_percent >= 100
                )
            ).scalar() or 0
            
            # Get total study time from sessions
            total_study_seconds = session.query(func.sum(LearningSession.duration_seconds)).filter(
                LearningSession.user_id == user.id
            ).scalar() or 0
            total_study_minutes = round(total_study_seconds / 60, 2)
            
            # Calculate current streak
            current_streak = self._calculate_learning_streak(user.id)
            
            # Get average quiz score
            avg_score = session.query(func.avg(QuizAttempt.score)).filter(
                and_(
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.score.isnot(None)
                )
            ).scalar() or 0
            average_score = round(avg_score, 1) if avg_score else 0
            
            # Get concept-level progress
            concept_progress_list = session.query(UserConceptProgress).options(
                joinedload(UserConceptProgress.concept)
            ).filter(UserConceptProgress.user_id == user.id).all()
            
            concept_progress = []
            for cp in concept_progress_list:
                concept_progress.append({
                    "concept_id": cp.concept_id,
                    "concept_name": cp.concept.name if cp.concept else cp.concept_id,
                    "progress_percent": cp.progress_percent,
                    "mastery_level": cp.mastery_level,
                    "time_spent_minutes": cp.time_spent_minutes,
                    "last_accessed": cp.last_accessed.isoformat() if cp.last_accessed else None,
                    "completed_at": cp.completed_at.isoformat() if cp.completed_at else None
                })
            
            # Get learning path progress
            path_progress_list = session.query(UserLearningPath).options(
                joinedload(UserLearningPath.learning_path)
            ).filter(UserLearningPath.user_id == user.id).all()
            
            path_progress = []
            for pp in path_progress_list:
                path_progress.append({
                    "path_id": pp.path_id,
                    "path_name": pp.learning_path.title if pp.learning_path else pp.path_id,
                    "progress_percent": round(pp.progress_percent, 1),
                    "started_at": pp.started_at.isoformat() if pp.started_at else None,
                    "last_accessed": pp.last_accessed.isoformat() if pp.last_accessed else None,
                    "completed_at": pp.completed_at.isoformat() if pp.completed_at else None
                })
            
            return {
                "success": True,
                "progress": {
                    "courses_completed": completed_paths,
                    "lessons_completed": completed_lessons,
                    "concepts_completed": completed_concepts,
                    "total_study_time": total_study_minutes,
                    "current_streak": current_streak,
                    "average_score": average_score
                },
                "concept_progress": concept_progress,
                "path_progress": path_progress
            }
            
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_learning_streak(self, user_internal_id: int) -> int:
        """
        Calculate the current learning streak for a user
        
        A streak is counted as consecutive days with at least one learning session
        """
        try:
            session = self._get_or_create_session()
            
            # Get the date of the last learning session
            last_session = session.query(LearningSession).filter(
                LearningSession.user_id == user_internal_id
            ).order_by(LearningSession.start_time.desc()).first()
            
            if not last_session:
                return 0
            
            # Get all session dates (date only, no time)
            sessions = session.query(
                func.date(LearningSession.start_time).label('session_date')
            ).filter(
                LearningSession.user_id == user_internal_id
            ).distinct().all()
            
            session_dates = [s.session_date for s in sessions]
            
            if not session_dates:
                return 0
            
            # Sort dates and find streak
            session_dates.sort(reverse=True)
            today = datetime.now(timezone.utc).date()
            yesterday = today - timedelta(days=1)
            
            # Check if the most recent session is today or yesterday
            most_recent = session_dates[0]
            if most_recent < yesterday:
                return 0
            
            # Calculate consecutive days
            streak = 1
            for i in range(1, len(session_dates)):
                expected_date = most_recent - timedelta(days=i)
                if expected_date in session_dates:
                    streak += 1
                else:
                    break
            
            return streak
            
        except Exception as e:
            print(f"Error calculating streak: {e}")
            return 0
    
    # =============================================================================
    # Learning Analytics
    # =============================================================================
    
    def get_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive learning analytics for a user
        
        Returns:
            Dictionary containing:
            - modules_completed: Number of completed modules/concepts
            - total_study_time: Total study time in minutes
            - average_score: Average quiz score
            - engagement_score: Calculated engagement score (0-100)
            - knowledge_retention: Estimated retention percentage
            - learning_velocity: Learning speed assessment
            - recommendations: Personalized recommendations
            - strengths: User's learning strengths
            - areas_for_improvement: Areas needing improvement
        """
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get basic metrics
            progress_data = self.get_user_progress(user_id)
            if not progress_data.get("success"):
                return progress_data
            
            basic_metrics = progress_data["progress"]
            
            # Get learning sessions for time analysis
            sessions = session.query(LearningSession).filter(
                LearningSession.user_id == user.id
            ).order_by(LearningSession.start_time.desc()).limit(30).all()
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(user.id, sessions)
            
            # Calculate knowledge retention
            retention = self._calculate_knowledge_retention(user.id)
            
            # Determine learning velocity
            velocity = self._determine_learning_velocity(user.id, sessions)
            
            # Generate personalized recommendations
            recommendations = self._generate_recommendations(progress_data, retention)
            
            # Identify strengths and areas for improvement
            strengths, areas_for_improvement = self._analyze_strengths_weaknesses(
                user.id, progress_data, retention, engagement_score
            )
            
            return {
                "success": True,
                "learning_analytics": {
                    "modules_completed": basic_metrics["concepts_completed"],
                    "total_study_time": basic_metrics["total_study_time"],
                    "average_score": basic_metrics["average_score"],
                    "engagement_score": engagement_score,
                    "knowledge_retention": retention,
                    "learning_velocity": velocity,
                    "total_sessions": len(sessions),
                    "current_streak": basic_metrics["current_streak"]
                },
                "recommendations": recommendations,
                "strengths": strengths,
                "areas_for_improvement": areas_for_improvement,
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
        except Exception as e:
            print(f"Error getting learning analytics: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_engagement_score(self, user_internal_id: int, sessions: List[LearningSession]) -> int:
        """
        Calculate an engagement score (0-100) based on:
        - Session frequency
        - Session duration
        - Consistency (streak)
        """
        try:
            if not sessions:
                return 0
            
            today = datetime.now(timezone.utc).date()
            
            # Score based on session frequency (last 30 days)
            recent_sessions = [s for s in sessions if s.start_time.date() >= today - timedelta(days=30)]
            frequency_score = min(100, len(recent_sessions) * 10)  # Max 10 sessions for full score
            
            # Score based on average session duration
            durations = [s.duration_seconds for s in sessions if s.duration_seconds]
            if durations:
                avg_duration = sum(durations) / len(durations)
                duration_score = min(100, (avg_duration / 1800) * 50)  # 30 min = full 50 points
            else:
                duration_score = 0
            
            # Score based on streak
            streak = self._calculate_learning_streak(user_internal_id)
            streak_score = min(100, streak * 10)  # 10-day streak = full score
            
            # Weighted total
            total_score = (frequency_score * 0.3) + (duration_score * 0.35) + (streak_score * 0.35)
            
            return min(100, round(total_score))
            
        except Exception as e:
            print(f"Error calculating engagement score: {e}")
            return 0
    
    def _calculate_knowledge_retention(self, user_internal_id: int) -> int:
        """
        Estimate knowledge retention percentage based on:
        - Quiz performance trends
        - Time since last review
        """
        try:
            session = self._get_or_create_session()
            
            # Get recent quiz attempts
            attempts = session.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_internal_id
            ).order_by(QuizAttempt.completed_at.desc()).limit(20).all()
            
            if not attempts:
                return 50  # Default neutral score
            
            # Calculate average score
            scores = [a.score for a in attempts if a.score is not None]
            if not scores:
                return 50
            
            avg_score = sum(scores) / len(scores)
            
            # Check for improvement trend
            if len(scores) >= 4:
                recent_avg = sum(scores[:4]) / 4
                older_avg = sum(scores[4:]) / len(scores[4:])
                if recent_avg > older_avg + 5:
                    # Improving - bonus retention
                    retention = min(100, avg_score + 10)
                elif recent_avg < older_avg - 5:
                    # Declining - penalty
                    retention = max(0, avg_score - 10)
                else:
                    retention = avg_score
            else:
                retention = avg_score
            
            return round(retention)
            
        except Exception as e:
            print(f"Error calculating retention: {e}")
            return 50
    
    def _determine_learning_velocity(self, user_internal_id: int, sessions: List[LearningSession]) -> str:
        """
        Determine learning velocity: Slow, Moderate, Fast, or Accelerated
        Based on session frequency and duration over the last 30 days
        """
        try:
            if not sessions:
                return "Not Started"
            
            today = datetime.now(timezone.utc).date()
            recent_sessions = [s for s in sessions if s.start_time.date() >= today - timedelta(days=30)]
            
            if not recent_sessions:
                return "Slow"
            
            # Calculate average weekly sessions
            weeks = 4  # Last 30 days
            avg_weekly = len(recent_sessions) / weeks
            
            # Calculate average session duration
            durations = [s.duration_seconds for s in recent_sessions if s.duration_seconds]
            avg_duration = sum(durations) / len(durations) if durations else 0
            avg_minutes = avg_duration / 60
            
            # Determine velocity
            if avg_weekly >= 5 and avg_minutes >= 30:
                return "Accelerated"
            elif avg_weekly >= 3 and avg_minutes >= 20:
                return "Fast"
            elif avg_weekly >= 1.5 and avg_minutes >= 15:
                return "Moderate"
            else:
                return "Slow"
                
        except Exception as e:
            print(f"Error determining velocity: {e}")
            return "Moderate"
    
    def _generate_recommendations(self, progress_data: Dict, retention: int) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        progress = progress_data.get("progress", {})
        streak = progress.get("current_streak", 0)
        avg_score = progress.get("average_score", 0)
        concepts_completed = progress.get("concepts_completed", 0)
        
        if streak < 3:
            recommendations.append("Try to maintain a daily learning streak for better retention")
        elif streak >= 7:
            recommendations.append("Great job on your learning streak! Keep it up!")
        
        if avg_score < 70:
            recommendations.append("Consider reviewing the material before retaking quizzes")
        elif avg_score >= 90:
            recommendations.append("Excellent quiz scores! You might be ready for advanced topics")
        
        if concepts_completed < 5:
            recommendations.append("Complete more concepts to build a strong foundation")
        elif concepts_completed >= 20:
            recommendations.append("You've mastered many concepts! Consider starting a new learning path")
        
        if retention < 60:
            recommendations.append("Review previously completed material to improve retention")
        
        recommendations.append("Explore the AI generator for deeper explanations of complex topics")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _analyze_strengths_weaknesses(
        self, 
        user_internal_id: int, 
        progress_data: Dict, 
        retention: int,
        engagement: int
    ) -> Tuple[List[str], List[str]]:
        """Analyze user's learning strengths and areas for improvement"""
        strengths = []
        weaknesses = []
        
        progress = progress_data.get("progress", {})
        streak = progress.get("current_streak", 0)
        avg_score = progress.get("average_score", 0)
        
        if streak >= 5:
            strengths.append("Consistent learning habits")
        if streak < 2:
            weaknesses.append("Need to improve learning consistency")
        
        if avg_score >= 85:
            strengths.append("Strong quiz performance")
        elif avg_score < 60:
            weaknesses.append("Quiz scores need improvement")
        
        if engagement >= 70:
            strengths.append("High engagement with learning content")
        elif engagement < 40:
            weaknesses.append("Low engagement with learning content")
        
        if retention >= 80:
            strengths.append("Excellent knowledge retention")
        elif retention < 50:
            weaknesses.append("Knowledge retention could be improved")
        
        return strengths, weaknesses
    
    # =============================================================================
    # Courses / Learning Paths
    # =============================================================================
    
    def get_courses(self, user_id: str = "") -> Dict[str, Any]:
        """
        Get all available courses (learning paths)
        
        Args:
            user_id: Optional user ID to include progress data
            
        Returns:
            Dictionary containing list of courses with optional progress info
        """
        try:
            session = self._get_or_create_session()
            
            # Get all published learning paths (excluding soft-deleted)
            paths = session.query(LearningPath).filter(
                and_(
                    LearningPath.is_published == True,
                    LearningPath.is_deleted == False
                )
            ).all()
            
            courses = []
            for path in paths:
                # Get concept count
                concept_count = session.query(func.count(LearningPathConcept.id)).filter(
                    LearningPathConcept.path_id == path.path_id
                ).scalar() or 0
                
                # Get lesson count
                lesson_count = session.query(func.count(Lesson.lesson_id)).filter(
                    Lesson.learning_path_id == path.path_id
                ).scalar() or 0
                
                # Get user progress if user_id provided
                user_progress = None
                enrolled = False
                if user_id:
                    user = self.get_user_by_id(user_id)
                    if user:
                        enrollment = session.query(UserLearningPath).filter(
                            and_(
                                UserLearningPath.user_id == user.id,
                                UserLearningPath.path_id == path.path_id
                            )
                        ).first()
                        
                        if enrollment:
                            enrolled = True
                            user_progress = round(enrollment.progress_percent, 1)
                
                course_data = {
                    "course_id": path.path_id,
                    "title": path.title,
                    "description": path.description,
                    "domain": path.category or "General",
                    "difficulty": path.difficulty or "beginner",
                    "content_type": "interactive",
                    "estimated_duration": path.estimated_duration,
                    "concept_count": concept_count,
                    "lesson_count": lesson_count,
                    "is_enrolled": enrolled,
                    "progress": user_progress
                }
                courses.append(course_data)
            
            return {
                "success": True,
                "courses": courses,
                "total": len(courses)
            }
            
        except Exception as e:
            print(f"Error getting courses: {e}")
            return {"success": False, "error": str(e)}
    
    def get_course_details(self, course_id: str, user_id: str = "") -> Dict[str, Any]:
        """
        Get detailed information about a specific course (learning path)
        
        Args:
            course_id: The course/learning path ID
            user_id: Optional user ID to include user's progress and enrollment status
            
        Returns:
            Dictionary containing detailed course information
        """
        try:
            session = self._get_or_create_session()
            
            # Get the learning path
            path = session.query(LearningPath).filter(
                LearningPath.path_id == course_id
            ).first()
            
            if not path:
                return {"success": False, "error": "Course not found"}
            
            # Get concepts in this path
            path_concepts = session.query(LearningPathConcept).options(
                joinedload(LearningPathConcept.concept)
            ).filter(LearningPathConcept.path_id == course_id).all()
            
            concepts = []
            for pc in path_concepts:
                if pc.concept:
                    concepts.append({
                        "concept_id": pc.concept.concept_id,
                        "name": pc.concept.name,
                        "description": pc.concept.description,
                        "order_index": pc.order_index
                    })
            
            # Get lessons in this path
            lessons = session.query(Lesson).filter(
                Lesson.learning_path_id == course_id
            ).all()
            
            lesson_list = []
            for lesson in lessons:
                lesson_list.append({
                    "lesson_id": lesson.lesson_id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "order_index": lesson.order_index,
                    "duration_minutes": lesson.duration_minutes
                })
            
            # Get user's enrollment and progress if user_id provided
            user_enrollment = None
            user_progress_percent = 0
            is_enrolled = False
            
            if user_id:
                user = self.get_user_by_id(user_id)
                if user:
                    enrollment = session.query(UserLearningPath).filter(
                        and_(
                            UserLearningPath.user_id == user.id,
                            UserLearningPath.path_id == course_id
                        )
                    ).first()
                    
                    if enrollment:
                        is_enrolled = True
                        user_progress_percent = round(enrollment.progress_percent, 1)
                        user_enrollment = {
                            "enrolled_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
                            "last_accessed": enrollment.last_accessed.isoformat() if enrollment.last_accessed else None,
                            "progress_percent": user_progress_percent
                        }
            
            return {
                "success": True,
                "course": {
                    "course_id": path.path_id,
                    "title": path.title,
                    "description": path.description,
                    "category": path.category,
                    "difficulty": path.difficulty,
                    "estimated_duration": path.estimated_duration,
                    "is_published": path.is_published,
                    "created_at": path.created_at.isoformat() if path.created_at else None,
                    "updated_at": path.updated_at.isoformat() if path.updated_at else None,
                    "concepts": concepts,
                    "lessons": lesson_list,
                    "concept_count": len(concepts),
                    "lesson_count": len(lesson_list),
                    "is_enrolled": is_enrolled,
                    "progress": user_progress_percent,
                    "enrollment": user_enrollment
                }
            }
            
        except Exception as e:
            print(f"Error getting course details: {e}")
            return {"success": False, "error": str(e)}
    
    def enroll_in_course(self, user_id: str, course_id: str) -> Dict[str, Any]:
        """Enroll user in a course (learning path)"""
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check if course exists
            path = session.query(LearningPath).filter(
                LearningPath.path_id == course_id
            ).first()
            
            if not path:
                return {"success": False, "error": "Course not found"}
            
            # Check if already enrolled
            existing = session.query(UserLearningPath).filter(
                and_(
                    UserLearningPath.user_id == user.id,
                    UserLearningPath.path_id == course_id
                )
            ).first()
            
            if existing:
                return {
                    "success": True,
                    "message": "Already enrolled in this course",
                    "progress": round(existing.progress_percent, 1)
                }
            
            # Create enrollment
            enrollment = UserLearningPath(
                user_id=user.id,
                path_id=course_id,
                progress_percent=0.0,
                started_at=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc)
            )
            
            session.add(enrollment)
            session.commit()
            
            return {
                "success": True,
                "message": "Successfully enrolled in course",
                "course_id": course_id
            }

        except Exception as e:
            print(f"Error enrolling in course: {e}")
            session.rollback()
            return {"success": False, "error": str(e)}
    
    # =============================================================================
    # Learning Paths (Database-backed)
    # =============================================================================
    
    def get_learning_paths(self, user_id: str = "") -> Dict[str, Any]:
        """
        Get all available learning paths with detailed information
        
        Args:
            user_id: Optional user ID to include enrollment and progress data
            
        Returns:
            Dictionary containing list of learning paths with progress info
        """
        try:
            session = self._get_or_create_session()
            
            # Get all published learning paths (excluding soft-deleted)
            paths = session.query(LearningPath).filter(
                and_(
                    LearningPath.is_published == True,
                    LearningPath.is_deleted == False
                )
            ).all()
            
            learning_paths = []
            for path in paths:
                # Get concepts in this path
                path_concepts = session.query(LearningPathConcept).options(
                    joinedload(LearningPathConcept.concept)
                ).filter(LearningPathConcept.path_id == path.path_id).all()
                
                concepts = []
                for pc in path_concepts:
                    if pc.concept:
                        concepts.append(pc.concept.concept_id)
                
                # Get lessons in this path
                lessons = session.query(Lesson).filter(
                    Lesson.learning_path_id == path.path_id
                ).all()
                
                # Build modules from lessons
                modules = []
                for idx, lesson in enumerate(lessons):
                    modules.append({
                        "id": lesson.lesson_id,
                        "title": lesson.title,
                        "type": "lesson",
                        "duration": f"{lesson.duration_minutes or 30} minutes" if lesson.duration_minutes else "30 minutes",
                        "completed": False
                    })
                
                # Get user enrollment and progress if user_id provided
                user_progress = None
                enrolled = False
                completed_modules = 0
                
                if user_id:
                    user = self.get_user_by_id(user_id)
                    if user:
                        enrollment = session.query(UserLearningPath).filter(
                            and_(
                                UserLearningPath.user_id == user.id,
                                UserLearningPath.path_id == path.path_id
                            )
                        ).first()
                        
                        if enrollment:
                            enrolled = True
                            user_progress = round(enrollment.progress_percent, 1)
                            completed_modules = int((user_progress / 100) * len(modules)) if modules else 0
                
                # Parse prerequisites if stored as JSON string
                prereqs = []
                if path.prerequisites:
                    if isinstance(path.prerequisites, str):
                        try:
                            prereqs = json.loads(path.prerequisites)
                        except:
                            prereqs = []
                    else:
                        prereqs = path.prerequisites
                
                # Get learning outcomes if available
                skills = []
                if path.learning_outcomes:
                    if isinstance(path.learning_outcomes, str):
                        try:
                            skills = json.loads(path.learning_outcomes)
                        except:
                            skills = []
                    else:
                        skills = path.learning_outcomes
                
                path_data = {
                    "id": path.path_id,
                    "title": path.title,
                    "description": path.description or "",
                    "courses": [],
                    "modules": modules,
                    "concepts": concepts,
                    "skills_covered": skills,
                    "prerequisites": prereqs,
                    "total_modules": len(modules),
                    "completed_modules": completed_modules,
                    "duration": f"{path.estimated_duration or 8} weeks" if path.estimated_duration else "8 weeks",
                    "estimated_hours": path.estimated_duration or 20,
                    "difficulty": path.difficulty or "beginner",
                    "progress": user_progress or 0,
                    "icon": path.category or "book",
                    "category": path.category or "general",
                    "next_step": modules[0]["title"] if modules else "Start Learning",
                    "is_enrolled": enrolled
                }
                learning_paths.append(path_data)
            
            return {
                "success": True,
                "paths": learning_paths,
                "total": len(learning_paths)
            }
            
        except Exception as e:
            print(f"Error getting learning paths: {e}")
            return {"success": False, "error": str(e)}
    
    def get_learning_path_details(self, path_id: str, user_id: str = "") -> Dict[str, Any]:
        """
        Get detailed information about a specific learning path
        
        Args:
            path_id: The learning path ID
            user_id: Optional user ID to include enrollment and progress data
            
        Returns:
            Dictionary containing detailed learning path information
        """
        try:
            session = self._get_or_create_session()
            
            # Get the learning path
            path = session.query(LearningPath).filter(
                LearningPath.path_id == path_id
            ).first()
            
            if not path:
                return {"success": False, "error": "Learning path not found"}
            
            # Get concepts in this path
            path_concepts = session.query(LearningPathConcept).options(
                joinedload(LearningPathConcept.concept)
            ).filter(LearningPathConcept.path_id == path_id).all()
            
            concepts = []
            for pc in path_concepts:
                if pc.concept:
                    concepts.append({
                        "concept_id": pc.concept.concept_id,
                        "name": pc.concept.name,
                        "description": pc.concept.description,
                        "order_index": pc.sequence_order,
                        "is_required": pc.is_required
                    })
            
            # Get lessons in this path
            lessons = session.query(Lesson).filter(
                Lesson.learning_path_id == path_id
            ).all()
            
            modules = []
            for idx, lesson in enumerate(lessons):
                # Get concepts for this lesson
                lesson_concepts = session.query(LessonConcept).options(
                    joinedload(LessonConcept.concept)
                ).filter(LessonConcept.lesson_id == lesson.lesson_id).all()
                
                lesson_concept_list = []
                for lc in lesson_concepts:
                    if lc.concept:
                        lesson_concept_list.append(lc.concept.concept_id)
                
                modules.append({
                    "id": lesson.lesson_id,
                    "title": lesson.title,
                    "description": lesson.description or "",
                    "type": "lesson",
                    "duration": f"{lesson.duration_minutes or 30} minutes" if lesson.duration_minutes else "30 minutes",
                    "completed": False,
                    "order_index": lesson.order_index or idx,
                    "concepts": lesson_concept_list
                })
            
            # Get user enrollment and progress if user_id provided
            user_enrollment = None
            is_enrolled = False
            user_progress = 0
            
            if user_id:
                user = self.get_user_by_id(user_id)
                if user:
                    enrollment = session.query(UserLearningPath).filter(
                        and_(
                            UserLearningPath.user_id == user.id,
                            UserLearningPath.path_id == path_id
                        )
                    ).first()
                    
                    if enrollment:
                        is_enrolled = True
                        user_progress = round(enrollment.progress_percent, 1)
                        user_enrollment = {
                            "enrolled_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
                            "last_accessed": enrollment.last_accessed.isoformat() if enrollment.last_accessed else None,
                            "progress_percent": user_progress
                        }
            
            # Parse prerequisites
            prerequisites = []
            if path.prerequisites:
                if isinstance(path.prerequisites, str):
                    try:
                        prerequisites = json.loads(path.prerequisites)
                    except:
                        prerequisites = []
                else:
                    prerequisites = path.prerequisites
            
            # Get learning outcomes
            skills = []
            if path.learning_outcomes:
                if isinstance(path.learning_outcomes, str):
                    try:
                        skills = json.loads(path.learning_outcomes)
                    except:
                        skills = []
                else:
                    skills = path.learning_outcomes
            
            return {
                "success": True,
                "path": {
                    "id": path.path_id,
                    "title": path.title,
                    "description": path.description or "",
                    "category": path.category or "general",
                    "difficulty": path.difficulty or "beginner",
                    "estimated_duration": path.estimated_duration,
                    "target_audience": path.target_audience or "all",
                    "is_published": path.is_published,
                    "is_enrolled": is_enrolled,
                    "progress": user_progress,
                    "concepts": concepts,
                    "modules": sorted(modules, key=lambda x: x.get("order_index", 0)),
                    "prerequisites": prerequisites,
                    "skills_covered": skills,
                    "enrollment": user_enrollment,
                    "created_at": path.created_at.isoformat() if path.created_at else None,
                    "updated_at": path.updated_at.isoformat() if path.updated_at else None
                }
            }
            
        except Exception as e:
            print(f"Error getting learning path details: {e}")
            return {"success": False, "error": str(e)}
    
    def enroll_in_learning_path(self, user_id: str, path_id: str) -> Dict[str, Any]:
        """
        Enroll user in a learning path
        
        Args:
            user_id: User ID
            path_id: Learning path ID
            
        Returns:
            Dictionary containing enrollment result
        """
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check if learning path exists
            path = session.query(LearningPath).filter(
                LearningPath.path_id == path_id
            ).first()
            
            if not path:
                return {"success": False, "error": "Learning path not found"}
            
            # Check if already enrolled
            existing = session.query(UserLearningPath).filter(
                and_(
                    UserLearningPath.user_id == user.id,
                    UserLearningPath.path_id == path_id
                )
            ).first()
            
            if existing:
                return {
                    "success": True,
                    "message": "Already enrolled in this learning path",
                    "progress": round(existing.progress_percent, 1)
                }
            
            # Create enrollment
            enrollment = UserLearningPath(
                user_id=user.id,
                path_id=path_id,
                progress_percent=0.0,
                started_at=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc)
            )
            
            session.add(enrollment)
            session.commit()
            
            return {
                "success": True,
                "message": f"Successfully enrolled in learning path: {path.title}",
                "path_id": path_id,
                "path_title": path.title
            }
            
        except Exception as e:
            print(f"Error enrolling in learning path: {e}")
            session.rollback()
            return {"success": False, "error": str(e)}
    
    # =============================================================================
    # Achievements
    # =============================================================================
    
    def get_achievements(self, user_id: str) -> Dict[str, Any]:
        """
        Get all achievements and user's earned achievements
        
        Returns:
            Dictionary containing:
            - all_achievements: List of all achievements with earned status
            - earned_count: Number of achievements earned
            - total_points: Total points earned
        """
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get all active achievements (excluding soft-deleted)
            all_achievements = session.query(Achievement).filter(
                and_(
                    Achievement.is_active == True,
                    Achievement.is_deleted == False
                )
            ).all()
            
            # Get user's earned achievements
            earned = session.query(UserAchievement).options(
                joinedload(UserAchievement.achievement)
            ).filter(UserAchievement.user_id == user.id).all()
            
            earned_ids = {ua.achievement_id for ua in earned}
            earned_points = sum(ua.achievement.points for ua in earned if ua.achievement)
            
            # Build achievement list with earned status
            achievements_list = []
            for achievement in all_achievements:
                is_earned = achievement.achievement_id in earned_ids
                
                # Find when it was earned
                earned_at = None
                if is_earned:
                    user_achievement = next(
                        (ua for ua in earned if ua.achievement_id == achievement.achievement_id),
                        None
                    )
                    if user_achievement:
                        earned_at = user_achievement.earned_at.isoformat() if user_achievement.earned_at else None
                
                achievements_list.append({
                    "id": achievement.achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon or "award",
                    "earned": is_earned,
                    "earned_at": earned_at,
                    "requirement": f"{achievement.criteria_value} {achievement.criteria_type.replace('_', ' ')}",
                    "category": achievement.criteria_type,
                    "tier": achievement.tier,
                    "points": achievement.points
                })
            
            return {
                "success": True,
                "achievements": achievements_list,
                "total": len(achievements_list),
                "earned_count": len(earned),
                "total_points": earned_points
            }
            
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return {"success": False, "error": str(e)}
    
    def get_badges(self, user_id: str) -> Dict[str, Any]:
        """Get all badges for a user"""
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get all active badges (excluding soft-deleted)
            all_badges = session.query(Badge).filter(
                and_(
                    Badge.is_active == True,
                    Badge.is_deleted == False
                )
            ).all()
            
            # Get user's earned badges
            earned = session.query(UserBadge).options(
                joinedload(UserBadge.badge)
            ).filter(UserBadge.user_id == user.id).all()
            
            earned_ids = {ub.badge_id for ub in earned}
            
            badges_list = []
            for badge in all_badges:
                is_earned = badge.badge_id in earned_ids
                
                earned_at = None
                if is_earned:
                    user_badge = next(
                        (ub for ub in earned if ub.badge_id == badge.badge_id),
                        None
                    )
                    if user_badge:
                        earned_at = user_badge.earned_at.isoformat() if user_badge.earned_at else None
                
                badges_list.append({
                    "badge_id": badge.badge_id,
                    "name": badge.name,
                    "description": badge.description,
                    "image_url": badge.image_url,
                    "earned": is_earned,
                    "earned_at": earned_at,
                    "tier": badge.tier,
                    "points": badge.points
                })
            
            return {
                "success": True,
                "badges": badges_list,
                "total": len(badges_list),
                "earned_count": len(earned)
            }
            
        except Exception as e:
            print(f"Error getting badges: {e}")
            return {"success": False, "error": str(e)}
    
    def check_and_award_achievements(self, user_id: str) -> Dict[str, Any]:
        """
        Check and award achievements based on user progress
        
        This should be called after completing lessons, quizzes, etc.
        """
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get user's current progress
            progress_data = self.get_user_progress(user_id)
            if not progress_data.get("success"):
                return progress_data
            
            # Get all achievements
            achievements = session.query(Achievement).filter(
                Achievement.is_active == True
            ).all()
            
            # Get already earned achievements
            earned_ids = {ua.achievement_id for ua in user.achievements}
            
            newly_earned = []
            
            for achievement in achievements:
                if achievement.achievement_id in earned_ids:
                    continue
                
                should_award = False
                
                # Check based on criteria type
                if achievement.criteria_type == "concepts_completed":
                    completed = progress_data["progress"]["concepts_completed"]
                    should_award = completed >= achievement.criteria_value
                    
                elif achievement.criteria_type == "quizzes_passed":
                    passed = session.query(func.count(QuizAttempt.id)).filter(
                        and_(
                            QuizAttempt.user_id == user.id,
                            QuizAttempt.is_passed == True
                        )
                    ).scalar() or 0
                    should_award = passed >= achievement.criteria_value
                    
                elif achievement.criteria_type == "streak_days":
                    streak = self._calculate_learning_streak(user.id)
                    should_award = streak >= achievement.criteria_value
                
                if should_award:
                    # Award the achievement
                    user_achievement = UserAchievement(
                        user_id=user.id,
                        achievement_id=achievement.achievement_id,
                        earned_at=datetime.now(timezone.utc)
                    )
                    session.add(user_achievement)
                    newly_earned.append(achievement.name)
            
            session.commit()
            
            return {
                "success": True,
                "new_achievements": newly_earned,
                "count": len(newly_earned)
            }
            
        except Exception as e:
            print(f"Error checking achievements: {e}")
            session.rollback()
            return {"success": False, "error": str(e)}
    
    # =============================================================================
    # Quizzes
    # =============================================================================
    
    def get_quizzes(self, user_id: str = "") -> Dict[str, Any]:
        """
        Get all available quizzes
        
        Args:
            user_id: Optional user ID to include user's attempts
            
        Returns:
            Dictionary containing list of quizzes with attempt info
        """
        try:
            session = self._get_or_create_session()
            
            # Get all published quizzes (excluding soft-deleted)
            quizzes = session.query(Quiz).filter(
                and_(
                    Quiz.is_published == True,
                    Quiz.is_deleted == False
                )
            ).all()
            
            # Get user's attempts if user_id provided
            user_attempts = {}
            if user_id:
                user = self.get_user_by_id(user_id)
                if user:
                    attempts = session.query(QuizAttempt).filter(
                        QuizAttempt.user_id == user.id
                    ).all()
                    for attempt in attempts:
                        if attempt.quiz_id not in user_attempts:
                            user_attempts[attempt.quiz_id] = []
                        user_attempts[attempt.quiz_id].append({
                            "attempt_id": attempt.attempt_id,
                            "score": attempt.score,
                            "is_passed": attempt.is_passed,
                            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
                        })
            
            quiz_list = []
            for quiz in quizzes:
                attempts = user_attempts.get(quiz.quiz_id, [])
                best_score = None
                completed = False
                if attempts:
                    scores = [a["score"] for a in attempts if a["score"] is not None]
                    if scores:
                        best_score = max(scores)
                    completed = any(a["is_passed"] for a in attempts)
                
                quiz_data = {
                    "id": quiz.quiz_id,
                    "title": quiz.title,
                    "description": quiz.description,
                    "concept_id": quiz.concept_id,
                    "lesson_id": quiz.lesson_id,
                    "passing_score": quiz.passing_score,
                    "time_limit_minutes": quiz.time_limit_minutes,
                    "max_attempts": quiz.max_attempts,
                    "completed": completed,
                    "best_score": best_score,
                    "attempts_count": len(attempts),
                    "recent_attempts": attempts[:3]
                }
                quiz_list.append(quiz_data)
            
            return {
                "success": True,
                "quizzes": quiz_list,
                "total": len(quiz_list)
            }
            
        except Exception as e:
            print(f"Error getting quizzes: {e}")
            return {"success": False, "error": str(e)}
    
    def get_quiz_by_id(self, quiz_id: str) -> Dict[str, Any]:
        """Get quiz details by ID"""
        try:
            session = self._get_or_create_session()
            
            quiz = session.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
            
            if not quiz:
                return {"success": False, "error": "Quiz not found"}
            
            return {
                "success": True,
                "quiz": {
                    "id": quiz.quiz_id,
                    "title": quiz.title,
                    "description": quiz.description,
                    "concept_id": quiz.concept_id,
                    "lesson_id": quiz.lesson_id,
                    "passing_score": quiz.passing_score,
                    "time_limit_minutes": quiz.time_limit_minutes,
                    "max_attempts": quiz.max_attempts
                }
            }
            
        except Exception as e:
            print(f"Error getting quiz: {e}")
            return {"success": False, "error": str(e)}
    
    def submit_quiz_attempt(
        self, 
        user_id: str, 
        quiz_id: str, 
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a quiz attempt and calculate score
        
        Args:
            user_id: User ID string
            quiz_id: Quiz ID
            answers: Dictionary of question IDs to answers
            
        Returns:
            Dictionary containing score, passed status, and feedback
        """
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            quiz = session.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
            
            if not quiz:
                return {"success": False, "error": "Quiz not found"}
            
            # Check attempt count
            attempt_count = session.query(func.count(QuizAttempt.attempt_id)).filter(
                and_(
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.quiz_id == quiz_id
                )
            ).scalar() or 0
            
            if attempt_count >= quiz.max_attempts:
                return {"success": False, "error": "Maximum attempts reached"}
            
            # Calculate score (simplified - in production, this would check against correct answers)
            total_questions = len(answers)
            correct_answers = 0
            
            # In a real implementation, you'd check against stored correct answers
            # For now, we simulate a reasonable score
            if total_questions > 0:
                # Simulate scoring based on answer quality
                score = 75 + (hash(str(answers)) % 25)  # Random score between 75-99
                correct_answers = int((score / 100) * total_questions)
            else:
                score = 0
            
            is_passed = score >= quiz.passing_score
            
            # Record the attempt
            attempt = QuizAttempt(
                user_id=user.id,
                quiz_id=quiz_id,
                concept_id=quiz.concept_id,
                score=score,
                total_questions=total_questions,
                correct_answers=correct_answers,
                time_taken_seconds=None,  # Would be calculated from start time
                is_passed=is_passed,
                completed_at=datetime.now(timezone.utc),
                answers=json.dumps(answers)
            )
            
            session.add(attempt)
            session.commit()
            
            # Check and award achievements
            self.check_and_award_achievements(user_id)
            
            result_message = "Keep learning and try again!"
            if is_passed:
                result_message = "Congratulations! You passed!"
            
            return {
                "success": True,
                "quiz_id": quiz_id,
                "score": score,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "passed": is_passed,
                "message": result_message
            }
            
        except Exception as e:
            print(f"Error submitting quiz: {e}")
            session.rollback()
            return {"success": False, "error": str(e)}
    
    def get_quiz_attempts(self, user_id: str, quiz_id: str = "") -> Dict[str, Any]:
        """Get quiz attempts for a user"""
        try:
            session = self._get_or_create_session()
            user = self.get_user_by_id(user_id)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            query = session.query(QuizAttempt).options(
                joinedload(QuizAttempt.quiz)
            ).filter(QuizAttempt.user_id == user.id)
            
            if quiz_id:
                query = query.filter(QuizAttempt.quiz_id == quiz_id)
            
            attempts = query.order_by(QuizAttempt.completed_at.desc()).limit(50).all()
            
            attempt_list = []
            for attempt in attempts:
                attempt_list.append({
                    "attempt_id": attempt.attempt_id,
                    "quiz_id": attempt.quiz_id,
                    "quiz_title": attempt.quiz.title if attempt.quiz else None,
                    "score": attempt.score,
                    "total_questions": attempt.total_questions,
                    "correct_answers": attempt.correct_answers,
                    "is_passed": attempt.is_passed,
                    "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
                })
            
            return {
                "success": True,
                "attempts": attempt_list,
                "total": len(attempt_list)
            }
            
        except Exception as e:
            print(f"Error getting quiz attempts: {e}")
            return {"success": False, "error": str(e)}


# =============================================================================
# Module-level convenience functions
# =============================================================================

def get_user_progress(user_id: str) -> Dict[str, Any]:
    """Get user progress"""
    store = UserDashboardStore()
    try:
        return store.get_user_progress(user_id)
    finally:
        store.close()

def get_learning_analytics(user_id: str) -> Dict[str, Any]:
    """Get learning analytics"""
    store = UserDashboardStore()
    try:
        return store.get_learning_analytics(user_id)
    finally:
        store.close()

def get_courses(user_id: str = "") -> Dict[str, Any]:
    """Get all courses"""
    store = UserDashboardStore()
    try:
        return store.get_courses(user_id)
    finally:
        store.close()

def get_course_details(course_id: str, user_id: str = "") -> Dict[str, Any]:
    """Get course details"""
    store = UserDashboardStore()
    try:
        return store.get_course_details(course_id, user_id)
    finally:
        store.close()

def enroll_in_course(user_id: str, course_id: str) -> Dict[str, Any]:
    """Enroll in a course"""
    store = UserDashboardStore()
    try:
        return store.enroll_in_course(user_id, course_id)
    finally:
        store.close()

def get_learning_paths(user_id: str = "") -> Dict[str, Any]:
    """Get all learning paths"""
    store = UserDashboardStore()
    try:
        return store.get_learning_paths(user_id)
    finally:
        store.close()

def get_learning_path_details(path_id: str, user_id: str = "") -> Dict[str, Any]:
    """Get learning path details"""
    store = UserDashboardStore()
    try:
        return store.get_learning_path_details(path_id, user_id)
    finally:
        store.close()

def enroll_in_learning_path(user_id: str, path_id: str) -> Dict[str, Any]:
    """Enroll in a learning path"""
    store = UserDashboardStore()
    try:
        return store.enroll_in_learning_path(user_id, path_id)
    finally:
        store.close()

def get_achievements(user_id: str) -> Dict[str, Any]:
    """Get achievements"""
    store = UserDashboardStore()
    try:
        return store.get_achievements(user_id)
    finally:
        store.close()

def get_badges(user_id: str) -> Dict[str, Any]:
    """Get badges"""
    store = UserDashboardStore()
    try:
        return store.get_badges(user_id)
    finally:
        store.close()

def get_quizzes(user_id: str = "") -> Dict[str, Any]:
    """Get quizzes"""
    store = UserDashboardStore()
    try:
        return store.get_quizzes(user_id)
    finally:
        store.close()

def submit_quiz_attempt(user_id: str, quiz_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
    """Submit quiz attempt"""
    store = UserDashboardStore()
    try:
        return store.submit_quiz_attempt(user_id, quiz_id, answers)
    finally:
        store.close()

def get_quiz_attempts(user_id: str, quiz_id: str = "") -> Dict[str, Any]:
    """Get quiz attempts"""
    store = UserDashboardStore()
    try:
        return store.get_quiz_attempts(user_id, quiz_id)
    finally:
        store.close()
