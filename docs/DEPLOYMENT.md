# Production Deployment Guide

This guide covers deploying WoW Guild Analytics to a production environment using Gunicorn as the WSGI server.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Systemd Service](#systemd-service)
5. [Nginx Configuration](#nginx-configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Quick Start

### Development (Local)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Flask development server
flask run
```

### Production (Server)
```bash
# Install dependencies
pip install -r requirements.txt

# Make startup script executable
chmod +x start_production.sh

# Start with Gunicorn
./start_production.sh
```

---

## Local Development

### Using Flask Development Server

The Flask development server is perfect for local development with features like auto-reload and detailed error pages.

**Start the server:**
```bash
flask run
```

**With debug mode:**
```bash
export FLASK_DEBUG=1
flask run
```

**Custom host/port:**
```bash
flask run --host=0.0.0.0 --port=5000
```

**Features:**
- Auto-reload on code changes
- Interactive debugger
- Detailed error pages
- Single-threaded (not for production!)

---

## Production Deployment

### Prerequisites

1. **Python 3.8+** installed
2. **Virtual environment** (recommended)
3. **Database** configured in `.env`
4. **Environment variables** set in `.env`

### Step 1: Install Gunicorn

Gunicorn is already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 2: Configuration

The application includes a pre-configured `gunicorn.conf.py` file with production-ready settings:

- **Workers:** Auto-calculated based on CPU cores `(2 x cores) + 1`
- **Bind Address:** `0.0.0.0:8000`
- **Timeout:** 30 seconds
- **Max Requests:** 1000 (prevents memory leaks)
- **Logging:** Separate access and error logs

**Edit `gunicorn.conf.py` to customize:**
```python
# Server socket
bind = "0.0.0.0:8000"  # Change port if needed

# Worker processes
workers = 4  # Set specific number of workers

# Timeouts
timeout = 60  # Increase for long-running requests
```

### Step 3: Start Gunicorn

**Option A: Using the startup script (recommended)**
```bash
./start_production.sh
```

**Option B: Direct command**
```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

**Option C: Custom configuration**
```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 30 wsgi:app
```

### Step 4: Verify

Check that the server is running:
```bash
curl http://localhost:8000
```

---

## Systemd Service

Running as a systemd service ensures the application starts on boot and restarts on failure.

### Step 1: Edit Service File

Edit `wow-guild-analytics.service` and update the paths:

```ini
# Change these to match your setup
User=your-username
Group=your-group
WorkingDirectory=/path/to/wow-guild-analytics
EnvironmentFile=/path/to/wow-guild-analytics/.env
ExecStart=/path/to/wow-guild-analytics/venv/bin/gunicorn ...
```

### Step 2: Install Service

```bash
# Copy service file to systemd directory
sudo cp wow-guild-analytics.service /etc/systemd/system/

# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable wow-guild-analytics

# Start the service
sudo systemctl start wow-guild-analytics
```

### Step 3: Manage Service

```bash
# Check status
sudo systemctl status wow-guild-analytics

# View logs
sudo journalctl -u wow-guild-analytics -f

# Restart service
sudo systemctl restart wow-guild-analytics

# Stop service
sudo systemctl stop wow-guild-analytics

# Disable auto-start
sudo systemctl disable wow-guild-analytics
```

---

## Nginx Configuration

Gunicorn should run behind a reverse proxy like Nginx for SSL, static files, and load balancing.

### Basic Nginx Configuration

Create `/etc/nginx/sites-available/wow-guild-analytics`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static {
        alias /var/www/wow-guild-analytics/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Logging
    access_log /var/log/nginx/wow-guild-analytics-access.log;
    error_log /var/log/nginx/wow-guild-analytics-error.log;
}
```

### Enable Nginx Site

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/wow-guild-analytics /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (certbot sets this up automatically)
sudo certbot renew --dry-run
```

---

## Monitoring and Maintenance

### Viewing Logs

**Gunicorn logs:**
```bash
# Access log
tail -f logs/gunicorn-access.log

# Error log
tail -f logs/gunicorn-error.log
```

**Systemd logs:**
```bash
# Follow logs in real-time
sudo journalctl -u wow-guild-analytics -f

# View last 100 lines
sudo journalctl -u wow-guild-analytics -n 100

# View logs since today
sudo journalctl -u wow-guild-analytics --since today
```

**Application logs:**
```bash
tail -f logs/app.log
```

### Performance Tuning

**Worker count calculation:**
- Formula: `(2 x CPU cores) + 1`
- Example: 4 cores = 9 workers
- Adjust based on workload (CPU vs I/O bound)

**Memory considerations:**
- Each worker uses ~50-150MB RAM
- Monitor with: `ps aux | grep gunicorn`

**Timeout settings:**
- Default: 30 seconds
- Increase for long-running requests (API calls, large syncs)
- AI Raid Composer may need 60+ seconds

### Health Checks

Create a simple health check endpoint:

```python
# Add to app/routes.py
@main_bp.route('/health')
def health_check():
    return {'status': 'healthy'}, 200
```

Monitor with:
```bash
curl http://localhost:8000/health
```

### Updating the Application

```bash
# Stop service
sudo systemctl stop wow-guild-analytics

# Pull latest code
git pull

# Install new dependencies
pip install -r requirements.txt

# Run migrations if needed
python migrate_*.py

# Start service
sudo systemctl start wow-guild-analytics
```

### Graceful Reload

Reload without downtime:
```bash
# Send HUP signal for graceful reload
sudo systemctl reload wow-guild-analytics

# Or use Gunicorn directly
kill -HUP $(cat logs/gunicorn.pid)
```

---

## Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

**2. Permission errors**
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/wow-guild-analytics

# Fix permissions
chmod -R 755 /var/www/wow-guild-analytics
```

**3. Workers timing out**
- Increase timeout in `gunicorn.conf.py`
- Check for slow database queries
- Monitor with logs

**4. High memory usage**
- Reduce worker count
- Enable `max_requests` to recycle workers
- Check for memory leaks

---

## Environment Variables

Ensure all required variables are in `.env`:

```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Database
DATABASE_URL=sqlite:///instance/guild_analytics.db

# Battle.net API
BNET_CLIENT_ID=your-client-id
BNET_CLIENT_SECRET=your-client-secret
BNET_REGION=us

# Azure OpenAI (for AI Raid Composer)
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## Security Checklist

- [ ] `.env` file has restricted permissions (600)
- [ ] Secret keys are strong and unique
- [ ] SSL/TLS enabled (HTTPS)
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Application runs as non-root user
- [ ] Database secured with authentication
- [ ] Regular security updates applied
- [ ] Nginx security headers configured
- [ ] Rate limiting enabled (if needed)
- [ ] Backup strategy in place

---

## Performance Optimization

### 1. Database

```bash
# Regular vacuum for SQLite
sqlite3 instance/guild_analytics.db "VACUUM;"

# Consider PostgreSQL for production
# Better concurrency and performance
```

### 2. Static Files

```nginx
# Nginx serves static files directly
location /static {
    alias /var/www/wow-guild-analytics/app/static;
    expires 30d;
    gzip on;
    gzip_types text/css application/javascript;
}
```

### 3. Caching

Consider adding Redis for session storage and caching:
```bash
pip install Flask-Caching redis
```

### 4. Load Balancing

For high traffic, run multiple Gunicorn instances behind Nginx:

```nginx
upstream wow_guild_analytics {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

location / {
    proxy_pass http://wow_guild_analytics;
}
```

---

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup.sh - Daily database backup

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/wow-guild-analytics"
DB_PATH="instance/guild_analytics.db"

mkdir -p $BACKUP_DIR
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/guild_analytics_$DATE.db'"

# Keep only last 7 days
find $BACKUP_DIR -name "guild_analytics_*.db" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /var/www/wow-guild-analytics/backup.sh
```

---

## Summary

**Development:**
```bash
flask run  # Simple, auto-reload, debugging
```

**Production:**
```bash
./start_production.sh  # Gunicorn, multi-worker, production-ready
```

**System Service:**
```bash
sudo systemctl start wow-guild-analytics  # Auto-start, auto-restart
```

For support, check logs:
- `logs/gunicorn-error.log`
- `logs/app.log`
- `sudo journalctl -u wow-guild-analytics -f`
