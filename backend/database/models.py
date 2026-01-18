"""
SQLAlchemy ORM Models for Jeseci Smart Learning Academy

This module defines all database tables as SQLAlchemy models using the
Declarative Base pattern. All models use SQLAlchemy 2.0 type hints
for better type safety and IDE support.

Comprehensive schema including:
- User Management: User, UserProfile, UserLearningPreference
- Learning Content: Concept, ConceptContent, ConceptRelation, LearningPath, Lesson
- Progress Tracking: UserConceptProgress, UserLearningPath, UserLessonProgress, LearningSession
- Assessment: Quiz, QuizAttempt
- Gamification: Achievement, UserAchievement, Badge, UserBadge
- System: SystemLog, SystemHealth, AIAgent
"""

from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, ForeignKey, 
    UniqueConstraint, Index, Float, JSON, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.config.database import Base

# =============================================================================
# Association Tables for Many-to-Many Relationships
# =============================================================================

# Concept-to-Concept self-referential relationship (prerequisites, related topics)
concept_relations = Table(
    "concept_relations",
    Base.metadata,
    Column("source_concept_id", String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"), primary_key=True),
    Column("target_concept_id", String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"), primary_key=True),
    Column("relation_type", String(50), default="related"),  # prerequisite, related, builds_on
    schema="jeseci_academy",
)




# =============================================================================
# User Domain Models
# =============================================================================

class User(Base):
    """Core User model for authentication and tracking
    
    This model only contains authentication and core tracking fields.
    Extended user information is stored in UserProfile.
    Learning preferences are stored in UserLearningPreference.
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "jeseci_academy"}
    
    # Primary key (internal technical ID)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # External business identifier (VARCHAR - e.g., "user_admin_abc123")
    user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    
    # Core authentication fields
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Status and roles
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    admin_role: Mapped[str] = mapped_column(String(50), default='student')
    
    # Email verification
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships - One-to-One (extended data)
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    preferences: Mapped[Optional["UserLearningPreference"]] = relationship(
        "UserLearningPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    
    # Learning Progress Relationships
    concept_progress: Mapped[List["UserConceptProgress"]] = relationship(
        "UserConceptProgress", back_populates="user", cascade="all, delete-orphan"
    )
    learning_paths: Mapped[List["UserLearningPath"]] = relationship(
        "UserLearningPath", back_populates="user", cascade="all, delete-orphan"
    )
    lesson_progress: Mapped[List["UserLessonProgress"]] = relationship(
        "UserLessonProgress", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["LearningSession"]] = relationship(
        "LearningSession", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Assessment & Gamification
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )
    badges: Mapped[List["UserBadge"]] = relationship(
        "UserBadge", back_populates="user", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"


class UserProfile(Base):
    """Extended user profile information (1:1 with User)"""
    __tablename__ = "user_profile"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # External URL
    profile_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Local file path
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, name='{self.first_name} {self.last_name}')>"


class UserLearningPreference(Base):
    """User learning preferences and settings (1:1 with User)"""
    __tablename__ = "user_learning_preferences"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), unique=True)
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=30)
    preferred_difficulty: Mapped[str] = mapped_column(String(20), default="intermediate")  # beginner, intermediate, advanced
    preferred_content_type: Mapped[str] = mapped_column(String(50), default="text")  # text, video, interactive
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_play_videos: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="preferences")
    
    def __repr__(self) -> str:
        return f"<UserLearningPreference(user_id={self.user_id}, goal={self.daily_goal_minutes}min)>"


# =============================================================================
# Content Domain Models
# =============================================================================

class Concept(Base):
    """Learning Concept model representing topics in the curriculum"""
    __tablename__ = "concepts"
    __table_args__ = {"schema": "jeseci_academy"}
    
    concept_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detailed_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    complexity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cognitive_load: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_time_minutes: Mapped[int] = mapped_column(Integer, default=15)
    key_terms: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of key terms
    synonyms: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of synonyms
    prerequisites: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of prerequisite concept IDs
    learning_outcomes: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of learning outcomes
    tags: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of tags
    icon: Mapped[str] = mapped_column(String(100), default='default')
    version: Mapped[int] = mapped_column(Integer, default=1)
    content_version: Mapped[int] = mapped_column(Integer, default=1)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    author_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    author_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seo_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='published')
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    lesson_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lesson_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    contents: Mapped[List["ConceptContent"]] = relationship(
        "ConceptContent", back_populates="concept", cascade="all, delete-orphan"
    )
    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz", back_populates="concept", cascade="all, delete-orphan"
    )
    learning_path_concepts: Mapped[List["LearningPathConcept"]] = relationship(
        "LearningPathConcept", back_populates="concept"
    )
    lesson_concepts: Mapped[List["LessonConcept"]] = relationship(
        "LessonConcept", back_populates="concept"
    )
    user_progress: Mapped[List["UserConceptProgress"]] = relationship(
        "UserConceptProgress", back_populates="concept"
    )
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="concept"
    )
    
    # Self-referential Many-to-Many relationships
    prerequisites: Mapped[List["Concept"]] = relationship(
        "Concept",
        secondary=concept_relations,
        primaryjoin=concept_id == concept_relations.c.source_concept_id,
        secondaryjoin=concept_id == concept_relations.c.target_concept_id,
        backref="dependents",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Concept(concept_id='{self.concept_id}', name='{self.name}')>"


class ConceptContent(Base):
    """Content blocks associated with a concept (1:N relationship)"""
    __tablename__ = "concept_content"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    concept_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"))
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # text, video, image, code, interactive
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Markdown or HTML content
    media_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    media_alt: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationship
    concept: Mapped["Concept"] = relationship("Concept", back_populates="contents")
    
    def __repr__(self) -> str:
        return f"<ConceptContent(id={self.id}, concept_id='{self.concept_id}', type='{self.content_type}')>"


class LearningPath(Base):
    """Learning Path model for organizing concepts into structured courses"""
    __tablename__ = "learning_paths"
    __table_args__ = {"schema": "jeseci_academy"}
    
    path_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in minutes
    target_audience: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prerequisites: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of prerequisite path names
    learning_outcomes: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of learning outcomes
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships - access concepts through LearningPathConcept association objects
    path_concepts: Mapped[List["LearningPathConcept"]] = relationship(
        "LearningPathConcept", back_populates="learning_path", cascade="all, delete-orphan"
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson", back_populates="learning_path", cascade="all, delete-orphan"
    )
    user_learning_paths: Mapped[List["UserLearningPath"]] = relationship(
        "UserLearningPath", back_populates="learning_path"
    )
    
    def __repr__(self) -> str:
        return f"<LearningPath(path_id='{self.path_id}', title='{self.title}')>"


class Lesson(Base):
    """Lesson model for organizing content within a learning path"""
    __tablename__ = "lessons"
    __table_args__ = {"schema": "jeseci_academy"}
    
    lesson_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    learning_path_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.learning_paths.path_id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in minutes
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships - access concepts through LessonConcept association objects
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="lessons")
    lesson_concepts: Mapped[List["LessonConcept"]] = relationship(
        "LessonConcept", back_populates="lesson", cascade="all, delete-orphan"
    )
    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz", back_populates="lesson", cascade="all, delete-orphan"
    )
    user_progress: Mapped[List["UserLessonProgress"]] = relationship(
        "UserLessonProgress", back_populates="lesson", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Lesson(lesson_id='{self.lesson_id}', title='{self.title}')>"


class LearningPathConcept(Base):
    """Association table for Learning Path - Concept many-to-many relationship"""
    __tablename__ = "learning_path_concepts"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.learning_paths.path_id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"))
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="path_concepts")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="learning_path_concepts")
    
    __table_args__ = (
        UniqueConstraint("path_id", "concept_id", name="uq_path_concept"),
        Index("idx_lpc_path_id", "path_id"),
        Index("idx_lpc_concept_id", "concept_id"),
    )
    
    def __repr__(self) -> str:
        return f"<LearningPathConcept(path_id='{self.path_id}', concept_id='{self.concept_id}')>"


class LessonConcept(Base):
    """Association table for Lesson - Concept many-to-many relationship"""
    __tablename__ = "lesson_concepts"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lesson_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.lessons.lesson_id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"))
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="lesson_concepts")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="lesson_concepts")
    
    __table_args__ = (
        UniqueConstraint("lesson_id", "concept_id", name="uq_lesson_concept"),
        Index("idx_lc_lesson_id", "lesson_id"),
        Index("idx_lc_concept_id", "concept_id"),
    )
    
    def __repr__(self) -> str:
        return f"<LessonConcept(lesson_id='{self.lesson_id}', concept_id='{self.concept_id}')>"


# =============================================================================
# Progress & Tracking Models
# =============================================================================

class UserConceptProgress(Base):
    """Tracks user progress through individual concepts"""
    __tablename__ = "user_concept_progress"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(100), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default='not_started')
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Extended progress tracking columns
    last_position: Mapped[int] = mapped_column(Integer, default=0)
    quiz_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quiz_attempts: Mapped[int] = mapped_column(Integer, default=0)
    quiz_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    time_spent_on_quiz: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_on_practice: Mapped[int] = mapped_column(Integer, default=0)
    mastery_level: Mapped[int] = mapped_column(Integer, default=0)
    mastery_progress: Mapped[int] = mapped_column(Integer, default=0)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_suggestions: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    difficulty_adjusted: Mapped[bool] = mapped_column(Boolean, default=False)
    recommended_difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    practice_exercises_completed: Mapped[int] = mapped_column(Integer, default=0)
    practice_correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    practice_wrong_answers: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="concept_progress")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="user_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_user_concept_progress"),
        Index("idx_ucp_user_id", "user_id"),
        Index("idx_ucp_concept_id", "concept_id"),
    )

    def __repr__(self) -> str:
        return f"<UserConceptProgress(user_id={self.user_id}, concept_id='{self.concept_id}', progress={self.progress_percent}%)>"


class UserLearningPath(Base):
    """Tracks user enrollment and progress in learning paths"""
    __tablename__ = "user_learning_paths"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    path_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.learning_paths.path_id", ondelete="CASCADE"))
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_paths")
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="user_learning_paths")
    
    __table_args__ = (
        UniqueConstraint("user_id", "path_id", name="uq_user_learning_path"),
        Index("idx_ulpath_user_id", "user_id"),
        Index("idx_ulpath_path_id", "path_id"),
    )
    
    def __repr__(self) -> str:
        return f"<UserLearningPath(user_id={self.user_id}, path_id='{self.path_id}', progress={self.progress_percent}%)>"


class UserLessonProgress(Base):
    """Tracks user progress through individual lessons"""
    __tablename__ = "user_lesson_progress"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    lesson_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.lessons.lesson_id", ondelete="CASCADE"))
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="lesson_progress")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="user_progress")
    
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
        Index("idx_ullp_user_id", "user_id"),
        Index("idx_ullp_lesson_id", "lesson_id"),
    )
    
    def __repr__(self) -> str:
        return f"<UserLessonProgress(user_id={self.user_id}, lesson_id='{self.lesson_id}', completed={self.is_completed})>"


class LearningSession(Base):
    """Tracks individual learning sessions"""
    __tablename__ = "learning_sessions"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    course_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    concept_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    path_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lesson_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    quiz_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    session_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    activities_completed: Mapped[int] = mapped_column(Integer, default=0)

    # Extended session tracking columns
    device_info: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    browser_info: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    platform: Mapped[str] = mapped_column(String(50), default='web')
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_events: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    meta_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    network_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    connection_speed: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    interactions_count: Mapped[int] = mapped_column(Integer, default=0)
    scroll_depth: Mapped[int] = mapped_column(Integer, default=0)
    focus_time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0)
    active_time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    idle_time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    progress_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    ai_insights: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("idx_ls_user_id", "user_id"),
        Index("idx_ls_start_time", "start_time"),
    )

    def __repr__(self) -> str:
        return f"<LearningSession(id={self.id}, session_id='{self.session_id}', user_id={self.user_id}, duration={self.duration_seconds}s)>"


# =============================================================================
# Assessment Models
# =============================================================================

class Quiz(Base):
    """Quiz model for assessments linked to concepts or lessons"""
    __tablename__ = "quizzes"
    __table_args__ = {"schema": "jeseci_academy"}
    
    quiz_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    concept_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="SET NULL"), nullable=True)
    lesson_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("jeseci_academy.lessons.lesson_id", ondelete="SET NULL"), nullable=True)
    passing_score: Mapped[int] = mapped_column(Integer, default=70)  # percentage
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    concept: Mapped[Optional["Concept"]] = relationship("Concept", back_populates="quizzes")
    lesson: Mapped[Optional["Lesson"]] = relationship("Lesson", back_populates="quizzes")
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="quiz", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Quiz(quiz_id='{self.quiz_id}', title='{self.title}')>"


class QuizAttempt(Base):
    """Records quiz attempts by users"""
    __tablename__ = "quiz_attempts"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    attempt_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    quiz_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.quizzes.quiz_id", ondelete="CASCADE"))
    concept_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="SET NULL"), nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=True)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    answers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON of user answers
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")
    concept: Mapped[Optional["Concept"]] = relationship("Concept", back_populates="quiz_attempts")
    
    __table_args__ = (
        Index("idx_qa_user_id", "user_id"),
        Index("idx_qa_quiz_id", "quiz_id"),
        Index("idx_qa_concept_id", "concept_id"),
    )
    
    def __repr__(self) -> str:
        return f"<QuizAttempt(attempt_id={self.attempt_id}, user_id={self.user_id}, score={self.score})>"


# =============================================================================
# Gamification Models
# =============================================================================

class Achievement(Base):
    """Achievement model for gamification milestones"""
    __tablename__ = "achievements"
    __table_args__ = {"schema": "jeseci_academy"}
    
    achievement_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)  # concepts_completed, quizzes_passed, streak_days
    criteria_value: Mapped[int] = mapped_column(Integer, default=1)
    points: Mapped[int] = mapped_column(Integer, default=10)
    tier: Mapped[str] = mapped_column(String(20), default="bronze")  # bronze, silver, gold, platinum
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    user_achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Achievement(achievement_id='{self.achievement_id}', name='{self.name}')>"


class UserAchievement(Base):
    """Tracks achievements earned by users"""
    __tablename__ = "user_achievements"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    achievement_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.achievements.achievement_id", ondelete="CASCADE"))
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
        Index("idx_ua_user_id", "user_id"),
        Index("idx_ua_achievement_id", "achievement_id"),
    )
    
    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id='{self.achievement_id}')>"


class Badge(Base):
    """Badge model for visual rewards"""
    __tablename__ = "badges"
    __table_args__ = {"schema": "jeseci_academy"}
    
    badge_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tier: Mapped[str] = mapped_column(String(20), default="bronze")  # bronze, silver, gold, platinum
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)
    criteria_value: Mapped[int] = mapped_column(Integer, default=1)
    points: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    user_badges: Mapped[List["UserBadge"]] = relationship(
        "UserBadge", back_populates="badge", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Badge(badge_id='{self.badge_id}', name='{self.name}')>"


class UserBadge(Base):
    """Tracks badges earned by users"""
    __tablename__ = "user_badges"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    badge_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.badges.badge_id", ondelete="CASCADE"))
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="badges")
    badge: Mapped["Badge"] = relationship("Badge", back_populates="user_badges")
    
    __table_args__ = (
        UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),
        Index("idx_ub_user_id", "user_id"),
        Index("idx_ub_badge_id", "badge_id"),
    )
    
    def __repr__(self) -> str:
        return f"<UserBadge(user_id={self.user_id}, badge_id='{self.badge_id}')>"


# =============================================================================
# System & Monitoring Models
# =============================================================================

class SystemLog(Base):
    """System log for debugging and monitoring"""
    __tablename__ = "system_logs"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    module: Mapped[str] = mapped_column(String(100), nullable=True)  # e.g., database, api, auth
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # Additional context as JSON
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="SET NULL"), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    __table_args__ = (
        Index("idx_sl_level", "level"),
        Index("idx_sl_module", "module"),
        Index("idx_sl_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<SystemLog(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"


class SystemHealth(Base):
    """System health and status monitoring"""
    __tablename__ = "system_health"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component: Mapped[str] = mapped_column(String(100), nullable=False)  # database, api, neo4j, openai
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # healthy, degraded, down, unknown
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metrics: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # Component-specific metrics
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index("idx_sh_component", "component"),
        Index("idx_sh_checked_at", "checked_at"),
    )
    
    def __repr__(self) -> str:
        return f"<SystemHealth(component='{self.component}', status='{self.status}')>"


class AIAgent(Base):
    """AI Agent configuration for content generation"""
    __tablename__ = "ai_agents"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # content_generator, quiz_maker, tutor
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # openai, anthropic, local
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2000)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cost_per_token: Mapped[float] = mapped_column(Float, default=0.0001)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    def __repr__(self) -> str:
        return f"<AIAgent(id={self.id}, name='{self.name}', provider='{self.provider}')>"


class AIGeneratedContent(Base):
    """Stores AI-generated content for admin management"""
    __tablename__ = "ai_generated_content"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    concept_name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # beginner, intermediate, advanced
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # The generated content body
    related_concepts: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of related concept names
    generated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # User ID who triggered generation
    model: Mapped[str] = mapped_column(String(100), default="openai")  # AI model used
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    __table_args__ = (
        Index("idx_aigc_domain", "domain"),
        Index("idx_aigc_difficulty", "difficulty"),
        Index("idx_aigc_generated_at", "generated_at"),
    )
    
    def __repr__(self) -> str:
        return f"<AIGeneratedContent(content_id='{self.content_id}', concept_name='{self.concept_name}')>"
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "content_id": self.content_id,
            "concept_name": self.concept_name,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "content": self.content,
            "related_concepts": self.related_concepts,
            "generated_by": self.generated_by,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }


class AIUsageStats(Base):
    """Tracks AI usage statistics for the admin dashboard"""
    __tablename__ = "ai_usage_stats"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False)  # total_generations, total_tokens, domain_usage
    stat_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Domain name for domain_usage
    stat_value: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("stat_type", "stat_key", name="uq_ai_stat"),
        Index("idx_aius_stat_type", "stat_type"),
    )
    
    def __repr__(self) -> str:
        return f"<AIUsageStats(type='{self.stat_type}', key='{self.stat_key}', value={self.stat_value})>"


class Testimonial(Base):
    """Testimonial model for user reviews and feedback"""
    __tablename__ = "testimonials"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=5)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_testimonial_approved", "is_approved"),
        Index("idx_testimonial_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Testimonial(id={self.id}, name='{self.name}', rating={self.rating})>"


# =============================================================================
# Authentication & Security Models
# =============================================================================

class EmailVerification(Base):
    """Email verification tokens for user registration"""
    __tablename__ = "email_verifications"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), default="email_verification")  # email_verification, email_change
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("idx_ev_user_id", "user_id"),
        Index("idx_ev_token", "token"),
        Index("idx_ev_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<EmailVerification(id={self.id}, user_id={self.user_id}, token='{self.token[:10]}...')>"


class PasswordReset(Base):
    """Password reset tokens for password recovery"""
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("idx_password_reset_tokens_user_id", "user_id"),
        Index("idx_password_reset_tokens_token", "token"),
        Index("idx_password_reset_tokens_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, token='{self.token[:10]}...')>"


# =============================================================================
# Code Execution Models
# =============================================================================

class SnippetVersion(Base):
    """Code snippet versions for version control"""
    __tablename__ = "snippet_versions"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snippet_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.code_snippets.snippet_id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    code_content: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        UniqueConstraint("snippet_id", "version_number", name="uq_snippet_version"),
        Index("idx_sv_snippet_id", "snippet_id"),
        Index("idx_sv_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SnippetVersion(id={self.id}, snippet_id='{self.snippet_id}', version={self.version_number})>"


class TestCase(Base):
    """Test cases for code snippets"""
    __tablename__ = "test_cases"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snippet_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.code_snippets.snippet_id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    timeout_ms: Mapped[int] = mapped_column(Integer, default=5000)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("idx_tc_snippet_id", "snippet_id"),
        Index("idx_tc_order", "order_index"),
    )

    def __repr__(self) -> str:
        return f"<TestCase(id={self.id}, snippet_id='{self.snippet_id}', name='{self.name}')>"


class DebugSession(Base):
    """Debug sessions for code debugging"""
    __tablename__ = "debug_sessions"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    snippet_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.code_snippets.snippet_id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="running")  # running, paused, completed
    current_line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    breakpoints: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of breakpoint line numbers
    variables: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # Current variable state
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("idx_ds_snippet_id", "snippet_id"),
        Index("idx_ds_user_id", "user_id"),
        Index("idx_ds_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<DebugSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"


# =============================================================================
# Course Models
# =============================================================================

class Course(Base):
    """Course model for organizing learning content"""
    __tablename__ = "courses"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), default='interactive')
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    course_concepts: Mapped[List["CourseConcept"]] = relationship(
        "CourseConcept", back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Course(course_id='{self.course_id}', title='{self.title}')>"


class CourseConcept(Base):
    """Association table for Course - Concept many-to-many relationship"""
    __tablename__ = "course_concepts"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[str] = mapped_column(String(100), ForeignKey("jeseci_academy.courses.course_id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(100), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="course_concepts")

    __table_args__ = (
        UniqueConstraint("course_id", "concept_id", name="uq_course_concept"),
        Index("idx_cc_course_id", "course_id"),
        Index("idx_cc_concept_id", "concept_id"),
    )

    def __repr__(self) -> str:
        return f"<CourseConcept(course_id='{self.course_id}', concept_id='{self.concept_id}')>"


# =============================================================================
# User Activities Models
# =============================================================================

class UserActivity(Base):
    """Tracks user learning activities"""
    __tablename__ = "user_activities"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    related_content_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    related_content_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default='completed')
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    ai_analysis: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_ua_user_id", "user_id"),
        Index("idx_ua_activity_type", "activity_type"),
        Index("idx_ua_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<UserActivity(activity_id='{self.activity_id}', user_id={self.user_id}, type='{self.activity_type}')>"


# =============================================================================
# Platform Stats Models
# =============================================================================

class PlatformStats(Base):
    """Stores aggregated platform statistics"""
    __tablename__ = "platform_stats"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stat_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    total_users: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    new_users: Mapped[int] = mapped_column(Integer, default=0)
    total_concepts: Mapped[int] = mapped_column(Integer, default=0)
    total_courses: Mapped[int] = mapped_column(Integer, default=0)
    total_lessons: Mapped[int] = mapped_column(Integer, default=0)
    total_learning_paths: Mapped[int] = mapped_column(Integer, default=0)
    total_achievements: Mapped[int] = mapped_column(Integer, default=0)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    total_session_duration: Mapped[int] = mapped_column(Integer, default=0)
    avg_session_duration: Mapped[int] = mapped_column(Integer, default=0)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    streak_active_users: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("stat_date", name="uq_stat_date"),
        Index("idx_ps_stat_date", "stat_date"),
    )

    def __repr__(self) -> str:
        return f"<PlatformStats(date='{self.stat_date}', users={self.total_users})>"


# =============================================================================
# Collaboration Models
# =============================================================================

class UserConnection(Base):
    """Tracks user connections (friends system)"""
    __tablename__ = "user_connections"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connection_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    connected_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "connected_user_id", name="uq_user_connection"),
        Index("idx_uc_user_id", "user_id"),
        Index("idx_uc_connected_user_id", "connected_user_id"),
    )

    def __repr__(self) -> str:
        return f"<UserConnection(user_id={self.user_id}, connected_user_id={self.connected_user_id}, status='{self.status}')>"


class Forum(Base):
    """Forum categories"""
    __tablename__ = "forums"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    forum_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default='general')
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    threads: Mapped[List["ForumThread"]] = relationship(
        "ForumThread", back_populates="forum", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Forum(forum_id='{self.forum_id}', name='{self.name}')>"


class ForumThread(Base):
    """Forum threads"""
    __tablename__ = "forum_threads"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    forum_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.forums.forum_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    forum: Mapped["Forum"] = relationship("Forum", back_populates="threads")
    posts: Mapped[List["ForumPost"]] = relationship(
        "ForumPost", back_populates="thread", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ForumThread(thread_id='{self.thread_id}', title='{self.title}')>"


class ForumPost(Base):
    """Forum posts (replies)"""
    __tablename__ = "forum_posts"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    thread_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.forum_threads.thread_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    parent_post_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    is_accepted_answer: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    thread: Mapped["ForumThread"] = relationship("ForumThread", back_populates="posts")

    def __repr__(self) -> str:
        return f"<ForumPost(post_id='{self.post_id}', thread_id='{self.thread_id}')>"


class ContentComment(Base):
    """Comments on lessons, courses, concepts, and learning paths"""
    __tablename__ = "content_comments"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    content_id: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_comment_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("idx_cc_content", "content_id", "content_type"),
        Index("idx_cc_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<ContentComment(comment_id='{self.comment_id}', content_id='{self.content_id}')>"


# =============================================================================
# Reputation System Models
# =============================================================================

class UserReputation(Base):
    """Tracks user reputation points and levels"""
    __tablename__ = "user_reputation"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), unique=True)
    reputation_points: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    total_upvotes_received: Mapped[int] = mapped_column(Integer, default=0)
    total_downvotes_received: Mapped[int] = mapped_column(Integer, default=0)
    total_accepted_answers: Mapped[int] = mapped_column(Integer, default=0)
    helpful_flags_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<UserReputation(user_id={self.user_id}, points={self.reputation_points}, level={self.level})>"


class ReputationEvent(Base):
    """Tracks individual reputation changes"""
    __tablename__ = "reputation_events"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    points_change: Mapped[int] = mapped_column(Integer, nullable=False)
    target_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_re_user_id", "user_id"),
        Index("idx_re_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ReputationEvent(event_id='{self.event_id}', user_id={self.user_id}, type='{self.event_type}')>"


class ContentUpvote(Base):
    """Tracks upvotes on content"""
    __tablename__ = "content_upvotes"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upvote_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    content_id: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    vote_type: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "content_id", "content_type", name="uq_content_upvote"),
        Index("idx_cu_content", "content_id", "content_type"),
    )

    def __repr__(self) -> str:
        return f"<ContentUpvote(upvote_id='{self.upvote_id}', user_id={self.user_id}, content_id='{self.content_id}')>"


# =============================================================================
# Study Groups Models
# =============================================================================

class StudyGroup(Base):
    """Study groups for collaborative learning"""
    __tablename__ = "study_groups"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    learning_goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_topic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_members: Mapped[int] = mapped_column(Integer, default=10)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit and soft delete fields
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    members: Mapped[List["StudyGroupMember"]] = relationship(
        "StudyGroupMember", back_populates="study_group", cascade="all, delete-orphan"
    )
    notes: Mapped[List["StudyGroupNote"]] = relationship(
        "StudyGroupNote", back_populates="study_group", cascade="all, delete-orphan"
    )
    discussions: Mapped[List["StudyGroupDiscussion"]] = relationship(
        "StudyGroupDiscussion", back_populates="study_group", cascade="all, delete-orphan"
    )
    messages: Mapped[List["StudyGroupMessage"]] = relationship(
        "StudyGroupMessage", back_populates="study_group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<StudyGroup(group_id='{self.group_id}', name='{self.name}')>"


class StudyGroupMember(Base):
    """Study group membership"""
    __tablename__ = "study_group_members"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    membership_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    group_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.study_groups.group_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20), default='member')
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    study_group: Mapped["StudyGroup"] = relationship("StudyGroup", back_populates="members")

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
        Index("idx_sgm_group_id", "group_id"),
        Index("idx_sgm_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<StudyGroupMember(membership_id='{self.membership_id}', group_id='{self.group_id}', user_id={self.user_id})>"


class StudyGroupNote(Base):
    """Shared notes in study groups"""
    __tablename__ = "study_group_notes"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    group_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.study_groups.group_id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    study_group: Mapped["StudyGroup"] = relationship("StudyGroup", back_populates="notes")

    def __repr__(self) -> str:
        return f"<StudyGroupNote(note_id='{self.note_id}', group_id='{self.group_id}', title='{self.title}')>"


class StudyGroupDiscussion(Base):
    """Discussions in study groups"""
    __tablename__ = "study_group_discussions"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    discussion_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    group_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.study_groups.group_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    study_group: Mapped["StudyGroup"] = relationship("StudyGroup", back_populates="discussions")

    def __repr__(self) -> str:
        return f"<StudyGroupDiscussion(discussion_id='{self.discussion_id}', group_id='{self.group_id}', topic='{self.topic}')>"


class StudyGroupMessage(Base):
    """Real-time messages in study groups"""
    __tablename__ = "study_group_messages"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    group_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.study_groups.group_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), default='text')
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    study_group: Mapped["StudyGroup"] = relationship("StudyGroup", back_populates="messages")

    def __repr__(self) -> str:
        return f"<StudyGroupMessage(message_id='{self.message_id}', group_id='{self.group_id}')>"


class StudyGroupGoal(Base):
    """Goals for study groups"""
    __tablename__ = "study_group_goals"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    goal_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    group_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.study_groups.group_id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<StudyGroupGoal(goal_id='{self.goal_id}', group_id='{self.group_id}', title='{self.title}')>"


# =============================================================================
# Mentorship Models
# =============================================================================

class MentorshipProfile(Base):
    """Mentor profiles"""
    __tablename__ = "mentorship_profiles"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), unique=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    expertise_areas: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    teaching_style: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    availability_hours: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_mentees: Mapped[int] = mapped_column(Integer, default=3)
    current_mentees_count: Mapped[int] = mapped_column(Integer, default=0)
    total_sessions_completed: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<MentorshipProfile(user_id={self.user_id}, is_available={self.is_available})>"


class MentorshipRequest(Base):
    """Mentorship requests"""
    __tablename__ = "mentorship_requests"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    mentee_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default='pending')
    topic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_schedule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    sessions: Mapped[List["MentorshipSession"]] = relationship(
        "MentorshipSession", back_populates="mentorship", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MentorshipRequest(request_id='{self.request_id}', mentor_id={self.mentor_id}, mentee_id={self.mentee_id})>"


class MentorshipSession(Base):
    """Mentorship sessions"""
    __tablename__ = "mentorship_sessions"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    mentorship_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.mentorship_requests.id", ondelete="CASCADE"))
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    mentee_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    status: Mapped[str] = mapped_column(String(20), default='scheduled')
    topic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mentor_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mentee_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mentor_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mentee_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    mentorship: Mapped["MentorshipRequest"] = relationship("MentorshipRequest", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<MentorshipSession(session_id='{self.session_id}', mentorship_id={self.mentorship_id})>"


# =============================================================================
# Moderation Models
# =============================================================================

class ContentReport(Base):
    """Content reports from users"""
    __tablename__ = "content_reports"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    reporter_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    content_id: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    report_reason: Mapped[str] = mapped_column(String(50), nullable=False)
    additional_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='pending')
    priority: Mapped[str] = mapped_column(String(20), default='normal')
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_cr_status", "status"),
        Index("idx_cr_priority", "priority"),
    )

    def __repr__(self) -> str:
        return f"<ContentReport(report_id='{self.report_id}', content_id='{self.content_id}', reason='{self.report_reason}')>"


class ModerationAction(Base):
    """Moderator actions"""
    __tablename__ = "moderation_actions"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    moderator_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    content_id: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_reversed: Mapped[bool] = mapped_column(Boolean, default=False)
    reversed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reversed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reversal_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_ma_moderator", "moderator_id"),
        Index("idx_ma_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ModerationAction(action_id='{self.action_id}', moderator_id={self.moderator_id}, type='{self.action_type}')>"


class ModerationQueue(Base):
    """Content awaiting moderation review"""
    __tablename__ = "moderation_queue"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    queue_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    content_id: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    report_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default='normal')
    status: Mapped[str] = mapped_column(String(20), default='pending')
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_mq_status", "status"),
        Index("idx_mq_priority", "priority"),
    )

    def __repr__(self) -> str:
        return f"<ModerationQueue(queue_id='{self.queue_id}', content_id='{self.content_id}')>"


# =============================================================================
# Peer Review Models
# =============================================================================

class PeerReviewSubmission(Base):
    """Peer review submissions"""
    __tablename__ = "peer_review_submissions"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    related_content_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    related_content_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='open')
    max_reviewers: Mapped[int] = mapped_column(Integer, default=2)
    current_reviewers: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments: Mapped[List["PeerReviewAssignment"]] = relationship(
        "PeerReviewAssignment", back_populates="submission", cascade="all, delete-orphan"
    )
    feedback: Mapped[List["PeerReviewFeedback"]] = relationship(
        "PeerReviewFeedback", back_populates="submission", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PeerReviewSubmission(submission_id='{self.submission_id}', title='{self.title}')>"


class PeerReviewAssignment(Base):
    """Peer review assignments"""
    __tablename__ = "peer_review_assignments"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assignment_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    submission_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.peer_review_submissions.submission_id", ondelete="CASCADE"))
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default='assigned')
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    submission: Mapped["PeerReviewSubmission"] = relationship("PeerReviewSubmission", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("submission_id", "reviewer_id", name="uq_review_assignment"),
        Index("idx_pra_reviewer", "reviewer_id"),
    )

    def __repr__(self) -> str:
        return f"<PeerReviewAssignment(assignment_id='{self.assignment_id}', submission_id='{self.submission_id}')>"


class PeerReviewFeedback(Base):
    """Peer review feedback"""
    __tablename__ = "peer_review_feedback"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feedback_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    assignment_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.peer_review_assignments.assignment_id", ondelete="CASCADE"))
    submission_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.peer_review_submissions.submission_id", ondelete="CASCADE"))
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    overall_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    author_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_upvotes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    submission: Mapped["PeerReviewSubmission"] = relationship("PeerReviewSubmission", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<PeerReviewFeedback(feedback_id='{self.feedback_id}', submission_id='{self.submission_id}')>"


# =============================================================================
# System & Analytics Models
# =============================================================================

class AuditLog(Base):
    """Comprehensive audit log for tracking all database changes"""
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action_type: Mapped[str] = mapped_column(String(20), nullable=False)
    old_values: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    changed_fields: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    performed_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    performed_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    application_source: Mapped[str] = mapped_column(String(50), default='admin_panel')
    country_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    country_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    isp_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_proxy: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    additional_context: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_al_table_record", "table_name", "record_id"),
        Index("idx_al_action", "action_type"),
        Index("idx_al_performed_by", "performed_by"),
        Index("idx_al_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(audit_id='{self.audit_id}', table='{self.table_name}', action='{self.action_type}')>"


class ContentView(Base):
    """Tracks content views for analytics"""
    __tablename__ = "content_views"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    view_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    content_id: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    view_duration: Mapped[int] = mapped_column(Integer, default=0)
    referrer_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    device_type: Mapped[str] = mapped_column(String(20), default='desktop')
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_unique_view: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("idx_cv_content_id", "content_id"),
        Index("idx_cv_content_type", "content_type"),
        Index("idx_cv_user_id", "user_id"),
        Index("idx_cv_viewed_at", "viewed_at"),
    )

    def __repr__(self) -> str:
        return f"<ContentView(view_id='{self.view_id}', content_id='{self.content_id}')>"


class ContentViewsSummary(Base):
    """Aggregated content views summary for fast analytics"""
    __tablename__ = "content_views_summary"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_id: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    total_views: Mapped[int] = mapped_column(Integer, default=0)
    unique_views: Mapped[int] = mapped_column(Integer, default=0)
    total_view_duration: Mapped[int] = mapped_column(Integer, default=0)
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    views_today: Mapped[int] = mapped_column(Integer, default=0)
    views_this_week: Mapped[int] = mapped_column(Integer, default=0)
    views_this_month: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("content_id", "content_type", name="uq_content_views_summary"),
        Index("idx_cvs_total", "total_views"),
    )

    def __repr__(self) -> str:
        return f"<ContentViewsSummary(content_id='{self.content_id}', total_views={self.total_views})>"


class Domain(Base):
    """Content domains for categorization"""
    __tablename__ = "domains"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[str] = mapped_column(String(20), default='#2563eb')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Domain(domain_id='{self.domain_id}', name='{self.name}')>"


# =============================================================================
# Notification Models
# =============================================================================

class Notification(Base):
    """In-app notifications for users"""
    __tablename__ = "notifications"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_n_user_id", "user_id"),
        Index("idx_n_user_unread", "user_id", "is_read"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}')>"


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"), primary_key=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    types_config: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<NotificationPreference(user_id={self.user_id}, email={self.email_enabled}, push={self.push_enabled})>"


# =============================================================================
# Contact & Communication Models
# =============================================================================

class ContactMessage(Base):
    """Contact form submissions"""
    __tablename__ = "contact_messages"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    contact_reason: Mapped[str] = mapped_column(String(50), default='general')
    status: Mapped[str] = mapped_column(String(20), default='new')
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    responded_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_cm_email", "email"),
        Index("idx_cm_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<ContactMessage(message_id='{self.message_id}', name='{self.name}')>"


class ChatExport(Base):
    """Chat conversation exports"""
    __tablename__ = "chat_exports"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    export_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    export_format: Mapped[str] = mapped_column(String(20), default='pdf')
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    conversation_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivery_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_ce_user_id", "user_id"),
        Index("idx_ce_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ChatExport(export_id='{self.export_id}', user_id={self.user_id}, format='{self.export_format}')>"


# =============================================================================
# Extended Code Execution Models
# =============================================================================

class CodeFolder(Base):
    """Code folders for organizing snippets"""
    __tablename__ = "code_folders"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_folder_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    color: Mapped[str] = mapped_column(String(20), default='#3b82f6')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<CodeFolder(id='{self.id}', name='{self.name}')>"


class CodeSnippet(Base):
    """Code snippets for user code storage"""
    __tablename__ = "code_snippets"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    code_content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), default='jac')
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    folder_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("idx_cs_user_id", "user_id"),
        Index("idx_cs_folder", "folder_id"),
    )

    def __repr__(self) -> str:
        return f"<CodeSnippet(id='{self.id}', title='{self.title}', language='{self.language}')>"


class ExecutionHistory(Base):
    """Execution history for code snippets"""
    __tablename__ = "execution_history"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    snippet_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    code_content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    entry_point: Mapped[str] = mapped_column(String(100), default='init')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_eh_user", "user_id", "created_at"),
        Index("idx_eh_snippet", "snippet_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ExecutionHistory(id='{self.id}', user_id={self.user_id}, status='{self.status}')>"


class TestResult(Base):
    """Test execution results"""
    __tablename__ = "test_results"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    test_case_id: Mapped[str] = mapped_column(String(64), ForeignKey("jeseci_academy.test_cases.id", ondelete="CASCADE"))
    execution_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    actual_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<TestResult(id='{self.id}', test_case_id='{self.test_case_id}', passed={self.passed})>"


class ErrorKnowledgeBase(Base):
    """Error patterns and suggestions for educational purposes"""
    __tablename__ = "error_knowledge_base"
    __table_args__ = {"schema": "jeseci_academy", "extend_existing": True}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    error_pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    examples: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    documentation_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(50), default='jac')
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit and soft delete fields
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<ErrorKnowledgeBase(id='{self.id}', error_type='{self.error_type}', title='{self.title}')>"


# =============================================================================
# Sync Engine Models (PostgreSQL-Neo4j Synchronization)
# =============================================================================

class SyncEventLog(Base):
    """Sync event log for PostgreSQL-Neo4j synchronization (outbox pattern)"""
    __tablename__ = "sync_event_log"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    source_version: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default='PENDING')  # PENDING, PUBLISHED, PROCESSING, COMPLETED, FAILED, SKIPPED
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    redis_message_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("idx_sync_event_log_event_id", "event_id"),
        Index("idx_sync_event_log_correlation_id", "correlation_id"),
        Index("idx_sync_event_log_entity", "entity_id", "entity_type"),
        Index("idx_sync_event_log_status", "status"),
        Index("idx_sync_event_log_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SyncEventLog(event_id='{self.event_id}', entity_type='{self.entity_type}', status='{self.status}')>"


class SyncStatus(Base):
    """Tracks sync status for individual entities"""
    __tablename__ = "sync_status"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_synced_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_version: Mapped[int] = mapped_column(Integer, default=0)
    neo4j_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    neo4j_checksum: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    has_pending_changes: Mapped[bool] = mapped_column(Boolean, default=False)
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False)
    conflict_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("entity_id", "entity_type", name="uq_sync_entity"),
        Index("idx_sync_status_entity", "entity_id", "entity_type"),
        Index("idx_sync_status_synced", "is_synced"),
    )

    def __repr__(self) -> str:
        return f"<SyncStatus(entity_id='{self.entity_id}', entity_type='{self.entity_type}', synced={self.is_synced})>"


class SyncConflict(Base):
    """Tracks synchronization conflicts between PostgreSQL and Neo4j"""
    __tablename__ = "sync_conflicts"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_version: Mapped[int] = mapped_column(Integer, nullable=False)
    target_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    target_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    difference_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_status: Mapped[str] = mapped_column(String(20), default='DETECTED')  # DETECTED, RESOLVED, MANUAL_REVIEW, IGNORED
    resolution_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_sync_conflicts_entity", "entity_id", "entity_type"),
        Index("idx_sync_conflicts_status", "resolution_status"),
        Index("idx_sync_conflicts_detected", "detected_at"),
    )

    def __repr__(self) -> str:
        return f"<SyncConflict(entity_id='{self.entity_id}', entity_type='{self.entity_type}', status='{self.resolution_status}')>"


class ReconciliationRun(Base):
    """Tracks reconciliation runs between PostgreSQL and Neo4j"""
    __tablename__ = "reconciliation_runs"
    __table_args__ = {"schema": "jeseci_academy"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entities_checked: Mapped[int] = mapped_column(Integer, default=0)
    inconsistencies_found: Mapped[int] = mapped_column(Integer, default=0)
    inconsistencies_repaired: Mapped[int] = mapped_column(Integer, default=0)
    conflicts_detected: Mapped[int] = mapped_column(Integer, default=0)
    conflicts_resolved: Mapped[int] = mapped_column(Integer, default=0)
    failed_entities: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='RUNNING')
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    batch_size: Mapped[int] = mapped_column(Integer, default=50)
    entities_included: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_reconciliation_runs_status", "status"),
        Index("idx_reconciliation_runs_started", "started_at"),
    )

    def __repr__(self) -> str:
        return f"<ReconciliationRun(run_id='{self.run_id}', run_type='{self.run_type}', status='{self.status}')>"


# =============================================================================
# Export all models for convenient importing
# =============================================================================

__all__ = [
    # User Domain
    "User", "UserProfile", "UserLearningPreference",
    # Content Domain
    "Concept", "ConceptContent", "LearningPath", "Lesson", "LearningPathConcept", "concept_relations",
    # Courses
    "Course", "CourseConcept",
    # Progress & Tracking
    "UserConceptProgress", "UserLearningPath", "UserLessonProgress", "LearningSession",
    # User Activities
    "UserActivity", "PlatformStats",
    # Assessment
    "Quiz", "QuizAttempt",
    # Gamification
    "Achievement", "UserAchievement", "Badge", "UserBadge",
    # System & Monitoring
    "SystemLog", "SystemHealth", "AIAgent",
    # AI
    "AIGeneratedContent", "AIUsageStats",
    # Testimonials
    "Testimonial",
    # Authentication & Security
    "EmailVerification", "PasswordReset",
    # Code Execution
    "SnippetVersion", "TestCase", "DebugSession",
    # Extended Code Execution
    "CodeFolder", "CodeSnippet", "ExecutionHistory", "TestResult", "ErrorKnowledgeBase",
    # Collaboration
    "UserConnection", "Forum", "ForumThread", "ForumPost", "ContentComment",
    # Reputation System
    "UserReputation", "ReputationEvent", "ContentUpvote",
    # Study Groups
    "StudyGroup", "StudyGroupMember", "StudyGroupNote", "StudyGroupDiscussion", "StudyGroupMessage", "StudyGroupGoal",
    # Mentorship
    "MentorshipProfile", "MentorshipRequest", "MentorshipSession",
    # Moderation
    "ContentReport", "ModerationAction", "ModerationQueue",
    # Peer Review
    "PeerReviewSubmission", "PeerReviewAssignment", "PeerReviewFeedback",
    # System & Analytics
    "AuditLog", "ContentView", "ContentViewsSummary", "Domain",
    # Notifications
    "Notification", "NotificationPreference",
    # Contact & Communication
    "ContactMessage", "ChatExport",
    # Sync Engine
    "SyncEventLog", "SyncStatus", "SyncConflict", "ReconciliationRun",
]
