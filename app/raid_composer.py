"""
Azure OpenAI service for raid composition suggestions.
Uses GPT-4o to analyze guild rosters and suggest optimal raid groups.
"""

from openai import AzureOpenAI
from flask import current_app
from app.models import Character
import json


class RaidComposerService:
    """Service for AI-powered raid composition suggestions"""
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Initialize Azure OpenAI client lazily"""
        if self.client is None:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=current_app.config['AZURE_OPENAI_ENDPOINT'],
                    api_key=current_app.config['AZURE_OPENAI_API_KEY'],
                    api_version=current_app.config['AZURE_OPENAI_API_VERSION'],
                    timeout=60.0,
                    max_retries=2
                )
            except Exception as e:
                current_app.logger.error(f"Failed to initialize Azure OpenAI client: {e}")
                raise
        return self.client
    
    def get_level_60_characters(self, guild_id):
        """Get all level 60 characters for a guild"""
        characters = Character.query.filter_by(
            guild_id=guild_id,
            level=60
        ).all()
        
        return [{
            'name': char.name,
            'class': char.character_class,
            'spec': char.spec_name,
            'item_level': char.average_item_level or 0,
            'equipped_ilvl': char.equipped_item_level or 0
        } for char in characters]
    
    def suggest_raid_composition(self, guild_id, raid_size=40, raid_type='General'):
        """
        Use Azure OpenAI to suggest optimal raid composition.
        
        Args:
            guild_id: The guild ID to analyze
            raid_size: Target raid size (20, 25, or 40)
            raid_type: Type of raid (e.g., 'Molten Core', 'BWL', 'Naxxramas', 'General')
        
        Returns:
            dict: AI-generated raid composition suggestions
        """
        try:
            # Get available level 60 characters
            characters = self.get_level_60_characters(guild_id)
            
            if not characters:
                return {
                    'error': 'No level 60 characters found in this guild.',
                    'suggestion': None
                }
            
            # Prepare the prompt for GPT-4o
            system_prompt = """You are an expert World of Warcraft Classic Anniversary Edition raid leader and strategist. 
Your role is to analyze guild rosters and suggest optimal raid compositions based on class balance, 
role distribution, and encounter requirements.

For World of Warcraft Classic raids, consider:
- Optimal class balance and raid composition for the specific encounter
- Buff coverage (Battle Shout, Mark of the Wild, etc.)
- Debuff slots and priorities (Warlocks, Shadow Priests, etc.)
- Tank requirements (Warriors, Druids)
- Healer requirements (Priests, Druids, Paladins, Shamans)
- DPS distribution (melee vs ranged balance)
- Item level as a tiebreaker when choosing between similar classes/specs
- Class synergies and group compositions
- Specific raid encounter mechanics and requirements

CRITICAL REQUIREMENTS:
1. NEVER select the same character twice - each character can only appear ONCE in the entire composition
2. Balance class composition first, then use item level to choose between characters of the same class/spec
3. For group_assignments: Create EXACTLY raid_size/5 groups (e.g., 40-person raid = 8 groups, 20-person = 4 groups)
4. Each group MUST have EXACTLY 5 members
5. Every character in raid_composition must appear in exactly one group
6. CRITICAL: List ALL selected characters in raid_composition arrays - tanks array must have ALL tanks, healers array must have ALL healers, dps array must have ALL DPS (verify counts match composition_summary)
7. Include raid-specific advice in recommendations (mention the raid type explicitly)
8. In character "reason" fields, mention raid-specific benefits when relevant
9. CRITICAL: You MUST respond with VALID JSON only. Ensure all strings are properly quoted and escaped.

Provide your response in VALID JSON format with the following structure:
{
    "raid_composition": {
        "tanks": [{"name": "CharName", "class": "Warrior", "reason": "Brief reason including raid-specific benefits"}],
        "healers": [{"name": "CharName", "class": "Priest", "reason": "Brief reason including raid-specific benefits"}],
        "dps": [{"name": "CharName", "class": "Rogue", "reason": "Brief reason including raid-specific benefits"}]
    },
    "group_assignments": [
        {
            "group_number": 1,
            "members": [
                {"name": "CharName", "class": "Warrior", "role": "Tank", "reason": "Brief reason"},
                {"name": "CharName2", "class": "Priest", "role": "Healer", "reason": "Brief reason"},
                {"name": "CharName3", "class": "Rogue", "role": "DPS", "reason": "Brief reason"},
                {"name": "CharName4", "class": "Mage", "role": "DPS", "reason": "Brief reason"},
                {"name": "CharName5", "class": "Warlock", "role": "DPS", "reason": "Brief reason"}
            ]
        }
    ],
    "composition_summary": {
        "total_characters": number,
        "tanks": number,
        "healers": number,
        "dps": number,
        "class_breakdown": {class_name: count}
    },
    "recommendations": [list of strategic recommendations specific to the raid type],
    "alternatives": [{"name": "CharName", "class": "Mage", "reason": "Why they could substitute for specific raid"}]
}

IMPORTANT: The raid_composition arrays (tanks, healers, dps) MUST contain ALL characters selected for the raid.
For example, if composition_summary shows 29 DPS, then the dps array must have exactly 29 character objects.

