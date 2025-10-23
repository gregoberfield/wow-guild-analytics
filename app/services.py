from app.models import Guild, Character, GuildMemberHistory, CharacterProgressionHistory
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
            
            # Track if this is the initial sync (no previous last_updated timestamp)
            is_initial_sync = guild is None or guild.last_updated is None
            
            if not guild:
                current_app.logger.info("Creating new guild record in database (initial sync)")
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
            added_count = 0
            
            # Track current member IDs to identify members who left
            current_member_bnet_ids = set()
            current_member_names = set()
            
            # Get existing characters to track new additions
            existing_character_ids = set()
            existing_characters_map = {}
            if guild.id:
                for char in Character.query.filter_by(guild_id=guild.id).all():
                    if char.bnet_id:
                        existing_character_ids.add(char.bnet_id)
                    existing_characters_map[(char.name, char.realm)] = char
            
            # Process each member
            current_app.logger.info(f"Processing {len(members)} members...")
            for idx, member in enumerate(members, 1):
                character_data = member.get('character', {})
                char_name = character_data.get('name')
                char_bnet_id = character_data.get('id')  # Battle.net character ID
                char_realm = character_data.get('realm', {}).get('slug', realm_slug)
                
                # Track this member as current
                if char_bnet_id:
                    current_member_bnet_ids.add(char_bnet_id)
                current_member_names.add((char_name, character_data.get('realm', {}).get('name', '')))
                
                if idx % 50 == 0:
                    current_app.logger.info(f"Progress: {idx}/{len(members)} members processed...")
                
                # Get or create character (try by bnet_id first, then by name)
                character = None
                is_new_character = False
                
                if char_bnet_id:
                    character = Character.query.filter_by(bnet_id=char_bnet_id).first()
                    if not character and char_bnet_id not in existing_character_ids:
                        is_new_character = True
                
                if not character:
                    character = Character.query.filter_by(
                        name=char_name,
                        realm=character_data.get('realm', {}).get('name', '')
                    ).first()
                    if not character:
                        is_new_character = True
                
                if not character:
                    character = Character(name=char_name)
                    is_new_character = True
                
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
                    character.last_login_timestamp = profile.get('last_login_timestamp')  # Unix timestamp in milliseconds
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
                
                # Flush to ensure character.id is available for queries
                db.session.flush()
                
                # Track character progression (level and item level changes)
                # Only track if character has meaningful data and isn't brand new
                if not is_new_character and character.id and guild.id:
                    should_track = False
                    
                    # Get the most recent progression entry for this character
                    last_progression = CharacterProgressionHistory.query.filter_by(
                        character_id=character.id,
                        guild_id=guild.id
                    ).order_by(CharacterProgressionHistory.timestamp.desc()).first()
                    
                    # Track only if this is the first entry OR if there's been a change
                    if not last_progression:
                        # First progression entry for this character
                        should_track = True
                    else:
                        # Check if any stat has changed from the last recorded value
                        level_changed = last_progression.character_level != character.level
                        avg_ilvl_changed = last_progression.average_item_level != character.average_item_level
                        equipped_ilvl_changed = last_progression.equipped_item_level != character.equipped_item_level
                        
                        if level_changed or avg_ilvl_changed or equipped_ilvl_changed:
                            should_track = True
                            current_app.logger.debug(
                                f"Progression change detected for {character.name}: "
                                f"Level {last_progression.character_level or 'None'}->{character.level or 'None'}, "
                                f"Avg iLvl {last_progression.average_item_level or 'None'}->{character.average_item_level or 'None'}, "
                                f"Equipped iLvl {last_progression.equipped_item_level or 'None'}->{character.equipped_item_level or 'None'}"
                            )
                    
                    # Only create entry if there's meaningful data and a change was detected
                    if should_track and (character.level or character.average_item_level):
                        progression_entry = CharacterProgressionHistory(
                            character_id=character.id,
                            guild_id=guild.id,
                            character_level=character.level,
                            average_item_level=character.average_item_level,
                            equipped_item_level=character.equipped_item_level
                        )
                        db.session.add(progression_entry)
                        current_app.logger.info(f"✓ Progression tracked for {character.name}")
                
                # Log new member addition if this is their first time in the guild
                # Skip history tracking during initial sync to avoid polluting history with existing members
                if is_new_character and guild.id and not is_initial_sync:
                    history_entry = GuildMemberHistory(
                        guild_id=guild.id,
                        character_name=char_name,
                        character_level=character.level,
                        character_class=character.character_class or 'Unknown',
                        action='added'
                    )
                    db.session.add(history_entry)
                    added_count += 1
            
            # Remove characters that are no longer in the guild
            current_app.logger.info("Checking for members who left the guild...")
            existing_characters = Character.query.filter_by(guild_id=guild.id).all()
            removed_count = 0
            
            for character in existing_characters:
                # Check if this character is still in the current roster
                is_still_member = False
                
                # Check by bnet_id first (most reliable)
                if character.bnet_id and character.bnet_id in current_member_bnet_ids:
                    is_still_member = True
                # Fall back to name + realm check
                elif (character.name, character.realm) in current_member_names:
                    is_still_member = True
                
                # Remove character if they're no longer in the guild
                if not is_still_member:
                    current_app.logger.info(f"Removing '{character.name}' (no longer in guild)")
                    
                    # Log member removal (skip during initial sync)
                    if not is_initial_sync:
                        history_entry = GuildMemberHistory(
                            guild_id=guild.id,
                            character_name=character.name,
                            character_level=character.level,
                            character_class=character.character_class or 'Unknown',
                            action='removed'
                        )
                        db.session.add(history_entry)
                    
                    # Delete progression history for this character in this guild
                    CharacterProgressionHistory.query.filter_by(
                        character_id=character.id,
                        guild_id=guild.id
                    ).delete()
                    
                    db.session.delete(character)
                    removed_count += 1
            
            db.session.commit()
            
            current_app.logger.info(f"✅ Guild sync completed successfully!")
            current_app.logger.info(f"   - Sync type: {'INITIAL' if is_initial_sync else 'UPDATE'}")
            current_app.logger.info(f"   - Total members: {len(members)}")
            current_app.logger.info(f"   - Profiles retrieved: {successful_profiles}")
            current_app.logger.info(f"   - Profiles unavailable: {failed_profiles}")
            if not is_initial_sync:
                current_app.logger.info(f"   - Members added: {added_count}")
                current_app.logger.info(f"   - Members removed: {removed_count}")
            else:
                current_app.logger.info(f"   - History tracking: Skipped (initial sync)")
            
            return guild, len(members), removed_count
            
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
                    # Retry logic for transient API errors (504, 503, 500, connection errors)
                    max_retries = current_app.config.get('API_MAX_RETRIES', 3)
                    retry_delay = current_app.config.get('API_RETRY_DELAY', 1.0)
                    
                    profile = None
                    last_error = None
                    
                    for attempt in range(max_retries):
                        try:
                            # Fetch character profile
                            profile = self.api.get_character_profile(realm_slug, character.name)
                            break  # Success, exit retry loop
                        except Exception as api_error:
                            last_error = api_error
                            error_msg = str(api_error)
                            
                            # Check if this is a retryable error
                            is_retryable = any(code in error_msg for code in ['504', '503', '500', 'timeout', 'connection'])
                            
                            if is_retryable and attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                                current_app.logger.warning(f"API error for '{character.name}' (attempt {attempt + 1}/{max_retries}): {error_msg}. Retrying in {wait_time}s...")
                                import time
                                time.sleep(wait_time)
                            else:
                                # Not retryable or out of retries
                                raise api_error
                    
                    if not profile:
                        raise last_error or Exception("Failed to fetch profile")
                    
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
                    
                    # Fetch character media (avatar)
                    try:
                        media = self.api.get_character_media(realm_slug, character.name)
                        # Extract avatar URL from assets
                        for asset in media.get('assets', []):
                            if asset.get('key') == 'avatar':
                                character.avatar_url = asset.get('value')
                                current_app.logger.debug(f"✅ {character.name}: Avatar URL updated")
                                break
                    except Exception as media_error:
                        # Avatar is optional, don't fail if not available
                        current_app.logger.debug(f"Could not fetch media for {character.name}: {str(media_error)}")
                    
                    character.last_updated = datetime.utcnow()
                    successful += 1

                    
                    # Commit every 25 characters to avoid losing progress
                    if idx % 25 == 0:
                        db.session.commit()
                    
                except Exception as e:
                    failed += 1
                    error_msg = str(e)
                    # Log ALL errors temporarily for debugging
                    current_app.logger.error(f"SYNC ERROR for '{character.name}': {error_msg}")
                    import traceback
                    current_app.logger.error(f"Traceback: {traceback.format_exc()}")
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
