#!/usr/bin/env python3
"""
Build final Garden of Eden video with proper image compositing.

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


def build_video_with_images(output_path: str, images: list, total_duration: float,
                            fade_duration: float = 3.0, fps: int = 24):
    """
    Build video with crossfading images using xfade filter.

    Args:
        output_path: Output video path
        images: List of (image_path, start_sec, end_sec) tuples
        total_duration: Total video duration in seconds
        fade_duration: Crossfade duration in seconds
        fps: Frames per second
    """
    if not images:
        print("No images to process")
        return False

    # Build FFmpeg inputs - each image becomes a video stream
    cmd = ['ffmpeg']

    # Add each image as input with duration
    for i, (img_path, start, end) in enumerate(images):
        duration = end - start
        cmd.extend([
            '-loop', '1',
            '-t', str(duration),
            '-i', img_path
        ])

    # Build filter complex using xfade for crossfades
    filters = []

    # First, scale all inputs to 1920x1080
    for i in range(len(images)):
        filters.append(
            f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v{i}]"
        )

    # Chain xfade filters between consecutive images
    if len(images) == 1:
        # Only one image, just output it
        filters.append(f"[v0]copy[outv]")
    else:
        # Calculate offsets and chain xfades
        current = "[v0]"
        offset = 0

        for i in range(1, len(images)):
            # Offset is when the transition starts (end of current - fade)
            prev_start, prev_end = images[i-1][1], images[i-1][2]
            curr_start, curr_end = images[i][1], images[i][2]

            # Duration of previous clip
            prev_duration = prev_end - prev_start
            offset = prev_duration - fade_duration

            out_label = "[outv]" if i == len(images) - 1 else f"[xf{i}]"

            # Use xfade transition
            filters.append(
                f"{current}[v{i}]xfade=transition=fade:duration={fade_duration}:"
                f"offset={offset}{out_label}"
            )

            current = out_label

            # Accumulate offset for next transition
            offset += (curr_end - curr_start) - fade_duration

    filter_complex = "; ".join(filters)

    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-t', str(total_duration),
        '-y',
        output_path
    ])

    print(f"Building video with {len(images)} images...")
    print(f"Total duration: {total_duration/60:.1f} minutes")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Video with images created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False


def build_slideshow_concat(output_path: str, images: list, total_duration: float,
                           fade_duration: float = 3.0, fps: int = 24):
    """
    Alternative approach: build slideshow using concat with fade filters.
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

    # Find audio file (check multiple possible locations)
    audio_candidates = [
        output_dir / "ultimate" / "garden_of_eden_ULTIMATE.mp3",
        output_dir / "garden_of_eden_ULTIMATE.mp3",
        session_dir / "final_export" / "garden_of_eden_ULTIMATE.mp3",
    ]
    audio_path = None
    for candidate in audio_candidates:
        if candidate.exists():
            audio_path = candidate
            break

    if not audio_path:
        print(f"Audio not found in any of:")
        for c in audio_candidates:
            print(f"  - {c}")
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

        # Find matching image (check multiple locations)
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

    # Build video with crossfading images
    temp_video = str(video_dir / "slideshow_temp.mp4")

    if not build_slideshow_concat(temp_video, images, total_duration, fade_duration=3.0):
        print("Failed to build slideshow")
        sys.exit(1)

    # Mux with audio
    final_video = str(video_dir / "garden_of_eden_FINAL.mp4")

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
