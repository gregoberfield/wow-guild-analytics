# Guild Sync Quick Reference

## Your Guild Information

**Guild Name:** Hordecore Casuals  
**Server:** Dreamscythe (Classic Anniversary)  
**Realm Slug:** `dreamscythe`  
**Guild Slug:** `hordecore-casuals`

## How to Sync Your Guild

1. Go to the "Sync Guild" page in the web interface
2. Enter:
   - **Realm Slug:** `dreamscythe`
   - **Guild Name Slug:** `hordecore-casuals`
3. Click "Sync Guild"

## Creating Slugs

Guild and realm names must be converted to "slugs" (lowercase with hyphens):

### Examples:
- "Hordecore Casuals" → `hordecore-casuals`
- "Knights of Azeroth" → `knights-of-azeroth`
- "Old Blanchy" → `old-blanchy`
- "Whitemane" → `whitemane`
- "Grobbulus" → `grobbulus`

### Rules:
1. Convert to lowercase
2. Replace spaces with hyphens (-)
3. Remove apostrophes and special characters
4. For accented characters, use the non-accented version

## WoW Classic Versions

This application is configured for **Classic Anniversary/Era servers** (1.14.x) which use the `profile-classic1x-us` namespace.

If you need to switch to other WoW versions:

### Classic Era/Anniversary (Current - Default)
- **Namespace:** `profile-classic1x-{region}`
- **Servers:** Dreamscythe, Nightslayer, Wild Growth, etc.
- **Version:** 1.14.x

### Classic (Cataclysm/Wrath)
- **Namespace:** `profile-classic-{region}`
- **Servers:** Servers running Cataclysm Classic
- Change in `app/bnet_api.py` line 18-19

### Retail WoW
- **Namespace:** `profile-{region}`
- **Servers:** Current expansion retail servers
- Change in `app/bnet_api.py` line 18-19
