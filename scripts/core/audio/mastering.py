#!/usr/bin/env python3
"""
Professional Audio Mastering Module
LUFS normalization, EQ, stereo enhancement, and peak limiting
With optional hypnotic voice enhancement integration

Based on proven techniques from Neural Network Navigator V2
Enhanced with hypnotic voice processing from voice_enhancement.py
"""

import subprocess
import os
import sys
import numpy as np
from scipy.io import wavfile

# Import voice enhancement module
try:
    from . import voice_enhancement
    VOICE_ENHANCEMENT_AVAILABLE = True
except ImportError:
    try:
        import voice_enhancement
        VOICE_ENHANCEMENT_AVAILABLE = True
    except ImportError:
        VOICE_ENHANCEMENT_AVAILABLE = False

def analyze_loudness(input_path):
    """
    Analyze audio loudness using FFmpeg loudnorm filter

    Args:
        input_path: Path to input audio file

    Returns:
        dict with {input_i, input_tp, input_lra, input_thresh} or None on error
    """
    print("\n" + "="*70)
    print("STEP 1: Analyzing Audio Levels")
    print("="*70 + "\n")

    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary',
        '-f', 'null',
        '-'
    ]

    print(f"Analyzing: {input_path}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        output = result.stderr

        # Parse metrics
        metrics = {}
        for line in output.split('\n'):
            if 'Input Integrated:' in line:
                metrics['input_i'] = line.split(':')[1].strip().split()[0]
            elif 'Input True Peak:' in line:
                metrics['input_tp'] = line.split(':')[1].strip().split()[0]
            elif 'Input LRA:' in line:
                metrics['input_lra'] = line.split(':')[1].strip().split()[0]
            elif 'Input Threshold:' in line:
                metrics['input_thresh'] = line.split(':')[1].strip().split()[0]

        if metrics:
            print("\nCurrent Audio Levels:")
            print(f"  Integrated Loudness: {metrics.get('input_i', 'N/A')} LUFS")
            print(f"  True Peak:          {metrics.get('input_tp', 'N/A')} dBTP")
            print(f"  Loudness Range:     {metrics.get('input_lra', 'N/A')} LU")
            print(f"  Threshold:          {metrics.get('input_thresh', 'N/A')} LUFS")
            print()
            return metrics
        else:
            print("✗ Could not parse loudness metrics")
            return None

    except subprocess.TimeoutExpired:
        print("✗ Analysis timed out")
        return None
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        return None


def master_audio(
    input_path,
    output_path,
    target_lufs=-14,
    target_tp=-1.5,
    target_lra=11,
    apply_eq=True,
    apply_stereo_enhancement=True,
    sample_rate=48000,
    bit_depth=24
):
    """
    Apply professional mastering chain to audio

    Args:
        input_path: Path to input audio file
        output_path: Path to output audio file
        target_lufs: Target integrated loudness (LUFS)
        target_tp: Target true peak (dBTP)
        target_lra: Target loudness range (LU)
        apply_eq: Apply warmth and presence EQ
        apply_stereo_enhancement: Apply subtle stereo widening
        sample_rate: Output sample rate
        bit_depth: Output bit depth (16 or 24)

    Returns:
        True on success, False on failure
    """
    print("\n" + "="*70)
    print("PROFESSIONAL AUDIO MASTERING")
    print("="*70 + "\n")

    # Analyze first
    analysis = analyze_loudness(input_path)

    print("="*70)
    print("STEP 2: Applying Mastering Chain")
    print("="*70 + "\n")

    # Build filter chain
    filters = []

    # 1. LUFS Normalization
    if analysis:
        filters.append(
            f"loudnorm=I={target_lufs}:TP={target_tp}:LRA={target_lra}:"
            f"measured_I={analysis['input_i']}:"
            f"measured_TP={analysis['input_tp']}:"
            f"measured_LRA={analysis['input_lra']}:"
            f"measured_thresh={analysis['input_thresh']}:"
            f"linear=true:print_format=summary"
        )
        print(f"✓ LUFS Normalization: {target_lufs} LUFS")
    else:
        # Fallback to single-pass
        filters.append(f"loudnorm=I={target_lufs}:TP={target_tp}:LRA={target_lra}")
        print(f"✓ LUFS Normalization: {target_lufs} LUFS (single-pass)")

    # 2. EQ for warmth and presence
    if apply_eq:
        # Warmth: Gentle boost to voice fundamentals (200-300 Hz)
        filters.append("equalizer=f=250:t=h:width=200:g=1.5")

        # Presence: Boost clarity (2-4 kHz)
        filters.append("equalizer=f=3000:t=h:width=2000:g=1.0")

        # High shelf: Gentle roll-off above 10 kHz (reduce harshness)
        filters.append("highshelf=f=10000:g=-0.5")

        print("✓ EQ Applied:")
        print("    +1.5 dB @ 250 Hz (warmth)")
        print("    +1.0 dB @ 3 kHz (presence)")
        print("    -0.5 dB > 10 kHz (smooth highs)")

    # 3. Stereo Enhancement
    if apply_stereo_enhancement:
        # Subtle widening - preserves mono compatibility
        # mlev (mid level) = 0.95, slev (side level) = 1.05
        filters.append("stereotools=mlev=0.95:slev=1.05:balance_in=0:balance_out=0")
        print("✓ Stereo Enhancement: 5% width increase")

    # 4. Final Safety Limiter
    # alimiter 'limit' parameter is linear (0.0625-1.0), not dB
    # 0.95 = approximately -0.45 dB, prevents clipping
    filters.append("alimiter=limit=0.95:attack=5:release=50")
    print("✓ Peak Limiter: 0.95 linear (~-0.45 dB) ceiling")

    filter_chain = ",".join(filters)

    # Determine output codec
    if bit_depth == 24:
        codec = 'pcm_s24le'
    else:
        codec = 'pcm_s16le'

    print(f"\nOutput Format: {bit_depth}-bit WAV @ {sample_rate} Hz")
    print()

    # Build FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', codec,
        '-ar', str(sample_rate),
        '-y',
        output_path
    ]

    print("Processing...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            print("\n✗ Mastering failed")
            print(result.stderr)
            return False

        # Verify output
        if not os.path.exists(output_path):
            print("\n✗ Output file not created")
            return False

        file_size = os.path.getsize(output_path) / (1024 * 1024)

        print("\n" + "="*70)
        print("✓ MASTERING COMPLETE!")
        print("="*70)
        print(f"\nMastered Audio: {output_path}")
        print(f"Size: {file_size:.1f} MB")
        print(f"Format: {bit_depth}-bit WAV @ {sample_rate} Hz")
        print(f"Target Loudness: {target_lufs} LUFS")
        print()

        return True

    except subprocess.TimeoutExpired:
        print("\n✗ Mastering timed out (>10 minutes)")
        return False
    except Exception as e:
        print(f"\n✗ Error during mastering: {e}")
        return False


def create_distribution_mp3(wav_path, mp3_path, bitrate='192k'):
    """
    Create high-quality MP3 from mastered WAV

    Args:
        wav_path: Path to mastered WAV file
        mp3_path: Path to output MP3 file
        bitrate: MP3 bitrate (e.g., '192k', '256k', '320k')

    Returns:
        True on success, False on failure
    """
    print("\n" + "="*70)
    print("Creating Distribution MP3")
    print("="*70 + "\n")

    cmd = [
        'ffmpeg',
        '-i', wav_path,
        '-c:a', 'libmp3lame',
        '-b:a', bitrate,
        '-y',
        mp3_path
    ]

    print(f"Source: {wav_path}")
    print(f"Output: {mp3_path}")
    print(f"Bitrate: {bitrate}")
    print()

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)

        file_size = os.path.getsize(mp3_path) / (1024 * 1024)
        print(f"✓ MP3 created: {file_size:.1f} MB\n")

        return True
    except Exception as e:
        print(f"✗ MP3 creation failed: {e}\n")
        return False


