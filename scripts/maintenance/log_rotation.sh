#!/bin/bash
# Rotate and compress dreamweaving logs
# Run daily via cron: 0 4 * * *
#
# This script:
# - Compresses logs older than 7 days
# - Deletes compressed logs older than 30 days
# - Reports log directory sizes

set -e

LOG_DIRS=(
    "/home/rsalars/Projects/dreamweaving/data/logs/automation"
    "/home/rsalars/Projects/dreamweaving/logs"
)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=== Log Rotation Started ==="

for log_dir in "${LOG_DIRS[@]}"; do
    if [ -d "$log_dir" ]; then
        log "Processing: $log_dir"

        # Count files before
        log_count=$(find "$log_dir" -name "*.log" -type f 2>/dev/null | wc -l)
        gz_count=$(find "$log_dir" -name "*.log.gz" -type f 2>/dev/null | wc -l)

        # Compress logs older than 7 days
        compressed=0
        while IFS= read -r -d '' file; do
            gzip "$file" 2>/dev/null && ((compressed++)) || true
        done < <(find "$log_dir" -name "*.log" -mtime +7 -type f -print0 2>/dev/null)

        # Delete compressed logs older than 30 days
        deleted=0
        while IFS= read -r -d '' file; do
            rm "$file" 2>/dev/null && ((deleted++)) || true
        done < <(find "$log_dir" -name "*.log.gz" -mtime +30 -type f -print0 2>/dev/null)

        # Report
        dir_size=$(du -sh "$log_dir" 2>/dev/null | cut -f1)
        log "  Size: $dir_size | Logs: $log_count | Archived: $gz_count | Compressed: $compressed | Deleted: $deleted"
    else
        log "Skipping (not found): $log_dir"
    fi
done

log "=== Log Rotation Complete ==="
