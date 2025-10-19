# Character Detail Sync Feature

## Overview

The Character Detail Sync feature allows you to fetch detailed profile information for all characters in a guild. This is a separate operation from the initial guild roster sync.

## Why Two Sync Operations?

### Guild Roster Sync
- **What it does**: Fetches the list of all guild members
- **Data obtained**: Character name, level, class, race, rank
- **Source**: Guild roster endpoint (single API call)
- **Speed**: Fast (~1-2 seconds)
- **Reliability**: 100% success rate

### Character Detail Sync  
- **What it does**: Fetches detailed profile for each individual character
- **Data obtained**: Item levels, gender, specialization, achievement points
- **Source**: Individual character profile endpoints (one call per character)
- **Speed**: Slower (864 characters = ~10-20 minutes with rate limiting)
- **Reliability**: 60-80% success rate (many profiles are private/not indexed)

## How to Use

### 1. Initial Guild Sync
First, sync the guild roster:
1. Go to "Sync Guild" in the navigation
2. Enter realm slug: `dreamscythe`
3. Enter guild slug: `hordecore-casuals`
4. Click "Sync Guild"

This creates all character records with basic data.

### 2. Character Detail Sync
Then, fetch detailed character information:
1. Navigate to the guild detail page
2. Click "Sync Character Details" button (top right)
3. Confirm the sync operation
4. Wait for completion (shows progress in logs)

## Data Completeness Indicator

The guild detail page shows:
- **Alert Banner**: Displays if less than 100% of characters have detailed data
- **Percentage**: Shows how many characters have profiles
- **Recommendation**: Suggests syncing if completeness is low

Example:
```
ℹ️ Character Data Status: 612 of 864 characters (70.8%) have detailed profile information.
   Click "Sync Character Details" above to fetch missing data like item levels, gender, and specializations.
```

## What Gets Updated

When you sync character details, the following fields are updated:

### From Character Profile API:
- `achievement_points` - Total achievement points
- `average_item_level` - Average equipped item level
- `equipped_item_level` - Currently equipped item level
- `gender` - Male/Female
- `faction` - Horde/Alliance
- `character_class` - Class (if missing from roster)
- `race` - Race (if missing from roster)

### From Specialization API:
- `spec_name` - Active specialization (e.g., "Protection", "Arms", "Fury")

## Expected Results

For a large guild (864 members):

| Metric | Typical Value |
|--------|---------------|
| Total Characters | 864 |
| Successful Syncs | 500-700 (60-80%) |
| Failed (404) | 150-350 (20-40%) |
| Sync Duration | 10-20 minutes |
| API Calls | ~1,700 (profile + spec per character) |

## Why Some Characters Fail

Characters may not have detailed profiles for several reasons:

1. **Privacy Settings**: Player has profile set to private
2. **Not Indexed**: Character hasn't logged in recently enough
3. **New Characters**: Recently created (< 24 hours old)
4. **Realm Transfers**: Just transferred and data not synced
5. **API Limitations**: Classic Anniversary API has limited data

**This is normal and expected!** The basic roster data is still stored.

## Progress Tracking

The sync operation logs progress every 25 characters:

```
Starting character detail sync for Hordecore Casuals
Total characters to sync: 864
Progress: 25/864 characters processed...
Progress: 50/864 characters processed...
Progress: 75/864 characters processed...
...
✅ Character detail sync completed!
   - Total characters: 864
   - Successfully synced: 612
   - Failed: 252
   - Skipped: 0
```

## Performance Optimizations

The sync includes several optimizations:

1. **Batch Commits**: Commits every 25 characters to prevent data loss
2. **Progress Logging**: Updates every 25 characters for visibility
3. **Error Handling**: Continues on failures, doesn't abort entire sync
4. **Rate Limiting**: Respects Battle.net API rate limits
5. **Smart Updates**: Can optionally skip characters that already have data

## Re-syncing

You can re-run the character detail sync anytime to:
- Update stale data (item levels change)
- Retry failed characters
- Fetch data for newly public profiles
- Update specializations (players change specs)

Each sync updates the `last_updated` timestamp for successfully synced characters.

## API Endpoint

You can also trigger character sync programmatically:

```bash
POST /guild/<guild_id>/sync-characters
```

This returns a redirect to the guild detail page with a flash message showing results.

## Best Practices

1. **Sync roster first**: Always run guild roster sync before character detail sync
2. **Be patient**: Large guilds take time - the sync will complete
3. **Check logs**: Monitor the terminal/logs for progress and errors
4. **Re-sync periodically**: Item levels and specs change, re-sync weekly
5. **Don't worry about failures**: 60-80% success is excellent for Classic

## Troubleshooting

### Sync Takes Too Long
- **Normal**: 864 characters = ~10-20 minutes
- **Solution**: Be patient, it's working!

### Low Success Rate (<50%)
- **Cause**: Many private profiles in your guild
- **Solution**: Nothing you can do, this is normal

### Sync Fails Completely
- **Check**: API credentials in `.env`
- **Check**: Internet connection
- **Check**: Battle.net API status
- **Solution**: Review error logs for specific issues

### No Data Updated
- **Cause**: Characters already have detailed data
- **Solution**: Working as intended, no updates needed

## UI Features

### Sync Button
- **Location**: Top right of guild detail page
- **Icon**: Rotating arrows (⟳)
- **Confirmation**: Asks before starting (can't be cancelled)
- **Feedback**: Shows flash message with results

### Data Status Alert
- **Shows when**: Less than 100% completeness
- **Color**: Blue info alert
- **Dismissible**: Can be closed
- **Action**: Suggests syncing if needed

## Database Impact

Each successful character sync updates:
- Character record (in-place update)
- `last_updated` timestamp
- Commits every 25 characters (prevents data loss)

No new records are created - only existing character records are updated.
