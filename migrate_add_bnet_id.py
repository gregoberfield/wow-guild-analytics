"""
Migration script to add bnet_id column to character table
"""
import sqlite3

db_path = 'instance/guild_data.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add bnet_id column if it doesn't exist (without UNIQUE constraint initially)
    cursor.execute('''
        ALTER TABLE character ADD COLUMN bnet_id INTEGER
    ''')
    
    conn.commit()
    print("✅ Successfully added bnet_id column to character table")
    print("ℹ️  Note: UNIQUE constraint will be enforced at the application level")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️  bnet_id column already exists")
    else:
        print(f"❌ Error: {e}")
finally:
    conn.close()
