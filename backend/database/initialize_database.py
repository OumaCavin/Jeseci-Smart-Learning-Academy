#!/usr/bin/env python3
"""
Database Initialization Script for Jeseci Smart Learning Academy

This script creates all database tables required by the application.
Run this script once during initial setup or whenever new tables are added.

Usage:
    python -m database.initialize_database

Or simply run the backend - it will automatically call initialize_all_tables()
"""

import os
import sys

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env'))

from logger_config import logger
import psycopg2
from psycopg2 import extras

# Database configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


def create_users_tables(cursor):
    """Create user-related tables"""
    logger.info("Creating user-related tables...")
    
    # Users table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.users (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(64) UNIQUE NOT NULL,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        is_admin BOOLEAN DEFAULT FALSE,
        admin_role VARCHAR(50) DEFAULT 'student',
        is_email_verified BOOLEAN DEFAULT FALSE,
        verification_token VARCHAR(255),
        token_expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login_at TIMESTAMP
    )
    """)
    
    # User profile table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_profile (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        bio TEXT,
        avatar_url VARCHAR(500),
        timezone VARCHAR(50),
        language VARCHAR(10) DEFAULT 'en',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # User learning preferences table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_learning_preferences (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        daily_goal_minutes INTEGER DEFAULT 30,
        preferred_difficulty VARCHAR(20) DEFAULT 'intermediate',
        preferred_content_type VARCHAR(50) DEFAULT 'text',
        notifications_enabled BOOLEAN DEFAULT TRUE,
        email_reminders BOOLEAN DEFAULT TRUE,
        dark_mode BOOLEAN DEFAULT FALSE,
        auto_play_videos BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Password reset tokens table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.password_reset_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        used_at TIMESTAMP
    )
    """)
    
    logger.info("✓ User tables created: users, user_profile, user_learning_preferences, password_reset_tokens")


