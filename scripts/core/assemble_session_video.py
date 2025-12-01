#!/usr/bin/env python3
"""
Cross-session video assembler.

Builds a final meditation video by:
1) Choosing a base background video (provided or auto-found; falls back to solid color)
2) Overlaying user-provided stills with fades (from images/uploaded/)
3) Adding optional title/subtitle text
4) Muxing in the final audio track (voice+beds)

Timings:
- If a manifest.yaml with sections exists in the session dir, section start/end are used.
- Otherwise, images are evenly distributed across the audio duration.

Image expectations:
- Place PNGs in <session>/images/uploaded/
- Typical names: 01_pretalk.png, 02_induction.png, ... but any *.png will be ordered by filename.

Example:
    python scripts/core/assemble_session_video.py \\
        --session sessions/garden-of-eden \\
        --audio sessions/garden-of-eden/output/garden_of_eden_complete.mp3 \\
        --title \"Garden of Eden\" --subtitle \"Guided Meditation\"
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from pydub import AudioSegment

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


def load_manifest_sections(session_dir: Path):
    """Load section timing from manifest.yaml if available."""
    manifest_path = session_dir / "manifest.yaml"
    if not manifest_path.exists() or yaml is None:
        return None
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        sections = data.get("sections", [])
        # Expect items with start/end seconds
        cleaned = []
        for s in sections:
            if "start" in s and "end" in s:
                cleaned.append((s.get("name", "section"), float(s["start"]), float(s["end"])))
        if cleaned:
            # Sort by start time
            return sorted(cleaned, key=lambda x: x[1])
    except Exception:
        return None
    return None


def get_audio_duration_seconds(audio_path: Path) -> float:
    audio = AudioSegment.from_file(audio_path)
    return len(audio) / 1000.0


def collect_images(session_dir: Path):
    """Collect PNGs from images/uploaded (preferred), then session root, then images/example."""
    upload_dir = session_dir / "images" / "uploaded"
    example_dir = session_dir / "images" / "example"
    upload_dir.mkdir(parents=True, exist_ok=True)

    candidates = (
        sorted(upload_dir.glob("*.png"))
        + sorted(session_dir.glob("*.png"))
        + (sorted(example_dir.glob("*.png")) if example_dir.exists() else [])
    )
    seen = []
    for path in candidates:
        if path not in seen:
            seen.append(path)
    return seen


def _escape_drawtext(text: str) -> str:
    """Escape characters for ffmpeg drawtext."""
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", r"\'")


def build_image_timing(images, total_duration, manifest_sections=None):
    """
    Return list of (path, start, end) for each image.
    If manifest_sections present, align images in order to sections (truncate to min length).
    Else, evenly distribute across total_duration.
    """
    if not images:
        return []

    if manifest_sections:
        slots = min(len(images), len(manifest_sections))
        timed = []
        for i in range(slots):
            _, start, end = manifest_sections[i]
            timed.append((images[i], start, end))
        return timed

    # Even distribution
    slot = total_duration / len(images)
    timed = []
    for idx, img in enumerate(images):
        start = idx * slot
        end = (idx + 1) * slot
        timed.append((img, start, end))
    return timed


def ensure_background_video(session_dir: Path, audio_duration: float, background_arg: Path | None):
    """
    Choose a background video. Priority:
    1) user-provided via --background
    2) composite_with_images.mp4 in output/video
    3) background_gradient.mp4 in output/video
    4) generate solid color clip with ffmpeg color filter (duration = audio)
    """
    if background_arg and background_arg.exists():
        return background_arg

    output_video_dir = session_dir / "output" / "video"
    for name in ["composite_with_images.mp4", "background_gradient.mp4"]:
        candidate = output_video_dir / name
        if candidate.exists():
            return candidate

    # Fallback: solid color
    fallback = output_video_dir / "solid_background.mp4"
    output_video_dir.mkdir(parents=True, exist_ok=True)
    duration = max(1.0, audio_duration)
    cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        f"color=c=black:s=1920x1080:d={duration}",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-y",
        str(fallback),
    ]
    subprocess.run(cmd, check=True)
    return fallback


def build_filter_complex(images_timed, title, subtitle, fade_seconds=2.0):
    """
    Build ffmpeg filter_complex for overlays and optional text.
    Returns (filter_str, output_label).
    """
    filters = []

    # Scale/pad and add alpha per image
    for idx, (img_path, _, _) in enumerate(images_timed):
        input_num = idx + 1  # video is 0
        filters.append(
            f"[{input_num}:v]"
            f"scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
            f"format=yuva420p[scaled{idx}]"
        )

    # Alpha envelopes
    for idx, (_, start_sec, end_sec) in enumerate(images_timed):
        fade_in_end = start_sec + fade_seconds
        fade_out_start = end_sec - fade_seconds
        alpha_expr = (
            f"'if(lt(T,{start_sec}),0,"
            f"if(lt(T,{fade_in_end}),(T-{start_sec})*{255/fade_seconds},"
            f"if(lt(T,{fade_out_start}),255,"
            f"if(lt(T,{end_sec}),({end_sec}-T)*{255/fade_seconds},0))))'"
        )
        filters.append(
            f"[scaled{idx}]geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a={alpha_expr}[alpha{idx}]"
        )

    # Overlay chain
    current = "[0:v]"
    for idx in range(len(images_timed)):
        out_label = "[out]" if idx == len(images_timed) - 1 and not (title or subtitle) else f"[tmp{idx}]"
        filters.append(f"{current}[alpha{idx}]overlay=0:0{out_label}")
        current = out_label

    # Optional titles
    if title or subtitle:
        draw = current
        text_filters = []
        if title:
            esc_title = _escape_drawtext(title)
            text_filters.append(
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:"
                f"text='{esc_title}':fontcolor=white@0.9:fontsize=64:"
                f"x=(w-text_w)/2:y=120:shadowcolor=black@0.6:shadowx=2:shadowy=2"
            )
        if subtitle:
            esc_sub = _escape_drawtext(subtitle)
            text_filters.append(
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                f"text='{esc_sub}':fontcolor=white@0.8:fontsize=36:"
                f"x=(w-text_w)/2:y=200:shadowcolor=black@0.6:shadowx=2:shadowy=2"
            )
        chain = ",".join(text_filters)
        filters.append(f"{draw}{',' if chain else ''}{chain}[out]")

    output_label = "[out]" if (title or subtitle or images_timed) else "[0:v]"
    filter_complex = "; ".join(filters)
    return filter_complex, output_label


def _probe_duration(path: Path):
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            stderr=subprocess.STDOUT,
        ).decode()
        return float(out.strip())
    except Exception:
        return None


def assemble(session_dir: Path, audio_path: Path, background_path: Path | None, title: str, subtitle: str, fade_seconds: float):
    audio_duration = get_audio_duration_seconds(audio_path)
    base_video = ensure_background_video(session_dir, audio_duration, background_path)

    if (session_dir / "manifest.yaml").exists() and yaml is None:
        print("ℹ️ manifest.yaml present but PyYAML not installed; falling back to even image spacing.")

    manifest_sections = load_manifest_sections(session_dir)
    images = collect_images(session_dir)
    images_timed = build_image_timing(images, audio_duration, manifest_sections)

    if images_timed:
        filter_complex, output_label = build_filter_complex(images_timed, title, subtitle, fade_seconds=fade_seconds)
        inputs = ["-i", str(base_video)]
        for img_path, _, _ in images_timed:
            inputs.extend(["-loop", "1", "-i", str(img_path)])
        cmd = [
            "ffmpeg",
            *inputs,
        ]
        # Audio input comes after maps; add later
        cmd += [
            "-filter_complex",
            filter_complex,
            "-map",
            output_label,
            "-map",
            f"{len(images_timed)+1}:a",  # audio will be last input
        ]
    else:
        # No overlays; just add text if provided
        inputs = ["-i", str(base_video), "-i", str(audio_path)]
        filter_complex = None
        if title or subtitle:
            filters = []
            base_label = "[0:v]"
            text_filters = []
            if title:
                text_filters.append(
                    f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:"
                    f"text='{title}':fontcolor=white@0.9:fontsize=64:"
                    f"x=(w-text_w)/2:y=120:shadowcolor=black@0.6:shadowx=2:shadowy=2"
                )
            if subtitle:
                text_filters.append(
                    f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                    f"text='{subtitle}':fontcolor=white@0.8:fontsize=36:"
                    f"x=(w-text_w)/2:y=200:shadowcolor=black@0.6:shadowx=2:shadowy=2"
                )
            chain = ",".join(text_filters)
            filter_complex = f"{base_label}{',' if chain else ''}{chain}[out]"
        cmd = ["ffmpeg", *inputs]
        if filter_complex:
            cmd += ["-filter_complex", filter_complex, "-map", "[out]"]
        else:
            cmd += ["-map", "0:v"]
        cmd += ["-map", "1:a"]  # audio is second input

    # Append audio input (for images branch)
    if images_timed:
        cmd.extend(["-i", str(audio_path)])
    out_dir = session_dir / "output" / "video"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "session_final.mp4"
    cmd.extend([
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        "-y",
        str(output_path),
    ])

    # Debug info
    print("\nInputs:")
    print(f"  Video: {base_video}")
    print(f"  Audio: {audio_path}")
    print(f"  Images: {len(images_timed)}")
    if manifest_sections:
        print("  Timing source: manifest.yaml sections")
    else:
        print("  Timing source: even distribution")

    if filter_complex:
        print("\nFilter preview (truncated):")
        print(filter_complex[:400] + ("..." if len(filter_complex) > 400 else ""))

    subprocess.run(cmd, check=True)

    video_duration = _probe_duration(output_path)
    delta = None
    if video_duration is not None:
        delta = video_duration - audio_duration

    summary = {
        "video": str(output_path),
        "audio": str(audio_path),
        "background": str(base_video),
        "images_used": [str(p) for p, _, _ in images_timed],
        "timing_source": "manifest" if manifest_sections else "even_spacing",
        "durations": {
            "audio_sec": audio_duration,
            "video_sec": video_duration,
            "delta_sec": delta,
        },
    }
    with open(out_dir / "video_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n✅ Session video created:")
    print(f"   {output_path}")
    if video_duration:
        print(f"   Video duration: {video_duration/60:.2f} min; Audio: {audio_duration/60:.2f} min; Δ={delta:.2f} sec")
    print(f"Summary: {out_dir/'video_summary.json'}")


def main():
    parser = argparse.ArgumentParser(description="Assemble a session video with overlays and audio.")
    parser.add_argument("--session", required=True, help="Path to session directory (contains images/, output/ etc.)")
    parser.add_argument("--audio", help="Path to mixed audio MP3/WAV. Default: <session>/output/garden_of_eden_complete.mp3 or first MP3 in output/.")
    parser.add_argument("--background", help="Optional background video path; otherwise auto-detected or generated.")
    parser.add_argument("--title", default="", help="Title text overlay.")
    parser.add_argument("--subtitle", default="", help="Subtitle text overlay.")
    parser.add_argument("--fade", type=float, default=2.0, help="Fade duration for stills (seconds).")
    args = parser.parse_args()

    session_dir = Path(args.session).resolve()
    if not session_dir.exists():
        print(f"❌ Session not found: {session_dir}")
        sys.exit(1)

    # Resolve audio path
    audio_path = Path(args.audio) if args.audio else None
    if not audio_path:
        # Try a common default
        candidates = list((session_dir / "output").glob("*.mp3"))
        if not candidates:
            print("❌ Audio file not provided and none found in session/output")
            sys.exit(1)
        audio_path = candidates[0]
    audio_path = audio_path.resolve()
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_path}")
        sys.exit(1)

    background_path = Path(args.background).resolve() if args.background else None
    if background_path and not background_path.exists():
        print(f"⚠️ Background not found, will auto-fallback: {background_path}")
        background_path = None

    assemble(
        session_dir=session_dir,
        audio_path=audio_path,
        background_path=background_path,
        title=args.title,
        subtitle=args.subtitle,
        fade_seconds=args.fade,
    )


if __name__ == "__main__":
    main()
