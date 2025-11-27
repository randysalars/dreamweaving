#!/bin/bash

# Garden of Eden - Final Video Compositor
# Combines background, particles, images, and audio

set -e  # Exit on error

echo "======================================================================"
echo "   Garden of Eden - Final Video Production"
echo "======================================================================"
echo ""

SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SESSION_DIR/output/video"
mkdir -p "$OUTPUT_DIR"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: Create background gradient video
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if [ ! -f "$OUTPUT_DIR/background_gradient.mp4" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "STEP 1: Generating chakra gradient background"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python3 generate_video_background.py
    python3 compile_video.py video_frames "$OUTPUT_DIR/background_gradient.mp4"
else
    echo "✓ Background gradient already exists, skipping..."
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Add Garden images with fade effects (if available)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Compositing Garden images (if available)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Use Python script for reliable image compositing
if python3 "$SESSION_DIR/composite_images.py"; then
    COMPOSITE_FILE="$OUTPUT_DIR/composite_with_images.mp4"
else
    echo "No images found, using background gradient only"
    COMPOSITE_FILE="$OUTPUT_DIR/background_gradient.mp4"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: Add title overlay
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Adding title overlay"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ffmpeg -i "$COMPOSITE_FILE" \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:\
text='GARDEN OF EDEN':fontcolor=white@0.9:fontsize=72:x=(w-text_w)/2:y=100:\
shadowcolor=black@0.8:shadowx=3:shadowy=3:enable='between(t,5,30)',\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:\
text='Guided Meditation | 25 Minutes':fontcolor=white@0.8:fontsize=36:x=(w-text_w)/2:y=200:\
shadowcolor=black@0.8:shadowx=2:shadowy=2:enable='between(t,5,30)'" \
  -c:v libx264 -crf 18 -y \
  "$OUTPUT_DIR/video_with_titles.mp4"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: Add meditation audio
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Adding meditation audio"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Use the natural v2 audio we generated
AUDIO_FILE="$SESSION_DIR/output/natural/garden_of_eden_NATURAL_v2.mp3"

if [ -f "$AUDIO_FILE" ]; then
    ffmpeg -i "$OUTPUT_DIR/video_with_titles.mp4" \
      -i "$AUDIO_FILE" \
      -c:v copy \
      -c:a aac \
      -b:a 192k \
      -shortest \
      -y \
      "$OUTPUT_DIR/garden_of_eden_FINAL.mp4"

    echo ""
    echo "======================================================================"
    echo "✨ FINAL VIDEO COMPLETE! ✨"
    echo "======================================================================"
    echo ""
    echo "📁 Output: $OUTPUT_DIR/garden_of_eden_FINAL.mp4"

    # Get file info
    FILE_SIZE=$(du -h "$OUTPUT_DIR/garden_of_eden_FINAL.mp4" | cut -f1)
    echo "📊 File size: $FILE_SIZE"

    echo ""
    echo "Next steps:"
    echo "  1. Review video: vlc $OUTPUT_DIR/garden_of_eden_FINAL.mp4"
    echo "  2. Create thumbnail: ./create_thumbnail.sh"
    echo "  3. Upload to YouTube with description from YOUTUBE_DESCRIPTION.md"

else
    echo "❌ Error: Audio file not found: $AUDIO_FILE"
    echo "   Generate it first with: ./create_natural_audio.sh"
    exit 1
fi
