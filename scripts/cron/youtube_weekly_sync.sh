#!/bin/bash
# =============================================================================
# YouTube Competitor Analysis Weekly Sync
# =============================================================================
# Run this script weekly to update competitor insights.
# Recommended: Sundays at 3 AM via cron
#
# Cron entry:
#   0 3 * * 0 /home/rsalars/Projects/dreamweaving/scripts/cron/youtube_weekly_sync.sh >> /home/rsalars/Projects/dreamweaving/logs/youtube_sync.log 2>&1
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
echo "YouTube Weekly Sync - $(date)"
echo "=============================================="

# Step 1: Analyze all categories
echo ""
echo "[1/4] Analyzing competitor videos..."
$PYTHON scripts/ai/youtube_competitor_analyzer.py --weekly-sync --categories all

# Step 2: Analyze our channel
echo ""
echo "[2/4] Analyzing our channel..."
$PYTHON scripts/ai/youtube_competitor_analyzer.py --our-channel

# Step 3: Extract insights
echo ""
echo "[3/4] Extracting patterns and insights..."
$PYTHON scripts/ai/youtube_insights_extractor.py --full-analysis

# Step 4: Sync to Notion (optional - uncomment if Notion DBs are configured)
# echo ""
# echo "[4/4] Syncing to Notion..."
# $PYTHON scripts/ai/notion_youtube_sync.py --sync-all

echo ""
echo "=============================================="
echo "Weekly sync complete - $(date)"
echo "=============================================="
echo ""
echo "Data saved to: $PROJECT_DIR/knowledge/youtube_competitor_data/"
