#!/usr/bin/env python3
"""
Sound Effect Synchronization Module for Dreamweaving

This module handles the parsing, timing, and rendering of sound effects
that are synchronized with vocal narration in hypnotic sessions.

SFX markers are embedded in SSML scripts using TWO formats:

1. Structured format (legacy):
    [[SFX:effect_name:param1=value1,param2=value2]]

2. Natural language format (preferred):
    [SFX: Description of sound, duration, notes]

Example:
    <prosody rate="1.0">
        You hear a gentle chime in the distance...
        [SFX: Deep ceremonial bell tone, resonant, 4 seconds with natural decay]
        <break time="3s"/>
    </prosody>

The module includes a shared SFX library at assets/sfx/ for reusing effects
across sessions. Effects are matched by keywords/tags and cached for future use.

Usage:
    from scripts.core.sfx_sync import (
        parse_sfx_markers,
        align_sfx_to_voice,
        render_sfx_track,
        SFXLibrary
    )

    # Initialize library
    library = SFXLibrary()

    # Parse markers from script
    markers = parse_sfx_markers(ssml_content)

    # Align to voice timing
    aligned = align_sfx_to_voice(markers, voice_duration)

    # Render final SFX track (uses library for caching)
    sfx_audio = render_sfx_track(aligned, sample_rate=48000, library=library)
"""

import re
import json
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from scipy.io import wavfile
import yaml


@dataclass
class SFXMarker:
    """Represents a single sound effect marker in the script."""
    effect_name: str
    parameters: Dict[str, Any]
    text_position: int              # Character position in original script
    surrounding_text: str           # Context around the marker
    description: str = ""           # Natural language description
    audio_time: float = 0.0         # Calculated time in audio (seconds)
    duration: float = 2.0           # Effect duration in seconds
    offset: float = 0.0             # Offset from trigger point
    library_match: Optional[str] = None  # Matched effect from library


@dataclass
class SFXTimeline:
    """Collection of aligned SFX markers."""
    markers: List[SFXMarker] = field(default_factory=list)
    total_duration: float = 0.0
    sample_rate: int = 48000


# =============================================================================
# SFX LIBRARY
# =============================================================================

class SFXLibrary:
    """
    Manages the shared SFX library at assets/sfx/.

    Provides lookup by keywords/tags and caching of generated effects.
    """

    def __init__(self, library_path: str = None):
        """Initialize the library."""
        if library_path is None:
            # Find project root
            self.library_root = Path(__file__).parent.parent.parent / "assets" / "sfx"
        else:
            self.library_root = Path(library_path)

        self.registry_path = self.library_root / "library.yaml"
        self.registry = {}
        self._load_registry()

    def _load_registry(self):
        """Load the library registry from YAML."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = yaml.safe_load(f) or {}

    def _save_registry(self):
        """Save the library registry to YAML."""
        self.library_root.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.registry, f, default_flow_style=False, sort_keys=False)

    def find_effect(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Find an effect in the library matching the description.

        Uses keyword matching against tags and keywords in the registry.

        Args:
            description: Natural language description of the effect

        Returns:
            Effect definition dict or None if not found
        """
        description_lower = description.lower()

        # Search all categories
        best_match = None
        best_score = 0

        for category, effects in self.registry.items():
            if category in ('version', 'sample_rate'):
                continue
            if not isinstance(effects, list):
                continue

            for effect in effects:
                score = self._match_score(description_lower, effect)
                if score > best_score:
                    best_score = score
                    best_match = effect

        # Require minimum match score
        if best_score >= 2:
            return best_match

        return None

    def _match_score(self, description: str, effect: Dict) -> int:
        """Calculate match score between description and effect."""
        score = 0

        # Check keywords (highest priority)
        for keyword in effect.get('keywords', []):
            if keyword.lower() in description:
                score += 5

        # Check tags
        for tag in effect.get('tags', []):
            if tag.lower() in description:
                score += 2

        # Check effect name
        name = effect.get('name', '').lower().replace('_', ' ')
        if name in description:
            score += 3

        return score

    def get_effect_path(self, effect: Dict) -> Optional[Path]:
        """Get the full path to an effect's audio file."""
        file_path = effect.get('file')
        if file_path:
            full_path = self.library_root / file_path
            if full_path.exists():
                return full_path
        return None

    def save_effect(
        self,
        category: str,
        name: str,
        audio: np.ndarray,
        sample_rate: int,
        tags: List[str],
        keywords: List[str],
        duration: float,
        generator: str = None,
        params: Dict = None
    ) -> str:
        """
        Save a generated effect to the library.

        Args:
            category: Effect category (bells, impacts, etc.)
            name: Effect name (snake_case)
            audio: Audio data as numpy array
            sample_rate: Audio sample rate
            tags: List of tags for matching
            keywords: List of keywords for matching
            duration: Duration in seconds
            generator: Generator function name
            params: Generator parameters

        Returns:
            Path to saved file
        """
        # Create category directory
        category_dir = self.library_root / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Save audio file
        file_name = f"{name}.wav"
        file_path = category_dir / file_name

        # Convert to int16 for WAV
        if audio.dtype != np.int16:
            audio_int16 = (audio * 32767).astype(np.int16)
        else:
            audio_int16 = audio

        wavfile.write(str(file_path), sample_rate, audio_int16)

        # Update registry
        if category not in self.registry:
            self.registry[category] = []

        # Check if effect already exists
        existing = None
        for i, eff in enumerate(self.registry[category]):
            if eff.get('name') == name:
                existing = i
                break

        effect_entry = {
            'name': name,
            'file': f"{category}/{file_name}",
            'duration': duration,
            'tags': tags,
            'keywords': keywords,
        }
        if generator:
            effect_entry['generator'] = generator
        if params:
            effect_entry['params'] = params

        if existing is not None:
            self.registry[category][existing] = effect_entry
        else:
            self.registry[category].append(effect_entry)

        self._save_registry()

        print(f"💾 Saved effect to library: {file_path}")
        return str(file_path)


