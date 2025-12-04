#!/usr/bin/env python3
"""
DREAMWEAVING - Hypnotic Post-Processing & Mastering

Unified psychoacoustic enhancement pipeline for hypnotic audio sessions.
Combines techniques from ATLAS Starship, Iron Soul Forge, and Garden of Eden.

TRIPLE-LAYER HYPNOTIC PRESENCE:
  Layer 1: Main voice (warmth + de-essing)
  Layer 2: Whisper overlay (ethereal high-frequency presence)
  Layer 3: Subharmonic warm (grounding bass foundation)

ADDITIONAL ENHANCEMENTS:
  - Double-voice (phase-shifted subliminal layer)
  - Room tone (intimate space reverb)
  - Cuddle waves (gentle amplitude rocking)
  - Echo (dreamy spatial depth)

FINAL MASTERING:
  - LUFS normalization (-14 LUFS for YouTube)
  - Warmth & presence EQ
  - Stereo enhancement
  - True peak limiting (-1.5 dBTP)

Usage:
    python3 hypnotic_post_process.py <input.wav> <output_name> [options]

    # Process session_mixed.wav to final master
    python3 hypnotic_post_process.py session_mixed.wav my_session_MASTER

    # Custom enhancement settings
    python3 hypnotic_post_process.py input.wav output --warmth 0.3 --echo-delay 200

    # Process a full session directory
    python3 hypnotic_post_process.py --session sessions/neural-network-navigator/
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
import subprocess
import os
import sys
import argparse
import gc
import traceback
from pathlib import Path

# Memory management for large files
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)


# =============================================================================
# DEFAULT ENHANCEMENT SETTINGS
# =============================================================================

DEFAULTS = {
    # Tape warmth
    'warmth_drive': 0.25,         # 0.0-1.0, higher = more saturation

    # De-essing
    'deess_enabled': True,

    # Whisper overlay (Layer 2: ethereal)
    'whisper_enabled': True,
    'whisper_db': -22,            # Level relative to voice

    # Subharmonic (Layer 3: grounding)
    'subharmonic_enabled': True,
    'subharmonic_db': -12,        # Level relative to voice

    # Double voice (subliminal)
    'double_enabled': True,
    'double_db': -14,             # Level relative to voice
    'double_delay_ms': 8,         # Phase shift delay

    # Room tone
    'room_enabled': True,
    'room_amount': 0.04,          # 0.0-1.0, wet mix percentage

    # Cuddle waves (amplitude modulation)
    'cuddle_enabled': True,
    'cuddle_freq': 0.05,          # Hz (one cycle per 20 seconds)
    'cuddle_depth_db': 1.5,       # Modulation depth

    # Echo (dreamy spatial)
    'echo_enabled': True,
    'echo_delay_ms': 180,         # Primary echo delay
    'echo_decay': 0.25,           # Echo volume (25% of original)
    'echo_feedback': 0.15,        # Feedback for secondary echoes

    # Mastering
    'target_lufs': -14,           # YouTube standard
    'true_peak_dbtp': -1.5,       # True peak ceiling
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def db_to_linear(db):
    """Convert dB to linear amplitude"""
    return 10 ** (db / 20)


def linear_to_db(linear):
    """Convert linear amplitude to dB"""
    return 20 * np.log10(np.maximum(linear, 1e-10))


def calculate_rms(audio):
    """Calculate RMS level of audio"""
    return np.sqrt(np.mean(audio ** 2))


def normalize_rms(audio, target_db=-16):
    """Normalize audio to target RMS level"""
    rms = calculate_rms(audio)
    current_db = linear_to_db(rms)
    gain = db_to_linear(target_db - current_db)
    return audio * gain


# =============================================================================
# AUDIO LOADING
# =============================================================================

def load_audio(filepath, sample_rate=48000):
    """Load audio file and normalize to float32 stereo"""
    print(f"\n📥 Loading: {os.path.basename(filepath)}")

    filepath = str(filepath)

    # Convert to WAV at target sample rate if needed
    if filepath.endswith('.mp3') or filepath.endswith('.wav'):
        temp_wav = filepath.replace('.mp3', '').replace('.wav', '') + '_temp_load.wav'
        subprocess.run([
            'ffmpeg', '-y', '-i', filepath,
            '-ar', str(sample_rate), '-ac', '2',
            '-acodec', 'pcm_s16le', temp_wav
        ], capture_output=True)
        load_path = temp_wav
    else:
        load_path = filepath

    rate, audio = wavfile.read(load_path)

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

    # Cleanup temp file
    if 'temp_load' in load_path and os.path.exists(load_path):
        os.remove(load_path)

    duration = len(audio) / sample_rate
    print(f"  ✓ Loaded: {duration:.1f}s ({duration/60:.1f} min) at {sample_rate}Hz stereo")

    return audio, sample_rate, duration


# =============================================================================
# ENHANCEMENT FUNCTIONS
# =============================================================================

def apply_warmth(audio, drive=0.25):
    """
    Apply tape saturation warmth using soft clipping.
    Creates analog-style harmonic richness.
    """
    print("  🔥 Applying tape warmth...")

    # Soft saturation using tanh
    gain = 1 + drive * 2
    saturated = np.tanh(audio * gain) / np.tanh(gain)

    # Blend with original (30-70% wet based on drive)
    blend = 0.3 + drive * 0.4
    output = audio * (1 - blend) + saturated * blend

    print(f"      Drive: {drive*100:.0f}%, Blend: {blend*100:.0f}%")
    return output


def apply_deessing(audio, sample_rate):
    """
    Reduce harsh sibilants (4-8 kHz).
    Dynamic gain reduction on sibilant frequencies only.
    """
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
    Create ethereal high-frequency whisper layer (Layer 2).
    HPF above 2kHz + reverb diffusion for spirit-double effect.
    """
    print("  👻 Creating whisper overlay (Layer 2: ethereal presence)...")

    nyq = sample_rate / 2

    # High-pass filter (above 2kHz)
    b_hp, a_hp = signal.butter(3, 2000/nyq, btype='high')

    whisper = np.zeros_like(audio)
    for ch in range(2):
        whisper[:, ch] = signal.filtfilt(b_hp, a_hp, audio[:, ch])

    # Add reverb-like diffusion (800ms decay)
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
    Create warm bass foundation layer (Layer 3).
    LPF below 400Hz + slight delay for grounding presence.
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
    Create phase-shifted subliminal double.
    Slight delay + stereo offset for hypnotic width.
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


