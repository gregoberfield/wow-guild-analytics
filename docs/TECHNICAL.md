# Technical Documentation

Technical details about the application architecture, implementation, and code structure.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Database Schema](#database-schema)
- [API Integration](#api-integration)
- [Code Structure](#code-structure)
- [Key Implementations](#key-implementations)

---

## Architecture Overview

### Technology Stack

**Backend:**
- Flask 3.0.0 - Web framework
- Flask-SQLAlchemy 3.1.1 - ORM for database operations
- Flask-Login 0.6.3 - User authentication and session management
- SQLite 3 - Database (can be swapped for PostgreSQL in production)

**Frontend:**
- Bootstrap 5.3.0 - CSS framework
- Bootstrap Icons - Icon library
- Chart.js 4.4.0 - Data visualization
- Vanilla JavaScript - Client-side interactions

**External APIs:**
- Battle.net OAuth 2.0 - API authentication
- Battle.net World of Warcraft Classic API - Game data

### Application Pattern

**Factory Pattern:**
- Application created via `create_app()` factory function
- Allows multiple instances with different configurations
- Enables easier testing

**Blueprint Architecture:**
- `main_bp` - Main application routes
- `auth_bp` - Authentication routes
- `admin_bp` - Administrative routes

**MVC-like Structure:**
- Models: `app/models.py`
- Views: `app/templates/`
- Controllers: `app/routes.py`, `app/admin.py`, `app/auth.py`
- Services: `app/services.py` (business logic)

---

## Database Schema

### User Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT 0 NOT NULL,
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    created_at DATETIME,
    last_login DATETIME
);
CREATE INDEX ix_user_username ON user(username);
CREATE INDEX ix_user_email ON user(email);
```

**Purpose:** User accounts with authentication and authorization

### Guild Table
```sql
CREATE TABLE guild (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    realm VARCHAR(100) NOT NULL,
    faction VARCHAR(20),
    member_count INTEGER,
    last_updated DATETIME
);
```

**Purpose:** Guild information and metadata

### Character Table
```sql
CREATE TABLE character (
    id INTEGER PRIMARY KEY,
    bnet_id BIGINT,
    name VARCHAR(100) NOT NULL,
    realm VARCHAR(100) NOT NULL,
    level INTEGER,
    character_class VARCHAR(50),
    race VARCHAR(50),
    gender VARCHAR(20),
    faction VARCHAR(20),
    achievement_points INTEGER,
    average_item_level INTEGER,
    equipped_item_level INTEGER,
    spec_name VARCHAR(50),
    rank INTEGER,
    last_updated DATETIME,
    guild_id INTEGER,
    FOREIGN KEY (guild_id) REFERENCES guild(id)
);
CREATE INDEX ix_character_bnet_id ON character(bnet_id);
```

**Purpose:** Character details and stats

### GuildMemberHistory Table
```sql
CREATE TABLE guild_member_history (
    id INTEGER PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    character_name VARCHAR(100) NOT NULL,
    character_level INTEGER,
    character_class VARCHAR(50),
    action VARCHAR(20) NOT NULL,  -- 'added' or 'removed'
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES guild(id)
);
CREATE INDEX ix_guild_member_history_timestamp ON guild_member_history(timestamp);
```

**Purpose:** Audit trail of member additions and removals

### CharacterProgressionHistory Table
```sql
CREATE TABLE character_progression_history (
    id INTEGER PRIMARY KEY,
    character_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    character_level INTEGER,
    average_item_level INTEGER,
    equipped_item_level INTEGER,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (character_id) REFERENCES character(id) ON DELETE CASCADE,
    FOREIGN KEY (guild_id) REFERENCES guild(id)
);
CREATE INDEX ix_character_progression_history_timestamp ON character_progression_history(timestamp);
```

**Purpose:** Track character progression over time

### Relationships

```
User (independent)

Guild 1---* Character (one-to-many)
Guild 1---* GuildMemberHistory (one-to-many)
Guild 1---* CharacterProgressionHistory (one-to-many)

Character 1---* CharacterProgressionHistory (one-to-many, cascade delete)
```

---

## API Integration

### Battle.net OAuth Flow

**Authentication:**
```python
# 1. Get access token
token_url = f"https://{region}.battle.net/oauth/token"
response = requests.post(
    token_url,
    auth=(client_id, client_secret),
    data={'grant_type': 'client_credentials'}
)
access_token = response.json()['access_token']
```

**API Requests:**
```python
# 2. Make authenticated requests
headers = {'Authorization': f'Bearer {access_token}'}
api_url = f"https://{region}.api.blizzard.com/..."
response = requests.get(api_url, headers=headers)
```

### API Endpoints Used

**Guild Roster:**
```
GET /data/wow/guild/{realm-slug}/{guild-name-slug}/roster
Namespace: profile-classic1x-{region}
```

**Character Profile:**
```
GET /profile/wow/character/{realm-slug}/{character-name-slug}
Namespace: profile-classic1x-{region}
```

**Character Specializations:**
```
GET /profile/wow/character/{realm-slug}/{character-name-slug}/specializations
Namespace: profile-classic1x-{region}
```

### Character Name Normalization

Special characters in names require URL encoding:
```python
def normalize_name(name):
    # Remove diacritics, handle special characters
    # Convert to lowercase
    # URL encode for API calls
    return urllib.parse.quote(normalized_name)
```

### Spec Extraction (Classic)

Classic doesn't have rigid specs, uses talent trees:
```python
def get_primary_spec_from_talents(specs):
    # Analyze talent point distribution across trees
    # Determine primary spec based on highest investment
    # Map to spec names (e.g., "Holy", "Protection", "Retribution")
```

---

## Code Structure

### Directory Layout
```
wow-guild-analytics/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models
│   ├── routes.py            # Main routes
│   ├── auth.py              # Authentication routes
│   ├── admin.py             # Admin routes
│   ├── services.py          # Business logic
│   ├── bnet_api.py          # Battle.net API client
│   ├── static/              # CSS, JS, images
│   │   ├── css/
│   │   │   └── style.css    # Dark theme styles
│   │   └── js/
│   │       └── main.js      # Client-side scripts
│   └── templates/           # Jinja2 templates
│       ├── base.html        # Base template
│       ├── index.html       # Home page
│       ├── guild_detail.html
│       ├── guild_history.html
│       ├── character_progression.html
│       ├── sync.html
│       ├── auth/
│       │   └── login.html
│       └── admin/
│           ├── index.html
│           ├── add_user.html
│           └── edit_user.html
├── instance/                # Instance-specific files
│   └── guild_data.db       # SQLite database
├── docs/                    # Documentation
├── logs/                    # Application logs
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── migrate_*.py            # Database migration scripts
```

### Key Components

**App Factory (`app/__init__.py`):**
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes import main_bp
    from app.auth import auth_bp
    from app.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app
```

**Models (`app/models.py`):**
- SQLAlchemy ORM models
- Relationships defined with `db.relationship()`
- Helper methods (e.g., `set_password()`, `check_password()`)
- `to_dict()` methods for JSON serialization

**Services (`app/services.py`):**
- `GuildService` - Business logic for guild operations
- `sync_guild_roster()` - Main sync method
- `get_guild_analytics()` - Analytics calculations
- API integration and data processing

**API Client (`app/bnet_api.py`):**
- `BattleNetAPI` class
- Token management and caching
- API request methods
- Error handling and retries

---

## Key Implementations

### Authentication System

**Password Hashing:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

**Login Required Decorator:**
```python
from flask_login import login_required

@main_bp.route('/sync', methods=['GET', 'POST'])
@login_required
def sync():
    # Only accessible to authenticated users
    pass
```

**Admin Required Decorator:**
```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
```

### Smart Progression Tracking

**Change Detection:**
```python
# Get most recent progression entry
last_progression = CharacterProgressionHistory.query.filter_by(
    character_id=character.id,
    guild_id=guild.id
).order_by(CharacterProgressionHistory.timestamp.desc()).first()

# Check for changes
if not last_progression:
    should_track = True  # First entry
else:
    level_changed = last_progression.character_level != character.level
    avg_ilvl_changed = last_progression.average_item_level != character.average_item_level
    equipped_ilvl_changed = last_progression.equipped_item_level != character.equipped_item_level
    
    should_track = level_changed or avg_ilvl_changed or equipped_ilvl_changed

# Only create entry if changed
if should_track:
    progression_entry = CharacterProgressionHistory(...)
    db.session.add(progression_entry)
```

### Cascade Deletes

**Model Configuration:**
```python
class Character(db.Model):
    progression_history = db.relationship(
        'CharacterProgressionHistory',
        backref='character',
        lazy=True,
        cascade='all, delete-orphan'  # Auto-delete on character removal
    )
```

**Explicit Deletion:**
```python
# Delete progression history when character leaves
CharacterProgressionHistory.query.filter_by(
    character_id=character.id,
    guild_id=guild.id
).delete()

db.session.delete(character)
```

### Dark Theme Implementation

**CSS Variables:**
```css
:root {
    --bg-primary: #000000;
    --bg-secondary: #1a1a1a;
    --text-primary: #ffffff;
    --text-secondary: #e0e0e0;
    --border-color: #333333;
}
```

**Chart.js Dark Theme:**
```javascript
Chart.defaults.color = '#e0e0e0';
Chart.defaults.borderColor = '#444';
Chart.defaults.backgroundColor = '#1a1a1a';
Chart.defaults.scale.grid.color = '#333';
```

### Pagination

**Backend:**
```python
page = request.args.get('page', 1, type=int)
per_page = 50

pagination = query.paginate(
    page=page,
    per_page=per_page,
    error_out=False
)

entries = pagination.items
```

**Template:**
```jinja2
{% for page_num in pagination.iter_pages(
    left_edge=1,
    right_edge=1,
    left_current=2,
    right_current=2
) %}
    {% if page_num %}
        <a href="{{ url_for('main.route', page=page_num) }}">
            {{ page_num }}
        </a>
    {% endif %}
{% endfor %}
```

### Error Handling

**Try-Except Blocks:**
```python
try:
    # API call or database operation
    result = risky_operation()
except SpecificException as e:
    current_app.logger.error(f"Error: {str(e)}")
    flash('User-friendly error message', 'error')
    return redirect(url_for('fallback_route'))
```

**Logging:**
```python
current_app.logger.info("Informational message")
current_app.logger.warning("Warning message")
current_app.logger.error("Error message")
current_app.logger.debug("Debug message")
```

---

## Performance Considerations

### Database Indexes
- `character.bnet_id` - Fast character lookups
- `user.username` and `user.email` - Fast authentication
- `*_history.timestamp` - Efficient time-based queries

### Query Optimization
- Use `db.session.flush()` to get IDs without full commit
- Batch operations when possible
- Use `first()` instead of `all()[0]`
- Limit query results with pagination

### Caching
- Battle.net access tokens cached in memory
- Consider adding Flask-Caching for frequently accessed data

### Async Considerations
- Character detail syncs can be slow for large guilds
- Consider background job queue (Celery) for production
- Provide progress indicators to users

---

## Security Best Practices

### Password Security
- Werkzeug password hashing (PBKDF2)
- Never store plaintext passwords
- Enforce password complexity in forms

### SQL Injection Prevention
- Use SQLAlchemy ORM (parameterized queries)
- Never concatenate user input into SQL

### XSS Prevention
- Jinja2 auto-escapes template variables
- Use `|safe` filter only for trusted content

### CSRF Protection
- Consider adding Flask-WTF for form CSRF tokens

### Session Security
- Use secure, random SECRET_KEY
- Set session cookie flags (secure, httponly, samesite)

### API Key Security
- Never commit real credentials to version control
- Use environment variables in production
- Rotate keys periodically

---

## Testing Recommendations

### Unit Tests
- Test models (User.set_password(), Character.to_dict())
- Test service methods (analytics calculations)
- Mock API calls in tests

### Integration Tests
- Test routes with authenticated/unauthenticated users
- Test database operations
- Test form submissions

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Password changes
- [ ] Guild roster sync
- [ ] Character details sync
- [ ] Member history tracking
- [ ] Progression tracking
- [ ] Analytics charts rendering
- [ ] Pagination on all list pages
- [ ] Admin user management
- [ ] Dark theme consistency

---

## Future Enhancements

### Potential Features
- Multi-guild comparison
- Export data to CSV/JSON
- Email notifications for member changes
- Scheduled automatic syncs
- REST API for external integrations
- Advanced analytics (turnover rates, activity patterns)
- Guild recruitment tracking
- Discord integration
- Mobile-responsive improvements

### Technical Improvements
- Migrate to PostgreSQL for production
- Add Redis for caching
- Implement Celery for background jobs
- Add comprehensive test suite
- Set up CI/CD pipeline
- Add API rate limiting
- Implement WebSocket for real-time updates
- Add data export/import functionality
