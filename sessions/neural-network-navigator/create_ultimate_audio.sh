#!/bin/bash
# Create Ultimate Neural Network Navigator Audio
# Complete sound design with dynamic binaural beats and sound effects

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Project root is two levels up from sessions/neural-network-navigator/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SESSION_DIR="$SCRIPT_DIR"

DURATION=1421  # 23:41 in seconds
SAMPLE_RATE=48000

cd "$PROJECT_ROOT"

echo "=========================================="
echo "NEURAL NETWORK NAVIGATOR - ULTIMATE AUDIO"
echo "=========================================="
echo ""
echo "Creating comprehensive soundscape with:"
echo "  - Dynamic binaural beats (alpha/theta/gamma)"
echo "  - Sound effects at key moments"
echo "  - Ambient pad"
echo "  - Professional mixing"
echo ""

# Create temp directory
mkdir -p temp_audio

# Generate binaural beat sections using our automation system
echo "=== GENERATING BINAURAL BEATS ==="

# Section 1: Pretalk (0-145s) - Alpha 10 Hz
echo "1. Pretalk - Alpha 10 Hz (0-145s)"
python3 scripts/core/generate_binaural.py --frequency 10 --duration 145 --output temp_audio/01_pretalk_binaural.wav

# Section 2: Induction (145-290s = 145s) - Theta 5 Hz
echo "2. Induction - Theta 5 Hz (145-290s)"
python3 scripts/core/generate_binaural.py --frequency 5 --duration 145 --output temp_audio/02_induction_binaural.wav

# Section 3: Neural Garden (290-580s = 290s) - Theta 5 Hz
echo "3. Neural Garden - Theta 5 Hz (290-580s)"
python3 scripts/core/generate_binaural.py --frequency 5 --duration 290 --output temp_audio/03_garden_binaural.wav

# Section 4: Pathfinder (580-870s = 290s) - Theta 5 Hz
echo "4. Pathfinder - Theta 5 Hz (580-870s)"
python3 scripts/core/generate_binaural.py --frequency 5 --duration 290 --output temp_audio/04_pathfinder_binaural.wav

# Section 5: Weaver (870-1160s = 290s) - Theta 6 Hz
echo "5. Weaver - Theta 6 Hz (870-1160s)"
python3 scripts/core/generate_binaural.py --frequency 6 --duration 290 --output temp_audio/05_weaver_binaural.wav

# Section 6: Gamma Burst (1160-1255s = 95s) - Gamma 40 Hz!!!
echo "6. GAMMA BURST - 40 Hz (1160-1255s) *** CRITICAL ***"
python3 scripts/core/generate_binaural.py --frequency 40 --duration 95 --output temp_audio/06_gamma_binaural.wav

# Section 7: Consolidation (1255-1400s = 145s) - Alpha 10 Hz
echo "7. Consolidation - Alpha 10 Hz (1255-1400s)"
python3 scripts/core/generate_binaural.py --frequency 10 --duration 145 --output temp_audio/07_consolidation_binaural.wav

# Section 8: Awakening (1400-1421s = 21s) - Alpha 10 Hz
echo "8. Awakening - Alpha 10 Hz (1400-1421s)"
python3 scripts/core/generate_binaural.py --frequency 10 --duration 21 --output temp_audio/08_awakening_binaural.wav

echo ""
echo "=== CONCATENATING BINAURAL BEATS ==="

# Create concat list with absolute paths (dynamically generated)
cat > temp_audio/binaural_concat.txt << EOF
file '${PROJECT_ROOT}/temp_audio/01_pretalk_binaural.wav'
file '${PROJECT_ROOT}/temp_audio/02_induction_binaural.wav'
file '${PROJECT_ROOT}/temp_audio/03_garden_binaural.wav'
file '${PROJECT_ROOT}/temp_audio/04_pathfinder_binaural.wav'
file '${PROJECT_ROOT}/temp_audio/05_weaver_binaural.wav'
file '${PROJECT_ROOT}/temp_audio/06_gamma_binaural.wav'
file '${PROJECT_ROOT}/temp_audio/07_consolidation_binaural.wav'
file '${PROJECT_ROOT}/temp_audio/08_awakening_binaural.wav'
EOF

# Concatenate all binaural sections
ffmpeg -f concat -safe 0 -i temp_audio/binaural_concat.txt -c copy -y temp_audio/binaural_complete.wav

