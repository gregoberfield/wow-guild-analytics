import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///guild_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Battle.net API credentials
    BNET_CLIENT_ID = os.environ.get('BNET_CLIENT_ID')
    BNET_CLIENT_SECRET = os.environ.get('BNET_CLIENT_SECRET')
    BNET_REGION = os.environ.get('BNET_REGION', 'us')  # us, eu, kr, tw, cn
    
    # Azure OpenAI / AI Foundry Configuration
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
    AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-08-01-preview')
    
    # Guild configuration
    GUILD_NAME = os.environ.get('GUILD_NAME', '')
    GUILD_REALM = os.environ.get('GUILD_REALM', '')
    GUILD_REALM_SLUG = os.environ.get('GUILD_REALM_SLUG', '')  # lowercase with hyphens
