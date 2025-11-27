#!/usr/bin/env python3
"""
OPTIMIZED Video Compositor for Neural Network Navigator
Improvements over original:
- Single-pass FFmpeg operation (no intermediate gradient video)
- Uses faster encoding presets
- Progress reporting
- Better error handling
- Reduced disk I/O
"""

import subprocess
import os
import sys

# Video specifications
WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 1680

# Image timings (image_file, start_time, end_time, fade_duration)
IMAGE_TIMINGS = [
    ("scene_01_opening_FINAL.png", 0, 150, 5.0),
    ("scene_02_descent_FINAL.png", 148, 420, 2.0),
    ("scene_03_neural_garden_FINAL.png", 418, 690, 2.0),
    ("scene_04_pathfinder_FINAL.png", 688, 960, 2.0),
    ("scene_05_weaver_FINAL.png", 958, 1128, 2.0),
    ("scene_06_gamma_burst_FINAL.png", 1125, 1128, 0.2),  # CRITICAL: Gamma flash
    ("scene_07_consolidation_FINAL.png", 1126, 1440, 2.0),
    ("scene_08_return_FINAL.png", 1438, 1680, 2.0),
]

def verify_prerequisites():
    """Check that all required files exist before starting"""
    print("\n" + "=" * 70)
    print("PRE-FLIGHT CHECK")
    print("=" * 70 + "\n")

    missing = []

    # Check images
    print("Checking images...")
    images_dir = "images"
    for img_file, _, _, _ in IMAGE_TIMINGS:
        img_path = f"{images_dir}/{img_file}"
        if not os.path.exists(img_path):
            missing.append(img_path)
        else:
            size_mb = os.path.getsize(img_path) / (1024 * 1024)
            print(f"  ✓ {img_file} ({size_mb:.1f} MB)")

    # Check gradients
    print("\nChecking gradients...")
    gradients_needed = [
        "gradient_01_opening.png",
        "gradient_02_descent.png",
        "gradient_03_neural_garden.png",
        "gradient_04_pathfinder.png",
        "gradient_05_weaver.png",
        "gradient_06_gamma_burst.png",
        "gradient_07_consolidation.png",
        "gradient_08_return.png",
    ]

    for gradient in gradients_needed:
        gradient_path = f"gradients/{gradient}"
        if not os.path.exists(gradient_path):
            missing.append(gradient_path)
        else:
            print(f"  ✓ {gradient}")

    # Check audio
    print("\nChecking audio...")
    audio_path = "working_files/audio_mix_master.wav"
    if not os.path.exists(audio_path):
        missing.append(audio_path)
    else:
        size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"  ✓ audio_mix_master.wav ({size_mb:.1f} MB)")

    if missing:
        print(f"\n✗ Missing files:")
        for f in missing:
            print(f"  - {f}")
        return False

    print(f"\n✓ All prerequisites satisfied\n")
    return True

