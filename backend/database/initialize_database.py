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
        created_by VARCHAR(64),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_by VARCHAR(64),
        last_login_at TIMESTAMP,
        is_deleted BOOLEAN DEFAULT FALSE,
        deleted_at TIMESTAMP,
        deleted_by VARCHAR(64)
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
        created_by VARCHAR(64),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_by VARCHAR(64),
        is_deleted BOOLEAN DEFAULT FALSE,
        deleted_at TIMESTAMP,
        deleted_by VARCHAR(64)
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
        user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
        token VARCHAR(128) NOT NULL UNIQUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        is_used BOOLEAN DEFAULT FALSE,
        ip_address VARCHAR(50),
        user_agent TEXT
    )
    """)
    
    # Add is_used column if table exists with old schema (using used_at)
    try:
        cursor.execute(f"""
            ALTER TABLE {DB_SCHEMA}.password_reset_tokens
            ADD COLUMN IF NOT EXISTS is_used BOOLEAN DEFAULT FALSE
        """)
    except Exception as e:
        logger.debug(f"is_used column might already exist: {e}")
    
    # Add missing columns if they don't exist
    try:
        cursor.execute(f"""
            ALTER TABLE {DB_SCHEMA}.password_reset_tokens
            ADD COLUMN IF NOT EXISTS ip_address VARCHAR(50)
        """)
    except Exception as e:
        logger.debug(f"ip_address column might already exist: {e}")
    
    try:
        cursor.execute(f"""
            ALTER TABLE {DB_SCHEMA}.password_reset_tokens
            ADD COLUMN IF NOT EXISTS user_agent TEXT
        """)
    except Exception as e:
        logger.debug(f"user_agent column might already exist: {e}")
    
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
        created_by VARCHAR(64),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_by VARCHAR(64),
        is_deleted BOOLEAN DEFAULT FALSE,
        deleted_at TIMESTAMP,
        deleted_by VARCHAR(64)
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(path_id, concept_id)
    )
    """)
    
    # Lesson concepts table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.lesson_concepts (
        id SERIAL PRIMARY KEY,
        lesson_id VARCHAR(50) NOT NULL,
        concept_id VARCHAR(100) NOT NULL,
        sequence_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(lesson_id, concept_id)
    )
    """)
    
    logger.info("✓ Content tables created: concepts, concept_content, learning_paths, lessons, learning_path_concepts, lesson_concepts")


def create_courses_table(cursor):
    """Create courses table"""
    logger.info("Creating courses table...")
    
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.courses (
        id SERIAL PRIMARY KEY,
        course_id VARCHAR(100) UNIQUE NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        domain VARCHAR(100),
        difficulty VARCHAR(50),
        estimated_duration INTEGER,
        content_type VARCHAR(50) DEFAULT 'interactive',
        is_published BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(64),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_by VARCHAR(64),
        is_deleted BOOLEAN DEFAULT FALSE,
        deleted_at TIMESTAMP,
        deleted_by VARCHAR(64)
    )
    """)
    
    # Also create course_concepts junction table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.course_concepts (
        id SERIAL PRIMARY KEY,
        course_id VARCHAR(100) NOT NULL,
        concept_id VARCHAR(100) NOT NULL,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(course_id, concept_id)
    )
    """)
    
    logger.info("✓ Courses tables created: courses, course_concepts")


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
        created_by VARCHAR(64),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_by VARCHAR(64),
        is_deleted BOOLEAN DEFAULT FALSE,
        deleted_at TIMESTAMP,
        deleted_by VARCHAR(64)
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
    
    # Seed default quizzes
    default_quizzes = [
        # Jac Language Basics
        ('quiz_jac_variables', 'Variables and Data Types', 'Test your understanding of variables in Jac', 'jac_variables', None, 70, 15, 3),
        ('quiz_jac_functions', 'Functions and Parameters', 'Test your knowledge of Jac functions', 'jac_functions', None, 70, 20, 3),
        ('quiz_jac_osp', 'Object-Spatial Programming', 'Test your understanding of OSP concepts', 'jac_osp', None, 75, 25, 3),
        
        # Python Basics
        ('quiz_python_syntax', 'Python Syntax Basics', 'Test Python syntax fundamentals', 'python_syntax', None, 70, 15, 3),
        ('quiz_python_data', 'Python Data Structures', 'Test your knowledge of Python data types', 'python_data', None, 70, 20, 3),
        
        # General Programming
        ('quiz_prog_basics', 'Programming Fundamentals', 'Test core programming concepts', 'prog_basics', None, 65, 15, 3),
        ('quiz_oop_concepts', 'OOP Concepts', 'Test object-oriented programming understanding', 'oop_concepts', None, 75, 20, 3),
    ]
    
    for quiz_id, title, description, concept_id, lesson_id, passing_score, time_limit, max_attempts in default_quizzes:
        cursor.execute(f"""
            INSERT INTO {DB_SCHEMA}.quizzes 
            (quiz_id, title, description, concept_id, lesson_id, passing_score, time_limit_minutes, max_attempts, is_published)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (quiz_id) DO NOTHING
        """, (quiz_id, title, description, concept_id, lesson_id, passing_score, time_limit, max_attempts))
    
    logger.info("✓ Default quizzes seeded")


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
        criteria_type VARCHAR(50),
        criteria_value INTEGER,
        points INTEGER DEFAULT 0,
        tier VARCHAR(20) DEFAULT 'bronze',
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
        criteria_type VARCHAR(50),
        criteria_value INTEGER,
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

    # Seed default achievements
    default_achievements = [
        # Learning achievements
        ('first_concept', 'First Steps', 'Complete your first concept', '🎯', 'concepts_completed', 1, 10, 'bronze'),
        ('concept_master', 'Concept Master', 'Complete 10 concepts', '📚', 'concepts_completed', 10, 25, 'silver'),
        ('knowledge_seeker', 'Knowledge Seeker', 'Complete 25 concepts', '🧠', 'concepts_completed', 25, 50, 'gold'),
        ('concept_champion', 'Concept Champion', 'Complete 50 concepts', '🏆', 'concepts_completed', 50, 100, 'platinum'),
        
        # Quiz achievements
        ('first_quiz', 'Quiz Beginner', 'Pass your first quiz', '✅', 'quizzes_passed', 1, 10, 'bronze'),
        ('quiz_master', 'Quiz Master', 'Pass 10 quizzes', '🎓', 'quizzes_passed', 10, 30, 'silver'),
        ('quiz_champion', 'Quiz Champion', 'Pass 25 quizzes', '🥇', 'quizzes_passed', 25, 60, 'gold'),
        ('perfect_score', 'Perfect Score', 'Score 100% on a quiz', '💯', 'quizzes_passed', 1, 50, 'gold'),
        
        # Streak achievements
        ('week_warrior', 'Week Warrior', 'Maintain a 7-day streak', '🔥', 'streak_days', 7, 20, 'bronze'),
        ('month_master', 'Month Master', 'Maintain a 30-day streak', '🌟', 'streak_days', 30, 75, 'silver'),
        ('dedication', 'Dedicated Learner', 'Maintain a 100-day streak', '💎', 'streak_days', 100, 200, 'platinum'),
        
        # Course achievements
        ('first_course', 'Course Starter', 'Complete your first course', '🚀', 'courses_completed', 1, 15, 'bronze'),
        ('course_explorer', 'Course Explorer', 'Complete 5 courses', '🌍', 'courses_completed', 5, 40, 'silver'),
        ('course_conqueror', 'Course Conqueror', 'Complete 10 courses', '👑', 'courses_completed', 10, 80, 'gold'),
    ]
    
    for achievement_id, name, description, icon, criteria_type, criteria_value, points, tier in default_achievements:
        cursor.execute(f"""
            INSERT INTO {DB_SCHEMA}.achievements 
            (achievement_id, name, description, icon, criteria_type, criteria_value, points, tier, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (achievement_id) DO NOTHING
        """, (achievement_id, name, description, icon, criteria_type, criteria_value, points, tier))
    
    logger.info("✓ Default achievements seeded")


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
    
    # Comprehensive Audit Log Table - captures all database changes without overwriting
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.audit_log (
        id SERIAL PRIMARY KEY,
        audit_id VARCHAR(64) UNIQUE NOT NULL,
        table_name VARCHAR(100) NOT NULL,
        record_id VARCHAR(100) NOT NULL,
        action_type VARCHAR(20) NOT NULL,
        old_values JSONB,
        new_values JSONB,
        changed_fields JSONB,
        performed_by VARCHAR(64),
        performed_by_id INTEGER,
        ip_address INET,
        user_agent TEXT,
        request_id VARCHAR(100),
        session_id VARCHAR(100),
        application_source VARCHAR(50) DEFAULT 'admin_panel',
        -- Geolocation data derived from IP address
        country_code VARCHAR(10),
        country_name VARCHAR(100),
        region VARCHAR(100),
        city VARCHAR(100),
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8),
        timezone VARCHAR(50),
        isp_name VARCHAR(200),
        is_proxy BOOLEAN,
        -- Additional context
        additional_context JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create indexes for efficient audit log querying
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_audit_log_table_record 
        ON {DB_SCHEMA}.audit_log(table_name, record_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_audit_log_action 
        ON {DB_SCHEMA}.audit_log(action_type)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_audit_log_performed_by 
        ON {DB_SCHEMA}.audit_log(performed_by)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_audit_log_created_at 
        ON {DB_SCHEMA}.audit_log(created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_audit_log_table_action 
        ON {DB_SCHEMA}.audit_log(table_name, action_type, created_at DESC)
    """)
    
    # Indexes for geolocation queries
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_audit_log_country 
        ON {DB_SCHEMA}.audit_log(country_code)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_audit_log_city 
        ON {DB_SCHEMA}.audit_log(city)
    """)
    
    logger.info("✓ System tables created: system_logs, system_health, audit_log")


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


def create_content_views_table(cursor):
    """Create content views tracking table for analytics"""
    logger.info("Creating content views tracking table...")

    # Content views table - tracks all content views for analytics
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.content_views (
        id SERIAL PRIMARY KEY,
        view_id VARCHAR(64) UNIQUE NOT NULL,
        content_id VARCHAR(100) NOT NULL,
        content_type VARCHAR(50) NOT NULL,
        user_id VARCHAR(64),
        session_id VARCHAR(100),
        ip_address INET,
        user_agent TEXT,
        viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        view_duration INTEGER DEFAULT 0,
        referrer_url TEXT,
        device_type VARCHAR(20) DEFAULT 'desktop',
        browser VARCHAR(50),
        country_code VARCHAR(10),
        is_unique_view BOOLEAN DEFAULT FALSE
    )
    """)

    # Create indexes for efficient querying
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_content_views_content_id
        ON {DB_SCHEMA}.content_views(content_id)
    """)

    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_content_views_content_type
        ON {DB_SCHEMA}.content_views(content_type)
    """)

    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_content_views_user_id
        ON {DB_SCHEMA}.content_views(user_id)
    """)

    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_content_views_viewed_at
        ON {DB_SCHEMA}.content_views(viewed_at)
    """)

    # Aggregated content views summary table for fast analytics queries
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.content_views_summary (
        id SERIAL PRIMARY KEY,
        content_id VARCHAR(100) NOT NULL,
        content_type VARCHAR(50) NOT NULL,
        total_views INTEGER DEFAULT 0,
        unique_views INTEGER DEFAULT 0,
        total_view_duration INTEGER DEFAULT 0,
        last_viewed_at TIMESTAMP,
        views_today INTEGER DEFAULT 0,
        views_this_week INTEGER DEFAULT 0,
        views_this_month INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(content_id, content_type)
    )
    """)

    # Create index on content_views_summary
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_content_views_summary_total
        ON {DB_SCHEMA}.content_views_summary(total_views DESC)
    """)

    logger.info("✓ Content views tables created: content_views, content_views_summary")


