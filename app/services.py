from app.models import Guild, Character
from app.bnet_api import BattleNetAPI
from app import db
from datetime import datetime
from flask import current_app

class GuildService:
    def __init__(self):
        self.api = BattleNetAPI()
    
    def sync_guild_roster(self, realm_slug, guild_name_slug):
        """Fetch and store guild roster from Battle.net API"""
        try:
            current_app.logger.info(f"Starting guild sync for '{guild_name_slug}' on '{realm_slug}'")
            
            # Get guild info
            current_app.logger.info("Fetching guild information...")
            guild_data = self.api.get_guild_info(realm_slug, guild_name_slug)
            current_app.logger.info(f"✅ Guild info retrieved: {guild_data.get('name')} - {guild_data.get('realm', {}).get('name')}")
            
            # Get or create guild
            guild = Guild.query.filter_by(
                name=guild_data.get('name'),
                realm=guild_data.get('realm', {}).get('name')
            ).first()
            
            if not guild:
                current_app.logger.info("Creating new guild record in database")
                guild = Guild(
                    name=guild_data.get('name'),
                    realm=guild_data.get('realm', {}).get('name'),
                    faction=guild_data.get('faction', {}).get('name')
                )
                db.session.add(guild)
            else:
                current_app.logger.info("Updating existing guild record")
            
            # Get roster
            current_app.logger.info("Fetching guild roster...")
            roster_data = self.api.get_guild_roster(realm_slug, guild_name_slug)
            members = roster_data.get('members', [])
            
            guild.member_count = len(members)
            guild.last_updated = datetime.utcnow()
            current_app.logger.info(f"✅ Roster retrieved: {len(members)} members found")
            
            # Track statistics
            successful_profiles = 0
            failed_profiles = 0
            
            # Process each member
            current_app.logger.info(f"Processing {len(members)} members...")
            for idx, member in enumerate(members, 1):
                character_data = member.get('character', {})
                char_name = character_data.get('name')
                char_bnet_id = character_data.get('id')  # Battle.net character ID
                char_realm = character_data.get('realm', {}).get('slug', realm_slug)
                
                if idx % 50 == 0:
                    current_app.logger.info(f"Progress: {idx}/{len(members)} members processed...")
                
                # Get or create character (try by bnet_id first, then by name)
                character = None
                if char_bnet_id:
                    character = Character.query.filter_by(bnet_id=char_bnet_id).first()
                
                if not character:
                    character = Character.query.filter_by(
                        name=char_name,
                        realm=character_data.get('realm', {}).get('name', '')
                    ).first()
                
                if not character:
                    character = Character(name=char_name)
                
                # Update character data from roster
                character.bnet_id = char_bnet_id
                character.realm = character_data.get('realm', {}).get('name', '')
                character.level = character_data.get('level', 0)
                # Note: roster API doesn't include class/race names, only IDs
                # These will be populated when we fetch the full character profile
                character.rank = member.get('rank', 0)
                character.guild_id = guild.id
                character.last_updated = datetime.utcnow()
                
                # Try to get additional character details (this may fail for some characters)
                try:
                    profile = self.api.get_character_profile(char_realm, char_name)
                    character.achievement_points = profile.get('achievement_points', 0)
                    character.average_item_level = profile.get('average_item_level', 0)
                    character.equipped_item_level = profile.get('equipped_item_level', 0)
                    character.gender = profile.get('gender', {}).get('name', '')
                    character.faction = profile.get('faction', {}).get('name', '')
                    character.character_class = profile.get('character_class', {}).get('name', '')
                    character.race = profile.get('race', {}).get('name', '')
                    successful_profiles += 1
                    
                    # Get active spec (Classic uses talent trees, not rigid specs)
                    try:
                        specs = self.api.get_character_specializations(char_realm, char_name)
                        # Extract primary spec from talent tree distribution
                        primary_spec = self.api.get_primary_spec_from_talents(specs)
                        if primary_spec:
                            character.spec_name = primary_spec
                        else:
                            character.spec_name = ''
                    except Exception as spec_error:
                        character.spec_name = ''
                        current_app.logger.warning(f"Could not fetch specialization for {char_name}: {str(spec_error)}")
                        
                except Exception as e:
                    failed_profiles += 1
                    error_msg = str(e)
                    if "404" in error_msg:
                        current_app.logger.debug(f"Character profile not found for '{char_name}' (may be private or not indexed)")
                    else:
                        current_app.logger.warning(f"Could not fetch details for '{char_name}': {error_msg}")
                
                db.session.add(character)
            
            db.session.commit()
            
            current_app.logger.info(f"✅ Guild sync completed successfully!")
            current_app.logger.info(f"   - Total members: {len(members)}")
            current_app.logger.info(f"   - Profiles retrieved: {successful_profiles}")
            current_app.logger.info(f"   - Profiles unavailable: {failed_profiles}")
            
            return guild, len(members)
            
        except Exception as e:
            current_app.logger.error(f"❌ Guild sync failed: {str(e)}")
            db.session.rollback()
            raise e
    
    def get_guild_analytics(self, guild_id):
        """Generate analytics for a guild"""
        guild = Guild.query.get(guild_id)
        if not guild:
            return None
        
        characters = Character.query.filter_by(guild_id=guild_id).all()
        
        # Class distribution
        class_distribution = {}
        for char in characters:
            class_name = char.character_class or 'Unknown'
            class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
        
        # Race distribution
        race_distribution = {}
        for char in characters:
            race_name = char.race or 'Unknown'
            race_distribution[race_name] = race_distribution.get(race_name, 0) + 1
        
        # Level distribution
        level_distribution = {}
        for char in characters:
            level = char.level or 0
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # Level by class distribution (for stacked chart) - exclude level 60
        level_class_distribution = {}
        all_classes = set()
        for char in characters:
            level = char.level or 0
            # Skip level 60 for this chart
            if level == 60:
                continue
            char_class = char.character_class or 'Unknown'
            all_classes.add(char_class)
            
            if level not in level_class_distribution:
                level_class_distribution[level] = {}
            
            level_class_distribution[level][char_class] = level_class_distribution[level].get(char_class, 0) + 1
        
        # Level 60 breakdown by class
        level_60_chars = [char for char in characters if char.level == 60]
        level_60_by_class = {}
        for char in level_60_chars:
            char_class = char.character_class or 'Unknown'
            level_60_by_class[char_class] = level_60_by_class.get(char_class, 0) + 1
        
        # Calculate percentages for level 60s
        total_60s = len(level_60_chars)
        level_60_percentages = {}
        if total_60s > 0:
            for char_class, count in level_60_by_class.items():
                level_60_percentages[char_class] = round((count / total_60s) * 100, 1)
        
        # Average item level
        item_levels = [char.average_item_level for char in characters if char.average_item_level]
        avg_ilvl = sum(item_levels) / len(item_levels) if item_levels else 0
        
        # Spec distribution (all characters)
        spec_distribution = {}
        for char in characters:
            if char.spec_name:
                spec_distribution[char.spec_name] = spec_distribution.get(char.spec_name, 0) + 1
        
        # Level 60 breakdown by class and spec
        level_60_class_spec = {}
        for char in level_60_chars:
            char_class = char.character_class or 'Unknown'
            char_spec = char.spec_name or 'Unknown'
            
            if char_class not in level_60_class_spec:
                level_60_class_spec[char_class] = {}
            
            level_60_class_spec[char_class][char_spec] = level_60_class_spec[char_class].get(char_spec, 0) + 1
        
        # Calculate data completeness
        chars_with_profiles = sum(1 for char in characters if char.average_item_level or char.gender)
        data_completeness = round((chars_with_profiles / len(characters) * 100), 1) if characters else 0
        
        return {
            'guild': guild,
            'total_members': len(characters),
            'class_distribution': class_distribution,
            'race_distribution': race_distribution,
            'level_distribution': level_distribution,
            'level_class_distribution': level_class_distribution,
            'all_classes': sorted(list(all_classes)),
            'level_60_count': total_60s,
            'level_60_by_class': level_60_by_class,
            'level_60_percentages': level_60_percentages,
            'level_60_class_spec': level_60_class_spec,
            'average_item_level': round(avg_ilvl, 2),
            'spec_distribution': spec_distribution,
            'characters': characters,
            'data_completeness': data_completeness,
            'chars_with_profiles': chars_with_profiles
        }
    
    def sync_character_details(self, guild_id):
        """
        Sync detailed information for all characters in a guild.
        This fetches individual character profiles from the API.
        """
        try:
            guild = Guild.query.get(guild_id)
            if not guild:
                raise Exception(f"Guild with ID {guild_id} not found")
            
            characters = Character.query.filter_by(guild_id=guild_id).all()
            total_chars = len(characters)
            
            current_app.logger.info(f"Starting character detail sync for {guild.name}")
            current_app.logger.info(f"Total characters to sync: {total_chars}")
            
            successful = 0
            failed = 0
            skipped = 0
            
            for idx, character in enumerate(characters, 1):
                # Get realm slug from character
                realm_slug = character.realm.lower().replace(' ', '-').replace("'", '')
                
                if idx % 25 == 0:
                    current_app.logger.info(f"Progress: {idx}/{total_chars} characters processed...")
                
                # Skip if character already has detailed data (optional optimization)
                # if character.average_item_level and character.gender:
                #     skipped += 1
                #     continue
                
                try:
                    # Fetch character profile
                    profile = self.api.get_character_profile(realm_slug, character.name)
                    
                    # Update character with profile data
                    character.achievement_points = profile.get('achievement_points', 0)
                    character.average_item_level = profile.get('average_item_level', 0)
                    character.equipped_item_level = profile.get('equipped_item_level', 0)
                    character.gender = profile.get('gender', {}).get('name', '')
                    character.faction = profile.get('faction', {}).get('name', '')
                    character.character_class = profile.get('character_class', {}).get('name', '')
                    character.race = profile.get('race', {}).get('name', '')
                    
                    # Fetch specialization (Classic uses talent trees)
                    try:
                        specs = self.api.get_character_specializations(realm_slug, character.name)
                        # Extract primary spec from talent tree distribution
                        primary_spec = self.api.get_primary_spec_from_talents(specs)
                        if primary_spec:
                            character.spec_name = primary_spec
                            current_app.logger.debug(f"✅ {character.name}: {primary_spec}")
                        else:
                            character.spec_name = ''
                            current_app.logger.debug(f"⚠️  {character.name}: No spec found (low level or no talents)")
                    except Exception as spec_error:
                        character.spec_name = ''
                        current_app.logger.warning(f"Could not fetch spec for {character.name}: {str(spec_error)}")
                    
                    character.last_updated = datetime.utcnow()
                    successful += 1
                    
                    # Commit every 25 characters to avoid losing progress
                    if idx % 25 == 0:
                        db.session.commit()
                    
                except Exception as e:
                    failed += 1
                    error_msg = str(e)
                    if "404" in error_msg:
                        current_app.logger.debug(f"Profile not found for '{character.name}'")
                    else:
                        current_app.logger.warning(f"Error fetching '{character.name}': {error_msg}")
            
            # Final commit
            db.session.commit()
            
            current_app.logger.info(f"✅ Character detail sync completed!")
            current_app.logger.info(f"   - Total characters: {total_chars}")
            current_app.logger.info(f"   - Successfully synced: {successful}")
            current_app.logger.info(f"   - Failed: {failed}")
            current_app.logger.info(f"   - Skipped: {skipped}")
            
            return {
                'total': total_chars,
                'successful': successful,
                'failed': failed,
                'skipped': skipped
            }
            
        except Exception as e:
            current_app.logger.error(f"❌ Character detail sync failed: {str(e)}")
            db.session.rollback()
            raise e
