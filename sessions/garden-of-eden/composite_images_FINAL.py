#!/usr/bin/env python3
"""
Composite multiple images onto video with proper timing and fade effects
FINAL VERSION: Uses geq filter for time-based alpha fading
"""

import subprocess
import sys
from pathlib import Path

def composite_images(base_video, output_video, images_config):
    """
    Composite images onto base video with smooth fades

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

    # Scale, pad, and add alpha channel to all images
    for idx in range(len(images_config)):
        input_num = idx + 1
        scale_filter = (
            f"[{input_num}:v]"
            f"scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
            f"format=yuva420p"  # Add alpha channel
            f"[scaled{idx}]"
        )
        filters.append(scale_filter)

    # Apply time-based alpha for each image using geq filter
    for idx, (img_path, start_sec, end_sec) in enumerate(images_config):
        fade_duration = 2.0  # 2 second fades
        fade_in_end = start_sec + fade_duration
        fade_out_start = end_sec - fade_duration

        # Build alpha expression for geq filter
        # T is the video timeline in seconds
        # Alpha goes from 0-255 (not 0-1 in geq)

        # Before start: alpha = 0
        # During fade in (start to fade_in_end): linear 0-255
        # Full opacity (fade_in_end to fade_out_start): alpha = 255
        # During fade out (fade_out_start to end): linear 255-0
        # After end: alpha = 0

        alpha_expr = (
            f"'if(lt(T,{start_sec}),0,"
            f"if(lt(T,{fade_in_end}),(T-{start_sec})*{255/fade_duration},"
            f"if(lt(T,{fade_out_start}),255,"
            f"if(lt(T,{end_sec}),({end_sec}-T)*{255/fade_duration},0))))'"
        )

        # Apply geq to modify only the alpha channel
        geq_filter = (
            f"[scaled{idx}]"
            f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a={alpha_expr}"
            f"[alpha{idx}]"
        )
        filters.append(geq_filter)

    # Build overlay chain (now all images have time-based alpha)
    current_stream = "[0:v]"
    for idx in range(len(images_config)):
        if idx == len(images_config) - 1:
            # Last overlay
            overlay_filter = f"{current_stream}[alpha{idx}]overlay=0:0[out]"
        else:
            # Intermediate overlay
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

    print(f"\nCompositing {len(images_config)} images with 2-second fades...")
    print(f"Output: {output_video}\n")

    # Run FFmpeg
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Compositing complete with all fades")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ FFmpeg error during compositing")
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
        print("✓ eden_01_pretalk.png (0:00-2:30)")

    if (session_dir / "eden_02_induction.png").exists():
        images.append((str(session_dir / "eden_02_induction.png"), 150, 480))
        print("✓ eden_02_induction.png (2:30-8:00)")

    if (session_dir / "eden_03_meadow.png").exists():
        images.append((str(session_dir / "eden_03_meadow.png"), 480, 810))
        print("✓ eden_03_meadow.png (8:00-13:30)")

    if (session_dir / "eden_04_serpent.png").exists():
        images.append((str(session_dir / "eden_04_serpent.png"), 810, 1020))
        print("✓ eden_04_serpent.png (13:30-17:00)")

    if (session_dir / "eden_05_tree.png").exists():
        images.append((str(session_dir / "eden_05_tree.png"), 1020, 1200))
        print("✓ eden_05_tree.png (17:00-20:00)")

    if (session_dir / "eden_06_divine.png").exists():
        images.append((str(session_dir / "eden_06_divine.png"), 1200, 1380))
        print("✓ eden_06_divine.png (20:00-23:00)")

    if (session_dir / "eden_07_return.png").exists():
        images.append((str(session_dir / "eden_07_return.png"), 1380, 1500))
        print("✓ eden_07_return.png (23:00-25:00)")

    if not images:
        print("❌ No images found")
        sys.exit(1)

    success = composite_images(str(base_video), str(output_video), images)

    sys.exit(0 if success else 1)
