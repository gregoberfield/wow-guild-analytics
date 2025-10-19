#!/usr/bin/env python3
"""
Quick test to verify the guild can be synced successfully
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('BNET_CLIENT_ID')
CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')
REGION = 'us'

# Get OAuth token
oauth_url = f'https://{REGION}.battle.net/oauth/token'
response = requests.post(
    oauth_url,
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={'grant_type': 'client_credentials'}
)

if response.status_code == 200:
    token = response.json()['access_token']
    print("✅ OAuth token obtained successfully")
else:
    print(f"❌ Failed to get token: {response.status_code}")
    exit(1)

# Test guild info
api_base = f'https://{REGION}.api.blizzard.com'
endpoint = "/data/wow/guild/dreamscythe/hordecore-casuals"
namespace = 'profile-classic1x-us'

headers = {'Authorization': f'Bearer {token}'}
params = {'namespace': namespace, 'locale': 'en_US'}

print(f"\nTesting Guild Info Endpoint...")
response = requests.get(f"{api_base}{endpoint}", headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Guild Info Retrieved Successfully!")
    print(f"   Guild: {data.get('name')}")
    print(f"   Realm: {data.get('realm', {}).get('name')}")
    print(f"   Faction: {data.get('faction', {}).get('name')}")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)
    exit(1)

# Test roster
endpoint = "/data/wow/guild/dreamscythe/hordecore-casuals/roster"
print(f"\nTesting Guild Roster Endpoint...")
response = requests.get(f"{api_base}{endpoint}", headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    members = data.get('members', [])
    print(f"✅ Guild Roster Retrieved Successfully!")
    print(f"   Total Members: {len(members)}")
    if members:
        print(f"\n   Sample Members:")
        for member in members[:5]:
            char = member.get('character', {})
            print(f"   - {char.get('name')} (Level {char.get('level')}, {char.get('playable_class', {}).get('name')})")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)
    exit(1)

print(f"\n{'='*60}")
print("🎉 All tests passed! The guild can be synced successfully.")
print(f"{'='*60}")
print("\nYou can now sync your guild through the web interface:")
print("  Realm Slug: dreamscythe")
print("  Guild Slug: hordecore-casuals")
