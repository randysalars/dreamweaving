#!/bin/bash
# Simple video creation using ultimate mix
# More reliable than the complex Python script

set -e

AUDIO="working_files/neural_navigator_ULTIMATE_MIX.wav"
IMAGES_DIR="images"
OUTPUT="final_export/neural_network_navigator_v2_ava_FINAL.mp4"

echo "========================================================================"
echo "CREATING FINAL VIDEO WITH ULTIMATE MIX"
echo "========================================================================"
echo ""

# Check inputs
if [ ! -f "$AUDIO" ]; then
    echo "✗ Audio file not found: $AUDIO"
    exit 1
fi

if [ ! -d "$IMAGES_DIR" ]; then
    echo "✗ Images directory not found: $IMAGES_DIR"
    exit 1
fi

# Create output directory
mkdir -p final_export

echo "Audio: $AUDIO"
echo "Images: $IMAGES_DIR"
echo "Output: $OUTPUT"
echo ""

# Scene timings (in seconds)
# Total duration: 1421 seconds (23:41)
SCENE_1_DUR=150    # 0:00 - 2:30 (Opening)
SCENE_2_DUR=150    # 2:30 - 5:00 (Induction)
SCENE_3_DUR=300    # 5:00 - 10:00 (Neural Garden)
SCENE_4_DUR=300    # 10:00 - 15:00 (Pathfinder)
SCENE_5_DUR=300    # 15:00 - 20:00 (Weaver)
SCENE_6_DUR=95     # 20:00 - 21:35 (Gamma Burst)
SCENE_7_DUR=145    # 21:35 - 24:00 (Consolidation)
SCENE_8_DUR=0      # 24:00 - end (Awakening - use rest of audio)

echo "Creating video with 8 scenes..."
echo "Duration: 23:41 (1421 seconds)"
echo "Resolution: 1920x1080 @ 30fps"
echo ""
echo "This will take several minutes..."
echo ""

# Build FFmpeg command
ffmpeg \
  -i "$AUDIO" \
  -loop 1 -t $SCENE_1_DUR -i "$IMAGES_DIR/scene_01_opening_FINAL.png" \
  -loop 1 -t $SCENE_2_DUR -i "$IMAGES_DIR/scene_02_descent_FINAL.png" \
  -loop 1 -t $SCENE_3_DUR -i "$IMAGES_DIR/scene_03_neural_garden_FINAL.png" \
  -loop 1 -t $SCENE_4_DUR -i "$IMAGES_DIR/scene_04_pathfinder_FINAL.png" \
  -loop 1 -t $SCENE_5_DUR -i "$IMAGES_DIR/scene_05_weaver_FINAL.png" \
  -loop 1 -t $SCENE_6_DUR -i "$IMAGES_DIR/scene_06_gamma_burst_FINAL.png" \
  -loop 1 -t $SCENE_7_DUR -i "$IMAGES_DIR/scene_07_consolidation_FINAL.png" \
  -loop 1 -i "$IMAGES_DIR/scene_08_return_FINAL.png" \
  -filter_complex "\
    [1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];\
    [2:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];\
    [3:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v2];\
    [4:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v3];\
    [5:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v4];\
    [6:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v5];\
    [7:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v6];\
    [8:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v7];\
    [v0][v1][v2][v3][v4][v5][v6][v7]concat=n=8:v=1:a=0[vout]" \
  -map "[vout]" \
  -map 0:a \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -pix_fmt yuv420p \
  -c:a aac \
  -b:a 256k \
  -ar 48000 \
  -movflags +faststart \
  -t 1421 \
  -y \
  "$OUTPUT"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo ""
    echo "========================================================================"
    echo "✓ VIDEO CREATION COMPLETE"
    echo "========================================================================"
    echo ""
    echo "Final Video: $OUTPUT"
    echo "Size: $SIZE"
    echo "Duration: 23:41 (1421 seconds)"
    echo "Resolution: 1920x1080 @ 30fps"
    echo ""
    echo "Features:"
    echo "  ✓ Ava Neural voice (warm, professional, corrected SSML)"
    echo "  ✓ V2 enhanced script (pretalk + 5 anchors + closing)"
    echo "  ✓ Professional audio mastering (-14 LUFS)"
    echo "  ✓ Dynamic binaural beats (Alpha → Theta → 40Hz Gamma → Alpha)"
    echo "  ✓ Pink noise ambient pad (cached from asset library)"
    echo "  ✓ Sound effects (singing bowls, crystal bells, wind chimes)"
    echo "  ✓ 8 visual scenes (1920x1080)"
    echo ""
else
    echo ""
    echo "✗ Video creation failed"
    exit 1
fi
