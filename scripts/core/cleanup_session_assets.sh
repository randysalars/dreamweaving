#!/bin/bash
# Auto-generated cleanup script for meditation session production
# Removes intermediate files while preserving final deliverables

set -e

SESSION_DIR="${1:-.}"

echo "======================================================================"
echo "Session Cleanup - Removing Intermediate Files"
echo "======================================================================"
echo ""
echo "Session: $SESSION_DIR"
echo ""

# Files to ALWAYS KEEP (final deliverables)
echo "Preserving final deliverables..."

# Clean intermediate video files
if [ -d "$SESSION_DIR/output/video" ]; then
    echo "Cleaning intermediate video files..."
    find "$SESSION_DIR/output/video" -type f \
        ! -name "*_final.mp4" \
        ! -name "session_final.mp4" \
        ! -name "concat*.txt" \
        -name "*.mp4" -delete 2>/dev/null || true
    
    # Remove audio segments
    find "$SESSION_DIR/output/video" -name "*_audio.mp3" -delete 2>/dev/null || true
    find "$SESSION_DIR/output/video" -name "*_audio.aac" -delete 2>/dev/null || true
fi

# Clean working_files but keep essential stems
if [ -d "$SESSION_DIR/working_files" ]; then
    echo "Cleaning working_files directory..."
    
    # Keep only final voice, binaural, and mixed files
    find "$SESSION_DIR/working_files" -type f \
        ! -name "voice_*_full.*" \
        ! -name "binaural_*_complete.*" \
        ! -name "*_complete_mixed.*" \
        ! -name "*.json" \
        -name "*.mp3" -o -name "*.wav" \
        -delete 2>/dev/null || true
fi

# Remove temp/test files
find "$SESSION_DIR" -maxdepth 1 -type f \
    -name "test_*.wav" -o -name "test_*.mp3" \
    -delete 2>/dev/null || true

echo ""
echo "======================================================================"
echo "Cleanup Summary"
echo "======================================================================"
echo ""
echo "PRESERVED FILES:"
if [ -d "$SESSION_DIR/output" ]; then
    find "$SESSION_DIR/output" -type f -name "*final*" -o -name "youtube_*" -o -name "YOUTUBE_*" | while read f; do
        size=$(du -h "$f" | cut -f1)
        echo "  ✓ ${f#$SESSION_DIR/} ($size)"
    done
fi

echo ""
echo "======================================================================"
echo "Cleanup Complete!"
echo "======================================================================"
