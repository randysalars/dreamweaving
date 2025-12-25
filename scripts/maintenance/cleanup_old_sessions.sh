#!/bin/bash
# Auto-cleanup completed sessions older than 14 days
# Run weekly via cron: 0 3 * * 0
#
# Only cleans sessions that:
# 1. Have a youtube_package directory (completed)
# 2. Have a manifest.yaml older than DAYS_OLD days
#
# Uses the existing cleanup_session.py script with --aggressive mode

set -e

PROJECT_ROOT="/home/rsalars/Projects/dreamweaving"
DAYS_OLD=14

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=== Session Cleanup Started ==="
log "Cleaning sessions older than $DAYS_OLD days"

cd "$PROJECT_ROOT"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    log "ERROR: Virtual environment not found at $PROJECT_ROOT/venv"
    exit 1
fi

cleaned_count=0
skipped_count=0

for session_dir in sessions/*/; do
    session_name=$(basename "$session_dir")

    # Skip template and hidden directories
    if [[ "$session_name" == _* ]] || [[ "$session_name" == .* ]]; then
        continue
    fi

    # Check if session has youtube_package (completed)
    if [ -d "${session_dir}output/youtube_package" ]; then
        # Check age of manifest.yaml
        manifest="${session_dir}manifest.yaml"
        if [ -f "$manifest" ]; then
            age_days=$(( ($(date +%s) - $(stat -c %Y "$manifest")) / 86400 ))
            if [ $age_days -gt $DAYS_OLD ]; then
                log "Cleaning: $session_name (${age_days} days old)"
                python3 scripts/core/cleanup_session.py "$session_dir" --aggressive 2>&1 | grep -E "(freed|final size)" || true
                ((cleaned_count++))
            else
                log "Skipping: $session_name (${age_days} days old - too recent)"
                ((skipped_count++))
            fi
        fi
    else
        log "Skipping: $session_name (not completed - no youtube_package)"
        ((skipped_count++))
    fi
done

log "=== Session Cleanup Complete ==="
log "Sessions cleaned: $cleaned_count"
log "Sessions skipped: $skipped_count"
log "Disk usage:"
df -h / | tail -1
