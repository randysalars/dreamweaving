#!/usr/bin/env python3
"""
Universal session audio generator.

Given an SSML script, this tool will:
1) Synthesize the voice track (chunked, to avoid provider limits)
2) Optionally adjust speaking rate toward a target duration
3) Generate a simple binaural bed that matches the desired length
4) Mix voice + binaural into a final MP3 (optional)

Example:
    python scripts/core/generate_session_audio.py \
        --ssml sessions/my-session/script.ssml \
        --voice en-US-Neural2-D \
        --target-minutes 22 \
        --match-mode bed_to_voice
"""

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from pydub import AudioSegment

# Local imports
from audio.binaural import generate as generate_binaural, save_stem
from generate_audio_chunked import synthesize_ssml_file_chunked

# Import validation utilities
try:
    script_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(script_dir))
    from utilities.validation import (
        validate_file_exists,
        validate_output_path,
        validate_speaking_rate,
        validate_pitch,
        validate_binaural_offset,
        validate_frequency,
        validate_volume_db,
        validate_percentage,
    )
except ImportError:
    # Fallback to basic validation
    validate_file_exists = str
    validate_output_path = str
    validate_speaking_rate = float
    validate_pitch = float
    validate_binaural_offset = float
    validate_frequency = float
    validate_volume_db = float
    validate_percentage = float


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _audio_duration_seconds(path: Path) -> float:
    """Return duration of an audio file in seconds."""
    audio = AudioSegment.from_file(path)
    return len(audio) / 1000.0


def _audio_stats(path: Path):
    audio = AudioSegment.from_file(path)
    peak_raw = audio.max_possible_amplitude
    peak = audio.max
    peak_db = 20 * math.log10(max(peak, 1) / peak_raw) if peak_raw else float("-inf")
    rms = audio.rms
    rms_db = 20 * math.log10(max(rms, 1) / peak_raw) if peak_raw else float("-inf")
    return {
        "duration_sec": len(audio) / 1000.0,
        "peak_dbfs": peak_db,
        "rms_dbfs": rms_db,
    }


def _extend_voice_with_silence(voice_path: Path, target_seconds: float, split_fraction: float = 0.75):
    """
    DEPRECATED: This function was used to work around Edge TTS ignoring SSML breaks.
    Google Cloud TTS respects SSML breaks, so this is no longer needed.
    Kept for backward compatibility only.

    Args:
        voice_path: Path to voice audio file
        target_seconds: Target duration in seconds
        split_fraction: Where to insert silence (0.75 = 75% through)

    Returns:
        New duration in seconds
    """
    voice = AudioSegment.from_file(voice_path)
    current_duration = len(voice) / 1000.0

    if current_duration >= target_seconds:
        return current_duration

    needed_silence_ms = int((target_seconds - current_duration) * 1000)
    split_point_ms = int(len(voice) * split_fraction)

    part1 = voice[:split_point_ms]
    part2 = voice[split_point_ms:]
    silence = AudioSegment.silent(duration=needed_silence_ms)

    extended = part1 + silence + part2

    print(f"   Extending voice: {current_duration:.1f}s → {target_seconds:.1f}s")
    print(f"   Inserting {needed_silence_ms/1000:.1f}s silence at {split_point_ms/1000:.1f}s mark")

    # Export with same format
    fmt = voice_path.suffix.lstrip(".")
    extended.export(voice_path, format=fmt, bitrate="320k" if fmt == "mp3" else None)

    return len(extended) / 1000.0


def _maybe_adjust_rate(current_rate: float, current_dur: float, target_dur: float):
    """
    Calculate an adjusted speaking rate to hit a target duration.
    Returns (new_rate, changed_flag).
    """
    if target_dur <= 0 or current_dur <= 0:
        return current_rate, False

    raw = current_rate * (current_dur / target_dur)
    # Keep rates in a sane, natural range
    adjusted = max(0.70, min(1.15, raw))
    changed = abs(adjusted - current_rate) > 0.02
    return adjusted, changed


def _mix_tracks(voice_path: Path, bed_path: Path, output_path: Path, voice_gain_db=0, bed_gain_db=-10):
    """Overlay voice + binaural bed, aligning lengths."""
    voice = AudioSegment.from_file(voice_path)
    bed = AudioSegment.from_file(bed_path)

    # Match durations to voice (voice is always the reference)
    if len(bed) < len(voice):
        padding = AudioSegment.silent(duration=len(voice) - len(bed))
        bed = bed + padding
    elif len(bed) > len(voice):
        bed = bed[:len(voice)]

    voice = voice + voice_gain_db
    bed = bed + bed_gain_db

    mixed = voice.overlay(bed)
    mixed.export(output_path, format="mp3", bitrate="320k", parameters=["-q:a", "0"])

    return len(mixed) / 1000.0


