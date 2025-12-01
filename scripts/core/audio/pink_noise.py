#!/usr/bin/env python3
"""
Pink Noise Generator
Universal module for Dreamweaving project
Pink noise (1/f noise) has equal energy per octave - natural, relaxing sound
Often combined with binaural beats for enhanced relaxation
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Union

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile

# Type aliases
StereoAudio = NDArray[np.float32]  # Shape: (samples, 2)
MonoAudio = NDArray[np.float64]    # Shape: (samples,)


def generate(
    duration_sec: float,
    sample_rate: int = 48000,
    amplitude: float = 0.15,
    fade_in_sec: float = 5.0,
    fade_out_sec: float = 8.0,
    stereo_variation: bool = True
) -> StereoAudio:
    """
    Generate pink noise audio.

    Args:
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        amplitude: Output amplitude (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)
        stereo_variation: If True, generate slightly different L/R channels

    Returns:
        numpy array of stereo audio samples (float32), shape (samples, 2)
    """

    print(f"Generating pink noise: {duration_sec/60:.1f} min")

    total_samples = int(sample_rate * duration_sec)

    # Generate pink noise using Voss-McCartney algorithm
    # This creates 1/f noise with approximately -3dB/octave rolloff
    if stereo_variation:
        # Generate independent L/R channels for wider stereo field
        left_channel = _generate_pink_noise_channel(total_samples)
        right_channel = _generate_pink_noise_channel(total_samples)
        pink_noise = np.stack([left_channel, right_channel], axis=1).astype(np.float32)
    else:
        # Generate mono and duplicate (perfect correlation)
        mono_channel = _generate_pink_noise_channel(total_samples)
        pink_noise = np.stack([mono_channel, mono_channel], axis=1).astype(np.float32)

    # Normalize and apply amplitude
    # Pink noise has higher RMS than white noise, so normalize carefully
    rms = np.sqrt(np.mean(pink_noise ** 2))
    pink_noise = (pink_noise / rms) * amplitude * 0.1  # Scale down for safety

    # Apply fade in/out
    if fade_in_sec > 0:
        fade_in_samples = int(fade_in_sec * sample_rate)
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        pink_noise[:fade_in_samples, 0] *= fade_in_curve
        pink_noise[:fade_in_samples, 1] *= fade_in_curve

    if fade_out_sec > 0:
        fade_out_samples = int(fade_out_sec * sample_rate)
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        pink_noise[-fade_out_samples:, 0] *= fade_out_curve
        pink_noise[-fade_out_samples:, 1] *= fade_out_curve

    print(f"✓ Pink noise generated: {len(pink_noise)/sample_rate/60:.1f} min")
    print(f"  RMS level: {np.sqrt(np.mean(pink_noise**2)):.4f}")

    return pink_noise


def _generate_pink_noise_channel(num_samples: int) -> MonoAudio:
    """
    Generate pink noise using Voss-McCartney algorithm.

    This method maintains N generators that are randomly updated at
    different rates, creating 1/f spectrum.

    Args:
        num_samples: Number of samples to generate

    Returns:
        Normalized mono audio samples (float64)
    """
    # Number of random sources (more = better pink noise quality)
    num_sources = 16

    # Initialize random sources
    sources = np.random.randn(num_sources)
    output = np.zeros(num_samples)

    # Update counters for each source
    update_rates = [2 ** i for i in range(num_sources)]

    for i in range(num_samples):
        # Update sources based on their update rates
        for j in range(num_sources):
            if i % update_rates[j] == 0:
                sources[j] = np.random.randn()

        # Sum all sources
        output[i] = np.sum(sources)

    # Normalize
    output = output / np.max(np.abs(output))

    return output


def save_stem(audio: StereoAudio, path: Union[str, os.PathLike], sample_rate: int = 48000) -> None:
    """
    Save pink noise as WAV file.

    Args:
        audio: numpy array (stereo, float32)
        path: Output file path
        sample_rate: Sample rate in Hz
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)

    # Save
    wavfile.write(path, sample_rate, audio_int)

    file_size = os.path.getsize(path) / (1024 * 1024)
    print(f"✓ Saved pink noise stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(
    manifest: Dict[str, Any],
    session_dir: Union[str, os.PathLike]
) -> Optional[str]:
    """
    Generate pink noise from session manifest.

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file, or None if disabled
    """
    if not manifest['sound_bed']['pink_noise'].get('enabled', False):
        print("Pink noise disabled in manifest")
        return None

    pink_config = manifest['sound_bed']['pink_noise']

    # Generate
    duration = manifest['session']['duration']
    stereo_variation = pink_config.get('stereo_variation', True)

    audio = generate(
        duration_sec=duration,
        stereo_variation=stereo_variation
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/pink_noise.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing pink noise generation...")

    # Test 1: Stereo variation
    print("\n1. Stereo pink noise (L/R variation):")
    audio_stereo = generate(duration_sec=30, stereo_variation=True)
    save_stem(audio_stereo, "test_pink_noise_stereo.wav")

    # Test 2: Mono (duplicated)
    print("\n2. Mono pink noise (L/R identical):")
    audio_mono = generate(duration_sec=30, stereo_variation=False)
    save_stem(audio_mono, "test_pink_noise_mono.wav")

    print("\n✓ Test complete: test_pink_noise_stereo.wav and test_pink_noise_mono.wav")
    print("\nListening notes:")
    print("  - Stereo version should have wider soundstage")
    print("  - Should sound like gentle rain or distant waterfall")
    print("  - Should be relaxing, not harsh or hissy")
