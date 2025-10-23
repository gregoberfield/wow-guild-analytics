# WoW Classic Character Profile API Documentation

**Last Updated:** October 23, 2025  
**API Version:** Classic Era 1.15.7 (Anniversary)  
**Namespace:** `profile-classic1x-us`

This document details all available data fields from the Battle.net API for WoW Classic Era/Anniversary character profiles.

---

## Important: API Indexing Limitations

**Not all guild members are guaranteed to be available via the character profile API.**

The Battle.net API has two separate systems:
- **Guild Roster API**: Returns ALL current guild members (always complete)
- **Character Profile API**: Only returns characters that have been indexed

### Characters That May Return 404

Characters may not be indexed by the profile API if they:
- Haven't logged in recently (exact threshold unknown, appears to be several weeks)
- Are low level and inactive
- Are freshly created or recently transferred
- Haven't been "pinged" by Blizzard's indexing system

**This is expected behavior, not a bug.** When syncing guild members, some characters will naturally return 404 errors and should be skipped gracefully. The roster API will still show them as guild members, but their detailed stats won't be available until they log in and get re-indexed.

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

### 1. **Titles** ❌
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/titles`  
**Purpose:** Character titles earned  
**Status:** Returns 404 - Not available for most characters

### 2. **PvP Summary** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/pvp-summary`  
**Purpose:** Honor kills, PvP rank, honorable kills  
**Status:** Available - Returns honor kills and PvP rank (0-14)

### 3. **Media** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/character-media`  
**Purpose:** Character avatar images  
**Status:** Available - Returns avatar URLs (limited compared to Retail)

### 4. **Specializations** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/specializations`  
**Purpose:** Talent tree distribution (Classic talent points)  
**Status:** Available - Returns talent groups with points distribution across trees

### 5. **Statistics** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/statistics`  
**Purpose:** Detailed combat stats, attributes, resistances, weapon damage  
**Status:** Available - Returns comprehensive character statistics

### 6. **Equipment** ✅
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/equipment`  
**Purpose:** All equipped items with full details  
**Status:** Available

### 7. **Appearance** ❌
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/appearance`  
**Purpose:** Character customization (face, hair, skin color, etc.)  
**Status:** Returns 403 Forbidden - Not accessible

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

## Statistics Endpoint Details

