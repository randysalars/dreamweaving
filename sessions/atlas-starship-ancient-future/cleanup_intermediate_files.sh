#!/bin/bash
# Cleanup intermediate files from ATLAS Starship session production
# Keeps only final deliverables

set -e

echo "======================================================================"
echo "ATLAS Starship Session Cleanup - Removing Intermediate Files"
echo "======================================================================"
echo ""

# Get the directory where this script is located (the session directory)
SESSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SESSION_DIR"

# Show current disk usage before cleanup
echo "Current disk usage:"
du -sh . 2>/dev/null || true
echo ""

# Files to KEEP (final deliverables)
echo "Files that will be PRESERVED:"
echo "  • output/atlas_starship_final.mp4 (main video)"
echo "  • output/atlas_starship_final.wav (24-bit master audio)"
echo "  • output/atlas_starship_final.mp3 (320kbps audio)"
echo "  • output/youtube_package/* (all YouTube upload files)"
echo "  • output/voice.mp3 (original voice recording)"
echo "  • working_files/stems/00_voice_mastered.wav (mastered voice)"
echo ""

read -p "Proceed with cleanup? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Cleaning intermediate audio stems..."
# Remove raw sound layer stems (keep mastered voice)
rm -fv working_files/stems/01_theta_gateway.wav 2>/dev/null || true
rm -fv working_files/stems/02_delta_drift.wav 2>/dev/null || true
rm -fv working_files/stems/03_xenolinguistic.wav 2>/dev/null || true
rm -fv working_files/stems/04_harmonic_drone.wav 2>/dev/null || true
rm -fv working_files/stems/05_sub_bass.wav 2>/dev/null || true
rm -fv working_files/stems/06_hyperspace_wind.wav 2>/dev/null || true
rm -fv working_files/stems/07_ship_memory.wav 2>/dev/null || true

echo ""
echo "Cleaning old/legacy output files..."
rm -fv output/atlas_ava_COMPLETE_MASTERED.mp3 2>/dev/null || true
rm -fv output/atlas_ava_final.mp4 2>/dev/null || true
rm -fv output/atlas_ava_MASTERED.mp3 2>/dev/null || true
rm -fv output/final_mix.mp3 2>/dev/null || true
rm -fv output/binaural.wav 2>/dev/null || true
rm -fv output/audio_summary.json 2>/dev/null || true

echo ""
echo "Cleaning old video folder..."
rm -rfv output/video 2>/dev/null || true

echo ""
echo "Cleaning temporary working files..."
rm -fv working_files/voice_temp.wav 2>/dev/null || true
rm -fv working_files/video_temp/* 2>/dev/null || true
rmdir working_files/video_temp 2>/dev/null || true

echo ""
echo "======================================================================"
echo "Cleanup Summary"
echo "======================================================================"
echo ""
echo "PRESERVED FILES (Final Deliverables):"

# Check and list preserved files
for file in \
    "output/atlas_starship_final.mp4" \
    "output/atlas_starship_final.wav" \
    "output/atlas_starship_final.mp3" \
    "output/voice.mp3" \
    "output/subtitles.vtt" \
    "working_files/stems/00_voice_mastered.wav"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "  ✓ $file ($size)"
    fi
done

echo ""
echo "YouTube Package:"
if [ -d "output/youtube_package" ]; then
    ls -lh output/youtube_package/ | tail -n +2 | awk '{print "  ✓ "$NF" ("$5")"}'
fi

echo ""
echo "Disk usage after cleanup:"
du -sh . 2>/dev/null || true

echo ""
echo "======================================================================"
echo "Cleanup Complete!"
echo "======================================================================"
