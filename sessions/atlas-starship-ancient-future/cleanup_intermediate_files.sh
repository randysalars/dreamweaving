#!/bin/bash
# Cleanup intermediate files from ATLAS session production
# Keeps only final deliverables

set -e

echo "======================================================================"
echo "ATLAS Session Cleanup - Removing Intermediate Files"
echo "======================================================================"
echo ""

SESSION_DIR="."

# Files to KEEP (final deliverables)
KEEP_FILES=(
    "output/atlas_ava_COMPLETE_MASTERED.mp3"
    "output/video/atlas_ava_final.mp4"
    "output/youtube_thumbnail.png"
    "output/YOUTUBE_DESCRIPTION.md"
    "output/YOUTUBE_PACKAGE_README.md"
)

# Directories with intermediate files to clean
echo "Cleaning intermediate video files..."
rm -fv output/video/*_audio.mp3 2>/dev/null || true
rm -fv output/video/ava_s*.mp4 2>/dev/null || true
rm -fv output/video/s[0-9].mp4 2>/dev/null || true
rm -fv output/video/0[0-9]_*.mp4 2>/dev/null || true
rm -fv output/video/solid_background.mp4 2>/dev/null || true
rm -fv output/video/atlas_session.mp4 2>/dev/null || true
rm -fv output/video/atlas_final.mp4 2>/dev/null || true
rm -fv output/video/atlas_ava_simple_video.mp4 2>/dev/null || true
rm -fv output/video/concat_*.txt 2>/dev/null || true
rm -fv output/video/ava_concat.txt 2>/dev/null || true

echo ""
echo "Cleaning intermediate audio files..."
rm -fv output/atlas_MASTERED.mp3 2>/dev/null || true
rm -fv output/atlas_COMPLETE_MASTERED.mp3 2>/dev/null || true

echo ""
echo "Cleaning working_files directory..."
# Keep binaural_atlas_complete.wav and final mixed files
find working_files -type f -name "*.mp3" ! -name "voice_atlas_ava_full.mp3" -delete 2>/dev/null || true
find working_files -type f -name "*.wav" ! -name "binaural_atlas_complete.wav" ! -name "atlas_ava_complete_mixed.wav" -delete 2>/dev/null || true

echo ""
echo "======================================================================"
echo "Cleanup Summary"
echo "======================================================================"
echo ""
echo "KEPT FILES (Final Deliverables):"
for file in "${KEEP_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "  ✓ $file ($size)"
    fi
done

echo ""
echo "Additional preserved files:"
ls -lh working_files/binaural_atlas_complete.wav 2>/dev/null | awk '{print "  ✓ working_files/binaural_atlas_complete.wav ("$5")"}'
ls -lh working_files/atlas_ava_complete_mixed.wav 2>/dev/null | awk '{print "  ✓ working_files/atlas_ava_complete_mixed.wav ("$5")"}'
ls -lh working_files/voice_atlas_ava_full.mp3 2>/dev/null | awk '{print "  ✓ working_files/voice_atlas_ava_full.mp3 ("$5")"}'

echo ""
echo "======================================================================"
echo "Cleanup Complete!"
echo "======================================================================"