def create_domains_table(cursor):
    """Create domains table for content categorization"""
    logger.info("Creating domains table...")

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.domains (
        id SERIAL PRIMARY KEY,
        domain_id VARCHAR(64) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        slug VARCHAR(200) UNIQUE NOT NULL,
        description TEXT,
        icon VARCHAR(50) DEFAULT '📚',
        color VARCHAR(20) DEFAULT '#2563eb',
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create index on name and slug for fast lookups
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_domains_name
        ON {DB_SCHEMA}.domains(name)
    """)

    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_domains_active
        ON {DB_SCHEMA}.domains(is_active)
    """)

    # Insert default domains if table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {DB_SCHEMA}.domains")
    if cursor.fetchone()[0] == 0:
        default_domains = [
            ('Computer Science', 'computer-science', 'Programming and computational thinking', '💻', '#2563eb'),
            ('Object-Spatial Programming', 'object-spatial-programming', 'JAC language and OSP concepts', '🔷', '#7c3aed'),
            ('Data Science', 'data-science', 'Data analysis and machine learning', '📊', '#059669'),
            ('Web Development', 'web-development', 'Frontend and backend web technologies', '🌐', '#0891b2'),
            ('Mathematics', 'mathematics', 'Mathematical foundations', '🔢', '#dc2626'),
        ]
        for name, slug, desc, icon, color in default_domains:
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.domains (domain_id, name, slug, description, icon, color)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (f"domain_{slug}", name, slug, desc, icon, color))

    logger.info("✓ Domains table created with default data")


