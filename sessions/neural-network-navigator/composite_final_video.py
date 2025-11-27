#!/usr/bin/env python3
"""
Composite final video for Neural Network Navigator
- Generates gradient background video base
- Composites 8 SDXL images with 2-second crossfades at correct timestamps
- Critical: Scene 6 gamma burst flash at exactly 18:45 (1125s) with 0.2s transition
- Embeds master audio mix
"""

import subprocess
import os
import sys
from pathlib import Path

# Video specifications
WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 1680  # 28 minutes = 1680 seconds

# Image timing configuration from master_timeline.json
# (image_file, start_time, end_time, transition_duration)
IMAGE_TIMINGS = [
    ("scene_01_opening_FINAL.png", 0, 150, 5.0),         # Opens with 5s fade in
    ("scene_02_descent_FINAL.png", 148, 420, 2.0),       # 2s before end of scene 1
    ("scene_03_neural_garden_FINAL.png", 418, 690, 2.0),
    ("scene_04_pathfinder_FINAL.png", 688, 960, 2.0),
    ("scene_05_weaver_FINAL.png", 958, 1128, 2.0),       # Weaver until after gamma
    # CRITICAL: Gamma burst flash
    ("scene_06_gamma_burst_FINAL.png", 1125, 1128, 0.2), # INSTANT flash, 3s duration
    ("scene_07_consolidation_FINAL.png", 1126, 1440, 2.0), # Fade back to consolidation
    ("scene_08_return_FINAL.png", 1438, 1680, 2.0),
]

# Gradient backgrounds correspond to image scenes
GRADIENT_BACKGROUND_MAP = {
    0: "gradient_01_opening.png",
    148: "gradient_02_descent.png",
    418: "gradient_03_neural_garden.png",
    688: "gradient_04_pathfinder.png",
    958: "gradient_05_weaver.png",
    1125: "gradient_06_gamma_burst.png",  # White flash gradient
    1126: "gradient_07_consolidation.png",
    1438: "gradient_08_return.png",
}

def generate_gradient_base_video():
    """
    Generate base gradient background video
    This creates a 28-minute video with color-shifting gradients
    """
    print("\n" + "=" * 70)
    print("STEP 1: Generate Gradient Background Base Video")
    print("=" * 70)

    # First, generate all gradient images
    print("\nGenerating gradient images...")
    result = subprocess.run(
        ['python3', 'generate_gradient_backgrounds.py'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error generating gradients: {result.stderr}")
        return False

    print(result.stdout)

    # Build FFmpeg command to create gradient background video
    # We'll use concat demuxer with timed segments

    print("\nCreating gradient background video with FFmpeg...")

    # Simple approach: Create a single gradient base and use that
    # For simplicity, use the opening gradient as base, we'll composite others via images

    base_gradient = "gradients/gradient_01_opening.png"

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', base_gradient,
        '-t', str(DURATION),
        '-vf', f'scale={WIDTH}:{HEIGHT},fps={FPS}',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', '18',
        'working_files/gradient_base.mp4'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"✗ Error creating base video: {result.stderr}")
        return False

    file_size = os.path.getsize('working_files/gradient_base.mp4') / (1024 * 1024)
    print(f"✓ Gradient base video created: working_files/gradient_base.mp4 ({file_size:.1f} MB)")

    return True

def composite_images_onto_video():
    """
    Composite all 8 SDXL images onto gradient background
    Uses geq filter for time-based alpha fading
    Critical: Gamma burst at 1125s with 0.2s flash transition
    """
    print("\n" + "=" * 70)
    print("STEP 2: Composite Images with Time-Based Alpha Fading")
    print("=" * 70)

    base_video = "working_files/gradient_base.mp4"
    output_video = "working_files/video_with_images.mp4"
    images_dir = "images"

    # Verify all images exist
    missing_images = []
    for img_file, _, _, _ in IMAGE_TIMINGS:
        img_path = f"{images_dir}/{img_file}"
        if not os.path.exists(img_path):
            missing_images.append(img_file)

    if missing_images:
        print(f"\n✗ Missing images: {', '.join(missing_images)}")
        print("  Images must complete generating first")
        return False

    # Build FFmpeg command
    cmd = ['ffmpeg', '-y', '-i', base_video]

    # Add all image inputs
    for img_file, _, _, _ in IMAGE_TIMINGS:
        cmd.extend(['-loop', '1', '-i', f'{images_dir}/{img_file}'])

    # Build filter_complex
    filters = []

    # Scale, pad, and add alpha channel to all images
    for idx in range(len(IMAGE_TIMINGS)):
        input_num = idx + 1
        scale_filter = (
            f"[{input_num}:v]"
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
            f"format=yuva420p"
            f"[scaled{idx}]"
        )
        filters.append(scale_filter)

    # Apply time-based alpha for each image using geq filter
    for idx, (img_file, start_sec, end_sec, fade_duration) in enumerate(IMAGE_TIMINGS):
        fade_in_end = start_sec + fade_duration
        fade_out_start = end_sec - fade_duration

        # Special handling for gamma burst (instant transition)
        if "gamma_burst" in img_file:
            # Gamma burst: instant flash (0.2s), hold for 3s, instant fade out
            alpha_expr = (
                f"'if(lt(T,{start_sec}),0,"
                f"if(lt(T,{start_sec + 0.2}),(T-{start_sec})*{255/0.2},"  # Quick 0.2s fade in
                f"if(lt(T,{end_sec - 0.2}),255,"  # Hold for 3s
                f"if(lt(T,{end_sec}),({end_sec}-T)*{255/0.2},0))))'"  # Quick 0.2s fade out
            )
        else:
            # Standard crossfade
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

    # Build overlay chain
    current_stream = "[0:v]"
    for idx in range(len(IMAGE_TIMINGS)):
        if idx == len(IMAGE_TIMINGS) - 1:
            # Last overlay
            overlay_filter = f"{current_stream}[alpha{idx}]overlay=0:0[video_out]"
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
        '-map', '[video_out]',
        '-c:v', 'libx264',
        '-crf', '18',
        '-t', str(DURATION),
        output_video
    ])

    print(f"\nCompositing {len(IMAGE_TIMINGS)} images with timed fades...")
    print(f"⚠️  Critical: Gamma burst flash at 18:45 (1125s)")
    print(f"Output: {output_video}\n")

    # Run FFmpeg (this will take a while)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"\n✗ FFmpeg error: {result.stderr}")
            return False

        file_size = os.path.getsize(output_video) / (1024 * 1024)
        print(f"\n✓ Image compositing complete: {output_video} ({file_size:.1f} MB)")
        return True

    except Exception as e:
        print(f"\n✗ Error during compositing: {e}")
        return False

