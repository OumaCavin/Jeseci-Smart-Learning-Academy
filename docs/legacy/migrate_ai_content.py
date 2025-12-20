"""
Database Migration Script
Adds AI content generation fields to the Concept model
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import create_engine, text
from config.database import DATABASE_URL


def migrate_database():
    """Add AI content fields to existing database"""
    
    print("🔄 Running database migration for AI content generation...")
    print("=" * 60)
    
    # Get database connection
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(concepts)"))
            columns = [row[1] for row in result]
            
            print(f"📊 Current columns in concepts table: {len(columns)}")
            
            # Add new columns if they don't exist
            new_columns = [
                ("lesson_content", "TEXT"),
                ("lesson_generated_at", "TEXT"),
                ("lesson_model_used", "TEXT")
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in columns:
                    print(f"   ➕ Adding column: {column_name}")
                    conn.execute(text(f"ALTER TABLE concepts ADD COLUMN {column_name} {column_type}"))
                else:
                    print(f"   ✅ Column already exists: {column_name}")
            
            # Commit the changes
            conn.commit()
            print("\n✅ Database migration completed successfully!")
            
            # Verify the migration
            result = conn.execute(text("PRAGMA table_info(concepts)"))
            final_columns = [row[1] for row in result]
            
            print(f"\n📈 Final columns count: {len(final_columns)}")
            print("🆕 New AI content columns:")
            for column_name, _ in new_columns:
                if column_name in final_columns:
                    print(f"   ✅ {column_name}")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    
    print("\n" + "=" * 60)
    print("🎉 Database migration complete!")
    print("📚 Ready for AI content generation!")


def recreate_database():
    """Recreate database from scratch (for development/testing)"""
    
    print("🗑️  Recreating database from scratch...")
    print("=" * 60)
    
    # Remove existing database file
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"   🗑️  Removed existing database: {db_path}")
    
    # Import and create all tables
    from database.models import Base
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    
    print("   ✅ Created all database tables")
    print("\n🎉 Database recreated successfully!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration for AI content generation")
    parser.add_argument("--recreate", action="store_true", help="Recreate database from scratch")
    args = parser.parse_args()
    
    if args.recreate:
        recreate_database()
    else:
        migrate_database()
        
    print("\n🚀 You can now run: python test_ai_content_generation.py")