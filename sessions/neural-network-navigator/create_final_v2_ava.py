#!/usr/bin/env python3
"""
Create Final Neural Network Navigator V2 with Ava Voice
Combines professional mastered Ava voice + binaural beats + images
"""

import subprocess
import os
import sys

def mix_voice_and_binaural(voice_path, binaural_path, output_path, voice_level=-16, binaural_level=-28):
    """
    Mix mastered voice with binaural beats

    Args:
        voice_path: Path to mastered voice WAV
        binaural_path: Path to binaural beats WAV
        output_path: Path to output mixed WAV
        voice_level: Voice LUFS target (default -16, clear and primary)
        binaural_level: Binaural LUFS target (default -28, subtle background)
    """
    print("\n" + "="*70)
    print("MIXING VOICE + BINAURAL BEATS")
    print("="*70 + "\n")

    print(f"Voice: {voice_path}")
    print(f"Binaural: {binaural_path}")
    print(f"Output: {output_path}")
    print()

    # Calculate gain adjustments
    # Voice is already mastered to -14 LUFS, needs to go to -16 LUFS = -2 dB
    voice_gain = voice_level - (-14)

    # Binaural is unmastered, rough estimate at -20 LUFS, needs to go to -28 = -8 dB
    binaural_gain = binaural_level - (-20)

    print(f"Voice gain: {voice_gain:+.1f} dB (targeting {voice_level} LUFS)")
    print(f"Binaural gain: {binaural_gain:+.1f} dB (targeting {binaural_level} LUFS)")
    print()

    # FFmpeg command to mix both tracks
    cmd = [
        'ffmpeg',
        '-i', voice_path,
        '-i', binaural_path,
        '-filter_complex',
        f'[0:a]volume={voice_gain}dB[voice];'
        f'[1:a]volume={binaural_gain}dB[binaural];'
        f'[voice][binaural]amix=inputs=2:duration=first:normalize=0[mixed]',
        '-map', '[mixed]',
        '-c:a', 'pcm_s24le',
        '-ar', '48000',
        '-y',
        output_path
    ]

    print("Mixing audio tracks...")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)

        file_size = os.path.getsize(output_path) / (1024 * 1024)

        print("\n" + "="*70)
        print("✓ MIXING COMPLETE")
        print("="*70)
        print(f"\nMixed Audio: {output_path}")
        print(f"Size: {file_size:.1f} MB")
        print(f"Voice Level: {voice_level} LUFS")
        print(f"Binaural Level: {binaural_level} LUFS")
        print()

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Mixing failed: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("\n✗ Mixing timed out")
        return False

