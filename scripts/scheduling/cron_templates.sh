#!/bin/bash
# Cron Templates for Dreamweaving Automation
#
# These templates can be added to your crontab for scheduled execution.
# Edit with: crontab -e
#
# IMPORTANT: Update DREAMWEAVING_PATH to your actual project path

DREAMWEAVING_PATH="/home/rsalars/Projects/dreamweaving"

# ============================================================
# CRON TEMPLATE EXAMPLES
# ============================================================

# -----------------------------
# Daily Tasks (Run at night)
# -----------------------------

# Process all incomplete sessions at 2 AM daily
# 0 2 * * * cd $DREAMWEAVING_PATH && source venv/bin/activate && python3 scripts/ai/batch_processor.py --all --status incomplete --audio-only --quiet >> logs/batch_$(date +\%Y\%m\%d).log 2>&1

# Run code review weekly on Sunday at 3 AM
# 0 3 * * 0 cd $DREAMWEAVING_PATH && source venv/bin/activate && python3 scripts/ai/learning/code_reviewer.py --update-knowledge >> logs/code_review.log 2>&1

# -----------------------------
# Weekly Tasks
# -----------------------------

# Generate analytics dashboard every Monday at 6 AM
# 0 6 * * 1 cd $DREAMWEAVING_PATH && source venv/bin/activate && python3 scripts/ai/dashboard_generator.py >> logs/dashboard.log 2>&1

# Archive old lessons every Sunday at 4 AM
# 0 4 * * 0 cd $DREAMWEAVING_PATH && source venv/bin/activate && python3 scripts/ai/learning/lessons_manager.py cleanup --days 180 >> logs/cleanup.log 2>&1

# ============================================================
# HELPER SCRIPTS
# ============================================================

cat << 'SCRIPT_DAILY' > /dev/null
#!/bin/bash
# daily_processing.sh - Run daily session processing
set -e
cd "$DREAMWEAVING_PATH"
source venv/bin/activate

echo "=== Daily Processing Started: $(date) ==="

# Process incomplete sessions
python3 scripts/ai/batch_processor.py --all --status incomplete --headless --quiet

# Generate quality reports
for session in sessions/*/; do
    if [ -f "${session}manifest.yaml" ]; then
        python3 scripts/ai/quality_scorer.py "$session" --json > "${session}working_files/quality_report.json" 2>/dev/null || true
    fi
done

echo "=== Daily Processing Complete: $(date) ==="
SCRIPT_DAILY

cat << 'SCRIPT_WEEKLY' > /dev/null
#!/bin/bash
# weekly_maintenance.sh - Run weekly maintenance tasks
set -e
cd "$DREAMWEAVING_PATH"
source venv/bin/activate

echo "=== Weekly Maintenance Started: $(date) ==="

# Code review
python3 scripts/ai/learning/code_reviewer.py --update-knowledge

# Archive old lessons
python3 scripts/ai/learning/lessons_manager.py cleanup --days 180

# Generate dashboard
python3 scripts/ai/dashboard_generator.py

# Show lessons summary
python3 scripts/ai/learning/lessons_manager.py stats

echo "=== Weekly Maintenance Complete: $(date) ==="
SCRIPT_WEEKLY

# ============================================================
# SETUP INSTRUCTIONS
# ============================================================

echo "
DREAMWEAVING CRON SETUP INSTRUCTIONS
=====================================

1. Create the logs directory:
   mkdir -p $DREAMWEAVING_PATH/logs

2. Create helper scripts:
   mkdir -p $DREAMWEAVING_PATH/scripts/scheduling

3. Edit your crontab:
   crontab -e

4. Add desired cron entries (uncomment lines above)

5. Verify cron is running:
   systemctl status cron

EXAMPLE: Process all sessions at 2 AM:
0 2 * * * cd $DREAMWEAVING_PATH && source venv/bin/activate && python3 scripts/ai/batch_processor.py --all --audio-only --quiet >> logs/batch_\$(date +\\%Y\\%m\\%d).log 2>&1

TESTING: Run a one-time test:
cd $DREAMWEAVING_PATH && source venv/bin/activate && python3 scripts/ai/batch_processor.py --all --dry-run
"
