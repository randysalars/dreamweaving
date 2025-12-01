#!/usr/bin/env python3
"""
ATLAS STARSHIP ANCIENT FUTURE - Video Assembly

Creates a video from section images with smooth crossfade transitions,
synchronized to the final mixed audio.

Images map to manifest sections:
- 01_pretalk.png → pretalk (0-150s)
- 02_induction.png → induction (150-540s)
- 03_journey_outer.png → boarding (540-900s)
- 04_corridor_glyphs.png → helm (900-1200s)
- 05_helm_attunement.png → download (1200-1500s)
- 06_gift_download.png → integration (1500-1597s)
- 07_return.png → (not used - audio ends at 1597s)
"""

import subprocess
import os

# Paths
SESSION_DIR = "/home/rsalars/Projects/dreamweaving/sessions/atlas-starship-ancient-future"
IMAGES_DIR = f"{SESSION_DIR}/images/uploaded"
AUDIO_PATH = f"{SESSION_DIR}/output/atlas_starship_final.mp3"
OUTPUT_PATH = f"{SESSION_DIR}/output/atlas_starship_final.mp4"

# Audio duration
AUDIO_DURATION = 1597.0

# Section timings (adjusted for actual audio duration)
# Format: (image_file, start_time, end_time)
SECTIONS = [
    ("01_pretalk.png", 0, 150),
    ("02_induction.png", 150, 540),
    ("03_journey_outer.png", 540, 900),
    ("04_corridor_glyphs.png", 900, 1200),
    ("05_helm_attunement.png", 1200, 1500),
    ("06_gift_download.png", 1500, AUDIO_DURATION),  # Covers integration + remaining
]

# Crossfade duration in seconds
CROSSFADE_DURATION = 3.0

def get_image_dimensions(image_path):
    """Get image dimensions using ffprobe"""
    result = subprocess.run([
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        image_path
    ], capture_output=True, text=True)
    w, h = result.stdout.strip().split(',')
    return int(w), int(h)

def create_video():
    print("=" * 70)
    print("ATLAS STARSHIP ANCIENT FUTURE - Video Assembly")
    print("=" * 70)

    # Check all images exist
    print("\n📸 Checking images...")
    for img, start, end in SECTIONS:
        path = f"{IMAGES_DIR}/{img}"
        if os.path.exists(path):
            w, h = get_image_dimensions(path)
            duration = end - start
            print(f"  ✓ {img}: {w}x{h}, {start:.0f}s-{end:.0f}s ({duration:.0f}s)")
        else:
            print(f"  ✗ Missing: {img}")
            return

    # Build FFmpeg complex filter for crossfades
    print("\n🎬 Building video with crossfades...")

    # Input files
    inputs = []
    for img, start, end in SECTIONS:
        inputs.extend(['-loop', '1', '-t', str(end - start + CROSSFADE_DURATION),
                      '-i', f"{IMAGES_DIR}/{img}"])

    # Add audio input
    inputs.extend(['-i', AUDIO_PATH])

    # Build complex filter
    n = len(SECTIONS)
    filter_parts = []

    # Scale all images to 1920x1080 and set frame rate
    for i in range(n):
        filter_parts.append(
            f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1,fps=30[v{i}]"
        )

    # Build xfade chain
    if n == 1:
        filter_parts.append(f"[v0]trim=0:{AUDIO_DURATION}[outv]")
    else:
        # First crossfade
        offset = SECTIONS[0][2] - CROSSFADE_DURATION  # end of first section minus crossfade
        filter_parts.append(
            f"[v0][v1]xfade=transition=fade:duration={CROSSFADE_DURATION}:offset={offset}[xf1]"
        )

        # Subsequent crossfades
        for i in range(2, n):
            prev_end = SECTIONS[i-1][2]
            offset = prev_end - CROSSFADE_DURATION - (CROSSFADE_DURATION * (i-1))  # Account for consumed time
            # Recalculate offset based on accumulated duration
            accumulated = sum(SECTIONS[j][2] - SECTIONS[j][1] for j in range(i)) - CROSSFADE_DURATION * (i-1)
            offset = accumulated - CROSSFADE_DURATION
            filter_parts.append(
                f"[xf{i-1}][v{i}]xfade=transition=fade:duration={CROSSFADE_DURATION}:offset={offset}[xf{i}]"
            )

        # Trim to exact audio duration
        filter_parts.append(f"[xf{n-1}]trim=0:{AUDIO_DURATION},setpts=PTS-STARTPTS[outv]")

    filter_complex = ";".join(filter_parts)

    # FFmpeg command
    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', f'{n}:a',  # Audio is the last input
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-shortest',
        OUTPUT_PATH
    ]

    print(f"\n  Running FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  ✗ FFmpeg error:")
        print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        return False

    # Verify output
    if os.path.exists(OUTPUT_PATH):
        size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
        # Get duration
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            OUTPUT_PATH
        ], capture_output=True, text=True)
        duration = float(result.stdout.strip())

        print(f"\n✅ Video created successfully!")
        print(f"   📁 {OUTPUT_PATH}")
        print(f"   📊 Size: {size_mb:.1f} MB")
        print(f"   ⏱️  Duration: {duration/60:.1f} minutes")
        return True
    else:
        print("  ✗ Output file not created")
        return False

