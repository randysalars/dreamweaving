#!/usr/bin/env python3
"""
Create YouTube thumbnail for ATLAS session
Uses the Helm Attunement image with text overlays
"""

import subprocess
from pathlib import Path

def create_thumbnail():
    """Create YouTube thumbnail with text overlay"""

    # Use the most visually striking image - Helm Attunement
    base_image = Path("images/uploaded/05_helm_attunement.png")
    output_file = Path("output/youtube_thumbnail.png")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("Creating YouTube Thumbnail")
    print("="*70)
    print(f"Base image: {base_image}")
    print(f"Output: {output_file}")

    # Create thumbnail with ffmpeg using drawtext filter
    # YouTube thumbnail size: 1280x720
    cmd = [
        "ffmpeg", "-y",
        "-i", str(base_image),
        "-vf",
        (
            # Scale and crop to 16:9 aspect ratio (1280x720)
            "scale=1280:720:force_original_aspect_ratio=increase,"
            "crop=1280:720,"
            # Add main title at top
            "drawtext="
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            "text='ATLAS':"
            "fontcolor=white:"
            "fontsize=120:"
            "x=(w-text_w)/2:"
            "y=80:"
            "shadowcolor=black@0.8:"
            "shadowx=4:"
            "shadowy=4,"
            # Add subtitle
            "drawtext="
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            "text='The Starship of the Ancient Future':"
            "fontcolor=white@0.95:"
            "fontsize=48:"
            "x=(w-text_w)/2:"
            "y=220:"
            "shadowcolor=black@0.8:"
            "shadowx=3:"
            "shadowy=3,"
            # Add feature text at bottom
            "drawtext="
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            "text='432Hz Binaural Beats | 40Hz Gamma Flash | 31 Minutes':"
            "fontcolor=white@0.9:"
            "fontsize=32:"
            "x=(w-text_w)/2:"
            "y=620:"
            "shadowcolor=black@0.8:"
            "shadowx=2:"
            "shadowy=2"
        ),
        "-frames:v", "1",
        str(output_file)
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    # Get file size
    size_mb = output_file.stat().st_size / (1024 * 1024)

    print(f"\n✅ Thumbnail created: {output_file}")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Dimensions: 1280x720 (16:9)")
    print("="*70)

    return output_file

if __name__ == "__main__":
    create_thumbnail()