echo ""
echo "=== GENERATING SOUND EFFECTS ==="

# Generate ambient pad for full duration
echo "Generating ambient pad..."
python3 scripts/core/generate_pink_noise.py --duration $DURATION --output temp_audio/ambient_pad.wav

# Place sound effects at specific moments
# Singing bowl at anchor moments (in closing section ~1410s)
echo "Placing singing bowl at anchor moments..."
ffmpeg -i sessions/neural-network-navigator/sound_effects/singing_bowl.wav -af "adelay=1410000|1410000" -t $DURATION -y temp_audio/singing_bowl_timed.wav

# Crystal bell at major transitions (290s, 580s, 870s)
echo "Placing crystal bells at transitions..."
ffmpeg -i sessions/neural-network-navigator/sound_effects/crystal_bell.wav \
  -af "adelay=290000|290000" -t $DURATION -y temp_audio/bell_1.wav

ffmpeg -i sessions/neural-network-navigator/sound_effects/crystal_bell.wav \
  -af "adelay=580000|580000" -t $DURATION -y temp_audio/bell_2.wav

ffmpeg -i sessions/neural-network-navigator/sound_effects/crystal_bell.wav \
  -af "adelay=870000|870000" -t $DURATION -y temp_audio/bell_3.wav

# Wind chime at awakening (1400s)
echo "Placing wind chime at awakening..."
ffmpeg -i sessions/neural-network-navigator/sound_effects/wind_chime.wav \
  -af "adelay=1400000|1400000" -t $DURATION -y temp_audio/wind_chime_timed.wav

# Gamma burst noise (1160s)
echo "Placing gamma burst noise..."
ffmpeg -i sessions/neural-network-navigator/sound_effects/gamma_burst_noise.wav \
  -af "adelay=1160000|1160000" -t $DURATION -y temp_audio/gamma_noise_timed.wav

echo ""
echo "=== MIXING ALL ELEMENTS ==="

# Mix everything together with proper levels
# Voice: -16 LUFS (already mastered, will add -2 dB)
# Binaural: -28 LUFS
# Ambient pad: -32 LUFS
# Sound effects: -30 LUFS

VOICE_FILE="sessions/neural-network-navigator/working_files/neural_navigator_v2_ava_MASTERED_FIXED.wav"

ffmpeg -i "$VOICE_FILE" \
  -i temp_audio/binaural_complete.wav \
  -i temp_audio/ambient_pad.wav \
  -i temp_audio/singing_bowl_timed.wav \
  -i temp_audio/bell_1.wav \
  -i temp_audio/bell_2.wav \
  -i temp_audio/bell_3.wav \
  -i temp_audio/wind_chime_timed.wav \
  -i temp_audio/gamma_noise_timed.wav \
  -filter_complex "\
    [0:a]volume=-2dB[voice];\
    [1:a]volume=-14dB[binaural];\
    [2:a]volume=-18dB[pad];\
    [3:a]volume=-16dB[bowl];\
    [4:a]volume=-16dB[bell1];\
    [5:a]volume=-16dB[bell2];\
    [6:a]volume=-16dB[bell3];\
    [7:a]volume=-16dB[chime];\
    [8:a]volume=-12dB[gamma];\
    [voice][binaural][pad][bowl][bell1][bell2][bell3][chime][gamma]amix=inputs=9:duration=first:normalize=0[mixed]" \
  -map "[mixed]" \
  -c:a pcm_s24le -ar 48000 \
  -y sessions/neural-network-navigator/working_files/neural_navigator_ULTIMATE_MIX.wav

echo ""
echo "=== CLEANUP ==="
# rm -rf temp_audio

echo ""
echo "=========================================="
echo "✅ ULTIMATE AUDIO COMPLETE!"
echo "=========================================="
echo ""
echo "Output: sessions/neural-network-navigator/working_files/neural_navigator_ULTIMATE_MIX.wav"
echo ""
echo "Features:"
echo "  ✓ Dynamic binaural beats (Alpha → Theta → 40Hz Gamma → Alpha)"
echo "  ✓ Sound effects at key moments"
echo "  ✓ Ambient pad throughout"
echo "  ✓ Professional mixing levels"
echo "  ✓ Duration: 23:41 (1421 seconds)"
echo ""
