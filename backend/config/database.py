"""
SQLAlchemy Database Configuration for Jeseci Smart Learning Academy

This module provides the database engine, session management, and base class
for SQLAlchemy ORM models. It loads configuration from environment variables
and supports PostgreSQL connections.

Models included:
- User Domain: User, UserProfile, UserLearningPreference
- Content Domain: Concept, ConceptContent, LearningPath, Lesson, LearningPathConcept
- Progress Tracking: UserConceptProgress, UserLearningPath, UserLessonProgress, LearningSession
- Assessment: Quiz, QuizAttempt
- Gamification: Achievement, UserAchievement, Badge, UserBadge
- System: SystemLog, SystemHealth, AIAgent
"""

import os
from typing import Generator
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.pool import QueuePool


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models"""
    pass


def get_database_url() -> str:
    """
    Construct database URL from environment variables.
    
    Expected environment variables:
    - POSTGRES_HOST: Database host (default: localhost)
    - POSTGRES_PORT: Database port (default: 5432)
    - POSTGRES_DB: Database name (default: jeseci_learning_academy)
    - POSTGRES_USER: Database user (default: jeseci_academy_user)
    - POSTGRES_PASSWORD: Database password (default: jeseci_secure_password_2024)
    - DB_SCHEMA: Database schema (default: jeseci_academy)
    
    Returns:
        PostgreSQL connection URL for SQLAlchemy
    """
    # Load from environment or use defaults
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "jeseci_learning_academy")
    user = os.getenv("POSTGRES_USER", "jeseci_academy_user")
    password = os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
    
    # Construct URL for psycopg2 driver
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    
    print(f"[INFO] Database URL constructed: postgresql+psycopg2://{user}:***@{host}:{port}/{database}")
    
    return url


def get_schema() -> str:
    """
    Get the database schema to use.
    
    Returns:
        Schema name (default: jeseci_academy)
    """
    return os.getenv("DB_SCHEMA", "jeseci_academy")


def get_engine():
    """
    Create and return SQLAlchemy engine with optimal settings.
    
    Uses QueuePool for connection pooling with reasonable defaults
    for a web application.
    """
    database_url = get_database_url()
    schema = get_schema()
    
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False,  # Set to True for SQL debugging
        connect_args={"options": f"-c search_path={schema}"}
    )
    
    # Set the schema on the engine
    def set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET search_path TO {schema}")
        cursor.close()
    
    event.listen(engine, "connect", set_search_path)
    
    print(f"[INFO] SQLAlchemy engine created with schema: {schema}")
    
    return engine


def get_session_factory():
    """
    Create session factory for generating database sessions.
    """
    engine = get_engine()
    
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI or context manager for scripts.
    
    Yields a database session and ensures it's closed after use.
    For use with FastAPI: Depends(get_db)
    For use in scripts: Use context manager pattern
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables from models.
    This function creates the schema if it doesn't exist.
    """
    engine = get_engine()
    schema = get_schema()
    
    # Create schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        conn.commit()
    
    # Import all models to ensure they are registered with Base.metadata
    from backend.database.models import (
        # User Domain
        User, UserProfile, UserLearningPreference,
        # Content Domain
        Concept, ConceptContent, LearningPath, Lesson, LearningPathConcept,
        concept_relations,
        # Progress & Tracking
        UserConceptProgress, UserLearningPath, UserLessonProgress, LearningSession,
        # Assessment
        Quiz, QuizAttempt,
        # Gamification
        Achievement, UserAchievement, Badge, UserBadge,
        # System & Monitoring
        SystemLog, SystemHealth, AIAgent,
    )
    
    # Set the schema for all models
    Base.metadata.schema = schema
    
    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)
    
    print(f"[INFO] Database tables created/verified in schema '{schema}' successfully")
    
    return engine


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


# Global session factory for import convenience
SessionLocal = get_session_factory()
