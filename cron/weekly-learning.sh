#!/bin/bash
# Weekly Learning - Deep Analysis
# Analyzes all video performance, extracts patterns, updates lessons_learned.yaml
#
# Cron: 0 10 * * 0 (3am MST Sunday = 10am UTC)
# Run manually: ./cron/weekly-learning.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/data/logs/automation"
LOG_FILE="$LOG_DIR/weekly-learning-$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "=== Weekly Learning Analysis: $(date) ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"
source venv/bin/activate

python -m scripts.automation.automated_learning --weekly >> "$LOG_FILE" 2>&1

echo "=== Completed: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Notify about lessons added (if any)
LESSONS_ADDED=$(grep -o "Lessons added: [0-9]*" "$LOG_FILE" | tail -1 | grep -o "[0-9]*" || echo "0")
if [ "$LESSONS_ADDED" -gt 0 ]; then
    echo "Added $LESSONS_ADDED new lessons to knowledge base" >> "$LOG_FILE"
fi
