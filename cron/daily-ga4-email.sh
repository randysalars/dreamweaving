#!/bin/bash
# Daily GA4 Email Report
#
# Suggested cron (send at ~7:15 in desired TZ):
# 15 7 * * * /path/to/dreamweaving/cron/daily-ga4-email.sh
#
# Prereqs:
# - GA_PROPERTY_ID, GOOGLE_APPLICATION_CREDENTIALS (or ADC)
# - RESEND_API_KEY
# - DAILY_ANALYTICS_TO (default: randy@salrs.nert)

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/data/logs/automation"
LOG_FILE="$LOG_DIR/daily-ga4-email-$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "=== Daily GA4 Email: $(date) ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"
source venv/bin/activate

python -m scripts.analytics.daily_ga4_email >> "$LOG_FILE" 2>&1

echo "=== Completed: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