def create_content_tables(cursor):
    """Create content-related tables"""
    logger.info("Creating content-related tables...")
    
    # Concepts table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.concepts (
        id SERIAL PRIMARY KEY,
        concept_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        display_name VARCHAR(200),
        category VARCHAR(100),
        difficulty_level VARCHAR(50) DEFAULT 'beginner',
        domain VARCHAR(100),
        description TEXT,
        icon VARCHAR(100) DEFAULT 'default',
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Concept content table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.concept_content (
        id SERIAL PRIMARY KEY,
        concept_id VARCHAR(100) NOT NULL,
        content_type VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Learning paths table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.learning_paths (
        id SERIAL PRIMARY KEY,
        path_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        title VARCHAR(200) NOT NULL,
        category VARCHAR(100),
        difficulty VARCHAR(50),
        estimated_duration INTEGER,
        target_audience VARCHAR(255),
        description TEXT,
        prerequisites JSONB,
        learning_outcomes JSONB,
        is_public BOOLEAN DEFAULT FALSE,
        is_published BOOLEAN DEFAULT FALSE,
        thumbnail_url VARCHAR(500),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Lessons table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.lessons (
        id SERIAL PRIMARY KEY,
        lesson_id VARCHAR(50) UNIQUE NOT NULL,
        learning_path_id VARCHAR(50) NOT NULL,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        sequence_order INTEGER DEFAULT 0,
        estimated_duration INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Learning path concepts table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.learning_path_concepts (
        id SERIAL PRIMARY KEY,
        path_id VARCHAR(50) NOT NULL,
        concept_id VARCHAR(100) NOT NULL,
        sequence_order INTEGER DEFAULT 0,
        is_required BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Lesson concepts table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.lesson_concepts (
        id SERIAL PRIMARY KEY,
        lesson_id VARCHAR(50) NOT NULL,
        concept_id VARCHAR(100) NOT NULL,
        sequence_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    logger.info("✓ Content tables created: concepts, concept_content, learning_paths, lessons, learning_path_concepts, lesson_concepts")


def create_progress_tables(cursor):
    """Create progress tracking tables"""
    logger.info("Creating progress tracking tables...")
    
    # User concept progress table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_concept_progress (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        concept_id VARCHAR(100) NOT NULL,
        status VARCHAR(20) DEFAULT 'not_started',
        progress_percent INTEGER DEFAULT 0,
        time_spent_seconds INTEGER DEFAULT 0,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, concept_id)
    )
    """)
    
    # User learning paths table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_learning_paths (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        path_id VARCHAR(50) NOT NULL,
        progress_percent INTEGER DEFAULT 0,
        status VARCHAR(20) DEFAULT 'not_started',
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, path_id)
    )
    """)
    
    # User lesson progress table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_lesson_progress (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        lesson_id VARCHAR(50) NOT NULL,
        status VARCHAR(20) DEFAULT 'not_started',
        progress_percent INTEGER DEFAULT 0,
        time_spent_seconds INTEGER DEFAULT 0,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, lesson_id)
    )
    """)
    
    # Learning sessions table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.learning_sessions (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(50) UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        course_id VARCHAR(50),
        concept_id VARCHAR(100),
        path_id VARCHAR(50),
        lesson_id VARCHAR(50),
        quiz_id VARCHAR(50),
        session_type VARCHAR(50),
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        duration_seconds INTEGER DEFAULT 0,
        activities_completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    logger.info("✓ Progress tables created: user_concept_progress, user_learning_paths, user_lesson_progress, learning_sessions")


def create_assessment_tables(cursor):
    """Create assessment/quiz tables"""
    logger.info("Creating assessment tables...")
    
    # Quizzes table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.quizzes (
        id SERIAL PRIMARY KEY,
        quiz_id VARCHAR(50) UNIQUE NOT NULL,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        concept_id VARCHAR(100),
        lesson_id VARCHAR(50),
        passing_score INTEGER DEFAULT 70,
        time_limit_minutes INTEGER,
        max_attempts INTEGER DEFAULT 3,
        is_published BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Quiz attempts table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.quiz_attempts (
        id SERIAL PRIMARY KEY,
        attempt_id VARCHAR(50) UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        quiz_id VARCHAR(50) NOT NULL,
        score INTEGER DEFAULT 0,
        total_questions INTEGER DEFAULT 0,
        correct_answers INTEGER DEFAULT 0,
        time_taken_seconds INTEGER DEFAULT 0,
        is_passed BOOLEAN DEFAULT FALSE,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    logger.info("✓ Assessment tables created: quizzes, quiz_attempts")


def create_gamification_tables(cursor):
    """Create gamification tables"""
    logger.info("Creating gamification tables...")
    
    # Achievements table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.achievements (
        id SERIAL PRIMARY KEY,
        achievement_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        icon VARCHAR(100),
        category VARCHAR(50),
        requirement_type VARCHAR(50),
        requirement_value INTEGER,
        points INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # User achievements table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_achievements (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        achievement_id VARCHAR(50) NOT NULL,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        progress INTEGER DEFAULT 0,
        UNIQUE(user_id, achievement_id)
    )
    """)
    
    # Badges table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.badges (
        id SERIAL PRIMARY KEY,
        badge_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        icon VARCHAR(100),
        category VARCHAR(50),
        tier VARCHAR(20),
        requirement TEXT,
        points INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # User badges table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_badges (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        badge_id VARCHAR(50) NOT NULL,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, badge_id)
    )
    """)
    
    logger.info("✓ Gamification tables created: achievements, user_achievements, badges, user_badges")


def create_system_tables(cursor):
    """Create system tables"""
    logger.info("Creating system tables...")
    
    # System logs table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.system_logs (
        id SERIAL PRIMARY KEY,
        log_id VARCHAR(50) UNIQUE NOT NULL,
        log_type VARCHAR(50),
        source VARCHAR(100),
        message TEXT,
        level VARCHAR(20),
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # System health table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.system_health (
        id SERIAL PRIMARY KEY,
        check_name VARCHAR(100) NOT NULL,
        status VARCHAR(20) NOT NULL,
        message TEXT,
        details JSONB,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    logger.info("✓ System tables created: system_logs, system_health")


def create_ai_tables(cursor):
    """Create AI-related tables"""
    logger.info("Creating AI-related tables...")
    
    # AI agents table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.ai_agents (
        id SERIAL PRIMARY KEY,
        agent_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        agent_type VARCHAR(50),
        status VARCHAR(20) DEFAULT 'active',
        capabilities JSONB,
        parameters JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # AI generated content table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.ai_generated_content (
        id SERIAL PRIMARY KEY,
        content_id VARCHAR(50) UNIQUE NOT NULL,
        concept_name VARCHAR(200),
        domain VARCHAR(100),
        difficulty VARCHAR(50),
        content TEXT,
        related_concepts JSONB,
        generated_by VARCHAR(100),
        model VARCHAR(50) DEFAULT 'openai',
        tokens_used INTEGER,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # AI usage stats table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.ai_usage_stats (
        id SERIAL PRIMARY KEY,
        stat_type VARCHAR(50) NOT NULL,
        stat_key VARCHAR(100) NOT NULL,
        stat_value INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(stat_type, stat_key)
    )
    """)
    
    logger.info("✓ AI tables created: ai_agents, ai_generated_content, ai_usage_stats")


