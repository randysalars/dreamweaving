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
    # Original categories
    (['bell', 'chime', 'gong', 'singing bowl'], 'bell', '_get_bell_params'),
    (['hammer', 'strike', 'clang', 'impact'], 'impact', '_get_impact_params'),
    (['fire', 'flame', 'crackle', 'burning', 'torch', 'ember'], 'fire', '_get_fire_params'),
    (['footstep', 'step', 'walking'], 'footstep', '_get_footstep_params'),
    (['ambient', 'atmosphere', 'continuous', 'rumble'], 'ambient', None),
    (['whoosh', 'wind', 'breath', 'bellows'], 'whoosh', None),
    (['heartbeat', 'heart', 'pulse'], 'heartbeat', '_get_heartbeat_params'),
    (['metal', 'resonan', 'hum', 'tone'], 'resonance', None),
    (['ethereal', 'magical', 'whisper', 'ancient', 'mystical'], 'mystical', None),

    # NEW: Atmospheric textures
    (['air', 'ether', 'shimmer', 'liminal', 'vortex', 'swirl'], 'atmospheric', None),

    # NEW: Water & fluid
    (['ocean', 'wave', 'stream', 'brook', 'rain', 'underwater', 'ripple', 'drip', 'water'], 'water', None),

    # NEW: Earth & grounding
    (['earth', 'ground', 'stone', 'rock', 'cavern', 'cave', 'tectonic'], 'earth', None),

    # NEW: Light effects
    (['solar', 'sunlight', 'radiant', 'glow', 'light'], 'light', None),

    # NEW: Celestial & heavenly
    (['celestial', 'angelic', 'heavenly', 'cosmic', 'stardust', 'prismatic', 'divine', 'portal'], 'celestial', None),

    # NEW: Presence & spirit
    (['presence', 'spirit', 'guide', 'entity', 'cloak', 'overtone', 'throat'], 'presence', None),

    # NEW: Advanced experimental
    (['fractal', 'spectral', 'lunar', 'solar', 'astral', 'field', 'particle'], 'advanced', None),

    # NEW: Transitions & portals
    (['transition', 'portal', 'shift', 'transform', 'vacuum', 'riser'], 'transition', None),

    # ENHANCED: Drums - various types
    (['drum', 'frame drum', 'shamanic', 'bodhran', 'buffalo'], 'drum', None),
    (['djembe', 'dunun', 'talking drum', 'african'], 'drum', None),
    (['daf', 'riqq', 'tabla', 'doumbek', 'persian', 'arabic'], 'drum', None),
    (['taiko', 'odaiko', 'shime', 'japanese drum'], 'drum', None),
    (['cinematic', 'epic drum', 'tom', 'earthquake'], 'drum', None),
    (['stretched drum', 'granular drum', 'experimental drum', 'spectral drum'], 'drum', None),
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