# =============================================================================
# SFX MARKER PARSING
# =============================================================================

def parse_sfx_markers(ssml_content: str, library: SFXLibrary = None) -> List[SFXMarker]:
    """
    Extract SFX markers from SSML script content.

    Supports two formats:
    1. Structured: [[SFX:effect_name:param1=value1,param2=value2]]
    2. Natural language: [SFX: Description of sound, duration, notes]

    Args:
        ssml_content: Full SSML script content
        library: Optional SFXLibrary for matching effects

    Returns:
        List of SFXMarker objects
    """
    markers = []

    # Parse structured format markers
    markers.extend(_parse_structured_markers(ssml_content))

    # Parse natural language format markers
    markers.extend(_parse_natural_markers(ssml_content, library))

    # Sort by position
    markers.sort(key=lambda m: m.text_position)

    return markers


def _parse_structured_markers(ssml_content: str) -> List[SFXMarker]:
    """Parse structured format [[SFX:effect_name:params]] markers."""
    markers = []
    pattern = r'\[\[SFX:(\w+)(?::([^\]]+))?\]\]'

    for match in re.finditer(pattern, ssml_content):
        effect_name = match.group(1)
        params_str = match.group(2) or ""
        params = _parse_params(params_str)

        context = _get_context(ssml_content, match.start(), match.end())

        marker = SFXMarker(
            effect_name=effect_name,
            parameters=params,
            text_position=match.start(),
            surrounding_text=context,
            description="",
            duration=_parse_duration(params.get('duration', '2s')),
            offset=_parse_duration(params.get('offset', '0s'))
        )
        markers.append(marker)

    return markers


def _parse_natural_markers(ssml_content: str, library: SFXLibrary = None) -> List[SFXMarker]:
    """Parse natural language format [SFX: Description] markers."""
    markers = []
    pattern = r'\[SFX:\s*([^\]]+)\]'

    for match in re.finditer(pattern, ssml_content):
        description = match.group(1).strip()

        # Skip if this was already matched by structured pattern
        if '[[SFX:' in ssml_content[max(0, match.start()-1):match.start()+2]:
            continue

        # Parse natural language description
        params, effect_name, duration = _parse_natural_description(description)
        context = _get_context(ssml_content, match.start(), match.end())

        # Try to match in library and merge params
        library_match, duration, params = _apply_library_match(
            library, description, duration, params
        )

        marker = SFXMarker(
            effect_name=effect_name,
            parameters=params,
            text_position=match.start(),
            surrounding_text=context,
            description=description,
            duration=duration,
            offset=params.get('offset', 0.0),
            library_match=library_match
        )
        markers.append(marker)

    return markers


def _get_context(content: str, start: int, end: int, context_size: int = 50) -> str:
    """Get surrounding context for a match."""
    ctx_start = max(0, start - context_size)
    ctx_end = min(len(content), end + context_size)
    return content[ctx_start:ctx_end]


def _apply_library_match(
    library: SFXLibrary,
    description: str,
    duration: float,
    params: Dict[str, Any]
) -> Tuple[Optional[str], float, Dict[str, Any]]:
    """Try to match effect in library and merge params."""
    if not library:
        return None, duration, params

    lib_effect = library.find_effect(description)
    if not lib_effect:
        return None, duration, params

    library_match = lib_effect.get('name')

    # Use library duration if not specified (default is 2.0)
    if abs(duration - 2.0) < 0.001 and 'duration' in lib_effect:
        duration = lib_effect['duration']

    # Merge library params (don't override existing)
    lib_params = lib_effect.get('params', {})
    for k, v in lib_params.items():
        if k not in params:
            params[k] = v

    return library_match, duration, params


