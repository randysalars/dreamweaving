#!/usr/bin/env python3
"""
Thin CLI wrapper for Dreamweaver utilities, suitable for MCP/automation.
Provides stable subcommands that delegate to existing implementations in
scripts/ai/dreamweaver_tools.py without changing core behavior.

Subcommands:
  scaffold           Create a session scaffold (dirs + outline/audio plan/YouTube pkg).
  outline            Generate (and optionally save) a journey outline.
  audio-plan         Generate (and optionally save) an audio plan.
  youtube-package    Generate (and optionally save) a YouTube package.
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is importable when invoked from anywhere
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ai import dreamweaver_tools as dw  # noqa: E402

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback if yaml unavailable
    yaml = None


def _print_json(data):
    print(json.dumps(data, indent=2))


def cmd_scaffold(args):
    result = dw.create_session_scaffold(
        session_name=args.session_name,
        theme=args.theme,
        duration_minutes=args.duration,
        depth_level=args.depth,
        base_path=args.base_path,
    )
    _print_json(result)


def cmd_outline(args):
    outline = dw.generate_journey_outline(
        theme=args.theme,
        duration_minutes=args.duration,
        depth_level=args.depth,
    )
    if args.session:
        path = dw.save_outline(outline, args.session)
        print(path)
    else:
        _print_json(outline.to_dict())


def cmd_audio_plan(args):
    plan = dw.suggest_audio_bed(
        target_state=args.target_state,
        duration_minutes=args.duration,
        environment=args.environment,
    )
    if args.session:
        path = dw.save_audio_plan(plan, args.session)
        print(path)
    else:
        _print_json(plan.to_dict())


def cmd_youtube_package(args):
    manifest = None
    if args.manifest:
        manifest_path = Path(args.manifest)
        if manifest_path.exists():
            text = manifest_path.read_text()
            if manifest_path.suffix.lower() in {".yaml", ".yml"} and yaml:
                manifest = yaml.safe_load(text)
            else:
                manifest = json.loads(text)
    package = dw.generate_youtube_package(args.session, manifest)
    if args.session:
        path = dw.save_youtube_package(package, args.session)
        print(path)
    else:
        _print_json(package)


def build_parser():
    parser = argparse.ArgumentParser(description="Dreamweaver MCP-friendly CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    scaffold = sub.add_parser("scaffold", help="Create session scaffold with defaults")
    scaffold.add_argument("session_name", help="Session slug (kebab-case)")
    scaffold.add_argument("theme", help="Theme/title for the session")
    scaffold.add_argument("--duration", type=int, default=30, help="Target duration (minutes)")
    scaffold.add_argument("--depth", default="Layer2", help="Depth level (Layer1|Layer2|Layer3|Ipsissimus)")
    scaffold.add_argument("--base-path", default="sessions", help="Base sessions directory")
    scaffold.set_defaults(func=cmd_scaffold)

    outline = sub.add_parser("outline", help="Generate journey outline")
    outline.add_argument("theme", help="Theme/title for the session")
    outline.add_argument("--duration", type=int, default=30, help="Target duration (minutes)")
    outline.add_argument("--depth", default="Layer2", help="Depth level (Layer1|Layer2|Layer3|Ipsissimus)")
    outline.add_argument("--session", help="Session directory to save outline.json")
    outline.set_defaults(func=cmd_outline)

    audio_plan = sub.add_parser("audio-plan", help="Generate audio plan")
    audio_plan.add_argument("--target-state", default="trance", choices=["relaxation", "trance", "deep_trance", "integration"], help="Target brainwave state")
    audio_plan.add_argument("--duration", type=int, default=30, help="Target duration (minutes)")
    audio_plan.add_argument("--environment", default="sacred_space", help="Ambience environment preset")
    audio_plan.add_argument("--session", help="Session directory to save working_files/audio_plan.json")
    audio_plan.set_defaults(func=cmd_audio_plan)

    yt = sub.add_parser("youtube-package", help="Generate YouTube package")
    yt.add_argument("session", help="Session directory (used for defaults and save path)")
    yt.add_argument("--manifest", help="Optional manifest JSON path (if already materialized)")
    yt.set_defaults(func=cmd_youtube_package)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
