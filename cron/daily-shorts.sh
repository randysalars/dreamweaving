#!/bin/bash
# Daily Shorts Script
#
# Generates and uploads a YouTube Short from website-only content.
# Time is determined by analytics_optimizer.
#
# CRON ENTRY (DISABLED - DO NOT ENABLE UNTIL TESTED):
# This should be scheduled at the optimal shorts upload time from analytics.
# Default fallback: 8:00 MST (15:00 UTC)
# 0 15 * * * /home/rsalars/Projects/dreamweaving/cron/daily-shorts.sh
#
# Manual test:
#   ./cron/daily-shorts.sh --dry-run
#   ./cron/daily-shorts.sh --session specific-session
#

set -e

# Configuration
PROJECT_ROOT="/home/rsalars/Projects/dreamweaving"
VENV_PATH="${PROJECT_ROOT}/venv"
LOG_DIR="${PROJECT_ROOT}/data/logs/automation"
LOG_FILE="${LOG_DIR}/daily-shorts-$(date +%Y%m%d).log"

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
SESSION=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --session)
            SESSION="--session $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log "=========================================="
log "Starting daily shorts"
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

# Run shorts generator
log "Running shorts generator..."
python3 -m scripts.automation.shorts_generator ${DRY_RUN} ${SESSION} 2>&1 | tee -a "${LOG_FILE}"

RESULT=$?

if [ $RESULT -eq 0 ]; then
    log "Daily shorts completed successfully"
else
    log "Daily shorts failed with exit code: $RESULT"
fi

log "=========================================="
log "Daily shorts finished"
log "=========================================="

exit $RESULT