def _parse_natural_description(description: str) -> Tuple[Dict[str, Any], str, float]:
    """
    Parse a natural language SFX description.

    Examples:
        "Deep ceremonial bell tone, resonant, 4 seconds with natural decay"
        "MASSIVE hammer strike on metal - deep, resonant, reverberant, 3 seconds"
        "Distant volcanic rumble, very low, 5 seconds, fade in from silence"

    Returns:
        (parameters dict, inferred effect name, duration)
    """
    description_lower = description.lower()

    # Extract duration
    duration = _extract_duration_from_description(description_lower)

    # Detect effect type and get type-specific params
    effect_name, type_params = _detect_effect_type(description_lower)

    # Get modifier params
    modifier_params = _extract_modifiers(description_lower, duration)

    # Combine params
    params = {'duration': duration}
    params.update(type_params)
    params.update(modifier_params)

    return params, effect_name, duration


def _extract_duration_from_description(description_lower: str) -> float:
    """Extract duration in seconds from description text."""
    duration_patterns = [
        r'(\d+(?:\.\d+)?)\s*seconds?',
        r'(\d+(?:\.\d+)?)\s*sec',
        r'(\d+(?:\.\d+)?)\s*s\b',
    ]
    for pattern in duration_patterns:
        match = re.search(pattern, description_lower)
        if match:
            return float(match.group(1))
    return 2.0  # Default duration


# Effect type detection rules: (keywords, effect_name, param_extractor)
EFFECT_TYPE_RULES = [
    (['bell', 'chime', 'gong', 'singing bowl'], 'bell', '_get_bell_params'),
    (['hammer', 'strike', 'clang', 'impact'], 'impact', '_get_impact_params'),
    (['fire', 'flame', 'crackle', 'burning'], 'fire', '_get_fire_params'),
    (['footstep', 'step', 'walking'], 'footstep', '_get_footstep_params'),
    (['ambient', 'atmosphere', 'continuous', 'rumble'], 'ambient', None),
    (['whoosh', 'wind', 'breath', 'bellows'], 'whoosh', None),
    (['heartbeat', 'heart', 'drum', 'pulse'], 'heartbeat', '_get_heartbeat_params'),
    (['metal', 'resonan', 'hum', 'tone'], 'resonance', None),
    (['ethereal', 'magical', 'whisper', 'ancient', 'mystical'], 'mystical', None),
]


def _detect_effect_type(description_lower: str) -> Tuple[str, Dict[str, Any]]:
    """Detect effect type from keywords and extract type-specific params."""
    for keywords, effect_name, param_func in EFFECT_TYPE_RULES:
        if any(kw in description_lower for kw in keywords):
            params = {}
            if param_func:
                param_extractor = globals().get(param_func)
                if param_extractor:
                    params = param_extractor(description_lower)
            return effect_name, params
    return 'unknown', {}


def _get_bell_params(description_lower: str) -> Dict[str, Any]:
    """Extract bell-specific parameters."""
    if 'deep' in description_lower or 'low' in description_lower:
        return {'frequency': 120}
    if 'bright' in description_lower or 'clear' in description_lower:
        return {'frequency': 440}
    return {'frequency': 220}


def _get_impact_params(description_lower: str) -> Dict[str, Any]:
    """Extract impact-specific parameters."""
    if 'massive' in description_lower:
        return {'intensity': 1.0, 'low_freq': 60}
    if 'distant' in description_lower:
        return {'intensity': 0.4, 'reverb': 0.7}
    return {}


def _get_fire_params(description_lower: str) -> Dict[str, Any]:
    """Extract fire-specific parameters."""
    if 'burst' in description_lower:
        return {'envelope': 'burst'}
    if 'crackling' in description_lower:
        return {'crackling': True}
    return {}


def _get_footstep_params(description_lower: str) -> Dict[str, Any]:
    """Extract footstep-specific parameters."""
    if 'stone' in description_lower:
        return {'material': 'stone'}
    if 'metal' in description_lower:
        return {'material': 'metal'}
    return {}


def _get_heartbeat_params(description_lower: str) -> Dict[str, Any]:
    """Extract heartbeat-specific parameters."""
    bpm_match = re.search(r'(\d+)\s*bpm', description_lower)
    if bpm_match:
        return {'bpm': int(bpm_match.group(1))}
    return {'bpm': 60}


