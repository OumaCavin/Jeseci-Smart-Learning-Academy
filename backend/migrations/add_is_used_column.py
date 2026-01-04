#!/usr/bin/env python3
"""
Migration script to add is_used column to password_reset_tokens table

This script fixes the issue where the password reset functionality fails
with: "column 'is_used' does not exist"

Run this script to migrate existing databases:
    python migrations/add_is_used_column.py
"""

import os
import sys
import psycopg2

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def migrate_is_used_column():
    """Add is_used column to password_reset_tokens table"""
    
    # Get database configuration
    config = {
        'host': os.getenv("POSTGRES_HOST", "localhost"),
        'port': int(os.getenv("POSTGRES_PORT", 5432)),
        'database': os.getenv("POSTGRES_DB", "jeseci_learning_academy"),
        'user': os.getenv("POSTGRES_USER", "jeseci_academy_user"),
        'password': os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
    }
    
    schema = os.getenv("DB_SCHEMA", "jeseci_academy")
    
    print(f"Connecting to database {config['database']} on {config['host']}:{config['port']}...")
    
    conn = None
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = %s AND table_name = 'password_reset_tokens'
            AND column_name = 'is_used'
        """, (schema,))
        
        if cursor.fetchone():
            print("✓ Column 'is_used' already exists. No migration needed.")
            cursor.close()
            return True
        
        print("Adding 'is_used' column to password_reset_tokens table...")
        
        # Add the is_used column
        cursor.execute(f"""
            ALTER TABLE {schema}.password_reset_tokens
            ADD COLUMN is_used BOOLEAN DEFAULT FALSE
        """)
        
        # Create index for faster lookups on is_used
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_password_reset_is_used
            ON {schema}.password_reset_tokens (is_used)
        """)
        
        conn.commit()
        cursor.close()
        
        print("✓ Migration successful! 'is_used' column added.")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Password Reset Tokens Migration")
    print("Adding 'is_used' column to password_reset_tokens table")
    print("=" * 60)
    print()
    
    success = migrate_is_used_column()
    
    print()
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed. Please check the error message above.")
        sys.exit(1)
