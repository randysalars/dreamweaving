#!/bin/bash
#########################################################
# Start Stable Diffusion WebUI Server for Dreamweaver
#########################################################
#
# This script starts the AUTOMATIC1111 Stable Diffusion WebUI
# in CPU-only mode with the API enabled.
#
# Usage:
#   ./scripts/utilities/start_sd_server.sh
#
# The server will be available at:
#   - Web UI: http://127.0.0.1:7860
#   - API: http://127.0.0.1:7860/sdapi/v1/txt2img
#
# To generate images programmatically:
#   python3 scripts/core/sd_api_client.py --generate "your prompt" --output output.png
#
# To generate Neural Network Navigator scenes:
#   python3 scripts/core/generate_sd_scenes.py sessions/neural-network-navigator/ --upscale
#

SD_WEBUI_DIR="$HOME/sd-webui"

if [ ! -d "$SD_WEBUI_DIR" ]; then
    echo "Error: SD WebUI not found at $SD_WEBUI_DIR"
    echo "Please run the installation first."
    exit 1
fi

# Check if model exists
MODEL_FILE="$SD_WEBUI_DIR/models/Stable-diffusion/sd-v1-5-pruned-emaonly.safetensors"
if [ ! -f "$MODEL_FILE" ]; then
    echo "Error: SD model not found at $MODEL_FILE"
    echo "Please download the model first."
    exit 1
fi

echo "=========================================="
echo "Starting Stable Diffusion WebUI (CPU Mode)"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  - Mode: CPU only (no CUDA)"
echo "  - Model: sd-v1-5-pruned-emaonly.safetensors"
echo "  - API: Enabled at http://127.0.0.1:7860"
echo ""
echo "Note: First startup will take several minutes to"
echo "install dependencies and load the model."
echo ""
echo "Press Ctrl+C to stop the server."
echo "=========================================="
echo ""

cd "$SD_WEBUI_DIR"
./webui.sh