def create_video_with_single_pass():
    """
    Create final video in a single optimized FFmpeg operation
    This composites images directly without intermediate video file
    """
    print("=" * 70)
    print("SINGLE-PASS VIDEO COMPOSITION")
    print("=" * 70 + "\n")

    images_dir = "images"
    audio_path = "working_files/audio_mix_master.wav"
    final_output = "final_export/neural_network_navigator.mp4"

    os.makedirs("final_export", exist_ok=True)

    # Build FFmpeg command - start with base gradient as color source
    cmd = ['ffmpeg', '-y']

    # Use base gradient as video stream foundation
    cmd.extend(['-loop', '1', '-i', 'gradients/gradient_01_opening.png'])

    # Add all 8 images
    for img_file, _, _, _ in IMAGE_TIMINGS:
        cmd.extend(['-loop', '1', '-i', f'{images_dir}/{img_file}'])

    # Add audio
    cmd.extend(['-i', audio_path])

    # Build complex filter
    filters = []

    # Base gradient scaled to video size with duration limit
    filters.append(
        f"[0:v]scale={WIDTH}:{HEIGHT},"
        f"fps={FPS},"
        f"trim=duration={DURATION},"
        f"setpts=PTS-STARTPTS"
        f"[base]"
    )

    # Scale and add alpha to all images
    for idx in range(len(IMAGE_TIMINGS)):
        input_num = idx + 1
        filters.append(
            f"[{input_num}:v]"
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
            f"format=yuva420p"
            f"[img{idx}]"
        )

    # Apply time-based alpha for each image
    for idx, (img_file, start_sec, end_sec, fade_duration) in enumerate(IMAGE_TIMINGS):
        fade_in_end = start_sec + fade_duration
        fade_out_start = end_sec - fade_duration

        # Gamma burst special handling
        if "gamma_burst" in img_file:
            # Ultra-fast 0.2s flash
            alpha_expr = (
                f"'if(lt(T,{start_sec}),0,"
                f"if(lt(T,{start_sec + 0.2}),(T-{start_sec})*{255/0.2},"
                f"if(lt(T,{end_sec - 0.2}),255,"
                f"if(lt(T,{end_sec}),({end_sec}-T)*{255/0.2},0))))'"
            )
        else:
            # Standard crossfade
            alpha_expr = (
                f"'if(lt(T,{start_sec}),0,"
                f"if(lt(T,{fade_in_end}),(T-{start_sec})*{255/fade_duration},"
                f"if(lt(T,{fade_out_start}),255,"
                f"if(lt(T,{end_sec}),({end_sec}-T)*{255/fade_duration},0))))'"
            )

        filters.append(
            f"[img{idx}]"
            f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a={alpha_expr}"
            f"[alpha{idx}]"
        )

    # Build overlay chain
    current = "[base]"
    for idx in range(len(IMAGE_TIMINGS)):
        if idx == len(IMAGE_TIMINGS) - 1:
            filters.append(f"{current}[alpha{idx}]overlay=0:0[video]")
        else:
            filters.append(f"{current}[alpha{idx}]overlay=0:0[v{idx}]")
            current = f"[v{idx}]"

    filter_complex = "; ".join(filters)

    # Complete command with optimizations
    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[video]',
        '-map', f'{len(IMAGE_TIMINGS) + 1}:a',  # Audio from last input
        '-c:v', 'libx264',
        '-preset', 'medium',  # Balanced speed/quality
        '-crf', '18',  # High quality
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-t', str(DURATION),
        '-movflags', '+faststart',  # Optimize for streaming
        final_output
    ])

    print(f"Compositing video with {len(IMAGE_TIMINGS)} images...")
    print(f"⚠️  Critical sync: Gamma burst at 18:45 (1125s)")
    print(f"Output: {final_output}")
    print(f"\nEncoding (this will take 15-25 minutes)...")
    print(f"Using preset: medium (balanced speed/quality)\n")

    # Run with progress output
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
            if 'time=' in line or 'frame=' in line or 'speed=' in line:
                # Parse and show clean progress
                if 'time=' in line:
                    import re
                    time_match = re.search(r'time=(\d+):(\d+):(\d+)', line)
                    if time_match:
                        h, m, s = map(int, time_match.groups())
                        elapsed = h * 3600 + m * 60 + s
                        progress = (elapsed / DURATION) * 100
                        print(f"\rProgress: {progress:.1f}% ({elapsed}/{DURATION}s)", end='', flush=True)

        process.wait()
        print()  # New line after progress

        if process.returncode != 0:
            print(f"\n✗ FFmpeg error")
            return False

        file_size = os.path.getsize(final_output) / (1024 * 1024)
        duration_min = DURATION / 60

        print(f"\n" + "=" * 70)
        print("✓ FINAL VIDEO COMPLETE!")
        print("=" * 70)
        print(f"\nOutput: {final_output}")
        print(f"Duration: {duration_min:.0f} minutes ({DURATION} seconds)")
        print(f"Size: {file_size:.1f} MB")
        print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} fps")
        print(f"\n⚠️  NEXT: Verify gamma burst sync at 18:45 (1125 seconds)")

        return True

    except Exception as e:
        print(f"\n✗ Error during composition: {e}")
        return False

def main():
    print("=" * 70)
    print("NEURAL NETWORK NAVIGATOR - Optimized Video Composition")
    print("=" * 70)
    print(f"\nCreating 28-minute meditation video")
    print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} fps\n")

    # Verify all files exist
    if not verify_prerequisites():
        print("\n✗ Cannot proceed - missing required files")
        return 1

    # Create video in single optimized pass
    if not create_video_with_single_pass():
        print("\n✗ Video composition failed")
        return 1

    print(f"\n✓ Production complete!")
    print(f"\nNext: Quality check - play video and verify:")
    print(f"  1. Voice clarity throughout")
    print(f"  2. Gamma burst sync at 18:45")
    print(f"  3. All transitions smooth")
    print(f"  4. Audio levels balanced")

    return 0

if __name__ == '__main__':
    exit(main())
