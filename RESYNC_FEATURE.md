# Guild Re-sync Feature

## Overview
The guild sync functionality has been enhanced to properly handle member changes when re-syncing an existing guild. Members who have left the guild will be automatically removed from the database.

## How It Works

### Initial Sync
When you first sync a guild:
1. Guild record is created in the database
2. All current members are added as Character records
3. Basic profile information is fetched for each member

### Re-sync Process
When you sync a guild that's already tracked:
1. **Fetch Current Roster**: Retrieves the latest member list from Battle.net API
2. **Update Existing Members**: Updates information for members still in the guild
3. **Add New Members**: Creates records for any new members who joined
4. **Remove Departed Members**: Deletes records for members who left the guild

### Member Tracking
The system uses two methods to identify characters:
1. **Battle.net ID** (most reliable): Each character has a unique `bnet_id`
2. **Name + Realm** (fallback): Used if Battle.net ID is not available

### Character Removal Logic
A character is removed if:
- Their `bnet_id` is not in the current roster (if they have a bnet_id), AND
- Their `name + realm` combination is not in the current roster

This ensures accurate tracking even if characters transfer servers or change names.

## Usage

### Via Web Interface
1. Navigate to `/sync`
2. Enter realm slug (e.g., `dreamscythe`)
3. Enter guild name slug (e.g., `hordecore-casuals`)
4. Click "Sync Guild"

### Success Message
After a successful sync, you'll see a message like:
```
Successfully synced 864 members from Hordecore Casuals (3 members removed)
```

The removed count will only appear if members were actually removed.

## Logging

The sync process logs detailed information:

```
INFO - Starting guild sync for 'hordecore-casuals' on 'dreamscythe'
INFO - ✅ Guild info retrieved: Hordecore Casuals - Dreamscythe
INFO - ✅ Roster retrieved: 864 members found
INFO - Processing 864 members...
INFO - Progress: 50/864 members processed...
INFO - Progress: 100/864 members processed...
...
INFO - Checking for members who left the guild...
INFO - Removing 'Oldmember' (no longer in guild)
INFO - Removing 'Inactive' (no longer in guild)
INFO - Removing 'Leftguild' (no longer in guild)
INFO - ✅ Guild sync completed successfully!
INFO -    - Total members: 864
INFO -    - Profiles retrieved: 712
INFO -    - Profiles unavailable: 152
INFO -    - Members removed: 3
```

## Why Members Are Removed

Common reasons for character removal:
- **Left Guild**: Player voluntarily left the guild
- **Kicked**: Character was removed by guild leadership
- **Server Transfer**: Character transferred to a different server (creates new bnet_id)
- **Faction Change**: Character changed faction (Classic Anniversary feature)
- **Account Deletion**: Player deleted their character or account

## Data Integrity

The removal process ensures:
- **No Orphaned Records**: Characters not in the guild are cleaned up
- **Accurate Member Count**: Guild member count always matches current roster
- **Clean Analytics**: Charts and statistics reflect only current members
- **Database Efficiency**: Prevents database bloat from inactive records

## Best Practices

### Regular Re-syncs
Re-sync your guild regularly to keep data current:
- **Daily**: For active guilds with frequent turnover
- **Weekly**: For stable guilds
- **Before Major Events**: Before raid nights or guild events

### After Major Changes
Re-sync after:
- Recruitment drives
- Guild merges
- Mass kicks/cleanups
- Server transfers

### Monitoring
Check the logs after each sync to see:
- How many profiles were successfully fetched
- How many members were removed
- Any errors or warnings

## Technical Details

### Database Operations
The re-sync process uses a single transaction:
1. Fetches current roster from API
2. Updates all character records
3. Deletes removed characters
4. Commits all changes atomically

If any error occurs, all changes are rolled back to maintain data integrity.

### Performance
- Tracks current members using Sets for O(1) lookup
- Batch processes character updates
- Single database query to find existing characters
- Efficient deletion of removed members

### Error Handling
- API failures trigger rollback
- Individual character profile failures don't stop the sync
- Detailed error logging for troubleshooting
- User-friendly error messages

## Example Scenarios

### Scenario 1: New Guild Recruitment
Before sync: 50 members
After sync: 65 members (15 new members joined)
Message: "Successfully synced 65 members from Guild Name"

### Scenario 2: Guild Cleanup
Before sync: 100 members
After sync: 80 members (20 inactive members removed)
Message: "Successfully synced 80 members from Guild Name (20 members removed)"

### Scenario 3: Stable Guild
Before sync: 200 members
After sync: 202 members (5 joined, 3 left)
Message: "Successfully synced 202 members from Guild Name (3 members removed)"

## Future Enhancements

Potential improvements:
- **History Tracking**: Store removed member history
- **Audit Log**: Track when members joined/left
- **Notifications**: Alert on significant membership changes
- **Scheduled Syncs**: Automatic periodic re-syncing
- **Member Activity**: Track last seen dates
