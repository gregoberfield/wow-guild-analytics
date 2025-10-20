#!/usr/bin/env python3
"""
Migration script to add User table to the database.
Run this after updating to the authentication version.
"""

from app import create_app, db
from app.models import User
import sys

def migrate():
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating User table...")
            db.create_all()
            
            # Check if any users exist
            user_count = User.query.count()
            
            if user_count == 0:
                print("\n" + "="*60)
                print("No users found. Creating default admin user...")
                print("="*60)
                
                # Create default admin user
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    is_active=True
                )
                admin.set_password('admin123')
                
                db.session.add(admin)
                db.session.commit()
                
                print("\n✅ Default admin user created successfully!")
                print("\nLogin credentials:")
                print("  Username: admin")
                print("  Password: admin123")
                print("\n⚠️  IMPORTANT: Please change the password immediately after logging in!")
                print("="*60 + "\n")
            else:
                print(f"✅ User table exists with {user_count} user(s)")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    migrate()
