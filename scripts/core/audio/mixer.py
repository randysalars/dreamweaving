#!/usr/bin/env python3
"""
Universal Audio Mixer
Combines multiple audio stems with level control and sidechain ducking
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, TypedDict, Union

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile

# Type aliases
StereoAudio = NDArray[np.float32]  # Shape: (samples, 2)


class StemConfigAudio(TypedDict, total=False):
    """Stem configuration with audio data."""
    audio: StereoAudio
    gain_db: float


class StemConfigPath(TypedDict, total=False):
    """Stem configuration with file path."""
    path: str
    gain_db: float


StemConfig = Union[StemConfigAudio, StemConfigPath]
StemsDict = Dict[str, StemConfig]


def mix_stems(
    stems: StemsDict,
    duration_sec: float,
    sample_rate: int = 48000,
    sidechain_enabled: bool = True,
    sidechain_targets: Optional[List[str]] = None,
    sidechain_threshold: float = -30,
    sidechain_ratio: float = 0.5
) -> StereoAudio:
    """
    Mix multiple audio stems into final track.

    Args:
        stems: Dict of {name: {'audio': numpy_array, 'gain_db': float}}
               or {name: {'path': str, 'gain_db': float}}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        sidechain_enabled: Enable sidechain ducking on background stems
        sidechain_targets: List of stem names to apply sidechain to (default: all except 'voice')
        sidechain_threshold: dB threshold for ducking (-30 to -50)
        sidechain_ratio: Ducking amount (0.0-1.0, where 1.0 = full duck)

    Returns:
        numpy array of mixed stereo audio (float32), shape (samples, 2)
    """

    print("\n" + "="*70)
    print("UNIVERSAL AUDIO MIXER")
    print("="*70 + "\n")

    total_samples = int(sample_rate * duration_sec)
    mixed = np.zeros((total_samples, 2), dtype=np.float32)

    # Load or get all stems
    loaded_stems = {}
    for name, config in stems.items():
        if 'audio' in config:
            # Already loaded numpy array
            audio = config['audio']
        elif 'path' in config:
            # Load from file
            if os.path.exists(config['path']):
                print(f"Loading: {name} from {config['path']}")
                sr, audio = wavfile.read(config['path'])

                # Normalize based on original dtype BEFORE converting to float32
                original_dtype = audio.dtype
                if original_dtype == np.int16:
                    audio = audio.astype(np.float32) / 32768.0
                elif original_dtype == np.int32:
                    audio = audio.astype(np.float32) / 2147483648.0
                else:
                    audio = audio.astype(np.float32)

                if len(audio.shape) == 1:
                    # Mono to stereo
                    audio = np.stack([audio, audio], axis=1)

                if sr != sample_rate:
                    print(f"  Warning: {name} sample rate {sr} != {sample_rate}")
                    print(f"  Continuing anyway (proper resampling recommended)")
            else:
                print(f"⚠️  Stem not found: {config['path']}")
                print(f"  Creating silent track for {name}")
                audio = np.zeros((total_samples, 2), dtype=np.float32)
        else:
            raise ValueError(f"Stem {name} must have 'audio' or 'path' key")

        # Ensure correct length
        if len(audio) < total_samples:
            # Pad with silence
            padding = np.zeros((total_samples - len(audio), 2), dtype=np.float32)
            audio = np.vstack([audio, padding])
        elif len(audio) > total_samples:
            # Truncate
            audio = audio[:total_samples]

        # Apply gain
        gain_db = config.get('gain_db', 0)
        gain_linear = 10 ** (gain_db / 20.0)
        audio = audio * gain_linear

        loaded_stems[name] = {
            'audio': audio,
            'gain_db': gain_db,
            'is_voice': name.lower() in ['voice', 'narration', 'vocals']
        }

        print(f"✓ {name}: {gain_db} dB (gain: {gain_linear:.4f})")

    # Apply sidechain ducking if enabled
    if sidechain_enabled and 'voice' in loaded_stems:
        print("\n" + "-"*70)
        print("SIDECHAIN DUCKING")
        print("-"*70 + "\n")

        voice_audio = loaded_stems['voice']['audio']

        # Determine which stems to duck
        if sidechain_targets is None:
            # Duck everything except voice
            sidechain_targets = [name for name in loaded_stems.keys()
                               if not loaded_stems[name]['is_voice']]

        if sidechain_targets:
            # Calculate voice envelope (RMS with sliding window)
            voice_envelope = _calculate_envelope(voice_audio, sample_rate, window_ms=100)

            # Convert threshold to linear
            threshold_linear = 10 ** (sidechain_threshold / 20.0)

            print(f"Voice threshold: {sidechain_threshold} dB (linear: {threshold_linear:.6f})")
            print(f"Ducking ratio: {sidechain_ratio * 100:.0f}%")
            print(f"Targets: {', '.join(sidechain_targets)}")
            print()

            # Apply ducking to each target
            for name in sidechain_targets:
                if name in loaded_stems:
                    print(f"  Ducking {name}...")
                    ducking_gain = _calculate_ducking_gain(
                        voice_envelope, threshold_linear, sidechain_ratio
                    )
                    loaded_stems[name]['audio'] = loaded_stems[name]['audio'] * ducking_gain

            print(f"\n✓ Sidechain ducking applied to {len(sidechain_targets)} stems")
        else:
            print("No sidechain targets specified")

    # Mix all stems
    print("\n" + "-"*70)
    print("MIXING")
    print("-"*70 + "\n")

    for name, data in loaded_stems.items():
        mixed += data['audio']
        print(f"  + {name}")

    # Check for clipping
    peak = np.max(np.abs(mixed))
    print(f"\nPeak level: {peak:.4f}")

    if peak > 0.98:
        print(f"⚠️  Clipping detected! Normalizing to 0.95...")
        mixed = mixed * (0.95 / peak)
        peak = 0.95

    # Calculate RMS
    rms = np.sqrt(np.mean(mixed ** 2))
    print(f"RMS level: {rms:.4f}")
    print(f"Estimated LUFS: ~{20 * np.log10(rms):.1f} dB")

    print("\n" + "="*70)
    print("✓ MIXING COMPLETE")
    print("="*70)

    return mixed


def _calculate_envelope(
    audio: StereoAudio,
    sample_rate: int,
    window_ms: float = 100,
    smoothing_ms: float = 50
) -> StereoAudio:
    """
    Calculate RMS envelope of audio signal.

    Args:
        audio: Stereo audio (numpy array)
        sample_rate: Sample rate in Hz
        window_ms: RMS window size in milliseconds
        smoothing_ms: Envelope smoothing window in milliseconds

    Returns:
        Envelope as stereo numpy array (same shape as input)
    """
    window_samples = int((window_ms / 1000.0) * sample_rate)
    smoothing_samples = int((smoothing_ms / 1000.0) * sample_rate)

    # Calculate RMS for mono sum (typical sidechain behavior)
    mono = np.mean(audio, axis=1)

    # RMS envelope
    envelope_mono = np.zeros(len(mono))
    for i in range(len(mono)):
        start = max(0, i - window_samples // 2)
        end = min(len(mono), i + window_samples // 2)
        window_data = mono[start:end]
        envelope_mono[i] = np.sqrt(np.mean(window_data ** 2))

    # Smooth envelope
    if smoothing_samples > 1:
        kernel = np.ones(smoothing_samples) / smoothing_samples
        envelope_mono = np.convolve(envelope_mono, kernel, mode='same')

    # Duplicate to stereo
    envelope = np.stack([envelope_mono, envelope_mono], axis=1)

    return envelope


def _calculate_ducking_gain(
    voice_envelope: StereoAudio,
    threshold: float,
    ratio: float
) -> StereoAudio:
    """
    Calculate ducking gain curve based on voice envelope.

    When voice is present (above threshold), reduce background stems.

    Args:
        voice_envelope: Voice RMS envelope (stereo)
        threshold: Linear threshold for ducking
        ratio: Ducking amount (0.0-1.0)

    Returns:
        Gain curve (stereo, same shape as voice_envelope)
    """
    gain = np.ones_like(voice_envelope)

    # Where voice is above threshold, apply ducking
    mask = voice_envelope > threshold

    # Calculate how much above threshold
    excess = np.maximum(0, voice_envelope - threshold)

    # Apply ducking ratio
    # When voice is present, reduce gain by ratio amount
    # ratio=0.5 means reduce to 50% (half volume) when voice is at threshold
    # ratio=1.0 means reduce to 0% (full duck)
    gain[mask] = 1.0 - (ratio * np.minimum(1.0, excess[mask] / threshold))

    return gain


def save_mix(
    audio: StereoAudio,
    path: Union[str, os.PathLike],
    sample_rate: int = 48000
) -> None:
    """
    Save mixed audio as WAV file.

    Args:
        audio: numpy array (stereo, float32)
        path: Output file path
        sample_rate: Sample rate in Hz
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)

    # Save
    wavfile.write(path, sample_rate, audio_int)

    file_size = os.path.getsize(path) / (1024 * 1024)
    print(f"\n✓ Saved mix: {path} ({file_size:.1f} MB)")