def _extract_modifiers(description_lower: str, duration: float) -> Dict[str, Any]:
    """Extract audio modifier parameters from description."""
    params = {}

    if 'fade in' in description_lower:
        params['fade_in'] = min(duration * 0.3, 2.0)

    if 'fade out' in description_lower or 'fading' in description_lower:
        params['fade_out'] = min(duration * 0.5, 3.0)

    if 'reverb' in description_lower or 'reverberant' in description_lower:
        params['reverb'] = 0.55

    if any(kw in description_lower for kw in ['soft', 'gentle', 'subtle']):
        params['gain_db'] = -18

    if any(kw in description_lower for kw in ['loud', 'massive']):
        params['gain_db'] = -8

    return params


def _parse_params(params_str: str) -> Dict[str, Any]:
    """Parse parameter string into dictionary."""
    params = {}
    if not params_str:
        return params

    for pair in params_str.split(','):
        if '=' in pair:
            key, value = pair.strip().split('=', 1)
            params[key.strip()] = _parse_value(value.strip())

    return params


def _parse_value(value: str) -> Any:
    """Parse a parameter value to appropriate type."""
    # Boolean
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'

    # Duration (e.g., "3s", "500ms")
    if value.endswith('s') and not value.endswith('ms'):
        try:
            return float(value[:-1])
        except ValueError:
            pass
    if value.endswith('ms'):
        try:
            return float(value[:-2]) / 1000
        except ValueError:
            pass

    # Frequency (e.g., "528hz")
    if value.lower().endswith('hz'):
        try:
            return float(value[:-2])
        except ValueError:
            pass

    # Number
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # String
    return value


def _parse_duration(value) -> float:
    """Parse duration value to seconds."""
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        if value.endswith('ms'):
            return float(value[:-2]) / 1000
        elif value.endswith('s'):
            return float(value[:-1])
        try:
            return float(value)
        except ValueError:
            return 2.0

    return 2.0


# =============================================================================
# SFX TIMING ALIGNMENT
# =============================================================================

def align_sfx_to_voice(
    markers: List[SFXMarker],
    voice_duration: float,
    ssml_content: str
) -> SFXTimeline:
    """
    Calculate audio timing for each SFX marker based on its position in the script.

    Uses a simple linear model: position in text corresponds proportionally
    to position in audio. More sophisticated timing can be achieved by
    parsing SSML break tags.

    Args:
        markers: List of SFX markers from parse_sfx_markers
        voice_duration: Total duration of voice audio in seconds
        ssml_content: Original SSML content for timing calculation

    Returns:
        SFXTimeline with calculated audio times
    """
    # Remove SSML tags to get raw text length
    text_only = re.sub(r'<[^>]+>', '', ssml_content)
    text_only = re.sub(r'\[\[SFX:[^\]]+\]\]', '', text_only)
    total_text_length = len(text_only)

    timeline = SFXTimeline(
        markers=[],
        total_duration=voice_duration
    )

    for marker in markers:
        # Calculate relative position in text
        # Account for removed SFX markers before this position
        adjusted_pos = _adjust_position_for_markers(
            marker.text_position, ssml_content
        )

        # Estimate time from text position (linear model)
        text_ratio = adjusted_pos / max(total_text_length, 1)
        base_time = text_ratio * voice_duration

        # Apply offset from parameters
        marker.audio_time = max(0, base_time + marker.offset)

        # Account for SSML breaks before this marker
        break_time = _calculate_break_time_before(marker.text_position, ssml_content)
        marker.audio_time += break_time

        timeline.markers.append(marker)

    # Sort by audio time
    timeline.markers.sort(key=lambda m: m.audio_time)

    return timeline


def _adjust_position_for_markers(position: int, content: str) -> int:
    """Adjust text position accounting for removed tags and markers."""
    # Count characters of tags/markers before this position
    prefix = content[:position]

    # Remove all SSML tags
    prefix_clean = re.sub(r'<[^>]+>', '', prefix)

    # Remove SFX markers
    prefix_clean = re.sub(r'\[\[SFX:[^\]]+\]\]', '', prefix_clean)

    return len(prefix_clean)


def _calculate_break_time_before(position: int, content: str) -> float:
    """Calculate total break time from SSML break tags before position."""
    prefix = content[:position]

    # Find all break tags
    break_pattern = r'<break\s+time="(\d+(?:\.\d+)?)(s|ms)"'
    total_break_time = 0.0

    for match in re.finditer(break_pattern, prefix):
        value = float(match.group(1))
        unit = match.group(2)
        if unit == 'ms':
            value /= 1000
        total_break_time += value

    return total_break_time


# =============================================================================
# SFX RENDERING
# =============================================================================

