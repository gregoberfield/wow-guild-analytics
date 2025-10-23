# WoW Classic Character Profile API Documentation

**Last Updated:** October 23, 2025  
**API Version:** Classic Era 1.15.7 (Anniversary)  
**Namespace:** `profile-classic1x-us`

This document details all available data fields from the Battle.net API for WoW Classic Era/Anniversary character profiles.

---

## Base Character Profile Endpoint

**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}`  
**Namespace:** `profile-classic1x-us`

### Available Root Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | integer | Unique character ID | `42802198` |
| `name` | string | Character name | `"Sidezz"` |
| `level` | integer | Character level (1-60) | `60` |
| `experience` | integer | Current experience points | `0` |
| `average_item_level` | integer | Average equipped item level | `63` |
| `equipped_item_level` | integer | Equipped item level | `60` |
| `last_login_timestamp` | long | Unix timestamp in milliseconds | `1755923237000` |

### Nested Objects

#### Gender
```json
{
  "type": "MALE",
  "name": "Male"
}
```
**Values:** `MALE`, `FEMALE`

#### Faction
```json
{
  "type": "HORDE",
  "name": "Horde"
}
```
**Values:** `HORDE`, `ALLIANCE`

#### Race
```json
{
  "key": {
    "href": "https://us.api.blizzard.com/data/wow/playable-race/5?namespace=static-1.15.7_60013-classic1x-us"
  },
  "name": "Undead",
  "id": 5
}
```

**Common Race IDs:**
- `1` - Human
- `2` - Orc
- `3` - Dwarf
- `4` - Night Elf
- `5` - Undead
- `6` - Tauren
- `7` - Gnome
- `8` - Troll

#### Character Class
```json
{
  "key": {
    "href": "https://us.api.blizzard.com/data/wow/playable-class/9?namespace=static-1.15.7_60013-classic1x-us"
  },
  "name": "Warlock",
  "id": 9
}
```

**Class IDs:**
- `1` - Warrior
- `2` - Paladin
- `3` - Hunter
- `4` - Rogue
- `5` - Priest
- `7` - Shaman
- `8` - Mage
- `9` - Warlock
- `11` - Druid

#### Active Spec
```json
{
  "key": {
    "href": "https://us.api.blizzard.com/data/wow/playable-specialization/0?namespace=static-1.15.7_60013-classic1x-us"
  },
  "id": 0
}
```
**Note:** Classic uses talent trees, not fixed specializations. The `id: 0` indicates no fixed spec.

#### Realm
```json
{
  "key": {
    "href": "https://us.api.blizzard.com/data/wow/realm/6103?namespace=dynamic-classic1x-us"
  },
  "name": "Dreamscythe",
  "id": 6103,
  "slug": "dreamscythe"
}
```

#### Guild
```json
{
  "key": {
    "href": "https://us.api.blizzard.com/data/wow/guild/dreamscythe/hordecore-casuals?namespace=profile-classic1x-us"
  },
  "name": "Hordecore Casuals",
  "id": 1834053,
  "realm": {
    "key": {
      "href": "https://us.api.blizzard.com/data/wow/realm/6103?namespace=dynamic-classic1x-us"
    },
    "name": "Dreamscythe",
    "id": 6103,
    "slug": "dreamscythe"
  },
  "faction": {
    "type": "HORDE",
    "name": "Horde"
  }
}
```

---

## Available Sub-Endpoints

These are linked from the main profile via `href` URLs:

### 1. **Titles** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/titles`  
**Purpose:** Character titles earned  
**Status:** Available

### 2. **PvP Summary** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/pvp-summary`  
**Purpose:** Honor kills, honorable kills, PvP statistics  
**Status:** Available

### 3. **Media** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/character-media`  
**Purpose:** Character avatar, render images  
**Status:** Available

### 4. **Specializations** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/specializations`  
**Purpose:** Talent tree distribution (Classic talent points)  
**Status:** Available - Returns talent groups with points distribution across trees

### 5. **Statistics** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/statistics`  
**Purpose:** Combat stats, character statistics  
**Status:** Available

### 6. **Equipment** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/equipment`  
**Purpose:** All equipped items with full details  
**Status:** Available

### 7. **Appearance** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/appearance`  
**Purpose:** Character customization (face, hair, skin color, etc.)  
**Status:** Available

---

## Equipment Endpoint Details

