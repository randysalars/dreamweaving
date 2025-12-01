#!/usr/bin/env python3
"""
Composite multiple images onto video with proper timing and fade effects
FINAL VERSION: Uses geq filter for time-based alpha fading

Updated workflow:
- User supplies images (downloaded from prompt-based generators) into
  sessions/garden-of-eden/images/uploaded
- Expected filenames (per section): 01_pretalk.png, 02_induction.png,
  03_meadow.png, 04_serpent.png, 05_tree.png, 06_divine.png, 07_return.png
- Legacy filenames (eden_XX_*.png) still supported as fallback
"""

import subprocess
import sys
from pathlib import Path


def _find_first_existing(candidates):
    """Return first existing Path from a list of Paths, else None."""
    for path in candidates:
        if path.exists():
            return path
    return None

def composite_images(base_video, output_video, images_config):
    """
    Composite images onto base video with smooth fades.

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
    session_dir = Path(__file__).parent
    output_dir = session_dir / "output" / "video"
    base_video = output_dir / "background_gradient.mp4"
    output_video = output_dir / "composite_with_images.mp4"

    uploaded_dir = session_dir / "images" / "uploaded"
    uploaded_dir.mkdir(parents=True, exist_ok=True)

    # Section timing map (seconds) with preferred filenames
    sections = [
        ("pretalk", 0, 150, ["01_pretalk.png", "eden_01_pretalk.png"]),
        ("induction", 150, 480, ["02_induction.png", "eden_02_induction.png"]),
        ("meadow", 480, 810, ["03_meadow.png", "eden_03_meadow.png"]),
        ("serpent", 810, 1020, ["04_serpent.png", "eden_04_serpent.png"]),
        ("tree", 1020, 1200, ["05_tree.png", "eden_05_tree.png"]),
        ("divine", 1200, 1380, ["06_divine.png", "eden_06_divine.png"]),
        ("return", 1380, 1500, ["07_return.png", "eden_07_return.png"]),
    ]

    images = []
    missing = []

    for key, start, end, names in sections:
        candidates = []
        for name in names:
            candidates.append(uploaded_dir / name)      # preferred location
            candidates.append(session_dir / name)       # legacy root
        chosen = _find_first_existing(candidates)
        if chosen:
            images.append((str(chosen), start, end))
            print(f"✓ {key}: {chosen.name} ({start//60}:{start%60:02d}-{end//60}:{end%60:02d})")
        else:
            missing.append(key)

    if missing:
        print(f"\n⚠️ Missing images for sections: {', '.join(missing)}")
        print(f"   Add PNGs to {uploaded_dir} using names like 01_pretalk.png, 02_induction.png, etc.")

    if not images:
        print("❌ No images found; composite will be skipped")
        sys.exit(1)

    success = composite_images(str(base_video), str(output_video), images)
    sys.exit(0 if success else 1)