def create_sync_engine_tables(cursor):
    """Create sync engine tables for PostgreSQL-Neo4j synchronization"""
    logger.info("Creating sync engine tables...")

    # Create custom enum types
    cursor.execute(f"""
        DO $$ BEGIN
            CREATE TYPE sync_event_status_enum AS ENUM (
                'PENDING', 'PUBLISHED', 'PROCESSING',
                'COMPLETED', 'FAILED', 'SKIPPED'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    cursor.execute(f"""
        DO $$ BEGIN
            CREATE TYPE conflict_resolution_status_enum AS ENUM (
                'DETECTED', 'RESOLVED', 'MANUAL_REVIEW', 'IGNORED'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create sync_event_log table (outbox pattern)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.sync_event_log (
            id SERIAL PRIMARY KEY,
            event_id VARCHAR(64) NOT NULL UNIQUE,
            correlation_id VARCHAR(64) NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            payload JSONB NOT NULL DEFAULT '{{}}',
            source_version INTEGER NOT NULL DEFAULT 0,
            status sync_event_status_enum NOT NULL DEFAULT 'PENDING',
            retry_count INTEGER NOT NULL DEFAULT 0,
            max_retries INTEGER NOT NULL DEFAULT 3,
            error_message TEXT,
            error_trace TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP,
            completed_at TIMESTAMP,
            redis_message_id VARCHAR(100)
        )
    """)

    # Create sync_status table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.sync_status (
            id SERIAL PRIMARY KEY,
            entity_id VARCHAR(100) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            is_synced BOOLEAN NOT NULL DEFAULT FALSE,
            last_synced_at TIMESTAMP,
            last_synced_version INTEGER,
            source_version INTEGER NOT NULL DEFAULT 0,
            neo4j_version INTEGER,
            neo4j_checksum VARCHAR(256),
            has_pending_changes BOOLEAN NOT NULL DEFAULT FALSE,
            has_conflict BOOLEAN NOT NULL DEFAULT FALSE,
            conflict_count INTEGER NOT NULL DEFAULT 0,
            last_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_id, entity_type)
        )
    """)

    # Create sync_conflicts table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.sync_conflicts (
            id SERIAL PRIMARY KEY,
            entity_id VARCHAR(100) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            conflict_type VARCHAR(50) NOT NULL,
            source_version INTEGER NOT NULL,
            target_version INTEGER,
            source_data JSONB NOT NULL,
            target_data JSONB,
            difference_summary TEXT,
            resolution_status conflict_resolution_status_enum NOT NULL DEFAULT 'DETECTED',
            resolution_method VARCHAR(50),
            resolved_by VARCHAR(100),
            resolution_notes TEXT,
            event_id VARCHAR(64),
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        )
    """)

    # Create reconciliation_runs table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.reconciliation_runs (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(64) NOT NULL UNIQUE,
            run_type VARCHAR(50) NOT NULL,
            entities_checked INTEGER NOT NULL DEFAULT 0,
            inconsistencies_found INTEGER NOT NULL DEFAULT 0,
            inconsistencies_repaired INTEGER NOT NULL DEFAULT 0,
            conflicts_detected INTEGER NOT NULL DEFAULT 0,
            conflicts_resolved INTEGER NOT NULL DEFAULT 0,
            failed_entities INTEGER NOT NULL DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            duration_seconds INTEGER,
            status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
            error_message TEXT,
            batch_size INTEGER NOT NULL DEFAULT 50,
            entities_included TEXT
        )
    """)

    # Create helper function for auto-updating timestamps
    cursor.execute(f"""
        CREATE OR REPLACE FUNCTION {DB_SCHEMA}.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Create triggers (will be skipped if they already exist)
    try:
        cursor.execute(f"""
            DROP TRIGGER IF EXISTS update_sync_event_log_updated_at ON {DB_SCHEMA}.sync_event_log;
            CREATE TRIGGER update_sync_event_log_updated_at
                BEFORE UPDATE ON {DB_SCHEMA}.sync_event_log
                FOR EACH ROW
                EXECUTE FUNCTION {DB_SCHEMA}.update_updated_at_column();
        """)
        cursor.execute(f"""
            DROP TRIGGER IF EXISTS update_sync_status_updated_at ON {DB_SCHEMA}.sync_status;
            CREATE TRIGGER update_sync_status_updated_at
                BEFORE UPDATE ON {DB_SCHEMA}.sync_status
                FOR EACH ROW
                EXECUTE FUNCTION {DB_SCHEMA}.update_updated_at_column();
        """)
    except Exception as e:
        logger.debug(f"Triggers might already exist: {e}")

    logger.info("✓ Sync engine tables created: sync_event_log, sync_status, sync_conflicts, reconciliation_runs")


def create_sync_engine_indexes(cursor):
    """Create indexes for sync engine tables"""
    logger.info("Creating sync engine indexes...")

    sync_indexes = [
        # Sync event log indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_event_log_event_id ON {DB_SCHEMA}.sync_event_log(event_id)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_event_log_correlation_id ON {DB_SCHEMA}.sync_event_log(correlation_id)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_event_log_entity ON {DB_SCHEMA}.sync_event_log(entity_id, entity_type)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_event_log_status ON {DB_SCHEMA}.sync_event_log(status)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_event_log_retry ON {DB_SCHEMA}.sync_event_log(status, retry_count) WHERE status IN ('PENDING', 'PUBLISHED', 'FAILED')",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_event_log_created ON {DB_SCHEMA}.sync_event_log(created_at DESC)",

        # Sync status indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_status_entity ON {DB_SCHEMA}.sync_status(entity_id, entity_type)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_status_synced ON {DB_SCHEMA}.sync_status(is_synced)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_status_pending ON {DB_SCHEMA}.sync_status(has_pending_changes) WHERE has_pending_changes = TRUE",

        # Sync conflicts indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_conflicts_entity ON {DB_SCHEMA}.sync_conflicts(entity_id, entity_type)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_conflicts_status ON {DB_SCHEMA}.sync_conflicts(resolution_status) WHERE resolution_status IN ('DETECTED', 'MANUAL_REVIEW')",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_sync_conflicts_detected ON {DB_SCHEMA}.sync_conflicts(detected_at DESC)",

        # Reconciliation runs indexes
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_reconciliation_runs_status ON {DB_SCHEMA}.reconciliation_runs(status)",
        f"CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_reconciliation_runs_started ON {DB_SCHEMA}.reconciliation_runs(started_at DESC)",
    ]

    for index_query in sync_indexes:
        try:
            cursor.execute(index_query)
        except Exception as e:
            logger.debug(f"Sync index might already exist: {e}")

    logger.info("✓ Sync engine indexes created")


def create_notification_tables(cursor):
    """Create notification-related tables for in-app notifications"""
    logger.info("Creating notification tables...")
    
    # Notifications table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            type VARCHAR(50) NOT NULL CHECK (type IN (
                'ACHIEVEMENT',
                'COURSE_MILESTONE',
                'CONTENT_UPDATE',
                'COMMUNITY_REPLY',
                'STREAK_REMINDER',
                'AI_RESPONSE',
                'SYSTEM_ANNOUNCEMENT'
            )),
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            link VARCHAR(500),
            is_read BOOLEAN DEFAULT FALSE,
            is_archived BOOLEAN DEFAULT FALSE,
            metadata JSONB DEFAULT '{{}}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Notification preferences table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.notification_preferences (
            user_id INTEGER PRIMARY KEY REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            email_enabled BOOLEAN DEFAULT TRUE,
            push_enabled BOOLEAN DEFAULT TRUE,
            types_config JSONB DEFAULT '{{
                "ACHIEVEMENT": true,
                "COURSE_MILESTONE": true,
                "CONTENT_UPDATE": true,
                "COMMUNITY_REPLY": true,
                "STREAK_REMINDER": true,
                "AI_RESPONSE": true,
                "SYSTEM_ANNOUNCEMENT": true
            }}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Create indexes for efficient querying
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_notifications_user_id 
        ON {DB_SCHEMA}.notifications(user_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_notifications_user_unread 
        ON {DB_SCHEMA}.notifications(user_id, is_read) WHERE is_read = FALSE
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_notifications_created_at 
        ON {DB_SCHEMA}.notifications(user_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_notifications_type 
        ON {DB_SCHEMA}.notifications(type)
    """)
    
    logger.info("✓ Notification tables created: notifications, notification_preferences")


