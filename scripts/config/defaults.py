#!/usr/bin/env python3
"""
Centralized default configuration values for the Dreamweaving project.

This module consolidates magic numbers and default values that were
previously scattered throughout the codebase. Use these constants
instead of hardcoding values in scripts.

Usage:
    from scripts.config.defaults import AUDIO, VIDEO, BINAURAL, TTS

    sample_rate = AUDIO['sample_rate_hz']
    video_width = VIDEO['width']
    carrier_freq = BINAURAL['carrier_freq']
"""

from typing import Dict, Any, List


# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================

AUDIO: Dict[str, Any] = {
    # Sample rates
    'sample_rate_hz': 24000,          # Default for TTS output
    'high_quality_rate': 48000,       # For final mixing/mastering

    # Chunk processing
    'max_chunk_bytes': 5000,          # Maximum bytes per SSML chunk for TTS API

    # Duration defaults (seconds)
    'default_duration_sec': 1800,     # 30 minutes - fallback when duration unknown
    'fade_duration_sec': 2.0,         # Standard fade in/out duration

    # Loudness targets (LUFS)
    'voice_lufs': -16,                # Target loudness for voice
    'binaural_lufs': -28,             # Target loudness for binaural beats
    'ambient_lufs': -32,              # Target loudness for ambient sounds
    'sfx_lufs': -30,                  # Target loudness for sound effects

    # Format defaults
    'mp3_bitrate': '320k',            # High quality MP3
    'wav_bit_depth': 24,              # 24-bit WAV for mastering
}


# =============================================================================
# VIDEO CONFIGURATION
# =============================================================================

VIDEO: Dict[str, Any] = {
    # Resolution
    'width': 1920,
    'height': 1080,
    'fps': 30,

    # Encoding
    'video_codec': 'libx264',
    'audio_codec': 'aac',
    'audio_bitrate': '320k',
    'crf': 18,                        # Quality (lower = better, 18-23 typical)
    'preset': 'slow',                 # Encoding speed/quality tradeoff

    # Aspect ratio
    'aspect_ratio': '16:9',
}


# =============================================================================
# BINAURAL BEATS CONFIGURATION
# =============================================================================

BINAURAL: Dict[str, Any] = {
    # Carrier frequency (Hz)
    'carrier_freq': 200,              # Default carrier frequency
    'carrier_freq_alt': 432,          # Alternative "healing" frequency

    # Beat frequencies by brainwave state (Hz)
    'delta_hz': 2.0,                  # Deep sleep (0.5-4 Hz)
    'theta_hz': 5.0,                  # Meditation/light sleep (4-8 Hz)
    'alpha_hz': 10.0,                 # Relaxed alertness (8-12 Hz)
    'beta_hz': 20.0,                  # Active thinking (12-30 Hz)
    'gamma_hz': 40.0,                 # Peak focus/insight (30-100 Hz)

    # Schumann resonance
    'schumann_hz': 7.83,              # Earth's natural resonance

    # Amplitude
    'default_amplitude': 0.3,         # Default binaural beat amplitude

    # Frequency validation ranges
    'min_freq_hz': 0.5,
    'max_freq_hz': 20000,
}


# =============================================================================
# TEXT-TO-SPEECH CONFIGURATION
# =============================================================================

TTS: Dict[str, Any] = {
    # Speaking rate
    'speaking_rate': 0.85,            # Slower for hypnotic effect
    'speaking_rate_normal': 1.0,      # Normal pace for pre-talk

    # Pitch
    'pitch_semitones': -2.0,          # Slightly lower for warmth

    # Volume
    'volume_gain_db': 0.0,            # No gain adjustment

    # Audio effects
    'effects_profile': ['headphone-class-device'],

    # Default voice options
    'default_language': 'en-US',
}


# =============================================================================
# VOICE OPTIONS
# =============================================================================

