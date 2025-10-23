import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    # Supports SQLite (dev/staging) and PostgreSQL (production via Azure Cosmos DB)
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite').lower()  # 'sqlite' or 'postgresql'
    
    if DB_TYPE == 'postgresql':
        # PostgreSQL / Azure Cosmos DB for PostgreSQL
        POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
        POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
        POSTGRES_DB = os.environ.get('POSTGRES_DB')
        POSTGRES_USER = os.environ.get('POSTGRES_USER')
        POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
        POSTGRES_SSL_MODE = os.environ.get('POSTGRES_SSL_MODE', 'require')  # require, verify-ca, verify-full
        
        # Build PostgreSQL connection string
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
            f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode={POSTGRES_SSL_MODE}"
        )
    else:
        # SQLite (default for development/staging)
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///guild_data.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PostgreSQL connection pool settings (only used when DB_TYPE=postgresql)
    if DB_TYPE == 'postgresql':
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
            'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),  # Recycle connections after 1 hour
            'pool_pre_ping': True,  # Verify connections before using them
            'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
        }
    
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
    
    # API Retry configuration
    API_MAX_RETRIES = int(os.environ.get('API_MAX_RETRIES', '3'))  # Max retries for failed API calls
    API_RETRY_DELAY = float(os.environ.get('API_RETRY_DELAY', '1.0'))  # Initial delay in seconds (exponential backoff)
