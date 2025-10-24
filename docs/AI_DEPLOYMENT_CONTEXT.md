# AI Assistant Deployment Context

**Purpose:** This document provides context for AI assistants working on this project. It explains the environment setup, deployment procedures, and key differences between environments.

**Last Updated:** October 24, 2025

---

## Project Overview

**Project:** WoW Guild Analytics (GuildMaestro)  
**Repository:** gregoberfield/wow-guild-analytics  
**Main Branch:** main  
**Tech Stack:** Flask, Celery, Redis, PostgreSQL (production), SQLite (dev/staging)

---

## Environment Configuration

### 1. Development (Local WSL)
- **Location:** `/home/greg/wow-guild-analytics` (local workspace)
- **User:** greg
- **Database:** SQLite (instance/guildmaestro.db)
- **Services:** Run manually or via systemd (local)
- **Purpose:** Active development, testing changes

### 2. Staging (Local WSL - Same Machine as Dev)
- **Location:** `/var/www/guildmaestro`
- **User:** greg (with sudo)
- **Database:** SQLite (instance/guildmaestro.db)
- **Celery Concurrency:** 2 workers (SQLite limitation)
- **Services:** 
  - `guildmaestro.service` (Gunicorn)
  - `celery-worker.service`
  - `celery-beat.service` (optional)
- **Purpose:** Pre-production testing on same environment structure as dev

### 3. Production (Azure VM)
- **Hostname:** guildmaestro.dev
- **SSH Access:** `ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev`
- **Application User:** guildmaestro (NOT azureuser)
- **Location:** `/var/www/guildmaestro`
- **Database:** PostgreSQL (Azure Cosmos DB for PostgreSQL)
  - Host: c-guildmaestro-db.z57jcl7woqecbr.postgres.cosmos.azure.com
  - Port: 5432
  - Database: guildmaestro
  - User: citus
  - SSL: Required
- **Celery Concurrency:** 4 workers (PostgreSQL supports higher concurrency)
- **Services:**
  - `guildmaestro.service` (Gunicorn, 3 workers, 600s timeout)
  - `celery-worker.service`
  - `celery-beat.service` (scheduled tasks)
- **Web Server:** Nginx (proxy to Gunicorn socket)
- **Domain:** https://guildmaestro.dev

---

## Deployment Procedures

### Development Environment
**No deployment needed** - working directly in the workspace.

```bash
# Make changes, test locally
cd /home/greg/wow-guild-analytics
# Run tests, etc.
```

### Staging Environment (Local)
**Staging is on the SAME WSL machine** at `/var/www/guildmaestro`.

```bash
# Copy files from dev to staging
cp /home/greg/wow-guild-analytics/path/to/file.py /var/www/guildmaestro/path/to/file.py

# OR for multiple files/full deployment
# (Usually just copy specific files that changed)

# Restart services
sudo systemctl restart celery-worker.service
sudo systemctl restart guildmaestro.service

# Check status
sudo systemctl status celery-worker.service --no-pager | head -15
```

### Production Environment (Azure VM)

**CRITICAL:** Production requires SSH as `azureuser`, then switch to `guildmaestro` user for file operations.

**Step 1: SSH Connection**
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev
```

**Step 2: Pull from GitHub (as guildmaestro user)**
```bash
# Use sudo su to switch to guildmaestro user for git operations
sudo su - guildmaestro -c 'cd /var/www/guildmaestro && git pull'
```

**Step 3: Restart Services (as azureuser with sudo)**
```bash
# Exit from guildmaestro user context, run as azureuser
sudo systemctl restart celery-worker.service
sudo systemctl restart guildmaestro.service

# Check status
sudo systemctl status celery-worker.service --no-pager | head -15
sudo systemctl status guildmaestro.service --no-pager | head -10
```

**Complete Production Deployment (One Command)**
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && git pull' && \
   sudo systemctl restart celery-worker.service guildmaestro.service && \
   sleep 2 && \
   sudo systemctl status celery-worker.service --no-pager | head -15"
```

---

## Common Pitfalls & Solutions

### ❌ Wrong: Trying to SSH as `guildmaestro` user
```bash
# This will fail - guildmaestro user doesn't have SSH access
ssh guildmaestro@guildmaestro.dev
```

