#!/usr/bin/env python3
"""
One-command session builder: audio + video.

Steps:
1) Generate voice (chunked TTS) with optional rate targeting duration
2) Generate simple binaural bed matched to voice
3) Mix voice + bed into a final MP3
4) Assemble video (background autodetect/fallback; overlays from images/uploaded)
5) Report output paths

Usage:
    python3 scripts/core/build_session.py \
        --session sessions/garden-of-eden \
        --ssml sessions/garden-of-eden/script.ssml \
        --voice en-US-Neural2-D \
        --target-minutes 25 \
        --title "Garden of Eden" --subtitle "Guided Meditation"
"""

import argparse
import sys
import time
from pathlib import Path

from generate_session_audio import main as audio_main  # reuse CLI
from assemble_session_video import main as video_main  # reuse CLI

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

# Import logging and audit
try:
    script_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(script_dir))
    from utilities.logging_config import get_logger
    from utilities.audit_logger import log_event, log_error, AuditContext
except ImportError:
    # Fallback if audit logger not available
    import logging
    get_logger = lambda name: logging.getLogger(name)
    log_event = lambda *args, **kwargs: None
    log_error = lambda *args, **kwargs: None

    class AuditContext:
        """Fallback no-op context manager when audit_logger unavailable."""
        def __init__(self, prefix=""):
            self.prefix = prefix  # Store prefix for compatibility
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

logger = get_logger(__name__)

# Import validation utilities
try:
    script_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(script_dir))
    from utilities.validation import (
        validate_dir_exists,
        validate_file_exists,
        validate_speaking_rate,
        validate_pitch,
        validate_binaural_offset,
        validate_frequency,
        validate_volume_db,
    )
except ImportError:
    # Fallback to basic validation
    validate_dir_exists = str
    validate_file_exists = str
    validate_speaking_rate = float
    validate_pitch = float
    validate_binaural_offset = float
    validate_frequency = float
    validate_volume_db = float


def load_manifest_defaults(session_dir: Path):
    defaults = {}
    manifest_path = session_dir / "manifest.yaml"
    if not manifest_path.exists() or yaml is None:
        return defaults
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        session = data.get("session", {})
        voice = data.get("voice", {}).get("voice_name")
        provider = data.get("voice", {}).get("provider")
        duration_sec = session.get("duration")

        # Load binaural configuration
        sound_bed = data.get("sound_bed", {})
        binaural = sound_bed.get("binaural", {})
        carrier_hz = binaural.get("base_hz")

        # Store full manifest data for beat schedule generation
        defaults["manifest_data"] = data

        if voice:
            defaults["voice"] = voice
        if provider:
            defaults["tts_provider"] = provider
        if duration_sec:
            defaults["target_minutes"] = float(duration_sec) / 60.0
        if carrier_hz:
            defaults["carrier_hz"] = float(carrier_hz)
    except Exception:
        return defaults
    return defaults


def run_audio(args, manifest_data=None):
    audio_args = [
        "--ssml",
        str(args.ssml),
        "--voice",
        args.voice,
        "--tts-provider",
        args.tts_provider,
        "--target-minutes",
        str(args.target_minutes),
        "--match-mode",
        args.match_mode,
        "--beat-hz",
        str(args.beat_hz),
        "--carrier-hz",
        str(args.carrier_hz),
        "--bed-gain-db",
        str(args.bed_gain_db),
        "--voice-gain-db",
        str(args.voice_gain_db),
        "--sample-rate",
        str(args.sample_rate),
        "--max-bytes",
        str(args.max_bytes),
    ]
    if args.output_dir:
        audio_args += ["--output-dir", str(args.output_dir)]
    if args.mix_name:
        audio_args += ["--mix-out", str((Path(args.output_dir) if args.output_dir else Path(args.ssml).parent / "output") / args.mix_name)]

    # Pass manifest as beat schedule if available
    if manifest_data:
        import json
        import tempfile
        # Create temporary JSON file with manifest data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest_data, f)
            temp_schedule_path = f.name
        audio_args += ["--beat-schedule", temp_schedule_path]

    sys.argv = ["generate_session_audio"] + audio_args
    audio_main()

    # Clean up temp file
    if manifest_data:
        import os
        os.unlink(temp_schedule_path)


