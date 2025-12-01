#!/usr/bin/env python3
"""
Test Basic Mixing: Voice + Binaural + Monaural
Validates core audio generation and mixing workflow
"""

import numpy as np
from scipy.io import wavfile
import os
import sys

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from audio import binaural, monaural

def mix_stems(voice_path, binaural_audio, monaural_audio,
              voice_gain_db=-16, binaural_gain_db=-28, monaural_gain_db=-30,
              sample_rate=48000):
    """
    Mix voice + binaural + monaural stems

    Args:
        voice_path: Path to voice audio file (WAV)
        binaural_audio: numpy array (stereo, float32)
        monaural_audio: numpy array (stereo, float32)
        voice_gain_db: Voice level in dB (LUFS approximation)
        binaural_gain_db: Binaural level in dB
        monaural_gain_db: Monaural level in dB
        sample_rate: Sample rate in Hz

    Returns:
        Mixed audio as numpy array (stereo, float32)
    """
    print("\n" + "="*70)
    print("MIXING STEMS")
    print("="*70 + "\n")

    # Load voice if it exists
    if os.path.exists(voice_path):
        print(f"Loading voice: {voice_path}")
        voice_sr, voice_data = wavfile.read(voice_path)

        # Convert to float32 stereo
        voice_data = voice_data.astype(np.float32) / 32768.0
        if len(voice_data.shape) == 1:
            # Mono to stereo
            voice_data = np.stack([voice_data, voice_data], axis=1)

        # Resample if needed (simple approach - proper resampling would use scipy.signal.resample)
        if voice_sr != sample_rate:
            print(f"  Warning: Voice sample rate {voice_sr} != {sample_rate}")
            print(f"  Using voice as-is (proper resampling recommended)")
    else:
        print(f"Voice file not found: {voice_path}")
        print("Creating silent voice track for testing...")
        voice_data = np.zeros_like(binaural_audio)

    # Ensure all tracks are same length
    max_length = max(len(voice_data), len(binaural_audio), len(monaural_audio))

    # Pad shorter tracks
    if len(voice_data) < max_length:
        padding = np.zeros((max_length - len(voice_data), 2), dtype=np.float32)
        voice_data = np.vstack([voice_data, padding])

    if len(binaural_audio) < max_length:
        padding = np.zeros((max_length - len(binaural_audio), 2), dtype=np.float32)
        binaural_audio = np.vstack([binaural_audio, padding])

    if len(monaural_audio) < max_length:
        padding = np.zeros((max_length - len(monaural_audio), 2), dtype=np.float32)
        monaural_audio = np.vstack([monaural_audio, padding])

    # Convert dB to linear gain
    voice_gain = 10 ** (voice_gain_db / 20.0)
    binaural_gain = 10 ** (binaural_gain_db / 20.0)
    monaural_gain = 10 ** (monaural_gain_db / 20.0)

    print(f"Stem Levels:")
    print(f"  Voice:    {voice_gain_db} dB (gain: {voice_gain:.4f})")
    print(f"  Binaural: {binaural_gain_db} dB (gain: {binaural_gain:.4f})")
    print(f"  Monaural: {monaural_gain_db} dB (gain: {monaural_gain:.4f})")
    print()

    # Mix stems
    mixed = (voice_data * voice_gain +
             binaural_audio * binaural_gain +
             monaural_audio * monaural_gain)

    # Normalize to prevent clipping
    peak = np.max(np.abs(mixed))
    if peak > 0.95:
        print(f"Peak detected: {peak:.3f} - normalizing to 0.95")
        mixed = mixed * (0.95 / peak)

    print(f"✓ Mixed track: {len(mixed)/sample_rate/60:.1f} minutes")
    print(f"  Peak level: {np.max(np.abs(mixed)):.3f}")
    print()

    return mixed


def main():
    print("="*70)
    print("BASIC MIXING TEST - Voice + Binaural + Monaural")
    print("="*70)

    # Test parameters
    duration = 120  # 2 minutes for quick test
    sample_rate = 48000

    # Define test sections (2-minute meditation intro)
    sections = [
        {
            'start': 0,
            'end': 60,
            'freq_start': 10,  # Alpha (relaxed focus)
            'freq_end': 10,
            'transition': 'linear'
        },
        {
            'start': 60,
            'end': 120,
            'freq_start': 10,
            'freq_end': 6,  # Transition to theta
            'transition': 'linear'
        }
    ]

    print("\n1. Generating Binaural Beats")
    print("-" * 70)
    binaural_audio = binaural.generate(
        sections=sections,
        duration_sec=duration,
        sample_rate=sample_rate,
        carrier_freq=200,
        amplitude=0.3
    )

    print("\n2. Generating Monaural Beats")
    print("-" * 70)
    monaural_audio = monaural.generate(
        sections=sections,
        duration_sec=duration,
        sample_rate=sample_rate,
        carrier_freq=150,
        amplitude=0.2
    )

    print("\n3. Mixing Stems")
    print("-" * 70)

    # For testing, we'll use a silent voice track since we don't have generated voice yet
    # In production, this would be the TTS-generated voice
    voice_path = "test_voice.wav"  # Placeholder - won't exist

    mixed_audio = mix_stems(
        voice_path=voice_path,
        binaural_audio=binaural_audio,
        monaural_audio=monaural_audio,
        voice_gain_db=-16,
        binaural_gain_db=-28,
        monaural_gain_db=-30
    )

    print("\n4. Saving Outputs")
    print("-" * 70)

    # Create test output directory
    os.makedirs("test_output", exist_ok=True)

    # Save individual stems
    binaural.save_stem(binaural_audio, "test_output/test_binaural.wav", sample_rate)
    monaural.save_stem(monaural_audio, "test_output/test_monaural.wav", sample_rate)

    # Save mixed output
    mixed_int = (mixed_audio * 32767).astype(np.int16)
    wavfile.write("test_output/test_mixed.wav", sample_rate, mixed_int)

    file_size = os.path.getsize("test_output/test_mixed.wav") / (1024 * 1024)
    print(f"✓ Saved mixed audio: test_output/test_mixed.wav ({file_size:.1f} MB)")

    print("\n" + "="*70)
    print("✓ BASIC MIXING TEST COMPLETE!")
    print("="*70)
    print("\nOutputs created:")
    print("  test_output/test_binaural.wav  - Binaural beats only")
    print("  test_output/test_monaural.wav  - Monaural beats only")
    print("  test_output/test_mixed.wav     - Combined mix (binaural + monaural)")
    print("\nNext Steps:")
    print("  1. Listen to each file to verify audio quality")
    print("  2. Verify binaural beats require headphones (stereo effect)")
    print("  3. Verify monaural beats work without headphones (mono effect)")
    print("  4. Confirm smooth frequency transitions in 2nd minute")
    print("\nOnce validated, proceed to implement remaining sound types:")
    print("  - isochronic.py, panning_beats.py, alternate_beeps.py")
    print("  - am_tones.py, pink_noise.py, nature.py, percussion.py")
    print()

    return 0


if __name__ == '__main__':
    try:
        exit(main())
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