### ✅ Correct: SSH as `azureuser`, then switch user
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev
sudo su - guildmaestro
```

### ❌ Wrong: Nested sudo in SSH command
```bash
# This will fail with "a terminal is required to read the password"
ssh azureuser@guildmaestro.dev "sudo su - guildmaestro -c 'cd /var/www && sudo systemctl restart service'"
```

### ✅ Correct: Separate sudo contexts
```bash
# Git pull as guildmaestro, service restart as azureuser
ssh azureuser@guildmaestro.dev "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && git pull' && sudo systemctl restart celery-worker.service"
```

---

## Database Configuration

### Environment Variable: DB_TYPE

**Development/Staging (.env):**
```bash
DB_TYPE=sqlite
# SQLite database file location
DATABASE_URL=sqlite:///instance/guildmaestro.db
```

**Production (.env):**
```bash
DB_TYPE=postgresql
POSTGRES_HOST=c-guildmaestro-db.z57jcl7woqecbr.postgres.cosmos.azure.com
POSTGRES_PORT=5432
POSTGRES_DB=guildmaestro
POSTGRES_USER=citus
POSTGRES_PASSWORD=ziHHbvv47uXD57L
POSTGRES_SSL_MODE=require
```

### Running Database Commands in Production

**Check Database Type:**
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && source venv/bin/activate && python3 -c \"from app import create_app; app = create_app(); db_uri = app.config.get(\\\"SQLALCHEMY_DATABASE_URI\\\"); print(\\\"PostgreSQL\\\" if \\\"postgresql\\\" in db_uri else \\\"SQLite\\\")\"'"
```

**Run Database Query:**
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && source venv/bin/activate && python3 << EOF
from app import create_app, db
from app.models import Character, Guild

app = create_app()
app.app_context().push()