For the "reason" field in each character selection, provide a 1-2 sentence explanation that includes:
- Why this character was chosen (class/spec fit, role, and item level)
- If relevant to the specific raid type, mention encounter-specific benefits
Examples:
- "Protection Warrior with strong gear (475 ilvl), essential for tanking Ragnaros in Molten Core"
- "Holy Priest (468 ilvl) with excellent raid healing output, crucial for dispelling curses in Molten Core"
- "Fire Mage (472 ilvl) optimal for Molten Core's low fire resistance encounters"
- "Well-geared Combat Rogue (465 ilvl) for consistent melee DPS"

IMPORTANT: When writing "reason" text:
- Use double quotes for all JSON strings (not single quotes)
- Escape any double quotes within text with backslash (\")
- Keep reasons concise (1-2 sentences maximum)
- This ensures valid JSON formatting
"""
            
            user_prompt = f"""Analyze this guild's level 60 roster and suggest an optimal {raid_size}-person raid composition for {raid_type}.

Available Characters ({len(characters)} total):
{json.dumps(characters, indent=2)}

Raid Size: {raid_size}
Raid Type: {raid_type}

CRITICAL INSTRUCTIONS:
1. Select EXACTLY {raid_size} unique characters (no duplicates!)
2. Prioritize optimal class balance for {raid_type}, using item level as a tiebreaker when choosing between characters of the same class
3. Create EXACTLY {raid_size // 5} groups of EXACTLY 5 members each
4. Ensure all {raid_size} selected characters appear in the group assignments
5. CRITICAL: Include ALL selected characters in the raid_composition arrays:
   - If you select 3 tanks, the "tanks" array must have 3 entries
   - If you select 8 healers, the "healers" array must have 8 entries  
   - If you select 29 DPS, the "dps" array must have 29 entries
   - Verify array lengths match the numbers in composition_summary
6. Include {raid_type}-specific advice in your recommendations
7. Mention {raid_type}-specific benefits in character selection reasons when applicable

For {raid_type} specifically, consider:
- Optimal class composition for the encounters (Warlocks for debuffs, Mages for DPS, etc.)
- Raid-specific resist requirements (e.g., fire resist for Molten Core)
- Key encounter mechanics
- Proper buff and debuff coverage
- Balance between melee and ranged DPS
- Item level to differentiate between similar options

Provide a balanced raid composition with proper tank, healer, and DPS distribution optimized for {raid_type}.
Ensure class balance is appropriate, using gear quality to select the best character within each class."""
            
            # Call Azure OpenAI
            client = self._get_client()
            response = client.chat.completions.create(
                model=current_app.config['AZURE_OPENAI_DEPLOYMENT'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=6000,  # Increased to accommodate large rosters and not_selected list
                response_format={"type": "json_object"}
            )
            
            # Get the raw response content
            raw_content = response.choices[0].message.content
            current_app.logger.info(f"Raw AI response length: {len(raw_content)} characters")
            
            # Check if response was truncated
            finish_reason = response.choices[0].finish_reason
            if finish_reason == 'length':
                current_app.logger.warning("AI response was truncated due to token limit!")
                # We'll still try to parse it, as it might be recoverable
            
            # Parse the response with better error handling
            try:
                suggestion = json.loads(raw_content)
            except json.JSONDecodeError as json_err:
                current_app.logger.error(f"JSON parsing error: {json_err}")
                current_app.logger.error(f"Raw response excerpt: {raw_content[:500]}...")
                current_app.logger.error(f"Error at position {json_err.pos}: {raw_content[max(0, json_err.pos-50):json_err.pos+50]}")
                
                # Try to salvage the response by fixing common JSON issues
                try:
                    # Remove any trailing commas before closing braces/brackets
                    import re
                    cleaned_content = re.sub(r',\s*}', '}', raw_content)
                    cleaned_content = re.sub(r',\s*]', ']', cleaned_content)
                    suggestion = json.loads(cleaned_content)
                    current_app.logger.info("Successfully recovered from JSON error by cleaning response")
                except Exception as recovery_err:
                    current_app.logger.error(f"Failed to recover from JSON error: {recovery_err}")
                    raise json_err
            
            return {
                'error': None,
                'suggestion': suggestion,
                'available_characters': len(characters),
                'model_used': current_app.config['AZURE_OPENAI_DEPLOYMENT'],
                'tokens_used': {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                }
            }
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON decode error in raid composition: {str(e)}")
            return {
                'error': f'AI response was not valid JSON. Please try again. Error: {str(e)}',
                'suggestion': None
            }
        except Exception as e:
            current_app.logger.error(f"Error generating raid composition: {str(e)}")
            return {
                'error': str(e),
                'suggestion': None
            }
    
    def is_configured(self):
        """Check if Azure OpenAI is properly configured"""
        return (
            current_app.config.get('AZURE_OPENAI_ENDPOINT') and
            current_app.config.get('AZURE_OPENAI_API_KEY') and
            current_app.config.get('AZURE_OPENAI_DEPLOYMENT')
        )
