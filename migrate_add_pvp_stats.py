#!/usr/bin/env python3
"""
Migration script to add PvP statistics columns to the Character table.

This adds:
- honorable_kills (INTEGER): Total honorable kills from PvP combat
- pvp_rank (INTEGER): Classic WoW honor rank (0-14)

These fields are populated from the Battle.net API pvp-summary endpoint.
"""

import sqlite3
import os

def migrate_sqlite():
    """Add PvP columns to SQLite database"""
    # Get the script directory and construct the database path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'instance', 'guild_data.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(character)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'honorable_kills' in columns and 'pvp_rank' in columns:
            print("PvP columns already exist in SQLite database")
            return True
        
        # Add honorable_kills column
        if 'honorable_kills' not in columns:
            print("Adding honorable_kills column to Character table...")
            cursor.execute("""
                ALTER TABLE character 
                ADD COLUMN honorable_kills INTEGER
            """)
            print("✓ Added honorable_kills column")
        
        # Add pvp_rank column
        if 'pvp_rank' not in columns:
            print("Adding pvp_rank column to Character table...")
            cursor.execute("""
                ALTER TABLE character 
                ADD COLUMN pvp_rank INTEGER
            """)
            print("✓ Added pvp_rank column")
        
        conn.commit()
        print("\n✓ SQLite migration completed successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error during SQLite migration: {e}")
        return False
    finally:
        conn.close()

def migrate_postgresql():
    """Add PvP columns to PostgreSQL database"""
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT', 5432),
            database=os.getenv('POSTGRES_DATABASE'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            sslmode='require'
        )
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'character'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        if 'honorable_kills' in columns and 'pvp_rank' in columns:
            print("PvP columns already exist in PostgreSQL database")
            conn.close()
            return True
        
        # Add honorable_kills column
        if 'honorable_kills' not in columns:
            print("Adding honorable_kills column to Character table...")
            cursor.execute("""
                ALTER TABLE character 
                ADD COLUMN honorable_kills INTEGER
            """)
            print("✓ Added honorable_kills column")
        
        # Add pvp_rank column
        if 'pvp_rank' not in columns:
            print("Adding pvp_rank column to Character table...")
            cursor.execute("""
                ALTER TABLE character 
                ADD COLUMN pvp_rank INTEGER
            """)
            print("✓ Added pvp_rank column")
        
        conn.commit()
        conn.close()
        print("\n✓ PostgreSQL migration completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error during PostgreSQL migration: {e}")
        return False

def main():
    """Run migration for the appropriate database type"""
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    
    print(f"Running PvP stats migration for {db_type} database...")
    print("=" * 60)
    
    if db_type == 'postgresql':
        success = migrate_postgresql()
    else:
        success = migrate_sqlite()
    
    if success:
        print("\nMigration complete! You can now sync PvP statistics.")
        print("\nNext steps:")
        print("1. Update Character model in app/models.py to include new columns")
        print("2. Modify sync_character_details() in app/services.py to fetch PvP data")
        print("3. Run a character sync to populate the new columns")
    else:
        print("\nMigration failed. Please check the error messages above.")
    
    return success

if __name__ == '__main__':
    main()
