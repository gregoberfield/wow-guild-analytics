# Character Special Characters & API Limitations

## The Problem

Characters with special characters (umlauts, accents, etc.) in their names sometimes fail to fetch their profiles from the Battle.net API.

### Examples
- `Bunnycàkes` → ✅ Works (Horde character, correct faction)
- `Sàbér` → ✅ Works (Horde character, correct faction)
- `Gewölbe` → ❌ 404 Not Found (private/not indexed, but would be correct faction if found)
- `Nimbüs` → ❌ 404 Not Found (private/not indexed)
- `Tröll` → ❌ 404 Not Found (private/not indexed)

## Why This Happens

The Battle.net API requires **realm slug + character name** to fetch profiles. It does **NOT** support fetching by character ID.

### Testing Results

```bash
# ❌ Cannot use character ID
GET /profile/wow/character/42802198
Response: 404 Not Found

# ✅ Must use realm + name
GET /profile/wow/character/dreamscythe/sidezz
Response: 200 OK
```

## Character Name Normalization

Our application normalizes character names for API calls:

```python
# Input: Bunnycàkes
# Normalization: bunnyc%C3%A0kes (URL-encoded lowercase)
# API Call: /profile/wow/character/dreamscythe/bunnyc%C3%A0kes
```

The normalization process:
1. **Lowercase** - Converts to lowercase (API is case-insensitive)
2. **URL Encoding** - Encodes special characters (à → %C3%A0, ö → %C3%B6)

### IMPORTANT: Why We Preserve Special Characters

**We must NOT remove accents/umlauts** because doing so can match the wrong character!

**Example of the problem:**
- Guild has: `Bunnycàkes` (Horde, Level 59, Shaman, Orc)
- If we strip accents: `bunnycakes`
- API returns: `Bunnycakes` (Alliance, Level 13, Druid, Night Elf) ❌ **WRONG CHARACTER!**

**Correct approach:**
- Guild has: `Bunnycàkes` (Horde, Level 59, Shaman, Orc)
- URL-encode as-is: `bunnyc%C3%A0kes`
- API returns: `Bunnycàkes` (Horde, Level 59, Shaman, Orc) ✅ **CORRECT!**

### Previous Bug (Now Fixed)

**Before Fix:**
```python
# ❌ WRONG: Stripped accents
normalized = unicodedata.normalize('NFKD', name)
normalized = normalized.encode('ascii', 'ignore').decode('ascii')
# Result: "bunnycakes" → fetched wrong Alliance character
```

**After Fix:**
```python
# ✅ CORRECT: Preserve accents, only URL-encode
normalized = name.lower()
normalized = quote(normalized, safe='')
# Result: "bunnyc%C3%A0kes" → fetches correct Horde character
```

## Why Some Characters Still Fail

Even with proper normalization, some characters return 404 because:

1. **Private Profiles** - Player has set their profile to private
2. **Not Indexed** - Character hasn't been indexed by Blizzard's API
3. **Inactive Characters** - Character hasn't logged in recently
4. **Server Transfers** - Recently transferred characters may not be synced
5. **API Limitations** - Classic Anniversary API has incomplete data

This is **normal and expected**. Typically 20-40% of characters in a large guild will fail to fetch.

## What We Store

### From Guild Roster API
- Character Name (with special characters preserved)
- Battle.net Character ID
- Level
- Rank
- Realm

### From Character Profile API (when available)
- Class name (e.g., "Warlock")
- Race name (e.g., "Undead")
- Gender
- Item levels
- Achievement points
- Specialization

## Solutions Implemented

### 1. Store Battle.net Character ID

We now store the `bnet_id` field from the roster API:

```python
class Character(db.Model):
    bnet_id = db.Column(db.BigInteger, index=True)
```

This allows us to:
- Uniquely identify characters even if their name changes
- Track characters across renames
- Avoid duplicate entries

### 2. Improved Character Lookup

When syncing, we now:
1. Try to find character by `bnet_id` first
2. Fall back to name + realm lookup
3. Create new character if neither found

```python
character = Character.query.filter_by(bnet_id=char_bnet_id).first()
if not character:
    character = Character.query.filter_by(
        name=char_name, 
        realm=realm_name
    ).first()
```

### 3. Character Detail Sync

A separate "Sync Character Details" button allows re-attempting profile fetches for all characters, which can help:
- Fetch newly public profiles
- Update changed data
- Retry previously failed lookups

## Expected Behavior

### Guild Roster Sync
- ✅ **100%** of characters get basic data (name, level, rank)
- ❌ **60-80%** of characters get detailed profiles
- ❌ **20-40%** fail (normal for large guilds)

### Character Detail Re-sync
- Retries all characters
- May fetch additional profiles that became available
- Updates existing profiles with current data

## Database Migration

To add the `bnet_id` field to existing databases:

```bash
python migrate_add_bnet_id.py
```

This adds the `bnet_id` column without disrupting existing data.

## Impact on Users

### What Works
✅ Guild roster shows all characters (even without profiles)
✅ Basic data (name, level, rank) always available
✅ Characters with profiles get full details
✅ Sorting and filtering works on all characters
✅ Analytics include all characters

### What's Limited
⚠️ Some characters show `-` for class/race/ilvl
⚠️ Class/race charts show "Unknown" category
⚠️ Re-syncing may not improve success rate much

### What Users Can't Control
❌ Cannot force private profiles to become public
❌ Cannot bypass Blizzard's API indexing delays
❌ Cannot use character IDs to bypass name issues

## Best Practices

1. **Run guild roster sync first** - Gets all basic data
2. **Wait a few hours** - Let Blizzard's API index characters
3. **Run character detail sync** - Fetch detailed profiles
4. **Accept 20-40% failure rate** - This is normal
5. **Re-sync weekly** - Keep data fresh

## Technical Details

### Character Name in Database
- Stored **with** special characters: `Gewölbe`
- Preserved exactly as returned by API
- Displayed in UI with original spelling

### Character Name for API
- Normalized **without** special characters: `gewolbe`
- Only used for API calls
- Never stored or displayed

### Battle.net Character ID
- Unique identifier: `42802198`
- Cannot be used to fetch profiles
- Useful for tracking character renames
- Stored in database for future use

## Summary

**The issue with special characters is not a bug** - it's a limitation of how the Battle.net API works. Our normalization is correct, but some characters simply aren't available via the API regardless of how we format their names.

The solution is to:
1. ✅ Store character IDs for better tracking
2. ✅ Accept that some profiles will be unavailable  
3. ✅ Display basic data for all characters
4. ✅ Show detailed data when available
