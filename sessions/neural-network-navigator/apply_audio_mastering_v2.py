#!/usr/bin/env python3
"""
Professional Audio Mastering for Neural Network Navigator V2
Applies LUFS normalization, EQ warmth, peak limiting, and stereo enhancement
"""

import subprocess
import os
import sys

def check_dependencies():
    """Check for required tools"""
    print("\n" + "=" * 70)
    print("AUDIO MASTERING - Dependency Check")
    print("=" * 70 + "\n")

    # Check for ffmpeg with loudnorm filter
    try:
        result = subprocess.run(
            ['ffmpeg', '-filters'],
            capture_output=True,
            text=True
        )
        if 'loudnorm' not in result.stdout:
            print("✗ FFmpeg loudnorm filter not found")
            print("  Install ffmpeg with: sudo apt install ffmpeg")
            return False
        print("✓ FFmpeg with loudnorm filter")
    except FileNotFoundError:
        print("✗ FFmpeg not found")
        print("  Install with: sudo apt install ffmpeg")
        return False

    return True

def analyze_lufs(input_file):
    """
    First pass: Analyze current LUFS levels
    Returns integrated loudness value
    """
    print("\n" + "=" * 70)
    print("STEP 1: Analyzing Current Audio Levels")
    print("=" * 70 + "\n")

    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary',
        '-f', 'null',
        '-'
    ]

    print(f"Analyzing: {input_file}")
    print("This will take 2-3 minutes for 28-minute file...\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Parse output for current levels
        output = result.stderr

        # Extract key metrics
        input_i = None
        input_tp = None
        input_lra = None
        input_thresh = None

        for line in output.split('\n'):
            if 'Input Integrated:' in line:
                input_i = line.split(':')[1].strip().split()[0]
            elif 'Input True Peak:' in line:
                input_tp = line.split(':')[1].strip().split()[0]
            elif 'Input LRA:' in line:
                input_lra = line.split(':')[1].strip().split()[0]
            elif 'Input Threshold:' in line:
                input_thresh = line.split(':')[1].strip().split()[0]

        print("Current Audio Levels:")
        print(f"  Integrated Loudness: {input_i} LUFS")
        print(f"  True Peak:          {input_tp} dBTP")
        print(f"  Loudness Range:     {input_lra} LU")
        print(f"  Threshold:          {input_thresh} LUFS")
        print()

        return output

    except subprocess.TimeoutExpired:
        print("✗ Analysis timed out (>5 minutes)")
        return None
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        return None

def apply_mastering(input_file, output_file, analysis_data):
    """
    Apply professional mastering chain:
    1. LUFS normalization to -14 (YouTube standard)
    2. Subtle warmth EQ (enhance voice frequencies)
    3. Peak limiting to prevent clipping
    4. Stereo width enhancement on binaural content
    """
    print("=" * 70)
    print("STEP 2: Applying Professional Mastering")
    print("=" * 70 + "\n")

    # Extract measured values from first pass
    measured_I = None
    measured_TP = None
    measured_LRA = None
    measured_thresh = None

    for line in analysis_data.split('\n'):
        if 'Input Integrated:' in line:
            measured_I = line.split(':')[1].strip().split()[0]
        elif 'Input True Peak:' in line:
            measured_TP = line.split(':')[1].strip().split()[0]
        elif 'Input LRA:' in line:
            measured_LRA = line.split(':')[1].strip().split()[0]
        elif 'Input Threshold:' in line:
            measured_thresh = line.split(':')[1].strip().split()[0]

    # Build comprehensive filter chain
    filters = []

    # 1. LUFS Normalization (-14 LUFS for YouTube)
    if measured_I and measured_TP and measured_LRA and measured_thresh:
        filters.append(
            f"loudnorm=I=-14:TP=-1.5:LRA=11:"
            f"measured_I={measured_I}:"
            f"measured_TP={measured_TP}:"
            f"measured_LRA={measured_LRA}:"
            f"measured_thresh={measured_thresh}:"
            f"linear=true:print_format=summary"
        )
    else:
        # Fallback to single-pass if measurements failed
        filters.append("loudnorm=I=-14:TP=-1.5:LRA=11")

    # 2. Subtle Warmth EQ
    # Gentle boost to voice fundamental frequencies (200-300 Hz)
    # Slight presence boost (2-4 kHz for clarity)
    # High-shelf roll-off above 10 kHz (reduce harshness)
    filters.append(
        "equalizer=f=250:t=h:width=200:g=1.5"  # Warmth
    )
    filters.append(
        "equalizer=f=3000:t=h:width=2000:g=1.0"  # Presence
    )
    filters.append(
        "highshelf=f=10000:g=-0.5"  # Gentle high-end taming
    )

    # 3. Stereo Width Enhancement (only affects binaural content)
    # Preserves mono voice, widens stereo binaural beats
    filters.append(
        "stereotools=mlev=0.95:slev=1.05:balance_in=0:balance_out=0"
    )

    # 4. Final Safety Limiter
    # Prevents any clipping from EQ boosts
    filters.append(
        "alimiter=limit=-1.0:attack=5:release=50"
    )

    filter_chain = ",".join(filters)

    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-af', filter_chain,
        '-c:a', 'pcm_s24le',  # High-quality WAV output
        '-ar', '48000',        # 48 kHz sample rate (pro standard)
        '-y',
        output_file
    ]

    print("Mastering Chain:")
    print("  1. LUFS Normalization → -14 LUFS (YouTube standard)")
    print("  2. Warmth EQ          → +1.5 dB @ 250 Hz")
    print("  3. Presence EQ        → +1.0 dB @ 3 kHz")
    print("  4. High Shelf         → -0.5 dB above 10 kHz")
    print("  5. Stereo Enhancement → 5% width increase")
    print("  6. Peak Limiter       → -1.0 dBTP ceiling")
    print()
    print(f"Output: {output_file}")
    print("Output Format: 24-bit WAV @ 48 kHz")
    print()
    print("Processing (this will take 3-5 minutes)...\n")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Monitor progress
        for line in process.stdout:
            # Show relevant progress lines
            if 'time=' in line:
                # Extract time for progress indicator
                import re
                time_match = re.search(r'time=(\\d+):(\\d+):(\\d+)', line)
                if time_match:
                    h, m, s = map(int, time_match.groups())
                    elapsed = h * 3600 + m * 60 + s
                    # Assume 28.7 minutes duration
                    total_seconds = 1722
                    progress = (elapsed / total_seconds) * 100
                    print(f"\\rProgress: {progress:.1f}%", end='', flush=True)

        process.wait()
        print()  # New line after progress

        if process.returncode != 0:
            print("\\n✗ Mastering failed")
            return False

        # Verify output
        if not os.path.exists(output_file):
            print("\\n✗ Output file not created")
            return False

        file_size = os.path.getsize(output_file) / (1024 * 1024)

        print("\\n" + "=" * 70)
        print("✓ MASTERING COMPLETE!")
        print("=" * 70)
        print(f"\\nMastered Audio: {output_file}")
        print(f"Size: {file_size:.1f} MB")
        print(f"Format: 24-bit WAV @ 48 kHz")
        print(f"Target Loudness: -14 LUFS (YouTube optimized)")
        print()

        return True

    except Exception as e:
        print(f"\\n✗ Error during mastering: {e}")
        return False

