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
#   12:00 AM - Daily single-session generation (no YouTube upload)

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

# Daily generation: 12am MST = 7am UTC
# Generates one dreamweaving session from the static topic list (no YouTube upload)
0 7 * * * ${CRON_DIR}/nightly-generation.sh >> ${LOG_DIR}/cron.log 2>&1
# === END DREAMWEAVING ===

# Reset cron timezone to server default after dreamweaving block
CRON_TZ=America/Denver # dreamweaving timezone reset
"

    # Install new crontab
    echo "${NEW_CRON}" | crontab -

    echo -e "${GREEN}Cron jobs installed successfully!${NC}"
    echo ""
    echo "Schedule (MST timezone):"
    echo "  12:00 AM - Daily single-session generation (no YouTube upload)"
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