def _generate_atmospheric(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Generate atmospheric textures: wind, sweeps, breath, shimmer, pads, whispers, vortex.

    Args:
        duration: Duration in seconds
        sample_rate: Audio sample rate
        params: Dict with 'type' and type-specific parameters
    """
    params = params or {}
    atmo_type = params.get('type', 'wind')
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    if atmo_type == 'wind':
        # Soft ethereal wind bed
        intensity = params.get('intensity', 0.3)
        filter_hz = params.get('filter_hz', 2000)
        noise = rng.standard_normal(samples).astype(np.float32)
        # Lowpass via moving average
        window = int(sample_rate / filter_hz)
        kernel = np.ones(max(window, 1)) / max(window, 1)
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        # Slow modulation
        mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
        output = filtered * mod * intensity

    elif atmo_type == 'sweep':
        # Ethereal rising sweep
        rise_time = params.get('rise_time', 4.0)
        filter_hz = params.get('filter_hz', 4000)
        freq_start = 100
        freq_end = filter_hz
        freq = freq_start + (freq_end - freq_start) * (t / duration) ** 0.5
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        sweep = np.sin(phase) + 0.3 * np.sin(phase * 2)
        envelope = np.sin(np.pi * t / duration)
        output = sweep * envelope * 0.5

    elif atmo_type == 'breath':
        # Breathing texture
        cycle_sec = params.get('cycle_sec', 7.0)
        depth = params.get('depth', 0.6)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.01)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        breath_mod = 0.5 + 0.5 * np.sin(2 * np.pi * t / cycle_sec)
        output = filtered * breath_mod * depth * 0.4

    elif atmo_type == 'shimmer':
        # High frequency sparkle/shimmer
        freq_min = params.get('freq_min', 8000)
        freq_max = params.get('freq_max', 16000)
        noise = rng.standard_normal(samples).astype(np.float32)
        # Highpass effect via bandpass
        freq_center = (freq_min + freq_max) / 2
        tone1 = np.sin(2 * np.pi * freq_center * t)
        tone2 = np.sin(2 * np.pi * (freq_center * 1.2) * t)
        mod = 0.5 + 0.5 * rng.random(samples).astype(np.float32)
        output = (tone1 + tone2 * 0.5) * mod * 0.3

    elif atmo_type == 'pad':
        # Ambient liminal pad
        base_freq = params.get('base_freq', 220)
        harmonics = params.get('harmonics', [1.0, 0.3, 0.1])
        pad = np.zeros(samples, dtype=np.float32)
        for i, h in enumerate(harmonics):
            pad += h * np.sin(2 * np.pi * base_freq * (i + 1) * t)
        # Slow evolving modulation
        mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.02 * t)
        output = pad * mod * 0.4

    elif atmo_type == 'whisper':
        # Wind whisper resonance
        formant_freq = params.get('formant_freq', 1500)
        noise = rng.standard_normal(samples).astype(np.float32)
        # Resonant filter simulation
        resonance = np.sin(2 * np.pi * formant_freq * t) * 0.3
        window = int(sample_rate * 0.005)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t)
        output = (filtered * 0.4 + resonance) * mod * 0.5

    elif atmo_type == 'vortex':
        # Swirling vortex effect
        rotation_hz = params.get('rotation_hz', 0.1)
        depth = params.get('depth', 0.7)
        # Rotating stereo will be handled at mix level
        base = np.sin(2 * np.pi * 150 * t) + 0.5 * np.sin(2 * np.pi * 220 * t)
        rotation = np.sin(2 * np.pi * rotation_hz * t)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.01)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        output = (base * 0.4 + filtered * 0.3) * (0.5 + depth * 0.5 * rotation)

    else:
        output = np.zeros(samples, dtype=np.float32)

    # Fade in/out
    fade_samples = int(sample_rate * 0.5)
    if fade_samples > 0 and len(output) > fade_samples * 2:
        output[:fade_samples] *= np.linspace(0, 1, fade_samples)
        output[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return output


def _generate_water(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Generate water effects: ocean, stream, underwater, drip, bowl, rain, submerged, ripple.
    """
    params = params or {}
    water_type = params.get('type', 'ocean')
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    if water_type == 'ocean':
        # Gentle ocean wave lapping
        wave_period = params.get('wave_period', 8.0)
        intensity = params.get('intensity', 0.4)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.02)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        # Wave envelope
        wave_env = 0.5 + 0.5 * np.sin(2 * np.pi * t / wave_period)
        output = filtered * wave_env * intensity

    elif water_type == 'stream':
        # Brook/trickle
        flow_rate = params.get('flow_rate', 0.5)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.005)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        # Irregular flow modulation
        mod = 0.6 + 0.4 * np.sin(2 * np.pi * 3 * t) * np.sin(2 * np.pi * 0.2 * t)
        output = filtered * mod * flow_rate * 0.5

    elif water_type == 'underwater':
        # Muffled underwater pulse
        pulse_hz = params.get('pulse_hz', 1.0)
        depth = params.get('depth', 0.8)
        # Deep rumble with pulse
        rumble = np.sin(2 * np.pi * 40 * t) + 0.5 * np.sin(2 * np.pi * 60 * t)
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * pulse_hz * t)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.03)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        output = (rumble * 0.4 + filtered * 0.2) * pulse * depth

    elif water_type == 'drip_stretch':
        # Time-stretched water drip
        stretch_factor = params.get('stretch_factor', 8.0)
        # Single drip stretched out
        drip_samples = int(samples / stretch_factor)
        drip_t = np.linspace(0, 1, drip_samples)
        drip = np.sin(2 * np.pi * 1000 * drip_t) * np.exp(-drip_t * 10)
        # Stretch by interpolation
        output = np.interp(np.linspace(0, drip_samples, samples), np.arange(drip_samples), drip).astype(np.float32)
        # Add ethereal shimmer
        shimmer = np.sin(2 * np.pi * 2000 * t) * 0.2 * np.sin(np.pi * t / duration)
        output = output * 0.6 + shimmer

    elif water_type == 'bowl':
        # Tibetan water bowl
        freq = params.get('freq', 432)
        water_amount = params.get('water_amount', 0.5)
        # Bowl resonance with water modulation
        bowl = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.7 * t)
        water_mod = 1.0 + water_amount * 0.2 * np.sin(2 * np.pi * 3 * t)
        envelope = np.exp(-t * 0.5)
        output = bowl * water_mod * envelope * 0.6

    elif water_type == 'rain':
        # Rain on leaves/surfaces
        density = params.get('density', 0.4)
        noise = rng.standard_normal(samples).astype(np.float32)
        # High frequency drops
        window = int(sample_rate * 0.002)
        kernel = np.ones(window) / window
        drops = np.convolve(noise, kernel, mode='same').astype(np.float32)
        # Random patter modulation
        patter = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 8 * t + rng.random() * np.pi))
        output = drops * patter * density * 0.4

    elif water_type == 'submerged':
        # Submerged wash/rumble
        rumble_hz = params.get('rumble_hz', 40)
        rumble = np.sin(2 * np.pi * rumble_hz * t) + 0.5 * np.sin(2 * np.pi * rumble_hz * 1.5 * t)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.04)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t)
        output = (rumble * 0.5 + filtered * 0.3) * mod

    elif water_type == 'ripple':
        # Ripple sweep transition
        spread_rate = params.get('spread_rate', 2.0)
        freq_start = 800
        freq_end = 200
        freq = freq_start + (freq_end - freq_start) * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        ripple = np.sin(phase) * np.sin(np.pi * t / duration)
        output = ripple * 0.5

    else:
        output = np.zeros(samples, dtype=np.float32)

    # Fade in/out
    fade_samples = int(sample_rate * 0.3)
    if fade_samples > 0 and len(output) > fade_samples * 2:
        output[:fade_samples] *= np.linspace(0, 1, fade_samples)
        output[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return output


def _generate_earth(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Generate earth/grounding effects: rumble, groan, stone, cavern, chime, pulse.
    """
    params = params or {}
    earth_type = params.get('type', 'rumble')
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    if earth_type == 'rumble':
        # Deep earth rumble
        freq = params.get('freq', 30)
        decay = params.get('decay', 8.0)
        rumble = np.sin(2 * np.pi * freq * t) + 0.6 * np.sin(2 * np.pi * freq * 1.5 * t)
        rumble += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
        envelope = np.exp(-t / decay)
        output = rumble * envelope * 0.6

    elif earth_type == 'groan':
        # Earth crust groaning
        freq_range = params.get('freq_range', [20, 80])
        freq = freq_range[0] + (freq_range[1] - freq_range[0]) * np.sin(np.pi * t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        groan = np.sin(phase)
        # Add texture
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.05)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        output = groan * 0.5 + filtered * 0.2

    elif earth_type == 'stone':
        # Stone shifting sound
        mass = params.get('mass', 0.7)
        noise = rng.standard_normal(samples).astype(np.float32)
        # Rumbling stone
        stone = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 2)
        window = int(sample_rate * 0.01)
        kernel = np.ones(window) / window
        grit = np.convolve(noise, kernel, mode='same').astype(np.float32)
        envelope = np.sin(np.pi * t / duration)
        output = (stone * mass + grit * 0.3) * envelope * 0.6

    elif earth_type == 'cavern':
        # Cavern resonance
        size = params.get('size', 'large')
        reverb = params.get('reverb', 0.8)
        reverb_time = {'small': 1.0, 'medium': 2.0, 'large': 4.0}.get(size, 2.0)
        # Deep drone
        drone = np.sin(2 * np.pi * 60 * t) + 0.4 * np.sin(2 * np.pi * 90 * t)
        # Reverb tail simulation
        tail_samples = int(sample_rate * reverb_time)
        tail = np.exp(-np.linspace(0, reverb_time, tail_samples) * 2)
        if len(drone) > tail_samples:
            reverbed = np.convolve(drone, tail, mode='same')[:samples] * reverb
        else:
            reverbed = drone * reverb
        output = reverbed.astype(np.float32) * 0.4

    elif earth_type == 'chime':
        # Rock/stone chime (like lithophone)
        material = params.get('material', 'stone')
        freq = params.get('freq', 880)
        # Stone has less sustain than metal
        decay_rate = 5.0 if material == 'stone' else 2.0
        chime = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.3 * t)
        envelope = np.exp(-t * decay_rate)
        output = chime * envelope * 0.6

    elif earth_type == 'pulse':
        # Earth pulse/heartbeat
        freq = params.get('freq', 40)
        bpm = params.get('bpm', 60)
        beat_interval = 60.0 / bpm
        beat_samples = int(beat_interval * sample_rate)
        output = np.zeros(samples, dtype=np.float32)
        # Single earth pulse
        pulse_len = int(sample_rate * 0.3)
        pulse_t = np.linspace(0, 0.3, pulse_len)
        pulse = np.sin(2 * np.pi * freq * pulse_t) * np.exp(-pulse_t * 8)
        # Place pulses
        pos = 0
        while pos + pulse_len < samples:
            output[pos:pos + pulse_len] += pulse
            pos += beat_samples
        output *= 0.6

    else:
        output = np.zeros(samples, dtype=np.float32)

    # Fade in/out
    fade_samples = int(sample_rate * 0.3)
    if fade_samples > 0 and len(output) > fade_samples * 2:
        output[:fade_samples] *= np.linspace(0, 1, fade_samples)
        output[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return output


def _generate_light(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Generate light/solar effects: shimmer, radiance.
    """
    params = params or {}
    light_type = params.get('type', 'shimmer')
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    warmth = params.get('warmth', 0.7)
    freq = params.get('freq', 5000)

    # High frequency shimmer with warmth
    shimmer = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.5 * t)
    # Warm low undertone
    warm_tone = np.sin(2 * np.pi * 220 * t) * warmth * 0.3
    # Sparkle modulation
    sparkle = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 8 * t))

    output = (shimmer * 0.3 * sparkle + warm_tone) * np.sin(np.pi * t / duration)

    return output * 0.5


