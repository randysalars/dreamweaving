#!/usr/bin/env python3
"""
Create video with section-based timing for 7 images across the Atlas journey
Maps images to narrative sections from manifest
"""

import subprocess
from pathlib import Path

# Section timing from manifest (adjusted to actual 1887s duration)
sections = [
    {"name": "01_pretalk", "image": "01_pretalk.png", "start": 0, "end": 150},
    {"name": "02_induction", "image": "02_induction.png", "start": 150, "end": 540},
    {"name": "03_journey_outer", "image": "03_journey_outer.png", "start": 540, "end": 920},
    {"name": "04_corridor_glyphs", "image": "04_corridor_glyphs.png", "start": 920, "end": 1240},
    {"name": "05_helm_attunement", "image": "05_helm_attunement.png", "start": 1240, "end": 1520},
    {"name": "06_gift_download", "image": "06_gift_download.png", "start": 1520, "end": 1700},
    {"name": "07_return", "image": "07_return.png", "start": 1700, "end": 1887},
]

def create_section_video(section, audio_file, output_dir):
    """Create a video segment for one section"""
    image_path = Path(f"images/uploaded/{section['image']}")
    duration = section['end'] - section['start']
    output_path = output_dir / f"{section['name']}.mp4"

    print(f"\n{'='*70}")
    print(f"Section: {section['name']}")
    print(f"  Image: {section['image']}")
    print(f"  Time: {section['start']}s - {section['end']}s ({duration}s)")
    print(f"{'='*70}")

    # Extract audio segment
    audio_segment = output_dir / f"{section['name']}_audio.mp3"
    cmd_audio = [
        "ffmpeg", "-y",
        "-ss", str(section['start']),
        "-t", str(duration),
        "-i", str(audio_file),
        "-c", "copy",
        str(audio_segment)
    ]
    subprocess.run(cmd_audio, check=True, capture_output=True)

    # Create video with image and audio segment
    cmd_video = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(duration),
        "-i", str(image_path),
        "-i", str(audio_segment),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path)
    ]

    subprocess.run(cmd_video, check=True, capture_output=True)
    print(f"✅ Created: {output_path}")

    return output_path

def concatenate_videos(video_files, output_file):
    """Concatenate all section videos into final video"""
    concat_file = Path("output/video/concat_sections.txt")

    with open(concat_file, 'w') as f:
        for video in video_files:
            f.write(f"file '{video.name}'\n")

    print(f"\n{'='*70}")
    print("Concatenating all sections...")
    print(f"{'='*70}")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_file)
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    print(f"✅ Final video created: {output_file}")

def main():
    audio_file = Path("output/atlas_ava_COMPLETE_MASTERED.mp3")
    output_dir = Path("output/video")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("ATLAS: Creating Video with 7 Section Images")
    print("="*70)

    # Create individual section videos
    section_videos = []
    for section in sections:
        video_path = create_section_video(section, audio_file, output_dir)
        section_videos.append(video_path)

    # Concatenate all sections
    final_output = output_dir / "atlas_ava_final.mp4"
    concatenate_videos(section_videos, final_output)

    # Verify duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(final_output)],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip())

    print(f"\n{'='*70}")
    print("COMPLETE!")
    print(f"{'='*70}")
    print(f"Final video: {final_output}")
    print(f"Duration: {duration:.1f}s ({duration/60:.2f} min)")
    print(f"Expected: 1887.0s (31.45 min)")
    print(f"Sections: {len(sections)} images")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
