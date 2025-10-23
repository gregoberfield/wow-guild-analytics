#!/usr/bin/env python3
"""
Migration script to add avatar_url column to Character table
"""
import sqlite3
import os

def migrate():
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'guild_data.db')
    
    print(f"Connecting to database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(character)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'avatar_url' in columns:
            print("⚠️  Column 'avatar_url' already exists, skipping migration")
            return
        
        # Add avatar_url column
        print("Adding avatar_url column to character table...")
        cursor.execute("""
            ALTER TABLE character 
            ADD COLUMN avatar_url VARCHAR(500)
        """)
        
        conn.commit()
        print("✅ Successfully added avatar_url column")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
