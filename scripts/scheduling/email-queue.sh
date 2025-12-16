#!/bin/bash
# Process salars.net email queue via API call
#
# This script calls the production email queue endpoint to process
# pending emails (gift notifications, order confirmations, etc.)
#
# Usage: ./email-queue.sh
# Cron: Runs every 5 minutes via systemd timer

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

ENDPOINT="https://www.salars.net/api/cron/email-queue"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/email_queue.log"

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Check for required token
if [ -z "${CRON_EMAIL_QUEUE_TOKEN:-}" ]; then
    log "ERROR: CRON_EMAIL_QUEUE_TOKEN not set in environment"
    exit 1
fi

log "Processing email queue..."

# Call the API endpoint with Bearer token auth
HTTP_CODE=$(curl -s -o /tmp/email_queue_response.json -w "%{http_code}" \
    -H "Authorization: Bearer $CRON_EMAIL_QUEUE_TOKEN" \
    -H "Content-Type: application/json" \
    "$ENDPOINT" 2>&1) || {
    log "ERROR: curl failed with exit code $?"
    exit 1
}

RESPONSE=$(cat /tmp/email_queue_response.json 2>/dev/null || echo "No response body")

if [ "$HTTP_CODE" = "200" ]; then
    log "SUCCESS (HTTP $HTTP_CODE): $RESPONSE"
    exit 0
elif [ "$HTTP_CODE" = "401" ]; then
    log "ERROR (HTTP $HTTP_CODE): Unauthorized - check CRON_EMAIL_QUEUE_TOKEN"
    exit 1
else
    log "ERROR (HTTP $HTTP_CODE): $RESPONSE"
    exit 1
fi
