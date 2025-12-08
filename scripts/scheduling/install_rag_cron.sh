#!/bin/bash
# =============================================================================
# Install RAG auto-sync as a systemd timer and/or file watcher
# Part of Phase 8: Automatic RAG Indexing System
# =============================================================================
#
# Usage:
#   ./scripts/scheduling/install_rag_cron.sh          # Install timer only
#   ./scripts/scheduling/install_rag_cron.sh --all    # Install timer + watcher
#   ./scripts/scheduling/install_rag_cron.sh --watcher # Install watcher only
#   ./scripts/scheduling/install_rag_cron.sh --remove # Remove all
#   ./scripts/scheduling/install_rag_cron.sh --status # Check status
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project directory
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Dreamweaving RAG Auto-Sync Setup${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "Project directory: $PROJECT_DIR"
echo ""

# Check if running as root for systemd operations
check_sudo() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}Note: This script requires sudo for systemd operations${NC}"
        return 1
    fi
    return 0
}

# Show timer status
show_status() {
    echo -e "${GREEN}Timer Status:${NC}"
    echo "----------------------------------------"
    if systemctl list-timers | grep -q rag-sync; then
        systemctl status rag-sync.timer --no-pager 2>/dev/null || true
        echo ""
        echo -e "${GREEN}Service Status:${NC}"
        systemctl status rag-sync.service --no-pager 2>/dev/null || echo "Service not currently running"
    else
        echo -e "${YELLOW}RAG sync timer is not installed${NC}"
    fi

    echo ""
    echo -e "${GREEN}File Watcher Status:${NC}"
    echo "----------------------------------------"
    if systemctl is-active --quiet rag-watcher.service 2>/dev/null; then
        systemctl status rag-watcher.service --no-pager 2>/dev/null || true
    else
        echo -e "${YELLOW}RAG file watcher is not running${NC}"
    fi
}

# Remove timer and watcher
remove_timer() {
    echo -e "${YELLOW}Removing RAG sync timer...${NC}"

    sudo systemctl stop rag-sync.timer 2>/dev/null || true
    sudo systemctl disable rag-sync.timer 2>/dev/null || true
    sudo rm -f /etc/systemd/system/rag-sync.service
    sudo rm -f /etc/systemd/system/rag-sync.timer

    echo -e "${YELLOW}Removing RAG file watcher...${NC}"
    sudo systemctl stop rag-watcher.service 2>/dev/null || true
    sudo systemctl disable rag-watcher.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/rag-watcher.service

    sudo systemctl daemon-reload

    echo -e "${GREEN}✅ RAG sync timer and watcher removed${NC}"
}

# Install file watcher
install_watcher() {
    echo "Installing RAG file watcher service..."
    echo ""

    # Create log directory
    mkdir -p "$PROJECT_DIR/logs"

    # Check for watchdog
    if ! "$PROJECT_DIR/venv/bin/python3" -c "import watchdog" 2>/dev/null; then
        echo -e "${YELLOW}Installing watchdog dependency...${NC}"
        "$PROJECT_DIR/venv/bin/pip" install watchdog
    fi

    # Create temporary service file with correct paths
    TEMP_SERVICE=$(mktemp)
    cat "$PROJECT_DIR/scripts/scheduling/rag-watcher.service" | \
        sed "s|/home/rsalars/Projects/dreamweaving|$PROJECT_DIR|g" > "$TEMP_SERVICE"

    # Copy to systemd
    echo "Copying watcher service file..."
    sudo cp "$TEMP_SERVICE" /etc/systemd/system/rag-watcher.service
    rm "$TEMP_SERVICE"

    # Set permissions
    sudo chmod 644 /etc/systemd/system/rag-watcher.service

    # Reload systemd
    echo "Reloading systemd..."
    sudo systemctl daemon-reload

    # Enable and start watcher
    echo "Enabling watcher..."
    sudo systemctl enable rag-watcher.service
    sudo systemctl start rag-watcher.service

    echo ""
    echo -e "${GREEN}✅ RAG file watcher installed and started${NC}"
    echo ""
    echo "The watcher monitors knowledge/ and prompts/ directories"
    echo "Changes trigger automatic re-indexing after 5 second debounce"
    echo ""
    echo "Commands:"
    echo "  systemctl status rag-watcher.service    # Check watcher status"
    echo "  journalctl -u rag-watcher.service -f    # View logs"
    echo "  sudo systemctl restart rag-watcher      # Restart watcher"
    echo ""
}