VOICES: Dict[str, Dict[str, str]] = {
    # Female voices (Google Neural2)
    'female_warm': {
        'name': 'en-US-Neural2-A',
        'description': 'Warm female voice',
    },
    'female_soft': {
        'name': 'en-US-Neural2-C',
        'description': 'Soft female voice',
    },
    'female_deep': {
        'name': 'en-US-Neural2-E',
        'description': 'Deep female voice',
    },
    'female_clear': {
        'name': 'en-US-Neural2-F',
        'description': 'Clear female voice',
    },

    # Male voices (Google Neural2)
    'male_deep': {
        'name': 'en-US-Neural2-D',
        'description': 'Deep male voice',
    },
    'male_warm': {
        'name': 'en-US-Neural2-I',
        'description': 'Warm male voice',
    },
    'male_rich': {
        'name': 'en-US-Neural2-J',
        'description': 'Rich male voice',
    },
}

# Default voice for hypnosis sessions
DEFAULT_VOICE = VOICES['male_warm']['name']


# =============================================================================
# VOICE ENHANCEMENT PRESETS
# =============================================================================

VOICE_ENHANCEMENT: Dict[str, Any] = {
    # De-essing
    'deess_frequency': 6000,          # Target frequency for de-essing
    'deess_threshold': -30,           # dB threshold

    # Tape warmth
    'warmth_drive': 0.3,              # Saturation amount (0-1)

    # Whisper overlay
    'whisper_volume': -20,            # dB below main voice
    'whisper_delay_ms': 50,           # Slight delay for depth

    # Compression
    'compression_ratio': 3,           # 3:1 ratio
    'compression_threshold': -20,     # dB threshold
}


# =============================================================================
# SESSION STRUCTURE
# =============================================================================

SESSION_STRUCTURE: Dict[str, List[str]] = {
    # Required directories in a session
    'required_dirs': [
        'output',
        'working_files',
        'images',
    ],

    # Optional directories
    'optional_dirs': [
        'final_export',
        'variants',
        'archive',
    ],

    # Required files
    'required_files': [
        'manifest.yaml',
    ],
}


# =============================================================================
# VALIDATION THRESHOLDS
# =============================================================================

VALIDATION: Dict[str, Any] = {
    # SSML validation
    'max_ssml_bytes': 5000,           # Google TTS limit per chunk
    'recommended_break_density': 0.15,  # Breaks per word for hypnosis

    # Audio validation
    'min_duration_sec': 60,           # Minimum session length
    'max_duration_sec': 7200,         # Maximum session length (2 hours)

    # Frequency validation
    'min_frequency_hz': 1,
    'max_frequency_hz': 20000,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_frequency(freq: float) -> bool:
    """Validate that a frequency is within acceptable range."""
    return VALIDATION['min_frequency_hz'] <= freq <= VALIDATION['max_frequency_hz']


def validate_duration(duration_sec: float) -> bool:
    """Validate that a duration is within acceptable range."""
    return VALIDATION['min_duration_sec'] <= duration_sec <= VALIDATION['max_duration_sec']


def get_voice_name(voice_key: str) -> str:
    """Get the full voice name from a short key."""
    if voice_key in VOICES:
        return VOICES[voice_key]['name']
    return DEFAULT_VOICE


if __name__ == '__main__':
    # Display configuration for debugging
    print("Dreamweaving Configuration Defaults")
    print("=" * 50)
    print(f"\nAudio Settings:")
    for key, value in AUDIO.items():
        print(f"  {key}: {value}")

    print(f"\nVideo Settings:")
    for key, value in VIDEO.items():
        print(f"  {key}: {value}")

    print(f"\nBinaural Settings:")
    for key, value in BINAURAL.items():
        print(f"  {key}: {value}")

    print(f"\nTTS Settings:")
    for key, value in TTS.items():
        print(f"  {key}: {value}")

    print(f"\nDefault Voice: {DEFAULT_VOICE}")
