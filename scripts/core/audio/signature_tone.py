#!/usr/bin/env python3
"""
Signature Tone Generator - Universal Dreamweaver Audio Signature

Creates a unique audio signature that appears at the intro and outro of every
Dreamweaver session. This creates neurological association with the trance state,
so returning listeners immediately begin to relax upon hearing it.

Design Philosophy:
- 432 Hz base frequency (associated with natural harmony)
- 7 Hz binaural beat (theta state, deep relaxation/meditation)
- Subtle shimmer envelope for ethereal quality
- Consistent placement creates Pavlovian conditioning for trance

The signature is designed to be:
1. Immediately recognizable but not intrusive
2. Calming and trance-inducing
3. Short enough to not delay the content
4. Rich enough to create lasting neural associations
"""

import os
from pathlib import Path
from typing import Optional, TypedDict

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

class SignatureConfig(TypedDict, total=False):
    """Configuration for the signature tone."""
    base_freq: float            # Base carrier frequency (default 432 Hz)
    binaural_beat: float        # Binaural beat frequency (default 7 Hz theta)
    duration_sec: float         # Total duration (default 5.0 seconds)
    fade_in_sec: float          # Fade in duration (default 1.5 seconds)
    fade_out_sec: float         # Fade out duration (default 2.0 seconds)
    shimmer_rate: float         # Shimmer modulation rate (default 0.5 Hz)
    shimmer_depth: float        # Shimmer depth 0-1 (default 0.15)
    harmonic_2nd: float         # 2nd harmonic level (default 0.25)
    harmonic_3rd: float         # 3rd harmonic level (default 0.1)
    sub_harmonic: float         # Sub-harmonic level (default 0.15)
    sample_rate: int            # Sample rate (default 48000)
    amplitude: float            # Overall amplitude 0-1 (default 0.3)


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================

DEFAULT_CONFIG: SignatureConfig = {
    'base_freq': 432.0,        # Natural tuning frequency
    'binaural_beat': 7.0,      # Theta state
    'duration_sec': 5.0,
    'fade_in_sec': 1.5,
    'fade_out_sec': 2.0,
    'shimmer_rate': 0.5,
    'shimmer_depth': 0.15,
    'harmonic_2nd': 0.25,
    'harmonic_3rd': 0.1,
    'sub_harmonic': 0.15,
    'sample_rate': 48000,
    'amplitude': 0.3,
}


# =============================================================================
# CORE GENERATION
# =============================================================================

