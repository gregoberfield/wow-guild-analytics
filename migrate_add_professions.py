#!/usr/bin/env python3
"""
Database migration to add profession columns to Character table.
Run this script to update your database schema.
"""

import sys
from app import create_app, db
from app.models import Character
from sqlalchemy import inspect

def migrate():
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("DATABASE MIGRATION: Add Profession Columns")
        print("=" * 70)
        
        # Check if columns already exist
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('character')]
        
        needs_migration = False
        
        if 'profession_1' not in columns:
            print("✓ profession_1 column needs to be added")
            needs_migration = True
        else:
            print("✓ profession_1 column already exists")
        
        if 'profession_2' not in columns:
            print("✓ profession_2 column needs to be added")
            needs_migration = True
        else:
            print("✓ profession_2 column already exists")
        
        if not needs_migration:
            print("\n✅ Database already up to date - no migration needed")
            return
        
        print("\n🔄 Running migration...")
        
        try:
            # Add columns if they don't exist
            if 'profession_1' not in columns:
                db.session.execute(db.text(
                    'ALTER TABLE character ADD COLUMN profession_1 VARCHAR(100)'
                ))
                print("✅ Added profession_1 column")
            
            if 'profession_2' not in columns:
                db.session.execute(db.text(
                    'ALTER TABLE character ADD COLUMN profession_2 VARCHAR(100)'
                ))
                print("✅ Added profession_2 column")
            
            db.session.commit()
            
            print("\n" + "=" * 70)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print("\nNext steps:")
            print("1. Sync character details to populate profession data:")
            print("   - Navigate to your guild page in the app")
            print("   - Click 'Sync Characters' button")
            print("2. Professions will be displayed in the character roster table")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    migrate()
