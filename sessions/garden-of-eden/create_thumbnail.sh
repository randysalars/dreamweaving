#!/bin/bash

# Create YouTube thumbnail with text overlay

SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SESSION_DIR/output/video"

echo "======================================================================"
echo "   Garden of Eden - Thumbnail Generator"
echo "======================================================================"
echo ""

# Check for available images in order of preference
if [ -f "$SESSION_DIR/eden_01_pretalk.png" ]; then
    echo "Using: eden_01_pretalk.png"
    BASE_IMAGE="$SESSION_DIR/eden_01_pretalk.png"
elif [ -f "$SESSION_DIR/eden_opening.png" ]; then
    echo "Using: eden_opening.png (legacy)"
    BASE_IMAGE="$SESSION_DIR/eden_opening.png"
elif [ -f "$SESSION_DIR/eden_03_meadow.png" ]; then
    echo "Using: eden_03_meadow.png"
    BASE_IMAGE="$SESSION_DIR/eden_03_meadow.png"
elif [ -f "$SESSION_DIR/eden_05_tree.png" ]; then
    echo "Using: eden_05_tree.png"
    BASE_IMAGE="$SESSION_DIR/eden_05_tree.png"
elif [ -f "$OUTPUT_DIR/garden_of_eden_FINAL.mp4" ]; then
    echo "Extracting frame from video at 8:00 (meadow scene)..."
    ffmpeg -i "$OUTPUT_DIR/garden_of_eden_FINAL.mp4" -ss 00:08:00 -vframes 1 -y "$OUTPUT_DIR/thumbnail_base.png" 2>/dev/null
    BASE_IMAGE="$OUTPUT_DIR/thumbnail_base.png"
else
    echo "❌ Error: No images or video found"
    echo ""
    echo "Please either:"
    echo "  1. Generate images (see FULL_IMAGE_GUIDE.md)"
    echo "  2. Or run ./create_final_video.sh first"
    echo ""
    echo "Recommended: Use eden_01_pretalk.png or eden_03_meadow.png for thumbnail"
    exit 1
fi

# Create thumbnail with text overlays
ffmpeg -i "$BASE_IMAGE" \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,\
pad=1280:720:(ow-iw)/2:(oh-ih)/2,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:\
text='GARDEN OF EDEN':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=150:\
borderw=4:bordercolor=black,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:\
text='25 Min Theta Meditation':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=280:\
borderw=3:bordercolor=black,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
text='🎧 HEADPHONES REQUIRED':fontcolor=yellow:fontsize=36:x=50:y=50:\
borderw=2:bordercolor=black,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
text='🌟 3D BINAURAL AUDIO':fontcolor=yellow:fontsize=36:x=50:y=100:\
borderw=2:bordercolor=black" \
  -frames:v 1 -y "$OUTPUT_DIR/thumbnail_final.jpg"

echo ""
echo "✅ Thumbnail created: $OUTPUT_DIR/thumbnail_final.jpg"
echo ""
echo "Preview with: eog $OUTPUT_DIR/thumbnail_final.jpg"
echo ""
echo "Upload this as your YouTube thumbnail!"
