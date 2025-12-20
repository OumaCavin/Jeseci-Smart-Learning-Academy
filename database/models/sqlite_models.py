"""
Simplified database models for SQLite compatibility
Uses JSON instead of PostgreSQL ARRAY types
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Float, 
    ForeignKey, JSON, Table, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
import uuid

from config.database import Base


# Association table for many-to-many relationships (simplified for SQLite)
concept_relations = Table(
    'concept_relations',
    Base.metadata,
    Column('concept_id', String(36), ForeignKey('concepts.concept_id'), primary_key=True),
    Column('related_concept_id', String(36), ForeignKey('concepts.concept_id'), primary_key=True),
    Column('relationship_type', String(50), nullable=False),
    Column('strength', Float, default=1.0)
)


class User(Base):
    """Core User model"""
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Learning preferences
    learning_style = Column(String(20), nullable=True)
    skill_level = Column(String(20), nullable=True)
    preferred_language = Column(String(10), default="en")
    
    # Status and tracking
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserLearningPreferences(Base):
    """User learning preferences and settings"""
    __tablename__ = "user_learning_preferences"
    
    preference_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    # Content preferences (using JSON instead of ARRAY)
    content_type_preferences = Column(JSON, default=list)
    difficulty_preferences = Column(JSON, default=dict)
    subject_preferences = Column(JSON, default=list)
    
    # Study behavior
    study_time_preferences = Column(JSON, default=dict)
    session_length_preferences = Column(Integer, default=30)
    
    # Interaction preferences
    interaction_preferences = Column(JSON, default=dict)
    feedback_preferences = Column(JSON, default=dict)
    
    # Accessibility and personalization
    accessibility_needs = Column(JSON, default=dict)
    personalization_settings = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Concept(Base):
    """Core concept model for knowledge graph"""
    __tablename__ = "concepts"
    
    concept_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    detailed_description = Column(Text, nullable=True)
    
    # Categorization
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    domain = Column(String(50), nullable=False)
    
    # Difficulty and complexity
    difficulty_level = Column(String(20), nullable=False)
    complexity_score = Column(Float, default=0.0)
    cognitive_load = Column(Float, default=0.0)
    
    # Content and resources (using JSON instead of ARRAY)
    key_terms = Column(JSON, default=list)
    synonyms = Column(JSON, default=list)
    multimedia_resources = Column(JSON, default=list)
    interactive_elements = Column(JSON, default=list)
    
    # Learning metadata
    learning_objectives = Column(JSON, default=list)
    assessment_criteria = Column(JSON, default=list)
    practical_applications = Column(JSON, default=list)
    real_world_examples = Column(JSON, default=list)
    common_misconceptions = Column(JSON, default=list)
    teaching_strategies = Column(JSON, default=list)
    
    # Analytics
    mastery_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    usage_frequency = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    average_completion_time = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    
    # Content quality
    content_quality_score = Column(Float, default=0.0)
    ai_generated_content = Column(Boolean, default=False)
    
    # AI-generated lesson content (Just-in-Time Content Generator)
    lesson_content = Column(Text, nullable=True)  # Stores AI-generated lesson content
    lesson_generated_at = Column(DateTime, nullable=True)  # When lesson was last generated
    lesson_model_used = Column(String(50), nullable=True)  # Which AI model was used
    
    # Versioning and timestamps
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


class LearningPath(Base):
    """Learning path and curriculum model"""
    __tablename__ = "learning_paths"
    
    path_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    
    # Path metadata
    category = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    estimated_duration = Column(Integer, nullable=True)
    target_audience = Column(String(100), nullable=True)
    
    # Structure
    is_public = Column(Boolean, default=False)
    is_ai_generated = Column(Boolean, default=False)
    adaptive = Column(Boolean, default=True)
    
    # Content
    prerequisites = Column(JSON, default=list)
    learning_outcomes = Column(JSON, default=list)
    assessment_points = Column(JSON, default=list)
    
    # Metadata
    created_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(String(20), default="1.0")


class LearningPathConcept(Base):
    """Association table for learning path concepts with order"""
    __tablename__ = "learning_path_concepts"
    
    path_id = Column(String(36), ForeignKey("learning_paths.path_id"), primary_key=True)
    concept_id = Column(String(36), ForeignKey("concepts.concept_id"), primary_key=True)
    sequence_order = Column(Integer, nullable=False)
    estimated_duration = Column(Integer, nullable=True)
    
    # Learning parameters
    required_mastery_level = Column(Float, default=0.8)
    adaptive_difficulty = Column(Boolean, default=True)


class LearningSession(Base):
    """Individual learning session model"""
    __tablename__ = "learning_sessions"
    
    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    path_id = Column(String(36), ForeignKey("learning_paths.path_id"), nullable=True)
    
    # Session details
    session_type = Column(String(50), nullable=False)
    status = Column(String(20), default="in_progress")
    
    # Content and progress
    current_concept_id = Column(String(36), ForeignKey("concepts.concept_id"), nullable=True)
    progress_percentage = Column(Float, default=0.0)
    concepts_completed = Column(JSON, default=list)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_duration = Column(Integer, default=0)
    
    # Performance
    average_score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    
    # AI and personalization
    ai_recommendations = Column(JSON, default=list)
    difficulty_adjustments = Column(JSON, default=dict)


class UserProgress(Base):
    """User progress tracking for concepts and learning"""
    __tablename__ = "user_progress"
    
    progress_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    concept_id = Column(String(36), ForeignKey("concepts.concept_id"), nullable=False)
    session_id = Column(String(36), ForeignKey("learning_sessions.session_id"), nullable=True)
    
    # Progress metrics
    mastery_level = Column(Float, default=0.0)
    confidence_level = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)
    
    # Learning history
    first_attempt = Column(DateTime, default=datetime.utcnow)
    last_review = Column(DateTime, default=datetime.utcnow)
    review_count = Column(Integer, default=0)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    streak_count = Column(Integer, default=0)
    
    # Spaced repetition
    next_review_date = Column(DateTime, nullable=True)
    review_interval = Column(Integer, default=1)
    
    # AI insights
    learning_velocity = Column(Float, default=0.0)
    struggling_areas = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_progress_user_concept', 'user_id', 'concept_id', unique=True),
        Index('idx_progress_mastery', 'mastery_level'),
        Index('idx_progress_next_review', 'next_review_date'),
    )


class Quiz(Base):
    """Quiz and assessment model"""
    __tablename__ = "quizzes"
    
    quiz_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Quiz metadata
    concept_id = Column(String(36), ForeignKey("concepts.concept_id"), nullable=False)
    quiz_type = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    
    # Content
    questions = Column(JSON, nullable=False)
    time_limit = Column(Integer, nullable=True)
    passing_score = Column(Float, default=0.7)
    max_attempts = Column(Integer, default=3)
    
    # Settings
    randomize_questions = Column(Boolean, default=False)
    show_correct_answers = Column(Boolean, default=True)
    allow_review = Column(Boolean, default=True)
    
    # Analytics
    average_score = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    total_attempts = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QuizAttempt(Base):
    """Individual quiz attempt model"""
    __tablename__ = "quiz_attempts"
    
    attempt_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey("quizzes.quiz_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    # Attempt details
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(20), default="in_progress")
    
    # Scoring
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=1.0)
    percentage = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    time_taken = Column(Integer, default=0)
    
    # Responses
    responses = Column(JSON, default=dict)
    feedback = Column(JSON, default=dict)
    
    # AI insights
    difficulty_rating = Column(Float, nullable=True)
    confusion_areas = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_attempt_user_quiz', 'user_id', 'quiz_id'),
        Index('idx_attempt_score', 'score'),
    )


class UserAchievement(Base):
    """User achievements and badges"""
    __tablename__ = "user_achievements"
    
    achievement_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    # Achievement details
    achievement_type = Column(String(50), nullable=False)
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    badge_icon = Column(String(100), nullable=True)
    
    # Achievement data
    value = Column(Float, default=0.0)
    target_value = Column(Float, default=1.0)
    percentage = Column(Float, default=0.0)
    
    # Metadata
    earned_at = Column(DateTime, default=datetime.utcnow)
    category = Column(String(50), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_achievement_user', 'user_id'),
        Index('idx_achievement_type', 'achievement_type'),
        Index('idx_achievement_category', 'category'),
    )


class UserConceptProgress(Base):
    """Tracks a user's progress on a specific concept - simplified for dashboard"""
    __tablename__ = "user_concept_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    concept_id = Column(String(36), ForeignKey("concepts.concept_id"), nullable=False)
    
    # Progress tracking fields matching frontend expectations
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed
    progress_percent = Column(Integer, default=0)       # 0 to 100
    time_spent_minutes = Column(Integer, default=0)     # Total time spent in minutes
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # Optional user notes
    user_notes = Column(Text, nullable=True)
    
    # Unique constraint to prevent duplicate progress records
    __table_args__ = (
        Index('idx_concept_progress_unique', 'user_id', 'concept_id', unique=True),
    )


