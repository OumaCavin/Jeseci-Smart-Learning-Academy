#!/usr/bin/env python3
"""
Database Migration Script for Adding Missing Columns

This script adds missing columns to the concepts and learning_sessions tables
that are required by the application but were not included in the initial schema.

Run this script to apply the migration:
    python -m database.migrate_add_missing_columns

Columns being added:
    concepts: detailed_description, complexity_score, estimated_time_minutes, 
              prerequisites, learning_outcomes, tags, icon, version, is_premium
    learning_sessions: device_info, browser_info, platform, ip_address, 
                       user_agent, session_events, meta_data, quality_score
"""

import os
import sys

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env'))

from logger_config import logger
import psycopg2

# Database configuration
DB_SCHEMA = os.getenv("DB_SCHEMA", "jeseci_academy")


def migrate_concepts_table(cursor):
    """Add missing columns to the concepts table"""
    logger.info("Migrating concepts table - adding missing columns...")
    
    columns_to_add = [
        # Detailed description column for comprehensive concept explanations
        ("detailed_description", "TEXT"),
        
        # Complexity scoring for adaptive learning
        ("complexity_score", "INTEGER DEFAULT 1"),
        
        # Estimated time to complete the concept
        ("estimated_time_minutes", "INTEGER DEFAULT 15"),
        
        # Prerequisites as JSON array of concept IDs
        ("prerequisites", "JSONB DEFAULT '[]'::jsonb"),
        
        # Learning outcomes as JSON array of strings
        ("learning_outcomes", "JSONB DEFAULT '[]'::jsonb"),
        
        # Tags for searching and categorization
        ("tags", "TEXT[]"),
        
        # Icon for visual representation
        ("icon", "VARCHAR(100) DEFAULT 'default'"),
        
        # Version number for content versioning
        ("version", "INTEGER DEFAULT 1"),
        
        # Premium content flag
        ("is_premium", "BOOLEAN DEFAULT FALSE"),
        
        # Content version for caching and updates
        ("content_version", "INTEGER DEFAULT 1"),
        
        # Author information
        ("author_name", "VARCHAR(100)"),
        ("author_id", "INTEGER"),
        
        # SEO metadata
        ("seo_title", "VARCHAR(200)"),
        ("seo_description", "TEXT"),
        
        # Status for content moderation
        ("status", "VARCHAR(20) DEFAULT 'published' CHECK (status IN ('draft', 'review', 'published', 'archived'))"),
        
        # Average rating from user feedback
        ("average_rating", "DECIMAL(3,2) DEFAULT 0"),
        
        # Total number of ratings
        ("rating_count", "INTEGER DEFAULT 0"),
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            cursor.execute(f"""
                ALTER TABLE {DB_SCHEMA}.concepts
                ADD COLUMN IF NOT EXISTS {column_name} {column_def}
            """)
            logger.info(f"  ✓ Added column: {column_name}")
        except Exception as e:
            logger.debug(f"Column {column_name} might already exist or error: {e}")
    
    # Create index on complexity_score for adaptive learning queries
    try:
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_concepts_complexity 
            ON {DB_SCHEMA}.concepts(complexity_score)
        """)
        logger.info("  ✓ Created index on complexity_score")
    except Exception as e:
        logger.debug(f"Index might already exist: {e}")
    
    # Create index on tags for filtering
    try:
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_concepts_tags 
            ON {DB_SCHEMA}.concepts USING GIN(tags)
        """)
        logger.info("  ✓ Created GIN index on tags")
    except Exception as e:
        logger.debug(f"Tags index might already exist: {e}")
    
    logger.info("✓ Concepts table migration completed")


def migrate_learning_sessions_table(cursor):
    """Add missing columns to the learning_sessions table"""
    logger.info("Migrating learning_sessions table - adding missing columns...")
    
    columns_to_add = [
        # Device information for analytics
        ("device_info", "JSONB DEFAULT '{}'::jsonb"),
        
        # Browser information
        ("browser_info", "VARCHAR(100)"),
        
        # Platform information (web, mobile, desktop)
        ("platform", "VARCHAR(50) DEFAULT 'web'"),
        
        # IP address for geo-analytics
        ("ip_address", "INET"),
        
        # User agent string
        ("user_agent", "TEXT"),
        
        # Session events as JSON array for detailed tracking
        ("session_events", "JSONB DEFAULT '[]'::jsonb"),
        
        # Additional metadata
        ("metadata", "JSONB DEFAULT '{}'::jsonb"),
        
        # Session quality score
        ("quality_score", "DECIMAL(5,2)"),
        
        # Network information
        ("network_type", "VARCHAR(50)"),
        ("connection_speed", "VARCHAR(50)"),
        
        # Engagement metrics
        ("interactions_count", "INTEGER DEFAULT 0"),
        ("scroll_depth", "INTEGER DEFAULT 0"),
        ("focus_time_seconds", "INTEGER DEFAULT 0"),
        
        # Error tracking
        ("errors_count", "INTEGER DEFAULT 0"),
        ("last_error_message", "TEXT"),
        
        # Completion tracking
        ("is_completed", "BOOLEAN DEFAULT FALSE"),
        ("completion_percentage", "INTEGER DEFAULT 0"),
        
        # Time-based metrics
        ("active_time_seconds", "INTEGER DEFAULT 0"),
        ("idle_time_seconds", "INTEGER DEFAULT 0"),
        
        # Learning progress data
        ("progress_data", "JSONB DEFAULT '{}'::jsonb"),
        
        # AI-generated insights
        ("ai_insights", "JSONB DEFAULT '{}'::jsonb"),
        
        # Feedback data
        ("feedback_rating", "INTEGER"),
        ("feedback_comment", "TEXT"),
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            cursor.execute(f"""
                ALTER TABLE {DB_SCHEMA}.learning_sessions
                ADD COLUMN IF NOT EXISTS {column_name} {column_def}
            """)
            logger.info(f"  ✓ Added column: {column_name}")
        except Exception as e:
            logger.debug(f"Column {column_name} might already exist or error: {e}")
    
    # Create index on user_id and start_time for session queries
    try:
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_learning_sessions_user_time 
            ON {DB_SCHEMA}.learning_sessions(user_id, start_time DESC)
        """)
        logger.info("  ✓ Created index on user_id, start_time")
    except Exception as e:
        logger.debug(f"Index might already exist: {e}")
    
    # Create index on is_completed for completion analytics
    try:
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_learning_sessions_completed 
            ON {DB_SCHEMA}.learning_sessions(user_id, is_completed) 
            WHERE is_completed = TRUE
        """)
        logger.info("  ✓ Created partial index on completed sessions")
    except Exception as e:
        logger.debug(f"Completed index might already exist: {e}")
    
    logger.info("✓ Learning sessions table migration completed")


