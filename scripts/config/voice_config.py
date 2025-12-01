#!/usr/bin/env python3
"""
Voice configuration loader for Dreamweaving.

This module provides a unified interface to voice configuration,
loading from the consolidated voice_config.yaml file.

Usage:
    from scripts.config.voice_config import (
        get_voice_profile,
        get_recommended_voices,
        get_prosody_for_section,
        VOICES,
        DEFAULT_VOICE
    )

    # Get a specific voice profile
    profile = get_voice_profile('warm_male')
    voice_name = profile['name']

    # Get recommended voices for a session type
    voices = get_recommended_voices('healing')

    # Get prosody settings for a section
    prosody = get_prosody_for_section('induction')
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


# Path to consolidated config
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
VOICE_CONFIG_PATH = CONFIG_DIR / "voice_config_consolidated.yaml"

# Fallback to old configs if consolidated doesn't exist
VOICE_CONFIG_YAML_PATH = CONFIG_DIR / "voice_config.yaml"
VOICE_PROFILES_JSON_PATH = CONFIG_DIR / "voice_profiles.json"


def _load_config() -> Dict[str, Any]:
    """Load the voice configuration file."""
    # Try consolidated config first
    if VOICE_CONFIG_PATH.exists():
        with open(VOICE_CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)

    # Fall back to original yaml
    if VOICE_CONFIG_YAML_PATH.exists():
        with open(VOICE_CONFIG_YAML_PATH, 'r') as f:
            return yaml.safe_load(f)

    # Return defaults if no config found
    return {
        'profiles': {
            'default': {
                'name': 'en-US-Neural2-A',
                'gender': 'female',
                'description': 'Default voice'
            }
        },
        'prosody_defaults': {
            'speaking_rate': 0.85,
            'pitch_semitones': -2.0
        }
    }


# Load config at module import
_config = _load_config()


# =============================================================================
# VOICE PROFILES
# =============================================================================

def get_voice_profile(profile_key: str) -> Dict[str, Any]:
    """
    Get a voice profile by key.

    Args:
        profile_key: Profile identifier (e.g., 'default', 'warm_male')

    Returns:
        Dict with voice profile settings

    Raises:
        KeyError: If profile not found
    """
    profiles = _config.get('profiles', {})
    if profile_key not in profiles:
        raise KeyError(f"Voice profile '{profile_key}' not found. "
                      f"Available: {list(profiles.keys())}")
    return profiles[profile_key]


def get_voice_name(profile_key: str) -> str:
    """
    Get the TTS voice name for a profile.

    Args:
        profile_key: Profile identifier

    Returns:
        Voice name string (e.g., 'en-US-Neural2-A')
    """
    return get_voice_profile(profile_key)['name']


def list_profiles() -> List[str]:
    """List all available voice profile keys."""
    return list(_config.get('profiles', {}).keys())


def get_profiles_by_gender(gender: str) -> List[Dict[str, Any]]:
    """
    Get all voice profiles of a specific gender.

    Args:
        gender: 'male' or 'female'

    Returns:
        List of matching profile dicts
    """
    profiles = _config.get('profiles', {})
    return [
        {**profile, 'key': key}
        for key, profile in profiles.items()
        if profile.get('gender', '').lower() == gender.lower()
    ]


# =============================================================================
# SESSION RECOMMENDATIONS
# =============================================================================

def get_recommended_voices(session_type: str) -> List[str]:
    """
    Get recommended voice profiles for a session type.

    Args:
        session_type: Type of session (e.g., 'healing', 'confidence')

    Returns:
        List of profile keys in order of preference
    """
    recommendations = _config.get('session_recommendations', {})
    return recommendations.get(session_type, ['default'])


def get_best_voice_for_session(session_type: str) -> Dict[str, Any]:
    """
    Get the best voice profile for a session type.

    Args:
        session_type: Type of session

    Returns:
        Voice profile dict
    """
    recommendations = get_recommended_voices(session_type)
    if recommendations:
        return get_voice_profile(recommendations[0])
    return get_voice_profile('default')


# =============================================================================
# PROSODY SETTINGS
# =============================================================================

def get_prosody_defaults() -> Dict[str, float]:
    """Get default prosody settings."""
    return _config.get('prosody_defaults', {
        'speaking_rate': 0.85,
        'pitch_semitones': -2.0,
        'volume_gain_db': 0.0
    })


def get_prosody_for_section(section: str) -> Dict[str, float]:
    """
    Get prosody settings for a specific section.

    Args:
        section: Section name (e.g., 'induction', 'journey')

    Returns:
        Dict with speaking_rate and pitch_semitones
    """
    defaults = get_prosody_defaults()
    section_prosody = _config.get('section_prosody', {})

    if section in section_prosody:
        return {**defaults, **section_prosody[section]}
    return defaults


# =============================================================================
# AUDIO SETTINGS
# =============================================================================

def get_audio_settings(preset: str = 'standard') -> Dict[str, Any]:
    """
    Get audio settings for a quality preset.

    Args:
        preset: Quality preset ('standard', 'high_quality', 'small_file')

    Returns:
        Dict with audio settings
    """
    audio = _config.get('audio', {})
    presets = audio.get('presets', {})
    return presets.get(preset, presets.get('standard', {
        'sample_rate_hz': 24000
    }))


def get_mastering_settings() -> Dict[str, Any]:
    """Get audio mastering settings."""
    audio = _config.get('audio', {})
    return audio.get('mastering', {
        'target_lufs': -14,
        'sample_rate_hz': 48000,
        'bit_depth': 24
    })


def get_tts_settings() -> Dict[str, Any]:
    """Get TTS output settings."""
    audio = _config.get('audio', {})
    return audio.get('tts', {
        'audio_encoding': 'MP3',
        'sample_rate_hz': 24000,
        'effects_profile': ['headphone-class-device']
    })


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

# Quick access to all profiles
VOICES = _config.get('profiles', {})

# Default voice name
DEFAULT_VOICE = VOICES.get('default', {}).get('name', 'en-US-Neural2-A')

# Default profile key
DEFAULT_PROFILE = 'default'

# Provider info
PROVIDER = _config.get('provider', {}).get('name', 'google')


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == '__main__':
    print("Voice Configuration Module")
    print("=" * 60)

    print(f"\nProvider: {PROVIDER}")
    print(f"Default Voice: {DEFAULT_VOICE}")

    print(f"\nAvailable Profiles ({len(list_profiles())}):")
    for key in list_profiles():
        profile = get_voice_profile(key)
        print(f"  - {key}: {profile['name']} ({profile.get('gender', 'unknown')})")

    print("\nFemale Voices:")
    for profile in get_profiles_by_gender('female'):
        print(f"  - {profile['key']}: {profile['name']}")

    print("\nMale Voices:")
    for profile in get_profiles_by_gender('male'):
        print(f"  - {profile['key']}: {profile['name']}")

    print("\nRecommended for 'healing' sessions:")
    for key in get_recommended_voices('healing'):
        print(f"  - {key}")

    print("\nProsody for 'induction' section:")
    prosody = get_prosody_for_section('induction')
    print(f"  Speaking Rate: {prosody.get('speaking_rate')}")
    print(f"  Pitch: {prosody.get('pitch_semitones')} semitones")

    print("\nMastering Settings:")
    mastering = get_mastering_settings()
    print(f"  Target LUFS: {mastering.get('target_lufs')}")
    print(f"  Sample Rate: {mastering.get('sample_rate_hz')} Hz")
