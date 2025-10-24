import requests
import unicodedata
from datetime import datetime, timedelta
from flask import current_app
from urllib.parse import quote

class BattleNetAPI:
    def __init__(self):
        self.client_id = current_app.config['BNET_CLIENT_ID']
        self.client_secret = current_app.config['BNET_CLIENT_SECRET']
        self.region = current_app.config['BNET_REGION']
        self.access_token = None
        self.token_expires = None
        
        # API endpoints based on region
        self.oauth_url = f'https://{self.region}.battle.net/oauth/token'
        self.api_base = f'https://{self.region}.api.blizzard.com'
        
        # For Classic Anniversary/Era (1.14.x), use 'classic1x' namespace
        # For regular Classic (Cataclysm), use 'classic' namespace
        # For Retail, use 'profile' namespace
        self.namespace = f'profile-classic1x-{self.region}'
        self.namespace_static = f'static-classic1x-{self.region}'
    
    def get_access_token(self):
        """Obtain OAuth access token from Battle.net"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        current_app.logger.info("Requesting new Battle.net OAuth token...")
        response = requests.post(
            self.oauth_url,
            auth=(self.client_id, self.client_secret),
            data={'grant_type': 'client_credentials'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            # Set expiration to 5 minutes before actual expiration for safety
            self.token_expires = datetime.now() + timedelta(seconds=data['expires_in'] - 300)
            current_app.logger.info("✅ OAuth token obtained successfully")
            return self.access_token
        else:
            current_app.logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")
    
    def _make_request(self, endpoint, params=None):
        """Make authenticated request to Battle.net API"""
        token = self.get_access_token()
        
        if params is None:
            params = {}
        
        params['locale'] = 'en_US'
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        url = f"{self.api_base}{endpoint}"
        current_app.logger.debug(f"API Request: {url} with params {params}")
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            current_app.logger.debug(f"API Response: {response.status_code} OK")
            return response.json()
        else:
            current_app.logger.debug(f"API Response: {response.status_code} - {response.text[:200]}")
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    def _normalize_character_name(self, name):
        """
        Normalize character name for API calls.
        IMPORTANT: We must preserve special characters (accents, umlauts).
        The requests library will handle URL encoding automatically.
        Removing accents causes wrong character matches (e.g., Bunnycàkes → bunnycakes fetches wrong char).
        """
        # Convert to lowercase (API is case-insensitive but prefers lowercase)
        # Do NOT manually URL-encode - requests.get() will handle this automatically
        normalized = name.lower()
        return normalized
    
    def get_guild_roster(self, realm_slug, guild_name_slug):
        """Get guild roster from Battle.net API"""
        endpoint = f"/data/wow/guild/{realm_slug}/{guild_name_slug}/roster"
        params = {'namespace': self.namespace}
        return self._make_request(endpoint, params)
    
    def get_guild_info(self, realm_slug, guild_name_slug):
        """Get guild information"""
        endpoint = f"/data/wow/guild/{realm_slug}/{guild_name_slug}"
        params = {'namespace': self.namespace}
        return self._make_request(endpoint, params)
    
    def get_character_profile(self, realm_slug, character_name_slug):
        """Get character profile summary"""
        # Normalize the character name
        normalized_name = self._normalize_character_name(character_name_slug)
        endpoint = f"/profile/wow/character/{realm_slug}/{normalized_name}"
        params = {'namespace': self.namespace}
        current_app.logger.debug(f"Fetching profile for character: {character_name_slug} (normalized: {normalized_name})")
        return self._make_request(endpoint, params)
    
    def get_character_equipment(self, realm_slug, character_name_slug):
        """Get character equipment"""
        normalized_name = self._normalize_character_name(character_name_slug)
        endpoint = f"/profile/wow/character/{realm_slug}/{normalized_name}/equipment"
        params = {'namespace': self.namespace}
        return self._make_request(endpoint, params)
    
    def get_character_specializations(self, realm_slug, character_name_slug):
        """Get character specializations"""
        normalized_name = self._normalize_character_name(character_name_slug)
        endpoint = f"/profile/wow/character/{realm_slug}/{normalized_name}/specializations"
        params = {'namespace': self.namespace}
        return self._make_request(endpoint, params)
    
    def get_character_media(self, realm_slug, character_name_slug):
        """Get character media (avatar, renders)"""
        normalized_name = self._normalize_character_name(character_name_slug)
        endpoint = f"/profile/wow/character/{realm_slug}/{normalized_name}/character-media"
        params = {'namespace': self.namespace}
        return self._make_request(endpoint, params)
    
    def get_character_pvp_summary(self, realm_slug, character_name_slug):
        """Get character PvP summary (honorable kills, pvp rank)"""
        normalized_name = self._normalize_character_name(character_name_slug)
        endpoint = f"/profile/wow/character/{realm_slug}/{normalized_name}/pvp-summary"
        params = {'namespace': self.namespace}
        return self._make_request(endpoint, params)
    
    def get_primary_spec_from_talents(self, spec_data):

        """
        Extract primary specialization from Classic talent tree data.
        In Classic, characters have 3 talent trees and can distribute points across them.
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
    
    def get_playable_classes(self):
        """Get list of playable classes"""
        endpoint = "/data/wow/playable-class/index"
        params = {'namespace': self.namespace_static}
        return self._make_request(endpoint, params)
    
    def get_playable_races(self):
        """Get list of playable races"""
        endpoint = "/data/wow/playable-race/index"
        params = {'namespace': self.namespace_static}
        return self._make_request(endpoint, params)
