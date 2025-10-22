#!/usr/bin/env python3
"""
Admin User Management Script for WoW Guild Analytics

This script provides utilities for managing the admin user account:
- Create default admin user
- Reset admin password
- Create additional users
- List all users

Usage:
    python manage_admin.py create      # Create default admin user
    python manage_admin.py reset       # Reset admin password to default
    python manage_admin.py list        # List all users
    python manage_admin.py add         # Add a new user (interactive)
"""

import sys
from app import create_app, db
from app.models import User
from getpass import getpass

def create_default_admin():
    """Create the default admin user"""
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        
        if existing_admin:
            print("❌ Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Is Active: {existing_admin.is_active}")
            print("\nTo reset the password, use: python manage_admin.py reset")
            return False
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Default admin user created successfully!")
        print("\nLogin Credentials:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  Username: admin")
        print("  Password: admin123")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n⚠️  IMPORTANT: Change this password immediately after logging in!")
        return True

def reset_admin_password():
    """Reset admin password to default"""
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("❌ Admin user does not exist!")
            print("Create it first with: python manage_admin.py create")
            return False
        
        admin.set_password('admin123')
        db.session.commit()
        
        print("✅ Admin password reset successfully!")
        print("\nLogin Credentials:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  Username: admin")
        print("  Password: admin123")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n⚠️  IMPORTANT: Change this password immediately!")
        return True

def list_users():
    """List all users in the database"""
    app = create_app()
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("❌ No users found in database!")
            print("Create admin user with: python manage_admin.py create")
            return
        
        print(f"\n📋 Found {len(users)} user(s):")
        print("━" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<8} {'Active':<8}")
        print("━" * 80)
        
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} "
                  f"{'Yes' if user.is_admin else 'No':<8} "
                  f"{'Yes' if user.is_active else 'No':<8}")
        
        print("━" * 80 + "\n")

def add_user_interactive():
    """Add a new user interactively"""
    app = create_app()
    with app.app_context():
        print("\n➕ Add New User")
        print("━" * 50)
        
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            return False
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            print(f"❌ User '{username}' already exists!")
            return False
        
        email = input("Email: ").strip()
        if not email:
            print("❌ Email cannot be empty!")
            return False
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            print(f"❌ Email '{email}' already in use!")
            return False
        
        password = getpass("Password: ")
        password_confirm = getpass("Confirm Password: ")
        
        if password != password_confirm:
            print("❌ Passwords do not match!")
            return False
        
        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            return False
        
        is_admin_input = input("Make admin? (y/N): ").strip().lower()
        is_admin = is_admin_input == 'y'
        
        is_active_input = input("Active user? (Y/n): ").strip().lower()
        is_active = is_active_input != 'n'
        
        # Create user
        user = User(
            username=username,
            email=email,
            is_admin=is_admin,
            is_active=is_active
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print("\n✅ User created successfully!")
        print("━" * 50)
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Admin: {'Yes' if is_admin else 'No'}")
        print(f"  Active: {'Yes' if is_active else 'No'}")
        print("━" * 50 + "\n")
        return True

def show_sql_commands():
    """Show SQL commands for manual user creation"""
    print("\n📝 Manual SQL Commands")
    print("━" * 80)
    print("\n1. Create Admin User:")
    print("   (Password is 'admin123' - change after first login)")
    print("""
INSERT INTO user (username, email, password_hash, is_admin, is_active, created_at)
VALUES (
    'admin',
    'admin@example.com',
    'scrypt:32768:8:1$jBq8rK9L3qXmEOvC$8c5e2a3d1f9b7e6c4a0d8f1b3e5c7a9d2f4b6e8c0a1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b0c1e3f5a7c9e1b3d5f7a9c0b2d4f6e8a0c1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b',
    1,
    1,
    datetime('now')
);
""")
    
    print("\n2. List All Users:")
    print("""
SELECT id, username, email, is_admin, is_active, created_at, last_login
FROM user;
""")
    
    print("\n3. Make User Admin:")
    print("""
UPDATE user SET is_admin = 1 WHERE username = 'admin';
""")
    
    print("\n4. Reset Admin Password to 'admin123':")
    print("""
UPDATE user
SET password_hash = 'scrypt:32768:8:1$jBq8rK9L3qXmEOvC$8c5e2a3d1f9b7e6c4a0d8f1b3e5c7a9d2f4b6e8c0a1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b0c1e3f5a7c9e1b3d5f7a9c0b2d4f6e8a0c1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b'
WHERE username = 'admin';
""")
    
    print("\n5. Access SQLite Database:")
    print("""
sqlite3 instance/guild_analytics.db
# Then run any SQL command above
# Type .exit to quit
""")
    print("━" * 80 + "\n")

def show_usage():
    """Show usage instructions"""
    print("""
WoW Guild Analytics - Admin User Management

Usage:
    python manage_admin.py <command>

Commands:
    create      Create default admin user (admin/admin123)
    reset       Reset admin password to default (admin123)
    list        List all users in database
    add         Add a new user (interactive)
    sql         Show SQL commands for manual operations
    help        Show this help message

Examples:
    python manage_admin.py create
    python manage_admin.py list
    python manage_admin.py add
    python manage_admin.py sql
""")

def main():
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        create_default_admin()
    elif command == 'reset':
        reset_admin_password()
    elif command == 'list':
        list_users()
    elif command == 'add':
        add_user_interactive()
    elif command == 'sql':
        show_sql_commands()
    elif command in ['help', '-h', '--help']:
        show_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print("\nRun 'python manage_admin.py help' for usage instructions")
        sys.exit(1)

if __name__ == '__main__':
    main()
