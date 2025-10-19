# WoW Guild Analytics

A Flask application that leverages the World of Warcraft Classic API to collect guild roster data and provide analytics on class distribution, race distribution, item levels, and more.

## Features

- Sync guild rosters from Battle.net API
- Track multiple guilds
- Analytics dashboards with charts
- Class and race distribution visualizations
- Character details including level, spec, and item level
- RESTful API endpoints for programmatic access

## Setup Instructions

### 1. Battle.net API Credentials

1. Go to https://develop.battle.net/access/clients
2. Create a new client
3. Note your Client ID and Client Secret

### 2. Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Battle.net credentials:
   ```
   BNET_CLIENT_ID=your-client-id-here
   BNET_CLIENT_SECRET=your-client-secret-here
   BNET_REGION=us  # or eu, kr, tw
   ```

### 3. Install Dependencies

The virtual environment is already created. Activate it and install dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python run.py
```

The application will be available at http://localhost:5000

### 5. Sync Your Guild

1. Navigate to the "Sync Guild" page
2. Enter your realm slug (e.g., "whitemane", "grobbulus")
3. Enter your guild name slug (e.g., "my-guild-name")
4. Click "Sync Guild"

## API Endpoints

- `GET /api/guild/<guild_id>/analytics` - Get analytics for a guild
- `GET /api/guild/<guild_id>/characters` - Get all characters in a guild

## Project Structure

```
wow-guild-analytics/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # Web routes
│   ├── bnet_api.py          # Battle.net API client
│   ├── services.py          # Business logic
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── sync.html
│       └── guild_detail.html
├── venv/                    # Virtual environment
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (create this)
```

## Notes

- The application uses SQLite by default for simplicity
- Data is cached in the database to reduce API calls
- The Battle.net API has rate limits - be mindful when syncing large guilds
- **Namespace Configuration:**
  - **Classic Anniversary/Era (1.14.x)**: `profile-classic1x-{region}` (default)
  - **Classic (Cataclysm/Wrath)**: `profile-classic-{region}`
  - **Retail WoW**: `profile-{region}`
  - Change the namespace in `bnet_api.py` if needed

## Troubleshooting

### "Failed to get access token"
- Check that your BNET_CLIENT_ID and BNET_CLIENT_SECRET are correct
- Verify the credentials at https://develop.battle.net/access/clients

### "API request failed: 404"
- Verify the realm slug and guild name slug are correct
- Try lowercase with hyphens replacing spaces
- Some special characters may need to be removed

### "Could not fetch details for character"
- Some characters may have privacy settings enabled
- The API may be rate limiting requests
- This is logged as a warning and won't stop the sync
