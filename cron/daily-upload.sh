#!/bin/bash
# Daily Upload Script
#
# Uploads one long-form video to YouTube at optimal time.
# Time is determined by analytics_optimizer.
#
# CRON ENTRY (DISABLED - DO NOT ENABLE UNTIL TESTED):
# This should be scheduled at the optimal upload time from analytics.
# Default fallback: 12:00 MST (19:00 UTC)
# 0 19 * * * /home/rsalars/Projects/dreamweaving/cron/daily-upload.sh
#
# Manual test:
#   ./cron/daily-upload.sh --dry-run
#   ./cron/daily-upload.sh --privacy unlisted
#

set -e

# Configuration
PROJECT_ROOT="/home/rsalars/Projects/dreamweaving"
VENV_PATH="${PROJECT_ROOT}/venv"
LOG_DIR="${PROJECT_ROOT}/data/logs/automation"
LOG_FILE="${LOG_DIR}/daily-upload-$(date +%Y%m%d).log"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Error handler
error_handler() {
    log "ERROR: Script failed on line $1"
    exit 1
}
trap 'error_handler $LINENO' ERR

# Parse arguments
DRY_RUN=""
PRIVACY=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --privacy)
            PRIVACY="--privacy $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log "=========================================="
log "Starting daily upload"
log "=========================================="

# Activate virtual environment
log "Activating virtual environment..."
source "${VENV_PATH}/bin/activate"

# Change to project directory
cd "${PROJECT_ROOT}"

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    log "Loading environment variables..."
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Run upload scheduler
log "Running upload scheduler..."
python3 -m scripts.automation.upload_scheduler ${DRY_RUN} ${PRIVACY} 2>&1 | tee -a "${LOG_FILE}"

RESULT=$?

if [ $RESULT -eq 0 ]; then
    log "Daily upload completed successfully"

    # Run archive manager if upload succeeded and not dry-run
    if [ -z "$DRY_RUN" ]; then
        log "Running archive manager..."
        python3 -m scripts.automation.archive_manager 2>&1 | tee -a "${LOG_FILE}"
    fi
else
    log "Daily upload failed with exit code: $RESULT"
fi

log "=========================================="
log "Daily upload finished"
log "=========================================="

exit $RESULT
