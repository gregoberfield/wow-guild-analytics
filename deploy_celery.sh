#!/bin/bash
# Quick deployment script for Celery + Redis
# Run this on your production server after pulling code

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  WoW Guild Analytics - Celery + Redis Deployment            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as guildmaestro user
if [ "$USER" != "guildmaestro" ]; then
    echo "⚠️  Warning: This script should be run as 'guildmaestro' user"
    echo "Switch user: sudo -u guildmaestro -i"
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

# Check if Redis is installed
echo "🔍 Checking Redis installation..."
if ! command -v redis-cli &> /dev/null; then
    echo "❌ Redis is not installed!"
    echo "Install with: sudo apt install redis-server -y"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo "❌ Redis is not running!"
    echo "Start with: sudo systemctl start redis-server"
    exit 1
fi

echo "✅ Redis is running"

# Check .env file for REDIS_URL
if ! grep -q "REDIS_URL" .env 2>/dev/null; then
    echo "⚠️  REDIS_URL not found in .env file"
    echo "Adding default REDIS_URL..."
    echo "" >> .env
    echo "# Redis Configuration" >> .env
    echo "REDIS_URL=redis://localhost:6379/0" >> .env
fi

# Install systemd services
echo "📋 Installing systemd services..."
echo "You will need to enter sudo password..."

sudo cp celery-worker.service /etc/systemd/system/
sudo cp celery-beat.service /etc/systemd/system/
sudo cp flower.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable services
echo "⚙️  Enabling services..."
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat
sudo systemctl enable flower

# Start services
echo "🚀 Starting services..."
sudo systemctl start celery-worker
sudo systemctl start celery-beat
sudo systemctl start flower

# Wait a moment for services to start
sleep 3

# Check service status
echo ""
echo "📊 Service Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo systemctl is-active --quiet celery-worker && echo "✅ Celery Worker: Running" || echo "❌ Celery Worker: Not running"
sudo systemctl is-active --quiet celery-beat && echo "✅ Celery Beat: Running" || echo "❌ Celery Beat: Not running"
sudo systemctl is-active --quiet flower && echo "✅ Flower: Running" || echo "❌ Flower: Not running"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo ""
echo "📖 Next Steps:"
echo "  1. Restart Flask app: sudo systemctl restart guildmaestro"
echo "  2. Test guild sync from web interface"
echo "  3. Access Flower dashboard: https://yourdomain.com/flower/"
echo "  4. Monitor logs: sudo journalctl -u celery-worker -f"
echo ""
echo "📚 Documentation:"
echo "  - docs/REDIS_SETUP.md"
echo "  - docs/CELERY_DEPLOYMENT.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
