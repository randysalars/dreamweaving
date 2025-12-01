#!/usr/bin/env python3
"""
Binaural Beats Generator

Universal module for generating binaural beats audio with support for:
- Frequency transitions between sections
- Gamma bursts for peak insight moments
- ADSR envelopes for smooth audio

Binaural beats work by playing slightly different frequencies in each ear,
causing the brain to perceive a "beat" at the frequency difference.
For example: 200 Hz in left ear + 210 Hz in right ear = 10 Hz binaural beat.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, TypedDict

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile


# Type definitions
class SectionDict(TypedDict, total=False):
    """Type definition for a binaural section."""
    start: int
    end: int
    freq_start: float
    freq_end: float
    beat_hz: float
    offset_hz: float
    transition: str


class GammaBurstDict(TypedDict):
    """Type definition for a gamma burst."""
    time: int
    duration: float
    frequency: float


# Type alias for stereo audio array
StereoAudio = NDArray[np.float32]


def generate(
    sections: List[SectionDict],
    duration_sec: float,
    sample_rate: int = 48000,
    carrier_freq: float = 200,
    amplitude: float = 0.3,
    fade_in_sec: float = 5.0,
    fade_out_sec: float = 8.0,
    gamma_bursts: Optional[List[GammaBurstDict]] = None
) -> StereoAudio:
    """
    Generate binaural beats audio.

    Creates a stereo audio track with binaural beats based on the provided
    section definitions. Each section can have its own frequency and
    transition type.

    Args:
        sections: List of section definitions with timing and frequency info.
            Each section should have:
            - start: Start time in seconds
            - end: End time in seconds
            - freq_start or beat_hz: Starting beat frequency in Hz
            - freq_end: Ending beat frequency (for transitions)
            - transition: 'linear', 'logarithmic', or 'hold'
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz (default: 48000)
        carrier_freq: Base carrier frequency in Hz (default: 200)
        amplitude: Output amplitude 0.0-1.0 (default: 0.3)
        fade_in_sec: Fade in duration in seconds (default: 5.0)
        fade_out_sec: Fade out duration in seconds (default: 8.0)
        gamma_bursts: Optional list of gamma burst events for peak moments

    Returns:
        Stereo audio as numpy array with shape (samples, 2)

    Example:
        >>> sections = [
        ...     {'start': 0, 'end': 60, 'freq_start': 10, 'freq_end': 10},
        ...     {'start': 60, 'end': 120, 'freq_start': 10, 'freq_end': 6}
        ... ]
        >>> audio = generate(sections, duration_sec=120)
    """
    print(f"Generating binaural beats: {duration_sec/60:.1f} min, carrier={carrier_freq}Hz")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    full_track: StereoAudio = np.zeros((total_samples, 2), dtype=np.float32)

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        freq_start = section.get('freq_start', section.get('beat_hz', 10))
        freq_end = section.get('freq_end', freq_start)
        transition = section.get('transition', 'linear')

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {freq_start}Hz→{freq_end}Hz ({transition})")

        # Check for gamma burst in this section
        gamma_in_section: Optional[GammaBurstDict] = None
        if gamma_bursts:
            for gamma in gamma_bursts:
                if start <= gamma['time'] < end:
                    gamma_in_section = gamma
                    break

        if gamma_in_section:
            # Split around gamma burst
            gamma_time = gamma_in_section['time']
            gamma_duration = gamma_in_section['duration']
            gamma_freq = gamma_in_section['frequency']

            # Pre-gamma segment
            pre_duration = gamma_time - start
            if pre_duration > 0:
                segment = _generate_segment(
                    pre_duration, freq_start, freq_end, carrier_freq,
                    amplitude, sample_rate, transition
                )
                end_sample = current_sample + len(segment)
                full_track[current_sample:end_sample] = segment
                current_sample = end_sample

            # Gamma burst
            print(f"    ⚡ GAMMA BURST at {gamma_time}s: {gamma_freq}Hz for {gamma_duration}s")
            gamma_segment = _generate_gamma_burst(
                carrier_freq, gamma_freq, gamma_duration,
                amplitude, sample_rate
            )
            end_sample = current_sample + len(gamma_segment)
            full_track[current_sample:end_sample] = gamma_segment
            current_sample = end_sample

            # Post-gamma segment
            post_duration = end - (gamma_time + gamma_duration)
            if post_duration > 0:
                segment = _generate_segment(
                    post_duration, freq_start, freq_end, carrier_freq,
                    amplitude, sample_rate, transition
                )
                end_sample = current_sample + len(segment)
                full_track[current_sample:end_sample] = segment
                current_sample = end_sample
        else:
            # Standard segment
            segment = _generate_segment(
                duration, freq_start, freq_end, carrier_freq,
                amplitude, sample_rate, transition
            )
            end_sample = current_sample + len(segment)
            full_track[current_sample:end_sample] = segment
            current_sample = end_sample

    # Apply global fade in/out
    if fade_in_sec > 0:
        fade_in_samples = int(fade_in_sec * sample_rate)
        fade_in_curve = np.linspace(0, 1, fade_in_samples).astype(np.float32)
        full_track[:fade_in_samples, 0] *= fade_in_curve
        full_track[:fade_in_samples, 1] *= fade_in_curve

    if fade_out_sec > 0:
        fade_out_samples = int(fade_out_sec * sample_rate)
        fade_out_curve = np.linspace(1, 0, fade_out_samples).astype(np.float32)
        full_track[-fade_out_samples:, 0] *= fade_out_curve
        full_track[-fade_out_samples:, 1] *= fade_out_curve

    print(f"✓ Binaural beats generated: {len(full_track)/sample_rate/60:.1f} min")

    return full_track


def _generate_segment(
    duration: float,
    freq_start: float,
    freq_end: float,
    carrier_freq: float,
    amplitude: float,
    sample_rate: int,
    transition: str = 'linear'
) -> StereoAudio:
    """
    Generate a single segment with frequency progression.

    Args:
        duration: Segment duration in seconds
        freq_start: Starting beat frequency in Hz
        freq_end: Ending beat frequency in Hz
        carrier_freq: Carrier frequency in Hz
        amplitude: Output amplitude (0.0-1.0)
        sample_rate: Sample rate in Hz
        transition: Transition type ('linear', 'logarithmic', or 'hold')

    Returns:
        Stereo audio segment as numpy array
    """
    segment_samples = int(sample_rate * duration)
    segment: StereoAudio = np.zeros((segment_samples, 2), dtype=np.float32)

    for i in range(segment_samples):
        t = i / sample_rate
        progress = i / segment_samples

        # Interpolate beat frequency
        if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
            beat_freq = freq_start * ((freq_end / freq_start) ** progress)
        else:  # linear or hold
            beat_freq = freq_start + (freq_end - freq_start) * progress

        # Calculate left/right frequencies
        left_freq = carrier_freq - (beat_freq / 2)
        right_freq = carrier_freq + (beat_freq / 2)

        # Generate tones
        segment[i, 0] = np.sin(2 * np.pi * left_freq * t) * amplitude
        segment[i, 1] = np.sin(2 * np.pi * right_freq * t) * amplitude

    return segment


def _generate_gamma_burst(
    carrier_freq: float,
    gamma_freq: float,
    duration: float,
    amplitude: float,
    sample_rate: int
) -> StereoAudio:
    """
    Generate intense gamma burst with quick envelope.

    Gamma bursts are used for peak insight moments, typically at 40 Hz.
    The envelope provides a quick fade in and longer fade out for
    smooth integration with surrounding audio.

    Args:
        carrier_freq: Carrier frequency in Hz
        gamma_freq: Gamma beat frequency in Hz (typically 40)
        duration: Burst duration in seconds
        amplitude: Base amplitude (0.0-1.0)
        sample_rate: Sample rate in Hz

    Returns:
        Stereo audio segment as numpy array
    """
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, endpoint=False)

    # Calculate frequencies
    left_freq = carrier_freq - (gamma_freq / 2)
    right_freq = carrier_freq + (gamma_freq / 2)

    # Generate tones
    left_tone = np.sin(2 * np.pi * left_freq * t)
    right_tone = np.sin(2 * np.pi * right_freq * t)

    # Envelope: quick fade in, sustain, quick fade out
    fade_in_samples = int(0.2 * sample_rate)
    fade_out_samples = int(0.5 * sample_rate)

    envelope = np.ones(len(t))
    envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)
    envelope[-fade_out_samples:] = np.linspace(1, 0, fade_out_samples)

    # Apply envelope with slight boost for impact
    left_tone = left_tone * envelope * amplitude * 1.2
    right_tone = right_tone * envelope * amplitude * 1.2

    stereo: StereoAudio = np.stack([left_tone, right_tone], axis=1).astype(np.float32)
    return stereo


def save_stem(
    audio: StereoAudio,
    path: Union[str, Path],
    sample_rate: int = 48000
) -> None:
    """
    Save binaural audio as WAV file.

    Args:
        audio: Stereo audio array (float32, shape (samples, 2))
        path: Output file path
        sample_rate: Sample rate in Hz

    Raises:
        OSError: If the file cannot be written
    """
    path = Path(path)

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)

    # Save
    wavfile.write(str(path), sample_rate, audio_int)

    file_size = path.stat().st_size / (1024 * 1024)
    print(f"✓ Saved binaural stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(
    manifest: Dict[str, Any],
    session_dir: Union[str, Path]
) -> Optional[Path]:
    """
    Generate binaural beats from session manifest.

    Reads the binaural configuration from the manifest and generates
    the appropriate audio file.

    Args:
        manifest: Session manifest dictionary
        session_dir: Path to session directory

    Returns:
        Path to generated stem file, or None if binaural is disabled

    Raises:
        KeyError: If required manifest fields are missing
    """
    session_dir = Path(session_dir)

    if not manifest['sound_bed']['binaural'].get('enabled', False):
        print("Binaural beats disabled in manifest")
        return None

    binaural_config = manifest['sound_bed']['binaural']

    # Build sections from manifest
    sections: List[SectionDict] = []
    for section in binaural_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'freq_start': section.get('offset_hz', section.get('beat_hz', 10)),
            'freq_end': section.get('offset_hz', section.get('beat_hz', 10)),
            'transition': 'linear'
        })

    # Extract gamma bursts if present
    gamma_bursts: List[GammaBurstDict] = []
    for fx in manifest.get('fx_timeline', []):
        if fx.get('type') == 'gamma_flash':
            gamma_bursts.append({
                'time': fx['time'],
                'duration': fx.get('duration_s', 3.0),
                'frequency': fx.get('freq_hz', 40)
            })

    # Generate
    duration = manifest['session']['duration']
    carrier = binaural_config.get('base_hz', 200)

    audio = generate(
        sections=sections,
        duration_sec=duration,
        carrier_freq=carrier,
        gamma_bursts=gamma_bursts if gamma_bursts else None
    )

    # Save
    stem_path = session_dir / "working_files" / "stems" / "binaural.wav"
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing binaural beat generation...")

    # Simple test: 2-minute track with alpha->theta transition
    test_sections: List[SectionDict] = [
        {'start': 0, 'end': 60, 'freq_start': 10, 'freq_end': 10},  # 10 Hz alpha
        {'start': 60, 'end': 120, 'freq_start': 10, 'freq_end': 6}  # Transition to 6 Hz theta
    ]

    audio = generate(test_sections, duration_sec=120, carrier_freq=200)
    save_stem(audio, "test_binaural.wav")

    print("✓ Test complete: test_binaural.wav")