def create_indexes(cursor):
    """Create database indexes for performance"""
    logger.info("Creating database indexes...")
    
    indexes = [
        # User indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_users_username ON {DB_SCHEMA}.users(username)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_users_email ON {DB_SCHEMA}.users(email)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_users_admin ON {DB_SCHEMA}.users(is_admin)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_verification_token ON {DB_SCHEMA}.users(verification_token)",
        
        # Content indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_concepts_category ON {DB_SCHEMA}.concepts(category)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_concepts_domain ON {DB_SCHEMA}.concepts(domain)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_learning_paths_category ON {DB_SCHEMA}.learning_paths(category)",
        
        # Progress indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_concept_progress_user ON {DB_SCHEMA}.user_concept_progress(user_id)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_learning_paths_user ON {DB_SCHEMA}.user_learning_paths(user_id)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_learning_sessions_user ON {DB_SCHEMA}.learning_sessions(user_id)",
        
        # Assessment indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_quiz_attempts_user ON {DB_SCHEMA}.quiz_attempts(user_id)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_quiz_attempts_quiz ON {DB_SCHEMA}.quiz_attempts(quiz_id)",
        
        # AI indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_ai_generated_domain ON {DB_SCHEMA}.ai_generated_content(domain)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_ai_generated_concept ON {DB_SCHEMA}.ai_generated_content(concept_name)",
    ]
    
    for index_query in indexes:
        try:
            cursor.execute(index_query)
        except Exception as e:
            logger.debug(f"Index might already exist: {e}")
    
    logger.info("✓ Database indexes created")


def initialize_database():
    """Initialize all database tables"""
    logger.info("="*60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("="*60)
    
    # Get database connection
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db = os.getenv("POSTGRES_DB", "jeseci_learning_academy")
    postgres_user = os.getenv("POSTGRES_USER", "jeseci_academy_user")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
    
    conn = None
    try:
        conn = psycopg2.connect(
            host=postgres_host,
            port=postgres_port,
            database=postgres_db,
            user=postgres_user,
            password=postgres_password
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        logger.info(f"Connected to PostgreSQL: {postgres_host}:{postgres_port}/{postgres_db}")
        
        # Create all tables
        create_users_tables(cursor)
        create_content_tables(cursor)
        create_progress_tables(cursor)
        create_assessment_tables(cursor)
        create_gamification_tables(cursor)
        create_system_tables(cursor)
        create_ai_tables(cursor)
        create_indexes(cursor)
        
        conn.commit()
        
        logger.info("")
        logger.info("="*60)
        logger.info("✓ ALL DATABASE TABLES CREATED SUCCESSFULLY!")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
