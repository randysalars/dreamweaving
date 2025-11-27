#!/bin/bash
#
# Neural Network Navigator: Enhanced Audio Production
# Complete workflow for generating enhanced meditation audio
#
# This script:
# 1. Generates enhanced voice track (removes metadata, adds pauses)
# 2. Uses existing binaural beat track (or generates if missing)
# 3. Mixes voice + binaural + sound effects
#

set -e  # Exit on error

echo "======================================================================"
echo "   NEURAL NETWORK NAVIGATOR - Enhanced Audio Production"
echo "======================================================================"
echo ""
echo "This will create an enhanced version of the audio with:"
echo "  • Removed script metadata from narration"
echo "  • Extended pauses on 'down...down...down' transitions"
echo "  • Extended pauses on 'up...up...up' transitions"
echo "  • Additional journey content for full duration"
echo "  • Immersive sound effects (bells, chimes, crystal tones)"
echo "  • Synchronized with binaural gamma burst"
echo ""

cd "$(dirname "$0")"

# Check if we're in the right directory
if [ ! -f "generate_enhanced_voice.py" ]; then
    echo "❌ Error: Must run from neural-network-navigator session directory"
    exit 1
fi

# Check for required files
echo "🔍 Checking prerequisites..."

if [ ! -f "working_files/voice_script_enhanced.ssml" ]; then
    echo "❌ Error: Enhanced SSML script not found"
    echo "   Expected: working_files/voice_script_enhanced.ssml"
    exit 1
fi
echo "  ✓ Enhanced SSML script found"

if [ ! -f "binaural_frequency_map.json" ]; then
    echo "❌ Error: Binaural frequency map not found"
    exit 1
fi
echo "  ✓ Binaural frequency map found"

# Check for Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi
echo "  ✓ Python 3 found"

# Check for required Python packages
echo ""
echo "📦 Checking Python dependencies..."
python3 -c "import google.cloud.texttospeech" 2>/dev/null || {
    echo "❌ Error: google-cloud-texttospeech not installed"
    echo "   Install with: pip install google-cloud-texttospeech"
    exit 1
}
echo "  ✓ google-cloud-texttospeech"

python3 -c "import pydub" 2>/dev/null || {
    echo "❌ Error: pydub not installed"
    echo "   Install with: pip install pydub"
    exit 1
}
echo "  ✓ pydub"

python3 -c "import numpy; import scipy" 2>/dev/null || {
    echo "❌ Error: numpy/scipy not installed"
    echo "   Install with: pip install numpy scipy"
    exit 1
}
echo "  ✓ numpy & scipy"

# Check Google Cloud authentication
echo ""
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth application-default print-access-token &> /dev/null; then
    echo "❌ Error: Google Cloud authentication not configured"
    echo "   Run: gcloud auth application-default login"
    exit 1
fi
echo "  ✓ Google Cloud authenticated"

echo ""
echo "======================================================================"
echo "STEP 1: Generate Enhanced Voice Track"
echo "======================================================================"
echo ""

if [ -f "working_files/voice_neural_navigator_enhanced.mp3" ]; then
    echo "⚠️  Enhanced voice track already exists"
    read -p "Regenerate? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  Skipping voice generation"
    else
        echo "  Regenerating voice track..."
        python3 generate_enhanced_voice.py
    fi
else
    echo "Generating enhanced voice track..."
    python3 generate_enhanced_voice.py
fi

echo ""
echo "======================================================================"
echo "STEP 2: Verify Binaural Beat Track"
echo "======================================================================"
echo ""

if [ ! -f "working_files/binaural_beats_neural_navigator.wav" ]; then
    echo "⚠️  Binaural beat track not found. Generating..."
    if [ -f "generate_binaural_neural.py" ]; then
        python3 generate_binaural_neural.py
    else
        echo "❌ Error: generate_binaural_neural.py not found"
        exit 1
    fi
else
    echo "  ✓ Binaural beat track exists"
fi

echo ""
echo "======================================================================"
echo "STEP 3: Create Enhanced Audio Mix"
echo "======================================================================"
echo ""

echo "Mixing voice + binaural + sound effects..."
python3 generate_enhanced_audio.py

echo ""
echo "======================================================================"
echo "✅ ENHANCEMENT COMPLETE!"
echo "======================================================================"
echo ""

if [ -f "working_files/neural_navigator_complete_enhanced.wav" ]; then
    FILE_SIZE=$(du -h "working_files/neural_navigator_complete_enhanced.wav" | cut -f1)
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "working_files/neural_navigator_complete_enhanced.wav" 2>/dev/null | awk '{printf "%.1f", $1/60}')

    echo "📁 Output file: working_files/neural_navigator_complete_enhanced.wav"
    echo "📊 Size: $FILE_SIZE"
    echo "⏱️  Duration: ${DURATION} minutes"
    echo ""
    echo "🎧 Listen with: ffplay working_files/neural_navigator_complete_enhanced.wav"
    echo "📤 Export to MP3: ffmpeg -i working_files/neural_navigator_complete_enhanced.wav -b:a 192k neural_navigator_enhanced.mp3"
    echo ""
    echo "✨ Enhancements included:"
    echo "   ✓ Script metadata removed from narration"
    echo "   ✓ Extended pauses on transition phrases"
    echo "   ✓ Journey extended to full duration"
    echo "   ✓ Bell chimes at Pathfinder entrance"
    echo "   ✓ Crystal resonance for insight flash"
    echo "   ✓ Singing bowl for Weaver entrance"
    echo "   ✓ Wind chime cascades at key moments"
    echo "   ✓ Natural, human voice quality preserved"
    echo ""
else
    echo "❌ Error: Output file not created"
    exit 1
fi

echo "Done! 🎉"
echo ""
