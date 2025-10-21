# AI Raid Composer - Quick Reference

Azure OpenAI-powered intelligent raid composition for WoW Classic guilds.

## Overview

The AI Raid Composer uses GPT-4o to analyze your guild's level 60 characters and generate optimal raid compositions based on class, spec, item level, and WoW Classic raid mechanics.

## Quick Start

### 1. Configure Azure OpenAI

Create or edit `.env` file:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### 2. Access the Feature

1. Log in to the application
2. Navigate to a guild detail page
3. Click "AI Raid Composer" button
4. Select raid size (20/25/40) and raid type
5. Click "Generate Raid Composition"

## Supported Raids

- **General Raid** - Balanced composition for any content
- **Molten Core** - Optimized for MC mechanics
- **Onyxia's Lair** - 40-person dragon encounter
- **Blackwing Lair** - BWL-specific considerations
- **Zul'Gurub** - 20-person composition
- **Ruins of Ahn'Qiraj** - 20-person composition
- **Temple of Ahn'Qiraj** - AQ40 mechanics
- **Naxxramas** - Endgame raid optimization

## What the AI Considers

### Role Distribution
- **Tanks**: 2-3 for 40-person raids (Warriors, Druids)
- **Healers**: 8-12 for 40-person raids (Priests, Druids, Paladins, Shamans)
- **DPS**: Remaining slots with balanced melee/ranged split

### Class Balance
- **Buffs**: Paladin blessings, Shaman totems, Druid marks
- **Debuffs**: Curse slots, Shadow Weaving, Sunder Armor
- **Utility**: Combat res, crowd control, dispels

### Group Synergies
- Melee DPS with Windfury Totems (Horde)
- Casters with mana-efficient groups
- Tanks with dedicated healer groups
- Hunter/Warlock pet management

## Output

### Composition Summary
- Total characters selected
- Tank/Healer/DPS breakdown
- Class distribution

### Role Assignments
- Specific characters assigned to tank/heal/DPS
- Reasoning for role assignments

### Group Assignments
- 8 groups of 5 for 40-person raids
- Balanced buffs and utility per group
- Optimized for party-wide abilities

### AI Recommendations
- Strategic advice for the composition
- Alternative suggestions
- Potential improvements
- Encounter-specific tips

## Requirements

### Guild Requirements
- Must have level 60 characters in the guild
- Characters must be synced with spec/item level data
- Minimum characters needed equals raid size

### User Requirements
- Must be logged in (authenticated user)
- No admin privileges required
- Available to all registered users

### Technical Requirements
- Azure OpenAI resource with GPT-4o deployment
- Valid API key and endpoint configured
- Network connectivity to Azure OpenAI service

## Token Usage

The AI Raid Composer displays token usage for transparency:
- **Prompt tokens**: Input (character roster + instructions)
- **Completion tokens**: AI-generated output
- **Total tokens**: Combined usage

Typical usage: 2,000-3,000 tokens per composition request.

## Troubleshooting

### "Azure OpenAI Not Configured"
- Verify environment variables are set in `.env`
- Check that variables are loaded (restart app if needed)
- Confirm Azure OpenAI endpoint is accessible

### "No Level 60 Characters"
- Sync guild roster first
- Run "Sync Character Details" to fetch level data
- Verify characters are actually level 60

### "Client.__init__() got an unexpected keyword argument 'proxies'"
- This is a version compatibility issue between openai and httpx packages
- Solution: Ensure `httpx<0.28.0` is installed
- Run: `pip install 'httpx<0.28.0'`
- This is already specified in requirements.txt
- Restart the application after installing

### "Failed to generate composition"
- Check Azure OpenAI API key is valid
- Verify deployment name matches your Azure configuration
- Check API version compatibility
- Review application logs for detailed error

### "Insufficient characters"
- Guild must have enough level 60s for the raid size
- For 40-person raid, need at least 40 level 60 characters
- Consider using smaller raid size (20 or 25)

## Best Practices

### Data Quality
- Keep guild roster synced regularly
- Ensure character details are up to date
- Verify spec detection is accurate (talent trees)

### Using AI Suggestions
- Treat as recommendations, not requirements
- Consider player skill and experience
- Account for encounter-specific needs
- Adapt based on available players

### Cost Management
- Each composition request uses ~2,500 tokens
- Monitor Azure OpenAI usage in Azure Portal
- Set spending limits if needed
- Cache common compositions

## API Integration

The AI Raid Composer can be accessed programmatically:

### Endpoint
```
POST /api/guild/<guild_id>/suggest-raid-composition
```

### Request Body
```json
{
  "raid_size": 40,
  "raid_type": "Molten Core"
}
```

### Response
```json
{
  "suggestion": {
    "composition_summary": {
      "total_characters": 40,
      "tanks": 3,
      "healers": 10,
      "dps": 27,
      "class_breakdown": { ... }
    },
    "raid_composition": {
      "tanks": ["Warrior1", "Warrior2", "Druid1"],
      "healers": [...],
      "dps": [...]
    },
    "group_assignments": [...],
    "recommendations": [...],
    "alternatives": [...]
  },
  "model_used": "gpt-4o",
  "tokens_used": {
    "prompt": 1500,
    "completion": 1200,
    "total": 2700
  }
}
```

## Security Notes

- **Never commit** Azure OpenAI credentials to git
- Store API keys in `.env` (already in `.gitignore`)
- Use environment variables in production
- Rotate API keys periodically
- Monitor usage for anomalies

See [SECURITY.md](SECURITY.md) for complete security guidelines.

## Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [GPT-4o Model Info](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4o-and-gpt-4-turbo)
- [WoW Classic Raid Composition Guide](https://classic.wowhead.com/guides/classic-raiding)

---

**Note**: This feature is optional. The application works perfectly fine without Azure OpenAI configuration - the AI Raid Composer will simply be disabled.
