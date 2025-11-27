#!/bin/bash

# Garden of Eden - NATURAL Voice Audio Production Script
# Generates audio with more human-sounding prosody
# All advanced consciousness-alteration technologies with natural voice delivery

# Color codes for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VOICE="${1:-en-US-Neural2-D}"  # Default voice if not specified
SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SESSION_DIR/output/natural"
SCRIPT_FILE="$SESSION_DIR/script_v3_natural.ssml"

# Activate virtual environment if it exists
PROJECT_ROOT="$(cd "$SESSION_DIR/../.." && pwd)"
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

echo "======================================================================"
echo "   🌿 NATURAL Garden of Eden Audio Production 🌿"
echo "   Human-Sounding Voice + Ultimate Consciousness Technologies"
echo "======================================================================"
echo ""
echo "Technologies Implemented:"
echo "  ✓ Natural Voice Prosody (conversational flow)"
echo "  ✓ Theta-Gamma Phase-Amplitude Coupling"
echo "  ✓ 3D Spatial Audio Spatialization"
echo "  ✓ Fractal White/Pink/Brown Noise Overlays"
echo "  ✓ Breath-Synchronized Frequency Glissandos"
echo "  ✓ Dynamic Chakra Harmonic Layering"
echo "  ✓ Polyvagal Somatic Triggers"
echo "  ✓ Hypnagogic Boundary Expansion"
echo "  ✓ Multisensory Entrainment"
echo "  ✓ Temporal Distortion Language"
echo "  ✓ DMN-Suppression Non-Dual Paradoxes"
echo "  ✓ Synesthetic Cross-Modal Perception"
echo "  ✓ Dream Incubation Lucid Triggers"
echo ""
echo "======================================================================"
echo ""

echo -e "${CYAN}📋 Configuration:${NC}"
echo "   Voice: $VOICE"
echo "   Script: script_v3_natural.ssml"
echo "   Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: Generate voice audio
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Generating voice audio from NATURAL script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 "$PROJECT_ROOT/scripts/core/generate_audio_chunked.py" \
    "$SCRIPT_FILE" \
    "$OUTPUT_DIR/voice_only.mp3" \
    "$VOICE"

if [ $? -ne 0 ]; then
    echo "❌ Error generating voice audio"
    exit 1
fi

echo ""
echo "✅ Voice audio generated: $OUTPUT_DIR/voice_only.mp3"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Generate ultimate frequencies
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Generating ULTIMATE multi-dimensional frequency track"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 "$SESSION_DIR/generate_ultimate_frequencies.py" \
    "$OUTPUT_DIR/natural_frequencies.wav"

if [ $? -ne 0 ]; then
    echo "❌ Error generating frequency track"
    exit 1
fi

echo ""
echo "✅ Ultimate frequencies generated: $OUTPUT_DIR/natural_frequencies.wav"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: Mix voice + frequencies
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Mixing voice + ultimate frequencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 "$SESSION_DIR/mix_audio.py" \
    "$OUTPUT_DIR/voice_only.mp3" \
    "$OUTPUT_DIR/natural_frequencies.wav" \
    "$OUTPUT_DIR/garden_of_eden_NATURAL.mp3"

if [ $? -ne 0 ]; then
    echo "❌ Error mixing audio"
    exit 1
fi

echo ""
echo "======================================================================"
echo "🌿 ✨ NATURAL VERSION COMPLETE! ✨ 🌿"
echo "======================================================================"
echo ""
echo -e "${GREEN}📁 Final Files:${NC}"
echo "   🎙️  Voice: $OUTPUT_DIR/voice_only.mp3"
echo "   🎵  Frequencies: $OUTPUT_DIR/natural_frequencies.wav"
echo "   ⭐ NATURAL: $OUTPUT_DIR/garden_of_eden_NATURAL.mp3"
echo ""
echo -e "${CYAN}🧬 Consciousness Alteration Technologies:${NC}"
echo ""
echo "   NATURAL VOICE:"
echo "   • Reduced pitch (-1st instead of -3st)"
echo "   • Natural rate (0.92 instead of x-slow)"
echo "   • Flowing sentences (70% fewer breaks)"
echo "   • Conversational connectors"
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
echo -e "${YELLOW}🎯 Expected Effects:${NC}"
echo "   • Deep hypnagogic trance states"
echo "   • Synesthetic sensory blending"
echo "   • Time dilation"
echo "   • Proprioceptive illusions (floating, expansion)"
echo "   • Mystical unity experiences (gamma bursts)"
echo "   • Enhanced dream recall + lucid dreams"
echo "   • DMN suppression (ego dissolution)"
echo "   • MORE NATURAL HYPNOTIC VOICE"
echo ""
echo -e "${YELLOW}⚠️  CRITICAL REQUIREMENTS:${NC}"
echo "   • MUST use high-quality headphones"
echo "   • Dark, quiet, undisturbed environment"
echo "   • Lying down or deeply reclined"
echo "   • Eyes closed throughout"
echo "   • No multitasking or distractions"
echo ""
echo "🌿 The natural gateway awaits. 🌿"
