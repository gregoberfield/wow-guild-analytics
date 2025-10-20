# Features Guide

This document describes all major features of the WoW Guild Analytics application.

## Table of Contents
- [Guild Management](#guild-management)
- [Character Tracking](#character-tracking)
- [Analytics & Visualizations](#analytics--visualizations)
- [Authentication & Access Control](#authentication--access-control)
- [History & Progression Tracking](#history--progression-tracking)

---

## Guild Management

### Guild Roster Sync

Synchronize guild rosters from the Battle.net API to track members and their information.

**Features:**
- Fetch guild roster from Battle.net API
- Store guild and character information in local database
- Track member count and last update timestamp
- Automatic character removal when members leave

**How to Use:**
1. Navigate to the Sync page
2. Enter realm slug (e.g., `faerlina`)
3. Enter guild name slug (e.g., `my-guild-name`)
4. Click "Sync Guild Roster"

**Requirements:**
- Valid Battle.net API credentials (Client ID and Secret)
- User must be authenticated

### Character Details Sync

Fetch detailed character information including specs, gear, and achievements.

**Features:**
- Detailed character profiles from Battle.net API
- Item level tracking (average and equipped)
- Spec/talent tree extraction for Classic
- Race, class, gender, faction information
- Achievement points tracking

**How to Use:**
1. Navigate to a guild detail page
2. Click "Sync Character Details" button
3. Confirm the operation (may take several minutes)

**Notes:**
- Some characters may have private profiles
- Classic spec detection uses talent tree distribution

---

## Character Tracking

### Character Normalization

Handles special characters in character names correctly for Battle.net API compatibility.

**Supported:**
- Accented characters (é, ñ, ü, etc.)
- Special characters that need URL encoding
- Proper name-to-slug conversion

### Character Progression History

Track individual character development over time with automatic snapshots.

**What's Tracked:**
- Character level changes
- Average item level progression
- Equipped item level progression
- Timestamps for all changes

**Features:**
- Smart tracking (only creates entries when stats change)
- Visual progression charts with dual Y-axes
- Detailed history table with change indicators
- Summary cards showing total gains
- Automatic cleanup when characters leave guild

**How to Access:**
- Click the chart icon (📈) next to any character name in the guild roster

**Data Lifecycle:**
- Created: When character stats change during sync
- Maintained: While character is a guild member
- Deleted: Automatically when character leaves guild

---

## Analytics & Visualizations

### Guild Analytics Dashboard

Comprehensive analytics and visualizations for guild composition and progression.

**Metrics Displayed:**
- Total member count
- Level 60 count and percentage
- Average item level across guild
- Data completeness percentage

**Charts Available:**

#### Class Distribution
- Pie chart showing class breakdown
- Interactive tooltips with counts and percentages

#### Race Distribution
- Pie chart showing race diversity
- Useful for faction balance analysis

#### Level Distribution by Class
- Stacked column chart
- Shows level ranges grouped by class
- Helps identify leveling patterns

#### Level 60 Breakdown by Class
- Bar chart showing max-level characters per class
- Percentage indicators for each class

#### Spec Distribution
- Bar chart of talent specializations
- Only for characters with detected specs
- Classic-specific talent tree analysis

**Customization:**
- Dark theme optimized charts
- Responsive design for all screen sizes
- Interactive tooltips and legends

---

## Authentication & Access Control

### User Authentication

Secure login system using Flask-Login with password hashing.

**Features:**
- Password hashing with Werkzeug
- Session management
- "Remember me" functionality
- Last login tracking

**Default Credentials:**
```
Username: admin
Password: admin123
```
⚠️ **Important:** Change the default password immediately!

### Access Control

Protected routes and administrative functions.

**Public Access:**
- View guild listings
- View guild analytics
- View character progression

**Authenticated Access Required:**
- Sync guild roster
- Sync character details

**Admin Access Required:**
- User management
- Add/edit/delete users
- View admin dashboard

### Admin Panel

Comprehensive user management interface for administrators.

**Features:**
- List all users with status indicators
- Add new users with role assignment
- Edit user details (username, email, password)
- Toggle admin privileges
- Activate/deactivate user accounts
- Self-protection (admins can't remove their own privileges)

**How to Access:**
- Login as admin user
- Navigate to `/admin/`

---

## History & Progression Tracking

### Guild Member History

Track all member additions and removals from guilds over time.

**What's Tracked:**
- Character name
- Character level at time of change
- Character class
- Action type (added/removed)
- Timestamp

**Features:**
- Complete audit trail of membership changes
- Pagination (50 entries per page)
- Filtering by action type (all, added, removed)
- Summary statistics (total added/removed)
- Newest changes displayed first

**How to Access:**
- Click "View History" button on guild detail page
- Navigate to `/guild/<id>/history`

**Use Cases:**
- Turnover analysis
- Recruitment tracking
- Retention monitoring
- Audit trails
- Seasonal pattern identification

### Character Progression Tracking

Detailed progression history for individual characters.

**Smart Tracking:**
- Only records when level or item level changes
- Prevents duplicate entries
- Maintains efficient database

**Visualization:**
- Interactive line chart with dual Y-axes
- Three data series: Level, Avg iLvl, Equipped iLvl
- Time-series from oldest to newest
- Tooltips showing exact values

**History Table:**
- All progression snapshots
- Change indicators (green for increases, red for decreases)
- Pagination for large histories
- Comparison between consecutive entries

**Statistics:**
- Total progression snapshots
- Level gain since tracking began
- Item level gain since tracking began
- Current vs initial comparison

---

## Dark Theme

The application uses a custom dark theme optimized for readability.

**Color Scheme:**
- Background: Black (#000000, #1a1a1a)
- Navbar: Blue (#0d6efd)
- Text: Light gray (#e0e0e0, #ffffff)
- Cards: Dark gray (#1a1a1a)
- Tables: Dark with hover effects

**Chart Styling:**
- Dark backgrounds for all charts
- Light text and labels
- Blue-themed tooltips
- High contrast for accessibility

---

## Data Synchronization

### Sync Workflow

1. **Initial Roster Sync**
   - Fetches guild information
   - Creates/updates guild record
   - Fetches roster member list
   - Creates basic character records
   - Tracks new member additions

2. **Character Details Sync**
   - Iterates through all characters
   - Fetches detailed profiles
   - Updates item levels, specs, achievements
   - Tracks progression changes (if stats changed)

3. **Subsequent Syncs**
   - Compares roster with database
   - Adds new members (logs to history)
   - Removes departed members (logs to history, deletes progression)
   - Updates existing character data
   - Creates progression entries only if stats changed

### Error Handling

- Graceful handling of private/missing profiles
- Detailed logging of all operations
- User-friendly error messages
- Partial success tracking (successful/failed profiles)

---

## Tips & Best Practices

### Regular Syncing
- Sync rosters regularly to capture member changes
- Run character details sync after roster sync for complete data
- More frequent syncs = more accurate progression tracking

### Performance
- Character details sync can take several minutes for large guilds
- Consider syncing during off-peak hours
- Database automatically handles cleanup

### Data Privacy
- Progression history deleted when members leave
- Only publicly available Battle.net data is stored
- No sensitive player information collected

### Database Maintenance
- Automatic cleanup on member removal
- Cascade deletes maintain referential integrity
- Regular syncs keep data fresh