class ConceptContent(Base):
    """Educational content for concepts - lessons, exercises, and reading materials"""
    __tablename__ = "concept_content"
    
    content_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    concept_id = Column(String(36), ForeignKey("concepts.concept_id"), nullable=False)
    
    # Content metadata
    title = Column(String(200), nullable=False)
    content_type = Column(String(50), nullable=False)  # lesson, exercise, reading, quiz, video, interactive
    order_index = Column(Integer, default=0)  # Order within the concept
    
    # Content body
    content = Column(Text, nullable=False)  # Main content in markdown/HTML
    summary = Column(Text, nullable=True)   # Brief summary
    learning_objectives = Column(JSON, default=list)  # Specific objectives for this content
    
    # Media and resources
    multimedia_resources = Column(JSON, default=list)  # Images, videos, audio files
    external_links = Column(JSON, default=list)        # Additional resources
    code_examples = Column(JSON, default=list)         # Programming examples
    interactive_elements = Column(JSON, default=list)  # Interactive components
    
    # Difficulty and prerequisites
    difficulty_level = Column(String(20), nullable=False)
    estimated_duration = Column(Integer, default=30)  # Duration in minutes
    prerequisites = Column(JSON, default=list)        # Required prior knowledge
    
    # Assessment and practice
    practice_questions = Column(JSON, default=list)   # Practice problems
    examples = Column(JSON, default=list)             # Worked examples
    exercises = Column(JSON, default=list)            # Hands-on exercises
    
    # Analytics
    completion_rate = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    completion_time = Column(Integer, default=0)      # Average completion time in minutes
    
    # Content quality and versioning
    content_quality_score = Column(Float, default=0.0)
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True)
    ai_generated = Column(Boolean, default=False)
    
    # Author and timestamps
    author = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_content_concept', 'concept_id'),
        Index('idx_content_type', 'content_type'),
        Index('idx_content_order', 'concept_id', 'order_index'),
    )


class UserContentProgress(Base):
    """Track user progress through specific content pieces"""
    __tablename__ = "user_content_progress"
    
    progress_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    content_id = Column(String(36), ForeignKey("concept_content.content_id"), nullable=False)
    
    # Progress tracking
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed, mastered
    progress_percent = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # Time spent in minutes
    
    # Performance metrics
    score = Column(Float, nullable=True)      # Score achieved (if applicable)
    attempts = Column(Integer, default=0)     # Number of attempts
    best_score = Column(Float, default=0.0)   # Best score achieved
    
    # Learning analytics
    first_accessed = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    last_completed = Column(DateTime, nullable=True)
    
    # User interactions
    notes = Column(Text, nullable=True)       # User's personal notes
    bookmarks = Column(JSON, default=list)    # Bookmarked sections
    difficulty_rating = Column(Float, nullable=True)  # User's difficulty rating
    
    # Spaced repetition
    next_review = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    
    # Indexes
    __table_args__ = (
        Index('idx_content_progress_user', 'user_id', 'content_id', unique=True),
        Index('idx_content_progress_status', 'status'),
        Index('idx_content_progress_next_review', 'next_review'),
    )