**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/equipment`

Returns an array of `equipped_items` with detailed information about each piece of gear.

### Equipment Item Structure

Each item in the `equipped_items` array contains:

```json
{
  "item": {
    "key": { "href": "..." },
    "id": 22267
  },
  "slot": {
    "type": "HEAD",
    "name": "Head"
  },
  "quantity": 1,
  "quality": {
    "type": "RARE",
    "name": "Rare"
  },
  "name": "Spellweaver's Turban",
  "media": {
    "key": { "href": "..." },
    "id": 22267
  },
  "item_class": {
    "name": "Armor",
    "id": 4
  },
  "item_subclass": {
    "name": "Cloth",
    "id": 1
  },
  "inventory_type": {
    "type": "HEAD",
    "name": "Head"
  },
  "binding": {
    "type": "ON_ACQUIRE",
    "name": "Binds when picked up"
  },
  "armor": {
    "value": 73,
    "display": {
      "display_string": "73 Armor",
      "color": { "r": 255, "g": 255, "b": 255, "a": 1.0 }
    }
  },
  "stats": [
    {
      "type": { "type": "INTELLECT", "name": "Intellect" },
      "value": 9,
      "display": {
        "display_string": "+9 Intellect",
        "color": { "r": 255, "g": 255, "b": 255, "a": 1.0 }
      }
    }
  ],
  "level": { "value": 60, "display_string": "Requires Level 60" }
}
```

### Equipment Slots

Available slot types:
- `HEAD` - Head
- `NECK` - Neck
- `SHOULDER` - Shoulder
- `BACK` - Back (cloak)
- `CHEST` - Chest
- `SHIRT` - Shirt
- `TABARD` - Tabard
- `WRIST` - Wrist (bracers)
- `HANDS` - Hands (gloves)
- `WAIST` - Waist (belt)
- `LEGS` - Legs
- `FEET` - Feet (boots)
- `FINGER_1` - Ring 1
- `FINGER_2` - Ring 2
- `TRINKET_1` - Trinket 1
- `TRINKET_2` - Trinket 2
- `MAIN_HAND` - Main hand weapon
- `OFF_HAND` - Off hand (weapon/shield)
- `RANGED` - Ranged (wand/gun/bow)

### Item Quality Types

- `POOR` - Poor (gray)
- `COMMON` - Common (white)
- `UNCOMMON` - Uncommon (green)
- `RARE` - Rare (blue)
- `EPIC` - Epic (purple)
- `LEGENDARY` - Legendary (orange)

### Item Stats

Common stat types in `stats` array:
- `INTELLECT` - Intellect
- `STAMINA` - Stamina
- `STRENGTH` - Strength
- `AGILITY` - Agility
- `SPIRIT` - Spirit
- `ARMOR` - Armor value
- `FIRE_RESISTANCE` - Fire resistance
- `NATURE_RESISTANCE` - Nature resistance
- `FROST_RESISTANCE` - Frost resistance
- `SHADOW_RESISTANCE` - Shadow resistance
- `ARCANE_RESISTANCE` - Arcane resistance

---

## Specializations Endpoint Details

**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/specializations`

Returns talent tree information for Classic characters.

### Structure

```json
{
  "specialization_groups": [
    {
      "is_active": true,
      "specializations": [
        {
          "specialization": {
            "key": { "href": "..." },
            "name": "Affliction",
            "id": 302
          },
          "spent_points": 31
        },
        {
          "specialization": {
            "key": { "href": "..." },
            "name": "Demonology",
            "id": 303
          },
          "spent_points": 0
        },
        {
          "specialization": {
            "key": { "href": "..." },
            "name": "Destruction",
            "id": 304
          },
          "spent_points": 20
        }
      ]
    }
  ]
}
```

**Note:** Classic characters have 3 talent trees per class. The tree with the most `spent_points` is typically considered the primary specialization. Characters can distribute 51 total talent points (levels 10-60) across the three trees.

---

## Endpoints NOT Available in Classic

The following endpoints that exist in Retail WoW are **NOT available** for Classic Era/Anniversary:

### ❌ Professions
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/professions`  
**Status:** Returns 404 - Not available in Classic API  
**Note:** Profession data is not exposed via the API for Classic servers

### ❌ Achievements
Individual achievement data is not available (only achievement points in base profile)

### ❌ Mythic Keystone Profile
Not applicable to Classic content

### ❌ Raids
No raid progression tracking endpoint (Classic doesn't have built-in raid tracking)

### ❌ Dungeons
No dungeon completion tracking endpoint

### ❌ Quests
No quest completion tracking endpoint

### ❌ Reputations
No reputation tracking endpoint

### ❌ Mounts/Pets/Toys
Collection data not available

---

## Implementation Notes

### Currently Used in Guild Maestro

Our application currently uses the following endpoints:

1. **Character Profile** - For basic character info (level, class, race, item levels, last login)
2. **Equipment** - For item level calculations
3. **Specializations** - For determining primary talent spec (most points spent)
4. **Guild Roster** - For syncing guild member lists

### Rate Limiting

- Battle.net API uses OAuth 2.0 for authentication
- Rate limits apply per client ID
- Token expires and must be refreshed periodically
- Our implementation includes automatic token refresh

### Data Freshness

- `last_login_timestamp` is in Unix milliseconds
- Character data updates when the character logs in
- Inactive characters may have stale data
- Guild roster updates when members log in

---

## Example Usage

```python
from app.bnet_api import BattleNetAPI

api = BattleNetAPI()

# Get character profile
profile = api.get_character_profile('dreamscythe', 'sidezz')
print(f"{profile['name']} - Level {profile['level']} {profile['character_class']['name']}")
print(f"Item Level: {profile['average_item_level']}")

# Get equipment
equipment = api.get_character_equipment('dreamscythe', 'sidezz')
for item in equipment['equipped_items']:
    print(f"{item['slot']['name']}: {item['name']} ({item['quality']['name']})")

# Get spec
specs = api.get_character_specializations('dreamscythe', 'sidezz')
for group in specs['specialization_groups']:
    if group['is_active']:
        max_points = 0
        primary_spec = None
        for spec in group['specializations']:
            if spec['spent_points'] > max_points:
                max_points = spec['spent_points']
                primary_spec = spec['specialization']['name']
        print(f"Primary Spec: {primary_spec} ({max_points} points)")
```

---

## References

- **Battle.net API Documentation:** https://develop.battle.net/documentation/world-of-warcraft-classic
- **OAuth 2.0 Guide:** https://develop.battle.net/documentation/guides/using-oauth
- **API Forum:** https://us.forums.blizzard.com/en/blizzard/c/api-discussion

---

## Changelog

- **2025-10-23:** Initial documentation created from live API responses
- Documented all available endpoints for WoW Classic Era/Anniversary
- Identified professions endpoint as unavailable (404) for Classic servers