def _synthesize_edge_tts(ssml_path: Path, out_path: Path, voice_name: str, speaking_rate: float, pitch_semitones: float):
    """
    DEPRECATED: Edge TTS has been removed from the production workflow.
    This function is kept for backward compatibility only but will raise an error if called.

    Edge TTS was removed because:
    - Ignores ALL SSML <break> tags
    - Too fast for hypnotic/meditative work
    - Audio quality issues (skipping/glitching)

    Use Google Cloud TTS Neural2 instead.
    """
    raise NotImplementedError(
        "Edge TTS is no longer supported in the production workflow. "
        "Please use Google Cloud TTS Neural2 instead. "
        "See docs/EDGE_TTS_REMOVAL.md for migration guide."
    )


def main():
    parser = argparse.ArgumentParser(description="Generate voice + binaural audio for any session topic.")
    parser.add_argument("--ssml", type=validate_file_exists, required=True, help="Path to SSML file.")
    parser.add_argument("--voice", default="en-US-Neural2-D", help="Voice name (default: Google Neural2-D).")
    parser.add_argument("--speaking-rate", type=validate_speaking_rate, default=0.75, help="Initial speaking rate multiplier (0.25-4.0, default: 0.75 for meditation).")
    parser.add_argument("--pitch", type=validate_pitch, default=-2.5, help="Pitch in semitones (-20 to +20, default: -2.5st).")
    parser.add_argument(
        "--tts-provider",
        choices=["google"],
        default="google",
        help="TTS provider (Google Cloud TTS only).",
    )
    parser.add_argument("--target-minutes", type=float, default=None, help="Optional target session length in minutes.")
    parser.add_argument(
        "--match-mode",
        choices=["bed_to_voice", "voice_to_target"],
        default="bed_to_voice",
        help="Whether to stretch the bed to the voice (default) or adjust voice rate toward target length.",
    )
    parser.add_argument("--beat-hz", type=validate_binaural_offset, default=7.83, help="Binaural beat frequency (0.5-100 Hz).")
    parser.add_argument(
        "--beat-schedule",
        default=None,
        help=(
            "JSON string or file path describing beat sections. "
            "Example: '[{\"start\":0,\"end\":600,\"freq_start\":14,\"freq_end\":10},{\"start\":600,\"end\":1800,\"freq_start\":8,\"freq_end\":7.83}]'. "
            "If provided, overrides --beat-hz."
        ),
    )
    parser.add_argument("--carrier-hz", type=validate_frequency, default=432.0, help="Carrier frequency (0.1-20000 Hz).")
    parser.add_argument("--bed-amplitude", type=validate_percentage, default=0.3, help="Bed amplitude (0.0-1.0, before dB gain).")
    parser.add_argument("--bed-gain-db", type=validate_volume_db, default=-12.0, help="Bed gain applied in final mix (-40 to +10 dB). Default: -12 dB (best practice).")
    parser.add_argument("--voice-gain-db", type=validate_volume_db, default=-6.0, help="Voice gain applied in final mix (-40 to +10 dB). Default: -6 dB (headroom for post-processing).")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: <ssml_dir>/output).")
    parser.add_argument("--voice-out", type=validate_output_path, default=None, help="Override voice output path.")
    parser.add_argument("--bed-out", type=validate_output_path, default=None, help="Override binaural bed output path.")
    parser.add_argument("--mix-out", type=validate_output_path, default=None, help="If set, export final mix MP3 to this path.")
    parser.add_argument("--sfx-path", default=None, help="Optional sound-effect file to overlay onto the bed.")
    parser.add_argument("--sfx-at-sec", type=float, default=0.0, help="Position for the sfx in seconds.")
    parser.add_argument("--sfx-gain-db", type=validate_volume_db, default=-6.0, help="Gain (-40 to +10 dB) applied to the sfx before overlay. Default: -6 dB (best practice).")
    parser.add_argument(
        "--sfx-config",
        default=None,
        help=(
            "JSON string or file path with list of ambient layers. "
            "Each item: {\"path\": \"resources/ambience/forest.wav\", \"start_sec\": 0, \"gain_db\": -8, \"loop\": true}."
        ),
    )
    parser.add_argument("--max-bytes", type=int, default=5000, help="Max SSML bytes per chunk (default: 5000).")
    parser.add_argument("--sample-rate", type=int, default=24000, choices=[16000, 22050, 24000, 44100, 48000], help="TTS sample rate Hz (default: 24000).")

    args = parser.parse_args()

    # args.ssml is already a Path from validate_file_exists
    ssml_path = Path(args.ssml).resolve()

    out_dir = Path(args.output_dir) if args.output_dir else ssml_path.parent / "output"
    _ensure_dir(out_dir)

    voice_out = Path(args.voice_out) if args.voice_out else out_dir / "voice.mp3"
    bed_out = Path(args.bed_out) if args.bed_out else out_dir / "binaural.wav"
    mix_out = Path(args.mix_out) if args.mix_out else out_dir / "final_mix.mp3"

    # Step 1: Generate voice
    speaking_rate = args.speaking_rate
    print("\n=== STEP 1: Synthesizing voice track ===")

    def synthesize_current(rate: float):
        # Google Cloud TTS only (Edge TTS removed from production workflow)
        synthesize_ssml_file_chunked(
            ssml_path,
            voice_out,
            voice_name=args.voice,
            speaking_rate=rate,
            pitch=args.pitch,
            max_bytes=args.max_bytes,
            sample_rate_hz=args.sample_rate,
        )

    synthesize_current(speaking_rate)
    voice_duration = _audio_duration_seconds(voice_out)

    # Optional: adjust speaking rate toward target duration
    if args.target_minutes and args.match_mode == "voice_to_target":
        target_seconds = args.target_minutes * 60

        # Google Cloud TTS respects SSML breaks, so we can adjust speaking rate
        adjusted_rate, changed = _maybe_adjust_rate(speaking_rate, voice_duration, target_seconds)
        if changed:
            print(f"\n🔄 Re-synthesizing voice to better match target length ({args.target_minutes} min)")
            print(f"   Current duration: {voice_duration/60:.2f} min; new speaking rate: {adjusted_rate:.3f}")
            speaking_rate = adjusted_rate
            synthesize_current(speaking_rate)
            voice_duration = _audio_duration_seconds(voice_out)

    # Step 2: Build binaural bed to match desired length
    print("\n=== STEP 2: Generating binaural bed ===")
    target_bed_duration = voice_duration
    if args.target_minutes and args.match_mode == "voice_to_target":
        target_bed_duration = max(target_bed_duration, args.target_minutes * 60)

    sections = []
    gamma_bursts = []  # NEW: Support for gamma flash effects

    if args.beat_schedule:
        try:
            raw = Path(args.beat_schedule).read_text() if Path(args.beat_schedule).exists() else args.beat_schedule
            schedule = json.loads(raw)
        except Exception as e:
            print(f"❌ Failed to parse beat schedule '{args.beat_schedule}': {e}")
            sys.exit(1)

        # Extract gamma bursts from fx_timeline if present
        if isinstance(schedule, dict) and 'fx_timeline' in schedule:
            for fx in schedule.get('fx_timeline', []):
                if fx.get('type') == 'gamma_flash' or fx.get('type') == 'gamma_burst':
                    gamma_bursts.append({
                        'time': float(fx.get('time', 0)),
                        'duration': float(fx.get('duration_s', fx.get('duration', 3.0))),
                        'frequency': float(fx.get('freq_hz', fx.get('frequency', 40)))
                    })
                    print(f"   Detected gamma burst: {fx.get('freq_hz', 40)}Hz at {fx.get('time')}s")

            # If schedule is a dict, extract binaural sections from it
            # Check for manifest format: sound_bed.binaural.sections
            if 'sound_bed' in schedule and 'binaural' in schedule.get('sound_bed', {}):
                binaural_config = schedule['sound_bed']['binaural']
                schedule = binaural_config.get('sections', [])
            else:
                # Fallback to old format
                schedule = schedule.get('sections', schedule.get('beat_schedule', []))

        for entry in schedule:
            start = entry.get("start_sec")
            if start is None:
                start = entry.get("start")
            if start is None and entry.get("start_min") is not None:
                start = float(entry["start_min"]) * 60
            start = float(start if start is not None else 0)

            end = entry.get("end_sec")
            if end is None:
                end = entry.get("end")
            if end is None and entry.get("end_min") is not None:
                end = float(entry["end_min"]) * 60
            end = float(end if end is not None else target_bed_duration)

            freq_start = float(entry.get("freq_start", entry.get("offset_hz", entry.get("beat_hz", args.beat_hz))))
            freq_end = float(entry.get("freq_end", freq_start))
            transition = entry.get("transition", "linear")

            sections.append(
                {
                    "start": start,
                    "end": end,
                    "freq_start": freq_start,
                    "freq_end": freq_end,
                    "transition": transition,
                }
            )

        # Ensure sections are ordered and cover the full duration
        sections = sorted(sections, key=lambda s: s["start"])
        if sections:
            if sections[-1]["end"] < target_bed_duration:
                sections[-1]["end"] = target_bed_duration
            if sections[0]["start"] > 0:
                sections.insert(
                    0,
                    {
                        "start": 0,
                        "end": sections[0]["start"],
                        "freq_start": sections[0]["freq_start"],
                        "freq_end": sections[0]["freq_start"],
                        "transition": "linear",
                    },
                )
    else:
        sections = [
            {
                "start": 0,
                "end": target_bed_duration,
                "freq_start": args.beat_hz,
                "freq_end": args.beat_hz,
                "transition": "linear",
            }
        ]

    bed_audio = generate_binaural(
        sections=sections,
        duration_sec=target_bed_duration,
        carrier_freq=args.carrier_hz,
        amplitude=args.bed_amplitude,
        fade_in_sec=2.0,
        fade_out_sec=4.0,
        gamma_bursts=gamma_bursts if gamma_bursts else None,
    )
    save_stem(bed_audio, str(bed_out))
    bed_segment = AudioSegment.from_file(bed_out)

    # Optional SFX overlay onto the bed (supports multiple layers)
    sfx_layers = []
    if args.sfx_path:
        sfx_layers.append(
            {"path": args.sfx_path, "start_sec": args.sfx_at_sec, "gain_db": args.sfx_gain_db, "loop": False}
        )
    if args.sfx_config:
        try:
            raw = Path(args.sfx_config).read_text() if Path(args.sfx_config).exists() else args.sfx_config
            config_layers = json.loads(raw)
            for layer in config_layers:
                sfx_layers.append(
                    {
                        "path": layer["path"],
                        "start_sec": float(layer.get("start_sec", layer.get("start", 0))),
                        "gain_db": float(layer.get("gain_db", 0)),
                        "loop": bool(layer.get("loop", False)),
                    }
                )
        except Exception as e:
            print(f"⚠️  Failed to parse SFX config '{args.sfx_config}': {e}")

    if sfx_layers:
        target_ms = len(bed_segment)
        for layer in sfx_layers:
            try:
                sfx = AudioSegment.from_file(layer["path"]) + layer["gain_db"]
                if layer.get("loop"):
                    # Repeat and trim to cover the full bed duration
                    repeats = (target_ms // len(sfx)) + 1
                    sfx = (sfx * int(repeats))[:target_ms]
                position_ms = max(0, int(layer.get("start_sec", 0) * 1000))
                print(f"Adding SFX {layer['path']} at {position_ms/1000:.2f}s (gain {layer['gain_db']} dB, loop={layer.get('loop', False)})")
                bed_segment = bed_segment.overlay(sfx, position=position_ms)
            except Exception as e:
                print(f"⚠️  Failed to apply SFX '{layer}': {e}")

        bed_segment.export(bed_out, format="wav")

    bed_duration = len(bed_segment) / 1000.0

    # Step 3: Optional final mix
    final_mix_duration = None
    mix_stats = None
    if mix_out:
        print("\n=== STEP 3: Mixing voice + bed ===")
        final_mix_duration = _mix_tracks(
            voice_out,
            bed_out,
            mix_out,
            voice_gain_db=args.voice_gain_db,
            bed_gain_db=args.bed_gain_db,
        )
        mix_stats = _audio_stats(mix_out)

    # Summary JSON
    summary = {
        "voice": str(voice_out),
        "voice_duration_min": round(voice_duration / 60, 3),
        "speaking_rate": round(speaking_rate, 3),
        "voice_pitch_semitones": args.pitch,
        "tts_provider": args.tts_provider,
        "bed": str(bed_out),
        "bed_duration_min": round(bed_duration / 60, 3),
        "bed_settings": {
            "beat_hz": args.beat_hz,
            "carrier_hz": args.carrier_hz,
            "bed_gain_db": args.bed_gain_db,
            "sections": sections,
        },
        "mix": str(mix_out) if mix_out else None,
        "mix_duration_min": round((final_mix_duration or 0) / 60, 3) if mix_out else None,
        "mix_stats": mix_stats,
        "sfx": str(args.sfx_path) if args.sfx_path else None,
        "sfx_at_sec": args.sfx_at_sec if args.sfx_path else None,
        "sfx_gain_db": args.sfx_gain_db if args.sfx_path else None,
        "sfx_layers": sfx_layers if sfx_layers else None,
    }
    with open(out_dir / "audio_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 70)
    print("✅ Session audio generation complete")
    print("=" * 70)
    print(f"Voice: {voice_out} ({voice_duration/60:.2f} min @ rate {speaking_rate:.3f})")
    print(f"Binaural bed: {bed_out} ({bed_duration/60:.2f} min, {args.beat_hz} Hz on {args.carrier_hz} Hz carrier)")
    if mix_out:
        print(f"Mix: {mix_out} ({(final_mix_duration or 0)/60:.2f} min, voice ref)")
        if mix_stats:
            print(f"Mix peak: {mix_stats['peak_dbfs']:.1f} dBFS, RMS: {mix_stats['rms_dbfs']:.1f} dBFS")
    print(f"Summary: {out_dir/'audio_summary.json'}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
