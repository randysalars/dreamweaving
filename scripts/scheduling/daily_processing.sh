#!/bin/bash
# daily_processing.sh - Run daily session processing
#
# This script processes incomplete sessions and generates quality reports.
# Can be run manually or via cron.
#
# Usage:
#   ./scripts/scheduling/daily_processing.sh
#   ./scripts/scheduling/daily_processing.sh --dry-run

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse arguments
DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Setup logging
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/daily_$TIMESTAMP.log"

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

log "=== Daily Processing Started ==="
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

# Count sessions
TOTAL_SESSIONS=$(find sessions -maxdepth 1 -type d | wc -l)
INCOMPLETE=$(find sessions -maxdepth 1 -type d -exec test ! -f {}/output/final.mp3 \; -print 2>/dev/null | wc -l || echo 0)

log "Total sessions: $((TOTAL_SESSIONS - 1))"
log "Incomplete sessions: $INCOMPLETE"

if [ "$DRY_RUN" = true ]; then
    log "DRY RUN - Would process incomplete sessions"
    python3 scripts/ai/batch_processor.py --all --status incomplete --dry-run
    exit 0
fi

# Process incomplete sessions
if [ "$INCOMPLETE" -gt 0 ]; then
    log "Processing incomplete sessions..."

    if [ "$VERBOSE" = true ]; then
        python3 scripts/ai/batch_processor.py --all --status incomplete --audio-only 2>&1 | tee -a "$LOG_FILE"
    else
        python3 scripts/ai/batch_processor.py --all --status incomplete --audio-only --quiet >> "$LOG_FILE" 2>&1
    fi

    log "Batch processing complete"
else
    log "No incomplete sessions to process"
fi

# Generate quality reports for all sessions
log "Generating quality reports..."
for session_dir in sessions/*/; do
    if [ -f "${session_dir}manifest.yaml" ]; then
        session_name=$(basename "$session_dir")

        # Generate quality report
        python3 scripts/ai/quality_scorer.py "$session_dir" --json > "${session_dir}working_files/quality_report.json" 2>/dev/null || true

        if [ "$VERBOSE" = true ]; then
            log "  Quality report: $session_name"
        fi
    fi
done

log "=== Daily Processing Complete ==="
log "Log saved to: $LOG_FILE"

# Summary
COMPLETED=$(grep -c "completed" "$LOG_FILE" 2>/dev/null || echo 0)
FAILED=$(grep -c "failed\|error" "$LOG_FILE" 2>/dev/null || echo 0)

echo ""
echo "Summary:"
echo "  Completed: $COMPLETED"
echo "  Failed: $FAILED"
echo "  Log: $LOG_FILE"
