#!/usr/bin/env python3
"""
Video Compositor for Neural Network Navigator V2
Uses enhanced audio V2 with complete pretalk and closing
Adjusted timing for 28.7 minute duration
"""

import subprocess
import os
import sys

# Video specifications
WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 1722  # 28.7 minutes (updated for V2 audio)

# Image timings adjusted for V2 (scaled proportionally)
# V1: 1680s -> V2: 1722s (factor: 1.025)
IMAGE_TIMINGS = [
    # (image_file, start_time, end_time, fade_duration)
    ("scene_01_opening_FINAL.png", 0, 180, 5.0),  # Extended pretalk
    ("scene_02_descent_FINAL.png", 178, 430, 2.0),
    ("scene_03_neural_garden_FINAL.png", 428, 708, 2.0),
    ("scene_04_pathfinder_FINAL.png", 706, 984, 2.0),
    ("scene_05_weaver_FINAL.png", 982, 1156, 2.0),
    ("scene_06_gamma_burst_FINAL.png", 1125, 1128, 0.2),  # CRITICAL: Gamma flash (unchanged)
    ("scene_07_consolidation_FINAL.png", 1154, 1476, 2.0),
    ("scene_08_return_FINAL.png", 1474, 1722, 2.0),  # Extended closing
]

def verify_prerequisites():
    """Check that all required files exist before starting"""
    print("\n" + "=" * 70)
    print("PRE-FLIGHT CHECK - V2")
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

    # Check audio V2
    print("\nChecking audio (V2)...")
    audio_path = "working_files/neural_navigator_complete_enhanced_v2.wav"
    if not os.path.exists(audio_path):
        missing.append(audio_path)
        print(f"  ✗ {audio_path}")
        print(f"  Run: ./create_enhanced_audio_v2.sh")
    else:
        size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"  ✓ neural_navigator_complete_enhanced_v2.wav ({size_mb:.1f} MB)")

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
    Uses V2 enhanced audio with complete pretalk and closing
    """
    print("=" * 70)
    print("SINGLE-PASS VIDEO COMPOSITION - V2")
    print("=" * 70 + "\n")

    images_dir = "images"
    audio_path = "working_files/neural_navigator_complete_enhanced_v2.wav"
    final_output = "final_export/neural_network_navigator_v2.mp4"

    os.makedirs("final_export", exist_ok=True)

    # Build FFmpeg command - start with base gradient as color source
    cmd = ['ffmpeg', '-y']

    # Use base gradient as video stream foundation
    cmd.extend(['-loop', '1', '-i', 'gradients/gradient_01_opening.png'])

    # Add all 8 images
    for img_file, _, _, _ in IMAGE_TIMINGS:
        cmd.extend(['-loop', '1', '-i', f'{images_dir}/{img_file}'])

    # Add audio V2
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
    print(f"\nV2 Features:")
    print(f"  • Complete pretalk with benefits explanation")
    print(f"  • Extended journey content")
    print(f"  • 5 post-hypnotic anchors")
    print(f"  • Proper awakening sequence")
    print(f"  • Duration: {DURATION/60:.1f} minutes")
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
        print("✓ FINAL VIDEO V2 COMPLETE!")
        print("=" * 70)
        print(f"\nOutput: {final_output}")
        print(f"Duration: {duration_min:.1f} minutes ({DURATION} seconds)")
        print(f"Size: {file_size:.1f} MB")
        print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} fps")
        print(f"\n✨ V2 Enhancements:")
        print(f"  • Detailed pretalk explaining journey benefits")
        print(f"  • Safety and control statements")
        print(f"  • Extended pauses on transitions")
        print(f"  • Proper 1-10 awakening countdown")
        print(f"  • 5 post-hypnotic anchors for daily practice")
        print(f"  • Sleep/dream integration suggestions")
        print(f"\n⚠️  NEXT: Verify gamma burst sync at 18:45 (1125 seconds)")

        return True

    except Exception as e:
        print(f"\n✗ Error during composition: {e}")
        return False

def main():
    print("=" * 70)
    print("NEURAL NETWORK NAVIGATOR V2 - Video Composition")
    print("Complete Professional Format with Pretalk & Closing")
    print("=" * 70)
    print(f"\nCreating 28.7-minute meditation video")
    print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} fps\n")

    # Verify all files exist
    if not verify_prerequisites():
        print("\n✗ Cannot proceed - missing required files")
        print("\nTo generate enhanced audio V2:")
        print("  ./create_enhanced_audio_v2.sh")
        return 1

    # Create video in single optimized pass
    if not create_video_with_single_pass():
        print("\n✗ Video composition failed")
        return 1

    print(f"\n✓ Production complete!")
    print(f"\nNext: Quality check - play video and verify:")
    print(f"  1. Pretalk clearly explains benefits (0:00-2:30)")
    print(f"  2. Voice clarity throughout")
    print(f"  3. Gamma burst sync at 18:45")
    print(f"  4. All transitions smooth")
    print(f"  5. Awakening countdown audible (24:30-26:00)")
    print(f"  6. Post-hypnotic anchors clear (26:00-29:00)")
    print(f"  7. Audio levels balanced")

    return 0

if __name__ == '__main__':
    exit(main())
