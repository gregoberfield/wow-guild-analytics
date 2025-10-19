# Specialization Extraction Fix

## The Problem

The `spec_name` field was consistently empty for all characters.

## Root Cause

The code was trying to extract specializations using the **Retail WoW API structure**, but Classic WoW Anniversary uses a completely different system based on **talent trees**.

### Retail WoW (Wrong for Classic)
```json
{
  "active_specialization": {
    "name": "Protection"
  }
}
```

### Classic WoW (Correct Structure)
```json
{
  "specialization_groups": [
    {
      "is_active": true,
      "specializations": [
        {
          "specialization_name": "Affliction",
          "spent_points": 9
        },
        {
          "specialization_name": "Demonology",
          "spent_points": 21
        },
        {
          "specialization_name": "Destruction",
          "spent_points": 21
        }
      ]
    }
  ]
}
```

## Classic WoW Talent System

In Classic WoW:
- Each class has **3 talent trees** (e.g., Warlock has Affliction, Demonology, Destruction)
- Players can distribute 51 points across any combination of trees
- There's no rigid "spec" - it's flexible based on how you allocate points
- **Primary spec** is determined by the tree with the most points

### Example Builds

**Deep Frost Mage:**
- Frost: 31 points ← Primary
- Fire: 0 points
- Arcane: 20 points

**Demo/Destro Warlock (Hybrid):**
- Affliction: 9 points
- Demonology: 21 points ← Tied for primary
- Destruction: 21 points ← Tied for primary
- Primary: Demonology (first one with max points)

## The Solution

Created a new method `get_primary_spec_from_talents()` that:
1. Finds the active specialization group
2. Iterates through all three talent trees
3. Returns the tree name with the most points allocated

### Code Implementation

```python
def get_primary_spec_from_talents(self, spec_data):
    """
    Extract primary specialization from Classic talent tree data.
    In Classic, characters have 3 talent trees and can distribute points.
    Primary spec is determined by the tree with the most points.
    """
    try:
        # Find active specialization group
        for group in spec_data.get('specialization_groups', []):
            if group.get('is_active', False):
                # Find the spec with most points
                max_points = 0
                primary_spec = None
                
                for spec in group.get('specializations', []):
                    points = spec.get('spent_points', 0)
                    spec_name = spec.get('specialization_name', '')
                    
                    if points > max_points:
                        max_points = points
                        primary_spec = spec_name
                
                return primary_spec
        
        return None
    except Exception as e:
        current_app.logger.debug(f"Error parsing spec data: {e}")
        return None
```

## Testing Results

| Character | Class | Primary Spec | Points Distribution |
|-----------|-------|--------------|---------------------|
| Sidezz | Warlock | Demonology | Affliction: 9, Demonology: 21, Destruction: 21 |
| Roby | Mage | Frost | Frost: 31+ (majority) |

## What Changed

### Files Modified

1. **app/bnet_api.py**
   - Added `get_primary_spec_from_talents()` method
   - Extracts primary spec from Classic talent tree structure

2. **app/services.py** (2 locations)
   - Updated guild roster sync to use new method
   - Updated character detail sync to use new method

### Before Fix
```python
# ❌ WRONG: Looking for Retail structure
specs = self.api.get_character_specializations(realm_slug, char_name)
active_spec = specs.get('active_specialization', {})  # Doesn't exist in Classic
character.spec_name = active_spec.get('name', '')  # Always empty
```

### After Fix
```python
# ✅ CORRECT: Parse Classic talent tree structure
specs = self.api.get_character_specializations(realm_slug, char_name)
primary_spec = self.api.get_primary_spec_from_talents(specs)
character.spec_name = primary_spec or ''
```

## Impact

### What Now Works
✅ Spec field populated with primary talent tree name
✅ Spec distribution analytics work correctly
✅ Can sort guild roster by spec
✅ Can filter/analyze by specialization

### Limitations
⚠️ Hybrid specs show only one tree (the one with most points)
⚠️ Doesn't show exact talent point distribution (31/20/0, etc.)
⚠️ Low-level characters (<10) may not have enough points to determine spec
⚠️ Characters with equal points in multiple trees show first tree found

### Possible Enhancements

Could store full talent distribution:
```python
character.spec_name = "Demonology"  # Primary
character.spec_points = "9/21/21"   # Affliction/Demonology/Destruction
character.spec_build = "Demo/Destro Hybrid"  # Human-readable
```

## What You Need to Do

**Re-sync character details** to populate the spec field:

1. Navigate to guild detail page
2. Click "Sync Character Details" button
3. Wait for sync to complete
4. Specs will now show (e.g., "Demonology", "Frost", "Protection")

Alternatively, delete database and re-sync entire guild.

## Summary

**Before:** Spec field always empty (looking for wrong API structure)

**After:** Spec field shows primary talent tree name (parsing Classic talent structure correctly)

This fix makes the spec field functional for Classic WoW Anniversary realms! 🎉
