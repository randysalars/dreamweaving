#!/usr/bin/env python3
"""
Composite multiple images onto video - SIMPLE VERSION (no fades, just testing)
"""

import subprocess
import sys
from pathlib import Path

def composite_images(base_video, output_video, images_config):
    """
    Composite images onto base video - SIMPLE TEST

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

    # Scale and pad all images first (NO FADES)
    for idx in range(len(images_config)):
        input_num = idx + 1
        scale_filter = (
            f"[{input_num}:v]"
            f"scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
            f"[img{idx}]"
        )
        filters.append(scale_filter)

    # Build overlay chain with enable filters
    current_stream = "[0:v]"
    for idx, (img_path, start_sec, end_sec) in enumerate(images_config):
        if idx == len(images_config) - 1:
            # Last overlay
            overlay_filter = (
                f"{current_stream}[img{idx}]"
                f"overlay=0:0:enable='between(t,{start_sec},{end_sec})'"
                f"[out]"
            )
        else:
            # Intermediate overlay
            overlay_filter = (
                f"{current_stream}[img{idx}]"
                f"overlay=0:0:enable='between(t,{start_sec},{end_sec})'"
                f"[tmp{idx}]"
            )
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
        '-t', '1500',
        '-y',
        output_video
    ])

    print(f"\nCompositing {len(images_config)} images (NO FADES - testing)...")
    print(f"Output: {output_video}\n")

    # Run FFmpeg
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Compositing complete")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ FFmpeg error during compositing")
        return False


if __name__ == "__main__":
    # Define image configuration
    session_dir = Path(__file__).parent
    output_dir = session_dir / "output" / "video"

    base_video = output_dir / "background_gradient.mp4"
    output_video = output_dir / "composite_test_simple.mp4"

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
