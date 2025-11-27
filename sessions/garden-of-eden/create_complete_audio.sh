#!/bin/bash
#
# Complete Audio Production Workflow for Garden of Eden
#
# This script automates the entire audio production process:
# 1. Generate voice from SSML
# 2. Generate binaural beats
# 3. Mix voice + binaural
#
# Usage: ./create_complete_audio.sh [voice_name]
#
# Example:
#   ./create_complete_audio.sh en-US-Neural2-D
#

set -e  # Exit on error

echo "======================================================================"
echo "   Garden of Eden - Complete Audio Production"
echo "   Full workflow: SSML → Voice → Binaural → Mixed Output"
echo "======================================================================"
echo ""

# Configuration
VOICE_NAME="${1:-en-US-Neural2-D}"
SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SESSION_DIR/output"
SCRIPT_SSML="$SESSION_DIR/script.ssml"
PROJECT_ROOT="$(cd "$SESSION_DIR/../.." && pwd)"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

echo "📋 Configuration:"
echo "   Voice: $VOICE_NAME"
echo "   Session: $SESSION_DIR"
echo "   Output: $OUTPUT_DIR"
echo ""

# Step 1: Generate voice audio from SSML
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Generating voice audio from SSML"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 ../../scripts/core/generate_audio_chunked.py \
    "$SCRIPT_SSML" \
    "$OUTPUT_DIR/voice_only.mp3" \
    "$VOICE_NAME"

echo ""
echo "✅ Voice audio generated: $OUTPUT_DIR/voice_only.mp3"
echo ""

# Step 2: Generate binaural beats
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Generating binaural beat track"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SESSION_DIR"
python3 generate_binaural_beats.py << EOF
1
EOF

mv binaural_track.wav "$OUTPUT_DIR/"

echo ""
echo "✅ Binaural track generated: $OUTPUT_DIR/binaural_track.wav"
echo ""

# Step 3: Mix voice and binaural
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Mixing voice + binaural beats"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 mix_audio.py \
    "$OUTPUT_DIR/voice_only.mp3" \
    "$OUTPUT_DIR/binaural_track.wav" \
    "$OUTPUT_DIR/garden_of_eden_complete.mp3"

echo ""
echo "======================================================================"
echo "✨ COMPLETE! Final audio ready for upload"
echo "======================================================================"
echo ""
echo "📁 Files created:"
echo "   1. $OUTPUT_DIR/voice_only.mp3 (voice only)"
echo "   2. $OUTPUT_DIR/binaural_track.wav (binaural only)"
echo "   3. $OUTPUT_DIR/garden_of_eden_complete.mp3 (FINAL MIX)"
echo ""
echo "🎯 Next steps:"
echo "   • Test the final audio with headphones"
echo "   • Verify binaural effect is subtle but present"
echo "   • Upload garden_of_eden_complete.mp3 to YouTube"
echo "   • Consider creating a version without binaural for accessibility"
echo ""
echo "🌿 Walk in innocence. Choose with wisdom. Live in wholeness. 🌿"
echo ""
