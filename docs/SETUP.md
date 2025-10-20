# Setup & Configuration Guide

Complete guide for setting up and configuring the WoW Guild Analytics application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Battle.net API Setup](#battlenet-api-setup)
- [Database Setup](#database-setup)
- [User Management](#user-management)
- [Running the Application](#running-the-application)

---

## Prerequisites

### Required Software
- Python 3.8 or higher
- pip (Python package manager)
- SQLite 3 (usually included with Python)

### Required Accounts
- Battle.net Developer Account (for API access)

---

## Installation

### 1. Clone or Download the Repository

```bash
cd /path/to/your/projects
# If using git:
git clone <repository-url> wow-guild-analytics
cd wow-guild-analytics
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements include:**
- Flask 3.0.0 - Web framework
- Flask-SQLAlchemy 3.1.1 - Database ORM
- Flask-Login 0.6.3 - Authentication
- Requests 2.31.0 - HTTP library for API calls
- Werkzeug 3.0.1 - Password hashing

---

## Battle.net API Setup

### 1. Create Battle.net Developer Account

1. Visit [https://develop.battle.net/](https://develop.battle.net/)
2. Log in with your Battle.net account
3. Navigate to "API Access" or "My Applications"

### 2. Create a New Client

1. Click "Create Client"
2. Fill in application details:
   - **Client Name:** WoW Guild Analytics (or your choice)
   - **Redirect URLs:** `http://localhost:5000/callback` (for development)
   - **Service:** World of Warcraft
3. Submit the form

### 3. Obtain Credentials

After creation, you'll receive:
- **Client ID** - Public identifier for your application
- **Client Secret** - Private key (keep secure!)

### 4. Configure Application

Edit `config.py` and add your credentials:

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/guild_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Battle.net API Configuration
    BNET_CLIENT_ID = 'your-client-id-here'
    BNET_CLIENT_SECRET = 'your-client-secret-here'
    BNET_REGION = 'us'  # or 'eu', 'kr', 'tw', 'cn'
```

**Security Notes:**
- Never commit `config.py` with real credentials to version control
- Use environment variables for production:
  ```python
  BNET_CLIENT_ID = os.environ.get('BNET_CLIENT_ID')
  BNET_CLIENT_SECRET = os.environ.get('BNET_CLIENT_SECRET')
  ```

### 5. Supported Regions

- `us` - Americas
- `eu` - Europe
- `kr` - Korea
- `tw` - Taiwan
- `cn` - China

---

## Database Setup

### 1. Create Instance Directory

The database will be stored in the `instance/` directory:

```bash
mkdir -p instance
```

### 2. Run Database Migrations

Run migrations in order to create all required tables:

```bash
# Create User table and default admin account
python migrate_add_users.py

# Create GuildMemberHistory table
python migrate_add_guild_history.py

# Create CharacterProgressionHistory table
python migrate_add_character_progression.py
```

**Migration Output:**
- Each script will confirm successful table creation
- Check for ✓ marks indicating success
- Review table structure and indexes

### 3. Verify Database

You can verify the database was created:

```bash
# Check that the database file exists
ls -la instance/guild_data.db

# Optional: View database schema with sqlite3
sqlite3 instance/guild_data.db ".schema"
```

**Expected Tables:**
- `user` - User accounts
- `guild` - Guild information
- `character` - Character details
- `guild_member_history` - Member addition/removal log
- `character_progression_history` - Character progression tracking

---

## User Management

### Default Admin Account

After running `migrate_add_users.py`, a default admin account is created:

```
Username: admin
Password: admin123
```

⚠️ **IMPORTANT:** Change this password immediately after first login!

### Changing Admin Password

1. Log in with default credentials
2. Navigate to Admin panel (`/admin/`)
3. Click "Edit" next to the admin user
4. Enter new password (twice for confirmation)
5. Click "Update User"

### Creating Additional Users

**Via Admin Panel (Recommended):**
1. Log in as admin
2. Navigate to `/admin/`
3. Click "Add New User"
4. Fill in details:
   - Username
   - Email
   - Password (twice)
   - Admin privileges (checkbox)
   - Active status (checkbox)
5. Click "Create User"

**Via Python Script:**
```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User(
        username='newuser',
        email='user@example.com',
        is_admin=False,
        is_active=True
    )
    user.set_password('secure-password-here')
    db.session.add(user)
    db.session.commit()
    print(f"User {user.username} created!")
```

---

## Running the Application

### Development Mode

Run the Flask development server:

```bash
python run.py
```

**Default Configuration:**
- Host: `127.0.0.1` (localhost)
- Port: `5000`
- Debug: `True`
- Auto-reload: Enabled

**Access the application:**
```
http://localhost:5000
```

### Production Mode

For production deployment, use a production WSGI server:

**Option 1: Gunicorn (Linux/Mac)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

**Option 2: Waitress (Windows-compatible)**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 --call app:create_app
```

**Production Checklist:**
- [ ] Change SECRET_KEY to a random, secure value
- [ ] Use environment variables for credentials
- [ ] Change default admin password
- [ ] Disable debug mode
- [ ] Set up HTTPS/SSL
- [ ] Configure proper logging
- [ ] Set up regular database backups
- [ ] Consider using PostgreSQL instead of SQLite
- [ ] Set up reverse proxy (nginx/Apache)

---

## Configuration Reference

### config.py Settings

```python
class Config:
    # Flask Configuration
    SECRET_KEY = 'your-secret-key'  # Change this!
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/guild_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Battle.net API
    BNET_CLIENT_ID = 'your-client-id'
    BNET_CLIENT_SECRET = 'your-client-secret'
    BNET_REGION = 'us'
    
    # Optional: Pagination
    ITEMS_PER_PAGE = 50
    
    # Optional: Session
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
```

### Environment Variables (Production)

```bash
export SECRET_KEY='random-secure-key-here'
export BNET_CLIENT_ID='your-client-id'
export BNET_CLIENT_SECRET='your-client-secret'
export BNET_REGION='us'
export DATABASE_URL='sqlite:///instance/guild_data.db'
```

---

## Troubleshooting

### Database Issues

**Error: "No such table"**
- Solution: Run all migration scripts in order

**Error: "Database is locked"**
- Solution: Close any open database connections
- Check for other processes accessing the database

### API Issues

**Error: "401 Unauthorized"**
- Check your Client ID and Client Secret in `config.py`
- Verify credentials are correct on Battle.net developer portal

**Error: "404 Not Found"**
- Verify realm and guild name slugs are correct
- Check that guild exists on the specified realm
- Ensure region is correct in config

**Error: "Character profile not found"**
- Some characters have private profiles
- Character may be too low level
- Character may not be properly indexed by Battle.net

### Authentication Issues

**Can't log in with default credentials**
- Ensure `migrate_add_users.py` was run successfully
- Check database for user records: `sqlite3 instance/guild_data.db "SELECT * FROM user;"`

**Forgot admin password**
- Run password reset script:
```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.set_password('new-password-here')
    db.session.commit()
    print("Password updated!")
```

---

## Next Steps

After setup is complete:

1. **First Login**
   - Navigate to `/auth/login`
   - Log in with admin credentials
   - Change default password

2. **Sync Your First Guild**
   - Navigate to `/sync`
   - Enter realm slug (e.g., `faerlina`)
   - Enter guild name slug (e.g., `my-guild`)
   - Click "Sync Guild Roster"

3. **Sync Character Details**
   - Navigate to the guild detail page
   - Click "Sync Character Details"
   - Wait for completion (may take several minutes)

4. **Explore Analytics**
   - View guild analytics on detail page
   - Check member history
   - View character progression

5. **Set Up Regular Syncing**
   - Sync regularly to track changes
   - Consider automated cron jobs for production

---

## Support & Resources

- **Battle.net API Documentation:** https://develop.battle.net/documentation
- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
