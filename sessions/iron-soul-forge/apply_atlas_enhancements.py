#!/usr/bin/env python3
"""
IRON SOUL FORGE - ATLAS-Style Hypnotic Enhancement

Applies the full triple-layered hypnotic presence from ATLAS Starship:
1. Tape warmth (soft saturation)
2. De-essing (sibilance reduction)
3. Whisper overlay - Layer 2: ethereal presence above (HPF + reverb)
4. Subharmonic layer - Layer 3: grounding presence below (LPF + delay)
5. Double-voice layer (phase-shifted subliminal)
6. Room tone (small room impulse response)
7. Cuddle waves (gentle amplitude modulation)

Then applies professional mastering:
- LUFS normalization to -14
- Warmth & presence EQ
- Stereo enhancement
- True peak limiting
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
import subprocess
import os
import sys

# Constants
SAMPLE_RATE = 48000

# Paths
SESSION_DIR = "/home/rsalars/Projects/dreamweaving/sessions/iron-soul-forge"
INPUT_FILE = f"{SESSION_DIR}/output/session_mixed_v3.wav"
OUTPUT_DIR = f"{SESSION_DIR}/output"

# Enhancement settings (from ATLAS manifest)
WARMTH_DRIVE = 0.25
WHISPER_DB = -22
SUBHARMONIC_DB = -12
DOUBLE_DB = -14
DOUBLE_DELAY_MS = 8
ROOM_AMOUNT = 0.03
CUDDLE_FREQUENCY = 0.05  # Hz (one cycle per 20 seconds)
CUDDLE_DEPTH_DB = 1.5

# Echo settings (subtle hypnotic delay)
ECHO_DELAY_MS = 180  # Primary echo delay
ECHO_DECAY = 0.25    # Echo volume (25% of original)
ECHO_FEEDBACK = 0.15 # Feedback for secondary echoes


def db_to_linear(db):
    """Convert dB to linear amplitude"""
    return 10 ** (db / 20)


def linear_to_db(linear):
    """Convert linear amplitude to dB"""
    return 20 * np.log10(np.maximum(linear, 1e-10))


def load_audio(filepath):
    """Load audio file and normalize to float32"""
    print(f"\n📥 Loading: {filepath}")

    # Convert to WAV if needed
    if filepath.endswith('.mp3'):
        temp_wav = filepath.replace('.mp3', '_temp.wav')
        subprocess.run([
            'ffmpeg', '-y', '-i', filepath,
            '-ar', str(SAMPLE_RATE), '-ac', '2',
            '-acodec', 'pcm_s16le', temp_wav
        ], capture_output=True)
        filepath = temp_wav

    rate, audio = wavfile.read(filepath)

    # Normalize based on dtype
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    elif audio.dtype == np.int32:
        audio = audio.astype(np.float32) / 2147483648.0
    else:
        audio = audio.astype(np.float32)

    # Ensure stereo
    if len(audio.shape) == 1:
        audio = np.stack([audio, audio], axis=1)

    duration = len(audio) / rate
    print(f"  ✓ Loaded: {duration:.1f}s at {rate}Hz stereo")

    return audio, rate


def apply_warmth(audio, drive=0.25):
    """Apply tape saturation warmth using soft clipping"""
    print("  🔥 Applying tape warmth...")

    # Soft saturation using tanh
    gain = 1 + drive * 2
    saturated = np.tanh(audio * gain) / np.tanh(gain)

    # Blend with original (30-70% wet based on drive)
    blend = 0.3 + drive * 0.4
    output = audio * (1 - blend) + saturated * blend

    return output


def apply_deessing(audio, sample_rate):
    """Reduce harsh sibilants (4-8 kHz)"""
    print("  🎤 Applying de-essing...")

    nyq = sample_rate / 2

    # Design bandpass for sibilance detection (4-8 kHz)
    b_detect, a_detect = signal.butter(2, [4000/nyq, 8000/nyq], btype='band')

    # Detect sibilance energy on left channel
    sibilance = signal.filtfilt(b_detect, a_detect, audio[:, 0])
    sibilance_env = np.abs(signal.hilbert(sibilance))

    # Smooth envelope (10ms)
    smooth_samples = int(0.01 * sample_rate)
    sibilance_env = np.convolve(sibilance_env, np.ones(smooth_samples)/smooth_samples, mode='same')

    # Calculate gain reduction (threshold-based)
    threshold = np.percentile(sibilance_env, 90) * 0.5
    gain_reduction = np.where(
        sibilance_env > threshold,
        threshold / (sibilance_env + 1e-10),
        1.0
    )
    gain_reduction = np.clip(gain_reduction, 0.3, 1.0)  # Max 10dB reduction

    # Apply to sibilant frequencies only
    b_cut, a_cut = signal.butter(2, [3000/nyq, 10000/nyq], btype='band')

    output = np.zeros_like(audio)
    for ch in range(2):
        sibilant_band = signal.filtfilt(b_cut, a_cut, audio[:, ch])
        other_bands = audio[:, ch] - sibilant_band
        output[:, ch] = other_bands + sibilant_band * gain_reduction

    return output


def create_whisper_layer(audio, sample_rate, level_db=-22):
    """
    Create ethereal high-frequency whisper layer (Layer 2)
    HPF above 2kHz + reverb diffusion
    """
    print("  👻 Creating whisper overlay (Layer 2: ethereal presence)...")

    nyq = sample_rate / 2

    # High-pass filter (above 2kHz)
    b_hp, a_hp = signal.butter(3, 2000/nyq, btype='high')

    whisper = np.zeros_like(audio)
    for ch in range(2):
        whisper[:, ch] = signal.filtfilt(b_hp, a_hp, audio[:, ch])

    # Add reverb-like diffusion
    reverb_length = int(0.8 * sample_rate)
    decay = np.exp(-np.linspace(0, 4, reverb_length))
    ir = np.random.randn(reverb_length) * decay * 0.1

    for ch in range(2):
        whisper[:, ch] = signal.fftconvolve(whisper[:, ch], ir, mode='same')

    # Apply level
    whisper *= db_to_linear(level_db)

    print(f"      Level: {level_db} dB")
    return whisper


def create_subharmonic_layer(audio, sample_rate, level_db=-12):
    """
    Create warm bass foundation layer (Layer 3)
    LPF below 400Hz + slight delay for warmth
    """
    print("  🔊 Creating subharmonic layer (Layer 3: grounding presence)...")

    nyq = sample_rate / 2

    # Low-pass filter (below 400 Hz)
    b_lp, a_lp = signal.butter(3, 400/nyq, btype='low')

    sub = np.zeros_like(audio)
    for ch in range(2):
        sub[:, ch] = signal.filtfilt(b_lp, a_lp, audio[:, ch])

    # Add slight delay (15ms creates warmth without echo)
    delay_samples = int(0.015 * sample_rate)
    sub = np.roll(sub, delay_samples, axis=0)
    sub[:delay_samples] = 0

    # Apply level
    sub *= db_to_linear(level_db)

    print(f"      Level: {level_db} dB, Delay: 15ms")
    return sub


def create_double_voice(audio, sample_rate, level_db=-14, delay_ms=8):
    """
    Create phase-shifted subliminal double
    Slight delay + stereo offset for width
    """
    print("  🎭 Creating double-voice layer (subliminal presence)...")

    delay_samples = int(delay_ms * sample_rate / 1000)

    # Delay the audio
    double = np.roll(audio, delay_samples, axis=0)
    double[:delay_samples] = 0

    # Slight stereo offset for width (±5 samples)
    double[:, 0] = np.roll(double[:, 0], 5)
    double[:, 1] = np.roll(double[:, 1], -5)

    # Apply level
    double *= db_to_linear(level_db)

    print(f"      Level: {level_db} dB, Delay: {delay_ms}ms")
    return double


def add_room_tone(audio, sample_rate, amount=0.03):
    """
    Add subtle room impulse response
    Early reflections at 10/20/35ms for physical presence
    """
    print("  🏠 Adding room tone...")

    # Simple room IR (small room simulation)
    room_length = int(0.3 * sample_rate)  # 300ms room
    t = np.linspace(0, 0.3, room_length)

    # Early reflections
    ir = np.zeros(room_length)
    ir[int(0.01 * sample_rate)] = 0.5   # 10ms
    ir[int(0.02 * sample_rate)] = 0.3   # 20ms
    ir[int(0.035 * sample_rate)] = 0.2  # 35ms

    # Diffuse tail
    ir += np.random.randn(room_length) * np.exp(-t * 10) * 0.1

    room = np.zeros_like(audio)
    for ch in range(2):
        room[:, ch] = signal.fftconvolve(audio[:, ch], ir, mode='same')

    # Blend
    output = audio * (1 - amount) + room * amount

    print(f"      Wet mix: {amount*100:.0f}%")
    return output


def apply_cuddle_waves(audio, sample_rate, freq=0.05, depth_db=1.5):
    """
    Apply gentle amplitude modulation for 'rocking' sensation
    Very slow sine wave modulation (one cycle per 20 seconds)
    """
    print("  🌊 Applying cuddle waves (amplitude modulation)...")

    duration = len(audio) / sample_rate
    t = np.linspace(0, duration, len(audio), False)

    # Very slow sine modulation
    modulation = 1 + (db_to_linear(depth_db) - 1) * np.sin(2 * np.pi * freq * t)

    output = audio * modulation[:, np.newaxis]

    print(f"      Frequency: {freq} Hz, Depth: ±{depth_db} dB")
    return output


def apply_echo(audio, sample_rate, delay_ms=180, decay=0.25, feedback=0.15):
    """
    Apply subtle hypnotic echo/delay effect
    Creates dreamy, spacious quality without muddying the voice
    """
    print("  🔊 Applying subtle echo...")

    delay_samples = int(delay_ms * sample_rate / 1000)

    # Create output buffer
    output = audio.copy()

    # Apply multi-tap echo with feedback
    echo_level = decay
    current_delay = delay_samples

    for _ in range(3):  # 3 echo taps
        if current_delay >= len(audio):
            break

        # Create delayed version
        delayed = np.zeros_like(audio)
        delayed[current_delay:] = audio[:-current_delay] * echo_level

        # Add to output
        output += delayed

        # Prepare next tap (feedback reduces each iteration)
        echo_level *= feedback
        current_delay += delay_samples

    print(f"      Delay: {delay_ms}ms, Decay: {decay*100:.0f}%, Feedback: {feedback*100:.0f}%")
    return output


def normalize_rms(audio, target_db=-16):
    """Normalize audio to target RMS level"""
    rms = np.sqrt(np.mean(audio ** 2))
    current_db = linear_to_db(rms)
    gain = db_to_linear(target_db - current_db)
    return audio * gain


def apply_mastering_chain(input_path, output_path):
    """Apply final mastering using FFmpeg"""
    print("\n🎚️ Applying final mastering chain...")

    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-af', (
            'loudnorm=I=-14:TP=-1.5:LRA=11,'
            'equalizer=f=250:t=h:width=200:g=1.5,'
            'equalizer=f=3000:t=h:width=2000:g=1.0,'
            'highshelf=f=10000:g=-0.5,'
            'stereotools=mlev=0.95:slev=1.05,'
            'alimiter=limit=0.9:attack=5:release=50'
        ),
        '-c:a', 'libmp3lame', '-b:a', '320k',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("  ✓ Mastering complete")
        return True
    else:
        print(f"  ✗ Mastering failed: {result.stderr}")
        return False


def main():
    print("=" * 70)
    print("IRON SOUL FORGE - ATLAS-Style Hypnotic Enhancement")
    print("=" * 70)
    print("\nApplying triple-layered hypnotic presence:")
    print("  Layer 1: Main voice (enhanced)")
    print("  Layer 2: Whisper overlay (ethereal)")
    print("  Layer 3: Subharmonic warm (grounding)")
    print("  + Double-voice, room tone, cuddle waves, echo")

    # Load input
    audio, rate = load_audio(INPUT_FILE)
    duration = len(audio) / rate

    print(f"\n✨ VOICE ENHANCEMENT")
    print("=" * 50)

    # Step 1: Tape warmth
    audio = apply_warmth(audio, WARMTH_DRIVE)

    # Step 2: De-essing
    audio = apply_deessing(audio, rate)

    # Step 3: Create enhancement layers
    whisper = create_whisper_layer(audio, rate, WHISPER_DB)
    subharmonic = create_subharmonic_layer(audio, rate, SUBHARMONIC_DB)
    double = create_double_voice(audio, rate, DOUBLE_DB, DOUBLE_DELAY_MS)

    # Step 4: Combine all layers
    print("\n  🎚️ Combining triple-layer presence...")
    enhanced = audio + whisper + subharmonic + double
    print("      Main voice + Whisper + Subharmonic + Double")

    # Step 5: Room tone
    enhanced = add_room_tone(enhanced, rate, ROOM_AMOUNT)

    # Step 6: Cuddle waves
    enhanced = apply_cuddle_waves(enhanced, rate, CUDDLE_FREQUENCY, CUDDLE_DEPTH_DB)

    # Step 7: Echo
    enhanced = apply_echo(enhanced, rate, ECHO_DELAY_MS, ECHO_DECAY, ECHO_FEEDBACK)

    # Step 8: Normalize
    print("\n  📊 Normalizing levels...")
    enhanced = normalize_rms(enhanced, -16)

    # Prevent clipping
    peak = np.max(np.abs(enhanced))
    if peak > 0.95:
        enhanced = enhanced * (0.95 / peak)
        print(f"      Applied headroom reduction: {linear_to_db(0.95/peak):.1f} dB")

    # Save intermediate WAV
    temp_wav = f"{OUTPUT_DIR}/iron-soul-forge-enhanced-temp.wav"
    print(f"\n💾 Saving intermediate: {temp_wav}")
    audio_16bit = (np.clip(enhanced, -1, 1) * 32767).astype(np.int16)
    wavfile.write(temp_wav, rate, audio_16bit)

    # Apply final mastering
    final_output = f"{OUTPUT_DIR}/iron-soul-forge-atlas-enhanced.mp3"
    success = apply_mastering_chain(temp_wav, final_output)

    # Cleanup
    if os.path.exists(temp_wav):
        os.remove(temp_wav)

    if success:
        # Get file info
        file_size = os.path.getsize(final_output) / (1024 * 1024)

        print("\n" + "=" * 70)
        print("✅ ENHANCEMENT COMPLETE!")
        print("=" * 70)
        print(f"\n📋 Output Summary:")
        print(f"   Duration: {duration/60:.1f} minutes")
        print(f"   Sample rate: {rate} Hz")
        print(f"   Format: 320kbps MP3")
        print(f"   Size: {file_size:.1f} MB")
        print(f"\n🎧 Output: {final_output}")
        print(f"\n🎚️ Enhancements Applied:")
        print(f"   ✓ Tape warmth (drive: {WARMTH_DRIVE})")
        print(f"   ✓ De-essing (4-8 kHz reduction)")
        print(f"   ✓ Whisper overlay ({WHISPER_DB} dB) - ethereal presence")
        print(f"   ✓ Subharmonic layer ({SUBHARMONIC_DB} dB) - grounding presence")
        print(f"   ✓ Double-voice ({DOUBLE_DB} dB, {DOUBLE_DELAY_MS}ms)")
        print(f"   ✓ Room tone ({ROOM_AMOUNT*100:.0f}% wet)")
        print(f"   ✓ Cuddle waves ({CUDDLE_FREQUENCY} Hz, ±{CUDDLE_DEPTH_DB} dB)")
        print(f"   ✓ Echo ({ECHO_DELAY_MS}ms, {ECHO_DECAY*100:.0f}% decay)")
        print(f"   ✓ LUFS normalization (-14 LUFS)")
        print(f"   ✓ Warmth & presence EQ")
        print(f"   ✓ Stereo enhancement (5%)")
        print(f"   ✓ True peak limiting (-1.5 dBTP)")
    else:
        print("\n✗ Enhancement failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
