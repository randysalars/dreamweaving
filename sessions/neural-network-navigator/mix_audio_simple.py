#!/usr/bin/env python3
"""
Simplified 3-layer audio mixer for Neural Network Navigator
Combines:
- Layer 1: Voice (center, 0 dB)
- Layer 2: Binaural beats (stereo, -20 dB)
- Layer 3: Minimal effects (gamma burst at 18:45, ambient pad)
"""

import numpy as np
from scipy.io import wavfile
import os
import subprocess
import tempfile

def load_audio(filepath):
    """
    Load audio file (MP3 or WAV) and return sample rate and normalized audio
    If MP3, converts to WAV first using FFmpeg
    """
    # Check if file is MP3
    if filepath.endswith('.mp3'):
        # Convert MP3 to WAV using FFmpeg
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_wav = tmp.name

        cmd = [
            'ffmpeg', '-i', filepath,
            '-ar', '44100',  # 44.1 kHz
            '-ac', '2',      # Stereo
            '-y',
            tmp_wav
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg conversion failed: {result.stderr}")

        # Read the converted WAV
        sample_rate, audio = wavfile.read(tmp_wav)

        # Clean up temp file
        os.remove(tmp_wav)
    else:
        # Direct WAV read
        sample_rate, audio = wavfile.read(filepath)

    # Convert to float32 and normalize to -1.0 to 1.0
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    elif audio.dtype == np.int32:
        audio = audio.astype(np.float32) / 2147483648.0
    else:
        audio = audio.astype(np.float32)

    # Convert mono to stereo if needed
    if len(audio.shape) == 1:
        audio = np.stack([audio, audio], axis=1)

    return sample_rate, audio

def adjust_volume(audio, db):
    """Adjust volume by decibels"""
    factor = 10 ** (db / 20.0)
    return audio * factor

def overlay_audio(base, overlay, start_time, sample_rate):
    """
    Overlay audio at specific timestamp
    base: background audio (will be modified in place)
    overlay: audio to overlay
    start_time: timestamp in seconds
    """
    start_sample = int(start_time * sample_rate)

    if start_sample >= len(base):
        print(f"  Warning: Start time {start_time}s is beyond base audio length")
        return

    # Calculate how many samples to overlay
    overlay_samples = min(len(overlay), len(base) - start_sample)

    # Add overlay to base
    base[start_sample:start_sample + overlay_samples] += overlay[:overlay_samples]

def mix_audio():
    print("=" * 60)
    print("NEURAL NETWORK NAVIGATOR - 3-Layer Audio Mixing")
    print("=" * 60)

    working_dir = "working_files"
    effects_dir = "sound_effects"

    # Load primary tracks
    print("\n1. Loading primary audio tracks...\n")

    print("  Loading voice...")
    voice_rate, voice = load_audio(f"{working_dir}/voice_neural_navigator.mp3")
    print(f"    ✓ Voice: {len(voice)/voice_rate:.1f}s, {voice_rate} Hz")

    print("  Loading binaural beats...")
    binaural_rate, binaural = load_audio(f"{working_dir}/binaural_beats_neural_navigator.wav")
    print(f"    ✓ Binaural: {len(binaural)/binaural_rate:.1f}s, {binaural_rate} Hz")

    # Resample if sample rates don't match - use the higher rate
    if voice_rate != binaural_rate:
        print(f"\n  Sample rate mismatch detected: voice={voice_rate}, binaural={binaural_rate}")
        print(f"  Resampling to {max(voice_rate, binaural_rate)} Hz...")

        target_rate = max(voice_rate, binaural_rate)

        # Resample voice if needed
        if voice_rate != target_rate:
            from scipy import signal
            ratio = target_rate / voice_rate
            num_samples = int(len(voice) * ratio)
            voice_resampled = np.zeros((num_samples, 2), dtype=np.float32)
            voice_resampled[:, 0] = signal.resample(voice[:, 0], num_samples)
            voice_resampled[:, 1] = signal.resample(voice[:, 1], num_samples)
            voice = voice_resampled
            voice_rate = target_rate
            print(f"    ✓ Voice resampled to {target_rate} Hz")

        # Resample binaural if needed
        if binaural_rate != target_rate:
            from scipy import signal
            ratio = target_rate / binaural_rate
            num_samples = int(len(binaural) * ratio)
            binaural_resampled = np.zeros((num_samples, 2), dtype=np.float32)
            binaural_resampled[:, 0] = signal.resample(binaural[:, 0], num_samples)
            binaural_resampled[:, 1] = signal.resample(binaural[:, 1], num_samples)
            binaural = binaural_resampled
            binaural_rate = target_rate
            print(f"    ✓ Binaural resampled to {target_rate} Hz")

    sample_rate = voice_rate

    # Determine final duration (use longer of the two)
    voice_duration = len(voice) / sample_rate
    binaural_duration = len(binaural) / sample_rate
    final_duration = max(voice_duration, binaural_duration)
    final_samples = int(final_duration * sample_rate)

    print(f"\n  Final duration: {final_duration/60:.1f} minutes ({final_samples} samples)")

    # Create master mix (start with zeros)
    print("\n2. Creating master mix canvas...")
    master = np.zeros((final_samples, 2), dtype=np.float32)

    # Layer 1: Voice (0 dB, center)
    print("\n3. Adding Layer 1: Voice (0 dB)...")
    voice_adjusted = adjust_volume(voice, 0)  # 0 dB = no change
    master[:len(voice_adjusted)] += voice_adjusted
    print(f"    ✓ Voice added at 0 dB")

    # Layer 2: Binaural beats (-20 dB, stereo)
    print("\n4. Adding Layer 2: Binaural beats (-20 dB)...")
    binaural_adjusted = adjust_volume(binaural, -20)  # Quiet background
    master[:len(binaural_adjusted)] += binaural_adjusted
    print(f"    ✓ Binaural beats added at -20 dB")

    # Layer 3: Effects
    print("\n5. Adding Layer 3: Effects...")

    # 3a. Ambient pad (full duration, -25 dB)
    try:
        print("  Loading ambient pad...")
        pad_rate, pad = load_audio(f"{effects_dir}/ambient_pad.wav")
        if pad_rate != sample_rate:
            print(f"    Warning: Ambient pad sample rate mismatch, skipping")
        else:
            pad_adjusted = adjust_volume(pad, -25)  # Very quiet background
            master[:len(pad_adjusted)] += pad_adjusted
            print(f"    ✓ Ambient pad added at -25 dB (full duration)")
    except Exception as e:
        print(f"    ✗ Could not load ambient pad: {e}")

    # 3b. Gamma burst at 18:45 (1125 seconds)
    gamma_time = 1125.0  # 18 minutes 45 seconds
    try:
        print(f"  Loading gamma burst (placing at {gamma_time/60:.2f} min)...")
        gamma_rate, gamma = load_audio(f"{effects_dir}/gamma_burst_noise.wav")
        if gamma_rate != sample_rate:
            print(f"    Warning: Gamma burst sample rate mismatch, skipping")
        else:
            gamma_adjusted = adjust_volume(gamma, -8)  # Noticeable but not overwhelming
            overlay_audio(master, gamma_adjusted, gamma_time, sample_rate)
            print(f"    ✓ Gamma burst added at 18:45 (-8 dB)")
    except Exception as e:
        print(f"    ✗ Could not load gamma burst: {e}")

    # 3c. Crystal bell at key moments (optional)
    bell_moments = [
        (180, "End of pre-talk"),           # 3:00
        (480, "Deeper into induction"),     # 8:00
        (720, "Neural garden arrival"),     # 12:00
        (1260, "After gamma burst"),        # 21:00
        (1560, "Consolidation"),            # 26:00
    ]

    try:
        print(f"  Loading crystal bell...")
        bell_rate, bell = load_audio(f"{effects_dir}/crystal_bell.wav")
        if bell_rate != sample_rate:
            print(f"    Warning: Crystal bell sample rate mismatch, skipping")
        else:
            bell_adjusted = adjust_volume(bell, -15)  # Subtle accent
            for timestamp, description in bell_moments:
                overlay_audio(master, bell_adjusted, timestamp, sample_rate)
            print(f"    ✓ Crystal bell added at {len(bell_moments)} moments (-15 dB)")
    except Exception as e:
        print(f"    ✗ Could not load crystal bell: {e}")

    # Normalize and apply gentle compression
    print("\n6. Normalizing and applying gentle compression...")

    # Find peak level
    peak = np.max(np.abs(master))
    print(f"  Peak level: {peak:.3f}")

    # Gentle compression (soft knee at -6 dB)
    threshold = 0.5  # -6 dB in linear
    ratio = 2.0      # 2:1 compression

    for i in range(len(master)):
        for channel in range(2):
            sample = master[i, channel]
            abs_sample = abs(sample)

            if abs_sample > threshold:
                # Amount above threshold
                excess = abs_sample - threshold

                # Compress the excess
                compressed_excess = excess / ratio

                # New sample value
                new_abs = threshold + compressed_excess
                master[i, channel] = new_abs if sample >= 0 else -new_abs

    # Normalize to -1 dB headroom
    target_level = 0.891  # -1 dB in linear (10^(-1/20))
    current_peak = np.max(np.abs(master))
    if current_peak > 0:
        master = master * (target_level / current_peak)

    print(f"  Compressed and normalized to -1 dB")

    # Export
    print("\n7. Exporting master audio...")
    output_path = f"{working_dir}/audio_mix_master.wav"

    # Convert to 16-bit PCM
    master_int16 = (master * 32767).astype(np.int16)

    wavfile.write(output_path, sample_rate, master_int16)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    duration_min = len(master) / sample_rate / 60

    print(f"\n✓ Master audio mix complete!")
    print(f"  Output: {output_path}")
    print(f"  Duration: {duration_min:.1f} minutes")
    print(f"  Size: {file_size:.1f} MB")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Channels: Stereo")

    print("\n" + "=" * 60)
    print("Next: Generate gradient backgrounds for video")
    print("=" * 60)

    return 0

if __name__ == '__main__':
    exit(mix_audio())
