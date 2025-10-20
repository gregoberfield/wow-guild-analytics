#!/usr/bin/env python3
"""
Migration script to add GuildMemberHistory table to existing database.
This enables tracking of member additions and removals during guild syncs.
"""

from app import create_app, db
from app.models import GuildMemberHistory

def migrate():
    """Add GuildMemberHistory table to the database."""
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Adding GuildMemberHistory table...")
        
        try:
            # Create the GuildMemberHistory table
            db.create_all()
            print("✓ GuildMemberHistory table created successfully!")
            
            # Verify table was created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'guild_member_history' in tables:
                print("✓ Verification successful: guild_member_history table exists")
                
                # Show table columns
                columns = inspector.get_columns('guild_member_history')
                print("\nTable structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                
                # Show indexes
                indexes = inspector.get_indexes('guild_member_history')
                if indexes:
                    print("\nIndexes:")
                    for idx in indexes:
                        print(f"  - {idx['name']}: {idx['column_names']}")
                
                print("\nMigration complete!")
                print("\nNext steps:")
                print("1. Sync your guild roster to start tracking member changes")
                print("2. Visit /guild/<id>/history to view the history log")
                
            else:
                print("✗ Error: Table was not created")
                return False
                
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
