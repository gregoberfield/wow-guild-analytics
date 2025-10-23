# PostgreSQL / Azure Cosmos DB for PostgreSQL Setup

This application supports both SQLite (for development/staging) and PostgreSQL (for production via Azure Cosmos DB for PostgreSQL).

## Database Configuration

The database type is controlled by the `DB_TYPE` environment variable:
- `DB_TYPE=sqlite` - Uses SQLite (default for dev/staging)
- `DB_TYPE=postgresql` - Uses PostgreSQL/Azure Cosmos DB

## Azure Cosmos DB for PostgreSQL Connection Details

You'll need the following information from your Azure Cosmos DB for PostgreSQL cluster:

### Required Environment Variables

```bash
DB_TYPE=postgresql
POSTGRES_HOST=your-cosmos-cluster.postgres.cosmos.azure.com
POSTGRES_PORT=5432
POSTGRES_DB=citus
POSTGRES_USER=citus
POSTGRES_PASSWORD=your-password-here
POSTGRES_SSL_MODE=require
```

### Getting Connection Information from Azure Portal

1. **Navigate to your Cosmos DB cluster** in Azure Portal
2. **Go to Settings > Connection strings**
3. You'll find:
   - **Host**: `your-cluster-name.postgres.cosmos.azure.com`
   - **Port**: `5432` (default)
   - **Database**: `citus` (default for Cosmos DB for PostgreSQL)
   - **Username**: `citus` (default)
   - **Password**: Your admin password (set during cluster creation)

### Connection String Format

The application automatically builds the connection string from the environment variables:

```
postgresql://citus:YOUR_PASSWORD@your-cluster.postgres.cosmos.azure.com:5432/citus?sslmode=require
```

### SSL Mode

Azure Cosmos DB for PostgreSQL requires SSL connections. Use:
- `POSTGRES_SSL_MODE=require` - Require SSL but don't verify certificate (recommended)
- `POSTGRES_SSL_MODE=verify-ca` - Verify SSL certificate authority
- `POSTGRES_SSL_MODE=verify-full` - Full SSL verification (most secure)

## Database Migration from SQLite to PostgreSQL

If you're migrating from SQLite to PostgreSQL:

### Option 1: Manual Migration (Recommended)

1. Export data from SQLite using the existing models
2. Set up PostgreSQL connection in production
3. Run migrations to create tables:
   ```bash
   flask db upgrade
   ```
4. Import data using custom migration scripts

### Option 2: Use pgloader

```bash
pgloader sqlite:///path/to/guild_data.db \
  postgresql://citus:password@your-cluster.postgres.cosmos.azure.com:5432/citus
```

## Connection Pool Settings (Optional)

For production PostgreSQL deployments, you can tune the connection pool:

```bash
DB_POOL_SIZE=10          # Number of connections to maintain
DB_POOL_RECYCLE=3600     # Recycle connections after 1 hour
DB_MAX_OVERFLOW=20       # Maximum overflow connections
```

These settings are automatically applied when `DB_TYPE=postgresql`.

## Testing the Connection

You can test the PostgreSQL connection before deploying:

```python
from config import Config
from sqlalchemy import create_engine

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
print("✅ PostgreSQL connection successful!")
connection.close()
```

## Switching Between Databases

### Development (SQLite)
```bash
DB_TYPE=sqlite
DATABASE_URL=sqlite:///guild_data.db
```

### Production (PostgreSQL)
```bash
DB_TYPE=postgresql
POSTGRES_HOST=your-cluster.postgres.cosmos.azure.com
POSTGRES_PORT=5432
POSTGRES_DB=citus
POSTGRES_USER=citus
POSTGRES_PASSWORD=your-password
POSTGRES_SSL_MODE=require
```

## Important Notes

1. **SSL is required** for Azure Cosmos DB for PostgreSQL connections
2. **Default database name** is `citus` (don't change unless you created a custom database)
3. **Default username** is `citus` (the admin user)
4. **Connection pooling** is automatically enabled for PostgreSQL to handle concurrent requests
5. **SQLite limitations** are removed with PostgreSQL (no more database locks during concurrent writes!)

## Troubleshooting

### Connection Refused
- Verify firewall rules in Azure Portal allow your IP
- Check that `POSTGRES_HOST` is correct

### SSL Error
- Ensure `POSTGRES_SSL_MODE=require` is set
- Azure Cosmos DB for PostgreSQL requires SSL

### Authentication Failed
- Verify `POSTGRES_PASSWORD` is correct
- Check that the user has proper permissions

### Database Not Found
- The default database is `citus`
- If you created a custom database, update `POSTGRES_DB`