def create_testimonials_table(cursor):
    """Create testimonials table for user reviews and feedback"""
    logger.info("Creating testimonials table...")
    
    # Testimonials table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.testimonials (
            id SERIAL PRIMARY KEY,
            testimonial_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER REFERENCES {DB_SCHEMA}.users(id) ON DELETE SET NULL,
            author_name VARCHAR(100) NOT NULL,
            author_role VARCHAR(100),
            author_avatar VARCHAR(500),
            content TEXT NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            is_approved BOOLEAN DEFAULT FALSE,
            is_featured BOOLEAN DEFAULT FALSE,
            is_published BOOLEAN DEFAULT TRUE,
            category VARCHAR(50) DEFAULT 'general',
            metadata JSONB DEFAULT '{{}}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_testimonials_user_id 
        ON {DB_SCHEMA}.testimonials(user_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_testimonials_published 
        ON {DB_SCHEMA}.testimonials(is_published, is_approved) 
        WHERE is_published = TRUE AND is_approved = TRUE
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_testimonials_featured 
        ON {DB_SCHEMA}.testimonials(is_featured, is_published) 
        WHERE is_featured = TRUE AND is_published = TRUE
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_testimonials_rating 
        ON {DB_SCHEMA}.testimonials(rating DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_testimonials_created 
        ON {DB_SCHEMA}.testimonials(created_at DESC)
    """)
    
    logger.info("✓ Testimonials table created: testimonials")


def create_contact_messages_table(cursor):
    """Create contact messages table for storing contact form submissions"""
    logger.info("Creating contact messages table...")
    
    # Contact messages table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.contact_messages (
            id SERIAL PRIMARY KEY,
            message_id VARCHAR(64) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            subject VARCHAR(255),
            message TEXT NOT NULL,
            contact_reason VARCHAR(50) DEFAULT 'general',
            status VARCHAR(20) DEFAULT 'new',
            is_read BOOLEAN DEFAULT FALSE,
            read_at TIMESTAMP,
            responded_at TIMESTAMP,
            responded_by VARCHAR(100),
            ip_address INET,
            user_agent TEXT,
            metadata JSONB DEFAULT '{{}}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_contact_messages_email 
        ON {DB_SCHEMA}.contact_messages(email)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_contact_messages_status 
        ON {DB_SCHEMA}.contact_messages(status, is_read)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_contact_messages_created 
        ON {DB_SCHEMA}.contact_messages(created_at DESC)
    """)
    
    logger.info("✓ Contact messages table created: contact_messages")


def create_chat_export_table(cursor):
    """Create chat export table for storing chat conversation exports"""
    logger.info("Creating chat export table...")
    
    # Chat export history table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.chat_exports (
            id SERIAL PRIMARY KEY,
            export_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            export_format VARCHAR(20) DEFAULT 'pdf',
            recipient_email VARCHAR(255),
            message_count INTEGER DEFAULT 0,
            conversation_title VARCHAR(255),
            file_path VARCHAR(500),
            file_size_bytes INTEGER,
            is_delivered BOOLEAN DEFAULT FALSE,
            delivered_at TIMESTAMP,
            delivery_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_chat_exports_user_id 
        ON {DB_SCHEMA}.chat_exports(user_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_chat_exports_created 
        ON {DB_SCHEMA}.chat_exports(created_at DESC)
    """)
    
    logger.info("✓ Chat export table created: chat_exports")


def create_user_activities_table(cursor):
    """Create user activities table for tracking user learning activities"""
    logger.info("Creating user activities table...")
    
    # User activities table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_activities (
            id SERIAL PRIMARY KEY,
            activity_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
                'lesson_completed',
                'quiz_passed',
                'achievement_unlocked',
                'streak_started',
                'course_enrolled',
                'module_completed',
                'level_up',
                'daily_goal_reached',
                'certificate_earned',
                'friend_joined',
                'comment_posted',
                'login'
            )),
            title VARCHAR(255),  -- Added title column
            description TEXT,
            metadata JSONB DEFAULT '{{}}',
            points_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for efficient querying
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_activities_user_id 
        ON {DB_SCHEMA}.user_activities(user_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_activities_type 
        ON {DB_SCHEMA}.user_activities(activity_type)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_activities_created 
        ON {DB_SCHEMA}.user_activities(user_id, created_at DESC)
    """)
    
    logger.info("✓ User activities table created: user_activities")


def create_platform_stats_table(cursor):
    """Create platform statistics table for storing aggregated platform metrics"""
    logger.info("Creating platform stats table...")
    
    # Platform stats table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.platform_stats (
            id SERIAL PRIMARY KEY,
            stat_date DATE NOT NULL UNIQUE,
            total_users INTEGER DEFAULT 0,
            active_users INTEGER DEFAULT 0,
            new_users INTEGER DEFAULT 0,
            total_concepts INTEGER DEFAULT 0,
            total_courses INTEGER DEFAULT 0,
            total_lessons INTEGER DEFAULT 0,
            total_learning_paths INTEGER DEFAULT 0,
            total_achievements INTEGER DEFAULT 0,
            total_sessions INTEGER DEFAULT 0,
            total_session_duration INTEGER DEFAULT 0,
            avg_session_duration INTEGER DEFAULT 0,
            completion_rate DECIMAL(5,2) DEFAULT 0,
            streak_active_users INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_platform_stats_date 
        ON {DB_SCHEMA}.platform_stats(stat_date DESC)
    """)
    
    logger.info("✓ Platform stats table created: platform_stats")


def create_collaboration_tables(cursor):
    """Create collaboration and community feature tables"""
    logger.info("Creating collaboration tables...")
    
    # User connections table (friends system)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_connections (
            id SERIAL PRIMARY KEY,
            connection_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            connected_user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'blocked')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, connected_user_id)
        )
    """)
    
    # Forums table (forum categories)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.forums (
            id SERIAL PRIMARY KEY,
            forum_id VARCHAR(64) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            category VARCHAR(50) DEFAULT 'general',
            icon VARCHAR(100) DEFAULT '💬',
            is_active BOOLEAN DEFAULT TRUE,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Forum threads table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.forum_threads (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(64) UNIQUE NOT NULL,
            forum_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.forums(forum_id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            is_pinned BOOLEAN DEFAULT FALSE,
            is_locked BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            last_reply_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Forum posts table (replies)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.forum_posts (
            id SERIAL PRIMARY KEY,
            post_id VARCHAR(64) UNIQUE NOT NULL,
            thread_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.forum_threads(thread_id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            parent_post_id VARCHAR(64) REFERENCES {DB_SCHEMA}.forum_posts(post_id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            like_count INTEGER DEFAULT 0,
            is_accepted_answer BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Content comments table (comments on lessons/courses)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.content_comments (
            id SERIAL PRIMARY KEY,
            comment_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            content_id VARCHAR(100) NOT NULL,
            content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('lesson', 'course', 'concept', 'learning_path')),
            parent_comment_id VARCHAR(64) REFERENCES {DB_SCHEMA}.content_comments(comment_id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            like_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ==============================================================================
    # UPVOTING AND REPUTATION SYSTEM TABLES
    # ==============================================================================
    
    # User reputation table - tracks reputation points and levels
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.user_reputation (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            reputation_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            total_upvotes_received INTEGER DEFAULT 0,
            total_downvotes_received INTEGER DEFAULT 0,
            total_accepted_answers INTEGER DEFAULT 0,
            helpful_flags_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
    """)
    
    # Reputation events table - tracks individual reputation changes
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.reputation_events (
            id SERIAL PRIMARY KEY,
            event_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
                'upvote_received',
                'downvote_received',
                'answer_accepted',
                'question_upvoted',
                'post_flagged_helpful',
                'mentorship_completed',
                'peer_review_completed',
                'streak_bonus',
                'achievement_bonus',
                'downvote_given',
                'flag_declined'
            )),
            points_change INTEGER NOT NULL,
            target_user_id INTEGER REFERENCES {DB_SCHEMA}.users(id) ON DELETE SET NULL,
            content_id VARCHAR(100),
            content_type VARCHAR(50),
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Upvotes table - tracks upvotes on content
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.content_upvotes (
            id SERIAL PRIMARY KEY,
            upvote_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            content_id VARCHAR(100) NOT NULL,
            content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('forum_post', 'forum_thread', 'content_comment', 'peer_review_feedback')),
            vote_type INTEGER NOT NULL CHECK (vote_type IN (1, -1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, content_id, content_type)
        )
    """)
    
    # ==============================================================================
    # STUDY GROUPS TABLES
    # ==============================================================================
    
    # Study groups table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.study_groups (
            id SERIAL PRIMARY KEY,
            group_id VARCHAR(64) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            learning_goal TEXT,
            target_topic VARCHAR(100),
            max_members INTEGER DEFAULT 10,
            is_public BOOLEAN DEFAULT TRUE,
            is_active BOOLEAN DEFAULT TRUE,
            created_by INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Study group members table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.study_group_members (
            id SERIAL PRIMARY KEY,
            membership_id VARCHAR(64) UNIQUE NOT NULL,
            group_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.study_groups(group_id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_id, user_id)
        )
    """)
    
    # Study group shared notes table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.study_group_notes (
            id SERIAL PRIMARY KEY,
            note_id VARCHAR(64) UNIQUE NOT NULL,
            group_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.study_groups(group_id) ON DELETE CASCADE,
            author_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            tags TEXT[],
            is_pinned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Study group goals table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.study_group_goals (
            id SERIAL PRIMARY KEY,
            goal_id VARCHAR(64) UNIQUE NOT NULL,
            group_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.study_groups(group_id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            target_completion_date DATE,
            is_completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Study group discussions table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.study_group_discussions (
            id SERIAL PRIMARY KEY,
            discussion_id VARCHAR(64) UNIQUE NOT NULL,
            group_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.study_groups(group_id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            topic VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            is_pinned BOOLEAN DEFAULT FALSE,
            reply_count INTEGER DEFAULT 0,
            last_reply_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Study group messages table (for real-time chat)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.study_group_messages (
            id SERIAL PRIMARY KEY,
            message_id VARCHAR(64) UNIQUE NOT NULL,
            group_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.study_groups(group_id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'link', 'file', 'milestone')),
            file_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ==============================================================================
    # MENTORSHIP SYSTEM TABLES
    # ==============================================================================
    
    # Mentorship profiles table - stores mentor information
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.mentorship_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            is_available BOOLEAN DEFAULT TRUE,
            expertise_areas TEXT[],
            years_experience INTEGER DEFAULT 0,
            teaching_style TEXT,
            bio TEXT,
            availability_hours VARCHAR(100),
            max_mentees INTEGER DEFAULT 3,
            current_mentees_count INTEGER DEFAULT 0,
            total_sessions_completed INTEGER DEFAULT 0,
            average_rating DECIMAL(3,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
    """)
    
    # Mentorship requests table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.mentorship_requests (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(64) UNIQUE NOT NULL,
            mentor_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            mentee_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'completed', 'cancelled')),
            topic VARCHAR(100),
            goals TEXT,
            preferred_schedule VARCHAR(100),
            message TEXT,
            response_message TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responded_at TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    
    # Mentorship sessions table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.mentorship_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(64) UNIQUE NOT NULL,
            mentorship_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.mentorship_requests(id) ON DELETE CASCADE,
            mentor_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            mentee_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            scheduled_at TIMESTAMP NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')),
            topic VARCHAR(200),
            notes TEXT,
            outcome TEXT,
            mentor_feedback TEXT,
            mentee_feedback TEXT,
            mentor_rating INTEGER CHECK (mentor_rating >= 1 AND mentor_rating <= 5),
            mentee_rating INTEGER CHECK (mentee_rating >= 1 AND mentee_rating <= 5),
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ==============================================================================
    # MODERATION TABLES
    # ==============================================================================
    
    # Content reports table - tracks user reports
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.content_reports (
            id SERIAL PRIMARY KEY,
            report_id VARCHAR(64) UNIQUE NOT NULL,
            reporter_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            content_id VARCHAR(100) NOT NULL,
            content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('forum_post', 'forum_thread', 'content_comment', 'study_group_note', 'study_group_message')),
            report_reason VARCHAR(50) NOT NULL CHECK (report_reason IN (
                'spam',
                'harassment',
                'inappropriate_content',
                'misinformation',
                'copyright',
                'other'
            )),
            additional_info TEXT,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'resolved', 'dismissed')),
            priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by INTEGER REFERENCES {DB_SCHEMA}.users(id) ON DELETE SET NULL,
            reviewed_at TIMESTAMP,
            resolution_notes TEXT
        )
    """)
    
    # Moderation actions table - tracks moderator actions
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.moderation_actions (
            id SERIAL PRIMARY KEY,
            action_id VARCHAR(64) UNIQUE NOT NULL,
            moderator_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            content_id VARCHAR(100) NOT NULL,
            content_type VARCHAR(50) NOT NULL,
            action_type VARCHAR(50) NOT NULL CHECK (action_type IN (
                'content_removed',
                'content_hidden',
                'user_warned',
                'user_suspended',
                'user_banned',
                'report_dismissed',
                'content_edited'
            )),
            reason TEXT,
            notes TEXT,
            is_reversed BOOLEAN DEFAULT FALSE,
            reversed_by INTEGER REFERENCES {DB_SCHEMA}.users(id) ON DELETE SET NULL,
            reversed_at TIMESTAMP,
            reversal_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Moderation queue table - content awaiting review
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.moderation_queue (
            id SERIAL PRIMARY KEY,
            queue_id VARCHAR(64) UNIQUE NOT NULL,
            content_id VARCHAR(100) NOT NULL,
            content_type VARCHAR(50) NOT NULL,
            report_id INTEGER REFERENCES {DB_SCHEMA}.content_reports(id) ON DELETE SET NULL,
            priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'resolved')),
            assigned_to INTEGER REFERENCES {DB_SCHEMA}.users(id) ON DELETE SET NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_at TIMESTAMP,
            resolved_at TIMESTAMP,
            resolution_summary TEXT
        )
    """)
    
    # ==============================================================================
    # PEER REVIEW SYSTEM TABLES
    # ==============================================================================
    
    # Peer review submissions table - work submitted for review
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.peer_review_submissions (
            id SERIAL PRIMARY KEY,
            submission_id VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('assignment', 'project', 'code', 'essay', 'presentation')),
            related_content_id VARCHAR(100),
            related_content_type VARCHAR(50),
            status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_review', 'completed', 'archived')),
            max_reviewers INTEGER DEFAULT 2,
            current_reviewers INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Peer review assignments table - tracks who reviews what
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.peer_review_assignments (
            id SERIAL PRIMARY KEY,
            assignment_id VARCHAR(64) UNIQUE NOT NULL,
            submission_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.peer_review_submissions(submission_id) ON DELETE CASCADE,
            reviewer_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'assigned' CHECK (status IN ('assigned', 'in_progress', 'completed', 'declined')),
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            deadline DATE,
            UNIQUE(submission_id, reviewer_id)
        )
    """)
    
    # Peer review feedback table - stores feedback given
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.peer_review_feedback (
            id SERIAL PRIMARY KEY,
            feedback_id VARCHAR(64) UNIQUE NOT NULL,
            assignment_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.peer_review_assignments(assignment_id) ON DELETE CASCADE,
            submission_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.peer_review_submissions(submission_id) ON DELETE CASCADE,
            reviewer_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
            strengths TEXT,
            improvements TEXT,
            comments TEXT,
            is_approved BOOLEAN DEFAULT FALSE,
            author_response TEXT,
            feedback_upvotes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ==============================================================================
    # INDEXES FOR ADVANCED COLLABORATION TABLES
    # ==============================================================================
    
    # User connections indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_connections_user 
        ON {DB_SCHEMA}.user_connections(user_id, status)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_connections_pending 
        ON {DB_SCHEMA}.user_connections(connected_user_id, status) WHERE status = 'pending'
    """)
    
    # Forums indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_forums_active 
        ON {DB_SCHEMA}.forums(is_active, sort_order)
    """)
    
    # Forum threads indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_forum_threads_forum 
        ON {DB_SCHEMA}.forum_threads(forum_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_forum_threads_user 
        ON {DB_SCHEMA}.forum_threads(user_id)
    """)
    
    # Forum posts indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_forum_posts_thread 
        ON {DB_SCHEMA}.forum_posts(thread_id, created_at ASC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_forum_posts_user 
        ON {DB_SCHEMA}.forum_posts(user_id)
    """)
    
    # Content comments indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_content_comments_content 
        ON {DB_SCHEMA}.content_comments(content_id, content_type, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_content_comments_user 
        ON {DB_SCHEMA}.content_comments(user_id)
    """)
    
    # Reputation indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_user_reputation_points 
        ON {DB_SCHEMA}.user_reputation(reputation_points DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_reputation_events_user 
        ON {DB_SCHEMA}.reputation_events(user_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_content_upvotes_content 
        ON {DB_SCHEMA}.content_upvotes(content_id, content_type)
    """)
    
    # Study groups indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_study_groups_active 
        ON {DB_SCHEMA}.study_groups(is_active, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_study_groups_topic 
        ON {DB_SCHEMA}.study_groups(target_topic)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_study_group_members_group 
        ON {DB_SCHEMA}.study_group_members(group_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_study_group_notes_group 
        ON {DB_SCHEMA}.study_group_notes(group_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_study_group_discussions_group 
        ON {DB_SCHEMA}.study_group_discussions(group_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_study_group_messages_group 
        ON {DB_SCHEMA}.study_group_messages(group_id, created_at DESC)
    """)
    
    # Mentorship indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_mentorship_profiles_available 
        ON {DB_SCHEMA}.mentorship_profiles(is_available, expertise_areas)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_mentorship_requests_mentor 
        ON {DB_SCHEMA}.mentorship_requests(mentor_id, status)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_mentorship_requests_mentee 
        ON {DB_SCHEMA}.mentorship_requests(mentee_id, status)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_mentorship_sessions_scheduled 
        ON {DB_SCHEMA}.mentorship_sessions(scheduled_at, status)
    """)
    
    # Moderation indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_content_reports_status 
        ON {DB_SCHEMA}.content_reports(status, priority)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_moderation_queue_status 
        ON {DB_SCHEMA}.moderation_queue(status, priority)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_moderation_actions_moderator 
        ON {DB_SCHEMA}.moderation_actions(moderator_id, created_at DESC)
    """)
    
    # Peer review indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_peer_review_submissions_user 
        ON {DB_SCHEMA}.peer_review_submissions(user_id, status)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_peer_review_assignments_reviewer 
        ON {DB_SCHEMA}.peer_review_assignments(reviewer_id, status)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_peer_review_feedback_submission 
        ON {DB_SCHEMA}.peer_review_feedback(submission_id)
    """)
    
    # Seed default forums if table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {DB_SCHEMA}.forums")
    if cursor.fetchone()[0] == 0:
        default_forums = [
            ('General Discussion', 'General topics and community announcements', 'general', '💬', 1),
            ('Help & Questions', 'Ask questions and get help from the community', 'help', '❓', 2),
            ('Jac Programming', 'Discuss Jac language and OSP concepts', 'programming', '📚', 3),
            ('Learning Tips', 'Share and discover learning strategies', 'tips', '💡', 4),
            ('Showcase', 'Share your projects and achievements', 'showcase', '🏆', 5),
            ('Announcements', 'Official platform announcements', 'announcements', '📢', 0),
        ]
        for name, desc, category, icon, sort_order in default_forums:
            cursor.execute(f"""
                INSERT INTO {DB_SCHEMA}.forums (forum_id, name, description, category, icon, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (f"forum_{category.lower().replace(' ', '_')}", name, desc, category, icon, sort_order))
    
    logger.info("✓ Collaboration tables created: user_connections, forums, forum_threads, forum_posts, content_comments")
    logger.info("✓ Reputation system tables created: user_reputation, reputation_events, content_upvotes")
    logger.info("✓ Study groups tables created: study_groups, study_group_members, study_group_notes, study_group_goals, study_group_discussions, study_group_messages")
    logger.info("✓ Mentorship tables created: mentorship_profiles, mentorship_requests, mentorship_sessions")
    logger.info("✓ Moderation tables created: content_reports, moderation_actions, moderation_queue")
    logger.info("✓ Peer review tables created: peer_review_submissions, peer_review_assignments, peer_review_feedback")


