#!/usr/bin/env python3
"""
Compile video frames into MP4 using FFmpeg
"""

import subprocess
import sys
from pathlib import Path

def compile_video(frames_dir="video_frames", output="background_gradient.mp4", fps=30):
    """Use FFmpeg to compile frames into video"""

    frames_path = Path(frames_dir)
    if not frames_path.exists():
        print(f"❌ Error: Frames directory not found: {frames_dir}")
        sys.exit(1)

    frame_pattern = str(frames_path / "frame_%06d.png")

    print(f"🎬 Compiling video from frames...")
    print(f"   Input: {frame_pattern}")
    print(f"   Output: {output}")

    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', frame_pattern,
        '-c:v', 'libx264',
        '-preset', 'slow',      # Better compression
        '-crf', '18',            # High quality (18-23 is good range)
        '-pix_fmt', 'yuv420p',   # Compatibility
        '-y',                    # Overwrite
        output
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Video compiled successfully!")
        print(f"   Output: {output}")

        # Get file size
        output_path = Path(output)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"   Size: {size_mb:.1f} MB")

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error:")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    frames_dir = sys.argv[1] if len(sys.argv) > 1 else "video_frames"
    output = sys.argv[2] if len(sys.argv) > 2 else "background_gradient.mp4"
    compile_video(frames_dir, output)
