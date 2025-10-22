#!/usr/bin/env python3
"""
Migration script to add Task table for background task tracking

Run this after updating requirements.txt and installing new dependencies:
    pip install -r requirements.txt
    python migrate_add_tasks.py
"""

from app import create_app, db
from app.models import Task
import sys

def migrate():
    """Add Task table to database"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting migration: Adding Task table...")
        
        try:
            # Create Task table
            db.create_all()
            print("✅ Task table created successfully")
            
            # Verify table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'task' in tables:
                print("✅ Migration completed successfully!")
                print("\nTask table schema:")
                for column in inspector.get_columns('task'):
                    print(f"  - {column['name']}: {column['type']}")
                return True
            else:
                print("❌ Error: Task table was not created")
                return False
                
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
