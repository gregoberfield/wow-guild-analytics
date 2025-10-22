#!/bin/bash
# Quick deployment script for Celery + Redis
# Run this on your production server after pulling code
# Part 1: Run as guildmaestro user
# Part 2: Run sudo commands separately (see end of script)

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  WoW Guild Analytics - Celery + Redis Deployment            ║"
echo "║  Part 1: User-level setup (run as guildmaestro)             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as guildmaestro user
if [ "$USER" != "guildmaestro" ]; then
    echo "⚠️  Warning: This script should be run as 'guildmaestro' user"
    echo "Switch user: sudo -u guildmaestro -i"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run migration
echo "🗄️  Running database migration..."
python migrate_add_tasks.py

# Create logs directory and set permissions
echo "📁 Creating logs directory..."
mkdir -p logs
chmod 755 logs

# Ensure proper ownership of entire application
echo "🔐 Setting file permissions..."
if [ -d logs ]; then
    echo "✅ Logs directory created"
else
    echo "❌ Failed to create logs directory"
    exit 1
fi

# Check if Redis is installed
echo "🔍 Checking Redis installation..."
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis is not installed!"
    echo "    An administrator needs to install it:"
    echo "    sudo apt install redis-server -y"
    echo ""
    echo "    Continuing anyway..."
else
    # Check if Redis is running
    if redis-cli ping &> /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is installed but not running"
        echo "    An administrator needs to start it:"
        echo "    sudo systemctl start redis-server"
        echo ""
        echo "    Continuing anyway..."
    fi
fi

# Check .env file for REDIS_URL
if ! grep -q "REDIS_URL" .env 2>/dev/null; then
    echo "⚠️  REDIS_URL not found in .env file"
    echo "Adding default REDIS_URL..."
    echo "" >> .env
    echo "# Redis Configuration" >> .env
    echo "REDIS_URL=redis://localhost:6379/0" >> .env
    echo "✅ Added REDIS_URL to .env"
fi

# Check for FLOWER_PASSWORD
if ! grep -q "FLOWER_PASSWORD" .env 2>/dev/null; then
    echo "⚠️  FLOWER_PASSWORD not found in .env file"
    echo "You should add it manually to .env:"
    echo "FLOWER_PASSWORD=your_secure_password"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ User-level setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "║  Part 2: Administrator tasks (requires sudo)                ║"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  The following commands need to be run by an administrator"
echo "    (someone with sudo access):"
echo ""
echo "# 1. Install systemd services"
echo "sudo cp /var/www/guildmaestro/celery-worker.service /etc/systemd/system/"
echo "sudo cp /var/www/guildmaestro/celery-beat.service /etc/systemd/system/"
echo "sudo cp /var/www/guildmaestro/celery-flower.service /etc/systemd/system/"
echo ""
echo "# 2. Reload systemd"
echo "sudo systemctl daemon-reload"
echo ""
echo "# 3. Enable services"
echo "sudo systemctl enable celery-worker"
echo "sudo systemctl enable celery-beat"
echo "sudo systemctl enable flower"
echo ""
echo "# 4. Ensure logs directory has correct permissions"
echo "sudo chown -R guildmaestro:guildmaestro /var/www/guildmaestro/logs"
echo ""
echo "# 5. Start services"
echo "sudo systemctl start celery-worker"
echo "sudo systemctl start celery-beat"
echo "sudo systemctl start flower"
echo ""
echo "# 6. Restart Flask app"
echo "sudo systemctl restart guildmaestro"
echo ""
echo "# 7. Check status"
echo "sudo systemctl status celery-worker"
echo "sudo systemctl status celery-beat"
echo "sudo systemctl status flower"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "� Copy the commands above and provide them to your administrator,"
echo "   or run them yourself if you have sudo access."
echo ""
echo "📚 Documentation:"
echo "  - docs/REDIS_SETUP.md"
echo "  - docs/CELERY_DEPLOYMENT.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