def create_video_simple():
    """Simpler approach: create video segments then concatenate"""
    print("=" * 70)
    print("ATLAS STARSHIP ANCIENT FUTURE - Video Assembly (Simple Method)")
    print("=" * 70)

    # Create individual segments with crossfade-ready durations
    # Add extra time to each segment to account for crossfade consumption
    print("\n📸 Creating video segments...")

    segment_files = []
    temp_dir = f"{SESSION_DIR}/working_files/video_temp"
    os.makedirs(temp_dir, exist_ok=True)

    n_sections = len(SECTIONS)
    for i, (img, start, end) in enumerate(SECTIONS):
        duration = end - start
        # Add crossfade buffer to all segments except the last
        if i < n_sections - 1:
            duration += CROSSFADE_DURATION
        segment_path = f"{temp_dir}/segment_{i:02d}.mp4"
        segment_files.append(segment_path)

        print(f"  Creating segment {i+1}: {img} ({duration:.0f}s)...")

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', f"{IMAGES_DIR}/{img}",
            '-t', str(duration),
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=24',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-an',
            segment_path
        ]
        subprocess.run(cmd, capture_output=True)

    # Create concat file with crossfades using xfade
    print("\n🎬 Applying crossfade transitions...")

    # Build xfade chain for all segments
    inputs = []
    for seg in segment_files:
        inputs.extend(['-i', seg])

    n = len(segment_files)
    filter_parts = []

    # First xfade
    current_offset = SECTIONS[0][2] - SECTIONS[0][1] - CROSSFADE_DURATION
    filter_parts.append(
        f"[0:v][1:v]xfade=transition=fade:duration={CROSSFADE_DURATION}:offset={current_offset}[xf1]"
    )

    # Track accumulated duration
    accumulated_duration = (SECTIONS[0][2] - SECTIONS[0][1]) + (SECTIONS[1][2] - SECTIONS[1][1]) - CROSSFADE_DURATION

    # Subsequent xfades
    for i in range(2, n):
        segment_duration = SECTIONS[i][2] - SECTIONS[i][1]
        current_offset = accumulated_duration - CROSSFADE_DURATION
        filter_parts.append(
            f"[xf{i-1}][{i}:v]xfade=transition=fade:duration={CROSSFADE_DURATION}:offset={current_offset}[xf{i}]"
        )
        accumulated_duration += segment_duration - CROSSFADE_DURATION

    filter_complex = ";".join(filter_parts)

    video_only = f"{temp_dir}/video_crossfaded.mp4"

    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', f'[xf{n-1}]',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        video_only
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Crossfade error: {result.stderr[-1000:]}")
        # Fallback: simple concat without crossfade
        print("  Falling back to simple concatenation...")
        return create_video_concat_simple(segment_files, temp_dir)

    # Add audio
    print("\n🔊 Adding audio track...")
    cmd = [
        'ffmpeg', '-y',
        '-i', video_only,
        '-i', AUDIO_PATH,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-shortest',
        OUTPUT_PATH
    ]

    subprocess.run(cmd, capture_output=True)

    # Cleanup
    print("\n🧹 Cleaning up temporary files...")
    for f in segment_files:
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists(video_only):
        os.remove(video_only)
    os.rmdir(temp_dir)

    # Verify
    if os.path.exists(OUTPUT_PATH):
        size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            OUTPUT_PATH
        ], capture_output=True, text=True)
        duration = float(result.stdout.strip())

        print(f"\n✅ Video created successfully!")
        print(f"   📁 {OUTPUT_PATH}")
        print(f"   📊 Size: {size_mb:.1f} MB")
        print(f"   ⏱️  Duration: {duration/60:.1f} minutes")
        return True

    return False

def create_video_concat_simple(segment_files, temp_dir):
    """Fallback: simple concat without crossfade"""
    print("  Using simple concatenation...")

    # Create concat list
    concat_list = f"{temp_dir}/concat.txt"
    with open(concat_list, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")

    video_only = f"{temp_dir}/video_concat.mp4"
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_list,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        video_only
    ]
    subprocess.run(cmd, capture_output=True)

    # Add audio
    cmd = [
        'ffmpeg', '-y',
        '-i', video_only,
        '-i', AUDIO_PATH,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-shortest',
        OUTPUT_PATH
    ]
    subprocess.run(cmd, capture_output=True)

    # Cleanup
    for f in segment_files:
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists(video_only):
        os.remove(video_only)
    if os.path.exists(concat_list):
        os.remove(concat_list)
    os.rmdir(temp_dir)

    if os.path.exists(OUTPUT_PATH):
        size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
        print(f"\n✅ Video created (simple concat)!")
        print(f"   📁 {OUTPUT_PATH}")
        print(f"   📊 Size: {size_mb:.1f} MB")
        return True
    return False

if __name__ == "__main__":
    create_video_simple()
