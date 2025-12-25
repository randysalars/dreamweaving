#!/bin/bash
# System-wide cleanup for dreamweaving workstation
# Run weekly via cron: 0 2 * * 0
#
# This script cleans:
# - Pip cache
# - Puppeteer/browser caches
# - NPM cache
# - Docker unused resources
# - Trash
# - Python __pycache__ directories
# - Journalctl logs (keeps 7 days)

set -e

LOG_DIR="/home/rsalars/Projects/dreamweaving/data/logs/automation"
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=== System Cleanup Started ==="
log "Initial disk usage:"
df -h / | tail -1

# Safe cache cleanups
log "Clearing pip cache..."
rm -rf ~/.cache/pip/* 2>/dev/null || true

log "Clearing puppeteer cache..."
rm -rf ~/.cache/puppeteer/* 2>/dev/null || true

log "Clearing uv cache..."
rm -rf ~/.cache/uv/* 2>/dev/null || true

log "Clearing npm cache..."
npm cache clean --force 2>/dev/null || true

# Docker cleanup (safe - only unused)
log "Pruning Docker unused resources..."
docker system prune -f --volumes 2>/dev/null || true

# Empty trash
log "Emptying trash..."
rm -rf ~/.local/share/Trash/* 2>/dev/null || true

# Python cache cleanup
log "Cleaning Python caches..."
find ~/Projects -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find ~/Projects -name "*.pyc" -delete 2>/dev/null || true
find ~/Projects -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Journalctl cleanup (keep 7 days) - requires sudo
log "Pruning journalctl logs (7 days retention)..."
sudo journalctl --vacuum-time=7d 2>/dev/null || log "Skipped journalctl (needs sudo)"

# Report
log "=== System Cleanup Complete ==="
log "Final disk usage:"
df -h / | tail -1
