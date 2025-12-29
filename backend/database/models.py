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
    key_terms: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of key terms
    synonyms: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of synonyms
    learning_objectives: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of learning objectives
    practical_applications: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of practical applications
    real_world_examples: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of real-world examples
    common_misconceptions: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of common misconceptions
    lesson_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lesson_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    concept_id: Mapped[str] = mapped_column(String(50), ForeignKey("jeseci_academy.concepts.concept_id", ondelete="CASCADE"))
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    mastery_level: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
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
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("jeseci_academy.users.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    concepts_covered: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON array of concept IDs
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    
    __table_args__ = (
        Index("idx_ls_user_id", "user_id"),
        Index("idx_ls_start_time", "start_time"),
    )
    
    def __repr__(self) -> str:
        return f"<LearningSession(id={self.id}, user_id={self.user_id}, duration={self.duration_seconds}s)>"


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
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tier: Mapped[str] = mapped_column(String(20), default="bronze")  # bronze, silver, gold, platinum
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)
    criteria_value: Mapped[int] = mapped_column(Integer, default=1)
    points: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
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
    
    __table_args__ = (
        UniqueConstraint("stat_type", "stat_key", name="uq_ai_stat"),
        Index("idx_aius_stat_type", "stat_type"),
    )
    
    def __repr__(self) -> str:
        return f"<AIUsageStats(type='{self.stat_type}', key='{self.stat_key}', value={self.stat_value})>"


# =============================================================================
# Export all models for convenient importing
# =============================================================================

__all__ = [
    # User Domain
    "User", "UserProfile", "UserLearningPreference",
    # Content Domain
    "Concept", "ConceptContent", "LearningPath", "Lesson", "LearningPathConcept", "concept_relations",
    # Progress & Tracking
    "UserConceptProgress", "UserLearningPath", "UserLessonProgress", "LearningSession",
    # Assessment
    "Quiz", "QuizAttempt",
    # Gamification
    "Achievement", "UserAchievement", "Badge", "UserBadge",
    # System & Monitoring
    "SystemLog", "SystemHealth", "AIAgent",
    # AI
    "AIGeneratedContent", "AIUsageStats",
]
