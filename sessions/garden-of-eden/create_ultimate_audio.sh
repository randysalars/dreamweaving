#!/bin/bash
#
# ULTIMATE Garden of Eden Audio Production
# Full implementation of ALL consciousness-alteration techniques
#
# Usage:
#   ./create_ultimate_audio.sh [voice_name]
#

set -e  # Exit on error

echo "======================================================================"
echo "   🌌 ULTIMATE Garden of Eden Audio Production 🌌"
echo "   Maximum Consciousness-Alteration Configuration"
echo "======================================================================"
echo ""
echo "Technologies Implemented:"
echo "  ✓ Theta-Gamma Phase-Amplitude Coupling"
echo "  ✓ 3D Spatial Audio Spatialization"
echo "  ✓ Fractal White/Pink/Brown Noise Overlays"
echo "  ✓ Breath-Synchronized Frequency Glissandos"
echo "  ✓ Dynamic Chakra Harmonic Layering"
echo "  ✓ Polyvagal Somatic Triggers (humming, eye movement)"
echo "  ✓ Hypnagogic Boundary Expansion"
echo "  ✓ Multisensory Entrainment (tactile, thermal, proprioceptive)"
echo "  ✓ Temporal Distortion Language"
echo "  ✓ DMN-Suppression Non-Dual Paradoxes"
echo "  ✓ Synesthetic Cross-Modal Perception"
echo "  ✓ Dream Incubation Lucid Triggers"
echo ""
echo "======================================================================"
echo ""

# Configuration
VOICE_NAME="${1:-en-US-Neural2-D}"
SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SESSION_DIR/output/ultimate"
SCRIPT_SSML="$SESSION_DIR/script_v2_ultimate.ssml"
PROJECT_ROOT="$(cd "$SESSION_DIR/../.." && pwd)"

# Activate virtual environment
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📋 Configuration:"
echo "   Voice: $VOICE_NAME"
echo "   Script: script_v2_ultimate.ssml"
echo "   Output: $OUTPUT_DIR"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Generating voice audio from ULTIMATE script"
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
echo "STEP 2: Generating ULTIMATE multi-dimensional frequency track"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SESSION_DIR"
python3 generate_ultimate_frequencies.py

mv ultimate_frequencies.wav "$OUTPUT_DIR/"

echo ""
echo "✅ Ultimate frequencies generated: $OUTPUT_DIR/ultimate_frequencies.wav"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Mixing voice + ultimate frequencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 mix_audio.py \
    "$OUTPUT_DIR/voice_only.mp3" \
    "$OUTPUT_DIR/ultimate_frequencies.wav" \
    "$OUTPUT_DIR/garden_of_eden_ULTIMATE.mp3"

echo ""
echo "======================================================================"
echo "🌌 ✨ ULTIMATE VERSION COMPLETE! ✨ 🌌"
echo "======================================================================"
echo ""
echo "📁 Final Files:"
echo "   🎙️  Voice: $OUTPUT_DIR/voice_only.mp3"
echo "   🎵  Frequencies: $OUTPUT_DIR/ultimate_frequencies.wav"
echo "   ⭐ ULTIMATE: $OUTPUT_DIR/garden_of_eden_ULTIMATE.mp3"
echo ""
echo "🧬 Consciousness Alteration Technologies:"
echo ""
echo "   SCRIPT ENHANCEMENTS:"
echo "   • Polyvagal triggers (humming, eye movement)"
echo "   • Hypnagogic boundary expansion"
echo "   • Temporal distortion (time stretching)"
echo "   • Multisensory entrainment (tactile, thermal, proprioceptive)"
echo "   • Synesthetic cross-modal perception"
echo "   • Theta-gamma coupling language"
echo "   • Dream incubation + lucid triggers"
echo ""
echo "   AUDIO TECHNOLOGIES:"
echo "   • Theta-Gamma Phase-Amplitude Coupling"
echo "   • 3D Spatial Audio Spatialization"
echo "   • Fractal Noise Overlays (pink/brown/white)"
echo "   • Breath-Synchronized Frequency Glissandos"
echo "   • Dynamic Chakra Harmonic Layering"
echo "   • Multi-layer Binaural + Isochronic"
echo ""
echo "🎯 Expected Effects:"
echo "   • Deep hypnagogic trance states"
echo "   • Synesthetic sensory blending"
echo "   • Time dilation (50min may feel like hours)"
echo "   • Proprioceptive illusions (floating, expansion)"
echo "   • Mystical unity experiences (gamma bursts)"
echo "   • Enhanced dream recall + lucid dreams"
echo "   • DMN suppression (ego dissolution)"
echo ""
echo "⚠️  CRITICAL REQUIREMENTS:"
echo "   • MUST use high-quality headphones"
echo "   • Dark, quiet, undisturbed environment"
echo "   • Lying down or deeply reclined"
echo "   • Eyes closed throughout"
echo "   • No multitasking or distractions"
echo ""
echo "🌿 The ultimate gateway awaits. 🌿"
echo ""