# Install timer
install_timer() {
    echo "Installing RAG auto-sync timer..."
    echo ""

    # Create log directory
    mkdir -p "$PROJECT_DIR/logs"

    # Check for .env file
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        echo -e "${YELLOW}Warning: .env file not found${NC}"
        echo "Creating placeholder .env file..."
        echo "# Add NOTION_TOKEN here" > "$PROJECT_DIR/.env"
        echo "NOTION_TOKEN=" >> "$PROJECT_DIR/.env"
    fi

    # Create temporary service file with correct paths
    TEMP_SERVICE=$(mktemp)
    cat "$PROJECT_DIR/scripts/scheduling/rag-sync.service" | \
        sed "s|/home/rsalars/Projects/dreamweaving|$PROJECT_DIR|g" > "$TEMP_SERVICE"

    # Copy files to systemd
    echo "Copying service files..."
    sudo cp "$TEMP_SERVICE" /etc/systemd/system/rag-sync.service
    sudo cp "$PROJECT_DIR/scripts/scheduling/rag-sync.timer" /etc/systemd/system/
    rm "$TEMP_SERVICE"

    # Set permissions
    sudo chmod 644 /etc/systemd/system/rag-sync.service
    sudo chmod 644 /etc/systemd/system/rag-sync.timer

    # Reload systemd
    echo "Reloading systemd..."
    sudo systemctl daemon-reload

    # Enable and start timer
    echo "Enabling timer..."
    sudo systemctl enable rag-sync.timer
    sudo systemctl start rag-sync.timer

    echo ""
    echo -e "${GREEN}✅ RAG auto-sync timer installed and started${NC}"
    echo ""
    echo "Schedule: Daily at 3:00 AM"
    echo ""
    echo "Commands:"
    echo "  systemctl status rag-sync.timer    # Check timer status"
    echo "  systemctl list-timers              # See all timers"
    echo "  journalctl -u rag-sync.service -f  # View logs"
    echo "  sudo systemctl start rag-sync      # Run manually now"
    echo ""

    # Show next run time
    echo -e "${GREEN}Next scheduled run:${NC}"
    systemctl list-timers rag-sync.timer --no-pager 2>/dev/null | tail -2 || echo "Timer scheduled"
}

# Test manual run
test_run() {
    echo -e "${GREEN}Testing RAG sync (manual run)...${NC}"
    echo ""

    cd "$PROJECT_DIR"
    source venv/bin/activate 2>/dev/null || true
    python3 scripts/ai/rag_auto_sync.py --status
}

# Parse arguments
case "${1:-install}" in
    --remove|-r)
        remove_timer
        ;;
    --status|-s)
        show_status
        ;;
    --test|-t)
        test_run
        ;;
    --watcher|-w)
        install_watcher
        ;;
    --all|-a)
        install_timer
        echo ""
        install_watcher
        ;;
    install|--install|-i|"")
        install_timer
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  install, --install, -i    Install the systemd timer only (default)"
        echo "  --watcher, -w             Install the file watcher only"
        echo "  --all, -a                 Install both timer AND watcher (recommended)"
        echo "  --remove, -r              Remove timer and watcher"
        echo "  --status, -s              Show timer and watcher status"
        echo "  --test, -t                Test RAG sync manually"
        echo "  --help, -h                Show this help message"
        echo ""
        echo "Timer: Runs daily at 3 AM (catches any missed changes)"
        echo "Watcher: Real-time monitoring of knowledge/ directory"
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
