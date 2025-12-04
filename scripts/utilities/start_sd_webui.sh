#!/bin/bash
# Start Stable Diffusion WebUI with API enabled for MCP integration
# Usage: ./start_sd_webui.sh [--background]

SD_WEBUI_PATH="${HOME}/sd-webui"
LOG_FILE="${HOME}/.sd-webui.log"

echo "Starting Stable Diffusion WebUI with API enabled..."

if [ ! -d "$SD_WEBUI_PATH" ]; then
    echo "Error: SD WebUI not found at $SD_WEBUI_PATH"
    exit 1
fi

cd "$SD_WEBUI_PATH"

# Check if already running
if curl -s http://127.0.0.1:7860/sdapi/v1/sd-models > /dev/null 2>&1; then
    echo "SD WebUI is already running at http://127.0.0.1:7860"
    exit 0
fi

if [ "$1" == "--background" ]; then
    echo "Starting in background mode..."
    echo "Logs will be written to $LOG_FILE"
    nohup ./webui.sh --api --listen > "$LOG_FILE" 2>&1 &
    echo "PID: $!"
    echo ""
    echo "Waiting for WebUI to start..."
    for i in {1..60}; do
        if curl -s http://127.0.0.1:7860/sdapi/v1/sd-models > /dev/null 2>&1; then
            echo "SD WebUI is ready at http://127.0.0.1:7860"
            exit 0
        fi
        sleep 2
        echo -n "."
    done
    echo ""
    echo "Timeout waiting for WebUI. Check logs at $LOG_FILE"
else
    echo "Starting in foreground mode (Ctrl+C to stop)..."
    ./webui.sh --api --listen
fi
