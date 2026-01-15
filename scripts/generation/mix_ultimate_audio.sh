#!/bin/bash
# Final mix of all 9 audio layers for Neural Network Navigator

cd sessions/neural-network-navigator

echo "=== MIXING 9 AUDIO LAYERS ==="
echo "1. Voice (mastered) at -2 dB"
echo "2. Binaural beats (dynamic) at -14 dB"
echo "3. Ambient pad at -18 dB"
echo "4. Singing bowl at -16 dB"
echo "5-7. Crystal bells (3x) at -16 dB"
echo "8. Wind chime at -16 dB"
echo "9. Gamma burst noise at -12 dB"
echo ""

ffmpeg \
  -i working_files/neural_navigator_v2_ava_MASTERED_FIXED.wav \
  -i ../../temp_audio/binaural_complete.wav \
  -i ../../temp_audio/ambient_pad.wav \
  -i ../../temp_audio/singing_bowl_timed.wav \
  -i ../../temp_audio/bell_1.wav \
  -i ../../temp_audio/bell_2.wav \
  -i ../../temp_audio/bell_3.wav \
  -i ../../temp_audio/wind_chime_timed.wav \
  -i ../../temp_audio/gamma_noise_timed.wav \
  -filter_complex '[0:a]volume=-2dB[voice];[1:a]volume=-14dB[binaural];[2:a]volume=-18dB[pad];[3:a]volume=-16dB[bowl];[4:a]volume=-16dB[bell1];[5:a]volume=-16dB[bell2];[6:a]volume=-16dB[bell3];[7:a]volume=-16dB[chime];[8:a]volume=-12dB[gamma];[voice][binaural][pad][bowl][bell1][bell2][bell3][chime][gamma]amix=inputs=9:duration=first:normalize=0[mixed]' \
  -map '[mixed]' \
  -c:a pcm_s24le \
  -ar 48000 \
  -y working_files/neural_navigator_ULTIMATE_MIX.wav

echo ""
echo "=== MIX COMPLETE ==="
ls -lh working_files/neural_navigator_ULTIMATE_MIX.wav