def mix_from_manifest(
    manifest: Dict[str, Any],
    session_dir: Union[str, os.PathLike]
) -> str:
    """
    Mix stems based on session manifest.

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to mixed output file
    """
    print("\n" + "="*70)
    print("MIXING FROM MANIFEST")
    print("="*70 + "\n")

    duration = manifest['session']['duration']
    mixing_config = manifest.get('mixing', {})

    # Build stems dict from manifest
    stems = {}

    # Voice
    voice_path = os.path.join(session_dir, "working_files/voice.wav")
    if os.path.exists(voice_path):
        stems['voice'] = {
            'path': voice_path,
            'gain_db': mixing_config.get('voice_lufs', -16)
        }

    # Sound bed stems
    sound_bed = manifest.get('sound_bed', {})
    stem_dir = os.path.join(session_dir, "working_files/stems")

    for sound_type, config in sound_bed.items():
        if isinstance(config, dict) and config.get('enabled', False):
            stem_path = os.path.join(stem_dir, f"{sound_type}.wav")
            if os.path.exists(stem_path):
                # Get LUFS target from manifest
                lufs_key = f"{sound_type}_lufs"
                gain_db = mixing_config.get(lufs_key, -30)

                stems[sound_type] = {
                    'path': stem_path,
                    'gain_db': gain_db
                }

    # Sidechain configuration
    sidechain_config = mixing_config.get('sidechain', {})
    sidechain_enabled = sidechain_config.get('enabled', True)
    sidechain_targets = sidechain_config.get('targets', None)

    # Mix
    mixed = mix_stems(
        stems=stems,
        duration_sec=duration,
        sidechain_enabled=sidechain_enabled,
        sidechain_targets=sidechain_targets
    )

    # Save
    output_path = os.path.join(session_dir, "working_files/mixed.wav")
    save_mix(mixed, output_path)

    return output_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing audio mixer...")

    # Create test stems
    duration = 10  # 10 seconds
    sample_rate = 48000
    samples = duration * sample_rate

    print("\nGenerating test stems...")

    # Voice: Intermittent signal (simulating speech)
    t = np.linspace(0, duration, samples, False)
    voice = np.zeros((samples, 2), dtype=np.float32)

    # Add speech-like bursts at 1s, 3s, 5s, 7s
    for burst_time in [1, 3, 5, 7]:
        start = int(burst_time * sample_rate)
        end = start + int(0.8 * sample_rate)  # 800ms bursts
        if end <= samples:
            # Modulated tone to simulate speech
            burst_t = np.linspace(0, 0.8, end - start, False)
            voice_signal = np.sin(2 * np.pi * 200 * burst_t) * 0.3
            voice_signal *= np.random.rand(len(burst_t)) * 0.5 + 0.5  # Add variation
            voice[start:end, 0] = voice_signal
            voice[start:end, 1] = voice_signal

    # Background: Continuous pink noise
    background = np.random.randn(samples, 2).astype(np.float32) * 0.15

    # Save test stems
    os.makedirs("test_mixer", exist_ok=True)

    voice_int = (voice * 32767).astype(np.int16)
    wavfile.write("test_mixer/voice.wav", sample_rate, voice_int)

    bg_int = (background * 32767).astype(np.int16)
    wavfile.write("test_mixer/background.wav", sample_rate, bg_int)

    print("✓ Test stems created")

    # Test 1: Mix without sidechain
    print("\n" + "="*70)
    print("TEST 1: Mix without sidechain")
    print("="*70)

    stems_no_sc = {
        'voice': {'path': 'test_mixer/voice.wav', 'gain_db': -16},
        'background': {'path': 'test_mixer/background.wav', 'gain_db': -28}
    }

    mixed_no_sc = mix_stems(stems_no_sc, duration, sidechain_enabled=False)
    save_mix(mixed_no_sc, "test_mixer/mixed_no_sidechain.wav")

    # Test 2: Mix with sidechain
    print("\n" + "="*70)
    print("TEST 2: Mix with sidechain ducking")
    print("="*70)

    stems_sc = {
        'voice': {'path': 'test_mixer/voice.wav', 'gain_db': -16},
        'background': {'path': 'test_mixer/background.wav', 'gain_db': -28}
    }

    mixed_sc = mix_stems(
        stems_sc,
        duration,
        sidechain_enabled=True,
        sidechain_targets=['background'],
        sidechain_threshold=-30,
        sidechain_ratio=0.7
    )
    save_mix(mixed_sc, "test_mixer/mixed_with_sidechain.wav")

    print("\n" + "="*70)
    print("✓ MIXER TESTS COMPLETE")
    print("="*70)
    print("\nOutputs created:")
    print("  test_mixer/voice.wav              - Voice stem (intermittent)")
    print("  test_mixer/background.wav         - Background stem (continuous)")
    print("  test_mixer/mixed_no_sidechain.wav - Mixed without ducking")
    print("  test_mixer/mixed_with_sidechain.wav - Mixed with ducking")
    print("\nListening test:")
    print("  Compare the two mixes - the sidechained version should have")
    print("  the background ducking down when voice is present")
