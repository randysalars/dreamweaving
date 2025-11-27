#!/bin/bash
#
# Enhanced Garden of Eden Audio Production
# Full workflow with consciousness-altering frequencies
#
# Usage:
#   ./create_enhanced_audio.sh [voice_name]
#
# Example:
#   ./create_enhanced_audio.sh en-US-Neural2-D
#

set -e  # Exit on error

echo "======================================================================"
echo "   Garden of Eden - ENHANCED Audio Production"
echo "   Multi-Layer Consciousness Alteration System"
echo "   Voice + Binaural + Isochronic + Gamma Bursts"
echo "======================================================================"
echo ""

# Configuration
VOICE_NAME="${1:-en-US-Neural2-D}"
SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SESSION_DIR/output/enhanced"
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Generating voice audio from enhanced SSML"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 ../../scripts/core/generate_audio_chunked.py \
    "$SCRIPT_SSML" \
    "$OUTPUT_DIR/voice_only.mp3" \
    "$VOICE_NAME"

echo ""
echo "✅ Voice audio generated: $OUTPUT_DIR/voice_only.mp3"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Generating enhanced multi-layer frequency track"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SESSION_DIR"
python3 generate_enhanced_frequencies.py

mv enhanced_frequencies.wav "$OUTPUT_DIR/"

echo ""
echo "✅ Enhanced frequencies generated: $OUTPUT_DIR/enhanced_frequencies.wav"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Mixing voice + enhanced frequencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 mix_audio.py \
    "$OUTPUT_DIR/voice_only.mp3" \
    "$OUTPUT_DIR/enhanced_frequencies.wav" \
    "$OUTPUT_DIR/garden_of_eden_ENHANCED.mp3"

echo ""
echo "======================================================================"
echo "✨ COMPLETE! Enhanced consciousness-altering audio ready!"
echo "======================================================================"
echo ""
echo "📁 Files created:"
echo "   1. $OUTPUT_DIR/voice_only.mp3 (voice only)"
echo "   2. $OUTPUT_DIR/enhanced_frequencies.wav (frequencies only)"
echo "   3. $OUTPUT_DIR/garden_of_eden_ENHANCED.mp3 (FINAL MIX) ⭐"
echo ""
echo "🧬 Enhancement Technologies:"
echo "   ✓ Binaural beats (stereo frequency difference)"
echo "   ✓ Isochronic tones (stronger than binaural)"
echo "   ✓ Frequency ramping (12→6→8→12 Hz journey)"
echo "   ✓ Gamma bursts (40 Hz for mystical unity)"
echo "   ✓ Multi-layer compositing (Theta + Delta + Gamma)"
echo "   ✓ Solfeggio frequencies (ancient healing)"
echo "   ✓ DMN suppression language (non-dual paradoxes)"
echo "   ✓ Synesthetic suggestions (sensory blending)"
echo "   ✓ Interoceptive guidance (heartbeat, energy)"
echo "   ✓ Somatic activation (chakra energy work)"
echo "   ✓ Breathwork synchronization (parasympathetic)"
echo ""
echo "🎯 Consciousness States Targeted:"
echo "   • Hypnagogic threshold (4-6 Hz Theta)"
echo "   • Synesthetic perception (cross-modal blending)"
echo "   • Default Mode Network quieting (ego dissolution)"
echo "   • Mystical unity (40 Hz gamma synchronization)"
echo "   • Energetic body activation (chakra system)"
echo ""
echo "🎧 CRITICAL: Use headphones for binaural effect!"
echo ""
echo "🌿 The gateway is open. 🌿"
echo ""