def create_mp3_export(wav_file, mp3_file):
    """
    Create high-quality MP3 export for distribution
    """
    print("=" * 70)
    print("STEP 3: Creating MP3 Export")
    print("=" * 70 + "\n")

    cmd = [
        'ffmpeg',
        '-i', wav_file,
        '-c:a', 'libmp3lame',
        '-b:a', '192k',  # High quality for meditation audio
        '-y',
        mp3_file
    ]

    print(f"Creating: {mp3_file}")
    print("Bitrate: 192 kbps (high quality)")
    print()

    try:
        subprocess.run(cmd, check=True, capture_output=True)

        file_size = os.path.getsize(mp3_file) / (1024 * 1024)

        print(f"✓ MP3 created: {file_size:.1f} MB")
        print()

        return True
    except Exception as e:
        print(f"✗ MP3 export failed: {e}")
        return False

def main():
    print("=" * 70)
    print("PROFESSIONAL AUDIO MASTERING - Neural Network Navigator V2")
    print("=" * 70)

    # Check dependencies
    if not check_dependencies():
        print("\\n✗ Missing dependencies")
        return 1

    # File paths
    input_file = "working_files/neural_navigator_complete_enhanced_v2.wav"
    output_file = "working_files/neural_navigator_complete_enhanced_v2_MASTERED.wav"
    mp3_file = "final_export/neural_network_navigator_v2_MASTERED.mp3"

    # Verify input exists
    if not os.path.exists(input_file):
        print(f"\\n✗ Input file not found: {input_file}")
        print("\\nRun ./create_enhanced_audio_v2.sh first")
        return 1

    # Create output directory
    os.makedirs("final_export", exist_ok=True)

    # Step 1: Analyze current levels
    analysis_data = analyze_lufs(input_file)
    if not analysis_data:
        print("\\n✗ Analysis failed")
        return 1

    # Step 2: Apply mastering
    if not apply_mastering(input_file, output_file, analysis_data):
        print("\\n✗ Mastering failed")
        return 1

    # Step 3: Create MP3 export
    if not create_mp3_export(output_file, mp3_file):
        print("\\n✗ MP3 export failed")
        return 1

    print("=" * 70)
    print("✨ PROFESSIONAL MASTERING COMPLETE!")
    print("=" * 70)
    print()
    print("Outputs Created:")
    print(f"  1. {output_file}")
    print(f"     → Mastered 24-bit WAV for archival/future use")
    print()
    print(f"  2. {mp3_file}")
    print(f"     → High-quality MP3 for distribution")
    print()
    print("Mastering Applied:")
    print("  ✓ LUFS normalized to -14 (YouTube optimized)")
    print("  ✓ Warmth EQ on voice frequencies")
    print("  ✓ Presence enhancement for clarity")
    print("  ✓ Stereo width optimization")
    print("  ✓ Peak limiting for safety")
    print()
    print("Next Steps:")
    print("  1. Compare mastered vs. unmastered (A/B test)")
    print("  2. Upload mastered MP3 to video project if desired")
    print("  3. Use mastered audio for all final distributions")
    print()
    print("Note: The current video uses the unmastered audio.")
    print("To use mastered audio in video, re-run composite script with mastered file.")

    return 0

if __name__ == '__main__':
    exit(main())
