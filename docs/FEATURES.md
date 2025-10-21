# Features Guide

This document describes all major features of the WoW Guild Analytics application.

## Table of Contents
- [Guild Management](#guild-management)
- [Character Tracking](#character-tracking)
- [Analytics & Visualizations](#analytics--visualizations)
- [AI Raid Composer](#ai-raid-composer)
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
- AI Raid Composer

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

## AI Raid Composer

**🤖 Azure OpenAI-Powered Raid Composition Suggestions**

Leverage GPT-4o to generate optimal raid compositions based on your guild's level 60 characters.

### Features

**Intelligent Composition:**
- Analyzes all level 60 characters in the guild
- Considers class, spec, and item level
- Optimizes for raid roles (tanks, healers, DPS)
- Balances buffs, debuffs, and class synergies
- Generates group assignments (8 groups for 40-person raids)

**Supported Raid Types:**
- General Raid
- Molten Core
- Onyxia's Lair
- Blackwing Lair
- Zul'Gurub (20)
- Ruins of Ahn'Qiraj (20)
- Temple of Ahn'Qiraj
- Naxxramas

**Raid Sizes:**
- 20-person raids
- 25-person raids
- 40-person raids

**Detailed Recommendations:**
- Tank assignments with reasoning
- Healer distribution across groups
- DPS composition with class balance
- Group assignments for optimal buffs/debuffs
- Alternative composition suggestions
- Strategic recommendations for specific encounters

### How to Use

1. **Navigate to AI Raid Composer:**
   - Go to a guild detail page
   - Click "AI Raid Composer" button
   - Or navigate to `/guild/<id>/raid-composer`

2. **Configure Raid:**
   - Select raid size (20, 25, or 40)
   - Select raid type (MC, BWL, Naxx, etc.)
   - Click "Generate Raid Composition"

3. **Review Results:**
   - **Composition Summary:** Total count, tanks, healers, DPS by class
   - **Role Assignments:** Detailed list of characters by role
   - **Group Assignments:** 5-person groups with balanced composition
   - **AI Recommendations:** Strategic advice for the composition
   - **Alternative Options:** Backup suggestions if available

### Requirements

**Azure OpenAI Configuration:**
- Azure OpenAI resource with GPT-4o deployment
- Environment variables configured:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_DEPLOYMENT` (default: 'gpt-4o')

**Guild Requirements:**
- Guild must have level 60 characters
- Characters must be synced with details (spec, item level)

**User Access:**
- Must be authenticated (logged in)
- Available to all authenticated users (not admin-only)

### How It Works

1. **Data Collection:** Fetches all level 60 characters with class, spec, and item level
2. **AI Analysis:** Sends character roster to GPT-4o with detailed prompts about WoW Classic raid strategy
3. **Composition Generation:** AI generates optimal composition considering:
   - Tank requirements (warriors with defensive stance, druids)
   - Healer balance (priests, druids, paladins, shamans)
   - DPS mix (melee vs. ranged, physical vs. casters)
   - Class buffs (Paladin blessings, Shaman totems, etc.)
   - Debuff slots (Curse of Elements, Shadow Weaving, etc.)
   - Group synergies (Windfury totems for melee, mana users with Spirit, etc.)
4. **Result Display:** Presents composition with group assignments and strategic recommendations

### Notes

- AI suggestions are recommendations, not requirements
- Actual raid composition may vary based on player skill, gear, and encounter mechanics
- The AI considers WoW Classic mechanics and meta strategies
- Token usage and model information displayed for transparency
- If Azure OpenAI is not configured, a warning message is displayed

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
