"""
SQLAlchemy ORM Models for Jeseci Smart Learning Academy

This module defines all database tables as SQLAlchemy models using the
Declarative Base pattern. All models use SQLAlchemy 2.0 type hints
for better type safety and IDE support.

Tables:
- User: Core user accounts and authentication
- Concept: Learning concepts and topics
- LearningPath: Learning path definitions
- LearningPathConcept: Association table for learning path concepts
- UserConceptProgress: User progress tracking for concepts
- UserLearningPath: User enrollment in learning paths
- Achievement: Achievement definitions
- UserAchievement: User earned achievements
- QuizAttempt: Quiz attempt records
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Text, DateTime, Float, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.config.database import Base


class User(Base):
    """Core User model for authentication and tracking"""
    __tablename__ = "users"
    
    # Primary key - using SERIAL for PostgreSQL
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Unique identifiers
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    
    # Authentication
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile information
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    concept_progress: Mapped[List["UserConceptProgress"]] = relationship(
        "UserConceptProgress", back_populates="user", cascade="all, delete-orphan"
    )
    learning_paths: Mapped[List["UserLearningPath"]] = relationship(
        "UserLearningPath", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"


class Concept(Base):
    """Learning Concept model representing topics in the curriculum"""
    __tablename__ = "concepts"
    
    # Primary key - using VARCHAR as per existing schema
    concept_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Concept details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Lesson content (could be AI-generated or manually created)
    lesson_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lesson_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    learning_path_concepts: Mapped[List["LearningPathConcept"]] = relationship(
        "LearningPathConcept", back_populates="concept"
    )
    user_progress: Mapped[List["UserConceptProgress"]] = relationship(
        "UserConceptProgress", back_populates="concept"
    )
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="concept"
    )
    
    def __repr__(self) -> str:
        return f"<Concept(concept_id='{self.concept_id}', name='{self.name}')>"


class LearningPath(Base):
    """Learning Path model for organizing concepts into structured courses"""
    __tablename__ = "learning_paths"
    
    # Primary key
    path_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Path details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in minutes
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    concepts: Mapped[List["LearningPathConcept"]] = relationship(
        "LearningPathConcept", back_populates="learning_path", cascade="all, delete-orphan"
    )
    user_learning_paths: Mapped[List["UserLearningPath"]] = relationship(
        "UserLearningPath", back_populates="learning_path"
    )
    
    def __repr__(self) -> str:
        return f"<LearningPath(path_id='{self.path_id}', title='{self.title}')>"


class LearningPathConcept(Base):
    """Association table for Learning Path - Concept many-to-many relationship"""
    __tablename__ = "learning_path_concepts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    path_id: Mapped[str] = mapped_column(String(50), ForeignKey("learning_paths.path_id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(50), ForeignKey("concepts.concept_id", ondelete="CASCADE"))
    
    # Additional fields
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="concepts")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="learning_path_concepts")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint("path_id", "concept_id", name="uq_path_concept"),
        Index("idx_learning_path_concepts_path_id", "path_id"),
        Index("idx_learning_path_concepts_concept_id", "concept_id"),
    )
    
    def __repr__(self) -> str:
        return f"<LearningPathConcept(path_id='{self.path_id}', concept_id='{self.concept_id}')>"


class UserConceptProgress(Base):
    """Tracks user progress through individual concepts"""
    __tablename__ = "user_concept_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(50), ForeignKey("concepts.concept_id", ondelete="CASCADE"))
    
    # Progress metrics
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    mastery_level: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="concept_progress")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="user_progress")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_user_concept_progress"),
        Index("idx_user_concept_progress_user_id", "user_id"),
        Index("idx_user_concept_progress_concept_id", "concept_id"),
    )
    
    def __repr__(self) -> str:
        return f"<UserConceptProgress(user_id={self.user_id}, concept_id='{self.concept_id}', progress={self.progress_percent}%)>"


class UserLearningPath(Base):
    """Tracks user enrollment and progress in learning paths"""
    __tablename__ = "user_learning_paths"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    path_id: Mapped[str] = mapped_column(String(50), ForeignKey("learning_paths.path_id", ondelete="CASCADE"))
    
    # Progress
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_paths")
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="user_learning_paths")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint("user_id", "path_id", name="uq_user_learning_path"),
        Index("idx_user_learning_paths_user_id", "user_id"),
        Index("idx_user_learning_paths_path_id", "path_id"),
    )
    
    def __repr__(self) -> str:
        return f"<UserLearningPath(user_id={self.user_id}, path_id='{self.path_id}', progress={self.progress_percent}%)>"


class Achievement(Base):
    """Achievement model for gamification"""
    __tablename__ = "achievements"
    
    achievement_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Achievement details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # How to earn this achievement
    
    # Timestamp
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
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    achievement_id: Mapped[str] = mapped_column(String(50), ForeignKey("achievements.achievement_id", ondelete="CASCADE"))
    
    # Timestamp
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_achievements_user_id", "user_id"),
        Index("idx_user_achievements_achievement_id", "achievement_id"),
    )
    
    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id='{self.achievement_id}')>"


class QuizAttempt(Base):
    """Records quiz attempts by users"""
    __tablename__ = "quiz_attempts"
    
    attempt_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(50), ForeignKey("concepts.concept_id", ondelete="CASCADE"))
    
    # Quiz results
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=True)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Timestamp
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
    concept: Mapped["Concept"] = relationship("Concept", back_populates="quiz_attempts")
    
    # Indexes
    __table_args__ = (
        Index("idx_quiz_attempts_user_id", "user_id"),
        Index("idx_quiz_attempts_concept_id", "concept_id"),
    )
    
    def __repr__(self) -> str:
        return f"<QuizAttempt(attempt_id={self.attempt_id}, user_id={self.user_id}, score={self.score})>"