def generate_signature(
    config: Optional[SignatureConfig] = None,
    variant: str = 'standard',
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Generate the Dreamweaver signature tone.

    Args:
        config: Optional configuration overrides
        variant: 'standard', 'intro', or 'outro' - affects envelope
                 'intro' has longer fade-in, gentle start
                 'outro' has longer fade-out, gentle end

    Returns:
        Tuple of (left_channel, right_channel) as numpy arrays
    """
    # Merge with defaults
    cfg = {**DEFAULT_CONFIG, **(config or {})}

    sr = cfg['sample_rate']
    duration = cfg['duration_sec']
    base_freq = cfg['base_freq']
    beat_freq = cfg['binaural_beat']
    amplitude = cfg['amplitude']

    # Adjust envelope based on variant
    if variant == 'intro':
        fade_in = min(cfg['fade_in_sec'] * 1.5, duration * 0.4)
        fade_out = cfg['fade_out_sec']
    elif variant == 'outro':
        fade_in = cfg['fade_in_sec']
        fade_out = min(cfg['fade_out_sec'] * 1.5, duration * 0.5)
    else:
        fade_in = cfg['fade_in_sec']
        fade_out = cfg['fade_out_sec']

    num_samples = int(duration * sr)
    t = np.linspace(0, duration, num_samples, dtype=np.float64)

    # Calculate left and right frequencies for binaural beat
    left_freq = base_freq
    right_freq = base_freq + beat_freq

    # Generate fundamental tones with harmonics
    left = _generate_rich_tone(t, left_freq, cfg)
    right = _generate_rich_tone(t, right_freq, cfg)

    # Apply shimmer envelope
    shimmer = _generate_shimmer_envelope(t, cfg['shimmer_rate'], cfg['shimmer_depth'])
    left *= shimmer
    right *= shimmer

    # Apply fade envelopes
    left = _apply_fades(left, sr, fade_in, fade_out)
    right = _apply_fades(right, sr, fade_in, fade_out)

    # Scale to final amplitude
    left *= amplitude
    right *= amplitude

    return left, right


def _generate_rich_tone(
    t: NDArray[np.float64],
    freq: float,
    cfg: SignatureConfig,
) -> NDArray[np.float64]:
    """Generate a tone with harmonics for richer sound."""
    # Fundamental
    tone = np.sin(2 * np.pi * freq * t)

    # Sub-harmonic (one octave below)
    if cfg['sub_harmonic'] > 0:
        tone += cfg['sub_harmonic'] * np.sin(2 * np.pi * (freq / 2) * t)

    # 2nd harmonic (one octave above)
    if cfg['harmonic_2nd'] > 0:
        tone += cfg['harmonic_2nd'] * np.sin(2 * np.pi * (freq * 2) * t)

    # 3rd harmonic (octave + fifth above)
    if cfg['harmonic_3rd'] > 0:
        tone += cfg['harmonic_3rd'] * np.sin(2 * np.pi * (freq * 3) * t)

    # Normalize to prevent clipping
    max_amp = 1.0 + cfg['sub_harmonic'] + cfg['harmonic_2nd'] + cfg['harmonic_3rd']
    tone /= max_amp

    return tone


def _generate_shimmer_envelope(
    t: NDArray[np.float64],
    rate: float,
    depth: float,
) -> NDArray[np.float64]:
    """Generate a slow shimmer envelope for ethereal quality."""
    # Use a combination of two slow oscillations for organic feel
    shimmer1 = np.sin(2 * np.pi * rate * t)
    shimmer2 = np.sin(2 * np.pi * (rate * 1.618) * t)  # Golden ratio offset

    # Combine and scale to depth
    shimmer = (shimmer1 * 0.6 + shimmer2 * 0.4) * depth

    # Shift to 0-centered around 1.0
    envelope = 1.0 + shimmer

    return envelope


def _apply_fades(
    audio: NDArray[np.float64],
    sample_rate: int,
    fade_in_sec: float,
    fade_out_sec: float,
) -> NDArray[np.float64]:
    """Apply smooth fade in and fade out to audio."""
    num_samples = len(audio)
    result = audio.copy()

    # Fade in
    fade_in_samples = int(fade_in_sec * sample_rate)
    if fade_in_samples > 0:
        fade_in_curve = np.linspace(0, 1, fade_in_samples) ** 2  # Quadratic ease-in
        result[:fade_in_samples] *= fade_in_curve

    # Fade out
    fade_out_samples = int(fade_out_sec * sample_rate)
    if fade_out_samples > 0:
        fade_out_curve = np.linspace(1, 0, fade_out_samples) ** 2  # Quadratic ease-out
        result[-fade_out_samples:] *= fade_out_curve

    return result


# =============================================================================
# HIGH-LEVEL API
# =============================================================================

def generate_intro_signature(
    output_path: Optional[str] = None,
    config: Optional[SignatureConfig] = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Generate the intro signature tone.

    Args:
        output_path: Optional path to save WAV file
        config: Optional configuration overrides

    Returns:
        Tuple of (left, right) channels
    """
    left, right = generate_signature(config, variant='intro')

    if output_path:
        save_stereo_wav(output_path, left, right, (config or DEFAULT_CONFIG).get('sample_rate', 48000))

    return left, right


def generate_outro_signature(
    output_path: Optional[str] = None,
    config: Optional[SignatureConfig] = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Generate the outro signature tone.

    Args:
        output_path: Optional path to save WAV file
        config: Optional configuration overrides

    Returns:
        Tuple of (left, right) channels
    """
    left, right = generate_signature(config, variant='outro')

    if output_path:
        save_stereo_wav(output_path, left, right, (config or DEFAULT_CONFIG).get('sample_rate', 48000))

    return left, right


def save_stereo_wav(
    path: str,
    left: NDArray[np.float64],
    right: NDArray[np.float64],
    sample_rate: int = 48000,
) -> None:
    """Save stereo audio to WAV file."""
    # Stack to stereo
    stereo = np.column_stack([left, right])

    # Convert to int16
    stereo_int = (stereo * 32767).astype(np.int16)

    # Ensure directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    # Save
    wavfile.write(path, sample_rate, stereo_int)
    print(f"Saved signature tone: {path}")


# =============================================================================
# INTEGRATION WITH SESSIONS
# =============================================================================

def embed_signature_in_session(
    session_audio_path: str,
    output_path: Optional[str] = None,
    intro: bool = True,
    outro: bool = True,
    config: Optional[SignatureConfig] = None,
) -> str:
    """
    Embed signature tones at the beginning and/or end of a session.

    Args:
        session_audio_path: Path to the session audio file
        output_path: Output path (defaults to replacing input)
        intro: Add intro signature
        outro: Add outro signature
        config: Optional signature configuration

    Returns:
        Path to the output file
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    sr = cfg['sample_rate']

    # Load session audio
    file_sr, session_audio = wavfile.read(session_audio_path)

    # Convert to float64 and handle mono/stereo
    if session_audio.dtype == np.int16:
        session_audio = session_audio.astype(np.float64) / 32767
    elif session_audio.dtype == np.int32:
        session_audio = session_audio.astype(np.float64) / 2147483647

    # Ensure stereo
    if len(session_audio.shape) == 1:
        session_audio = np.column_stack([session_audio, session_audio])

    # Resample if needed (simple approach - ideally use scipy.signal.resample)
    if file_sr != sr:
        print(f"Warning: Session at {file_sr}Hz, signature at {sr}Hz - using session rate")
        cfg['sample_rate'] = file_sr
        sr = file_sr

    result = session_audio

    # Add intro signature
    if intro:
        left, right = generate_signature(cfg, variant='intro')
        intro_stereo = np.column_stack([left, right])

        # Add small gap
        gap = np.zeros((int(0.5 * sr), 2))

        result = np.vstack([intro_stereo, gap, result])
        print(f"Added intro signature ({len(left)/sr:.1f}s)")

    # Add outro signature
    if outro:
        left, right = generate_signature(cfg, variant='outro')
        outro_stereo = np.column_stack([left, right])

        # Add small gap
        gap = np.zeros((int(0.5 * sr), 2))

        result = np.vstack([result, gap, outro_stereo])
        print(f"Added outro signature ({len(left)/sr:.1f}s)")

    # Prepare output path
    if output_path is None:
        output_path = session_audio_path

    # Convert back to int16 and save
    result_int = (np.clip(result, -1, 1) * 32767).astype(np.int16)
    wavfile.write(output_path, sr, result_int)

    print(f"Saved with signature: {output_path}")
    return output_path


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for signature tone generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate Dreamweaver signature tones',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate standalone signature files
  python signature_tone.py --output signatures/

  # Embed signature in a session
  python signature_tone.py --embed session_audio.wav --output session_with_sig.wav

  # Generate with custom settings
  python signature_tone.py --output sig.wav --base-freq 440 --duration 7
        """
    )

    parser.add_argument('--output', '-o', help='Output path (file or directory)')
    parser.add_argument('--embed', help='Embed signature in existing session audio')
    parser.add_argument('--intro-only', action='store_true', help='Generate/embed intro only')
    parser.add_argument('--outro-only', action='store_true', help='Generate/embed outro only')

    # Configuration options
    parser.add_argument('--base-freq', type=float, default=432.0,
                        help='Base frequency in Hz (default: 432)')
    parser.add_argument('--beat-freq', type=float, default=7.0,
                        help='Binaural beat frequency in Hz (default: 7 theta)')
    parser.add_argument('--duration', type=float, default=5.0,
                        help='Duration in seconds (default: 5.0)')
    parser.add_argument('--amplitude', type=float, default=0.3,
                        help='Amplitude 0-1 (default: 0.3)')

    args = parser.parse_args()

    # Build config
    config: SignatureConfig = {
        'base_freq': args.base_freq,
        'binaural_beat': args.beat_freq,
        'duration_sec': args.duration,
        'amplitude': args.amplitude,
    }

    do_intro = not args.outro_only
    do_outro = not args.intro_only

    if args.embed:
        # Embed mode
        output = args.output or args.embed
        embed_signature_in_session(
            args.embed,
            output,
            intro=do_intro,
            outro=do_outro,
            config=config,
        )
    else:
        # Generate standalone files
        output_dir = args.output or '.'
        if os.path.isdir(output_dir) or not output_dir.endswith('.wav'):
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            if do_intro:
                intro_path = os.path.join(output_dir, 'signature_intro.wav')
                generate_intro_signature(intro_path, config)

            if do_outro:
                outro_path = os.path.join(output_dir, 'signature_outro.wav')
                generate_outro_signature(outro_path, config)
        else:
            # Single file output
            if do_intro and not do_outro:
                generate_intro_signature(output_dir, config)
            elif do_outro and not do_intro:
                generate_outro_signature(output_dir, config)
            else:
                # Standard variant
                left, right = generate_signature(config, variant='standard')
                save_stereo_wav(output_dir, left, right)


if __name__ == '__main__':
    main()
