#!/usr/bin/env python3
"""
Automated YouTube package generator for meditation sessions.
Creates complete YouTube-ready package from session manifest.

Usage:
    python3 scripts/core/package_youtube.py --session sessions/my-session
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    yaml = None


def load_manifest(session_dir):
    manifest_path = session_dir / "manifest.yaml"
    if not manifest_path.exists() or yaml is None:
        return {}
    with open(manifest_path, "r") as f:
        return yaml.safe_load(f)


def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def get_audio_duration(audio_path):
    if not audio_path or not audio_path.exists():
        return 1800
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 1800


def create_thumbnail(session_dir, manifest, output_dir):
    print("\n=== Creating YouTube Thumbnail ===")
    youtube_config = manifest.get("youtube", {})
    
    # Find source image
    if "thumbnail_source" in youtube_config:
        source_image = session_dir / youtube_config["thumbnail_source"]
    else:
        images_dir = session_dir / "images" / "uploaded"
        if not images_dir.exists():
            print("❌ No images/uploaded directory")
            return None
        images = sorted(images_dir.glob("*.png"))
        if not images:
            print("❌ No PNG images found")
            return None
        # Use middle or important image
        for img in images:
            if any(w in img.stem.lower() for w in ["helm", "attunement", "climax"]):
                source_image = img
                break
        else:
            source_image = images[len(images) // 2]
    
    if not source_image.exists():
        print(f"❌ Source image not found: {source_image}")
        return None
    
    output_file = output_dir / "youtube_thumbnail.png"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    title = youtube_config.get("title", manifest.get("session", {}).get("topic", "Meditation"))
    
    # Simple thumbnail without text overlay (to avoid escaping issues)
    cmd = [
        "ffmpeg", "-y", "-i", str(source_image),
        "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720",
        "-frames:v", "1", str(output_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"✅ Thumbnail created: {output_file} ({file_size:.2f} MB)")
        return output_file
    except subprocess.CalledProcessError:
        print("❌ Failed to create thumbnail")
        return None


def create_description(session_dir, manifest, output_dir, audio_duration):
    print("\n=== Creating YouTube Description ===")

    session = manifest.get("session", {})
    youtube_config = manifest.get("youtube", {})

    title = youtube_config.get("title", session.get("topic", "Meditation Session"))
    desc = f"# {title}\n\n"

    if youtube_config.get("description"):
        desc += youtube_config["description"] + "\n\n"

    minutes = int(audio_duration // 60)
    desc += f"**Duration**: {minutes} minutes\n\n"

    # Archetypes section (if present)
    archetypes = manifest.get("archetypes", [])
    if archetypes:
        desc += "## 🎭 Journey Archetypes\n\n"
        desc += "This meditation journey features symbolic encounters with:\n\n"
        for archetype in archetypes:
            name = archetype.get("name", "Unknown")
            role = archetype.get("role", "guide")
            arch_desc = archetype.get("description", "")
            qualities = archetype.get("qualities", [])

            desc += f"**{name}** - {role.replace('_', ' ').title()}\n"
            if arch_desc:
                desc += f"  {arch_desc}\n"
            if qualities:
                desc += f"  *Qualities: {', '.join(qualities)}*\n"
            desc += "\n"

    desc += "## 🎧 Audio Specifications\n\n"

    # Binaural info
    binaural = manifest.get("sound_bed", {}).get("binaural", {})
    if binaural.get("enabled"):
        carrier = binaural.get("base_hz", 432)
        desc += f"- **Binaural Beats**: {carrier} Hz carrier\n"

    # FX timeline
    fx_timeline = manifest.get("fx_timeline", [])
    for fx in fx_timeline:
        if fx.get("type") == "gamma_flash":
            time_str = format_timestamp(fx.get("time", 0))
            desc += f"- **Gamma Flash**: {fx.get('freq_hz', 40)} Hz at {time_str}\n"

    desc += "\n## 🌌 Timeline\n\n"

    # Add chapter markers
    sections = manifest.get("sections", [])
    for section in sections:
        start_time = format_timestamp(section.get("start", 0))
        name = section.get("name", "").replace("_", " ").title()
        desc += f"**{start_time}** - {name}\n"

    desc += "\n⚠️ Use headphones for binaural effectiveness\n"
    desc += "Do not use while driving or operating machinery\n\n"

    # Tags
    tags = youtube_config.get("tags", ["meditation", "binaural beats"])
    desc += "#" + " #".join(tags) + "\n"

    desc_file = output_dir / "YOUTUBE_DESCRIPTION.md"
    desc_file.write_text(desc)
    print(f"✅ Description created: {desc_file}")
    return desc_file


def create_vtt_subtitles(session_dir, manifest, output_dir):
    """Generate WebVTT subtitle file for YouTube from manifest sections"""
    print("\n=== Creating VTT Subtitles ===")

    sections = manifest.get("sections", [])
    if not sections:
        print("⚠️  No sections in manifest, skipping VTT generation")
        return None

    vtt_file = output_dir / "subtitles.vtt"

    # WebVTT format
    vtt_content = "WEBVTT\n\n"

    for i, section in enumerate(sections):
        start_time = section.get("start", 0)
        end_time = section.get("end", start_time + 60)
        name = section.get("name", f"Section {i+1}").replace("_", " ").title()
        description = section.get("description", "")
        brainwave = section.get("brainwave_target", "")

        # Format timestamps as HH:MM:SS.mmm
        start_formatted = format_vtt_timestamp(start_time)
        end_formatted = format_vtt_timestamp(end_time)

        # Create subtitle text
        subtitle_text = name
        if description:
            subtitle_text += f"\n{description}"
        if brainwave:
            subtitle_text += f"\n({brainwave})"

        # Write cue
        vtt_content += f"{i+1}\n"
        vtt_content += f"{start_formatted} --> {end_formatted}\n"
        vtt_content += f"{subtitle_text}\n\n"

    vtt_file.write_text(vtt_content)
    print(f"✅ VTT subtitles created: {vtt_file}")
    print(f"   {len(sections)} subtitle cues generated")
    return vtt_file


def format_vtt_timestamp(seconds):
    """Format seconds to WebVTT timestamp (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def create_upload_guide(session_dir, manifest, output_dir):
    print("\n=== Creating Upload Guide ===")

    guide = "# YouTube Upload Package\n\n"
    guide += f"**Created**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    guide += "## 📦 Package Contents\n\n"
    guide += "- youtube_thumbnail.png\n"
    guide += "- YOUTUBE_DESCRIPTION.md\n"
    guide += "- subtitles.vtt (WebVTT subtitles)\n"
    guide += "- Final video and audio files\n\n"
    guide += "## 🎬 Upload Settings\n\n"
    guide += "**Category**: Education\n"
    guide += "**Age Restriction**: No\n"
    guide += "**Comments**: Allow (moderate)\n\n"
    guide += "### Subtitles/CC\n"
    guide += "1. Upload `subtitles.vtt` as English subtitles\n"
    guide += "2. YouTube will auto-generate additional languages\n\n"

    guide_file = output_dir / "YOUTUBE_PACKAGE_README.md"
    guide_file.write_text(guide)
    print(f"✅ Upload guide created: {guide_file}")
    return guide_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    parser.add_argument("--audio", help="Audio file path")
    parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    session_dir = Path(args.session).resolve()
    if not session_dir.exists():
        print(f"❌ Session not found: {session_dir}")
        sys.exit(1)
    
    manifest = load_manifest(session_dir)
    output_dir = Path(args.output_dir) if args.output_dir else session_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    audio_path = Path(args.audio) if args.audio else None
    audio_duration = get_audio_duration(audio_path)
    if not audio_path:
        audio_duration = manifest.get("session", {}).get("duration", 1800)
    
    print("=" * 70)
    print("YouTube Package Generator")
    print("=" * 70)

    create_thumbnail(session_dir, manifest, output_dir)
    create_description(session_dir, manifest, output_dir, audio_duration)
    create_vtt_subtitles(session_dir, manifest, output_dir)
    create_upload_guide(session_dir, manifest, output_dir)

    print("\n✅ YouTube Package Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