# Built-in effect generators
def _generate_bell(
    duration: float,
    freq: float = 528,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate a bell/chime tone."""
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)

    # Fundamental and overtones
    fundamental = np.sin(2 * np.pi * freq * t)
    overtone1 = 0.5 * np.sin(2 * np.pi * freq * 2.0 * t)
    overtone2 = 0.25 * np.sin(2 * np.pi * freq * 3.0 * t)

    tone = fundamental + overtone1 + overtone2

    # Exponential decay envelope
    envelope = np.exp(-t * 2.0)
    tone = tone * envelope

    # Normalize
    tone = tone / np.max(np.abs(tone)) * 0.7

    return tone


def _generate_ambient_hum(
    duration: float,
    freq: float = 100,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate a low ambient hum."""
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)

    # Multiple low frequencies for richness
    hum = (
        0.5 * np.sin(2 * np.pi * freq * t) +
        0.3 * np.sin(2 * np.pi * freq * 1.5 * t) +
        0.2 * np.sin(2 * np.pi * freq * 0.5 * t)
    )

    # Slow modulation
    modulation = 0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t)
    hum = hum * modulation

    # Fade in/out
    fade_samples = int(sample_rate * 0.5)
    hum[:fade_samples] *= np.linspace(0, 1, fade_samples)
    hum[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return hum * 0.4


def _generate_whoosh(
    duration: float,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate a whoosh/wind effect."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Filtered noise (using modern Generator API with seed for reproducibility)
    rng = np.random.default_rng(seed=42)
    noise = rng.standard_normal(samples).astype(np.float32)

    # Simple lowpass via moving average
    window_size = int(sample_rate * 0.01)
    kernel = np.ones(window_size) / window_size
    filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)

    # Envelope: rise and fall
    envelope = np.sin(np.pi * t / duration) ** 2
    whoosh = filtered * envelope * 0.5

    return whoosh


def _generate_heartbeat(
    duration: float,
    bpm: float = 60,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate a heartbeat rhythm."""
    samples = int(sample_rate * duration)
    output = np.zeros(samples, dtype=np.float32)

    beat_interval = 60.0 / bpm
    beat_samples = int(beat_interval * sample_rate)

    # Single beat waveform (two thuds)
    beat_duration = 0.15
    beat_t = np.linspace(0, beat_duration, int(sample_rate * beat_duration))

    # First thud (louder)
    thud1 = np.sin(2 * np.pi * 40 * beat_t) * np.exp(-beat_t * 30)
    # Second thud (softer, 0.1s later)
    thud2 = 0.6 * np.sin(2 * np.pi * 40 * beat_t) * np.exp(-beat_t * 35)

    # Combine into single beat pattern
    beat_pattern_len = int(sample_rate * 0.3)
    beat_pattern = np.zeros(beat_pattern_len, dtype=np.float32)
    beat_pattern[:len(thud1)] = thud1
    offset = int(sample_rate * 0.12)
    beat_pattern[offset:offset + len(thud2)] += thud2

    # Place beats throughout duration
    pos = 0
    while pos + len(beat_pattern) < samples:
        output[pos:pos + len(beat_pattern)] += beat_pattern
        pos += beat_samples

    return output * 0.6


def _generate_impact(
    duration: float,
    low_freq: float = 60,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate a heavy impact sound (hammer strike, metallic clang)."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Low frequency thump
    thump = np.sin(2 * np.pi * low_freq * t)
    thump_envelope = np.exp(-t * 8)  # Fast decay

    # Metallic resonance (multiple high frequencies)
    resonance = (
        0.4 * np.sin(2 * np.pi * 220 * t) +
        0.3 * np.sin(2 * np.pi * 440 * t) +
        0.2 * np.sin(2 * np.pi * 880 * t)
    )
    resonance_envelope = np.exp(-t * 3)  # Slower decay for ring

    # Noise burst for attack transient
    rng = np.random.default_rng(seed=42)
    noise = rng.standard_normal(samples).astype(np.float32)
    noise_envelope = np.exp(-t * 50)  # Very fast decay

    impact = (
        thump * thump_envelope * 0.6 +
        resonance * resonance_envelope * 0.3 +
        noise * noise_envelope * 0.2
    )

    # Normalize
    max_val = np.max(np.abs(impact))
    if max_val > 0:
        impact = impact / max_val * 0.8

    return impact


def _generate_fire(
    duration: float,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate fire crackling/burning sounds."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    rng = np.random.default_rng(seed=42)

    # Base crackling noise
    noise = rng.standard_normal(samples).astype(np.float32)

    # Bandpass filter simulation (keep mid-high frequencies)
    window_size = int(sample_rate * 0.002)
    kernel = np.ones(window_size) / window_size
    filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)

    # Random amplitude modulation for crackling effect
    crackle_rate = 20  # Hz - rate of crackling
    crackle_mod = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * crackle_rate * t + rng.random() * 2 * np.pi))

    # Add some low rumble
    rumble = 0.2 * np.sin(2 * np.pi * 30 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * t))

    fire = filtered * crackle_mod * 0.4 + rumble

    # Fade in/out
    fade_samples = int(sample_rate * 0.3)
    if fade_samples > 0 and len(fire) > fade_samples * 2:
        fire[:fade_samples] *= np.linspace(0, 1, fade_samples)
        fire[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return fire * 0.5


def _generate_ambient(
    duration: float,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate ambient atmosphere (cave, volcanic, etc.)."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    rng = np.random.default_rng(seed=42)

    # Low drone
    drone = (
        0.4 * np.sin(2 * np.pi * 50 * t) +
        0.3 * np.sin(2 * np.pi * 75 * t) +
        0.2 * np.sin(2 * np.pi * 100 * t)
    )

    # Slow modulation
    mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
    drone = drone * mod

    # Subtle noise layer
    noise = rng.standard_normal(samples).astype(np.float32)
    window_size = int(sample_rate * 0.02)
    kernel = np.ones(window_size) / window_size
    filtered_noise = np.convolve(noise, kernel, mode='same').astype(np.float32) * 0.1

    ambient = drone * 0.4 + filtered_noise

    # Long fade in/out
    fade_samples = int(sample_rate * 0.5)
    if fade_samples > 0 and len(ambient) > fade_samples * 2:
        ambient[:fade_samples] *= np.linspace(0, 1, fade_samples)
        ambient[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return ambient


def _generate_resonance(
    duration: float,
    freq: float = 200,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate metallic resonance/singing bowl type sound."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Fundamental and harmonics (singing bowl style)
    tone = (
        1.0 * np.sin(2 * np.pi * freq * t) +
        0.6 * np.sin(2 * np.pi * freq * 2.0 * t) +
        0.4 * np.sin(2 * np.pi * freq * 2.71 * t) +  # Non-harmonic for metallic quality
        0.3 * np.sin(2 * np.pi * freq * 3.5 * t) +
        0.2 * np.sin(2 * np.pi * freq * 4.2 * t)
    )

    # Slow amplitude modulation (beating effect)
    beat = 0.9 + 0.1 * np.sin(2 * np.pi * 0.5 * t)
    tone = tone * beat

    # Long exponential decay
    envelope = np.exp(-t * 0.8)
    tone = tone * envelope

    # Normalize
    max_val = np.max(np.abs(tone))
    if max_val > 0:
        tone = tone / max_val * 0.7

    return tone


def _generate_footstep(
    duration: float,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate footstep on stone/metal surface."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    rng = np.random.default_rng(seed=42)

    # Initial impact noise burst
    noise = rng.standard_normal(samples).astype(np.float32)

    # Very fast attack and decay for footstep
    attack_samples = int(sample_rate * 0.02)
    impact_envelope = np.zeros(samples, dtype=np.float32)
    if attack_samples > 0:
        impact_envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    decay_envelope = np.exp(-t * 15)
    envelope = np.minimum(impact_envelope + decay_envelope, 1.0)

    # Add some low thump
    thump = np.sin(2 * np.pi * 80 * t) * np.exp(-t * 20) * 0.5

    # Bandpass for stone-like quality
    window_size = int(sample_rate * 0.003)
    kernel = np.ones(window_size) / window_size
    filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)

    footstep = filtered * envelope * 0.6 + thump

    # Short reverb tail simulation
    reverb_samples = int(sample_rate * 0.15)
    if reverb_samples > 0 and len(footstep) > reverb_samples:
        reverb_tail = np.zeros(samples, dtype=np.float32)
        for i in range(3):
            delay = int(sample_rate * (0.03 + i * 0.02))
            if delay < samples:
                reverb_tail[delay:] += footstep[:-delay] * (0.3 - i * 0.1)
        footstep += reverb_tail * 0.3

    return footstep * 0.7


def _generate_mystical(
    duration: float,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate mystical/ethereal transition sound."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    rng = np.random.default_rng(seed=42)

    # Rising/falling shimmer (frequency sweep)
    sweep_start = 200
    sweep_end = 800
    freq_sweep = sweep_start + (sweep_end - sweep_start) * np.sin(np.pi * t / duration)
    phase = 2 * np.pi * np.cumsum(freq_sweep) / sample_rate
    shimmer = np.sin(phase)

    # Add harmonics
    shimmer += 0.5 * np.sin(phase * 2)
    shimmer += 0.25 * np.sin(phase * 3)

    # Soft modulation
    mod = 0.7 + 0.3 * np.sin(2 * np.pi * 2 * t)
    shimmer = shimmer * mod

    # Breathy noise texture
    noise = rng.standard_normal(samples).astype(np.float32)
    window_size = int(sample_rate * 0.01)
    kernel = np.ones(window_size) / window_size
    filtered_noise = np.convolve(noise, kernel, mode='same').astype(np.float32) * 0.15

    mystical = shimmer * 0.5 + filtered_noise

    # Bell-shaped envelope (fade in and out)
    sin_envelope = np.sin(np.pi * t / duration)
    # Avoid negative values from floating point errors
    sin_envelope = np.maximum(sin_envelope, 0)
    envelope = np.sqrt(sin_envelope)
    mystical = mystical * envelope

    # Normalize
    max_val = np.max(np.abs(mystical))
    if max_val > 0:
        mystical = mystical / max_val * 0.6

    return mystical


def _generate_drum(
    duration: float,
    freq: float = 60,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate deep drum hit."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Low frequency thump with pitch bend down
    pitch_bend = freq * np.exp(-t * 3)  # Pitch drops quickly
    phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
    thump = np.sin(phase)

    # Fast attack, medium decay envelope
    envelope = np.exp(-t * 4)

    drum = thump * envelope

    return drum * 0.7


def _generate_transition(
    duration: float,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate a smooth transition/crossfade sound."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Gentle rising tone
    freq_start = 150
    freq_end = 300
    freq = freq_start + (freq_end - freq_start) * (t / duration)
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    tone = np.sin(phase)

    # Add soft harmonics
    tone += 0.3 * np.sin(phase * 2)

    # Smooth envelope
    envelope = np.sin(np.pi * t / duration)
    tone = tone * envelope * 0.4

    return tone


# Effect generator registry
EFFECT_GENERATORS = {
    # Bells and chimes
    'bell': _generate_bell,
    'bell_chime': _generate_bell,
    'chime': _generate_bell,
    'gong': lambda d, sr=48000: _generate_bell(d, freq=120, sample_rate=sr),
    'singing_bowl': lambda d, sr=48000: _generate_resonance(d, freq=440, sample_rate=sr),

    # Ambient and atmosphere
    'hum': _generate_ambient_hum,
    'ambient_hum': _generate_ambient_hum,
    'ambient': _generate_ambient,
    'atmosphere': _generate_ambient,
    'drone': _generate_ambient,
    'rumble': _generate_ambient,
    'volcanic': _generate_ambient,
    'cave': _generate_ambient,

    # Wind and whoosh
    'whoosh': _generate_whoosh,
    'wind': _generate_whoosh,
    'breath': _generate_whoosh,
    'air': _generate_whoosh,

    # Impacts and strikes
    'impact': _generate_impact,
    'hammer': _generate_impact,
    'hammer_strike': _generate_impact,
    'strike': _generate_impact,
    'clang': _generate_impact,
    'metallic_impact': _generate_impact,
    'anvil': _generate_impact,

    # Fire effects
    'fire': _generate_fire,
    'flame': _generate_fire,
    'crackle': _generate_fire,
    'burning': _generate_fire,
    'molten': _generate_fire,
    'magma': _generate_fire,
    'lava': _generate_fire,

    # Metallic resonance
    'resonance': _generate_resonance,
    'metallic': _generate_resonance,
    'ring': _generate_resonance,
    'shimmer': _generate_resonance,
    'crystallize': _generate_resonance,
    'harmonic': _generate_resonance,

    # Footsteps
    'footstep': _generate_footstep,
    'step': _generate_footstep,
    'footfall': _generate_footstep,
    'stone_step': _generate_footstep,
    'metal_step': _generate_footstep,

    # Mystical and ethereal
    'mystical': _generate_mystical,
    'ethereal': _generate_mystical,
    'transition': _generate_transition,
    'merge': _generate_mystical,
    'whisper': _generate_mystical,
    'ancient': _generate_mystical,
    'sacred': _generate_mystical,

    # Drums and rhythm
    'heartbeat': _generate_heartbeat,
    'pulse': _generate_heartbeat,
    'drum': _generate_drum,
    'deep_drum': _generate_drum,
    'ritual_drum': _generate_drum,
}


def render_effect(
    effect_name: str,
    parameters: Dict[str, Any],
    sample_rate: int = 48000
) -> np.ndarray:
    """
    Render a single effect to audio.

    Args:
        effect_name: Name of the effect
        parameters: Effect parameters
        sample_rate: Audio sample rate

    Returns:
        Mono audio numpy array
    """
    duration = parameters.get('duration', 2.0)
    if isinstance(duration, str):
        duration = _parse_duration(duration)

    # Try to load from file first
    file_path = parameters.get('file')
    if file_path and Path(file_path).exists():
        _, audio = wavfile.read(file_path)
        audio = audio.astype(np.float32)
        if np.issubdtype(audio.dtype, np.integer):
            audio = audio / 32768.0
        # Take mono if stereo
        if len(audio.shape) > 1:
            audio = audio[:, 0]
        return audio

    # Use generator
    generator = EFFECT_GENERATORS.get(effect_name.lower())
    if generator:
        return generator(duration, sample_rate=sample_rate)

    # Unknown effect - return silence with warning
    print(f"⚠️  Unknown SFX effect: {effect_name}, using silence")
    return np.zeros(int(sample_rate * duration), dtype=np.float32)


def render_sfx_track(
    timeline: SFXTimeline,
    sample_rate: int = 48000
) -> np.ndarray:
    """
    Render all SFX markers to a single audio track.

    Args:
        timeline: Aligned SFX timeline
        sample_rate: Output sample rate

    Returns:
        Stereo audio numpy array (samples, 2)
    """
    total_samples = int(timeline.total_duration * sample_rate)
    output = np.zeros((total_samples, 2), dtype=np.float32)

    for marker in timeline.markers:
        # Render the effect
        effect_audio = render_effect(
            marker.effect_name,
            marker.parameters,
            sample_rate
        )

        # Apply fade in/out if specified
        fade_in = marker.parameters.get('fade_in', 0.1)
        fade_out = marker.parameters.get('fade_out', 0.3)
        if isinstance(fade_in, str):
            fade_in = _parse_duration(fade_in)
        if isinstance(fade_out, str):
            fade_out = _parse_duration(fade_out)

        fade_in_samples = int(fade_in * sample_rate)
        fade_out_samples = int(fade_out * sample_rate)

        if fade_in_samples > 0 and fade_in_samples < len(effect_audio):
            effect_audio[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)
        if fade_out_samples > 0 and fade_out_samples < len(effect_audio):
            effect_audio[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)

        # Apply gain - default to 0 dB (unity) so SFX are audible
        # Individual effects can specify lower gain if needed
        gain_db = marker.parameters.get('gain_db', 0)
        gain_linear = 10 ** (gain_db / 20)
        effect_audio = effect_audio * gain_linear

        # Place in output at correct time
        start_sample = int(marker.audio_time * sample_rate)
        end_sample = start_sample + len(effect_audio)

        if end_sample > total_samples:
            effect_audio = effect_audio[:total_samples - start_sample]
            end_sample = total_samples

        if start_sample < total_samples:
            # Center pan (mono to stereo)
            output[start_sample:end_sample, 0] += effect_audio
            output[start_sample:end_sample, 1] += effect_audio

    return output


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def process_script_sfx(
    ssml_path: str,
    voice_audio_path: str,
    output_path: str,
    sample_rate: int = 48000,
    library: SFXLibrary = None
) -> Optional[str]:
    """
    Complete SFX processing pipeline.

    Args:
        ssml_path: Path to SSML script
        voice_audio_path: Path to generated voice audio
        output_path: Path for output SFX track
        sample_rate: Audio sample rate
        library: Optional SFXLibrary for effect lookup/caching

    Returns:
        Path to rendered SFX track, or None if no markers found
    """
    # Read SSML
    with open(ssml_path, 'r', encoding='utf-8') as f:
        ssml_content = f.read()

    # Get voice duration (support both WAV and MP3)
    voice_path = Path(voice_audio_path)
    if voice_path.suffix.lower() == '.mp3':
        # Use ffprobe for MP3 duration
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', str(voice_path)],
            capture_output=True, text=True
        )
        voice_duration = float(result.stdout.strip())
    else:
        file_sr, voice_audio = wavfile.read(voice_audio_path)
        voice_duration = len(voice_audio) / file_sr

    # Parse markers
    markers = parse_sfx_markers(ssml_content, library)
    if not markers:
        print("No SFX markers found in script")
        return None

    print(f"Found {len(markers)} SFX markers:")
    for m in markers:
        print(f"  - {m.effect_name}: {m.parameters}")

    # Align to voice timing
    timeline = align_sfx_to_voice(markers, voice_duration, ssml_content)
    timeline.sample_rate = sample_rate
    timeline.total_duration = voice_duration

    print("\nAligned SFX timeline:")
    for m in timeline.markers:
        print(f"  {m.audio_time:.2f}s: {m.effect_name}")

    # Render SFX track
    sfx_audio = render_sfx_track(timeline, sample_rate)

    # Save
    # Convert to int16 for WAV output
    sfx_int16 = (sfx_audio * 32767).astype(np.int16)
    wavfile.write(output_path, sample_rate, sfx_int16)

    print(f"\n✅ SFX track saved to: {output_path}")
    return output_path


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 4:
        print("Usage: python sfx_sync.py <script.ssml> <voice.wav> <output_sfx.wav>")
        print("\nExample:")
        print("  python sfx_sync.py session/script.ssml session/output/voice.wav session/output/sfx.wav")
        sys.exit(1)

    ssml_path = sys.argv[1]
    voice_path = sys.argv[2]
    output_path = sys.argv[3]

    process_script_sfx(ssml_path, voice_path, output_path)
