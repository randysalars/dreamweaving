#!/usr/bin/env python3
"""
Grid Clip Generator

Slices a video into evenly spaced short clips and optionally attaches subtitles
and a lightweight visual overlay. Useful when you need a fixed number of clips
regardless of keyword hits.

Example:
    PATH="venv/bin:$PATH" python -m scripts.automation.grid_clip_generator \
        --input-video sessions/christmas-light-entered/output/video/session_final.mp4 \
        --transcript output/blessing_clips/transcripts/audio.srt \
        --clip-len 12 --stride 50 --max-clips 40 \
        --output-root output/blessing_clips_grid
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List, Optional

from scripts.automation.blessing_clip_pipeline import (
    ClipArtifacts,
    Segment,
    apply_overlay,
    burn_subtitles,
    clip_media,
    clip_subtitles,
    ffprobe_duration,
    parse_srt_file,
    write_index_csv,
)


def build_grid_segments(duration: float, clip_len: float, stride: float, max_clips: int) -> List[Segment]:
    segments: List[Segment] = []
    start = 0.0
    while start < duration and len(segments) < max_clips:
        end = min(duration, start + clip_len)
        segments.append(Segment(start=start, end=end, reason="grid", score=1))
        start += stride
    return segments


def ensure_dirs(root: Path) -> tuple[Path, Path, Path, Path, Path]:
    raw_dir = root / "clips_raw"
    sub_dir = root / "clips_sub"
    final_dir = root / "clips_final"
    work_dir = root / "work"
    transcript_dir = root / "transcripts"
    for d in (raw_dir, sub_dir, final_dir, work_dir, transcript_dir):
        d.mkdir(parents=True, exist_ok=True)
    return raw_dir, sub_dir, final_dir, work_dir, transcript_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate evenly spaced grid clips.")
    parser.add_argument("--input-video", type=Path, required=True, help="Source video path")
    parser.add_argument("--transcript", type=Path, help="Optional SRT to slice into per-clip subtitles")
    parser.add_argument("--output-root", type=Path, default=Path("output/blessing_clips_grid"), help="Output root directory")
    parser.add_argument("--clip-len", type=float, default=12.0, help="Clip length in seconds")
    parser.add_argument("--stride", type=float, default=50.0, help="Stride between clip starts in seconds")
    parser.add_argument("--max-clips", type=int, default=40, help="Maximum number of clips")
    parser.add_argument("--burn", action="store_true", default=True, help="Burn subtitles into video (default on)")
    parser.add_argument("--no-burn", dest="burn", action="store_false", help="Disable subtitle burn-in")
    parser.add_argument("--overlay", action="store_true", default=True, help="Apply visual overlay (default on)")
    parser.add_argument("--no-overlay", dest="overlay", action="store_false", help="Disable visual overlay")
    parser.add_argument("--brightness", type=float, default=0.05, help="Overlay brightness lift")
    parser.add_argument("--saturation", type=float, default=1.1, help="Overlay saturation")
    parser.add_argument("--fade", type=float, default=0.4, help="Fade duration seconds for in/out")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    if not args.input_video.exists():
        raise FileNotFoundError(f"Input video not found: {args.input_video}")

    raw_dir, sub_dir, final_dir, _, _ = ensure_dirs(args.output_root)

    duration = ffprobe_duration(args.input_video)
    if duration is None:
        raise RuntimeError("ffprobe not available; cannot determine video duration")

    segments = build_grid_segments(duration, args.clip_len, args.stride, args.max_clips)
    logging.info("Planned %d grid segments (clip_len=%.1fs, stride=%.1fs)", len(segments), args.clip_len, args.stride)

    captions = []
    if args.transcript:
        captions = parse_srt_file(args.transcript)
        logging.info("Loaded transcript with %d captions", len(captions))

    artifacts: List[ClipArtifacts] = []
    for idx, seg in enumerate(segments, start=1):
        clip_name = f"clip_{idx:03d}.mp4"
        raw_path = raw_dir / clip_name
        srt_path = raw_dir / clip_name.replace(".mp4", ".srt")

        logging.info("Cutting %s (%.1f–%.1f)", clip_name, seg.start, seg.end)
        clip_media(args.input_video, seg, raw_path, reencode_fallback=True)

        if captions:
            clip_subtitles(captions, seg, srt_path)

        burned_path: Optional[Path] = None
        if args.burn and captions and srt_path.exists():
            burned_path = sub_dir / clip_name.replace(".mp4", "_sub.mp4")
            burn_subtitles(raw_path, srt_path, burned_path)

        final_overlay_path: Optional[Path] = None
        if args.overlay:
            final_overlay_path = final_dir / clip_name.replace(".mp4", "_final.mp4")
            apply_overlay(
                burned_path or raw_path,
                final_overlay_path,
                brightness=args.brightness,
                saturation=args.saturation,
                fade_duration=args.fade,
                clip_duration=max(0.1, seg.end - seg.start),
            )

        artifacts.append(
            ClipArtifacts(
                segment=seg,
                raw_path=raw_path,
                srt_path=srt_path,
                burned_path=burned_path,
                final_overlay_path=final_overlay_path,
            )
        )

    index_csv = args.output_root / "index.csv"
    write_index_csv(index_csv, artifacts)
    logging.info("Grid slicing complete. Index: %s", index_csv)


if __name__ == "__main__":
    main()
