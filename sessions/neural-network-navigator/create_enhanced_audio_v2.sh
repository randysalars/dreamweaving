#!/bin/bash
#
# Neural Network Navigator: Enhanced Audio Production V2
# Complete professional format with pretalk and closing
#
# This script:
# 1. Generates enhanced voice track V2 (with pretalk/closing)
# 2. Uses existing binaural beat track (or generates if missing)
# 3. Mixes voice + binaural + sound effects
#

set -e  # Exit on error

echo "======================================================================"
echo "   NEURAL NETWORK NAVIGATOR - Enhanced Audio V2"
echo "   Complete Professional Format"
echo "======================================================================"
echo ""
echo "Version 2 includes:"
echo "  ✓ Detailed pretalk explaining journey benefits"
echo "  ✓ Safety and control statements"
echo "  ✓ Preparation instructions"
echo "  ✓ Extended journey content with strategic pauses"
echo "  ✓ Proper 1-10 awakening countdown"
echo "  ✓ 5 post-hypnotic anchors for daily practice"
echo "  ✓ Sleep/dream integration suggestions"
echo "  ✓ Immersive sound effects"
echo "  ✓ Full 25-28 minute session duration"
echo ""
echo "This follows the professional Dreamweaving format."
echo ""

cd "$(dirname "$0")"

# Check if we're in the right directory
if [ ! -f "generate_enhanced_voice_v2.py" ]; then
    echo "❌ Error: Must run from neural-network-navigator session directory"
    exit 1
fi

# Check for required files
echo "🔍 Checking prerequisites..."

if [ ! -f "working_files/voice_script_enhanced_v2.ssml" ]; then
    echo "❌ Error: Enhanced SSML V2 script not found"
    echo "   Expected: working_files/voice_script_enhanced_v2.ssml"
    exit 1
fi
echo "  ✓ Enhanced SSML V2 script found (with pretalk/closing)"

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
echo "STEP 1: Generate Enhanced Voice Track V2"
echo "======================================================================"
echo ""
echo "This will use chunked generation for the larger script file."
echo "The complete script includes:"
echo "  • Detailed pretalk with benefits explanation"
echo "  • Extended journey with strategic pauses"
echo "  • Proper awakening sequence (1-10)"
echo "  • 5 post-hypnotic anchors"
echo "  • Sleep/dream integration"
echo ""

if [ -f "working_files/voice_neural_navigator_enhanced_v2.mp3" ]; then
    echo "⚠️  Enhanced voice V2 track already exists"
    read -p "Regenerate? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  Skipping voice generation"
    else
        echo "  Regenerating voice track V2..."
        python3 generate_enhanced_voice_v2.py
    fi
else
    echo "Generating enhanced voice track V2..."
    python3 generate_enhanced_voice_v2.py
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
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "working_files/binaural_beats_neural_navigator.wav" 2>/dev/null | awk '{printf "%.0f", $1}')
    echo "  Duration: $((DURATION/60)) minutes $((DURATION%60)) seconds"
fi

echo ""
echo "======================================================================"
echo "STEP 3: Create Enhanced Audio Mix V2"
echo "======================================================================"
echo ""

echo "Mixing voice V2 + binaural + sound effects..."
echo ""
echo "Note: Using voice_neural_navigator_enhanced_v2.mp3"
echo ""

# Update the mixing script to use V2 file
if [ -f "generate_enhanced_audio.py" ]; then
    # Create a V2 version of the mixing script
    sed 's/voice_neural_navigator_enhanced\.mp3/voice_neural_navigator_enhanced_v2.mp3/g; s/neural_navigator_complete_enhanced\.wav/neural_navigator_complete_enhanced_v2.wav/g' generate_enhanced_audio.py > generate_enhanced_audio_v2.py
    python3 generate_enhanced_audio_v2.py
    rm generate_enhanced_audio_v2.py
else
    echo "❌ Error: generate_enhanced_audio.py not found"
    exit 1
fi

echo ""
echo "======================================================================"
echo "✅ ENHANCEMENT V2 COMPLETE!"
echo "======================================================================"
echo ""

if [ -f "working_files/neural_navigator_complete_enhanced_v2.wav" ]; then
    FILE_SIZE=$(du -h "working_files/neural_navigator_complete_enhanced_v2.wav" | cut -f1)
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "working_files/neural_navigator_complete_enhanced_v2.wav" 2>/dev/null | awk '{printf "%.1f", $1/60}')

    echo "📁 Output file: working_files/neural_navigator_complete_enhanced_v2.wav"
    echo "📊 Size: $FILE_SIZE"
    echo "⏱️  Duration: ${DURATION} minutes"
    echo ""
    echo "🎧 Listen with: ffplay working_files/neural_navigator_complete_enhanced_v2.wav"
    echo "📤 Export to MP3: ffmpeg -i working_files/neural_navigator_complete_enhanced_v2.wav -b:a 192k neural_navigator_enhanced_v2.mp3"
    echo ""
    echo "✨ Version 2 Enhancements:"
    echo "   ✓ Detailed pretalk explaining benefits"
    echo "   ✓ Safety and control statements"
    echo "   ✓ Preparation instructions for optimal experience"
    echo "   ✓ Extended pauses on transition phrases"
    echo "   ✓ Journey content extends full duration"
    echo "   ✓ Proper 1-10 awakening countdown"
    echo "   ✓ 5 practical post-hypnotic anchors:"
    echo "      • Three Conscious Breaths (activate learning)"
    echo "      • Pathfinder's Touch (creative problem-solving)"
    echo "      • Golden Thread Visualization (integrate knowledge)"
    echo "      • Neural Garden Gateway (peak performance)"
    echo "      • Plasticity Affirmation (dispel doubt)"
    echo "   ✓ Sleep/dream integration suggestions"
    echo "   ✓ Bell chimes, crystal tones, singing bowls"
    echo "   ✓ Natural, human voice quality preserved"
    echo "   ✓ Professional Dreamweaving format compliance"
    echo ""
    echo "📖 See PRETALK_CLOSING_ENHANCEMENTS.md for detailed comparison"
    echo ""
else
    echo "❌ Error: Output file not created"
    exit 1
fi

echo "Done! 🎉"
echo ""
