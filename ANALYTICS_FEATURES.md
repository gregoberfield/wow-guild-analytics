# Enhanced Analytics Features

## New Analytics Added

### 1. **Level Distribution by Class (Stacked Bar Chart)**
A comprehensive stacked column chart showing:
- **X-axis**: Character levels (1-60)
- **Y-axis**: Number of characters at each level
- **Stacks**: Each class shown as a different colored segment
- **Purpose**: Visualize the leveling progression across all classes in your guild

**Features:**
- Color-coded by class (using official WoW class colors)
- Interactive tooltips showing exact counts
- Stacked view to see total characters per level
- Legend to identify each class

### 2. **Level 60 Specialization Breakdown by Class**
A stacked column chart showing spec distribution within each class:
- **X-axis**: Character classes (Druid, Hunter, Mage, etc.)
- **Y-axis**: Number of characters
- **Stacked Columns**: Each spec shown as a different colored segment stacked vertically
- **Purpose**: Visualize how level 60s are distributed across specializations within each class

**Features:**
- Color-coded by specialization (30+ unique spec colors)
- Interactive tooltips showing counts per spec and class totals
- Stacked view to see total level 60s per class at a glance
- Legend to identify each specialization
- **Only includes level 60 characters**

**Example:**
- Warlock column shows: Demonology (bottom, purple) + Destruction (middle, red) + Affliction (top, green)
- Priest column shows: Holy (bottom, yellow) + Shadow (middle, dark purple) + Discipline (top, white)
- Height of each column = total level 60s for that class

### 3. **Level 60 Breakdown by Class**
Two complementary visualizations for max-level characters:

#### A. Horizontal Bar Chart
- Shows total count of level 60s per class
- Sorted by count (most to least)
- Color-coded using class colors
- Tooltips show both count and percentage

#### B. Statistics Table
A detailed table showing:
- Class name
- Total count of level 60 characters
- Percentage of level 60s (%)
- Grand total at the bottom

### 3. **Updated Summary Cards**
The top stat cards now include:
- **Total Members**: All characters in guild
- **Level 60s**: Count and percentage of max level
- **Avg Item Level**: Average across all members
- **Faction**: Horde/Alliance

## Data Structure

### Backend (`app/services.py`)
New analytics data returned:

```python
{
    'level_class_distribution': {
        60: {'Warrior': 45, 'Mage': 38, 'Priest': 22, ...},
        59: {'Warrior': 12, 'Mage': 8, ...},
        ...
    },
    'all_classes': ['Druid', 'Hunter', 'Mage', ...],
    'level_60_count': 612,
    'level_60_by_class': {
        'Warrior': 45,
        'Mage': 38,
        ...
    },
    'level_60_percentages': {
        'Warrior': 7.4,
        'Mage': 6.2,
        ...
    }
}
```

## Visual Design

### Class Colors (Official WoW)
- **Warrior**: #C41F3B (Dark Red)
- **Paladin**: #F58CBA (Pink)
- **Hunter**: #ABD473 (Green)
- **Rogue**: #FFF569 (Yellow)
- **Priest**: #FFFFFF (White)
- **Shaman**: #0070DE (Blue)
- **Mage**: #69CCF0 (Cyan)
- **Warlock**: #9482C9 (Purple)
- **Druid**: #FF7D0A (Orange)

### Chart Configuration
All charts use:
- Responsive design (adapts to screen size)
- Interactive tooltips with detailed information
- Consistent color scheme
- Clear labels and legends
- Professional Chart.js styling

## Page Layout

The guild detail page now has this structure:

```
┌─────────────────────────────────────────────────────┐
│  Summary Cards (4 across)                           │
│  Total | Level 60s | Avg iLvl | Faction            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Level Distribution by Class                        │
│  (Full-width stacked bar chart, levels 1-59)        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Level 60 Specialization Breakdown by Class         │
│  (Full-width stacked column chart, level 60s only)  │
└─────────────────────────────────────────────────────┘

┌──────────────────────────┬──────────────────────────┐
│  Level 60 Breakdown      │  Level 60 Statistics     │
│  (Horizontal Bar Chart)  │  (Data Table)            │
└──────────────────────────┴──────────────────────────┘

┌──────────────────────────┬──────────────────────────┐
│  Class Distribution      │  Race Distribution       │
│  (Doughnut Chart)        │  (Bar Chart)             │
└──────────────────────────┴──────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Guild Roster Table                                 │
│  (Full member list with sortable columns)          │
└─────────────────────────────────────────────────────┘
```

## API Endpoint Updates

The `/api/guild/<guild_id>/analytics` endpoint now returns:

```json
{
    "guild_name": "Hordecore Casuals",
    "total_members": 864,
    "level_60_count": 612,
    "level_60_by_class": {...},
    "level_60_percentages": {...},
    "level_class_distribution": {...},
    "class_distribution": {...},
    "race_distribution": {...},
    "level_distribution": {...},
    "average_item_level": 45.2,
    "spec_distribution": {...}
}
```

## Use Cases

### For Guild Leaders
- **Recruitment**: See which classes need more representation at max level
- **Progression Planning**: Understand how many raiders are available
- **Activity Tracking**: Monitor leveling progression over time

### For Raiders
- **Class Balance**: See how your class compares to others
- **Guild Composition**: Understand the raid team makeup
- **Alt Tracking**: See distribution of alt characters

### For Analysts
- **Trend Analysis**: Export data via API for further analysis
- **Comparisons**: Compare multiple guilds side-by-side
- **Historical Data**: Track changes over time (with repeated syncs)

## Technical Details

### Performance
- All calculations done server-side
- Results cached in database
- Charts render client-side with Chart.js
- Responsive design for mobile/tablet/desktop

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Chart.js 4.4.0 from CDN

## Example Insights

For a guild with 864 members and 612 at level 60:
- **Max Level Rate**: 70.8% of guild is max level
- **Class Balance**: Can see if certain classes are over/under represented
- **Leveling Activity**: Identify levels with most active characters
- **Raid Readiness**: Quick view of potential raid roster size
