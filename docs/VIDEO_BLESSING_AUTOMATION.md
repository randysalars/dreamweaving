# Blessing Clip Automation

End-to-end automation for mining “blessing” moments from longform video, slicing 10–20s clips, and delivering subtitle-ready shorts with optional visual polish. Everything runs locally with FFmpeg and Whisper.

## Objectives
- Zero-manual pass: transcribe → detect → slice → subtitle → polish.
- Keep it reproducible: YAML config, deterministic heuristics, JSON/CSV outputs.
- Keep it cheap: local Whisper + stream-copy first, re-encode only if needed.

## Layout
- Input: `input/full_video.mp4` (or `--input-video`), optional `input_audio`.
- Work: `output/blessing_clips/work/audio.wav` + transcripts in `output/blessing_clips/transcripts/`.
- Outputs:
  - `output/blessing_clips/clips_raw/clip_###.mp4` (+ `.srt`)
  - `output/blessing_clips/clips_sub/clip_###_sub.mp4` (burned subs, optional)
  - `output/blessing_clips/clips_final/clip_###_final.mp4` (overlay, optional)
  - Manifests: `segments.json`, `index.csv`
- Config: `config/blessing_clip_config.yaml`

## Pipeline (improved)
1) **Pre-flight**: Assert `ffmpeg`, `whisper` CLI, readable input. Probe duration via `ffprobe` for clamping.
2) **Audio prep**: Extract mono 16kHz WAV (`ffmpeg -vn -ac 1 -ar 16000`), unless `--input-audio` is supplied.
3) **Transcription**: `whisper AUDIO --model medium --output_format srt --language en` into `transcripts/`. Skip with `--skip-transcription --transcript path`.
4) **Segment detection** (hybrid rules):
   - **Keyword hits** (case-insensitive) using `keywords` list; pad `pad_pre_seconds`/`pad_post_seconds`.
   - **Pause windows** where SRT gaps exceed `pause_gap_seconds`.
   - Normalize to `min_len_seconds`/`max_len_seconds`, clamp to media duration, merge overlaps (reasons + scores are aggregated).
   - Rank by score (keywords > pauses) then time; cap to `max_clips` (default 60).
   - Persist to `segments.json` with `{start,end,reason,score}` for auditing.
5) **Clip slicing**: `ffmpeg -ss START -t DURATION -c copy` into `clips_raw/`; if copy fails, auto re-encode with `libx264+aac` (`fallback_reencode` toggle).
6) **Subtitles per clip**: Cut SRT to each window, reset timestamps to 0, save alongside raw clip.
7) **Optional burn-in**: `ffmpeg -vf subtitles=clip.srt -c:a copy` → `clips_sub/` (controlled by `burn_subtitles` or `--no-burn`).
8) **Optional overlay**: Lightweight filter `eq(brightness,saturation)+fade in/out` → `clips_final/` (controlled by `overlay_enabled` or `--no-overlay`).
9) **Indexing**: `index.csv` enumerates clip id, times, reasons, and all artifact paths.

## Config Highlights (`config/blessing_clip_config.yaml`)
- Detection: `keywords`, `pause_gap_seconds`, `pad_pre_seconds`, `pad_post_seconds`, `min_len_seconds`, `max_len_seconds`, `max_clips`
- Rendering: `burn_subtitles`, `overlay_enabled`, `overlay.brightness|saturation|fade_duration`, `fallback_reencode`
- IO: `input_video`, `input_audio` (optional), `work_dir`, `transcript_dir`, `output_root`, `whisper_model`, `language`

## Quick Start
```bash
cd ~/Projects/dreamweaving

# Ensure deps
python -m pip install -r requirements.txt
python -m pip install openai-whisper  # whisper CLI

# Run full pipeline (default config/paths)
python -m scripts.automation.blessing_clip_pipeline \
  --config config/blessing_clip_config.yaml \
  --input-video input/full_video.mp4

# Reuse an existing transcript and skip Whisper
python -m scripts.automation.blessing_clip_pipeline \
  --config config/blessing_clip_config.yaml \
  --transcript output/blessing_clips/transcripts/video.srt \
  --skip-transcription

# Disable overlay or burn-in
python -m scripts.automation.blessing_clip_pipeline --no-overlay
python -m scripts.automation.blessing_clip_pipeline --no-burn
```

## Operational Notes
- Default clip range targets 40–60 outputs; tune `keywords`, `pause_gap_seconds`, and `max_clips` per talk.
- Stream-copy first keeps the pipeline fast; enabling `fallback_reencode` improves success on non-keyframe-aligned cuts.
- All manifests are human-auditable; adjust windows directly in `segments.json` and rerun slicing-only by reusing transcripts and skipping Whisper.