def add_room_tone(audio, sample_rate, amount=0.04):
    """
    Add subtle room impulse response.
    Early reflections at 10/20/35ms for intimate physical presence.
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


def apply_cuddle_waves(audio, sample_rate, duration, freq=0.05, depth_db=1.5):
    """
    Apply gentle amplitude modulation for 'rocking' sensation.
    Very slow sine wave creates hypnotic comfort response.
    """
    print("  🌊 Applying cuddle waves (amplitude modulation)...")

    t = np.linspace(0, duration, len(audio), False)

    # Very slow sine modulation
    modulation = 1 + (db_to_linear(depth_db) - 1) * np.sin(2 * np.pi * freq * t)

    output = audio * modulation[:, np.newaxis]

    print(f"      Frequency: {freq} Hz ({1/freq:.0f}s cycle), Depth: ±{depth_db} dB")
    return output


def apply_echo(audio, sample_rate, delay_ms=180, decay=0.25, feedback=0.15):
    """
    Apply subtle hypnotic echo/delay effect.
    Creates dreamy, spacious quality for trance induction.
    Multi-tap with feedback for natural decay.
    """
    print("  🔊 Applying subtle echo...")

    delay_samples = int(delay_ms * sample_rate / 1000)

    # Create output buffer
    output = audio.copy()

    # Apply multi-tap echo with feedback
    echo_level = decay
    current_delay = delay_samples

    for tap in range(3):  # 3 echo taps
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


# =============================================================================
# MASTERING CHAIN
# =============================================================================

def apply_mastering_chain(input_path, output_wav, output_mp3, target_lufs=-14, true_peak=-1.5):
    """
    Apply final mastering using FFmpeg:
    - LUFS normalization
    - Warmth & presence EQ
    - Stereo enhancement
    - True peak limiting
    """
    print("\n🎚️ FINAL MASTERING")
    print("=" * 60)

    # Build filter chain
    filters = [
        f'loudnorm=I={target_lufs}:TP={true_peak}:LRA=11',
        'equalizer=f=250:t=h:width=200:g=1.5',     # Warmth
        'equalizer=f=3000:t=h:width=2000:g=1.0',   # Presence
        'highshelf=f=10000:g=-0.5',                # Smooth highs
        'stereotools=mlev=0.95:slev=1.05',         # 5% stereo width
        'alimiter=limit=0.9:attack=5:release=50'   # Safety limiter
    ]

    filter_string = ','.join(filters)

    print(f"  📊 Target: {target_lufs} LUFS, {true_peak} dBTP")
    print("  🎛️ EQ: +1.5dB@250Hz, +1dB@3kHz, -0.5dB>10kHz")
    print("  🔊 Stereo: +5% width")
    print("  🔒 Limiter: 0.9 ceiling")

    # Create 24-bit WAV
    print(f"\n  💾 Creating 24-bit WAV...")
    cmd_wav = [
        'ffmpeg', '-y', '-i', str(input_path),
        '-af', filter_string,
        '-c:a', 'pcm_s24le', '-ar', '48000',
        str(output_wav)
    ]
    result_wav = subprocess.run(cmd_wav, capture_output=True, text=True)

    # Create 320kbps MP3
    print(f"  💾 Creating 320kbps MP3...")
    cmd_mp3 = [
        'ffmpeg', '-y', '-i', str(input_path),
        '-af', filter_string,
        '-c:a', 'libmp3lame', '-b:a', '320k',
        str(output_mp3)
    ]
    result_mp3 = subprocess.run(cmd_mp3, capture_output=True, text=True)

    if result_wav.returncode == 0 and result_mp3.returncode == 0:
        wav_size = os.path.getsize(output_wav) / (1024 * 1024)
        mp3_size = os.path.getsize(output_mp3) / (1024 * 1024)
        print(f"\n  ✓ {output_wav} ({wav_size:.1f} MB)")
        print(f"  ✓ {output_mp3} ({mp3_size:.1f} MB)")
        return True
    else:
        print(f"  ✗ Mastering failed")
        if result_wav.returncode != 0:
            print(f"    WAV error: {result_wav.stderr[:200]}")
        if result_mp3.returncode != 0:
            print(f"    MP3 error: {result_mp3.stderr[:200]}")
        return False


# =============================================================================
# MAIN PROCESSING PIPELINE
# =============================================================================

def process_audio(
    input_path,
    output_name,
    output_dir=None,
    settings=None
):
    """
    Main hypnotic post-processing pipeline.

    Args:
        input_path: Path to input audio file (WAV or MP3)
        output_name: Base name for output files (without extension)
        output_dir: Output directory (default: same as input)
        settings: Dict of enhancement settings (uses DEFAULTS if not provided)

    Returns:
        Tuple of (wav_path, mp3_path) on success, None on failure
    """
    # Merge settings with defaults
    cfg = DEFAULTS.copy()
    if settings:
        cfg.update(settings)

    # Resolve paths
    input_path = Path(input_path)
    if output_dir is None:
        output_dir = input_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🧠 DREAMWEAVING - Hypnotic Post-Processing")
    print("=" * 70)
    print("\nTriple-Layer Hypnotic Presence:")
    print("  Layer 1: Main voice (warmth + de-essing)")
    print("  Layer 2: Whisper overlay (ethereal)")
    print("  Layer 3: Subharmonic warm (grounding)")
    print("  + Double-voice, room tone, cuddle waves, echo")

    # Load audio
    audio, sample_rate, duration = load_audio(input_path)

    print(f"\n✨ HYPNOTIC ENHANCEMENT")
    print("=" * 60)

    # Step 1: Tape warmth
    audio = apply_warmth(audio, cfg['warmth_drive'])

    # Step 2: De-essing
    if cfg['deess_enabled']:
        audio = apply_deessing(audio, sample_rate)

    # Step 3: Create enhancement layers
    layers = []

    if cfg['whisper_enabled']:
        whisper = create_whisper_layer(audio, sample_rate, cfg['whisper_db'])
        layers.append(('whisper', whisper))

    if cfg['subharmonic_enabled']:
        subharmonic = create_subharmonic_layer(audio, sample_rate, cfg['subharmonic_db'])
        layers.append(('subharmonic', subharmonic))

    if cfg['double_enabled']:
        double = create_double_voice(audio, sample_rate, cfg['double_db'], cfg['double_delay_ms'])
        layers.append(('double', double))

    # Step 4: Combine all layers
    print("\n  🎚️ Combining triple-layer presence...")
    enhanced = audio.copy()
    for name, layer in layers:
        enhanced += layer
    print(f"      Main voice + {' + '.join([l[0] for l in layers])}")

    # Step 5: Room tone
    if cfg['room_enabled']:
        enhanced = add_room_tone(enhanced, sample_rate, cfg['room_amount'])

    # Step 6: Cuddle waves
    if cfg['cuddle_enabled']:
        enhanced = apply_cuddle_waves(
            enhanced, sample_rate, duration,
            cfg['cuddle_freq'], cfg['cuddle_depth_db']
        )

    # Step 7: Echo
    if cfg['echo_enabled']:
        enhanced = apply_echo(
            enhanced, sample_rate,
            cfg['echo_delay_ms'], cfg['echo_decay'], cfg['echo_feedback']
        )

    # Step 8: Normalize
    print("\n  📊 Pre-master normalization...")
    enhanced = normalize_rms(enhanced, -16)

    # Prevent clipping
    peak = np.max(np.abs(enhanced))
    if peak > 0.95:
        enhanced = enhanced * (0.95 / peak)
        print(f"      Applied headroom: {linear_to_db(0.95/peak):.1f} dB")

    # Save intermediate WAV
    temp_wav = output_dir / f"{output_name}_temp.wav"
    print(f"\n💾 Saving intermediate: {temp_wav.name}")
    audio_16bit = (np.clip(enhanced, -1, 1) * 32767).astype(np.int16)
    wavfile.write(str(temp_wav), sample_rate, audio_16bit)

    # Final mastering
    output_wav = output_dir / f"{output_name}.wav"
    output_mp3 = output_dir / f"{output_name}.mp3"

    success = apply_mastering_chain(
        temp_wav, output_wav, output_mp3,
        cfg['target_lufs'], cfg['true_peak_dbtp']
    )

    # Cleanup temp file
    if temp_wav.exists():
        temp_wav.unlink()

    if success:
        print("\n" + "=" * 70)
        print("✅ HYPNOTIC POST-PROCESSING COMPLETE!")
        print("=" * 70)
        print(f"\n📋 Output Summary:")
        print(f"   Duration: {duration/60:.1f} minutes")
        print(f"   Sample rate: {sample_rate} Hz")

        print(f"\n🎧 Enhancements Applied:")
        print(f"   ✓ Tape warmth ({cfg['warmth_drive']*100:.0f}%)")
        if cfg['deess_enabled']:
            print(f"   ✓ De-essing (4-8 kHz)")
        if cfg['whisper_enabled']:
            print(f"   ✓ Whisper overlay ({cfg['whisper_db']} dB)")
        if cfg['subharmonic_enabled']:
            print(f"   ✓ Subharmonic ({cfg['subharmonic_db']} dB)")
        if cfg['double_enabled']:
            print(f"   ✓ Double-voice ({cfg['double_db']} dB, {cfg['double_delay_ms']}ms)")
        if cfg['room_enabled']:
            print(f"   ✓ Room tone ({cfg['room_amount']*100:.0f}%)")
        if cfg['cuddle_enabled']:
            print(f"   ✓ Cuddle waves ({cfg['cuddle_freq']} Hz, ±{cfg['cuddle_depth_db']} dB)")
        if cfg['echo_enabled']:
            print(f"   ✓ Echo ({cfg['echo_delay_ms']}ms, {cfg['echo_decay']*100:.0f}%)")

        print(f"\n🎚️ Mastering:")
        print(f"   ✓ LUFS: {cfg['target_lufs']} LUFS")
        print(f"   ✓ True peak: {cfg['true_peak_dbtp']} dBTP")
        print(f"   ✓ Warmth & presence EQ")
        print(f"   ✓ Stereo enhancement (5%)")

        print(f"\n📁 Output Files:")
        print(f"   {output_wav}")
        print(f"   {output_mp3}")

        return output_wav, output_mp3
    else:
        print("\n✗ Post-processing failed!")
        return None


# =============================================================================
# LIGHTWEIGHT FFmpeg-ONLY PROCESSING (LOW MEMORY)
# =============================================================================

def process_audio_ffmpeg_only(input_path, output_name, output_dir, settings=None):
    """
    Lightweight post-processing using FFmpeg only.
    Avoids loading entire file into Python memory.
    Good for long sessions (>30 min) or low-memory systems.
    """
    cfg = DEFAULTS.copy()
    if settings:
        cfg.update(settings)

    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_wav = output_dir / f"{output_name}.wav"
    output_mp3 = output_dir / f"{output_name}.mp3"

    print("=" * 70)
    print("🧠 DREAMWEAVING - Hypnotic Post-Processing (FFmpeg Mode)")
    print("=" * 70)
    print("\n⚡ Using lightweight FFmpeg-only processing")
    print("   (Lower memory usage, suitable for long sessions)")

    # Get duration
    try:
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', str(input_path)]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        print(f"\n📥 Input: {input_path.name}")
        print(f"   Duration: {duration/60:.1f} minutes")
    except Exception as e:
        print(f"   Warning: Could not get duration: {e}")
        duration = 0

    # Build FFmpeg filter chain
    filters = []

    # Warmth (soft saturation approximation)
    if cfg['warmth_drive'] > 0:
        # Use compressor + bass boost for warmth
        filters.append(f"acompressor=threshold=-20dB:ratio=4:attack=10:release=100:makeup=2")
        filters.append(f"equalizer=f=200:t=h:width=200:g={cfg['warmth_drive']*3}")
        print(f"   ✓ Warmth: {cfg['warmth_drive']*100:.0f}%")

    # De-essing (high-frequency reduction on peaks)
    if cfg['deess_enabled']:
        filters.append("highshelf=f=6000:g=-2")
        print("   ✓ De-essing")

    # Room tone (small reverb)
    if cfg['room_enabled'] and cfg['room_amount'] > 0:
        # FFmpeg doesn't have built-in reverb, use chorus for space
        filters.append(f"chorus=0.5:0.9:50|60:0.4|0.32:0.25|0.4:2|1.3")
        print(f"   ✓ Room tone: {cfg['room_amount']*100:.0f}%")

    # Echo
    if cfg['echo_enabled']:
        delay_ms = cfg['echo_delay_ms']
        decay = cfg['echo_decay']
        filters.append(f"aecho=0.8:0.7:{delay_ms}:{decay}")
        print(f"   ✓ Echo: {delay_ms}ms, {decay*100:.0f}%")

    # Subharmonic boost (low-end warmth)
    if cfg['subharmonic_enabled']:
        filters.append(f"equalizer=f=80:t=h:width=100:g={abs(cfg['subharmonic_db'])/4}")
        print(f"   ✓ Subharmonic boost")

    # Stereo width
    filters.append("stereotools=mlev=0.95:slev=1.05")
    print("   ✓ Stereo enhancement")

    # Mastering chain
    filters.append(f"loudnorm=I={cfg['target_lufs']}:TP={cfg['true_peak_dbtp']}:LRA=11")
    filters.append("equalizer=f=250:t=h:width=200:g=1.5")  # Warmth
    filters.append("equalizer=f=3000:t=h:width=2000:g=1.0")  # Presence
    filters.append("highshelf=f=10000:g=-0.5")  # Smooth highs
    filters.append("alimiter=limit=0.9:attack=5:release=50")  # Safety

    filter_string = ','.join(filters)

    print(f"\n🎚️ MASTERING")
    print(f"   Target: {cfg['target_lufs']} LUFS, {cfg['true_peak_dbtp']} dBTP")

    # Create WAV
    print(f"\n💾 Creating 24-bit WAV...")
    cmd_wav = [
        'ffmpeg', '-y', '-i', str(input_path),
        '-af', filter_string,
        '-c:a', 'pcm_s24le', '-ar', '48000',
        str(output_wav)
    ]

    try:
        result_wav = subprocess.run(cmd_wav, capture_output=True, text=True, timeout=600)
        if result_wav.returncode != 0:
            print(f"   ✗ WAV failed: {result_wav.stderr[:300]}")
            return None
    except subprocess.TimeoutExpired:
        print("   ✗ WAV creation timed out")
        return None
    except Exception as e:
        print(f"   ✗ WAV error: {e}")
        return None

    # Create MP3
    print(f"💾 Creating 320kbps MP3...")
    cmd_mp3 = [
        'ffmpeg', '-y', '-i', str(input_path),
        '-af', filter_string,
        '-c:a', 'libmp3lame', '-b:a', '320k',
        str(output_mp3)
    ]

    try:
        result_mp3 = subprocess.run(cmd_mp3, capture_output=True, text=True, timeout=600)
        if result_mp3.returncode != 0:
            print(f"   ✗ MP3 failed: {result_mp3.stderr[:300]}")
            return None
    except subprocess.TimeoutExpired:
        print("   ✗ MP3 creation timed out")
        return None
    except Exception as e:
        print(f"   ✗ MP3 error: {e}")
        return None

    # Verify outputs
    if output_wav.exists() and output_mp3.exists():
        wav_size = output_wav.stat().st_size / (1024 * 1024)
        mp3_size = output_mp3.stat().st_size / (1024 * 1024)

        print(f"\n" + "=" * 70)
        print("✅ HYPNOTIC POST-PROCESSING COMPLETE!")
        print("=" * 70)
        print(f"\n📁 Output Files:")
        print(f"   {output_wav} ({wav_size:.1f} MB)")
        print(f"   {output_mp3} ({mp3_size:.1f} MB)")

        return output_wav, output_mp3
    else:
        print("   ✗ Output files not created")
        return None


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Dreamweaving Hypnotic Post-Processing & Mastering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python3 hypnotic_post_process.py session_mixed.wav my_session_MASTER

  # Process a session directory (auto-finds session_mixed.wav)
  python3 hypnotic_post_process.py --session sessions/neural-network-navigator/

  # Custom settings
  python3 hypnotic_post_process.py input.wav output --warmth 0.3 --echo-delay 200

  # Minimal processing (voice enhancement only, no echo)
  python3 hypnotic_post_process.py input.wav output --no-echo --no-cuddle
        """
    )

    # Input/Output
    parser.add_argument('input', nargs='?', help='Input audio file (WAV or MP3)')
    parser.add_argument('output', nargs='?', help='Output name (without extension)')
    parser.add_argument('--session', '-s', help='Session directory (auto-process)')
    parser.add_argument('--output-dir', '-o', help='Output directory')

    # Enhancement toggles
    parser.add_argument('--no-deess', action='store_true', help='Disable de-essing')
    parser.add_argument('--no-whisper', action='store_true', help='Disable whisper layer')
    parser.add_argument('--no-subharmonic', action='store_true', help='Disable subharmonic')
    parser.add_argument('--no-double', action='store_true', help='Disable double-voice')
    parser.add_argument('--no-room', action='store_true', help='Disable room tone')
    parser.add_argument('--no-cuddle', action='store_true', help='Disable cuddle waves')
    parser.add_argument('--no-echo', action='store_true', help='Disable echo')

    # Enhancement parameters
    parser.add_argument('--warmth', type=float, help=f'Warmth drive 0-1 (default: {DEFAULTS["warmth_drive"]})')
    parser.add_argument('--whisper-db', type=float, help=f'Whisper level dB (default: {DEFAULTS["whisper_db"]})')
    parser.add_argument('--sub-db', type=float, help=f'Subharmonic level dB (default: {DEFAULTS["subharmonic_db"]})')
    parser.add_argument('--double-db', type=float, help=f'Double-voice level dB (default: {DEFAULTS["double_db"]})')
    parser.add_argument('--double-delay', type=float, help=f'Double-voice delay ms (default: {DEFAULTS["double_delay_ms"]})')
    parser.add_argument('--room', type=float, help=f'Room amount 0-1 (default: {DEFAULTS["room_amount"]})')
    parser.add_argument('--cuddle-freq', type=float, help=f'Cuddle frequency Hz (default: {DEFAULTS["cuddle_freq"]})')
    parser.add_argument('--cuddle-depth', type=float, help=f'Cuddle depth dB (default: {DEFAULTS["cuddle_depth_db"]})')
    parser.add_argument('--echo-delay', type=float, help=f'Echo delay ms (default: {DEFAULTS["echo_delay_ms"]})')
    parser.add_argument('--echo-decay', type=float, help=f'Echo decay 0-1 (default: {DEFAULTS["echo_decay"]})')
    parser.add_argument('--echo-feedback', type=float, help=f'Echo feedback 0-1 (default: {DEFAULTS["echo_feedback"]})')

    # Mastering
    parser.add_argument('--lufs', type=float, help=f'Target LUFS (default: {DEFAULTS["target_lufs"]})')
    parser.add_argument('--peak', type=float, help=f'True peak dBTP (default: {DEFAULTS["true_peak_dbtp"]})')

    # Processing mode
    parser.add_argument('--ffmpeg-only', action='store_true',
                       help='Use lightweight FFmpeg-only processing (lower memory, for long sessions)')

    args = parser.parse_args()

    # Handle session mode
    if args.session:
        session_dir = Path(args.session)
        input_file = session_dir / 'output' / 'session_mixed.wav'
        if not input_file.exists():
            print(f"Error: {input_file} not found")
            sys.exit(1)

        # Extract session name from directory
        session_name = session_dir.name.replace('-', '_')
        output_name = f"{session_name}_MASTER"
        output_dir = session_dir / 'output'

    elif args.input:
        input_file = Path(args.input)
        if not input_file.exists():
            print(f"Error: {input_file} not found")
            sys.exit(1)

        output_name = args.output or input_file.stem + '_MASTER'
        output_dir = Path(args.output_dir) if args.output_dir else input_file.parent
    else:
        parser.print_help()
        sys.exit(1)

    # Build settings
    settings = {}

    # Toggles
    if args.no_deess:
        settings['deess_enabled'] = False
    if args.no_whisper:
        settings['whisper_enabled'] = False
    if args.no_subharmonic:
        settings['subharmonic_enabled'] = False
    if args.no_double:
        settings['double_enabled'] = False
    if args.no_room:
        settings['room_enabled'] = False
    if args.no_cuddle:
        settings['cuddle_enabled'] = False
    if args.no_echo:
        settings['echo_enabled'] = False

    # Parameters
    if args.warmth is not None:
        settings['warmth_drive'] = args.warmth
    if args.whisper_db is not None:
        settings['whisper_db'] = args.whisper_db
    if args.sub_db is not None:
        settings['subharmonic_db'] = args.sub_db
    if args.double_db is not None:
        settings['double_db'] = args.double_db
    if args.double_delay is not None:
        settings['double_delay_ms'] = args.double_delay
    if args.room is not None:
        settings['room_amount'] = args.room
    if args.cuddle_freq is not None:
        settings['cuddle_freq'] = args.cuddle_freq
    if args.cuddle_depth is not None:
        settings['cuddle_depth_db'] = args.cuddle_depth
    if args.echo_delay is not None:
        settings['echo_delay_ms'] = args.echo_delay
    if args.echo_decay is not None:
        settings['echo_decay'] = args.echo_decay
    if args.echo_feedback is not None:
        settings['echo_feedback'] = args.echo_feedback
    if args.lufs is not None:
        settings['target_lufs'] = args.lufs
    if args.peak is not None:
        settings['true_peak_dbtp'] = args.peak

    # Process - choose mode based on --ffmpeg-only flag
    try:
        if args.ffmpeg_only:
            result = process_audio_ffmpeg_only(input_file, output_name, output_dir, settings)
        else:
            result = process_audio(input_file, output_name, output_dir, settings)

        if result is None:
            sys.exit(1)
    except MemoryError:
        print("\n❌ Memory error! Try running with --ffmpeg-only flag for lower memory usage.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