def create_code_snippets_tables(cursor):
    """Create code snippets, execution history, versioning, testing, and debugging tables"""
    logger.info("Creating code snippets and related tables...")
    
    # Code folders table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.code_folders (
            id VARCHAR(64) PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            parent_folder_id VARCHAR(64) REFERENCES {DB_SCHEMA}.code_folders(id) ON DELETE SET NULL,
            color VARCHAR(20) DEFAULT '#3b82f6',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Code snippets table - expanded with multi-language support
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.code_snippets (
            id VARCHAR(64) PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            code_content TEXT NOT NULL,
            language VARCHAR(50) DEFAULT 'jac',
            description TEXT,
            is_public BOOLEAN DEFAULT FALSE,
            folder_id VARCHAR(64) REFERENCES {DB_SCHEMA}.code_folders(id) ON DELETE SET NULL,
            execution_count INTEGER DEFAULT 0,
            last_executed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Execution history table - expanded with more status types
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.execution_history (
            id VARCHAR(64) PRIMARY KEY,
            snippet_id VARCHAR(64) REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE SET NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            code_content TEXT NOT NULL,
            status VARCHAR(30) NOT NULL CHECK (status IN ('success', 'error', 'timeout', 'memory_exceeded', 'output_exceeded')),
            output TEXT,
            error_message TEXT,
            execution_time_ms INTEGER DEFAULT 0,
            entry_point VARCHAR(100) DEFAULT 'init',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Snippet versions table for version history
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.snippet_versions (
            id VARCHAR(64) PRIMARY KEY,
            snippet_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE CASCADE,
            version_number INTEGER NOT NULL,
            code_content TEXT NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            change_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(snippet_id, version_number)
        )
    """)
    
    # Test cases table for auto-grading
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.test_cases (
            id VARCHAR(64) PRIMARY KEY,
            snippet_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE CASCADE,
            name VARCHAR(200) NOT NULL,
            input_data TEXT,
            expected_output TEXT NOT NULL,
            is_hidden BOOLEAN DEFAULT FALSE,
            order_index INTEGER DEFAULT 0,
            timeout_ms INTEGER DEFAULT 5000,
            created_by INTEGER REFERENCES {DB_SCHEMA}.users(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Test results table for recording test execution
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.test_results (
            id VARCHAR(64) PRIMARY KEY,
            test_case_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.test_cases(id) ON DELETE CASCADE,
            execution_id VARCHAR(64) REFERENCES {DB_SCHEMA}.execution_history(id) ON DELETE SET NULL,
            passed BOOLEAN NOT NULL,
            actual_output TEXT,
            execution_time_ms INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Error knowledge base for educational suggestions
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.error_knowledge_base (
            id VARCHAR(64) PRIMARY KEY,
            error_pattern VARCHAR(500) NOT NULL,
            error_type VARCHAR(100) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            suggestion TEXT NOT NULL,
            examples TEXT,
            documentation_link VARCHAR(500),
            language VARCHAR(50) DEFAULT 'jac',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Debug sessions table for step-through debugging
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.debug_sessions (
            id VARCHAR(64) PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            snippet_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'terminated')),
            current_line INTEGER,
            breakpoints TEXT,
            variables TEXT,
            call_stack TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for performance optimization
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_code_snippets_user 
        ON {DB_SCHEMA}.code_snippets(user_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_code_snippets_folder 
        ON {DB_SCHEMA}.code_snippets(folder_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_execution_history_user 
        ON {DB_SCHEMA}.execution_history(user_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_execution_history_snippet 
        ON {DB_SCHEMA}.execution_history(snippet_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_snippet_versions_snippet 
        ON {DB_SCHEMA}.snippet_versions(snippet_id, version_number DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_test_cases_snippet 
        ON {DB_SCHEMA}.test_cases(snippet_id, order_index)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_test_results_case 
        ON {DB_SCHEMA}.test_results(test_case_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_debug_sessions_user 
        ON {DB_SCHEMA}.debug_sessions(user_id, status)
    """)
    
    # Seed common error patterns for Python
    seed_error_patterns_python = [
        ('python', r'IndentationError', 'IndentationError',
         'Indentation Error',
         'Your code has incorrect indentation.',
         'Make sure all code blocks (like loops and functions) are properly aligned. Python uses spaces or tabs consistently. Check that you are using the same type of indentation throughout your file.',
         'if True:\n    print("Aligned properly")\nelse:\n    print("Also aligned")',
         'https://realpython.com/lessons/indentation-python/',
         1),
        ('python', r'SyntaxError', 'SyntaxError',
         'Syntax Error',
         'There is a syntax error in your code.',
         'Check for missing colons, parentheses, quotes, or brackets. The error message usually points to the exact location where the parser got confused.',
         None,
         'https://docs.python.org/3/tutorial/errors.html',
         2),
        ('python', r'NameError', 'NameError',
         'Undefined Variable',
         'You are using a variable that has not been defined.',
         'Make sure you have defined the variable before using it. Check for typos in variable names. Remember that Python is case-sensitive.',
         'x = 5\nprint(x)  # x is defined first',
         'https://realpython.com/python-errors-exceptions/',
         3),
        ('python', r'TypeError', 'TypeError',
         'Type Mismatch',
         'You are performing an operation on incompatible types.',
         'Check the types of your variables. You may need to convert strings to numbers using int() or float(), or concatenate strings properly.',
         'str_num = "10"\nprint(int(str_num))  # Convert string to int',
         'https://realpython.com/python-data-type-conversion/',
         4),
        ('python', r'ZeroDivisionError', 'ZeroDivisionError',
         'Division by Zero',
         'You are trying to divide by zero.',
         'Add a check to ensure the divisor is not zero before performing division.',
         'if divisor != 0:\n    result = dividend / divisor',
         'https://realpython.com/python-divmod/',
         5),
        ('python', r'IndexError', 'IndexError',
         'List Index Out of Range',
         'You are trying to access an index that does not exist.',
         'Make sure your index is within the bounds of the list or string. Remember that Python uses 0-based indexing.',
         'my_list = [1, 2, 3]\nprint(my_list[0])  # Valid: 0 to len-1',
         'https://realpython.com/python-lists-tuples/',
         6),
        ('python', r'KeyError', 'KeyError',
         'Dictionary Key Not Found',
         'You are trying to access a dictionary key that does not exist.',
         'Use the .get() method with a default value, or check if the key exists using "in" operator before accessing it.',
         'my_dict = {"a": 1}\nprint(my_dict.get("a"))  # Use get() to avoid KeyError',
         'https://realpython.com/python-dicts/',
         7),
        ('python', r'FileNotFoundError', 'FileNotFoundError',
         'File Not Found',
         'The file you are trying to read does not exist.',
         'Check the file path and make sure the file exists before trying to read it. You can use os.path.exists() to check.',
         'import os\nif os.path.exists("file.txt"):\n    with open("file.txt") as f:\n        content = f.read()',
         'https://realpython.com/working-with-large-python-files/',
         8),
        ('python', r'AttributeError', 'AttributeError',
         'Attribute Not Found',
         'The object does not have the attribute you are trying to access.',
         'Check the type of your object and make sure it has the attribute you are trying to use. Review the object documentation.',
         'my_list = [1, 2, 3]\nmy_list.append(4)  # append is a valid list method',
         'https://realpython.com/lessons/python-attributes/',
         9),
        ('python', r'ValueError', 'ValueError',
         'Invalid Value',
         'You are trying to convert a value to an inappropriate type.',
         'Check the format of your input data and make sure it can be converted to the expected type. Use try-except for invalid inputs.',
         'try:\n    num = int("123")\nexcept ValueError:\n    print("Cannot convert to int")',
         'https://realpython.com/python-exceptions/',
         10),
        ('python', r'ModuleNotFoundError', 'ModuleNotFoundError',
         'Module Not Found',
         'The Python module you are trying to import does not exist.',
         'Make sure the module is installed. Use pip to install missing modules: pip install module-name.',
         'import numpy as np  # Make sure numpy is installed first',
         'https://realpython.com/python-import/',
         11),
        ('python', r'ImportError', 'ImportError',
         'Import Error',
         'There is a problem importing a module or function.',
         'Check the import statement and make sure the module path is correct.',
         'from collections import OrderedDict',
         'https://docs.python.org/3/tutorial/modules.html',
         12),
    ]
    
    # Seed common error patterns for JavaScript
    seed_error_patterns_js = [
        ('javascript', r'Unexpected token', 'SyntaxError',
         'Unexpected Token',
         'There is a syntax error in your JavaScript code.',
         'Check for missing brackets, parentheses, semicolons, or commas. The error points to where the parser got confused.',
         None,
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_Types',
         1),
        ('javascript', r'ReferenceError', 'ReferenceError',
         'Reference Error',
         'You are using a variable that has not been defined.',
         'Make sure you have declared the variable with let, const, or var before using it.',
         'let x = 5;\nconsole.log(x);',
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Not_defined',
         2),
        ('javascript', r'TypeError', 'TypeError',
         'Type Error',
         'You are trying to use a value in an inappropriate way.',
         'Check if the value is null or undefined before trying to use it as an object.',
         'const obj = {a: 1};\nconsole.log(obj.a);',
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Called_on_incompatible_type',
         3),
        ('javascript', r'SyntaxError: Unexpected end of input', 'SyntaxError',
         'Unexpected End of Input',
         'Your code is missing a closing bracket, parenthesis, or brace.',
         'Make sure all opening braces have corresponding closing braces.',
         'function myFunction() {\n    // code\n}  // Proper closing brace',
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Control_flow_and_error_handling',
         4),
        ('javascript', r'Cannot read', 'TypeError',
         'Cannot Read Property',
         'You are trying to access a property of null or undefined.',
         'Add null checks before accessing properties, or use optional chaining (?.) operator.',
         'const obj = null;\nconsole.log(obj?.property);  // Safe with optional chaining',
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining',
         5),
        ('javascript', r'is not defined', 'ReferenceError',
         'Not Defined',
         'A variable or function you are trying to use has not been defined.',
         'Make sure all variables are declared before use. Check for typos in names.',
         'const myVar = "Hello";\nconsole.log(myVar);',
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_Types',
         6),
        ('javascript', r'NaN', 'ValueError',
         'Not a Number',
         'The result of a mathematical operation is not a valid number.',
         'Check your input values. Use isNaN() to check for NaN results.',
         'const result = 0 / 0;\nif (isNaN(result)) {\n    console.log("Result is NaN");\n}',
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/NaN',
         7),
        ('javascript', r'Cannot set properties of undefined', 'TypeError',
         'Cannot Set Property',
         'You are trying to set a property on an undefined object.',
         'Make sure the object is initialized before setting its properties.',
         'let obj = {};\nobj.property = "value";  // Object must exist first',
         'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Cant_assign_to_read_only_property',
         8),
    ]
    
    # Seed error patterns
    cursor.execute(f"SELECT COUNT(*) FROM {DB_SCHEMA}.error_knowledge_base")
    if cursor.fetchone()[0] == 0:
        for pattern in seed_error_patterns_python + seed_error_patterns_js:
            try:
                cursor.execute(f"""
                    INSERT INTO {DB_SCHEMA}.error_knowledge_base 
                    (id, error_pattern, error_type, title, description, suggestion, examples, documentation_link, language, priority)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (f"ekb_{uuid.uuid4().hex[:12]}", pattern[0], pattern[1], pattern[2], pattern[3], pattern[4], pattern[5], pattern[6], pattern[7], pattern[8]))
            except Exception as e:
                logger.debug(f"Could not seed error pattern: {e}")
    
    logger.info("✓ Code snippets and related tables created: code_folders, code_snippets, execution_history, snippet_versions, test_cases, test_results, error_knowledge_base, debug_sessions")


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
        create_courses_table(cursor)
        create_progress_tables(cursor)
        create_assessment_tables(cursor)
        create_gamification_tables(cursor)
        create_system_tables(cursor)
        create_ai_tables(cursor)
        create_content_views_table(cursor)
        create_domains_table(cursor)
        create_sync_engine_tables(cursor)
        create_sync_engine_indexes(cursor)
        create_notification_tables(cursor)
        create_testimonials_table(cursor)
        create_contact_messages_table(cursor)
        create_chat_export_table(cursor)
        create_platform_stats_table(cursor)
        create_user_activities_table(cursor)
        create_collaboration_tables(cursor)
        create_code_snippets_tables(cursor)
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
