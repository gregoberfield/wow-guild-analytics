# Redis Installation and Configuration

## Installation Steps for Production Server

### 1. Install Redis Server

```bash
# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server -y

# Verify installation
redis-server --version
```

### 2. Configure Redis for Production

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf
```

**Key configuration changes:**

```conf
# Bind to localhost only (security)
bind 127.0.0.1 ::1

# Set supervised mode for systemd
supervised systemd

# Set max memory limit (250 MB should be plenty for your use case)
maxmemory 256mb
maxmemory-policy allkeys-lru

# Enable persistence (save snapshots)
save 900 1      # Save if 1 key changed in 900 seconds
save 300 10     # Save if 10 keys changed in 300 seconds
save 60 10000   # Save if 10000 keys changed in 60 seconds

# Set log level
loglevel notice

# Set log file location
logfile /var/log/redis/redis-server.log
```

### 3. Enable and Start Redis

```bash
# Enable Redis to start on boot
sudo systemctl enable redis-server

# Start Redis service
sudo systemctl start redis-server

# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 4. Verify Redis is Running

```bash
# Check Redis info
redis-cli info server

# Check memory usage
redis-cli info memory

# Monitor Redis in real-time (Ctrl+C to exit)
redis-cli monitor
```

### 5. Set Up Redis Security (Optional but Recommended)

```bash
# Generate a strong password
openssl rand -base64 32

# Edit Redis config
sudo nano /etc/redis/redis.conf
```

Add this line (replace with your generated password):
```conf
requirepass YOUR_STRONG_PASSWORD_HERE
```

Restart Redis:
```bash
sudo systemctl restart redis-server

# Test with password
redis-cli -a YOUR_STRONG_PASSWORD_HERE ping
```

**Update your .env file with the password:**
```bash
REDIS_URL=redis://:YOUR_STRONG_PASSWORD_HERE@localhost:6379/0
```

### 6. Monitor Redis Memory Usage

```bash
# Check current memory usage
redis-cli info memory | grep used_memory_human

# Set up memory monitoring alert (optional)
watch -n 5 'redis-cli info memory | grep used_memory_human'
```

### 7. Firewall Configuration (Security)

```bash
# Ensure Redis is NOT accessible from outside
sudo ufw status

# Redis should only be accessible locally (not needed if using default config)
# If firewall is active, ensure port 6379 is NOT open externally
```

## Troubleshooting

### Redis Won't Start

```bash
# Check logs
sudo journalctl -u redis-server -n 50

# Check configuration syntax
redis-server /etc/redis/redis.conf --test-config

# Check if port 6379 is already in use
sudo netstat -tlnp | grep 6379
```

### High Memory Usage

```bash
# Check number of keys
redis-cli dbsize

# Check memory usage by key type
redis-cli --bigkeys

# Flush all data (CAREFUL - this deletes everything!)
redis-cli flushall
```

### Connection Refused

```bash
# Check if Redis is running
sudo systemctl status redis-server

# Check if listening on correct port
sudo netstat -tlnp | grep redis

# Test connection
redis-cli ping
```

## Next Steps

After Redis is installed and running:
1. Install Python dependencies: `pip install -r requirements.txt`
2. Configure Celery workers (see DEPLOYMENT.md)
3. Start Celery worker and beat services
4. Monitor with Flower dashboard

## Useful Commands

```bash
# Restart Redis
sudo systemctl restart redis-server

# View Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Access Redis CLI
redis-cli

# View all keys (in Redis CLI)
KEYS *

# Clear all Celery tasks (if needed)
redis-cli FLUSHDB

# Monitor Redis commands in real-time
redis-cli monitor
```