def master_from_manifest(manifest, session_dir):
    """
    Master audio based on session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        dict with paths to mastered files
    """
    print("\n" + "="*70)
    print("MASTERING FROM MANIFEST")
    print("="*70 + "\n")

    mastering_config = manifest.get('mastering', {})

    # Input: mixed audio
    input_path = os.path.join(session_dir, "working_files/mixed.wav")

    if not os.path.exists(input_path):
        print(f"✗ Mixed audio not found: {input_path}")
        print("Run mixer first!")
        return None

    # Outputs
    output_dir = os.path.join(session_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    session_name = manifest['session']['name'].lower().replace(' ', '_')

    wav_path = os.path.join(output_dir, f"{session_name}_master.wav")
    mp3_path = os.path.join(output_dir, f"{session_name}_master.mp3")

    # Master
    success = master_audio(
        input_path=input_path,
        output_path=wav_path,
        target_lufs=mastering_config.get('target_lufs', -14),
        target_tp=mastering_config.get('true_peak_dbtp', -1.5),
        target_lra=mastering_config.get('target_lra', 11),
        sample_rate=mastering_config.get('sample_rate_hz', 48000),
        bit_depth=mastering_config.get('bit_depth', 24)
    )

    if not success:
        return None

    # Create MP3
    create_distribution_mp3(wav_path, mp3_path)

    return {
        'wav': wav_path,
        'mp3': mp3_path
    }


def master_with_voice_enhancement(
    input_path,
    output_path,
    target_lufs=-14,
    target_tp=-1.5,
    target_lra=11,
    apply_eq=True,
    apply_stereo_enhancement=True,
    sample_rate=48000,
    bit_depth=24,
    # Voice enhancement options
    apply_voice_enhancement=True,
    warmth_drive=0.25,
    apply_deessing=True,
    add_whisper=True,
    whisper_db=-22,
    add_double=True,
    double_db=-14,
    double_delay_ms=8,
    add_room=True,
    room_amount=0.03,
    add_micropan=False,
    micropan_amount=0.03
):
    """
    Apply professional mastering chain with optional hypnotic voice enhancement

    This combines the voice enhancement processing (tape warmth, whisper overlay,
    double-voicing, room tone) with professional mastering (LUFS normalization,
    EQ, stereo enhancement, limiting).

    Args:
        input_path: Path to input audio file
        output_path: Path to output audio file
        target_lufs: Target integrated loudness (LUFS)
        target_tp: Target true peak (dBTP)
        target_lra: Target loudness range (LU)
        apply_eq: Apply warmth and presence EQ
        apply_stereo_enhancement: Apply subtle stereo widening
        sample_rate: Output sample rate
        bit_depth: Output bit depth (16 or 24)

        # Voice enhancement options:
        apply_voice_enhancement: Enable voice enhancement processing
        warmth_drive: Tape saturation amount (0.0-1.0)
        apply_deessing: Reduce harsh sibilance
        add_whisper: Add whisper overlay (spirit-double effect)
        whisper_db: Whisper layer volume
        add_double: Add phase-shifted double-voicing
        double_db: Double voice volume
        double_delay_ms: Double voice delay in milliseconds
        add_room: Add room impulse response
        room_amount: Room reverb mix (0.0-1.0)
        add_micropan: Add stereo micro-panning (ASMR effect)
        micropan_amount: Micro-panning intensity

    Returns:
        True on success, False on failure
    """
    print("\n" + "="*70)
    print("PROFESSIONAL MASTERING WITH VOICE ENHANCEMENT")
    print("="*70 + "\n")

    # Step 1: Apply voice enhancement if available and requested
    enhanced_input = input_path

    if apply_voice_enhancement:
        if not VOICE_ENHANCEMENT_AVAILABLE:
            print("⚠ Voice enhancement module not available, skipping...")
        else:
            print("="*70)
            print("STEP 0: Applying Hypnotic Voice Enhancement")
            print("="*70 + "\n")

            # Create temp file for enhanced audio
            import tempfile
            temp_dir = tempfile.gettempdir()
            enhanced_temp = os.path.join(temp_dir, "voice_enhanced_temp.wav")

            try:
                success = voice_enhancement.enhance_voice(
                    input_path=input_path,
                    output_path=enhanced_temp,
                    apply_warmth=True,
                    warmth_drive=warmth_drive,
                    apply_deessing=apply_deessing,
                    add_whisper=add_whisper,
                    whisper_db=whisper_db,
                    add_double=add_double,
                    double_db=double_db,
                    double_delay_ms=double_delay_ms,
                    add_room=add_room,
                    room_amount=room_amount,
                    add_micropan=add_micropan,
                    micropan_amount=micropan_amount,
                    cleanup_temp=True
                )

                if success and os.path.exists(enhanced_temp):
                    enhanced_input = enhanced_temp
                    print("✓ Voice enhancement applied successfully\n")
                else:
                    print("⚠ Voice enhancement failed, using original audio\n")

            except Exception as e:
                print(f"⚠ Voice enhancement error: {e}")
                print("  Using original audio\n")

    # Step 2: Apply standard mastering chain
    result = master_audio(
        input_path=enhanced_input,
        output_path=output_path,
        target_lufs=target_lufs,
        target_tp=target_tp,
        target_lra=target_lra,
        apply_eq=apply_eq,
        apply_stereo_enhancement=apply_stereo_enhancement,
        sample_rate=sample_rate,
        bit_depth=bit_depth
    )

    # Cleanup temp file
    if enhanced_input != input_path and os.path.exists(enhanced_input):
        try:
            os.remove(enhanced_input)
        except OSError:
            pass

    return result


def master_voice_from_manifest(manifest, session_dir):
    """
    Master voice audio with enhancement based on session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        dict with paths to mastered files
    """
    print("\n" + "="*70)
    print("MASTERING VOICE FROM MANIFEST (WITH ENHANCEMENT)")
    print("="*70 + "\n")

    mastering_config = manifest.get('mastering', {})
    voice_config = manifest.get('voice_enhancement', {})

    # Input: voice audio
    input_path = os.path.join(session_dir, "working_files/voice.wav")

    # Fallback to mixed if voice doesn't exist
    if not os.path.exists(input_path):
        input_path = os.path.join(session_dir, "working_files/mixed.wav")

    if not os.path.exists(input_path):
        print("✗ Audio not found in working_files/")
        return None

    # Outputs
    output_dir = os.path.join(session_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    session_name = manifest['session']['name'].lower().replace(' ', '_')

    wav_path = os.path.join(output_dir, f"{session_name}_master.wav")
    mp3_path = os.path.join(output_dir, f"{session_name}_master.mp3")

    # Determine if voice enhancement should be applied
    apply_enhancement = voice_config.get('enabled', True)

    # Master with enhancement
    success = master_with_voice_enhancement(
        input_path=input_path,
        output_path=wav_path,
        target_lufs=mastering_config.get('target_lufs', -14),
        target_tp=mastering_config.get('true_peak_dbtp', -1.5),
        target_lra=mastering_config.get('target_lra', 11),
        sample_rate=mastering_config.get('sample_rate_hz', 48000),
        bit_depth=mastering_config.get('bit_depth', 24),
        # Voice enhancement from manifest
        apply_voice_enhancement=apply_enhancement,
        warmth_drive=voice_config.get('warmth_drive', 0.25),
        apply_deessing=voice_config.get('deessing', True),
        add_whisper=voice_config.get('whisper_overlay', True),
        whisper_db=voice_config.get('whisper_db', -22),
        add_double=voice_config.get('double_voice', True),
        double_db=voice_config.get('double_db', -14),
        double_delay_ms=voice_config.get('double_delay_ms', 8),
        add_room=voice_config.get('room_tone', True),
        room_amount=voice_config.get('room_amount', 0.03),
        add_micropan=voice_config.get('stereo_micropan', False),
        micropan_amount=voice_config.get('micropan_amount', 0.03)
    )

    if not success:
        return None

    # Create MP3
    create_distribution_mp3(wav_path, mp3_path)

    return {
        'wav': wav_path,
        'mp3': mp3_path
    }


# Example usage for testing
if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='Professional audio mastering with optional hypnotic voice enhancement'
    )
    parser.add_argument('input', help='Input WAV file')
    parser.add_argument('-o', '--output', help='Output WAV file (default: <input>_MASTERED.wav)')
    parser.add_argument('--enhance', action='store_true',
                        help='Apply hypnotic voice enhancement (tape warmth, whisper overlay, etc.)')
    parser.add_argument('--lufs', type=float, default=-14,
                        help='Target LUFS (default: -14)')
    parser.add_argument('--no-whisper', action='store_true',
                        help='Disable whisper overlay')
    parser.add_argument('--no-double', action='store_true',
                        help='Disable phase-shifted double-voicing')

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output or input_file.replace('.wav', '_MASTERED.wav')

    print(f"Mastering: {input_file}")

    if args.enhance:
        print("Voice enhancement: ENABLED")
        success = master_with_voice_enhancement(
            input_path=input_file,
            output_path=output_file,
            target_lufs=args.lufs,
            target_tp=-1.5,
            apply_voice_enhancement=True,
            add_whisper=not args.no_whisper,
            add_double=not args.no_double
        )
    else:
        success = master_audio(
            input_path=input_file,
            output_path=output_file,
            target_lufs=args.lufs,
            target_tp=-1.5
        )

    if success:
        # Create MP3
        mp3_file = output_file.replace('.wav', '.mp3')
        create_distribution_mp3(output_file, mp3_file)

        print("\n" + "="*70)
        print("MASTERING COMPLETE!")
        print("="*70)
        print("\nOutputs:")
        print(f"  WAV: {output_file}")
        print(f"  MP3: {mp3_file}")
    else:
        print("\n✗ Mastering failed")
        sys.exit(1)
