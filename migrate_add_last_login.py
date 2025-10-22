#!/usr/bin/env python3
"""
Migration script to add last_login_timestamp column to Character table
"""
from app import create_app, db
from app.models import Character
from sqlalchemy import inspect

def migrate():
    app = create_app()
    with app.app_context():
        print("Starting migration: Add last_login_timestamp to Character table")
        print("=" * 80)
        
        # Check if column already exists
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('character')]
        
        if 'last_login_timestamp' in columns:
            print("✓ Column 'last_login_timestamp' already exists in Character table")
            print("No migration needed.")
            return
        
        print("Adding 'last_login_timestamp' column to Character table...")
        
        # Add the column using raw SQL (safer for existing databases)
        with db.engine.connect() as conn:
            conn.execute(db.text(
                "ALTER TABLE character ADD COLUMN last_login_timestamp BIGINT"
            ))
            conn.commit()
        
        print("✅ Column added successfully!")
        print("\nMigration complete!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Run a guild sync to populate the last_login_timestamp data")
        print("3. The 'Last Seen' column will appear in the guild roster")

if __name__ == '__main__':
    migrate()
