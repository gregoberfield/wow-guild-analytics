#!/bin/bash
#
# Production startup script for WoW Guild Analytics
# This script starts the application using Gunicorn WSGI server
#
# Usage:
#   ./start_production.sh         # Start in foreground
#   ./start_production.sh &        # Start in background
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  WoW Guild Analytics - Production Startup${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please create a .env file with your configuration."
    echo "You can use .env.example as a template."
    exit 1
fi

# Create logs directory if it doesn't exist
if [ ! -d logs ]; then
    echo -e "${YELLOW}Creating logs directory...${NC}"
    mkdir -p logs
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${RED}ERROR: Gunicorn is not installed!${NC}"
    echo "Install it with: pip install -r requirements.txt"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

echo -e "${GREEN}✓${NC} Environment variables loaded"
echo -e "${GREEN}✓${NC} Logs directory ready"
echo ""

# Display configuration
echo -e "${YELLOW}Configuration:${NC}"
echo "  • WSGI Application: wsgi:app"
echo "  • Config File: gunicorn.conf.py"
echo "  • Bind Address: 0.0.0.0:8000"
echo "  • Workers: Auto-detected based on CPU cores"
echo "  • Access Log: logs/gunicorn-access.log"
echo "  • Error Log: logs/gunicorn-error.log"
echo ""

# Start Gunicorn
echo -e "${GREEN}Starting Gunicorn...${NC}"
echo ""

exec gunicorn -c gunicorn.conf.py wsgi:app
