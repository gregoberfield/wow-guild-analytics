# CRITICAL BUG FIX: Character Name Normalization

## The Bug

**Symptom:** Horde guild was showing Alliance characters

**Root Cause:** Character name normalization was stripping accents, causing the API to return different characters with similar names.

## Example

Guild Roster has: `Bunnycàkes` (Horde, Orc Shaman, Level 59, ID: 44463278)

### What Was Happening (BROKEN)

```python
# Old normalization
name = "Bunnycàkes"
normalized = unicodedata.normalize('NFKD', name)  # Decompose: à → a + `
normalized = normalized.encode('ascii', 'ignore').decode('ascii')  # Strip: à → a
normalized = normalized.lower()  # bunnycakes
normalized = quote(normalized, safe='')  # bunnycakes

# API call
GET /profile/wow/character/dreamscythe/bunnycakes

# API returns
{
  "name": "Bunnycakes",  # ← DIFFERENT CHARACTER!
  "faction": "Alliance",
  "race": "Night Elf",
  "character_class": "Druid",
  "level": 13,
  "guild": null
}
```

**Result:** Stored wrong character data (Alliance instead of Horde) ❌

### What Happens Now (FIXED)

```python
# New normalization
name = "Bunnycàkes"
normalized = name.lower()  # bunnycàkes
normalized = quote(normalized, safe='')  # bunnyc%C3%A0kes (URL-encoded)

# API call
GET /profile/wow/character/dreamscythe/bunnyc%C3%A0kes

# API returns
{
  "id": 44463278,  # ← CORRECT CHARACTER!
  "name": "Bunnycàkes",
  "faction": {"name": "Horde"},
  "race": {"name": "Orc"},
  "character_class": {"name": "Shaman"},
  "level": 59,
  "guild": {"name": "Hordecore Casuals"}
}
```

**Result:** Stores correct character data ✅

## Impact

### Characters Affected

Any character with special characters in their name:
- Characters with accents: `à`, `é`, `è`, `ù`, etc.
- Characters with umlauts: `ä`, `ö`, `ü`, etc.
- Characters with other diacritics

### Data Corruption

Before this fix, the following could happen:
1. ✅ Guild roster sync finds character in guild list
2. ❌ Character profile fetch returns **different character** with similar name
3. ❌ Database stores **wrong faction**, class, race, level, etc.
4. ❌ Analytics show incorrect faction distribution

## The Fix

### Code Change

**File:** `app/bnet_api.py`

**Before:**
```python
def _normalize_character_name(self, name):
    """Normalize character name for API calls."""
    # Remove accents/diacritics (e.g., Gewölbe -> Gewolbe)
    normalized = unicodedata.normalize('NFKD', name)
    normalized = normalized.encode('ascii', 'ignore').decode('ascii')
    normalized = normalized.lower()
    normalized = quote(normalized, safe='')
    return normalized
```

**After:**
```python
def _normalize_character_name(self, name):
    """
    Normalize character name for API calls.
    IMPORTANT: We must preserve special characters (accents, umlauts).
    Removing accents causes wrong character matches.
    """
    normalized = name.lower()
    normalized = quote(normalized, safe='')
    return normalized
```

### Testing Results

| Character | Old Method | New Method | Status |
|-----------|------------|------------|--------|
| `Bunnycàkes` | Alliance L13 Druid ❌ | Horde L59 Shaman ✅ | FIXED |
| `Sàbér` | Alliance L60 Warrior ❌ | Horde L60 Warrior ✅ | FIXED |
| `Gewölbe` | Alliance L? ? ❌ | 404 (correct) ⚠️ | OK |

Note: `Gewölbe` returns 404 for both methods because that character's profile is genuinely unavailable (private/not indexed), but if it were available, the new method would fetch the correct Horde character.

## What You Need to Do

### 1. Re-sync Your Guild

The database currently has incorrect data for characters with special characters. You need to:

```bash
# Option A: Delete the database and start fresh
rm instance/guild_data.db
python run.py
# Then sync guild again

# Option B: Just re-sync (may leave some incorrect data)
# Navigate to your guild detail page
# Click "Sync Character Details" button
```

### 2. Verify Faction

After re-syncing, verify that all characters show the correct faction:

```sql
-- Check for Alliance characters (should be zero in Horde guild)
SELECT COUNT(*) FROM character WHERE faction = 'Alliance';

-- If any found, those characters need re-syncing
```

## Prevention

This bug has been fixed in the codebase. Future syncs will:
1. ✅ Preserve special characters in character names
2. ✅ URL-encode them properly (`à` → `%C3%A0`)
3. ✅ Fetch the correct character from the API
4. ✅ Store accurate faction, race, class data

## Lessons Learned

### What We Learned

1. **Never strip diacritics from identifiers** - They distinguish between different entities
2. **Test with real data** - Edge cases with special characters aren't obvious
3. **Validate faction** - Guild faction should match all member factions
4. **Use character IDs when available** - Would have caught this (ID mismatch)

### Best Practices Going Forward

1. **Preserve original names** - Only URL-encode for transport
2. **Validate returned data** - Check if character ID matches expected
3. **Log mismatches** - Warning if fetched character has different faction
4. **Add assertions** - Horde guild should never have Alliance members

## Summary

**BEFORE:** Stripping accents caused API to return wrong characters → wrong faction data

**AFTER:** Preserving accents (with URL encoding) returns correct characters → correct faction data

**Action Required:** Re-sync your guild to fix corrupted data

This was an excellent catch that prevented ongoing data corruption! 🎉
