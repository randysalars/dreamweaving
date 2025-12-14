#!/usr/bin/env python3
"""
Blessing Clip Pipeline

Fully automates:
1) Audio extraction and Whisper transcription
2) Segment detection (keywords + pause gaps)
3) Clip slicing with ffmpeg
4) Per-clip subtitles and optional burn-in/overlay

Usage:
    python -m scripts.automation.blessing_clip_pipeline \
        --config config/blessing_clip_config.yaml \
        --input-video input/full_video.mp4

    # Skip transcription if you already have an SRT
    python -m scripts.automation.blessing_clip_pipeline \
        --config config/blessing_clip_config.yaml \
        --transcript work/transcripts/dreamweaving.srt \
        --skip-transcription
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import srt
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "blessing_clip_config.yaml"

DEFAULT_CONFIG: Dict = {
    "input_video": "input/full_video.mp4",
    "input_audio": None,
    "work_dir": "output/blessing_clips/work",
    "transcript_dir": "output/blessing_clips/transcripts",
    "output_root": "output/blessing_clips",
    "whisper_model": "medium",
    "language": "en",
    "keywords": ["light", "peace", "christ", "heart", "stillness", "blessing"],
    "pause_gap_seconds": 1.8,
    "pad_pre_seconds": 2.0,
    "pad_post_seconds": 8.0,
    "min_len_seconds": 10.0,
    "max_len_seconds": 20.0,
    "max_clips": 60,
    "burn_subtitles": True,
    "overlay_enabled": True,
    "overlay": {"brightness": 0.05, "saturation": 1.1, "fade_duration": 0.4},
    "fallback_reencode": True,
}


@dataclass
class Caption:
    start: float
    end: float
    text: str


@dataclass
class Segment:
    start: float
    end: float
    reason: str
    score: int


@dataclass
class ClipArtifacts:
    segment: Segment
    raw_path: Path
    srt_path: Path
    burned_path: Optional[Path] = None
    final_overlay_path: Optional[Path] = None


def deep_merge(base: Dict, override: Dict) -> Dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: Path) -> Dict:
    if not config_path.exists():
        logging.warning("Config %s not found, using defaults", config_path)
        return DEFAULT_CONFIG

    with open(config_path, "r", encoding="utf-8") as f:
        file_cfg = yaml.safe_load(f) or {}
    merged = deep_merge(DEFAULT_CONFIG, file_cfg)
    return merged


def ensure_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd: Sequence[str], description: str) -> None:
    logging.debug("Running: %s", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        stdout = exc.stdout.decode("utf-8", errors="ignore")
        stderr = exc.stderr.decode("utf-8", errors="ignore")
        logging.error("%s failed\nstdout: %s\nstderr: %s", description, stdout, stderr)
        raise


def escape_ffmpeg_path(path: Path) -> str:
    # Escape characters that break ffmpeg filter args
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace(" ", "\\ ")


def extract_audio(input_video: Path, audio_path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required but not found on PATH")
    ensure_paths([audio_path.parent])
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_video),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(audio_path),
    ]
    run_cmd(cmd, "Audio extraction")


def run_whisper(audio_path: Path, transcript_dir: Path, model: str, language: str) -> Path:
    whisper_bin = shutil.which("whisper")
    if whisper_bin is None:
        raise RuntimeError("whisper CLI not found. Install with `pip install openai-whisper`.")

    ensure_paths([transcript_dir])
    cmd = [
        whisper_bin,
        str(audio_path),
        "--model",
        model,
        "--output_dir",
        str(transcript_dir),
        "--output_format",
        "srt",
    ]
    if language:
        cmd.extend(["--language", language])

    run_cmd(cmd, "Whisper transcription")

    srt_files = sorted(transcript_dir.glob("*.srt"))
    if not srt_files:
        raise RuntimeError("Whisper transcription completed but no SRT found")
    return srt_files[0]


def parse_srt_file(path: Path) -> List[Caption]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    subtitles = list(srt.parse(content))
    return [
        Caption(
            start=sub.start.total_seconds(),
            end=sub.end.total_seconds(),
            text=sub.content.replace("\n", " "),
        )
        for sub in subtitles
    ]


def detect_segments(
    captions: List[Caption],
    keywords: List[str],
    pause_gap: float,
    pad_pre: float,
    pad_post: float,
    min_len: float,
    max_len: float,
    max_clips: int,
    total_duration: Optional[float],
) -> List[Segment]:
    detected: List[Segment] = []
    kw_lower = [k.lower() for k in keywords]
    last_end = 0.0

    for cap in captions:
        text_lower = cap.text.lower()
        matches = [kw for kw in kw_lower if kw in text_lower]
        if matches:
            start = max(0.0, cap.start - pad_pre)
            end = cap.end + pad_post
            reason = f"keywords:{','.join(sorted(set(matches)))}"
            score = 2 + len(matches)
            detected.append(Segment(start=start, end=end, reason=reason, score=score))

        gap = cap.start - last_end
        if gap >= pause_gap:
            start = max(0.0, last_end - pad_pre)
            end = cap.start + pad_post
            reason = f"pause>{pause_gap:.1f}s"
            detected.append(Segment(start=start, end=end, reason=reason, score=1))

        last_end = cap.end

    merged = merge_segments(detected, min_len, max_len, total_duration)
    merged.sort(key=lambda s: (-s.score, s.start))
    return merged[:max_clips]


def merge_segments(
    segments: List[Segment],
    min_len: float,
    max_len: float,
    total_duration: Optional[float],
) -> List[Segment]:
    if not segments:
        return []

    segments = sorted(segments, key=lambda s: s.start)
    merged: List[Segment] = []

    current = segments[0]
    for seg in segments[1:]:
        if seg.start <= current.end + 0.5:
            current.end = max(current.end, seg.end)
            current.score += seg.score
            current.reason = f"{current.reason}|{seg.reason}"
        else:
            merged.append(current)
            current = seg
    merged.append(current)

    normalized: List[Segment] = []
    for seg in merged:
        if seg.end <= seg.start:
            continue
        duration = seg.end - seg.start
        if duration < min_len:
            seg.end = seg.start + min_len
        if duration > max_len:
            seg.end = seg.start + max_len
        if total_duration is not None:
            seg.end = min(seg.end, total_duration)
            seg.start = max(0.0, seg.start)
            if seg.start >= total_duration:
                continue
        normalized.append(seg)

    return normalized


def ffprobe_duration(path: Path) -> Optional[float]:
    probe_bin = shutil.which("ffprobe")
    if probe_bin is None:
        return None
    cmd = [
        probe_bin,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception:
        return None


def clip_media(
    video_path: Path,
    segment: Segment,
    output_path: Path,
    reencode_fallback: bool,
) -> None:
    ensure_paths([output_path.parent])
    duration = max(0.1, segment.end - segment.start)
    base_cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{segment.start:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{duration:.3f}",
        "-c",
        "copy",
        str(output_path),
    ]

    try:
        run_cmd(base_cmd, "Clip slicing (stream copy)")
        return
    except subprocess.CalledProcessError:
        if not reencode_fallback:
            raise

    reencode_cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{segment.start:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    run_cmd(reencode_cmd, "Clip slicing (re-encode fallback)")


def clip_subtitles(
    captions: List[Caption], segment: Segment, srt_output: Path
) -> None:
    ensure_paths([srt_output.parent])
    selected = []
    for cap in captions:
        if cap.end <= segment.start or cap.start >= segment.end:
            continue
        start_offset = max(0.0, cap.start - segment.start)
        end_offset = max(start_offset + 0.1, cap.end - segment.start)
        selected.append(
            srt.Subtitle(
                index=len(selected) + 1,
                start=timedelta(seconds=start_offset),
                end=timedelta(seconds=end_offset),
                content=cap.text,
            )
        )
    if not selected:
        return
    with open(srt_output, "w", encoding="utf-8") as f:
        f.write(srt.compose(selected))


def burn_subtitles(input_clip: Path, srt_path: Path, output_clip: Path) -> None:
    escaped = escape_ffmpeg_path(srt_path)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_clip),
        "-vf",
        f"subtitles={escaped}",
        "-c:a",
        "copy",
        str(output_clip),
    ]
    run_cmd(cmd, "Subtitle burn-in")


def apply_overlay(
    input_clip: Path,
    output_clip: Path,
    brightness: float,
    saturation: float,
    fade_duration: float,
    clip_duration: float,
) -> None:
    fade_out_start = max(0.0, clip_duration - fade_duration)
    filter_chain = (
        f"eq=brightness={brightness}:saturation={saturation},"
        f"fade=t=in:st=0:d={fade_duration},"
        f"fade=t=out:st={fade_out_start}:d={fade_duration}"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_clip),
        "-vf",
        filter_chain,
        "-c:a",
        "copy",
        str(output_clip),
    ]
    run_cmd(cmd, "Visual overlay")


def write_segments_json(path: Path, segments: List[Segment]) -> None:
    ensure_paths([path.parent])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "reason": seg.reason,
                    "score": seg.score,
                }
                for seg in segments
            ],
            f,
            indent=2,
        )


def write_index_csv(path: Path, artifacts: List[ClipArtifacts]) -> None:
    ensure_paths([path.parent])
    with open(path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "clip_id",
                "start",
                "end",
                "reason",
                "raw_path",
                "srt_path",
                "burned_path",
                "final_overlay_path",
            ]
        )
        for art in artifacts:
            writer.writerow(
                [
                    art.raw_path.stem,
                    f"{art.segment.start:.2f}",
                    f"{art.segment.end:.2f}",
                    art.segment.reason,
                    str(art.raw_path),
                    str(art.srt_path),
                    str(art.burned_path) if art.burned_path else "",
                    str(art.final_overlay_path) if art.final_overlay_path else "",
                ]
            )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automate blessing clip generation")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to YAML config")
    parser.add_argument("--input-video", type=Path, help="Override input video path")
    parser.add_argument("--input-audio", type=Path, help="Provide pre-extracted audio")
    parser.add_argument("--transcript", type=Path, help="Existing SRT to reuse")
    parser.add_argument("--skip-transcription", action="store_true", help="Skip Whisper run")
    parser.add_argument("--model", help="Override Whisper model name")
    parser.add_argument("--max-clips", type=int, help="Limit number of clips")
    parser.add_argument("--no-burn", action="store_true", help="Disable subtitle burn-in")
    parser.add_argument("--no-overlay", action="store_true", help="Disable visual overlay")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s %(message)s")

    cfg = load_config(args.config)

    input_video = args.input_video or Path(cfg["input_video"])
    input_audio = args.input_audio or (Path(cfg["input_audio"]) if cfg.get("input_audio") else None)
    work_dir = Path(cfg["work_dir"])
    transcript_dir = Path(cfg["transcript_dir"])
    output_root = Path(cfg["output_root"])

    raw_dir = output_root / "clips_raw"
    sub_dir = output_root / "clips_sub"
    final_dir = output_root / "clips_final"

    ensure_paths([work_dir, transcript_dir, raw_dir, sub_dir, final_dir])

    model = args.model or cfg["whisper_model"]
    max_clips = args.max_clips or cfg["max_clips"]

    if not input_video.exists() and not input_audio:
        raise FileNotFoundError(f"Input video not found: {input_video}")

    audio_path = input_audio or (work_dir / "audio.wav")
    if not input_audio:
        logging.info("Extracting audio...")
        extract_audio(input_video, audio_path)
    else:
        logging.info("Using provided audio: %s", audio_path)

    if args.skip_transcription and not args.transcript:
        raise ValueError("--skip-transcription requires --transcript to be provided")

    if args.transcript:
        transcript_path = args.transcript
    else:
        logging.info("Running Whisper transcription with model=%s...", model)
        transcript_path = run_whisper(audio_path, transcript_dir, model, cfg.get("language", ""))

    logging.info("Parsing transcript: %s", transcript_path)
    captions = parse_srt_file(transcript_path)

    total_duration = ffprobe_duration(input_video) if input_video.exists() else None
    logging.info("Detecting segments (max %d clips)...", max_clips)
    segments = detect_segments(
        captions=captions,
        keywords=cfg["keywords"],
        pause_gap=cfg["pause_gap_seconds"],
        pad_pre=cfg["pad_pre_seconds"],
        pad_post=cfg["pad_post_seconds"],
        min_len=cfg["min_len_seconds"],
        max_len=cfg["max_len_seconds"],
        max_clips=max_clips,
        total_duration=total_duration,
    )

    if not segments:
        logging.warning("No segments detected; exiting")
        return

    segments_json = output_root / "segments.json"
    write_segments_json(segments_json, segments)
    logging.info("Detected %d segments -> %s", len(segments), segments_json)

    artifacts: List[ClipArtifacts] = []
    for idx, seg in enumerate(segments, start=1):
        clip_name = f"clip_{idx:03d}.mp4"
        srt_name = f"clip_{idx:03d}.srt"
        raw_path = raw_dir / clip_name
        srt_path = raw_dir / srt_name

        logging.info("Cutting clip %s (%.1f-%.1f) %s", clip_name, seg.start, seg.end, seg.reason)
        clip_media(input_video, seg, raw_path, cfg["fallback_reencode"])
        clip_subtitles(captions, seg, srt_path)

        burned_path = None
        if not args.no_burn and cfg.get("burn_subtitles", True) and srt_path.exists():
            burned_path = sub_dir / clip_name.replace(".mp4", "_sub.mp4")
            burn_subtitles(raw_path, srt_path, burned_path)

        final_overlay_path = None
        overlay_enabled = cfg.get("overlay_enabled", True) and not args.no_overlay
        overlay_cfg = cfg.get("overlay", {})
        input_for_overlay = burned_path or raw_path
        if overlay_enabled:
            final_overlay_path = final_dir / clip_name.replace(".mp4", "_final.mp4")
            clip_duration = max(0.1, seg.end - seg.start)
            apply_overlay(
                input_for_overlay,
                final_overlay_path,
                brightness=overlay_cfg.get("brightness", 0.05),
                saturation=overlay_cfg.get("saturation", 1.1),
                fade_duration=overlay_cfg.get("fade_duration", 0.4),
                clip_duration=clip_duration,
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

    index_csv = output_root / "index.csv"
    write_index_csv(index_csv, artifacts)
    logging.info("Pipeline complete. Index written to %s", index_csv)


if __name__ == "__main__":
    main()
