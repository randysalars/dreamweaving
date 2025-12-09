#!/bin/bash
# =============================================================================
# YouTube Our Channel Daily Check
# =============================================================================
# Run this script daily to track our channel performance.
# Recommended: Daily at 6 AM via cron
#
# Cron entry:
#   0 6 * * * /home/rsalars/Projects/dreamweaving/scripts/cron/youtube_daily_check.sh >> /home/rsalars/Projects/dreamweaving/logs/youtube_daily.log 2>&1
# =============================================================================

set -e

# Configuration
PROJECT_DIR="/home/rsalars/Projects/dreamweaving"
VENV_PATH="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
PYTHON="$VENV_PATH/bin/python3"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

echo "=============================================="
echo "YouTube Daily Check - $(date)"
echo "=============================================="

# Check our channel metrics
$PYTHON scripts/ai/youtube_competitor_analyzer.py --our-channel

echo ""
echo "Daily check complete - $(date)"
