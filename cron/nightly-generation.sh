#!/bin/bash
# Nightly Generation Script
#
# Generates a single dreamweaving session from the static topic list.
# Scheduled to run daily at 12am MST (7am UTC).
#
# CRON ENTRY (DISABLED - DO NOT ENABLE UNTIL TESTED):
# 0 4 * * * /home/rsalars/Projects/dreamweaving/cron/nightly-generation.sh
#
# Manual test:
#   ./cron/nightly-generation.sh --dry-run
#   ./cron/nightly-generation.sh --count 1
#

set -e

# Configuration
PROJECT_ROOT="/home/rsalars/Projects/dreamweaving"
VENV_PATH="${PROJECT_ROOT}/venv"
LOG_DIR="${PROJECT_ROOT}/data/logs/automation"
LOG_FILE="${LOG_DIR}/nightly-generation-$(date +%Y%m%d).log"

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
COUNT=1
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --count)
            COUNT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log "=========================================="
log "Starting nightly generation"
log "=========================================="

# Select topic from static list (if available)
TOPIC_FILE="${PROJECT_ROOT}/config/dreamweaving_topics.txt"
TOPIC_ARG=()
if [ -s "${TOPIC_FILE}" ]; then
    SELECTED_TOPIC=$(shuf -n 1 "${TOPIC_FILE}" | tr -d '\r')
    log "Selected topic: ${SELECTED_TOPIC}"
    TOPIC_ARG=(--topic "${SELECTED_TOPIC}")
else
    log "Topic file missing or empty: ${TOPIC_FILE}"
fi

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

# Run nightly builder
log "Running nightly builder..."
CMD=(python3 -m scripts.automation.nightly_builder --count "${COUNT}")
if [ -n "${DRY_RUN}" ]; then
    CMD+=("--dry-run")
fi
CMD+=("${TOPIC_ARG[@]}")

"${CMD[@]}" 2>&1 | tee -a "${LOG_FILE}"

RESULT=$?

if [ $RESULT -eq 0 ]; then
    log "Nightly generation completed successfully"
else
    log "Nightly generation failed with exit code: $RESULT"
fi

log "=========================================="
log "Nightly generation finished"
log "=========================================="

exit $RESULT