**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/statistics`

Returns detailed character statistics including combat stats, resistances, and derived attributes.

### Structure

```json
{
  "health": 3554,
  "power": 4753,
  "power_type": {
    "key": { "href": "..." },
    "name": "Mana",
    "id": 0
  },
  "strength": {
    "base": 44,
    "effective": 60
  },
  "agility": {
    "base": 48,
    "effective": 64
  },
  "intellect": {
    "base": 108,
    "effective": 244
  },
  "stamina": {
    "base": 66,
    "effective": 232
  },
  "spirit": {
    "base": 120,
    "effective": 189
  },
  "melee_crit": {
    "rating_bonus": 0.0,
    "value": 0.0,
    "rating_normalized": 0
  },
  "attack_power": 50,
  "main_hand_damage_min": 125.64286,
  "main_hand_damage_max": 184.64285,
  "main_hand_speed": 2.7,
  "main_hand_dps": 57.460316,
  "off_hand_damage_min": 4.071429,
  "off_hand_damage_max": 4.071429,
  "off_hand_speed": 2.0,
  "off_hand_dps": 2.0357144,
  "spell_power": 229,
  "spell_penetration": 0,
  "spell_crit": {
    "rating_bonus": 0.0,
    "value": 9.726,
    "rating_normalized": 0
  },
  "mana_regen": 132.0,
  "mana_regen_combat": 132.0,
  "armor": {
    "base": 671,
    "effective": 1625
  },
  "dodge": {
    "rating_bonus": 0.0,
    "value": 5.2000003,
    "rating_normalized": 0
  },
  "parry": {
    "rating_bonus": 0.0,
    "value": 0.0,
    "rating_normalized": 0
  },
  "block": {
    "rating_bonus": 0.0,
    "value": 0.0,
    "rating_normalized": 0
  },
  "ranged_crit": {
    "rating_bonus": 0.0,
    "value": 5.2000003,
    "rating_normalized": 0
  },
  "defense": {
    "base": 300,
    "effective": 300
  },
  "fire_resistance": {
    "base": 0,
    "effective": 52
  },
  "holy_resistance": {
    "base": 0,
    "effective": 0
  },
  "shadow_resistance": {
    "base": 10,
    "effective": 52
  },
  "nature_resistance": {
    "base": 0,
    "effective": 27
  },
  "arcane_resistance": {
    "base": 0,
    "effective": 27
  }
}
```

### Available Statistics

#### Core Stats
- `health` - Total health points
- `power` - Total power (mana/rage/energy)
- `power_type` - Power type (Mana, Rage, Energy, Focus)

#### Primary Attributes
Each has `base` and `effective` values:
- `strength` - Strength (increases melee power)
- `agility` - Agility (increases armor, crit, dodge)
- `intellect` - Intellect (increases spell power, mana)
- `stamina` - Stamina (increases health)
- `spirit` - Spirit (increases health/mana regen)

#### Combat Stats
- `attack_power` - Melee attack power
- `spell_power` - Spell damage/healing power
- `spell_penetration` - Spell penetration (reduces target resistance)

#### Weapon Stats
- `main_hand_damage_min/max` - Main hand weapon damage range
- `main_hand_speed` - Main hand weapon speed
- `main_hand_dps` - Main hand damage per second
- `off_hand_damage_min/max` - Off hand weapon damage range
- `off_hand_speed` - Off hand weapon speed
- `off_hand_dps` - Off hand damage per second

#### Critical Strike
Each has `rating_bonus`, `value`, and `rating_normalized`:
- `melee_crit` - Melee critical strike chance (%)
- `spell_crit` - Spell critical strike chance (%)
- `ranged_crit` - Ranged critical strike chance (%)

#### Defensive Stats
- `armor` - Armor (base and effective)
- `defense` - Defense skill (base and effective)
- `dodge` - Dodge chance (%)
- `parry` - Parry chance (%)
- `block` - Block chance (%)

#### Resistances
Each has `base` and `effective` values:
- `fire_resistance` - Fire resistance
- `holy_resistance` - Holy resistance (Paladins/Priests)
- `shadow_resistance` - Shadow resistance
- `nature_resistance` - Nature resistance
- `arcane_resistance` - Arcane resistance
- `frost_resistance` - Frost resistance (if present)

#### Regeneration
- `mana_regen` - Mana regeneration per 5 seconds (out of combat)
- `mana_regen_combat` - Mana regeneration per 5 seconds (in combat)

**Note:** In Classic WoW, the difference between `base` and `effective` stats represents buffs, gear bonuses, and talents. Rating-based stats (like in Retail) don't exist - Classic uses percentage-based values directly.

---

## PvP Summary Endpoint Details

**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/pvp-summary`

Returns PvP statistics and honor rank information.

### Structure

```json
{
  "honorable_kills": 844,
  "pvp_rank": 9,
  "character": {
    "key": { "href": "..." },
    "name": "Sidezz",
    "id": 42802198,
    "realm": {
      "key": { "href": "..." },
      "name": "Dreamscythe",
      "id": 6103,
      "slug": "dreamscythe"
    }
  }
}
```

### Available Fields

- `honorable_kills` - Total honorable kills (HKs) earned
- `pvp_rank` - Current PvP rank (0-14)

### PvP Ranks (Classic Honor System)

Classic WoW uses a 14-rank honor system:

| Rank | Title (Alliance) | Title (Horde) |
|------|-----------------|---------------|
| 0 | No rank | No rank |
| 1 | Private | Scout |
| 2 | Corporal | Grunt |
| 3 | Sergeant | Sergeant |
| 4 | Master Sergeant | Senior Sergeant |
| 5 | Sergeant Major | First Sergeant |
| 6 | Knight | Stone Guard |
| 7 | Knight-Lieutenant | Blood Guard |
| 8 | Knight-Captain | Legionnaire |
| 9 | Knight-Champion | Centurion |
| 10 | Lieutenant Commander | Champion |
| 11 | Commander | Lieutenant General |
| 12 | Marshal | General |
| 13 | Field Marshal | Warlord |
| 14 | Grand Marshal | High Warlord |

