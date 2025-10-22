# Celery + Redis Deployment Guide

This guide covers deploying the background task processing system using Celery and Redis.

## Prerequisites

- Redis installed and running (see `docs/REDIS_SETUP.md`)
- Python virtual environment activated
- Application code updated with Celery integration

## Step 1: Install Dependencies

```bash
cd /var/www/guildmaestro

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

## Step 2: Update Environment Variables

Add to your `.env` file:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# If you set a Redis password (recommended):
# REDIS_URL=redis://:YOUR_REDIS_PASSWORD@localhost:6379/0

# Flower Dashboard Password (optional but recommended)
FLOWER_PASSWORD=your_secure_password_here
```

## Step 3: Run Database Migration

```bash
# Add Task table to database
python migrate_add_tasks.py
```

Expected output:
```
🔄 Starting migration: Adding Task table...
✅ Task table created successfully
✅ Migration completed successfully!
```

## Step 4: Test Celery Worker Locally

Before setting up systemd services, test that Celery works:

```bash
# Terminal 1: Start Celery worker
celery -A app.celery_config.celery worker --loglevel=info

# Terminal 2: Start Celery Beat (scheduler)
celery -A app.celery_config.celery beat --loglevel=info

# Terminal 3: (Optional) Start Flower monitoring
celery -A app.celery_config.celery flower --port=5555
```

Test by triggering a guild sync from the web interface. You should see:
- Task appears in Celery worker log
- Progress updates in the UI
- Task completes successfully

Press `Ctrl+C` to stop the test workers.

## Step 5: Install Systemd Services

```bash
# Copy service files to systemd directory
sudo cp celery-worker.service /etc/systemd/system/
sudo cp celery-beat.service /etc/systemd/system/
sudo cp flower.service /etc/systemd/system/

# Reload systemd to recognize new services
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat
sudo systemctl enable flower  # Optional

# Start services
sudo systemctl start celery-worker
sudo systemctl start celery-beat
sudo systemctl start flower  # Optional
```

## Step 6: Verify Services are Running

```bash
# Check Celery worker status
sudo systemctl status celery-worker

# Check Celery Beat status
sudo systemctl status celery-beat

# Check Flower status (if enabled)
sudo systemctl status flower

# View logs
sudo journalctl -u celery-worker -n 50 -f
sudo journalctl -u celery-beat -n 50 -f
```

Expected output for each service:
```
● celery-worker.service - Celery Worker for WoW Guild Analytics
   Loaded: loaded (/etc/systemd/system/celery-worker.service; enabled)
   Active: active (running) since...
```

## Step 7: Configure Nginx for Flower (Optional)

If you want to access Flower dashboard via your domain:

```nginx
# Add to your nginx configuration
location /flower/ {
    proxy_pass http://localhost:5555/flower/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support for Flower
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

Reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

Access Flower at: `https://yourdomain.com/flower/`

## Step 8: Test End-to-End

1. Log into your application
2. Go to "Sync Guild" page
3. Enter guild details and submit
4. You should be redirected to task status page
5. Watch progress update in real-time
6. Task should complete and redirect to guild detail page

## Monitoring and Maintenance

### View Celery Logs

```bash
# Worker logs
tail -f /home/guildmanager/wow-guild-analytics/logs/celery-worker.log

# Beat scheduler logs
tail -f /home/guildmanager/wow-guild-analytics/logs/celery-beat.log

# Flower logs
tail -f /home/guildmanager/wow-guild-analytics/logs/flower.log
```

### Restart Services

```bash
# Restart after code changes
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat

# Restart all
sudo systemctl restart celery-worker celery-beat flower
```

### Check Redis Queue

```bash
# See pending tasks
redis-cli llen celery

# View all keys
redis-cli keys "*"

# Monitor Redis in real-time
redis-cli monitor
```

### Clear All Tasks (if needed)

```bash
# WARNING: This clears ALL Celery tasks from Redis
redis-cli -n 0 flushdb

# Or via Flower dashboard: Tasks → Purge
```

## Troubleshooting

### Worker Won't Start

```bash
# Check logs
sudo journalctl -u celery-worker -n 100

# Common issues:
# 1. Redis not running
sudo systemctl status redis-server

# 2. Permission issues with logs directory
sudo chown -R guildmaestro:guildmaestro /var/www/guildmaestro/logs

# 3. Python path issues
which python  # Should show venv python
```

