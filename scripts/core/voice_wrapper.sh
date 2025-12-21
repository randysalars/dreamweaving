#!/bin/bash
# Voice Generation Wrapper
# Tries multiple TTS providers in order of preference
# Usage: voice_wrapper.sh <ssml_file> <output_dir>

set -e

SSML_FILE="$1"
OUTPUT_DIR="$2"

if [ -z "$SSML_FILE" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <ssml_file> <output_dir>"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=================================="
echo "  Voice Generation Wrapper"
echo "=================================="
echo

# Try providers in order
PROVIDERS=(
    "google:$PROJECT_ROOT/scripts/core/generate_voice.py"
    "coqui:$PROJECT_ROOT/venv_coqui/bin/python:$PROJECT_ROOT/scripts/core/generate_voice_coqui_simple.py"
)

for provider_config in "${PROVIDERS[@]}"; do
    IFS=':' read -r name interpreter script <<< "$provider_config"
    
    echo "Trying provider: $name"
    
    if [ "$name" == "google" ]; then
        # Try Google Cloud TTS
        if python "$script" "$SSML_FILE" "$OUTPUT_DIR" 2>&1 | grep -q "BILLING_DISABLED\|403"; then
            echo "  ❌ Google TTS: Billing disabled"
            continue
        else
            echo "  ✅ Google TTS: Success"
            exit 0
        fi
    elif [ "$name" == "coqui" ]; then
        # Try Coqui TTS
        if [ ! -f "$interpreter" ]; then
            echo "  ⚠️  Coqui not installed (run: python3.11 -m venv venv_coqui && venv_coqui/bin/pip install TTS pydub)"
            continue
        fi
        
        echo "  Using Coqui TTS (this may take 5-10 minutes)..."
        if "$interpreter" "$script" "$SSML_FILE" "$OUTPUT_DIR"; then
            echo "  ✅ Coqui TTS: Success"
            exit 0
        else
            echo "  ❌ Coqui TTS: Failed"
            continue
        fi
    fi
done

echo
echo "❌ All voice generation providers failed"
echo
echo "Solutions:"
echo "  1. Enable Google Cloud TTS billing: https://console.developers.google.com/billing"
echo "  2. Or use Coqui TTS (free, slower):"
echo "     cd $PROJECT_ROOT"
echo "     python3.11 -m venv venv_coqui"
echo "     venv_coqui/bin/pip install TTS pydub"
exit 1
