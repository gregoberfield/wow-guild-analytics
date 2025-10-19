#!/usr/bin/env python3
"""
Test script to investigate WoW Classic Anniversary API endpoints and namespaces
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# API credentials
CLIENT_ID = os.getenv('BNET_CLIENT_ID')
CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')
REGION = os.getenv('BNET_REGION', 'us')

# Get OAuth token
def get_access_token():
    oauth_url = f'https://{REGION}.battle.net/oauth/token'
    response = requests.post(
        oauth_url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials'}
    )
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None

# Test different namespace variations
def test_guild_endpoint(realm_slug, guild_slug, namespace):
    token = get_access_token()
    if not token:
        return
    
    api_base = f'https://{REGION}.api.blizzard.com'
    endpoint = f"/data/wow/guild/{realm_slug}/{guild_slug}"
    
    headers = {'Authorization': f'Bearer {token}'}
    params = {'namespace': namespace, 'locale': 'en_US'}
    
    url = f"{api_base}{endpoint}"
    print(f"\n{'='*80}")
    print(f"Testing: {namespace}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS!")
        data = response.json()
        print(f"Guild: {data.get('name')}")
        print(f"Realm: {data.get('realm', {}).get('name')}")
        print(f"Faction: {data.get('faction', {}).get('name')}")
        return True
    else:
        print(f"❌ FAILED: {response.text[:200]}")
        return False

if __name__ == "__main__":
    print("WoW Classic Anniversary API Namespace Investigation")
    print("="*80)
    
    # Guild info
    realm_slug = "dreamscythe"
    guild_slug = "hordecore-casuals"
    
    print(f"\nGuild: {guild_slug}")
    print(f"Realm: {realm_slug}")
    
    # Test different namespaces
    namespaces = [
        'profile-classic-us',           # Original Classic
        'profile-classic1x-us',         # Classic Era (1.14)
        'dynamic-classic-us',           # Dynamic Classic
        'profile-classic-anniversary-us', # Anniversary (guess)
        'profile-classic-era-us',       # Era (guess)
        'static-classic-us',            # Static Classic
        'dynamic-classic1x-us',         # Dynamic Classic Era
    ]
    
    print(f"\n\nTesting {len(namespaces)} different namespace variations...\n")
    
    for ns in namespaces:
        if test_guild_endpoint(realm_slug, guild_slug, ns):
            print(f"\n🎉 FOUND WORKING NAMESPACE: {ns}")
            break
    
    print("\n" + "="*80)
    print("Testing complete!")
