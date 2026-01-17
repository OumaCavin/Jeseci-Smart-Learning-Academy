#!/usr/bin/env python3
"""
Database Migration Script for Jeseci Smart Learning Academy

This script adds missing columns to the database schema that were identified
in the log analysis. These columns are defined in the models but may not exist
in the actual database if the schema wasn't properly synced.

Missing columns to add:
1. concepts.subcategory
2. user_achievements.notification_sent
3. user_lesson_progress.is_completed

Usage:
    python backend/scripts/migrate_add_columns.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import get_engine, text
from backend.config.logging_config import get_logger

logger = get_logger(__name__)


def run_migrations():
    """Run all required migrations"""
    
    engine = get_engine()
    
    migrations = [
        {
            'name': 'Add subcategory to concepts',
            'sql': """
                ALTER TABLE jeseci_academy.concepts 
                ADD COLUMN IF NOT EXISTS subcategory VARCHAR(100) DEFAULT NULL
            """,
            'verify': """
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'jeseci_academy' 
                AND table_name = 'concepts' 
                AND column_name = 'subcategory'
            """
        },
        {
            'name': 'Add notification_sent to user_achievements',
            'sql': """
                ALTER TABLE jeseci_academy.user_achievements 
                ADD COLUMN IF NOT EXISTS notification_sent BOOLEAN DEFAULT FALSE
            """,
            'verify': """
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'jeseci_academy' 
                AND table_name = 'user_achievements' 
                AND column_name = 'notification_sent'
            """
        },
        {
            'name': 'Add is_completed to user_lesson_progress',
            'sql': """
                ALTER TABLE jeseci_academy.user_lesson_progress 
                ADD COLUMN IF NOT EXISTS is_completed BOOLEAN DEFAULT FALSE
            """,
            'verify': """
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'jeseci_academy' 
                AND table_name = 'user_lesson_progress' 
                AND column_name = 'is_completed'
            """
        },
        {
            'name': 'Add notification_sent to user_badges',
            'sql': """
                ALTER TABLE jeseci_academy.user_badges 
                ADD COLUMN IF NOT EXISTS notification_sent BOOLEAN DEFAULT FALSE
            """,
            'verify': """
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'jeseci_academy' 
                AND table_name = 'user_badges' 
                AND column_name = 'notification_sent'
            """
        },
    ]
    
    logger.info("Starting database migrations...")
    
    with engine.connect() as conn:
        for migration in migrations:
            name = migration['name']
            sql = migration['sql']
            verify = migration['verify']
            
            try:
                # Check if column already exists
                result = conn.execute(text(verify))
                exists = result.fetchone() is not None
                
                if exists:
                    logger.info(f"✓ {name}: Column already exists, skipping")
                else:
                    # Add column
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✓ {name}: Column added successfully")
                    
            except Exception as e:
                logger.error(f"✗ {name}: Failed - {e}")
                continue
    
    logger.info("Database migrations completed!")
    
    # Verify all columns exist
    verify_all(engine)


def verify_all(engine):
    """Verify all required columns exist"""
    logger.info("\nVerifying all columns...")
    
    checks = [
        ('jeseci_academy', 'concepts', 'subcategory'),
        ('jeseci_academy', 'user_achievements', 'notification_sent'),
        ('jeseci_academy', 'user_lesson_progress', 'is_completed'),
        ('jeseci_academy', 'user_badges', 'notification_sent'),
    ]
    
    all_ok = True
    with engine.connect() as conn:
        for schema, table, column in checks:
            try:
                result = conn.execute(text(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_schema = '{schema}' 
                    AND table_name = '{table}' 
                    AND column_name = '{column}'
                """))
                exists = result.fetchone() is not None
                status = "✓" if exists else "✗"
                logger.info(f"{status} {schema}.{table}.{column}")
                if not exists:
                    all_ok = False
            except Exception as e:
                logger.error(f"✗ {schema}.{table}.{column}: {e}")
                all_ok = False
    
    if all_ok:
        logger.info("\n✓ All columns verified successfully!")
    else:
        logger.warning("\n⚠ Some columns are missing. Please check the errors above.")
    
    return all_ok


if __name__ == "__main__":
    run_migrations()