**Note:** Ranks 12-14 grant access to epic PvP gear rewards. The Classic honor system requires weekly participation to maintain/increase rank.

---

## Media Endpoint Details

**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/character-media`

Returns URLs for character avatar and render images.

### Structure

```json
{
  "character": {
    "key": { "href": "..." },
    "name": "Sidezz",
    "id": 42802198,
    "realm": {
      "key": { "href": "..." },
      "name": "Dreamscythe",
      "id": 6103,
      "slug": "dreamscythe"
    }
  },
  "assets": [
    {
      "key": "avatar",
      "value": "https://render.worldofwarcraft.com/classic1x-us/character/dreamscythe/22/42802198-avatar.jpg"
    }
  ]
}
```

### Available Assets

- `avatar` - Small character portrait image (typically 64x64 or similar)

**Note:** Unlike Retail WoW, Classic may have limited render assets. The `avatar` is the primary image type available. Full-body character renders and in-game renders may not be available for all characters.

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

### ❌ Titles
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/titles`  
**Status:** Returns 404 for most characters - Limited/unreliable availability

### ❌ Appearance
**Endpoint:** `/profile/wow/character/{realm-slug}/{character-name}/appearance`  
**Status:** Returns 403 Forbidden - Not accessible

---

## Implementation Notes

### Currently Used in Guild Maestro

Our application currently uses the following endpoints:

1. **Character Profile** - For basic character info (level, class, race, item levels, last login)
2. **Equipment** - For item level calculations
3. **Specializations** - For determining primary talent spec (most points spent)
4. **Guild Roster** - For syncing guild member lists

### Potentially Useful (Not Yet Implemented)

1. **Statistics** - Could display detailed character stats (spell power, resistances, etc.)
2. **PvP Summary** - Could show PvP rank and honorable kills
3. **Media** - Could display character avatars in the roster

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

# Get statistics
stats_endpoint = f"/profile/wow/character/dreamscythe/sidezz/statistics"
stats = api._make_request(stats_endpoint, {'namespace': 'profile-classic1x-us'})
print(f"Health: {stats['health']}")
print(f"Spell Power: {stats['spell_power']}")
print(f"Spell Crit: {stats['spell_crit']['value']:.2f}%")

# Get PvP summary
pvp_endpoint = f"/profile/wow/character/dreamscythe/sidezz/pvp-summary"
pvp = api._make_request(pvp_endpoint, {'namespace': 'profile-classic1x-us'})
print(f"PvP Rank: {pvp['pvp_rank']}")
print(f"Honorable Kills: {pvp['honorable_kills']}")

# Get media
media_endpoint = f"/profile/wow/character/dreamscythe/sidezz/character-media"
media = api._make_request(media_endpoint, {'namespace': 'profile-classic1x-us'})
for asset in media['assets']:
    if asset['key'] == 'avatar':
        print(f"Avatar URL: {asset['value']}")
```

---

## References

- **Battle.net API Documentation:** https://develop.battle.net/documentation/world-of-warcraft-classic
- **OAuth 2.0 Guide:** https://develop.battle.net/documentation/guides/using-oauth
- **API Forum:** https://us.forums.blizzard.com/en/blizzard/c/api-discussion

---

## Changelog

- **2025-10-23:** Initial documentation created from live API responses
- **2025-10-23:** Added detailed Statistics endpoint documentation (combat stats, attributes, resistances)
- **2025-10-23:** Added PvP Summary endpoint documentation (honor kills, PvP ranks)
- **2025-10-23:** Added Media endpoint documentation (avatar URLs)
- **2025-10-23:** Updated endpoint availability status:
  - ✅ Statistics - Available (comprehensive character stats)
  - ✅ PvP Summary - Available (rank and HKs)
  - ✅ Media - Available (avatar images)
  - ❌ Titles - Returns 404 (unreliable/unavailable)
  - ❌ Appearance - Returns 403 Forbidden (not accessible)
  - ❌ Professions - Returns 404 (confirmed not available for Classic)
- Documented all available endpoints for WoW Classic Era/Anniversary
