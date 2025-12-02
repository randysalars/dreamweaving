#!/usr/bin/env python3
"""
Build final Iron Soul Forge video with crossfading images.

Uses a 2-step approach:
1. Create video with crossfading images (evenly distributed across duration)
2. Mux with final audio
"""

import subprocess
import sys
from pathlib import Path

from pydub import AudioSegment


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds."""
    audio = AudioSegment.from_file(audio_path)
    return len(audio) / 1000.0


def build_slideshow_concat(output_path: str, images: list, total_duration: float,
                           fade_duration: float = 3.0, fps: int = 24):
    """
    Build slideshow using concat with fade filters.
    Each image is shown for its section duration with fade in/out.
    """
    if not images:
        print("No images")
        return False

    cmd = ['ffmpeg']

    # Add all images as inputs (each loops for its duration)
    for img_path, start, end in images:
        duration = end - start
        cmd.extend([
            '-loop', '1',
            '-framerate', str(fps),
            '-t', str(duration),
            '-i', img_path
        ])

    # Build filter chain: scale each, add fades, concat
    filters = []
    fade_inputs = []

    for i, (_, start, end) in enumerate(images):
        duration = end - start

        # Scale to 1920x1080
        scale_out = f"[s{i}]"
        filters.append(
            f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1{scale_out}"
        )

        # Add fade in at start and fade out at end
        fade_out = f"[f{i}]"
        fade_out_start = max(0, duration - fade_duration)
        filters.append(
            f"{scale_out}fade=t=in:st=0:d={fade_duration},"
            f"fade=t=out:st={fade_out_start}:d={fade_duration}{fade_out}"
        )

        fade_inputs.append(fade_out)

    # Concat all faded segments
    concat_inputs = "".join(fade_inputs)
    filters.append(f"{concat_inputs}concat=n={len(images)}:v=1:a=0[outv]")

    filter_complex = "; ".join(filters)

    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-y',
        output_path
    ])

    print(f"Building slideshow with {len(images)} images...")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Slideshow created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False


def mux_audio_video(video_path: str, audio_path: str, output_path: str):
    """Combine video and audio into final output."""
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        '-y',
        output_path
    ]

    print(f"Muxing audio and video...")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Final video created: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Mux error: {e.stderr}")
        return False


def add_title_overlay(input_path: str, output_path: str, title: str, subtitle: str):
    """Add title and subtitle overlays to video."""
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:"
            f"text='{title}':fontcolor=white@0.9:fontsize=64:"
            f"x=(w-text_w)/2:y=120:shadowcolor=black@0.6:shadowx=2:shadowy=2,"
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            f"text='{subtitle}':fontcolor=white@0.8:fontsize=36:"
            f"x=(w-text_w)/2:y=200:shadowcolor=black@0.6:shadowx=2:shadowy=2"
        ),
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', '18',
        '-c:a', 'copy',
        '-y',
        output_path
    ]

    print("Adding title overlays...")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Title overlay error: {e.stderr}")
        return False


def main():
    session_dir = Path(__file__).parent
    output_dir = session_dir / "output"
    video_dir = output_dir / "video"
    video_dir.mkdir(parents=True, exist_ok=True)

    # Find audio file
    audio_path = output_dir / "iron-soul-forge-mixed.mp3"
    if not audio_path.exists():
        print(f"Audio not found: {audio_path}")
        sys.exit(1)

    total_duration = get_audio_duration(str(audio_path))
    print(f"Audio duration: {total_duration/60:.1f} minutes")

    # Collect images from uploaded directory
    uploaded_dir = session_dir / "images" / "uploaded"
    image_files = sorted(uploaded_dir.glob("*.png"))

    if not image_files:
        print("No images found in images/uploaded/")
        sys.exit(1)

    print(f"Found {len(image_files)} images")

    # Distribute images evenly across duration
    slot_duration = total_duration / len(image_files)
    images = []
    for i, img in enumerate(image_files):
        start = i * slot_duration
        end = (i + 1) * slot_duration
        images.append((str(img), start, end))
        print(f"  Image {i+1}: {img.name} ({start/60:.1f}m - {end/60:.1f}m)")

    # Build video with crossfading images
    temp_video = str(video_dir / "slideshow_temp.mp4")

    if not build_slideshow_concat(temp_video, images, total_duration, fade_duration=3.0):
        print("Failed to build slideshow")
        sys.exit(1)

    # Mux with audio
    muxed_video = str(video_dir / "iron_soul_forge_muxed.mp4")

    if not mux_audio_video(temp_video, str(audio_path), muxed_video):
        print("Failed to mux audio")
        sys.exit(1)

    # Add title overlays
    final_video = str(video_dir / "iron_soul_forge_FINAL.mp4")

    if not add_title_overlay(muxed_video, final_video, "The Iron Soul Forge", "Forging Unbreakable Courage Within"):
        print("Failed to add title overlays")
        sys.exit(1)

    # Cleanup temp files
    Path(temp_video).unlink(missing_ok=True)
    Path(muxed_video).unlink(missing_ok=True)

    print(f"\n{'='*60}")
    print(f"SUCCESS: Final video created")
    print(f"  Output: {final_video}")
    print(f"  Duration: {total_duration/60:.1f} minutes")
    print(f"  Images: {len(images)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