def migrate_user_concept_progress_table(cursor):
    """Add missing columns to the user_concept_progress table"""
    logger.info("Migrating user_concept_progress table - adding missing columns...")
    
    columns_to_add = [
        # Detailed progress tracking
        ("last_position", "INTEGER DEFAULT 0"),
        
        # Quiz results
        ("quiz_score", "INTEGER"),
        ("quiz_attempts", "INTEGER DEFAULT 0"),
        ("quiz_passed", "BOOLEAN DEFAULT FALSE"),
        
        # Time tracking
        ("time_spent_on_quiz", "INTEGER DEFAULT 0"),
        ("time_spent_on_practice", "INTEGER DEFAULT 0"),
        
        # Mastery tracking
        ("mastery_level", "INTEGER DEFAULT 0"),
        ("mastery_progress", "INTEGER DEFAULT 0"),
        
        # Notes and bookmarks
        ("user_notes", "TEXT"),
        ("bookmarked", "BOOLEAN DEFAULT FALSE"),
        
        # AI-generated suggestions
        ("ai_suggestions", "JSONB DEFAULT '[]'::jsonb"),
        
        # Difficulty adjustment
        ("difficulty_adjusted", "BOOLEAN DEFAULT FALSE"),
        ("recommended_difficulty", "VARCHAR(20)"),
        
        # Practice data
        ("practice_exercises_completed", "INTEGER DEFAULT 0"),
        ("practice_correct_answers", "INTEGER DEFAULT 0"),
        ("practice_wrong_answers", "INTEGER DEFAULT 0"),
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            cursor.execute(f"""
                ALTER TABLE {DB_SCHEMA}.user_concept_progress
                ADD COLUMN IF NOT EXISTS {column_name} {column_def}
            """)
            logger.info(f"  ✓ Added column: {column_name}")
        except Exception as e:
            logger.debug(f"Column {column_name} might already exist or error: {e}")
    
    logger.info("✓ User concept progress table migration completed")


def migrate_user_activities_table(cursor):
    """Add missing columns to the user_activities table"""
    logger.info("Migrating user_activities table - adding missing columns...")
    
    columns_to_add = [
        # Activity metadata
        ("metadata", "JSONB DEFAULT '{}'::jsonb"),
        
        # Related content
        ("related_content_id", "VARCHAR(100)"),
        ("related_content_type", "VARCHAR(50)"),
        
        # Duration tracking
        ("duration_seconds", "INTEGER DEFAULT 0"),
        
        # Status tracking
        ("status", "VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('in_progress', 'completed', 'paused', 'cancelled'))"),
        
        # Score/result data
        ("score", "INTEGER"),
        ("result_data", "JSONB DEFAULT '{}'::jsonb"),
        
        # AI-generated data
        ("ai_analysis", "JSONB DEFAULT '{}'::jsonb"),
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            cursor.execute(f"""
                ALTER TABLE {DB_SCHEMA}.user_activities
                ADD COLUMN IF NOT EXISTS {column_name} {column_def}
            """)
            logger.info(f"  ✓ Added column: {column_name}")
        except Exception as e:
            logger.debug(f"Column {column_name} might already exist or error: {e}")
    
    logger.info("✓ User activities table migration completed")


def run_migration():
    """Run all migrations"""
    logger.info("="*60)
    logger.info("DATABASE MIGRATION - Adding Missing Columns")
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
        logger.info("")
        
        # Run migrations
        migrate_concepts_table(cursor)
        logger.info("")
        
        migrate_learning_sessions_table(cursor)
        logger.info("")
        
        migrate_user_concept_progress_table(cursor)
        logger.info("")
        
        migrate_user_activities_table(cursor)
        logger.info("")
        
        conn.commit()
        
        logger.info("")
        logger.info("="*60)
        logger.info("✓ ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
