#!/bin/bash
# Install Cron Jobs for Daily Workflow
#
# This script installs the cron jobs for automated video generation and uploads.
#
# Usage:
#   ./scripts/utilities/install_cron_jobs.sh         # Install cron jobs
#   ./scripts/utilities/install_cron_jobs.sh --show  # Show current crontab
#   ./scripts/utilities/install_cron_jobs.sh --remove # Remove dreamweaving cron jobs
#
# Schedule (MST timezone):
#   9:00 PM - Nightly generation (5 sessions)
#   8:00 AM - Daily shorts upload
#   12:00 PM - Daily long-form upload
#   3:00 PM - Daily analytics collection
#   3:00 AM Sunday - Weekly learning

set -e

PROJECT_ROOT="/home/rsalars/Projects/dreamweaving"
CRON_DIR="${PROJECT_ROOT}/cron"
LOG_DIR="${PROJECT_ROOT}/data/logs/automation"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

show_current() {
    echo -e "${YELLOW}Current crontab:${NC}"
    crontab -l 2>/dev/null || echo "(empty)"
}

remove_cron_jobs() {
    echo -e "${YELLOW}Removing dreamweaving cron jobs...${NC}"
    crontab -l 2>/dev/null | grep -v "dreamweaving" | crontab - || true
    echo -e "${GREEN}Dreamweaving cron jobs removed.${NC}"
    show_current
}

install_cron_jobs() {
    echo -e "${YELLOW}Installing dreamweaving cron jobs...${NC}"

    # Read current crontab (if any)
    CURRENT_CRON=$(crontab -l 2>/dev/null || true)

    # Remove any existing dreamweaving entries (case-insensitive)
    FILTERED_CRON=$(echo "${CURRENT_CRON}" | grep -vi "dreamweaving" || true)

    # Define new cron entries
    # All times are UTC (server time)
    # MST = UTC-7 (standard) or UTC-6 (daylight savings)
    # Using UTC times for consistency

    NEW_CRON="${FILTERED_CRON}

# === DREAMWEAVING AUTOMATED WORKFLOW ===
# Installed: $(date '+%Y-%m-%d %H:%M:%S')
# All times are UTC
CRON_TZ=UTC # dreamweaving timezone anchor

# Nightly generation: 9pm MST = 4am UTC next day
# Generates 5 dreamweaving sessions from Notion topics
0 4 * * * ${CRON_DIR}/nightly-generation.sh >> ${LOG_DIR}/cron.log 2>&1

# Daily shorts: 8am MST = 3pm UTC
# Creates and uploads a YouTube Short with website CTA
0 15 * * * ${CRON_DIR}/daily-shorts.sh >> ${LOG_DIR}/cron.log 2>&1

# Daily upload: 12pm MST = 7pm UTC
# Uploads one long-form video to YouTube
0 19 * * * ${CRON_DIR}/daily-upload.sh >> ${LOG_DIR}/cron.log 2>&1

# Daily analytics: 3pm MST = 10pm UTC
# Fetches YouTube analytics for videos 48+ hours old
0 22 * * * ${CRON_DIR}/daily-analytics.sh >> ${LOG_DIR}/cron.log 2>&1

# Weekly learning: 3am MST Sunday = 10am UTC Sunday
# Deep analysis and lesson extraction
0 10 * * 0 ${CRON_DIR}/weekly-learning.sh >> ${LOG_DIR}/cron.log 2>&1
# === END DREAMWEAVING ===

# Reset cron timezone to server default after dreamweaving block
CRON_TZ=America/Denver # dreamweaving timezone reset
"

    # Install new crontab
    echo "${NEW_CRON}" | crontab -

    echo -e "${GREEN}Cron jobs installed successfully!${NC}"
    echo ""
    echo "Schedule (MST timezone):"
    echo "  9:00 PM  - Nightly generation (5 sessions)"
    echo "  8:00 AM  - Daily shorts upload"
    echo "  12:00 PM - Daily long-form upload"
    echo "  3:00 PM  - Daily analytics collection"
    echo "  3:00 AM Sunday - Weekly learning"
    echo ""
    echo "Logs: ${LOG_DIR}/cron.log"
    echo ""

    show_current
}

# Parse arguments
case "${1:-}" in
    --show)
        show_current
        ;;
    --remove)
        remove_cron_jobs
        ;;
    --help|-h)
        echo "Usage: $0 [--show|--remove|--help]"
        echo ""
        echo "Options:"
        echo "  (none)   Install cron jobs"
        echo "  --show   Show current crontab"
        echo "  --remove Remove dreamweaving cron jobs"
        echo "  --help   Show this help"
        ;;
    *)
        install_cron_jobs
        ;;
esac