def create_video_from_images(audio_path, images_dir, output_path, duration_sec):
    """
    Create video with images and audio

    Args:
        audio_path: Path to final mixed audio
        images_dir: Directory containing scene images
        output_path: Path to output video
        duration_sec: Total duration in seconds
    """
    print("\n" + "="*70)
    print("CREATING FINAL VIDEO")
    print("="*70 + "\n")

    # Image timings for V2 (28.7 minutes = 1722 seconds)
    # Based on the V2 enhanced script sections
    scenes = [
        {'image': 'scene_01_opening_FINAL.png', 'start': 0, 'end': 150},          # Pretalk
        {'image': 'scene_02_descent_FINAL.png', 'start': 150, 'end': 300},        # Induction
        {'image': 'scene_03_neural_garden_FINAL.png', 'start': 300, 'end': 600},  # Neural Garden
        {'image': 'scene_04_pathfinder_FINAL.png', 'start': 600, 'end': 900},     # Pathfinder
        {'image': 'scene_05_weaver_FINAL.png', 'start': 900, 'end': 1200},        # Weaver
        {'image': 'scene_06_gamma_burst_FINAL.png', 'start': 1200, 'end': 1350},  # Gamma + Consolidation
        {'image': 'scene_07_consolidation_FINAL.png', 'start': 1350, 'end': 1500},# Integration
        {'image': 'scene_08_return_FINAL.png', 'start': 1500, 'end': duration_sec}# Awakening + Closing
    ]

    # Build filter complex for image sequence with crossfades
    filter_parts = []
    input_specs = []

    # Add audio input
    input_specs.append(f'-i {audio_path}')

    # Add all images as inputs
    for i, scene in enumerate(scenes):
        image_path = os.path.join(images_dir, scene['image'])
        input_specs.append(f"-loop 1 -t {scene['end'] - scene['start']} -i {image_path}")

    # Create video stream for each scene
    for i in range(len(scenes)):
        filter_parts.append(f"[{i+1}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
                           f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v{i}]")

    # Concatenate all video streams
    concat_inputs = ''.join([f'[v{i}]' for i in range(len(scenes))])
    filter_parts.append(f"{concat_inputs}concat=n={len(scenes)}:v=1:a=0[vout]")

    filter_complex = ';'.join(filter_parts)

    # Build full FFmpeg command
    cmd = ['ffmpeg']
    cmd.extend(input_specs[0].split())  # Audio input

    for input_spec in input_specs[1:]:  # Image inputs
        cmd.extend(input_spec.split())

    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[vout]',
        '-map', '0:a',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '256k',
        '-ar', '48000',
        '-movflags', '+faststart',
        '-y',
        output_path
    ])

    print(f"Creating video with {len(scenes)} scenes...")
    print(f"Duration: {duration_sec / 60:.1f} minutes")
    print(f"Resolution: 1920x1080 @ 30fps")
    print()
    print("This will take several minutes...")
    print()

    try:
        # Run with real-time progress
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Monitor progress
        for line in process.stdout:
            if 'time=' in line:
                # Extract time progress
                parts = line.split('time=')
                if len(parts) > 1:
                    time_str = parts[1].split()[0]
                    print(f"\rEncoding: {time_str} / {duration_sec//60:02d}:{duration_sec%60:02d}", end='', flush=True)

        process.wait()
        print()  # New line after progress

        if process.returncode == 0:
            file_size = os.path.getsize(output_path) / (1024 * 1024)

            print("\n" + "="*70)
            print("✓ VIDEO CREATION COMPLETE")
            print("="*70)
            print(f"\nFinal Video: {output_path}")
            print(f"Size: {file_size:.1f} MB")
            print(f"Duration: {duration_sec / 60:.1f} minutes")
            print(f"Resolution: 1920x1080 @ 30fps")
            print()

            return True
        else:
            print("\n✗ Video encoding failed")
            return False

    except Exception as e:
        print(f"\n✗ Error creating video: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("NEURAL NETWORK NAVIGATOR V2 - FINAL PRODUCTION")
    print("Ava Voice + Binaural Beats + Professional Mastering")
    print("="*70 + "\n")

    # Paths
    working_dir = "working_files"
    images_dir = "images"
    output_dir = "final_export"

    # Use the ultimate mix (voice + binaural + ambient + effects)
    ultimate_mix_path = os.path.join(working_dir, "neural_navigator_ULTIMATE_MIX.wav")
    final_video = os.path.join(output_dir, "neural_network_navigator_v2_ava_FINAL.mp4")

    # Duration (23:41 for ultimate mix)
    duration_sec = 1421  # 23 minutes 41 seconds

    # Check inputs exist
    if not os.path.exists(ultimate_mix_path):
        print(f"✗ Ultimate mix file not found: {ultimate_mix_path}")
        print("Run create_ultimate_audio.sh first to generate the complete audio mix")
        return 1

    if not os.path.exists(images_dir):
        print(f"✗ Images directory not found: {images_dir}")
        return 1

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create final video with ultimate mix
    print("Creating Final Video with Ultimate Mix")
    success = create_video_from_images(
        ultimate_mix_path,
        images_dir,
        final_video,
        duration_sec
    )

    if not success:
        print("\n✗ Video creation failed")
        return 1

    # Success!
    print("\n" + "="*70)
    print("🎉 PRODUCTION COMPLETE!")
    print("="*70)
    print()
    print("Final Output:")
    print(f"  {final_video}")
    print()
    print("Features:")
    print("  ✓ Ava Neural voice (warm, professional, corrected SSML)")
    print("  ✓ V2 enhanced script (pretalk + 5 anchors + closing)")
    print("  ✓ Professional audio mastering (-14 LUFS)")
    print("  ✓ Dynamic binaural beats (Alpha → Theta → 40Hz Gamma → Alpha)")
    print("  ✓ Pink noise ambient pad (cached from asset library)")
    print("  ✓ Sound effects (singing bowls, crystal bells, wind chimes)")
    print("  ✓ 8 visual scenes (1920x1080)")
    print("  ✓ 23.7 minutes duration")
    print()

    return 0

if __name__ == '__main__':
    os.chdir('/home/rsalars/Projects/dreamweaving/sessions/neural-network-navigator')
    sys.exit(main())
