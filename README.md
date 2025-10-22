# WoW Guild Analytics

A comprehensive Flask application for tracking and analyzing World of Warcraft Classic guild rosters using the Battle.net API. Monitor member changes, track character progression, and visualize guild composition with interactive charts.

## Features

### Core Features
- **Guild Roster Management** - Sync and track multiple guild rosters
- **Character Progression Tracking** - Monitor individual character level and gear progression over time
- **Member History** - Complete audit trail of member additions and removals
- **Analytics Dashboard** - Interactive charts for class, race, spec, and level distributions
- **User Authentication** - Secure login system with role-based access control
- **Admin Panel** - User management interface for administrators
- **Dark Theme** - Modern, eye-friendly dark interface
- **Auto-cleanup** - Automatically removes members who left the guild during re-sync

## Quick Start

### Prerequisites
- Python 3.8+
- Battle.net Developer Account

### Installation

```bash
# Clone the repository
cd wow-guild-analytics

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Battle.net API credentials
# Edit config.py and add your Client ID and Secret

# Run database migrations
python migrate_add_users.py
python migrate_add_guild_history.py
python migrate_add_character_progression.py
python migrate_add_last_login.py

# Start the application
# For development:
python run.py
# OR
flask run

# For production:
./start_production.sh
```

### First Login

Default admin credentials:
```
Username: admin
Password: admin123
```
⚠️ **Change this password immediately after first login!**

Access the application at: **http://localhost:5000**

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Setup Guide](docs/SETUP.md)** - Complete installation and configuration instructions
- **[Features Guide](docs/FEATURES.md)** - Detailed description of all features and how to use them
- **[Technical Documentation](docs/TECHNICAL.md)** - Architecture, database schema, and implementation details

## Usage Workflow

1. **Login** - Access the application with your credentials
2. **Sync Guild Roster** - Navigate to Sync page, enter realm and guild name
3. **Sync Character Details** - Click "Sync Character Details" on guild page for full data
4. **View Analytics** - Explore charts and statistics on guild detail page
5. **Track History** - Click "View History" to see member additions/removals
6. **Monitor Progression** - Click chart icons next to character names to view their progression

## Technology Stack

- **Backend**: Flask 3.0.0, SQLAlchemy 3.1.1, Flask-Login 0.6.3
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **Frontend**: Bootstrap 5.3.0, Chart.js 4.4.0
- **API**: Battle.net World of Warcraft Classic API

## Project Structure


```
wow-guild-analytics/
├── app/                    # Application package
│   ├── models.py          # Database models
│   ├── routes.py          # Main routes
│   ├── auth.py            # Authentication
│   ├── admin.py           # Admin panel
│   ├── services.py        # Business logic
│   ├── bnet_api.py        # Battle.net API client
│   ├── templates/         # Jinja2 templates
│   └── static/            # CSS, JS, images
├── docs/                   # Documentation
├── instance/              # Database and instance files
├── config.py              # Configuration
├── run.py                 # Application entry point
└── migrate_*.py           # Database migrations
```

## API Endpoints

- `GET /api/guild/<id>/analytics` - Guild analytics JSON
- `GET /api/guild/<id>/characters` - Guild character list JSON

## Key Features

### Character Progression Tracking
- Automatic snapshots of level and item level during syncs
- Only records when values actually change (no duplicates)
- Visual charts showing progression over time
- Automatic cleanup when characters leave guild

### Member History
- Complete audit trail of all member changes
- Filterable by action type (added/removed)
- Pagination for large histories
- Summary statistics

### Analytics Dashboard
- Class and race distribution pie charts
- Level distribution by class (stacked columns)
- Level 60 breakdown by class
- Spec distribution for max-level characters
- All charts optimized for dark theme

## Configuration

Edit `config.py`:

```python
class Config:
    # Flask
    SECRET_KEY = 'your-secret-key-here'
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/guild_data.db'
    
    # Battle.net API
    BNET_CLIENT_ID = 'your-client-id'
    BNET_CLIENT_SECRET = 'your-client-secret'
    BNET_REGION = 'us'  # or 'eu', 'kr', 'tw', 'cn'
```

## Security Notes

- Change default admin password immediately
- Use strong SECRET_KEY in production
- Never commit real API credentials to version control
- Use environment variables for sensitive data in `.env` file
- HTTPS is required for production deployments (use Nginx + Let's Encrypt)
- See [Security Guide](docs/SECURITY.md) for detailed security practices
- See [Deployment Guide](docs/DEPLOYMENT.md) for production setup

## Deployment

### Development
```bash
flask run  # Auto-reload, debugging enabled
```

### Production
```bash
# Using Gunicorn (recommended)
./start_production.sh

# Or as a systemd service
sudo systemctl start wow-guild-analytics
```

See the [Deployment Guide](docs/DEPLOYMENT.md) for detailed production deployment instructions including:
- Gunicorn WSGI server setup
- Systemd service configuration
- Nginx reverse proxy setup
- SSL/TLS with Let's Encrypt
- Monitoring and maintenance
- Performance optimization

## Troubleshooting

**"No such table" error**
- Run all migration scripts in order

**"401 Unauthorized" from API**
- Verify Battle.net credentials in config.py

**"Character not found"**
- Some characters have private profiles
- Character may not be indexed by Battle.net yet

See [Setup Guide](docs/SETUP.md) for more troubleshooting tips.

## Support

For detailed documentation, see the `docs/` directory:
- Setup and installation: [docs/SETUP.md](docs/SETUP.md)
- Feature descriptions: [docs/FEATURES.md](docs/FEATURES.md)
- Technical details: [docs/TECHNICAL.md](docs/TECHNICAL.md)
- Security practices: [docs/SECURITY.md](docs/SECURITY.md)
- **Production deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**