# Your database operations here
guild = Guild.query.first()
print(f\"Guild: {guild.name}, Realm: {guild.realm}\")

# Update example
Character.query.filter(db.or_(Character.realm == None, Character.realm == \"\")).update({\"realm\": guild.realm})
db.session.commit()
print(\"Update complete\")
EOF
'"
```

---

## Service Management

### Check Service Status
```bash
# Development/Staging (local)
sudo systemctl status celery-worker.service
sudo systemctl status guildmaestro.service

# Production (SSH)
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo systemctl status celery-worker.service --no-pager | head -15"
```

### View Logs
```bash
# Development/Staging (local)
sudo journalctl -u celery-worker.service -n 50 --no-pager
tail -f /var/www/guildmaestro/logs/celery-worker.log

# Production (SSH)
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo journalctl -u celery-worker.service -n 50 --no-pager"
```

### Restart Services After Code Changes
```bash
# Both Celery and Gunicorn need restart after code changes
sudo systemctl restart celery-worker.service
sudo systemctl restart guildmaestro.service

# Just Celery after task/service changes
sudo systemctl restart celery-worker.service

# Just Gunicorn after route/template changes
sudo systemctl restart guildmaestro.service
```

---

## Celery Worker Concurrency

### Staging (SQLite)
- **Concurrency:** 2 workers
- **Reason:** SQLite has database lock limitations
- **Service file:** `--concurrency=2`

### Production (PostgreSQL)
- **Concurrency:** 4 workers
- **Reason:** PostgreSQL supports concurrent writes
- **Service file:** `--concurrency=4`

### Why It Matters
- SQLite locks the entire database on write operations
- Higher concurrency with SQLite causes "database is locked" errors
- PostgreSQL uses row-level locking, supports many concurrent operations

---

## Git Workflow

### Typical Workflow
```bash
# 1. Make changes in development
cd /home/greg/wow-guild-analytics
# ... edit files ...

# 2. Commit and push to GitHub
git add .
git commit -m "Description of changes"
git push

# 3. Deploy to staging (local copy)
cp /home/greg/wow-guild-analytics/changed-file.py /var/www/guildmaestro/changed-file.py
sudo systemctl restart celery-worker.service guildmaestro.service

# 4. Test in staging
# ... verify changes work ...

# 5. Deploy to production (git pull)
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && git pull' && \
   sudo systemctl restart celery-worker.service guildmaestro.service"
```

---

## Python Virtual Environment

All environments use Python virtual environments located at `venv/` in the project root.

### Activate Virtual Environment
```bash
# Local (dev/staging)
source venv/bin/activate

# Production (in SSH session as guildmaestro)
source /var/www/guildmaestro/venv/bin/activate
```

### Run Python Commands in Production
```bash
# Always activate venv first
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && source venv/bin/activate && python3 -c \"print(\\\"Hello\\\")\"'"
```

---

## Quick Reference

### File Locations
- **Dev workspace:** `/home/greg/wow-guild-analytics`
- **Staging:** `/var/www/guildmaestro` (same machine)
- **Production:** `/var/www/guildmaestro` (Azure VM)
- **SSH Key:** `/home/greg/guildmaestro-prod_key.pem`

### User Contexts
- **Dev:** greg
- **Staging:** greg (with sudo)
- **Production SSH:** azureuser
- **Production App:** guildmaestro

### Service Names
- `guildmaestro.service` - Gunicorn web server
- `celery-worker.service` - Celery worker
- `celery-beat.service` - Celery scheduler (periodic tasks)

### Database Types
- **Dev/Staging:** SQLite
- **Production:** PostgreSQL (Azure Cosmos DB)

---

## Testing Deployment

### Verify Git Commits in Production
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && git log --oneline -5'"
```

### Verify File Exists
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'ls -la /var/www/guildmaestro/path/to/file.py'"
```

### Check Running Processes
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "ps aux | grep -E 'celery|gunicorn'"
```

---

## Emergency Procedures

### Services Won't Start
```bash
# Check detailed logs
sudo journalctl -u celery-worker.service -n 100 --no-pager
sudo journalctl -u guildmaestro.service -n 100 --no-pager

# Check for syntax errors
cd /var/www/guildmaestro
source venv/bin/activate
python3 -m py_compile app/routes.py  # or any changed file
```

### Database Issues
```bash
# Check database connectivity (production)
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && source venv/bin/activate && python3 -c \"from app import create_app, db; app = create_app(); app.app_context().push(); print(db.engine.url)\"'"
```

### Rollback Deployment
```bash
# In production, git pull previous commit
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && git reset --hard HEAD~1' && \
   sudo systemctl restart celery-worker.service guildmaestro.service"
```

---

## Notes for AI Assistants

1. **Always use the full SSH command** with the key path when accessing production
2. **Never assume** you can SSH directly as guildmaestro - always go through azureuser
3. **Remember** staging and dev are on the same WSL machine (different directories)
4. **Don't forget** to restart services after deployment
5. **Database operations** in production require the venv activation and proper escaping
6. **Celery concurrency** matters - don't suggest changing it without understanding the DB backend
7. **When creating scripts** to run in production, use heredoc (EOF) to avoid escaping issues
8. **Git operations** in production must be done as the guildmaestro user
9. **Service restarts** must be done as azureuser (not guildmaestro)
10. **Always verify** deployments by checking git log or file existence

---

## Common Tasks Cheat Sheet

### Deploy Code Change to Production
```bash
# Commit locally first
git add app/services.py
git commit -m "Fix issue"
git push

# Deploy to production
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && git pull' && \
   sudo systemctl restart celery-worker.service guildmaestro.service"
```

### Check Production Logs
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo journalctl -u celery-worker.service -n 50 --no-pager"
```

### Run Database Update in Production
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev "sudo su - guildmaestro -c 'cd /var/www/guildmaestro && source venv/bin/activate && python3 << EOF
from app import create_app, db
from app.models import Character, Guild

app = create_app()
app.app_context().push()

# Update logic here
guild = Guild.query.first()
Character.query.filter(Character.realm.is_(None)).update({\"realm\": guild.realm})
db.session.commit()
print(\"Done\")
EOF
'"
```

### Check Service Status in Production
```bash
ssh -i /home/greg/guildmaestro-prod_key.pem azureuser@guildmaestro.dev \
  "sudo systemctl status celery-worker.service guildmaestro.service --no-pager"
```

---

**End of Document**
