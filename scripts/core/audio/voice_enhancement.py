#!/usr/bin/env python3
"""
Hypnotic Voice Enhancement Module
Post-processing techniques to make TTS voices smoother, warmer, and more trance-inducing

Techniques implemented:
1. Tape saturation / tube warmth
2. Whisper overlay (spirit-double effect)
3. Phase-shifted double-voicing
4. Room impulse response
5. Sibilance/plosive softening (de-esser)
6. Breath layer addition
7. Subtle stereo micro-panning
8. Low-pass warmth filter
9. Subharmonic warm layer (bass doubling)
10. Amplitude modulation "cuddle waves" (slow volume undulation)
11. Triple-layered hypnotic presence (main + whisper + subharmonic)

Based on professional hypnosis audio production techniques.
"""

import subprocess
import os
import sys
import numpy as np
from scipy.io import wavfile
from scipy import signal
import tempfile
import shutil


def _run_ffmpeg(cmd, timeout=300):
    """Run FFmpeg command and handle errors"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def apply_tape_warmth(input_path, output_path, drive=0.3, warmth=0.5):
    """
    Apply tape saturation and tube warmth effect

    Adds subtle harmonic distortion that creates warmth and "body resonance"

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        drive: Saturation amount (0.0-1.0, default 0.3)
        warmth: Low-frequency emphasis (0.0-1.0, default 0.5)

    Returns:
        True on success
    """
    print("  Applying tape warmth...")

    # FFmpeg filter chain for tape warmth:
    # 1. Subtle soft clipping (asymmetric saturation)
    # 2. Low-shelf boost for warmth
    # 3. High-frequency roll-off (tape head loss simulation)

    saturation = 1.0 + (drive * 0.5)  # 1.0-1.5 range
    low_boost = warmth * 2.0  # 0-2 dB boost

    filters = [
        # Soft saturation via acompressor with makeup gain
        f"acompressor=threshold=0.7:ratio=3:attack=5:release=50:makeup={drive}",
        # Warmth: low-shelf boost
        f"lowshelf=f=200:g={low_boost}:t=s",
        # Tape roll-off: gentle high-shelf cut
        "highshelf=f=8000:g=-1.5:t=s",
        # Subtle harmonic enhancement via bass boost + soft limit
        "bass=g=1.5:f=150",
    ]

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print("    ✓ Tape warmth applied")
    else:
        print(f"    ✗ Tape warmth failed: {error}")

    return success


def apply_de_esser(input_path, output_path, threshold=0.4, frequency=6000):
    """
    Reduce harsh sibilance (s, sh, ch sounds) and plosives

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        threshold: Detection threshold (0.0-1.0)
        frequency: Target frequency for sibilance (Hz)

    Returns:
        True on success
    """
    print("  Applying de-esser...")

    # FFmpeg de-esser filter chain:
    # High-shelf compressor targeting sibilant frequencies

    filters = [
        # Split into bands, compress the high-frequency band
        f"highpass=f={frequency-1000}",
        f"acompressor=threshold={threshold}:ratio=4:attack=1:release=50",
        # Reduce harshness in the 4-8 kHz range
        f"equalizer=f={frequency}:t=h:width=2000:g=-2",
    ]

    # Alternative approach using bandreject for specific sibilance reduction
    filter_chain = f"equalizer=f={frequency}:t=h:width=1500:g=-3,highshelf=f=10000:g=-1"

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print("    ✓ De-esser applied")
    else:
        print(f"    ✗ De-esser failed: {error}")

    return success


def create_whisper_layer(input_path, output_path, volume_db=-20, reverb_wet=0.2):
    """
    Create whisper overlay (spirit-double effect)

    Duplicates voice, applies high-pass filter, reverb, and stereo spread
    Creates subliminal reinforcement layer

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        volume_db: Volume reduction in dB (default -20)
        reverb_wet: Reverb wet/dry mix (0.0-1.0)

    Returns:
        True on success
    """
    print("  Creating whisper layer...")

    # Convert dB to linear gain
    linear_gain = 10 ** (volume_db / 20)

    filters = [
        # High-pass filter (voice becomes whisper-like)
        "highpass=f=900",
        # Gentle low-pass to remove harshness
        "lowpass=f=6000",
        # Add subtle reverb using FFmpeg's aecho
        f"aecho=0.8:0.7:60:0.3",
        # Reduce volume
        f"volume={linear_gain}",
        # Stereo spread
        "stereotools=slev=1.2:mlev=0.8",
    ]

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print(f"    ✓ Whisper layer created at {volume_db} dB")
    else:
        print(f"    ✗ Whisper layer failed: {error}")

    return success


def create_double_voice(input_path, output_path, delay_ms=8, volume_db=-12):
    """
    Create phase-shifted double-voicing effect

    Duplicates voice with slight delay and low-pass filter
    Creates "presence" and warm human room-tone

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        delay_ms: Delay in milliseconds (5-12 typical)
        volume_db: Volume reduction in dB

    Returns:
        True on success
    """
    print("  Creating double-voice layer...")

    linear_gain = 10 ** (volume_db / 20)

    filters = [
        # Delay
        f"adelay={delay_ms}|{delay_ms}",
        # Low-pass filter (soften the doubled voice)
        "lowpass=f=5000",
        # Reduce volume
        f"volume={linear_gain}",
    ]

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print(f"    ✓ Double-voice created ({delay_ms}ms delay, {volume_db} dB)")
    else:
        print(f"    ✗ Double-voice failed: {error}")

    return success


def add_room_tone(input_path, output_path, room_amount=0.03):
    """
    Add subtle room impulse response

    Makes voice feel physically present without obvious echo

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        room_amount: Mix amount (0.0-0.1, 3-5% typical)

    Returns:
        True on success
    """
    print("  Adding room presence...")

    # Use FFmpeg's aecho to simulate small room
    # Format: in_gain|out_gain|delays|decays
    # Short delays (10-30ms) with rapid decay = small room feel

    filters = [
        f"aecho=0.8:0.9:10|15|20:0.3|0.25|0.2",
        # Mix back with dry signal (room_amount as wet level)
        # This is approximated by the aecho parameters
    ]

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print(f"    ✓ Room presence added ({room_amount*100:.0f}% wet)")
    else:
        print(f"    ✗ Room tone failed: {error}")

    return success


def apply_stereo_micropanning(input_path, output_path, amount=0.03):
    """
    Apply subtle stereo micro-movements

    Creates sense of being "inside" the experience
    Uses slow LFO panning (ASMR-like effect)

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        amount: Panning amount (0.0-0.1, 3-5% typical)

    Returns:
        True on success
    """
    print("  Applying stereo micro-panning...")

    # FFmpeg apulsator creates subtle stereo movement
    # Very slow LFO (0.1 Hz) with minimal depth

    depth = min(amount * 3, 0.15)  # Max 15% depth

    filters = [
        f"apulsator=mode=sine:hz=0.08:amount={depth}:offset_l=0:offset_r=0.5",
    ]

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print(f"    ✓ Stereo micro-panning applied ({amount*100:.0f}% depth)")
    else:
        print(f"    ✗ Micro-panning failed: {error}")

    return success


def create_subharmonic_layer(input_path, output_path, volume_db=-12):
    """
    Create subharmonic warm layer (bass doubling)

    Duplicates voice, applies low-pass filter and slight delay
    Creates warm, body-resonance foundation beneath the voice

    This is Layer 3 of the triple-layered hypnotic presence:
    - Layer 1: Main voice (clear, natural)
    - Layer 2: Whisper ghost (HPF + reverb)
    - Layer 3: Subharmonic warm (LPF + delay)

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        volume_db: Volume reduction in dB (default -12)

    Returns:
        True on success
    """
    print("  Creating subharmonic warm layer...")

    linear_gain = 10 ** (volume_db / 20)

    filters = [
        # Low-pass filter at 400 Hz (only bass frequencies)
        "lowpass=f=400",
        # Slight delay (5-12ms creates warmth without obvious echo)
        "adelay=8|8",
        # Additional low-shelf boost for body resonance
        "lowshelf=f=200:g=2:t=s",
        # Reduce volume
        f"volume={linear_gain}",
    ]

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print(f"    ✓ Subharmonic layer created at {volume_db} dB")
    else:
        print(f"    ✗ Subharmonic layer failed: {error}")

    return success


def apply_cuddle_waves(input_path, output_path, frequency_hz=0.05, depth_db=1.5):
    """
    Apply amplitude modulation "cuddle waves"

    Subtle slow-volume undulations that create metaphorical "rocking"
    in the listener's nervous system. Simulates being gently held.

    Uses very slow LFO (0.04-0.07 Hz) with small amplitude variation (±1.5 dB)

    Args:
        input_path: Path to input audio
        output_path: Path to output audio
        frequency_hz: LFO frequency in Hz (default 0.05 = one cycle per 20 seconds)
        depth_db: Volume variation depth in dB (default 1.5)

    Returns:
        True on success
    """
    print("  Applying cuddle waves (amplitude modulation)...")

    # Convert dB depth to linear amount
    # ±1.5 dB means multiplier varies from ~0.84 to ~1.19
    # FFmpeg's tremolo effect uses amount as percentage
    depth_percent = (10 ** (depth_db / 20) - 1) * 100  # ~18.8% for 1.5 dB

    # Clamp depth to safe range
    depth_percent = min(max(depth_percent, 5), 30)

    filters = [
        # Tremolo effect: very slow sine wave modulation
        f"tremolo=f={frequency_hz}:d={depth_percent/100}",
    ]

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print(f"    ✓ Cuddle waves applied ({frequency_hz} Hz, ±{depth_db} dB)")
    else:
        print(f"    ✗ Cuddle waves failed: {error}")

    return success


def generate_breath_layer(duration_seconds, output_path, sample_rate=48000):
    """
    Generate ultra-quiet breath cues

    Creates subliminal "safety" signal for nervous system

    Args:
        duration_seconds: Duration of audio
        output_path: Path to output audio
        sample_rate: Sample rate

    Returns:
        True on success
    """
    print("  Generating breath layer...")

    try:
        # Generate very quiet pink noise bursts as "breath" approximation
        duration = int(duration_seconds * sample_rate)
        breath_audio = np.zeros((duration, 2), dtype=np.float32)

        # Create breath-like sounds every 4-6 seconds
        breath_interval = int(5 * sample_rate)  # 5 seconds average
        breath_duration = int(0.4 * sample_rate)  # 400ms breath

        num_breaths = duration // breath_interval

        for i in range(num_breaths):
            start = i * breath_interval + np.random.randint(-sample_rate, sample_rate)
            start = max(0, min(start, duration - breath_duration))

            # Generate soft noise burst
            noise = np.random.randn(breath_duration, 2).astype(np.float32)

            # Shape with envelope (fade in/out)
            envelope = np.hanning(breath_duration)
            noise *= envelope[:, np.newaxis]

            # Very quiet (-40 dB)
            noise *= 0.01

            # Lowpass filter effect (make it softer)
            # Simple averaging for smoothing
            for j in range(3):
                noise[1:] = (noise[1:] + noise[:-1]) / 2

            end = start + breath_duration
            if end <= duration:
                breath_audio[start:end] += noise

        # Normalize to prevent clipping
        max_val = np.max(np.abs(breath_audio))
        if max_val > 0:
            breath_audio = breath_audio / max_val * 0.01  # Keep very quiet

        # Save as WAV
        breath_audio_int = (breath_audio * 32767).astype(np.int16)
        wavfile.write(output_path, sample_rate, breath_audio_int)

        print(f"    ✓ Breath layer generated ({num_breaths} breaths)")
        return True

    except Exception as e:
        print(f"    ✗ Breath layer failed: {e}")
        return False


def mix_enhancement_layers(
    voice_path,
    output_path,
    whisper_path=None,
    double_path=None,
    breath_path=None,
    subharmonic_path=None
):
    """
    Mix voice with enhancement layers

    Creates triple-layered hypnotic presence:
    - Layer 1: Main voice (clear, natural)
    - Layer 2: Whisper ghost (HPF + reverb) - ethereal presence above
    - Layer 3: Subharmonic warm (LPF + delay) - grounding presence below

    Args:
        voice_path: Path to main voice audio
        output_path: Path to output
        whisper_path: Path to whisper layer (optional)
        double_path: Path to double-voice layer (optional)
        breath_path: Path to breath layer (optional)
        subharmonic_path: Path to subharmonic warm layer (optional)

    Returns:
        True on success
    """
    print("  Mixing enhancement layers...")

    inputs = ['-i', voice_path]
    filter_inputs = ['[0:a]']

    idx = 1
    if whisper_path and os.path.exists(whisper_path):
        inputs.extend(['-i', whisper_path])
        filter_inputs.append(f'[{idx}:a]')
        idx += 1

    if double_path and os.path.exists(double_path):
        inputs.extend(['-i', double_path])
        filter_inputs.append(f'[{idx}:a]')
        idx += 1

    if breath_path and os.path.exists(breath_path):
        inputs.extend(['-i', breath_path])
        filter_inputs.append(f'[{idx}:a]')
        idx += 1

    if subharmonic_path and os.path.exists(subharmonic_path):
        inputs.extend(['-i', subharmonic_path])
        filter_inputs.append(f'[{idx}:a]')
        idx += 1

    # Mix all inputs
    filter_complex = f"{''.join(filter_inputs)}amix=inputs={len(filter_inputs)}:duration=longest:normalize=0"

    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex', filter_complex,
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        output_path
    ]

    success, error = _run_ffmpeg(cmd)
    if success:
        print(f"    ✓ {len(filter_inputs)} layers mixed (triple-layer presence)")
    else:
        print(f"    ✗ Layer mixing failed: {error}")

    return success


def enhance_voice(
    input_path,
    output_path,
    apply_warmth=True,
    apply_deessing=True,
    add_whisper=True,
    add_double=True,
    add_breath=False,
    add_room=True,
    add_micropan=False,
    add_subharmonic=True,
    add_cuddle_waves=True,
    warmth_drive=0.25,
    whisper_db=-22,
    double_db=-14,
    double_delay_ms=8,
    room_amount=0.03,
    micropan_amount=0.03,
    subharmonic_db=-12,
    cuddle_frequency=0.05,
    cuddle_depth_db=1.5,
    cleanup_temp=True
):
    """
    Apply full hypnotic voice enhancement chain

    Creates triple-layered hypnotic presence with psychoacoustic enhancements:
    - Layer 1: Main voice (clear, natural)
    - Layer 2: Whisper ghost (HPF + reverb) - ethereal presence
    - Layer 3: Subharmonic warm (LPF + delay) - grounding presence

    Args:
        input_path: Path to input voice audio
        output_path: Path to enhanced output
        apply_warmth: Apply tape saturation warmth
        apply_deessing: Reduce sibilance
        add_whisper: Add whisper overlay (spirit-double)
        add_double: Add phase-shifted double
        add_breath: Add breath layer
        add_room: Add room presence
        add_micropan: Add stereo micro-panning
        add_subharmonic: Add subharmonic warm layer (bass foundation)
        add_cuddle_waves: Add amplitude modulation (gentle rocking)
        warmth_drive: Warmth amount (0-1)
        whisper_db: Whisper layer volume
        double_db: Double-voice volume
        double_delay_ms: Double-voice delay
        room_amount: Room mix amount
        micropan_amount: Panning depth
        subharmonic_db: Subharmonic layer volume
        cuddle_frequency: Cuddle wave LFO frequency (Hz)
        cuddle_depth_db: Cuddle wave amplitude variation (dB)
        cleanup_temp: Remove temporary files

    Returns:
        True on success
    """
    print("\n" + "="*70)
    print("HYPNOTIC VOICE ENHANCEMENT")
    print("="*70 + "\n")

    # Create temp directory for intermediate files
    temp_dir = tempfile.mkdtemp(prefix="voice_enhance_")

    try:
        current_file = input_path
        step = 0

        # Get audio duration for breath layer
        try:
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                        input_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
        except (ValueError, AttributeError, subprocess.SubprocessError):
            duration = 1800  # Default 30 minutes

        # Step 1: De-essing (do this first to prevent artifacts)
        if apply_deessing:
            step += 1
            step_output = os.path.join(temp_dir, f"step{step}_deessed.wav")
            if apply_de_esser(current_file, step_output):
                current_file = step_output

        # Step 2: Tape warmth
        if apply_warmth:
            step += 1
            step_output = os.path.join(temp_dir, f"step{step}_warm.wav")
            if apply_tape_warmth(current_file, step_output, drive=warmth_drive):
                current_file = step_output

        # Step 3: Room presence
        if add_room:
            step += 1
            step_output = os.path.join(temp_dir, f"step{step}_room.wav")
            if add_room_tone(current_file, step_output, room_amount=room_amount):
                current_file = step_output

        # Step 4: Micro-panning
        if add_micropan:
            step += 1
            step_output = os.path.join(temp_dir, f"step{step}_panned.wav")
            if apply_stereo_micropanning(current_file, step_output, amount=micropan_amount):
                current_file = step_output

        # Create enhancement layers
        whisper_path = None
        double_path = None
        breath_path = None
        subharmonic_path = None

        # Step 5: Create whisper layer (Layer 2: ethereal presence above)
        if add_whisper:
            whisper_path = os.path.join(temp_dir, "whisper_layer.wav")
            create_whisper_layer(input_path, whisper_path, volume_db=whisper_db)

        # Step 6: Create double-voice layer
        if add_double:
            double_path = os.path.join(temp_dir, "double_layer.wav")
            create_double_voice(input_path, double_path,
                              delay_ms=double_delay_ms, volume_db=double_db)

        # Step 7: Create subharmonic warm layer (Layer 3: grounding presence below)
        if add_subharmonic:
            subharmonic_path = os.path.join(temp_dir, "subharmonic_layer.wav")
            create_subharmonic_layer(input_path, subharmonic_path,
                                    volume_db=subharmonic_db)

        # Step 8: Create breath layer
        if add_breath:
            breath_path = os.path.join(temp_dir, "breath_layer.wav")
            generate_breath_layer(duration, breath_path)

        # Step 9: Mix all layers (triple-layered hypnotic presence)
        if any([whisper_path, double_path, breath_path, subharmonic_path]):
            step += 1
            step_output = os.path.join(temp_dir, f"step{step}_layered.wav")
            if mix_enhancement_layers(current_file, step_output,
                                     whisper_path, double_path, breath_path,
                                     subharmonic_path):
                current_file = step_output

        # Step 10: Apply cuddle waves (amplitude modulation for gentle rocking)
        if add_cuddle_waves:
            step += 1
            step_output = os.path.join(temp_dir, f"step{step}_cuddle.wav")
            if apply_cuddle_waves(current_file, step_output,
                                 frequency_hz=cuddle_frequency,
                                 depth_db=cuddle_depth_db):
                current_file = step_output

        # Final output
        shutil.copy(current_file, output_path)

        # Report
        print("\n" + "="*70)
        print("✓ VOICE ENHANCEMENT COMPLETE")
        print("="*70)

        enhancements = []
        if apply_deessing:
            enhancements.append("De-essing")
        if apply_warmth:
            enhancements.append(f"Tape warmth ({warmth_drive*100:.0f}%)")
        if add_room:
            enhancements.append(f"Room presence ({room_amount*100:.0f}%)")
        if add_micropan:
            enhancements.append(f"Stereo micro-panning ({micropan_amount*100:.0f}%)")
        if add_whisper:
            enhancements.append(f"Whisper layer ({whisper_db} dB)")
        if add_double:
            enhancements.append(f"Double-voice ({double_db} dB, {double_delay_ms}ms)")
        if add_subharmonic:
            enhancements.append(f"Subharmonic warm ({subharmonic_db} dB)")
        if add_breath:
            enhancements.append("Breath cues")
        if add_cuddle_waves:
            enhancements.append(f"Cuddle waves ({cuddle_frequency} Hz, ±{cuddle_depth_db} dB)")

        print("\nEnhancements applied:")
        for e in enhancements:
            print(f"  ✓ {e}")

        print(f"\nOutput: {output_path}")

        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Size: {file_size:.1f} MB")

        return True

    except Exception as e:
        print(f"\n✗ Enhancement failed: {e}")
        return False

    finally:
        # Cleanup temp files
        if cleanup_temp and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


# CLI interface
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Hypnotic Voice Enhancement")
        print("="*40)
        print("\nUsage: python3 voice_enhancement.py <input.wav> [output.wav]")
        print("\nApplies professional hypnotic voice enhancement:")
        print("  - Tape saturation warmth")
        print("  - De-essing (sibilance reduction)")
        print("  - Whisper overlay (spirit-double)")
        print("  - Phase-shifted double-voicing")
        print("  - Room impulse response")
        print("\nOptional flags:")
        print("  --no-whisper    Skip whisper layer")
        print("  --no-double     Skip double-voice")
        print("  --add-breath    Add breath cues")
        print("  --add-micropan  Add stereo micro-panning")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) > 2 and not sys.argv[2].startswith('--'):
        output_file = sys.argv[2]
    else:
        output_file = input_file.replace('.wav', '_ENHANCED.wav').replace('.mp3', '_ENHANCED.wav')

    # Parse flags
    add_whisper = '--no-whisper' not in sys.argv
    add_double = '--no-double' not in sys.argv
    add_breath = '--add-breath' in sys.argv
    add_micropan = '--add-micropan' in sys.argv

    success = enhance_voice(
        input_file,
        output_file,
        add_whisper=add_whisper,
        add_double=add_double,
        add_breath=add_breath,
        add_micropan=add_micropan
    )

    sys.exit(0 if success else 1)
