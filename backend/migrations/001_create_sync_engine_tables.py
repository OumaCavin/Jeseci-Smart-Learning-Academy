"""
Database Migration: Create Sync Engine Tables

This migration creates the tables required for the event-driven synchronization
system that maintains eventual consistency between PostgreSQL and Neo4j databases.

Tables Created:
- sync_event_log: Main table for tracking synchronization events (outbox pattern)
- sync_status: Tracks current synchronization status for each entity
- sync_conflicts: Records detected conflicts between PostgreSQL and Neo4j
- reconciliation_runs: Records reconciliation job runs for auditing

Author: Cavin Otieno
Date: 2025-12-26
"""

import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import get_engine
from sqlalchemy import text


def run_migration():
    """
    Main function to run the migration.
    
    This function orchestrates the entire migration process,
    creating all required tables for the sync engine.
    """
    print("=" * 80)
    print("Starting Sync Engine Tables Migration")
    print("=" * 80)
    print()
    
    try:
        # Get database engine
        engine = get_engine()
        print(f"Connected to database successfully.")
        print()
        
        # Get the SQL migration file path
        sql_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "001_create_sync_engine_tables.sql"
        )
        
        print(f"Reading SQL migration from: {sql_file_path}")
        
        # Read and execute the SQL file
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        # Split by semicolons to execute statements individually
        # This handles the DO blocks and other PostgreSQL-specific syntax better
        with engine.connect() as conn:
            # Execute the entire SQL script
            conn.execute(text(sql_content))
            conn.commit()
        
        print()
        print("=" * 80)
        print("Migration completed successfully!")
        print("=" * 80)
        print()
        print("The following tables have been created in the 'jeseci_academy' schema:")
        print("  1. sync_event_log - Tracks synchronization events (outbox pattern)")
        print("  2. sync_status - Tracks current sync status for entities")
        print("  3. sync_conflicts - Records detected conflicts between databases")
        print("  4. reconciliation_runs - Records reconciliation job runs")
        print()
        print("Custom enum types created:")
        print("  1. sync_event_status_enum")
        print("  2. conflict_resolution_status_enum")
        print()
        
        return True
        
    except Exception as e:
        print(f"\nMigration failed with error: {str(e)}")
        print("\nPlease check the error message and fix any issues.")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
