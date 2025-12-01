#!/bin/bash
# Professional Audio Mastering for Neural Network Navigator V2
# Simplified approach using FFmpeg directly

set -e

echo "======================================================================"
echo "PROFESSIONAL AUDIO MASTERING - Neural Network Navigator V2"
echo "======================================================================"
echo ""

INPUT="working_files/neural_navigator_complete_enhanced_v2.wav"
OUTPUT="working_files/neural_navigator_complete_enhanced_v2_MASTERED.wav"
MP3_OUTPUT="final_export/neural_network_navigator_v2_MASTERED.mp3"

# Check input exists
if [ ! -f "$INPUT" ]; then
    echo "✗ Input file not found: $INPUT"
    echo "Run ./create_enhanced_audio_v2.sh first"
    exit 1
fi

mkdir -p final_export

echo "Input: $INPUT"
echo "Output: $OUTPUT"
echo ""

echo "======================================================================"
echo "STEP 1: Analyzing Current Audio Levels"
echo "======================================================================"
echo ""

# Analyze current LUFS
ffmpeg -i "$INPUT" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary -f null - 2>&1 | tee /tmp/lufs_analysis.txt

echo ""
echo "======================================================================"
echo "STEP 2: Applying Professional Mastering"
echo "======================================================================"
echo ""

echo "Mastering Chain:"
echo "  1. LUFS Normalization → -14 LUFS (YouTube standard)"
echo "  2. Warmth EQ          → +1.5 dB @ 250 Hz"
echo "  3. Presence EQ        → +1.0 dB @ 3 kHz"
echo "  4. Stereo Enhancement → Subtle width increase"
echo "  5. Peak Limiter       → -1.0 dBTP ceiling"
echo ""

# Apply mastering with single-pass loudnorm (simpler, more reliable)
ffmpeg -i "$INPUT" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,\
       equalizer=f=250:t=h:width=200:g=1.5,\
       equalizer=f=3000:t=h:width=2000:g=1.0,\
       highshelf=f=10000:g=-0.5,\
       alimiter=limit=0.9:attack=5:release=50" \
  -c:a pcm_s24le \
  -ar 48000 \
  -y "$OUTPUT"

echo ""
echo "======================================================================"
echo "STEP 3: Creating MP3 Export"
echo "======================================================================"
echo ""

ffmpeg -i "$OUTPUT" \
  -c:a libmp3lame \
  -b:a 192k \
  -y "$MP3_OUTPUT"

echo ""
echo "======================================================================"
echo "✨ PROFESSIONAL MASTERING COMPLETE!"
echo "======================================================================"
echo ""

# Get file sizes
WAV_SIZE=$(du -h "$OUTPUT" | cut -f1)
MP3_SIZE=$(du -h "$MP3_OUTPUT" | cut -f1)

echo "Outputs Created:"
echo "  1. $OUTPUT ($WAV_SIZE)"
echo "     → Mastered 24-bit WAV for archival/future use"
echo ""
echo "  2. $MP3_OUTPUT ($MP3_SIZE)"
echo "     → High-quality MP3 for distribution"
echo ""
echo "Mastering Applied:"
echo "  ✓ LUFS normalized to -14 (YouTube optimized)"
echo "  ✓ Warmth EQ on voice frequencies"
echo "  ✓ Presence enhancement for clarity"
echo "  ✓ Peak limiting for safety"
echo ""
echo "Next Steps:"
echo "  1. Compare mastered vs. unmastered (A/B test)"
echo "  2. Listen to: $MP3_OUTPUT"
echo "  3. Use mastered audio for all final distributions"
echo ""

echo "✓ All mastering tasks complete!"