### Tasks Stuck in PENDING

```bash
# Check if worker is processing tasks
redis-cli llen celery

# Check worker processes
ps aux | grep celery

# Restart worker
sudo systemctl restart celery-worker
```

### High Memory Usage

```bash
# Check Redis memory
redis-cli info memory

# Check Celery worker memory
ps aux | grep celery | grep worker

# Adjust worker concurrency in celery-worker.service:
--concurrency=1  # Reduce from 2 to 1
```

### Scheduled Tasks Not Running

```bash
# Check Celery Beat status
sudo systemctl status celery-beat

# View Beat schedule
redis-cli hgetall celery-beat-schedule

# Check Beat logs
sudo journalctl -u celery-beat -n 100
```

## Performance Tuning

### For Your 2 vCPU / 4GB Server

Current settings in `celery-worker.service`:
- `--concurrency=2`: 2 worker processes (good for 2 vCPU)
- `--max-tasks-per-child=1000`: Restart worker after 1000 tasks

If experiencing performance issues:

```bash
# Reduce to 1 worker
--concurrency=1

# Or use threads instead of processes
--pool=solo
```

### Rate Limiting

In `app/celery_config.py`, tasks are rate-limited to prevent API abuse:

```python
task_default_rate_limit='10/m'  # Max 10 tasks per minute
```

Adjust if needed for your Blizzard API limits.

## Scheduled Sync Configuration

The daily guild sync runs at 3 AM UTC by default.

To change the schedule, edit `app/celery_config.py`:

```python
beat_schedule={
    'sync-all-guilds-daily': {
        'task': 'app.tasks.sync_all_guilds_scheduled',
        'schedule': crontab(hour=3, minute=0),  # Change hour here
    },
},
```

After changing, restart Beat:
```bash
sudo systemctl restart celery-beat
```

## Health Checks

### Monitor Task Success Rate

Via Flower dashboard:
1. Access `https://yourdomain.com/flower/`
2. Go to Tasks → Overview
3. Check success vs failure rate

### Monitor Redis Health

```bash
# Quick health check
redis-cli ping  # Should return PONG

# Memory usage
redis-cli info memory | grep used_memory_human

# Connected clients
redis-cli info clients
```

## Backup Considerations

### What to Backup

1. **SQLite database** (includes Task records)
   ```bash
   /var/www/guildmaestro/instance/guild_analytics.db
   ```

2. **Redis data** (optional - tasks are transient)
   ```bash
   # Redis RDB file (if persistence enabled)
   /var/lib/redis/dump.rdb
   ```

### What NOT to Backup

- Celery Beat schedule file (auto-generated)
- Log files (can be large)
- Redis cache (transient data)

## Security Checklist

- [ ] Redis password set (recommended)
- [ ] Flower dashboard password set
- [ ] Flower only accessible via Nginx (not directly on port 5555)
- [ ] Redis bound to localhost only
- [ ] Systemd services running as non-root user
- [ ] Log files have appropriate permissions

## Next Steps

After deployment:
1. Monitor Flower dashboard for first 24 hours
2. Check scheduled sync runs successfully at 3 AM
3. Monitor Redis memory usage
4. Review Celery logs for any errors
5. Test manual guild sync from UI

## Useful Commands Cheat Sheet

```bash
# Service Management
sudo systemctl status celery-worker
sudo systemctl restart celery-worker
sudo systemctl stop celery-worker
sudo systemctl start celery-worker

# Logs
sudo journalctl -u celery-worker -f
tail -f /var/www/guildmaestro/logs/celery-worker.log

# Redis
redis-cli ping
redis-cli info memory
redis-cli llen celery
redis-cli keys "*"

# Celery CLI (with venv activated)
celery -A app.celery_config.celery inspect active
celery -A app.celery_config.celery inspect stats
celery -A app.celery_config.celery inspect registered

# Purge all tasks
celery -A app.celery_config.celery purge
```

## Support

For issues:
1. Check logs: `sudo journalctl -u celery-worker -n 100`
2. Check Redis: `redis-cli ping`
3. Check Flower dashboard: `https://yourdomain.com/flower/`
4. Review this guide's troubleshooting section
