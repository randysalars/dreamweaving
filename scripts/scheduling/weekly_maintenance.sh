#!/bin/bash
# weekly_maintenance.sh - Run weekly maintenance tasks
#
# This script performs:
# - Code quality review
# - Lessons cleanup/archival
# - Dashboard generation
# - Statistics summary
#
# Usage:
#   ./scripts/scheduling/weekly_maintenance.sh
#   ./scripts/scheduling/weekly_maintenance.sh --skip-dashboard

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse arguments
SKIP_DASHBOARD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-dashboard)
            SKIP_DASHBOARD=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Setup logging
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/weekly_$TIMESTAMP.log"

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

log "=== Weekly Maintenance Started ==="
log "Project: $PROJECT_ROOT"

# Activate virtual environment
cd "$PROJECT_ROOT"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    log "Virtual environment activated"
else
    log "ERROR: Virtual environment not found"
    exit 1
fi

# Code review
log ""
log "--- Code Quality Review ---"
python3 scripts/ai/learning/code_reviewer.py --update-knowledge 2>&1 | tee -a "$LOG_FILE"

# Archive old lessons
log ""
log "--- Lessons Cleanup ---"
python3 scripts/ai/learning/lessons_manager.py cleanup --days 180 2>&1 | tee -a "$LOG_FILE"

# Generate dashboard (if not skipped)
if [ "$SKIP_DASHBOARD" = false ]; then
    log ""
    log "--- Generating Dashboard ---"
    if [ -f "scripts/ai/dashboard_generator.py" ]; then
        python3 scripts/ai/dashboard_generator.py 2>&1 | tee -a "$LOG_FILE"
    else
        log "Dashboard generator not found, skipping"
    fi
fi

# Show statistics
log ""
log "--- Knowledge Base Statistics ---"
python3 scripts/ai/learning/lessons_manager.py stats 2>&1 | tee -a "$LOG_FILE"

# Session statistics
log ""
log "--- Session Statistics ---"
TOTAL_SESSIONS=$(find sessions -maxdepth 1 -type d -not -name sessions | wc -l)
COMPLETE_SESSIONS=$(find sessions -maxdepth 2 -name "final.mp3" | wc -l)
YOUTUBE_PACKAGES=$(find sessions -maxdepth 3 -type d -name "youtube_package" | wc -l)

log "Total sessions: $TOTAL_SESSIONS"
log "Complete (with audio): $COMPLETE_SESSIONS"
log "YouTube packages: $YOUTUBE_PACKAGES"

# Disk usage
log ""
log "--- Disk Usage ---"
SESSIONS_SIZE=$(du -sh sessions 2>/dev/null | cut -f1)
KNOWLEDGE_SIZE=$(du -sh knowledge 2>/dev/null | cut -f1)
log "Sessions: $SESSIONS_SIZE"
log "Knowledge base: $KNOWLEDGE_SIZE"

log ""
log "=== Weekly Maintenance Complete ==="
log "Log saved to: $LOG_FILE"
