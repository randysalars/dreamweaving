#!/usr/bin/env python3
"""
Build final Temple of a Thousand Steps video with proper image compositing.

Uses a simpler 2-step approach:
1. Create video with crossfading images
2. Mux with final audio

Images from manifest.yaml sections are crossfaded at transition points.
"""

import subprocess
import sys
from pathlib import Path

import yaml
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
        subprocess.run(cmd, check=True)
        print("Slideshow created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error")
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
        subprocess.run(cmd, check=True)
        print(f"Final video created: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Mux error: {e}")
        return False


def main():
    session_dir = Path(__file__).parent
    output_dir = session_dir / "output"
    video_dir = output_dir / "video"
    video_dir.mkdir(parents=True, exist_ok=True)

    # Load manifest for section timing
    manifest_path = session_dir / "manifest.yaml"
    if not manifest_path.exists():
        print("No manifest.yaml found")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    # Find audio file
    audio_path = output_dir / "final_mix.mp3"
    if not audio_path.exists():
        print(f"Audio not found: {audio_path}")
        sys.exit(1)

    total_duration = get_audio_duration(str(audio_path))
    print(f"Audio duration: {total_duration/60:.1f} minutes")

    # Build image list from manifest sections
    images = []
    uploaded_dir = session_dir / "images" / "uploaded"

    sections = manifest.get('sections', [])
    for section in sections:
        start = section['start']
        end = section['end']

        # Find matching image
        img_name = section.get('image')
        if img_name:
            img_path = uploaded_dir / img_name
            if img_path.exists():
                images.append((str(img_path), start, end))
                print(f"  Section '{section['name']}': {img_name} ({start//60}:{start%60:02d} - {end//60}:{end%60:02d})")
            else:
                print(f"  Warning: Image not found: {img_path}")

    if not images:
        print("No images found in manifest sections")
        sys.exit(1)

    print(f"\nFound {len(images)} images")

    # Adjust timing if needed - extend last image to match audio duration
    if images:
        last_img, last_start, last_end = images[-1]
        if last_end < total_duration:
            print(f"  Extending last image from {last_end}s to {total_duration:.1f}s")
            images[-1] = (last_img, last_start, total_duration)

    # Build video with crossfading images
    temp_video = str(video_dir / "slideshow_temp.mp4")

    if not build_slideshow_concat(temp_video, images, total_duration, fade_duration=3.0):
        print("Failed to build slideshow")
        sys.exit(1)

    # Mux with audio
    final_video = str(video_dir / "temple_of_a_thousand_steps_FINAL.mp4")

    if not mux_audio_video(temp_video, str(audio_path), final_video):
        print("Failed to mux audio")
        sys.exit(1)

    # Cleanup temp file
    Path(temp_video).unlink(missing_ok=True)

    print(f"\n{'='*60}")
    print(f"SUCCESS: Final video created")
    print(f"  Output: {final_video}")
    print(f"  Duration: {total_duration/60:.1f} minutes")
    print(f"  Images: {len(images)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