def _generate_celestial(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Generate celestial/mystical effects: choir, particles, pad, portal, whisper.
    """
    params = params or {}
    celestial_type = params.get('type', 'choir')
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    if celestial_type == 'choir':
        # Angelic choir swell
        voices = params.get('voices', 4)
        freq = params.get('freq', 440)
        output = np.zeros(samples, dtype=np.float32)
        for i in range(voices):
            # Slightly detuned voices
            voice_freq = freq * (1.0 + (i - voices/2) * 0.005)
            voice = np.sin(2 * np.pi * voice_freq * t)
            voice += 0.3 * np.sin(2 * np.pi * voice_freq * 2 * t)
            # Slow vibrato
            vibrato = 1.0 + 0.01 * np.sin(2 * np.pi * (4 + i * 0.5) * t)
            output += voice * vibrato / voices
        envelope = np.sin(np.pi * t / duration)
        output *= envelope * 0.5

    elif celestial_type == 'particles':
        # Stardust sparkle particles
        density = params.get('density', 0.6)
        freq_range = params.get('freq_range', [4000, 12000])
        # Random sparkle particles
        output = np.zeros(samples, dtype=np.float32)
        num_particles = int(density * duration * 10)
        for _ in range(num_particles):
            pos = int(rng.random() * samples)
            freq = freq_range[0] + rng.random() * (freq_range[1] - freq_range[0])
            length = int(sample_rate * (0.05 + rng.random() * 0.1))
            if pos + length < samples:
                particle_t = np.linspace(0, length/sample_rate, length)
                particle = np.sin(2 * np.pi * freq * particle_t) * np.exp(-particle_t * 20)
                output[pos:pos+length] += particle * 0.3

    elif celestial_type == 'pad':
        # Heavenly ambient pad
        base = params.get('base', 220)
        warmth = params.get('warmth', 0.6)
        pad = np.sin(2 * np.pi * base * t) + 0.5 * np.sin(2 * np.pi * base * 2 * t)
        pad += 0.3 * np.sin(2 * np.pi * base * 3 * t)
        mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
        output = pad * mod * warmth * 0.4

    elif celestial_type == 'portal':
        # Portal shimmer opening
        rise_time = params.get('rise_time', 3.0)
        shimmer = params.get('shimmer', 0.8)
        freq_start = 200
        freq_end = 2000
        freq = freq_start + (freq_end - freq_start) * (t / duration) ** 0.7
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        tone = np.sin(phase) + shimmer * 0.5 * np.sin(phase * 2)
        # Rising envelope
        envelope = (t / duration) ** 0.5 * np.sin(np.pi * t / duration)
        output = tone * envelope * 0.5

    elif celestial_type == 'whisper':
        # Cosmic whisper
        formant = params.get('formant', 1200)
        reverb = params.get('reverb', 0.9)
        noise = rng.standard_normal(samples).astype(np.float32)
        # Formant resonance
        resonance = np.sin(2 * np.pi * formant * t) * 0.4
        window = int(sample_rate * 0.008)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t)
        whisper = (filtered * 0.3 + resonance) * mod
        # Simple reverb simulation
        output = whisper * reverb * 0.5

    else:
        output = np.zeros(samples, dtype=np.float32)

    # Fade in/out
    fade_samples = int(sample_rate * 0.3)
    if fade_samples > 0 and len(output) > fade_samples * 2:
        output[:fade_samples] *= np.linspace(0, 1, fade_samples)
        output[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return output


def _generate_presence(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Generate presence/spirit effects: whisper, breath, vocal_air, overtone, shimmer, fabric.
    """
    params = params or {}
    presence_type = params.get('type', 'whisper')
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    if presence_type == 'whisper':
        # Phase whisper for spirit guide
        phase_diff = params.get('phase_diff', 0.01)
        formant = params.get('formant', 1200)
        noise = rng.standard_normal(samples).astype(np.float32)
        resonance = np.sin(2 * np.pi * formant * t)
        # Phase modulation
        phase_mod = np.sin(2 * np.pi * 0.1 * t) * phase_diff
        resonance2 = np.sin(2 * np.pi * formant * (t + phase_mod))
        window = int(sample_rate * 0.005)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        output = (filtered * 0.3 + resonance * 0.2 + resonance2 * 0.2) * 0.6

    elif presence_type == 'breath':
        # Formant breath presence
        formant_freq = params.get('formant_freq', 800)
        noise = rng.standard_normal(samples).astype(np.float32)
        formant = np.sin(2 * np.pi * formant_freq * t) * 0.3
        window = int(sample_rate * 0.01)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        breath_env = np.sin(np.pi * t / duration)
        output = (filtered * 0.4 + formant) * breath_env * 0.5

    elif presence_type == 'vocal_air':
        # Soft angelic vocal air
        brightness = params.get('brightness', 0.4)
        noise = rng.standard_normal(samples).astype(np.float32)
        # Multiple formants for vocal quality
        formant1 = np.sin(2 * np.pi * 600 * t) * 0.2
        formant2 = np.sin(2 * np.pi * 1200 * t) * brightness * 0.15
        window = int(sample_rate * 0.008)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        output = (filtered * 0.3 + formant1 + formant2) * 0.5

    elif presence_type == 'overtone':
        # Overtone/throat singing drone
        base_freq = params.get('base_freq', 150)
        harmonics = params.get('harmonics', 6)
        output = np.zeros(samples, dtype=np.float32)
        for h in range(1, harmonics + 1):
            # Odd harmonics more prominent
            amp = 1.0 / h if h % 2 == 1 else 0.5 / h
            output += amp * np.sin(2 * np.pi * base_freq * h * t)
        # Slow modulation
        mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t)
        output *= mod * 0.4

    elif presence_type == 'shimmer':
        # Arrival shimmer
        rise_time = params.get('rise_time', 2.0)
        sustain = params.get('sustain', 3.0)
        # Rising shimmer
        freq = 400 + 800 * (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        shimmer = np.sin(phase) + 0.5 * np.sin(phase * 2)
        # Envelope: rise then sustain
        envelope = np.minimum(t / rise_time, 1.0) * np.sin(np.pi * t / duration)
        output = shimmer * envelope * 0.5

    elif presence_type == 'fabric':
        # Cloak/robe rustle
        density = params.get('density', 0.4)
        noise = rng.standard_normal(samples).astype(np.float32)
        # Fabric-like filtered noise
        window = int(sample_rate * 0.003)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        # Irregular movement
        movement = 0.3 + 0.7 * np.abs(np.sin(2 * np.pi * 5 * t + rng.random() * np.pi))
        output = filtered * movement * density * 0.5

    else:
        output = np.zeros(samples, dtype=np.float32)

    # Fade in/out
    fade_samples = int(sample_rate * 0.2)
    if fade_samples > 0 and len(output) > fade_samples * 2:
        output[:fade_samples] *= np.linspace(0, 1, fade_samples)
        output[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return output


def _generate_advanced(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Generate advanced/experimental effects: fractal, particles, spectral_choir, tuned_drum, field_pulse, sparkfield.
    """
    params = params or {}
    adv_type = params.get('type', 'fractal')
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    if adv_type == 'fractal':
        # Evolving fractal atmosphere
        complexity = params.get('complexity', 0.7)
        evolution_rate = params.get('evolution_rate', 0.01)
        output = np.zeros(samples, dtype=np.float32)
        # Multiple layers of sine waves with evolving phases
        num_layers = int(5 + complexity * 10)
        for i in range(num_layers):
            freq = 50 + i * 30 + 20 * np.sin(2 * np.pi * evolution_rate * i * t)
            phase = 2 * np.pi * np.cumsum(freq) / sample_rate
            output += (1.0 / (i + 1)) * np.sin(phase)
        output = output / num_layers * 0.5

    elif adv_type == 'particles':
        # Drifting cosmic particles
        density = params.get('density', 0.3)
        drift_rate = params.get('drift_rate', 0.05)
        output = np.zeros(samples, dtype=np.float32)
        num_particles = int(density * duration * 20)
        for _ in range(num_particles):
            pos = int(rng.random() * samples)
            freq = 500 + rng.random() * 2000
            drift = 1.0 + drift_rate * np.sin(2 * np.pi * 0.1 * t)
            length = int(sample_rate * (0.1 + rng.random() * 0.3))
            if pos + length < samples:
                particle_t = np.linspace(0, length/sample_rate, length)
                particle = np.sin(2 * np.pi * freq * particle_t) * np.exp(-particle_t * 5)
                output[pos:pos+length] += particle * 0.2

    elif adv_type == 'spectral_choir':
        # Spectral drum choir (harmonics from drum)
        source = params.get('source', 'frame')
        voices = params.get('voices', 8)
        base_freq = 80 if source == 'frame' else 50
        output = np.zeros(samples, dtype=np.float32)
        for v in range(voices):
            freq = base_freq * (v + 1)
            amp = 1.0 / (v + 1)
            voice = amp * np.sin(2 * np.pi * freq * t)
            # Slow modulation
            mod = 0.7 + 0.3 * np.sin(2 * np.pi * (0.05 + v * 0.01) * t)
            output += voice * mod
        envelope = np.sin(np.pi * t / duration)
        output *= envelope * 0.4

    elif adv_type == 'tuned_drum':
        # Planetary tuned drum (lunar 210.42 Hz, solar 126.22 Hz)
        freq = params.get('freq', 210.42)
        decay = params.get('decay', 12.0)
        # Deep resonant drum with specific frequency
        pitch_bend = freq * np.exp(-t * 0.5)
        phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
        drum = np.sin(phase) + 0.4 * np.sin(phase * 2)
        envelope = np.exp(-t / decay)
        output = drum * envelope * 0.6

    elif adv_type == 'field_pulse':
        # Resonant field pulse
        freq = params.get('freq', 30)
        earth_blend = params.get('earth_blend', 0.5)
        # Base pulse
        pulse = np.sin(2 * np.pi * freq * t)
        # Earth resonance (7.83 Hz Schumann)
        schumann = np.sin(2 * np.pi * 7.83 * t) * earth_blend
        # Combine
        mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
        output = (pulse * 0.6 + schumann * 0.4) * mod * 0.5

    elif adv_type == 'sparkfield':
        # Astral sparkfield
        density = params.get('density', 0.5)
        freq_range = params.get('freq_range', [3000, 12000])
        output = np.zeros(samples, dtype=np.float32)
        num_sparks = int(density * duration * 30)
        for _ in range(num_sparks):
            pos = int(rng.random() * samples)
            freq = freq_range[0] + rng.random() * (freq_range[1] - freq_range[0])
            length = int(sample_rate * (0.02 + rng.random() * 0.08))
            if pos + length < samples:
                spark_t = np.linspace(0, length/sample_rate, length)
                spark = np.sin(2 * np.pi * freq * spark_t) * np.exp(-spark_t * 30)
                output[pos:pos+length] += spark * 0.25

    else:
        output = np.zeros(samples, dtype=np.float32)

    # Fade in/out
    fade_samples = int(sample_rate * 0.5)
    if fade_samples > 0 and len(output) > fade_samples * 2:
        output[:fade_samples] *= np.linspace(0, 1, fade_samples)
        output[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return output


def _generate_drum_expanded(
    duration: float,
    sample_rate: int = 48000,
    params: Dict[str, Any] = None
) -> np.ndarray:
    """
    Expanded drum generator supporting many drum types:
    frame, buffalo, bodhran, ocean, damaru, djembe, dunun, talking, daf, riqq,
    tabla, doumbek, taiko, odaiko, shime, cinematic, earthquake, granular, etc.
    """
    params = params or {}
    drum_type = params.get('type', 'frame')
    freq = params.get('freq', 60)
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    rng = np.random.default_rng(seed=42)

    if drum_type in ('frame', 'shamanic'):
        # Frame drum / shamanic drum
        decay = params.get('decay', 3.5)
        resonance = params.get('resonance', 0.7)
        pitch_bend = freq * np.exp(-t * 2)
        phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
        drum = np.sin(phase) * resonance
        # Overtones
        drum += 0.3 * np.sin(phase * 2.3)
        envelope = np.exp(-t / decay)
        output = drum * envelope * 0.7

    elif drum_type == 'buffalo':
        # Deep buffalo drum
        pattern = params.get('pattern', 'single')
        sub_layer = params.get('sub_layer', False)
        decay = params.get('decay', 4.0)
        bpm = params.get('bpm', 60)

        pitch_bend = freq * np.exp(-t * 1.5)
        phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
        drum = np.sin(phase)
        if sub_layer:
            drum += 0.5 * np.sin(phase * 0.5)  # Sub-bass layer

        if pattern == 'heartbeat':
            # Double beat pattern
            beat_interval = 60.0 / bpm
            output = np.zeros(samples, dtype=np.float32)
            beat_len = int(sample_rate * 0.4)
            pos = 0
            while pos + beat_len < samples:
                # First beat
                beat_t = np.linspace(0, 0.4, beat_len)
                beat = np.sin(2 * np.pi * freq * beat_t) * np.exp(-beat_t * 5)
                output[pos:pos+beat_len] += beat
                # Second beat (softer)
                pos2 = pos + int(sample_rate * 0.15)
                if pos2 + beat_len < samples:
                    output[pos2:pos2+beat_len] += beat * 0.6
                pos += int(beat_interval * sample_rate)
            output *= 0.7
        elif pattern == 'double':
            # Double pulse
            output = np.zeros(samples, dtype=np.float32)
            beat_len = int(sample_rate * 0.3)
            beat_t = np.linspace(0, 0.3, beat_len)
            beat = np.sin(2 * np.pi * freq * beat_t) * np.exp(-beat_t * 6)
            output[:beat_len] = beat
            pos2 = int(sample_rate * 0.2)
            if pos2 + beat_len < samples:
                output[pos2:pos2+beat_len] += beat * 0.8
            output *= 0.7
        else:
            envelope = np.exp(-t / decay)
            output = drum * envelope * 0.7

    elif drum_type == 'bodhran':
        # Irish bodhran with roll
        pattern = params.get('pattern', 'roll')
        bpm = params.get('bpm', 80)
        if pattern == 'roll':
            output = np.zeros(samples, dtype=np.float32)
            roll_freq = bpm / 60 * 4  # 4 hits per beat
            hit_interval = int(sample_rate / roll_freq)
            hit_len = int(sample_rate * 0.05)
            hit_t = np.linspace(0, 0.05, hit_len)
            hit = np.sin(2 * np.pi * 100 * hit_t) * np.exp(-hit_t * 30)
            pos = 0
            while pos + hit_len < samples:
                amp = 0.5 + 0.5 * np.sin(2 * np.pi * 2 * pos / sample_rate)  # Volume variation
                output[pos:pos+hit_len] += hit * amp
                pos += hit_interval
            output *= 0.6
        else:
            output = np.sin(2 * np.pi * freq * t) * np.exp(-t * 5) * 0.6

    elif drum_type == 'ocean':
        # Ocean drum (rain stick-like)
        wave_rate = params.get('wave_rate', 0.2)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.01)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        wave = 0.5 + 0.5 * np.sin(2 * np.pi * wave_rate * t)
        output = filtered * wave * 0.5

    elif drum_type == 'djembe':
        # West African djembe with zones
        zone = params.get('zone', 'bass')
        intensity = params.get('intensity', 0.7)
        resonance = params.get('resonance', 0.7)

        if zone == 'bass':
            freq_local = 80
            decay = 0.3
        elif zone == 'tone':
            freq_local = 200
            decay = 0.2
        else:  # slap
            freq_local = 400
            decay = 0.1

        drum = np.sin(2 * np.pi * freq_local * t) * np.exp(-t / decay)
        # Add attack noise for slap
        if zone == 'slap':
            noise = rng.standard_normal(samples).astype(np.float32)
            drum += noise * np.exp(-t * 50) * 0.3
        output = drum * intensity * resonance * 0.7

    elif drum_type == 'dunun':
        # Dunun bass drum
        decay = params.get('decay', 3.0)
        drum = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
        envelope = np.exp(-t / decay)
        output = drum * envelope * 0.7

    elif drum_type == 'taiko':
        # Japanese taiko
        intensity = params.get('intensity', 0.7)
        decay = params.get('decay', 5.0)
        # Massive low end with resonance
        pitch_bend = 60 * np.exp(-t * 0.5)
        phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
        drum = np.sin(phase) + 0.4 * np.sin(phase * 2)
        # Attack transient
        attack = rng.standard_normal(samples).astype(np.float32) * np.exp(-t * 30) * 0.3
        envelope = np.exp(-t / decay)
        output = (drum + attack) * envelope * intensity * 0.8

    elif drum_type == 'odaiko':
        # Massive odaiko (big taiko)
        decay = params.get('decay', 8.0)
        pitch_bend = 30 * np.exp(-t * 0.3)
        phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
        drum = np.sin(phase) + 0.5 * np.sin(phase * 2) + 0.3 * np.sin(phase * 0.5)
        envelope = np.exp(-t / decay)
        output = drum * envelope * 0.8

    elif drum_type == 'cinematic':
        # Cinematic tom/impact
        decay = params.get('decay', 4.0)
        reverb = params.get('reverb', 0.7)
        pitch_bend = freq * np.exp(-t * 2)
        phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
        drum = np.sin(phase) + 0.3 * np.sin(phase * 2)
        envelope = np.exp(-t / decay)
        # Simple reverb tail
        output = drum * envelope * 0.7
        if reverb > 0:
            tail_len = int(sample_rate * reverb * 2)
            if tail_len < samples:
                tail = np.exp(-np.linspace(0, 2, tail_len) * 3)
                output = np.convolve(output, tail, mode='same')[:samples].astype(np.float32)

    elif drum_type == 'earthquake':
        # Distant earthquake rumble drum
        distance = params.get('distance', 'far')
        decay_mult = {'near': 1.0, 'medium': 2.0, 'far': 4.0}.get(distance, 2.0)
        freq_local = freq if freq > 0 else 25
        rumble = np.sin(2 * np.pi * freq_local * t) + 0.5 * np.sin(2 * np.pi * freq_local * 1.5 * t)
        noise = rng.standard_normal(samples).astype(np.float32)
        window = int(sample_rate * 0.05)
        kernel = np.ones(window) / window
        filtered = np.convolve(noise, kernel, mode='same').astype(np.float32)
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
        envelope = np.exp(-t / (decay_mult * 2))
        output = (rumble * 0.5 + filtered * 0.3) * mod * envelope * 0.6

    elif drum_type == 'granular':
        # Granular drum texture
        grain_size = params.get('grain_size', 50)
        scatter = params.get('scatter', 0.5)
        density = params.get('density', 0.4)
        output = np.zeros(samples, dtype=np.float32)
        grain_samples = int(sample_rate * grain_size / 1000)
        num_grains = int(density * duration * 50)
        # Base drum sound to granulate
        base_t = np.linspace(0, 0.2, int(sample_rate * 0.2))
        base_drum = np.sin(2 * np.pi * freq * base_t) * np.exp(-base_t * 10)
        for _ in range(num_grains):
            pos = int(rng.random() * (samples - grain_samples))
            grain_start = int(rng.random() * max(1, len(base_drum) - grain_samples))
            grain = base_drum[grain_start:grain_start + min(grain_samples, len(base_drum) - grain_start)]
            if len(grain) > 0 and pos + len(grain) < samples:
                # Apply grain window
                window = np.hanning(len(grain))
                output[pos:pos + len(grain)] += grain * window * scatter
        output *= 0.6

    elif drum_type in ('stretched', 'reverse'):
        # Time-stretched or reversed drum
        source = params.get('source', 'frame')
        stretch_factor = params.get('stretch_factor', 10.0)
        fade = params.get('fade', True)
        # Generate base drum
        base_len = int(samples / stretch_factor)
        base_t = np.linspace(0, base_len / sample_rate, base_len)
        base = np.sin(2 * np.pi * freq * base_t) * np.exp(-base_t * 5)
        # Stretch
        output = np.interp(np.linspace(0, base_len, samples), np.arange(base_len), base).astype(np.float32)
        if drum_type == 'reverse':
            output = output[::-1]
        if fade:
            fade_samples = int(sample_rate * 1.0)
            if fade_samples < samples:
                output[:fade_samples] *= np.linspace(0, 1, fade_samples)
                output[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        output *= 0.6

    else:
        # Default simple drum
        pitch_bend = freq * np.exp(-t * 3)
        phase = 2 * np.pi * np.cumsum(pitch_bend) / sample_rate
        drum = np.sin(phase)
        envelope = np.exp(-t * 4)
        output = drum * envelope * 0.7

    return output


def _generate_drum(
    duration: float,
    freq: float = 60,
    sample_rate: int = 48000
) -> np.ndarray:
    """Generate deep drum hit (simple version for backward compatibility)."""
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
    'torch': _generate_fire,
    'ember': _generate_fire,

    # Metallic resonance
    'resonance': _generate_resonance,
    'metallic': _generate_resonance,
    'ring': _generate_resonance,
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
    'frame_drum': _generate_drum,
    'buffalo_drum': _generate_drum,
    'shamanic_drum': _generate_drum,
    'bodhran': _generate_drum,
    'djembe': _generate_drum,
    'dunun': _generate_drum,
    'talking_drum': _generate_drum,
    'daf': _generate_drum,
    'riqq': _generate_drum,
    'tabla': _generate_drum,
    'doumbek': _generate_drum,
    'taiko': _generate_drum,
    'odaiko': _generate_drum,
    'shime': _generate_drum,
    'damaru': _generate_drum,
    'ocean_drum': _generate_drum,

    # NEW: Atmospheric textures
    'atmospheric': _generate_atmospheric,
    'air': _generate_atmospheric,
    'ether': _generate_atmospheric,
    'shimmer': _generate_atmospheric,
    'liminal': _generate_atmospheric,
    'vortex': _generate_atmospheric,
    'pad': _generate_atmospheric,

    # NEW: Water effects
    'water': _generate_water,
    'ocean': _generate_water,
    'stream': _generate_water,
    'brook': _generate_water,
    'rain': _generate_water,
    'underwater': _generate_water,
    'ripple': _generate_water,
    'drip': _generate_water,
    'wave': _generate_water,

    # NEW: Earth effects
    'earth': _generate_earth,
    'ground': _generate_earth,
    'stone': _generate_earth,
    'rock': _generate_earth,
    'cavern': _generate_earth,
    'tectonic': _generate_earth,

    # NEW: Light effects
    'light': _generate_light,
    'solar': _generate_light,
    'sunlight': _generate_light,
    'radiant': _generate_light,
    'glow': _generate_light,

    # NEW: Celestial effects
    'celestial': _generate_celestial,
    'angelic': _generate_celestial,
    'heavenly': _generate_celestial,
    'cosmic': _generate_celestial,
    'stardust': _generate_celestial,
    'prismatic': _generate_celestial,
    'divine': _generate_celestial,
    'portal': _generate_celestial,
    'choir': _generate_celestial,

    # NEW: Presence effects
    'presence': _generate_presence,
    'spirit': _generate_presence,
    'guide': _generate_presence,
    'entity': _generate_presence,
    'cloak': _generate_presence,
    'overtone': _generate_presence,
    'throat_singing': _generate_presence,

    # NEW: Advanced effects
    'advanced': _generate_advanced,
    'fractal': _generate_advanced,
    'spectral': _generate_advanced,
    'lunar': _generate_advanced,
    'astral': _generate_advanced,
    'field': _generate_advanced,
    'particle': _generate_advanced,
    'sparkfield': _generate_advanced,

    # NEW: Transition effects
    'transition': _generate_transition,
    'portal_transition': _generate_transition,
    'shift': _generate_transition,
    'transform': _generate_transition,
    'vacuum': _generate_transition,
    'riser': _generate_transition,
    'sweep': _generate_transition,
    'scatter': _generate_transition,
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
