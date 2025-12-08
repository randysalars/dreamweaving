#!/usr/bin/env python3
"""
DREAMWEAVING - Hypnotic Post-Processing & Mastering

Unified psychoacoustic enhancement pipeline for hypnotic audio sessions.
Combines techniques from ATLAS Starship, Iron Soul Forge, and Garden of Eden.

LAYERED HYPNOTIC PRESENCE:
  Layer 1: Main voice (warmth + de-essing)
  Layer 2: Whisper overlay (ethereal high-frequency presence)
  Layer 3: Subharmonic warm (optional, grounding bass foundation)

ADDITIONAL ENHANCEMENTS (CONFIGURABLE):
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
from typing import Optional, List, Dict

# Local imports for adaptive processing
try:
    from core.audio.adaptive_processing import (
        apply_full_adaptive_processing,
        stages_from_manifest,
        create_anchoring_layer,
        STAGE_PRESETS,
    )
    ADAPTIVE_AVAILABLE = True
except ImportError:
    ADAPTIVE_AVAILABLE = False

# Memory management for large files
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)


# =============================================================================
# DEFAULT ENHANCEMENT SETTINGS
# =============================================================================

DEFAULTS = {
    # Voice cleanup (NEW: Remove fuzz/static from audio)
    'cleanup_enabled': True,      # Enable voice cleanup filters
    'cleanup_highpass': 80,       # Remove low rumble below Hz
    'cleanup_lowpass': 12000,     # Remove harsh highs above Hz
    'cleanup_denoise': True,      # FFT-based denoising
    'cleanup_denoise_amount': 25, # Denoise noise floor (-dB)

    # Tape warmth (lowered for clarity)
    'warmth_drive': 0.15,         # 0.0-1.0, higher = more saturation

    # De-essing
    'deess_enabled': True,

    # Whisper overlay (Layer 2: ethereal)
    'whisper_enabled': True,
    'whisper_db': -24,            # Level relative to voice

    # Subharmonic (Layer 3: grounding)
    'subharmonic_enabled': False,  # disabled by default for clarity
    'subharmonic_db': -12,        # Level relative to voice

    # Room tone
    'room_enabled': True,
    'room_amount': 0.02,          # 0.0-1.0, wet mix percentage

    # Cuddle waves (amplitude modulation)
    'cuddle_enabled': True,
    'cuddle_freq': 0.05,          # Hz (one cycle per 20 seconds)
    'cuddle_depth_db': 1.0,       # Modulation depth

    # Echo (dreamy spatial)
    'echo_enabled': False,
    'echo_delay_ms': 180,         # Primary echo delay
    'echo_decay': 0.25,           # Echo volume (25% of original)
    'echo_feedback': 0.15,        # Feedback for secondary echoes

    # NEW: Dual reverb system (short room + long hall)
    'dual_reverb_enabled': False,
    'short_reverb_time': 0.3,     # 300ms room reverb
    'short_reverb_wet': 0.12,     # 12% wet mix
    'long_reverb_time': 8.0,      # 8 second hall reverb
    'long_reverb_wet': 0.06,      # 6% wet mix (very subtle)
    'long_reverb_predelay': 0.05, # 50ms predelay for clarity

    # NEW: High-frequency whisper aura (subliminal presence)
    'hf_aura_enabled': False,
    'hf_aura_db': -40,            # Very quiet (-40 dB)
    'hf_aura_cutoff': 4000,       # HPF cutoff in Hz

    # NEW: Adaptive processing (stage-aware enhancements)
    'adaptive_enabled': True,
    'spectral_motion_enabled': True,  # Slow EQ sweeps for "living" sound
    'hdra_enabled': True,             # Hypnotic Dynamic Range Architecture
    'spatial_animation_enabled': True,  # Stage-aware stereo field
    'breath_sync_enabled': True,      # Breath-synchronized modulation
    'anchoring_enabled': True,        # Final minute subliminal anchor
    'anchoring_duration': 60,         # Anchor duration in seconds

    # Mastering
    'target_lufs': -14,           # YouTube standard
    'true_peak_dbtp': -1.5,       # True peak ceiling
}


# =============================================================================
# VOICE-CLEAR MODE SETTINGS
# =============================================================================
# Optimized for maximum voice intelligibility while maintaining hypnotic depth.
# Disables secondary layers that can cause muddiness.
# Approved settings from Carnegie Steel Empire session testing.

VOICE_CLEAR_SETTINGS = {
    # Voice cleanup - aggressive for maximum clarity
    'cleanup_enabled': True,
    'cleanup_highpass': 100,      # Slightly higher to remove more rumble
    'cleanup_lowpass': 11000,     # Slightly lower to tame more highs
    'cleanup_denoise': True,
    'cleanup_denoise_amount': 30, # Stronger denoising

    # Tape warmth - subtle analog feel
    'warmth_drive': 0.20,

    # De-essing - always on for smoothness
    'deess_enabled': True,

    # Voice-doubling layers - ALL DISABLED for clarity
    'whisper_enabled': False,
    'subharmonic_enabled': False,
    'hf_aura_enabled': False,
    'dual_reverb_enabled': False,
    'adaptive_enabled': False,

    # Room tone - minimal spatial context
    'room_enabled': True,
    'room_amount': 0.03,

    # Cuddle waves - gentle amplitude modulation
    'cuddle_enabled': True,
    'cuddle_freq': 0.05,
    'cuddle_depth_db': 1.2,

    # Echo - subtle depth (not voice-doubling)
    'echo_enabled': True,
    'echo_delay_ms': 250,
    'echo_decay': 0.12,
    'echo_feedback': 0.08,

    # Mastering
    'target_lufs': -14,
    'true_peak_dbtp': -1.5,
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
# NEW: DUAL REVERB SYSTEM
# =============================================================================

def _create_enhancement_layers(audio, sample_rate, cfg):
    """Create whisper and subharmonic layers."""
    layers = []

    if cfg['whisper_enabled']:
        whisper = create_whisper_layer(audio, sample_rate, cfg['whisper_db'])
        layers.append(('whisper', whisper))

    if cfg['subharmonic_enabled']:
        subharmonic = create_subharmonic_layer(audio, sample_rate, cfg['subharmonic_db'])
        layers.append(('subharmonic', subharmonic))

    return layers


def _apply_spatial_effects(enhanced, sample_rate, duration, cfg):
    """Apply room tone, cuddle waves, echo, dual reverb, and HF aura."""
    # Room tone
    if cfg['room_enabled']:
        enhanced = add_room_tone(enhanced, sample_rate, cfg['room_amount'])

    # Cuddle waves
    if cfg['cuddle_enabled']:
        enhanced = apply_cuddle_waves(
            enhanced, sample_rate, duration,
            cfg['cuddle_freq'], cfg['cuddle_depth_db']
        )

    # Echo
    if cfg['echo_enabled']:
        enhanced = apply_echo(
            enhanced, sample_rate,
            cfg['echo_delay_ms'], cfg['echo_decay'], cfg['echo_feedback']
        )

    # Dual reverb (short room + long hall)
    if cfg.get('dual_reverb_enabled', True):
        enhanced = apply_dual_reverb(enhanced, sample_rate, cfg)

    # High-frequency whisper aura (subliminal presence)
    if cfg.get('hf_aura_enabled', True):
        hf_aura = create_hf_whisper_aura(
            enhanced, sample_rate,
            cfg.get('hf_aura_db', -40),
            cfg.get('hf_aura_cutoff', 4000)
        )
        enhanced = enhanced + hf_aura

    return enhanced


def _apply_adaptive_processing(enhanced, sample_rate, duration, cfg, manifest=None):
    """Apply intelligent adaptive processing based on hypnosis stages."""
    if not ADAPTIVE_AVAILABLE:
        print("  ⚠ Adaptive processing not available (import failed)")
        return enhanced

    if not cfg.get('adaptive_enabled', True):
        return enhanced

    print("\n  🧠 ADAPTIVE PROCESSING")
    print("  " + "=" * 40)

    # Extract stages from manifest if available
    stages = []
    if manifest and 'sections' in manifest:
        stages = stages_from_manifest(manifest)
        print(f"    Detected {len(stages)} hypnosis stages from manifest")
    else:
        # Create default stages based on duration
        print("    Using default stage timing (no manifest)")
        # Standard 30-minute session timing
        stages = _create_default_stages(duration)

    # Apply full adaptive processing
    enhanced = apply_full_adaptive_processing(
        enhanced, sample_rate, stages,
        voice_track=None,  # Could be added if voice is available separately
        enable_spectral_motion=cfg.get('spectral_motion_enabled', True),
        enable_masking=False,  # Requires separate voice track
        enable_hdra=cfg.get('hdra_enabled', True),
        enable_spatial=cfg.get('spatial_animation_enabled', True),
        enable_breath_sync=cfg.get('breath_sync_enabled', True),
    )

    # Add anchoring layer in final minute
    if cfg.get('anchoring_enabled', True):
        anchor_duration = min(cfg.get('anchoring_duration', 60), duration * 0.1)
        anchor_start = duration - anchor_duration

        print(f"    Adding anchoring layer (last {anchor_duration:.0f}s)")
        anchor_layer = create_anchoring_layer(anchor_duration, sample_rate)

        # Mix anchoring layer into final portion
        anchor_start_sample = int(anchor_start * sample_rate)
        anchor_samples = len(anchor_layer)

        if anchor_start_sample + anchor_samples <= len(enhanced):
            enhanced[anchor_start_sample:anchor_start_sample + anchor_samples] += anchor_layer

    return enhanced


def _create_default_stages(duration: float) -> List[Dict]:
    """Create default hypnosis stages based on duration."""
    # Standard distribution: 10% pretalk, 15% induction, 50% journey, 15% integration, 10% awakening
    stages = [
        {'name': 'pretalk', 'start': 0, 'end': duration * 0.10, **STAGE_PRESETS['pretalk']},
        {'name': 'induction', 'start': duration * 0.10, 'end': duration * 0.25, **STAGE_PRESETS['induction']},
        {'name': 'journey', 'start': duration * 0.25, 'end': duration * 0.75, **STAGE_PRESETS['journey']},
        {'name': 'integration', 'start': duration * 0.75, 'end': duration * 0.90, **STAGE_PRESETS['integration']},
        {'name': 'awakening', 'start': duration * 0.90, 'end': duration, **STAGE_PRESETS['awakening']},
    ]
    return stages


def _print_core_enhancements(cfg):
    """Print core audio enhancement summary."""
    enhancements = [
        (True, f"Tape warmth ({cfg['warmth_drive']*100:.0f}%)"),
        (cfg['deess_enabled'], "De-essing (4-8 kHz)"),
        (cfg['whisper_enabled'], f"Whisper overlay ({cfg['whisper_db']} dB)"),
        (cfg['subharmonic_enabled'], f"Subharmonic ({cfg['subharmonic_db']} dB)"),
        (cfg['room_enabled'], f"Room tone ({cfg['room_amount']*100:.0f}%)"),
        (cfg['cuddle_enabled'], f"Cuddle waves ({cfg['cuddle_freq']} Hz, ±{cfg['cuddle_depth_db']} dB)"),
        (cfg['echo_enabled'], f"Echo ({cfg['echo_delay_ms']}ms, {cfg['echo_decay']*100:.0f}%)"),
        (cfg.get('dual_reverb_enabled', True),
         f"Dual reverb (short: {cfg.get('short_reverb_time', 0.3)*1000:.0f}ms, "
         f"long: {cfg.get('long_reverb_time', 8.0):.1f}s)"),
        (cfg.get('hf_aura_enabled', True), f"HF whisper aura ({cfg.get('hf_aura_db', -40)} dB)"),
    ]
    for enabled, desc in enhancements:
        if enabled:
            print(f"   ✓ {desc}")


def _print_adaptive_summary(cfg):
    """Print adaptive processing summary."""
    if not cfg.get('adaptive_enabled', True):
        return
    print("\n🧠 Adaptive Processing (Stage-Aware):")
    features = [
        (cfg.get('spectral_motion_enabled', True), "Spectral motion (living EQ sweep)"),
        (cfg.get('hdra_enabled', True), "HDR-A (hypnotic dynamic range architecture)"),
        (cfg.get('spatial_animation_enabled', True), "Spatial animation (stage-aware stereo field)"),
        (cfg.get('breath_sync_enabled', True), "Breath synchronization (0.15 Hz modulation)"),
        (cfg.get('anchoring_enabled', True), f"Post-hypnotic anchoring ({cfg.get('anchoring_duration', 60)}s)"),
    ]
    for enabled, desc in features:
        if enabled:
            print(f"   ✓ {desc}")


def _print_enhancement_summary(cfg, duration, sample_rate):
    """Print summary of applied enhancements."""
    print("\n📋 Output Summary:")
    print(f"   Duration: {duration/60:.1f} minutes")
    print(f"   Sample rate: {sample_rate} Hz")

    print("\n🎧 Enhancements Applied:")
    _print_core_enhancements(cfg)
    _print_adaptive_summary(cfg)

    print("\n🎚️ Mastering:")
    print(f"   ✓ LUFS: {cfg['target_lufs']} LUFS")
    print(f"   ✓ True peak: {cfg['true_peak_dbtp']} dBTP")
    print("   ✓ Warmth & presence EQ")
    print("   ✓ Stereo enhancement (5%)")


def apply_dual_reverb(audio, sample_rate, cfg):
    """
    Apply professional dual-reverb system for depth and presence.

    Creates two reverb layers:
    - Short reverb (room): Physical presence, 0.2-0.4 seconds
    - Long reverb (hall): Ethereal depth, 6-12 seconds

    This combination provides both intimacy and spaciousness,
    ideal for hypnotic dreamweaving content.

    Args:
        audio: Input stereo audio array
        sample_rate: Sample rate in Hz
        cfg: Configuration dict with reverb parameters

    Returns:
        Audio with dual reverb applied
    """
    print("  🏛️ Applying dual reverb system...")

    output = audio.copy()

    # Short room reverb (physical presence)
    short_time = cfg.get('short_reverb_time', 0.3)
    short_wet = cfg.get('short_reverb_wet', 0.12)

    if short_wet > 0:
        room_samples = int(short_time * sample_rate)
        # Create room impulse response with early reflections
        t_room = np.linspace(0, short_time, room_samples)
        room_ir = np.exp(-t_room * (5 / short_time))  # Exponential decay
        # Add randomness for natural diffusion
        rng = np.random.default_rng(42)  # Seeded for consistency
        room_ir *= rng.standard_normal(room_samples) * 0.1

        room_reverb = np.zeros_like(audio)
        for ch in range(2):
            room_reverb[:, ch] = signal.fftconvolve(audio[:, ch], room_ir, mode='same')

        # Blend with dry signal
        output = output * (1 - short_wet) + room_reverb * short_wet
        print(f"      Short reverb: {short_time*1000:.0f}ms, {short_wet*100:.0f}% wet")

    # Long hall reverb (ethereal depth)
    long_time = cfg.get('long_reverb_time', 8.0)
    long_wet = cfg.get('long_reverb_wet', 0.06)
    predelay = cfg.get('long_reverb_predelay', 0.05)
    predelay_samples = int(predelay * sample_rate)

    if long_wet > 0:
        hall_samples = int(long_time * sample_rate)
        t_hall = np.linspace(0, long_time, hall_samples)

        # Create hall impulse response with modulated diffusion
        hall_decay = np.exp(-t_hall * (0.5))  # Slower decay for hall
        rng = np.random.default_rng(123)  # Different seed for variation
        hall_ir = hall_decay * rng.standard_normal(hall_samples) * 0.05

        # Add subtle modulation for shimmer effect
        shimmer_mod = 1 + 0.1 * np.sin(2 * np.pi * 2 * t_hall)
        hall_ir *= shimmer_mod

        hall_reverb = np.zeros_like(audio)
        for ch in range(2):
            convolved = signal.fftconvolve(audio[:, ch], hall_ir, mode='same')
            # Apply predelay
            if predelay_samples > 0 and predelay_samples < len(convolved):
                hall_reverb[predelay_samples:, ch] = convolved[:-predelay_samples]
            else:
                hall_reverb[:, ch] = convolved

        # Add hall reverb (don't subtract from dry, just add)
        output = output + hall_reverb * long_wet
        print(f"      Long reverb: {long_time:.1f}s, {long_wet*100:.0f}% wet, {predelay*1000:.0f}ms predelay")

    return output


def create_hf_whisper_aura(audio, sample_rate, level_db=-40, cutoff_hz=4000):
    """
    Create extremely subtle high-frequency presence layer.

    This creates a subliminal "aura" around the voice by:
    1. High-pass filtering to extract only high frequencies
    2. Adding shimmer reverb for ethereal quality
    3. Mixing at very low level (-35 to -45 dB)

    The result is felt more than heard, creating an angelic presence.

    Args:
        audio: Input stereo audio array
        sample_rate: Sample rate in Hz
        level_db: Output level in dB (default -40, very quiet)
        cutoff_hz: High-pass filter cutoff (default 4000 Hz)

    Returns:
        HF aura layer (to be added to main mix)
    """
    print("  ✨ Creating high-frequency whisper aura...")

    nyq = sample_rate / 2

    # High-pass filter to extract only high frequencies
    b_hp, a_hp = signal.butter(3, cutoff_hz / nyq, btype='high')

    hf_layer = np.zeros_like(audio)
    for ch in range(2):
        hf_layer[:, ch] = signal.filtfilt(b_hp, a_hp, audio[:, ch])

    # Add shimmer reverb (1.5 second ethereal tail)
    reverb_length = int(1.5 * sample_rate)
    t_reverb = np.linspace(0, 1.5, reverb_length)
    rng = np.random.default_rng(777)
    reverb_ir = np.exp(-t_reverb * 3) * rng.standard_normal(reverb_length) * 0.05

    for ch in range(2):
        hf_layer[:, ch] = signal.fftconvolve(hf_layer[:, ch], reverb_ir, mode='same')

    # Apply level
    hf_layer *= db_to_linear(level_db)

    print(f"      Cutoff: {cutoff_hz} Hz, Level: {level_db} dB")
    return hf_layer


# =============================================================================
# VOICE CLEANUP (Remove fuzz/static)
# =============================================================================

def apply_voice_cleanup(input_path, output_path, cfg):
    """
    Apply voice cleanup filters using FFmpeg to remove fuzz and static.

    Filters:
    - highpass: Remove low rumble
    - lowpass: Remove harsh high frequencies
    - afftdn: FFT-based denoising for fuzz/static removal
    - acompressor: Gentle compression to smooth dynamics

    Args:
        input_path: Path to input audio file
        output_path: Path to output audio file
        cfg: Configuration dict with cleanup settings

    Returns:
        True on success, False on failure
    """
    if not cfg.get('cleanup_enabled', True):
        print("  ⏭️  Voice cleanup disabled, skipping...")
        return True

    print("\n🧹 VOICE CLEANUP")
    print("=" * 60)

    # Build filter chain
    filters = []

    # Highpass filter - remove low rumble
    highpass_freq = cfg.get('cleanup_highpass', 80)
    filters.append(f'highpass=f={highpass_freq}')
    print(f"  📉 Highpass: {highpass_freq} Hz (remove low rumble)")

    # Lowpass filter - remove harsh highs
    lowpass_freq = cfg.get('cleanup_lowpass', 12000)
    filters.append(f'lowpass=f={lowpass_freq}')
    print(f"  📈 Lowpass: {lowpass_freq} Hz (tame harsh highs)")

    # FFT-based denoising
    if cfg.get('cleanup_denoise', True):
        denoise_amount = cfg.get('cleanup_denoise_amount', 25)
        # afftdn: nf=noise floor, nr=noise reduction strength, nt=noise type (w=white)
        filters.append(f'afftdn=nf=-{denoise_amount}:nr=10:nt=w')
        print(f"  🔇 Denoise: -{denoise_amount}dB noise floor (FFT-based)")

    # Gentle compression to smooth dynamics
    filters.append('acompressor=threshold=-20dB:ratio=3:attack=5:release=50')
    print("  🔊 Compressor: -20dB threshold, 3:1 ratio")

    filter_string = ','.join(filters)

    # Run FFmpeg
    cmd = [
        'ffmpeg', '-y', '-i', str(input_path),
        '-af', filter_string,
        '-c:a', 'pcm_s24le', '-ar', '48000',
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"\n  ✓ Cleanup complete: {os.path.basename(output_path)}")
        return True
    else:
        print(f"\n  ✗ Cleanup failed: {result.stderr[:200]}")
        return False


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
    print("\nLayered Hypnotic Presence:")
    print("  Layer 1: Main voice (warmth + de-essing)")
    print("  Layer 2: Whisper overlay (ethereal)")
    print("  Layer 3: Subharmonic warm (optional)")
    print("  + Room tone, cuddle waves; echo/reverb optional")

    # Load audio
    audio, sample_rate, duration = load_audio(input_path)

    print("\n✨ HYPNOTIC ENHANCEMENT")
    print("=" * 60)

    # Step 1: Tape warmth
    audio = apply_warmth(audio, cfg['warmth_drive'])

    # Step 2: De-essing
    if cfg['deess_enabled']:
        audio = apply_deessing(audio, sample_rate)

    # Step 3: Create and combine enhancement layers
    layers = _create_enhancement_layers(audio, sample_rate, cfg)
    print("\n  🎚️ Combining triple-layer presence...")
    enhanced = audio.copy()
    for name, layer in layers:
        enhanced += layer
    print(f"      Main voice + {' + '.join([name for name, _ in layers])}")

    # Step 4: Apply spatial effects (room, cuddle, echo, dual reverb, HF aura)
    enhanced = _apply_spatial_effects(enhanced, sample_rate, duration, cfg)

    # Step 5: Apply adaptive processing (stage-aware enhancements)
    if cfg.get('adaptive_enabled', True) and ADAPTIVE_AVAILABLE:
        enhanced = _apply_adaptive_processing(enhanced, sample_rate, duration, cfg)

    # Step 6: Normalize and prevent clipping
    print("\n  📊 Pre-master normalization...")
    enhanced = normalize_rms(enhanced, -16)
    peak = np.max(np.abs(enhanced))
    if peak > 0.95:
        enhanced = enhanced * (0.95 / peak)
        print(f"      Applied headroom: {linear_to_db(0.95/peak):.1f} dB")

    # Save intermediate WAV
    temp_wav = output_dir / f"{output_name}_temp.wav"
    print(f"\n💾 Saving intermediate: {temp_wav.name}")
    audio_16bit = (np.clip(enhanced, -1, 1) * 32767).astype(np.int16)
    wavfile.write(str(temp_wav), sample_rate, audio_16bit)

    # Step 7: Apply voice cleanup (remove fuzz/static)
    if cfg.get('cleanup_enabled', True):
        cleanup_wav = output_dir / f"{output_name}_cleanup.wav"
        cleanup_success = apply_voice_cleanup(temp_wav, cleanup_wav, cfg)
        if cleanup_success and cleanup_wav.exists():
            # Use cleanup file for mastering
            master_input = cleanup_wav
        else:
            # Fall back to temp_wav if cleanup failed
            master_input = temp_wav
    else:
        master_input = temp_wav

    # Final mastering
    output_wav = output_dir / f"{output_name}.wav"
    output_mp3 = output_dir / f"{output_name}.mp3"

    success = apply_mastering_chain(
        master_input, output_wav, output_mp3,
        cfg['target_lufs'], cfg['true_peak_dbtp']
    )

    # Cleanup temp files
    if temp_wav.exists():
        temp_wav.unlink()
    cleanup_wav = output_dir / f"{output_name}_cleanup.wav"
    if cleanup_wav.exists():
        cleanup_wav.unlink()

    if success:
        print("\n" + "=" * 70)
        print("✅ HYPNOTIC POST-PROCESSING COMPLETE!")
        print("=" * 70)
        _print_enhancement_summary(cfg, duration, sample_rate)
        print("\n📁 Output Files:")
        print(f"   {output_wav}")
        print(f"   {output_mp3}")
        return output_wav, output_mp3

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

    # Subharmonic boost (low-end warmth)
    if cfg['subharmonic_enabled']:
        filters.append(f"equalizer=f=80:t=h:width=100:g={abs(cfg['subharmonic_db'])/4}")
        print(f"   ✓ Subharmonic boost")

    # Echo
    if cfg['echo_enabled']:
        delay_ms = cfg['echo_delay_ms']
        decay = cfg['echo_decay']
        filters.append(f"aecho=0.8:0.7:{delay_ms}:{decay}")
        print(f"   ✓ Echo: {delay_ms}ms, {decay*100:.0f}%")

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

def _resolve_io_paths(args):
    """Resolve input file, output name, and output directory from args."""
    if args.session:
        session_dir = Path(args.session)
        input_file = session_dir / 'output' / 'session_mixed.wav'
        if not input_file.exists():
            print(f"Error: {input_file} not found")
            sys.exit(1)
        session_name = session_dir.name.replace('-', '_')
        output_name = f"{session_name}_MASTER"
        output_dir = session_dir / 'output'
        return input_file, output_name, output_dir

    if args.input:
        input_file = Path(args.input)
        if not input_file.exists():
            print(f"Error: {input_file} not found")
            sys.exit(1)
        output_name = args.output or input_file.stem + '_MASTER'
        output_dir = Path(args.output_dir) if args.output_dir else input_file.parent
        return input_file, output_name, output_dir

    return None, None, None


def _build_settings_from_args(args):
    """Build settings dictionary from parsed CLI arguments."""
    settings = {}

    # Apply voice-clear preset first (can be overridden by explicit flags)
    if getattr(args, 'voice_clear', False):
        print("\n🎯 Voice-Clear Mode: Maximum voice intelligibility")
        settings.update(VOICE_CLEAR_SETTINGS)
        return settings  # Voice-clear mode ignores other flags for simplicity

    # Toggle mappings: (arg_name, setting_key)
    toggles = [
        ('no_cleanup', 'cleanup_enabled'),
        ('no_deess', 'deess_enabled'),
        ('no_whisper', 'whisper_enabled'),
        ('no_subharmonic', 'subharmonic_enabled'),
        ('no_room', 'room_enabled'),
        ('no_cuddle', 'cuddle_enabled'),
        ('no_echo', 'echo_enabled'),
        ('no_dual_reverb', 'dual_reverb_enabled'),
        ('no_hf_aura', 'hf_aura_enabled'),
        ('no_adaptive', 'adaptive_enabled'),
        ('no_spectral_motion', 'spectral_motion_enabled'),
        ('no_hdra', 'hdra_enabled'),
        ('no_spatial_animation', 'spatial_animation_enabled'),
        ('no_breath_sync', 'breath_sync_enabled'),
        ('no_anchoring', 'anchoring_enabled'),
    ]
    for arg_name, setting_key in toggles:
        if getattr(args, arg_name, False):
            settings[setting_key] = False

    # Parameter mappings: (arg_name, setting_key)
    params = [
        ('warmth', 'warmth_drive'),
        ('whisper_db', 'whisper_db'),
        ('sub_db', 'subharmonic_db'),
        ('room', 'room_amount'),
        ('cuddle_freq', 'cuddle_freq'),
        ('cuddle_depth', 'cuddle_depth_db'),
        ('echo_delay', 'echo_delay_ms'),
        ('echo_decay', 'echo_decay'),
        ('echo_feedback', 'echo_feedback'),
        ('short_reverb_time', 'short_reverb_time'),
        ('short_reverb_wet', 'short_reverb_wet'),
        ('long_reverb_time', 'long_reverb_time'),
        ('long_reverb_wet', 'long_reverb_wet'),
        ('long_reverb_predelay', 'long_reverb_predelay'),
        ('hf_aura_db', 'hf_aura_db'),
        ('hf_aura_cutoff', 'hf_aura_cutoff'),
        ('lufs', 'target_lufs'),
        ('peak', 'true_peak_dbtp'),
    ]
    for arg_name, setting_key in params:
        value = getattr(args, arg_name, None)
        if value is not None:
            settings[setting_key] = value

    return settings


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
    parser.add_argument('--no-cleanup', action='store_true', help='Disable voice cleanup (highpass/lowpass/denoise)')
    parser.add_argument('--no-deess', action='store_true', help='Disable de-essing')
    parser.add_argument('--no-whisper', action='store_true', help='Disable whisper layer')
    parser.add_argument('--no-subharmonic', action='store_true', help='Disable subharmonic layer')
    parser.add_argument('--no-room', action='store_true', help='Disable room tone')
    parser.add_argument('--no-cuddle', action='store_true', help='Disable cuddle waves')
    parser.add_argument('--no-echo', action='store_true', help='Disable echo')
    parser.add_argument('--no-dual-reverb', action='store_true', help='Disable dual reverb system')
    parser.add_argument('--no-hf-aura', action='store_true', help='Disable high-frequency whisper aura')
    parser.add_argument('--no-adaptive', action='store_true', help='Disable adaptive processing')
    parser.add_argument('--no-spectral-motion', action='store_true', help='Disable spectral motion')
    parser.add_argument('--no-hdra', action='store_true', help='Disable dynamic range architecture')
    parser.add_argument('--no-spatial-animation', action='store_true', help='Disable spatial animation')
    parser.add_argument('--no-breath-sync', action='store_true', help='Disable breath synchronization')
    parser.add_argument('--no-anchoring', action='store_true', help='Disable final anchoring layer')

    # Enhancement parameters
    parser.add_argument('--warmth', type=float, help=f'Warmth drive 0-1 (default: {DEFAULTS["warmth_drive"]})')
    parser.add_argument('--whisper-db', type=float, help=f'Whisper level dB (default: {DEFAULTS["whisper_db"]})')
    parser.add_argument('--sub-db', type=float, help=f'Subharmonic level dB (default: {DEFAULTS["subharmonic_db"]})')
    parser.add_argument('--room', type=float, help=f'Room amount 0-1 (default: {DEFAULTS["room_amount"]})')
    parser.add_argument('--cuddle-freq', type=float, help=f'Cuddle frequency Hz (default: {DEFAULTS["cuddle_freq"]})')
    parser.add_argument('--cuddle-depth', type=float, help=f'Cuddle depth dB (default: {DEFAULTS["cuddle_depth_db"]})')
    parser.add_argument('--echo-delay', type=float, help=f'Echo delay ms (default: {DEFAULTS["echo_delay_ms"]})')
    parser.add_argument('--echo-decay', type=float, help=f'Echo decay 0-1 (default: {DEFAULTS["echo_decay"]})')
    parser.add_argument('--echo-feedback', type=float, help=f'Echo feedback 0-1 (default: {DEFAULTS["echo_feedback"]})')

    # Dual reverb parameters (NEW)
    parser.add_argument('--short-reverb-time', type=float,
                       help=f'Short reverb time in seconds (default: {DEFAULTS["short_reverb_time"]})')
    parser.add_argument('--short-reverb-wet', type=float,
                       help=f'Short reverb wet mix 0-1 (default: {DEFAULTS["short_reverb_wet"]})')
    parser.add_argument('--long-reverb-time', type=float,
                       help=f'Long reverb time in seconds (default: {DEFAULTS["long_reverb_time"]})')
    parser.add_argument('--long-reverb-wet', type=float,
                       help=f'Long reverb wet mix 0-1 (default: {DEFAULTS["long_reverb_wet"]})')
    parser.add_argument('--long-reverb-predelay', type=float,
                       help=f'Long reverb predelay in seconds (default: {DEFAULTS["long_reverb_predelay"]})')

    # HF aura parameters (NEW)
    parser.add_argument('--hf-aura-db', type=float,
                       help=f'HF aura level in dB (default: {DEFAULTS["hf_aura_db"]})')
    parser.add_argument('--hf-aura-cutoff', type=float,
                       help=f'HF aura HPF cutoff in Hz (default: {DEFAULTS["hf_aura_cutoff"]})')

    # Mastering
    parser.add_argument('--lufs', type=float, help=f'Target LUFS (default: {DEFAULTS["target_lufs"]})')
    parser.add_argument('--peak', type=float, help=f'True peak dBTP (default: {DEFAULTS["true_peak_dbtp"]})')

    # Processing mode
    parser.add_argument('--ffmpeg-only', action='store_true',
                       help='Use lightweight FFmpeg-only processing (lower memory, for long sessions)')
    parser.add_argument('--voice-clear', action='store_true',
                       help='Voice-first mode: max voice clarity, minimal effects. '
                            'Disables whisper, subharmonic, HF-aura, dual-reverb, adaptive. '
                            'Keeps warmth(20%%), room(3%%), echo(250ms/12%%), cuddle(1.2dB).')

    args = parser.parse_args()

    # Resolve input/output paths
    input_file, output_name, output_dir = _resolve_io_paths(args)
    if input_file is None:
        parser.print_help()
        sys.exit(1)

    # Build settings from CLI arguments
    settings = _build_settings_from_args(args)

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
