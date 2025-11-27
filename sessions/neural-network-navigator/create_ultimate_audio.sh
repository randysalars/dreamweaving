#!/bin/bash
#
# Master orchestration script for Neural Network Navigator production
# Option B: Simplified Production (8-9 hours)
#
# This script runs all production steps in order:
# 1. SSML voice script creation ✓ COMPLETE
# 2. Voice generation ✓ COMPLETE
# 3. Binaural beats generation ✓ COMPLETE
# 4. Image generation (running in background)
# 5. Essential sound effects ✓ COMPLETE
# 6. 3-layer audio mixing (NEXT)
# 7. Gradient backgrounds (NEXT)
# 8. Final video composition (WAITING FOR IMAGES)
# 9. Quality check

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source ../../venv/bin/activate

echo "======================================================================"
echo "NEURAL NETWORK NAVIGATOR - Ultimate Production Pipeline"
echo "Option B: Simplified Production"
echo "======================================================================"
echo ""

# Check what's already complete
echo "Checking production status..."
echo ""

# Phase 1-2: Setup (already complete)
echo "✓ Phase 1: Setup complete (Edge TTS, SDXL installed)"
echo "✓ Phase 2: SSML voice script created"

# Phase 3: Voice (already complete)
if [ -f "working_files/voice_neural_navigator.mp3" ]; then
    VOICE_SIZE=$(du -h working_files/voice_neural_navigator.mp3 | cut -f1)
    echo "✓ Phase 3: Voice generated ($VOICE_SIZE)"
else
    echo "✗ Phase 3: Voice missing - run generate_voice_v2.py"
    exit 1
fi

# Phase 4: Binaural beats (already complete)
if [ -f "working_files/binaural_beats_neural_navigator.wav" ]; then
    BINAURAL_SIZE=$(du -h working_files/binaural_beats_neural_navigator.wav | cut -f1)
    echo "✓ Phase 4: Binaural beats generated ($BINAURAL_SIZE)"
else
    echo "✗ Phase 4: Binaural beats missing - run generate_binaural_neural.py"
    exit 1
fi

# Phase 5: Images (check if running or complete)
IMAGE_COUNT=$(ls images/scene_*_FINAL.png 2>/dev/null | wc -l)
if [ "$IMAGE_COUNT" -eq 8 ]; then
    echo "✓ Phase 5: All 8 images generated"
    IMAGES_COMPLETE=true
else
    echo "⏳ Phase 5: Images generating ($IMAGE_COUNT/8 complete)"
    echo "   (Images are generating in background - continuing with audio)"
    IMAGES_COMPLETE=false
fi

# Phase 6: Sound effects (already complete)
if [ -d "sound_effects" ] && [ $(ls sound_effects/*.wav 2>/dev/null | wc -l) -ge 5 ]; then
    echo "✓ Phase 6: Essential sound effects generated (5 files)"
else
    echo "⚠️  Phase 6: Sound effects incomplete - generating now..."
    python3 generate_essential_sounds.py
fi

echo ""
echo "======================================================================"

# Phase 7: Audio mixing
echo ""
echo "Phase 7: 3-Layer Audio Mixing"
echo "======================================================================"
if [ -f "working_files/audio_mix_master.wav" ]; then
    AUDIO_SIZE=$(du -h working_files/audio_mix_master.wav | cut -f1)
    echo "✓ Master audio mix already exists ($AUDIO_SIZE)"
    echo "  Skipping remix (delete file to regenerate)"
else
    echo "Mixing voice + binaural + effects..."
    python3 mix_audio_simple.py
    if [ $? -ne 0 ]; then
        echo "✗ Audio mixing failed"
        exit 1
    fi
fi

# Phase 8: Gradient backgrounds
echo ""
echo "Phase 8: Gradient Background Generation"
echo "======================================================================"
if [ -d "gradients" ] && [ $(ls gradients/*.png 2>/dev/null | wc -l) -ge 8 ]; then
    echo "✓ Gradients already generated"
else
    echo "Generating gradient backgrounds..."
    python3 generate_gradient_backgrounds.py
    if [ $? -ne 0 ]; then
        echo "✗ Gradient generation failed"
        exit 1
    fi
fi

# Phase 9: Final video composition
echo ""
echo "Phase 9: Final Video Composition"
echo "======================================================================"

if [ "$IMAGES_COMPLETE" = false ]; then
    echo "⏸️  WAITING: Image generation must complete before video composition"
    echo ""
    echo "Current status: $IMAGE_COUNT/8 images complete"
    echo ""
    echo "When images are done, run:"
    echo "  python3 composite_final_video.py"
    echo ""
    echo "Or re-run this script to complete the pipeline"
    exit 0
fi

# Images are complete - proceed with video composition
if [ -f "final_export/neural_network_navigator.mp4" ]; then
    FINAL_SIZE=$(du -h final_export/neural_network_navigator.mp4 | cut -f1)
    echo "✓ Final video already exists ($FINAL_SIZE)"
    echo "  Delete to regenerate"
else
    echo "Compositing final video..."
    echo "⚠️  This will take 15-30 minutes (FFmpeg encoding)"
    python3 composite_final_video.py
    if [ $? -ne 0 ]; then
        echo "✗ Video composition failed"
        exit 1
    fi
fi

# Phase 10: Quality check
echo ""
echo "======================================================================"
echo "Phase 10: Quality Check"
echo "======================================================================"
echo ""
echo "Manual quality check required:"
echo ""
echo "1. Play final video: final_export/neural_network_navigator.mp4"
echo "2. Verify duration: 28:00 minutes"
echo "3. Check voice clarity throughout"
echo "4. ⚠️  CRITICAL: Verify gamma burst sync at 18:45 (1125 seconds)"
echo "   - White flash should sync with voice 'FLASH' moment"
echo "   - Binaural should jump to 40 Hz gamma for 3 seconds"
echo "   - Visual should show brilliant white scene"
echo "5. Test with headphones for binaural effect"
echo "6. Check all image transitions are smooth (2-second crossfades)"
echo ""
echo "======================================================================"
echo "✓ PRODUCTION PIPELINE COMPLETE!"
echo "======================================================================"
echo ""
echo "Final output: final_export/neural_network_navigator.mp4"
echo ""
