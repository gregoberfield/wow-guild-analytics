#!/usr/bin/env python3
"""
Migration script to add CharacterProgressionHistory table to existing database.
This enables tracking of character level and item level changes over time.
"""

from app import create_app, db
from app.models import CharacterProgressionHistory

def migrate():
    """Add CharacterProgressionHistory table to the database."""
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Adding CharacterProgressionHistory table...")
        
        try:
            # Create the CharacterProgressionHistory table
            db.create_all()
            print("✓ CharacterProgressionHistory table created successfully!")
            
            # Verify table was created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'character_progression_history' in tables:
                print("✓ Verification successful: character_progression_history table exists")
                
                # Show table columns
                columns = inspector.get_columns('character_progression_history')
                print("\nTable structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                
                # Show indexes
                indexes = inspector.get_indexes('character_progression_history')
                if indexes:
                    print("\nIndexes:")
                    for idx in indexes:
                        print(f"  - {idx['name']}: {idx['column_names']}")
                
                # Show foreign keys
                foreign_keys = inspector.get_foreign_keys('character_progression_history')
                if foreign_keys:
                    print("\nForeign Keys:")
                    for fk in foreign_keys:
                        print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                
                print("\nMigration complete!")
                print("\nAbout this feature:")
                print("- Character progression is tracked automatically during guild syncs")
                print("- Records level and item level changes over time")
                print("- Progression history is deleted when a character leaves the guild")
                print("- View progression: Click the chart icon next to any character name")
                
                print("\nNext steps:")
                print("1. Sync your guild roster to start tracking character progression")
                print("2. Re-sync periodically to capture progression updates")
                print("3. Click the chart icon next to character names to view their history")
                
            else:
                print("✗ Error: Table was not created")
                return False
                
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
