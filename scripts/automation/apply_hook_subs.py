#!/usr/bin/env python3
"""
Apply hook overlays to grid clips.

Reads overlay hooks CSV (clip_id,line1,line2), builds a simple two-line SRT
per clip (line1 from 0-5.5s, line2 from 5.5s to clip end), and burns it onto
the existing grid `clip_###_final.mp4` files.

Outputs go to `output/blessing_clips_grid/clips_final_hook/clip_###_hook.mp4`
by default.

Usage:
    PATH="venv/bin:$PATH" python -m scripts.automation.apply_hook_subs \
      --hooks output/blessing_clips_grid/overlay_hooks.csv \
      --final-dir output/blessing_clips_grid/clips_final \
      --out-dir output/blessing_clips_grid/clips_final_hook
"""

from __future__ import annotations

import argparse
import csv
import logging
import subprocess
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

import srt


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


def write_srt(path: Path, line1: str, line2: str, clip_len: float) -> None:
    # Allocate roughly half/half timing
    mid = min(clip_len / 2, 6.0)  # don't go beyond 6s on first line
    end = clip_len
    subs = [
        srt.Subtitle(index=1, start=timedelta(seconds=0), end=timedelta(seconds=mid), content=line1),
        srt.Subtitle(index=2, start=timedelta(seconds=mid), end=timedelta(seconds=end), content=line2),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subs))


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


def burn(input_video: Path, srt_path: Path, output_video: Path) -> None:
    output_video.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_video),
        "-vf",
        f"subtitles={srt_path}",
        "-c:a",
        "copy",
        str(output_video),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Burn hook subtitles onto grid clips.")
    parser.add_argument("--hooks", type=Path, required=True, help="CSV with clip_id,line1,line2")
    parser.add_argument("--final-dir", type=Path, required=True, help="Directory containing clip_###_final.mp4")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory for hook-burned videos")
    parser.add_argument("--work-dir", type=Path, default=Path("output/blessing_clips_grid/work_hooks"), help="Where to store temp SRTs")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")

    hooks = read_hooks(args.hooks)
    logging.info("Loaded %d hooks", len(hooks))

    for hook in hooks:
        input_path = args.final_dir / f"{hook.clip_id}_final.mp4"
        if not input_path.exists():
            # Fallback to raw clip naming if _final isn't present
            alt = args.final_dir / f"{hook.clip_id}.mp4"
            input_path = alt if alt.exists() else input_path
        if not input_path.exists():
            logging.warning("Skipping %s: input not found (%s)", hook.clip_id, input_path)
            continue

        clip_len = ffprobe_duration(input_path)
        srt_path = args.work_dir / f"{hook.clip_id}.srt"
        write_srt(srt_path, hook.line1, hook.line2, clip_len)

        output_path = args.out_dir / f"{hook.clip_id}_hook.mp4"
        logging.info("Burning hook onto %s -> %s", input_path.name, output_path)
        burn(input_path, srt_path, output_path)

    logging.info("Done.")


if __name__ == "__main__":
    main()
