#!/usr/bin/env python3
"""
Generate TTS for hook lines and mix onto grid clips.

Reads overlay_hooks.csv (clip_id,line1,line2), generates TTS for the two lines
combined (gTTS), and mixes the voice track with the existing audio while
keeping the burned-in hook subtitles.

Outputs to clips_final_hook_voice/clip_###_voice.mp4 by default.

Usage:
    PATH="venv/bin:$PATH" python -m scripts.automation.apply_hook_voice \
      --hooks output/blessing_clips_grid/overlay_hooks.csv \
      --final-hook-dir output/blessing_clips_grid/clips_final_hook \
      --out-dir output/blessing_clips_grid/clips_final_hook_voice
"""

from __future__ import annotations

import argparse
import csv
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from gtts import gTTS


@dataclass
class Hook:
    clip_id: str
    line1: str
    line2: str


def read_hooks(path: Path) -> List[Hook]:
    hooks: List[Hook] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hooks.append(Hook(clip_id=row["clip_id"], line1=row["line1"], line2=row["line2"]))
    return hooks


def synth(text: str, out_path: Path, lang: str = "en") -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tts = gTTS(text=text, lang=lang)
    tts.save(str(out_path))


def ffprobe_duration(path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def mix_audio(video: Path, voice: Path, out_path: Path, duck: float = 0.78) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Duck original audio slightly, mix TTS at full volume, normalize.
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-i",
        str(voice),
        "-filter_complex",
        f"[0:a]volume={duck}[a0];[a0][1:a]amix=inputs=2:normalize=1[aout]",
        "-map",
        "0:v",
        "-map",
        "[aout]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate hook TTS and mix onto grid clips.")
    parser.add_argument("--hooks", type=Path, required=True, help="overlay_hooks.csv")
    parser.add_argument("--final-hook-dir", type=Path, required=True, help="Directory with clip_###_hook.mp4 (burned subs)")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory for voice-mixed clips")
    parser.add_argument("--work-dir", type=Path, default=Path("output/blessing_clips_grid/work_voice"), help="Temp dir for TTS audio")
    parser.add_argument("--duck", type=float, default=0.78, help="Volume factor for original audio during mix")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    hooks = read_hooks(args.hooks)
    logging.info("Loaded %d hooks", len(hooks))

    # Synthesize voice tracks
    for hook in hooks:
        text = f"{hook.line1}. {hook.line2}"
        voice_path = args.work_dir / f"{hook.clip_id}.mp3"
        logging.info("Synthesizing voice for %s", hook.clip_id)
        synth(text, voice_path)

    # Mix onto videos
    for hook in hooks:
        src = args.final_hook_dir / f"{hook.clip_id}_hook.mp4"
        if not src.exists():
            logging.warning("Skipping %s: missing video %s", hook.clip_id, src)
            continue
        voice_path = args.work_dir / f"{hook.clip_id}.mp3"
        if not voice_path.exists():
            logging.warning("Skipping %s: missing voice %s", hook.clip_id, voice_path)
            continue
        out_path = args.out_dir / f"{hook.clip_id}_voice.mp4"
        logging.info("Mixing voice onto %s -> %s", src.name, out_path)
        mix_audio(src, voice_path, out_path, duck=args.duck)


if __name__ == "__main__":
    main()