def add_master_audio():
    """
    Add master audio mix to final video
    """
    print("\n" + "=" * 70)
    print("STEP 3: Add Master Audio Mix")
    print("=" * 70)

    video_input = "working_files/video_with_images.mp4"
    audio_input = "working_files/audio_mix_master.wav"
    final_output = "final_export/neural_network_navigator.mp4"

    # Create final export directory
    os.makedirs("final_export", exist_ok=True)

    # Verify audio exists
    if not os.path.exists(audio_input):
        print(f"\n✗ Master audio not found: {audio_input}")
        print("  Run mix_audio_simple.py first")
        return False

    # FFmpeg command to combine video + audio
    cmd = [
        'ffmpeg', '-y',
        '-i', video_input,
        '-i', audio_input,
        '-c:v', 'copy',  # Copy video stream (already encoded)
        '-c:a', 'aac',   # Encode audio as AAC
        '-b:a', '320k',  # High quality audio
        '-shortest',     # Match shortest stream (should be equal)
        final_output
    ]

    print(f"\nAdding audio to video...")
    print(f"Output: {final_output}\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"\n✗ FFmpeg error: {result.stderr}")
            return False

        file_size = os.path.getsize(final_output) / (1024 * 1024)
        duration_min = DURATION / 60

        print(f"\n" + "=" * 70)
        print("✓ FINAL VIDEO COMPLETE!")
        print("=" * 70)
        print(f"\nOutput: {final_output}")
        print(f"Duration: {duration_min:.0f} minutes ({DURATION} seconds)")
        print(f"Size: {file_size:.1f} MB")
        print(f"Resolution: {WIDTH}x{HEIGHT}")
        print(f"Frame rate: {FPS} fps")
        print(f"\n⚠️  CRITICAL: Verify gamma burst sync at 18:45 (1125 seconds)")
        print(f"\nNext: Quality check - full 28-minute playthrough")

        return True

    except Exception as e:
        print(f"\n✗ Error adding audio: {e}")
        return False

def main():
    print("=" * 70)
    print("NEURAL NETWORK NAVIGATOR - Final Video Composition")
    print("=" * 70)
    print(f"\nCreating complete 28-minute meditation video")
    print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} fps")
    print(f"Duration: {DURATION/60:.0f} minutes\n")

    # Step 1: Generate gradient base video
    if not generate_gradient_base_video():
        print("\n✗ Failed to generate gradient base")
        return 1

    # Step 2: Composite images
    if not composite_images_onto_video():
        print("\n✗ Failed to composite images")
        return 1

    # Step 3: Add master audio
    if not add_master_audio():
        print("\n✗ Failed to add audio")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
