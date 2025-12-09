#!/bin/bash
# Daily Analytics Collection
# Fetches YouTube analytics for videos uploaded 48+ hours ago
#
# Cron: 0 22 * * * (3pm MST = 10pm UTC)
# Run manually: ./cron/daily-analytics.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/data/logs/automation"
LOG_FILE="$LOG_DIR/daily-analytics-$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "=== Daily Analytics Collection: $(date) ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"
source venv/bin/activate

python -m scripts.automation.automated_learning --daily >> "$LOG_FILE" 2>&1

echo "=== Completed: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