def run_video(args, session_dir: Path, audio_path: Path):
    video_args = [
        "--session",
        str(session_dir),
        "--audio",
        str(audio_path),
        "--fade",
        str(args.fade),
    ]
    if args.title:
        video_args += ["--title", args.title]
    if args.subtitle:
        video_args += ["--subtitle", args.subtitle]
    if args.background:
        video_args += ["--background", str(args.background)]
    sys.argv = ["assemble_session_video"] + video_args
    video_main()


def main():
    parser = argparse.ArgumentParser(description="One-command build for session audio+video.")
    parser.add_argument("--session", type=validate_dir_exists, required=True, help="Session directory.")
    parser.add_argument("--ssml", type=validate_file_exists, required=True, help="Path to SSML file.")
    parser.add_argument("--voice", default="en-US-Neural2-D", help="Voice name (default: Google Neural2-D).")
    parser.add_argument("--tts-provider", choices=["google"], default="google", help="TTS provider (Google Cloud TTS only).")
    parser.add_argument("--target-minutes", type=float, default=None, help="Target duration (minutes).")
    parser.add_argument("--match-mode", choices=["bed_to_voice", "voice_to_target"], default="bed_to_voice",
                       help="bed_to_voice (default): binaural matches actual voice duration; voice_to_target: extends to target-minutes")
    parser.add_argument("--beat-hz", type=validate_binaural_offset, default=7.83, help="Binaural beat frequency (0.5-100 Hz).")
    parser.add_argument("--carrier-hz", type=validate_frequency, default=432.0, help="Carrier frequency (0.1-20000 Hz).")
    parser.add_argument("--bed-gain-db", type=validate_volume_db, default=-12.0, help="Bed gain (-40 to +10 dB). Default: -12 dB (best practice).")
    parser.add_argument("--voice-gain-db", type=validate_volume_db, default=-6.0, help="Voice gain (-40 to +10 dB). Default: -6 dB (headroom for post-processing).")
    parser.add_argument("--sample-rate", type=int, default=24000, choices=[16000, 22050, 24000, 44100, 48000], help="Sample rate Hz.")
    parser.add_argument("--max-bytes", type=int, default=5000)
    parser.add_argument("--output-dir", help="Override audio output dir (default: <ssml_dir>/output).")
    parser.add_argument("--mix-name", default=None, help="Final mixed audio filename (default: final_mix.mp3).")
    parser.add_argument("--title", default="", help="Video title text.")
    parser.add_argument("--subtitle", default="", help="Video subtitle text.")
    parser.add_argument("--background", help="Optional background video path.")
    parser.add_argument("--fade", type=float, default=2.0, help="Fade for stills (seconds).")
    parser.add_argument("--auto-package", action="store_true", help="Auto-generate YouTube package and cleanup")
    args = parser.parse_args()

    # args.session and args.ssml are already validated by validate_dir_exists/validate_file_exists
    session_dir = Path(args.session).resolve()
    ssml_path = Path(args.ssml).resolve()
    session_name = session_dir.name
    build_start = time.time()

    # Start audit context for correlated logging
    with AuditContext("build"):
        logger.info(f"Starting session build: {session_name}")
        log_event("session_build_started", session_name, {
            "ssml_path": str(ssml_path),
            "voice": args.voice,
            "target_minutes": args.target_minutes,
        })

        manifest_defaults = load_manifest_defaults(session_dir)
        manifest_data = manifest_defaults.get("manifest_data")

        # Apply manifest defaults
        if manifest_defaults and args.target_minutes is None:
            args.target_minutes = manifest_defaults.get("target_minutes", None)
        if manifest_defaults and args.voice == parser.get_default("voice") and manifest_defaults.get("voice"):
            args.voice = manifest_defaults["voice"]
        if manifest_defaults and args.tts_provider == parser.get_default("tts_provider") and manifest_defaults.get("tts_provider"):
            args.tts_provider = manifest_defaults["tts_provider"]
        if manifest_defaults and args.carrier_hz == parser.get_default("carrier_hz") and manifest_defaults.get("carrier_hz"):
            args.carrier_hz = manifest_defaults["carrier_hz"]

        if args.target_minutes is None:
            args.target_minutes = 25.0
        if args.mix_name is None:
            args.mix_name = "final_mix.mp3"
        if (session_dir / "manifest.yaml").exists() and yaml is None:
            logger.warning("manifest.yaml present but PyYAML not installed; defaults may not be auto-applied.")

        # Run audio with manifest data for beat schedule
        logger.info("Starting audio generation...")
        try:
            run_audio(args, manifest_data)
            log_event("audio_generated", session_name, {"mix_name": args.mix_name})
        except Exception as e:
            log_error(session_name, e, {"stage": "audio_generation"})
            logger.error(f"Audio generation failed: {e}")
            raise

        # Locate mixed audio
        output_dir = Path(args.output_dir) if args.output_dir else ssml_path.parent / "output"
        preferred_mix = output_dir / args.mix_name
        if preferred_mix.exists():
            mixed_candidates = [preferred_mix]
        else:
            mixed_candidates = sorted(output_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not mixed_candidates:
            logger.error("Mixed audio not found in output/.")
            log_error(session_name, FileNotFoundError("Mixed audio not found"), {"stage": "audio_location"})
            sys.exit(1)
        audio_path = mixed_candidates[0]

        # Run video assembly
        logger.info("Starting video assembly...")
        try:
            run_video(args, session_dir, audio_path)
            log_event("video_assembled", session_name, {"audio_path": str(audio_path)})
        except Exception as e:
            log_error(session_name, e, {"stage": "video_assembly"})
            logger.error(f"Video assembly failed: {e}")
            raise

        video_path = session_dir / 'output' / 'video' / 'session_final.mp4'

        # Optional: Auto-package for YouTube
        if args.auto_package:
            logger.info("Auto-packaging for YouTube...")
            try:
                import subprocess
                subprocess.run([
                    "python3", "scripts/core/package_youtube.py",
                    "--session", str(session_dir),
                    "--audio", str(audio_path)
                ], check=True)
                logger.info("YouTube package created")
                log_event("youtube_packaged", session_name, {"audio_path": str(audio_path)})
            except Exception as e:
                logger.warning(f"YouTube packaging failed: {e}")
                log_error(session_name, e, {"stage": "youtube_packaging"})

            # Run cleanup
            logger.info("Running cleanup...")
            try:
                subprocess.run([
                    "bash", "scripts/core/cleanup_session_assets.sh",
                    str(session_dir)
                ], check=True)
                logger.info("Cleanup complete")
                log_event("cleanup_performed", session_name, {})
            except Exception as e:
                logger.warning(f"Cleanup failed: {e}")

        # Calculate build duration
        build_duration = time.time() - build_start

        # Log completion
        log_event("session_build_completed", session_name, {
            "audio_path": str(audio_path),
            "video_path": str(video_path),
            "duration_seconds": round(build_duration, 1),
            "auto_packaged": args.auto_package,
        })

        print("\n" + "=" * 70)
        print("✅ BUILD COMPLETE")
        print("=" * 70)
        print(f"Audio: {audio_path}")
        print(f"Video: {video_path}")
        print(f"Duration: {build_duration:.1f}s")
        if args.auto_package:
            print(f"YouTube Package: {session_dir / 'output' / 'YOUTUBE_PACKAGE_README.md'}")
        print("=" * 70)

        logger.info(f"Build complete for {session_name} in {build_duration:.1f}s")


if __name__ == "__main__":
    main()
