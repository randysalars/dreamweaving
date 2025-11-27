#!/usr/bin/env python3
"""
Composite multiple images onto video with proper timing and fade effects
VERSION 2: Fixed overlay logic
"""

import subprocess
import sys
from pathlib import Path

def composite_images(base_video, output_video, images_config):
    """
    Composite images onto base video

    images_config: list of (image_path, start_time, end_time) tuples
    """

    if not images_config:
        print("No images to composite")
        return False

    # Build FFmpeg command
    cmd = ['ffmpeg', '-i', base_video]

    # Add all image inputs
    for img_path, _, _ in images_config:
        cmd.extend(['-loop', '1', '-i', img_path])

    # Build filter_complex
    filters = []

    # Scale and pad all images first
    for idx in range(len(images_config)):
        input_num = idx + 1
        scale_filter = (
            f"[{input_num}:v]"
            f"scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
            f"format=yuva420p"  # Need alpha channel for fading
            f"[scaled{idx}]"
        )
        filters.append(scale_filter)

    # Now create overlays with time-based enable and opacity fading
    current_stream = "[0:v]"
    for idx, (img_path, start_sec, end_sec) in enumerate(images_config):
        duration = end_sec - start_sec
        fade_duration = 2.0  # 2 second fades

        # Create expression for smooth fade in/out within the time window
        # Fade in: alpha goes from 0 to 1 over first 2 seconds
        # Fade out: alpha goes from 1 to 0 over last 2 seconds
        # Full: alpha = 1 in the middle

        fade_in_end = start_sec + fade_duration
        fade_out_start = end_sec - fade_duration

        # Build the alpha expression:
        # - Before start_sec: alpha = 0
        # - start_sec to fade_in_end: linear fade from 0 to 1
        # - fade_in_end to fade_out_start: alpha = 1
        # - fade_out_start to end_sec: linear fade from 1 to 0
        # - After end_sec: alpha = 0

        alpha_expr = (
            f"if(lt(t,{start_sec}),0,"
            f"if(lt(t,{fade_in_end}),(t-{start_sec})/{fade_duration},"
            f"if(lt(t,{fade_out_start}),1,"
            f"if(lt(t,{end_sec}),({end_sec}-t)/{fade_duration},0))))"
        )

        # Apply alpha using colorchannelmixer
        alpha_filter = (
            f"[scaled{idx}]"
            f"colorchannelmixer=aa={alpha_expr}"
            f"[alpha{idx}]"
        )
        filters.append(alpha_filter)

        # Overlay this image
        if idx == len(images_config) - 1:
            # Last overlay outputs to [out]
            overlay_filter = f"{current_stream}[alpha{idx}]overlay=0:0[out]"
        else:
            # Intermediate overlays
            overlay_filter = f"{current_stream}[alpha{idx}]overlay=0:0[tmp{idx}]"
            current_stream = f"[tmp{idx}]"

        filters.append(overlay_filter)

    # Join all filters
    filter_complex = "; ".join(filters)

    # Complete command
    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[out]',
        '-c:v', 'libx264',
        '-crf', '18',
        '-t', '1500',  # 25 minutes
        '-y',
        output_video
    ])

    print(f"Compositing {len(images_config)} images...")
    print(f"Output: {output_video}")

    # DEBUG: Print the command
    print("\n" + "="*80)
    print("FILTER COMPLEX (first 500 chars):")
    print("="*80)
    print(filter_complex[:500])
    print("...")
    print("="*80 + "\n")

    # Run FFmpeg
    try:
        subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("✅ Compositing complete")
        return True
    except subprocess.CalledProcessError:
        print("❌ FFmpeg error during compositing")
        return False


if __name__ == "__main__":
    # Define image configuration
    session_dir = Path(__file__).parent
    output_dir = session_dir / "output" / "video"

    base_video = output_dir / "background_gradient.mp4"
    output_video = output_dir / "composite_with_images.mp4"

    # Image timings (path, start_sec, end_sec)
    images = []

    if (session_dir / "eden_01_pretalk.png").exists():
        images.append((str(session_dir / "eden_01_pretalk.png"), 0, 150))
        print("✓ Found: eden_01_pretalk.png (0:00-2:30)")

    if (session_dir / "eden_02_induction.png").exists():
        images.append((str(session_dir / "eden_02_induction.png"), 150, 480))
        print("✓ Found: eden_02_induction.png (2:30-8:00)")

    if (session_dir / "eden_03_meadow.png").exists():
        images.append((str(session_dir / "eden_03_meadow.png"), 480, 810))
        print("✓ Found: eden_03_meadow.png (8:00-13:30)")

    if (session_dir / "eden_04_serpent.png").exists():
        images.append((str(session_dir / "eden_04_serpent.png"), 810, 1020))
        print("✓ Found: eden_04_serpent.png (13:30-17:00)")

    if (session_dir / "eden_05_tree.png").exists():
        images.append((str(session_dir / "eden_05_tree.png"), 1020, 1200))
        print("✓ Found: eden_05_tree.png (17:00-20:00)")

    if (session_dir / "eden_06_divine.png").exists():
        images.append((str(session_dir / "eden_06_divine.png"), 1200, 1380))
        print("✓ Found: eden_06_divine.png (20:00-23:00)")

    if (session_dir / "eden_07_return.png").exists():
        images.append((str(session_dir / "eden_07_return.png"), 1380, 1500))
        print("✓ Found: eden_07_return.png (23:00-25:00)")

    if not images:
        print("❌ No images found")
        sys.exit(1)

    print(f"\nCompositing {len(images)} images into video...")

    success = composite_images(str(base_video), str(output_video), images)

    sys.exit(0 if success else 1)
