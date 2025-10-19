#!/usr/bin/env python3
"""
Test character name normalization for special characters
"""
import os
import sys
import unicodedata
from urllib.parse import quote

def normalize_character_name(name):
    """
    Normalize character name for API calls.
    Converts special characters and ensures proper URL encoding.
    """
    # Remove accents/diacritics (e.g., Gewölbe -> Gewolbe)
    normalized = unicodedata.normalize('NFKD', name)
    normalized = normalized.encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase
    normalized = normalized.lower()
    # URL encode any remaining special characters
    normalized = quote(normalized, safe='')
    return normalized

# Test cases
test_names = [
    "Cptmorgue",
    "Bingojones", 
    "Gewölbe",
    "Årthas",
    "Démon",
    "Naïve",
    "Café",
    "Señor",
]

print("Character Name Normalization Test")
print("=" * 70)
print(f"{'Original Name':<20} {'Normalized Name':<20} {'URL Encoded':<20}")
print("=" * 70)

for name in test_names:
    normalized = normalize_character_name(name)
    print(f"{name:<20} {normalized:<20} {normalized:<20}")

print("=" * 70)

# Now test with actual API if credentials are available
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    import requests
    
    load_dotenv()
    
    CLIENT_ID = os.getenv('BNET_CLIENT_ID')
    CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')
    REGION = 'us'
    
    if CLIENT_ID and CLIENT_SECRET:
        print("\n🔍 Testing with Battle.net API...")
        
        # Get OAuth token
        oauth_url = f'https://{REGION}.battle.net/oauth/token'
        response = requests.post(
            oauth_url,
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={'grant_type': 'client_credentials'}
        )
        
        if response.status_code == 200:
            token = response.json()['access_token']
            print("✅ OAuth token obtained")
            
            # Test a character with special chars
            test_char = "Gewölbe"
            normalized = normalize_character_name(test_char)
            
            api_base = f'https://{REGION}.api.blizzard.com'
            endpoint = f"/profile/wow/character/dreamscythe/{normalized}"
            
            headers = {'Authorization': f'Bearer {token}'}
            params = {'namespace': 'profile-classic1x-us', 'locale': 'en_US'}
            
            print(f"\nTesting character: {test_char}")
            print(f"Normalized to: {normalized}")
            print(f"API endpoint: {endpoint}")
            
            response = requests.get(f"{api_base}{endpoint}", headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Character found: {data.get('name')}")
            elif response.status_code == 404:
                print(f"⚠️  Character not found (404) - May be private or not on this realm")
            else:
                print(f"❌ Failed: {response.status_code}")
        else:
            print("❌ Failed to get OAuth token")
    else:
        print("\n⚠️  Skipping API test (credentials not found)")
        
except ImportError as e:
    print(f"\n⚠️  Skipping API test (missing dependencies: {e})")
