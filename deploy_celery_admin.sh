#!/bin/bash
# Administrator tasks for Celery + Redis deployment
# This script must be run by a user with sudo privileges
# Run AFTER deploy_celery.sh has been run by the guildmaestro user

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  WoW Guild Analytics - Celery Admin Setup                   ║"
echo "║  Run this script with sudo privileges                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run with sudo or as root"
    echo "   Usage: sudo ./deploy_celery_admin.sh"
    exit 1
fi

# Verify we're in the right directory
if [ ! -f "celery-worker.service" ]; then
    echo "❌ Error: Cannot find celery-worker.service"
    echo "   Make sure you're in /var/www/guildmaestro"
    exit 1
fi

echo "📋 Installing systemd services..."
cp celery-worker.service /etc/systemd/system/
cp celery-beat.service /etc/systemd/system/
cp flower.service /etc/systemd/system/
echo "✅ Service files copied"

echo ""
echo "🔄 Reloading systemd..."
systemctl daemon-reload
echo "✅ Systemd reloaded"

echo ""
echo "⚙️  Enabling services to start on boot..."
systemctl enable celery-worker
systemctl enable celery-beat
systemctl enable flower
echo "✅ Services enabled"

echo ""
echo "🔐 Setting correct permissions on logs directory..."
chown -R guildmaestro:guildmaestro /var/www/guildmaestro/logs
chmod 755 /var/www/guildmaestro/logs
echo "✅ Permissions set"

echo ""
echo "🚀 Starting Celery services..."
systemctl start celery-worker
systemctl start celery-beat
systemctl start flower

# Wait for services to start
sleep 3

echo ""
echo "📊 Service Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

systemctl is-active --quiet celery-worker && echo "✅ Celery Worker: Running" || echo "❌ Celery Worker: Not running (check logs)"
systemctl is-active --quiet celery-beat && echo "✅ Celery Beat: Running" || echo "❌ Celery Beat: Not running (check logs)"
systemctl is-active --quiet flower && echo "✅ Flower: Running" || echo "❌ Flower: Not running (check logs)"

echo ""
echo "🔄 Restarting Flask application..."
if systemctl is-active --quiet guildmaestro; then
    systemctl restart guildmaestro
    echo "✅ Flask app restarted"
else
    echo "⚠️  Flask app service not found or not running"
    echo "   If your Flask service has a different name, restart it manually"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Admin setup complete!"
echo ""
echo "📖 Verification Steps:"
echo ""
echo "1. Check Celery worker logs:"
echo "   journalctl -u celery-worker -n 50"
echo ""
echo "2. Check Celery beat logs:"
echo "   journalctl -u celery-beat -n 50"
echo ""
echo "3. Check Flower logs:"
echo "   journalctl -u flower -n 50"
echo ""
echo "4. Check Flask app logs:"
echo "   journalctl -u guildmaestro -n 50"
echo ""
echo "5. Test guild sync from web interface"
echo ""
echo "6. Access Flower dashboard:"
echo "   https://yourdomain.com/flower/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
