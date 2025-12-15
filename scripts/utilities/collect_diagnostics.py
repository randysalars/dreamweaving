#!/usr/bin/env python3
"""
Diagnostic Collector - Bundles all context needed to debug a session failure.

Creates a comprehensive diagnostic bundle for a specific session, collecting:
- Manifest and script contents
- Log files and error traces
- Audio file metadata
- Directory structure
- Environment snapshot
- Git diff for session files
- Knowledge base recommendations

Usage:
    python3 scripts/utilities/collect_diagnostics.py sessions/{session}
    python3 scripts/utilities/collect_diagnostics.py sessions/{session} --output ./diagnostics/
    python3 scripts/utilities/collect_diagnostics.py sessions/{session} --json
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_session_path(session_arg: str) -> Path:
    """Convert session argument to full path."""
    if session_arg.startswith("sessions/"):
        return PROJECT_ROOT / session_arg
    return PROJECT_ROOT / "sessions" / session_arg


def collect_file_content(file_path: Path, max_lines: int = 200) -> Dict[str, Any]:
    """Collect file content with metadata."""
    result = {
        "exists": file_path.exists(),
        "path": str(file_path.relative_to(PROJECT_ROOT)) if file_path.exists() else str(file_path),
    }

    if not file_path.exists():
        return result

    stat = file_path.stat()
    result["size_bytes"] = stat.st_size
    result["modified"] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

    # Read text content
    if file_path.suffix in [".yaml", ".yml", ".json", ".ssml", ".xml", ".md", ".txt", ".log"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                if len(lines) > max_lines:
                    result["content"] = "".join(lines[:max_lines])
                    result["truncated"] = True
                    result["total_lines"] = len(lines)
                else:
                    result["content"] = "".join(lines)
                    result["truncated"] = False
        except Exception as e:
            result["read_error"] = str(e)

    return result


def collect_audio_metadata(file_path: Path) -> Dict[str, Any]:
    """Collect audio file metadata using ffprobe."""
    result = {
        "exists": file_path.exists(),
        "path": str(file_path.relative_to(PROJECT_ROOT)) if file_path.exists() else str(file_path),
    }

    if not file_path.exists():
        return result

    stat = file_path.stat()
    result["size_bytes"] = stat.st_size
    result["size_mb"] = round(stat.st_size / (1024 * 1024), 2)

    # Get ffprobe metadata
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode == 0:
            result["ffprobe"] = json.loads(proc.stdout)
        else:
            result["ffprobe_error"] = proc.stderr
    except FileNotFoundError:
        result["ffprobe_error"] = "ffprobe not found"
    except subprocess.TimeoutExpired:
        result["ffprobe_error"] = "ffprobe timed out"
    except Exception as e:
        result["ffprobe_error"] = str(e)

    return result


def collect_directory_structure(dir_path: Path, max_depth: int = 3) -> Dict[str, Any]:
    """Collect directory structure listing."""
    result = {
        "path": str(dir_path.relative_to(PROJECT_ROOT)) if dir_path.exists() else str(dir_path),
        "exists": dir_path.exists(),
    }

    if not dir_path.exists():
        return result

    files = []
    for root, dirs, filenames in os.walk(dir_path):
        root_path = Path(root)
        depth = len(root_path.relative_to(dir_path).parts)
        if depth > max_depth:
            dirs.clear()  # Stop recursion
            continue

        for filename in filenames:
            file_path = root_path / filename
            rel_path = file_path.relative_to(dir_path)
            stat = file_path.stat()
            files.append({
                "path": str(rel_path),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            })

    result["files"] = sorted(files, key=lambda x: x["path"])
    result["total_files"] = len(files)

    return result


def collect_git_info(session_path: Path) -> Dict[str, Any]:
    """Collect git information for session files."""
    result = {}

    try:
        # Check if git is available
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        result["error"] = "git not available"
        return result

    # Get git status for session
    try:
        rel_path = session_path.relative_to(PROJECT_ROOT)
        cmd = ["git", "status", "--porcelain", str(rel_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=10)
        if proc.returncode == 0:
            result["status"] = proc.stdout.strip().split("\n") if proc.stdout.strip() else []
        else:
            result["status_error"] = proc.stderr
    except Exception as e:
        result["status_error"] = str(e)

    # Get recent commits affecting session
    try:
        rel_path = session_path.relative_to(PROJECT_ROOT)
        cmd = ["git", "log", "--oneline", "-5", "--", str(rel_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=10)
        if proc.returncode == 0:
            result["recent_commits"] = proc.stdout.strip().split("\n") if proc.stdout.strip() else []
        else:
            result["commits_error"] = proc.stderr
    except Exception as e:
        result["commits_error"] = str(e)

    # Get diff for uncommitted changes
    try:
        rel_path = session_path.relative_to(PROJECT_ROOT)
        cmd = ["git", "diff", "--stat", str(rel_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=10)
        if proc.returncode == 0 and proc.stdout.strip():
            result["uncommitted_diff"] = proc.stdout.strip()
    except Exception as e:
        result["diff_error"] = str(e)

    return result


def collect_environment_snapshot() -> Dict[str, Any]:
    """Collect environment information."""
    result = {}

    # Python info
    result["python_version"] = sys.version
    result["python_executable"] = sys.executable

    # Check venv
    result["in_venv"] = sys.prefix != sys.base_prefix
    if result["in_venv"]:
        result["venv_path"] = sys.prefix

    # Environment variables (names only, not values for security)
    relevant_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT",
        "PATH",
        "VIRTUAL_ENV",
        "PYTHONPATH",
        "SALARSU_API_TOKEN",
        "BLOB_READ_WRITE_TOKEN",
        "ELEVEN_API_KEY"
    ]
    result["env_vars_set"] = {
        var: var in os.environ for var in relevant_vars
    }

    # System info
    import platform
    result["platform"] = platform.platform()
    result["machine"] = platform.machine()

    # Disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(PROJECT_ROOT)
        result["disk_space"] = {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "used_percent": round((used / total) * 100, 1)
        }
    except Exception as e:
        result["disk_space_error"] = str(e)

    return result


def collect_audit_trail(session_path: Path) -> Dict[str, Any]:
    """Collect audit log entries for the session."""
    audit_path = session_path / ".audit_log.jsonl"
    result = {
        "exists": audit_path.exists(),
        "path": str(audit_path.relative_to(PROJECT_ROOT)) if audit_path.exists() else None
    }

    if not audit_path.exists():
        return result

    events = []
    try:
        with open(audit_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Return last 50 events
        result["total_events"] = len(events)
        result["recent_events"] = events[-50:] if len(events) > 50 else events

        # Find errors
        errors = [e for e in events if e.get("event_type") == "error_occurred"]
        result["error_count"] = len(errors)
        result["recent_errors"] = errors[-10:] if errors else []

    except Exception as e:
        result["read_error"] = str(e)

    return result


def suggest_knowledge_refs(manifest_path: Path) -> List[str]:
    """Suggest relevant knowledge base entries based on manifest."""
    suggestions = []

    if not manifest_path.exists():
        suggestions.append("audio_production_methodology")
        suggestions.append("script_production_workflow")
        return suggestions

    try:
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)

        session_data = manifest.get("session", {})

        # Based on outcome
        outcome = session_data.get("desired_outcome", "")
        if "healing" in outcome.lower():
            suggestions.append("knowledge/outcome_registry.yaml")
        if "transformation" in outcome.lower():
            suggestions.append("knowledge/archetypes.yaml")

        # Always suggest core memories
        suggestions.extend([
            "audio_production_methodology",
            "script_production_workflow",
            "production_workflow_stages",
        ])

        # Based on theme/title
        title = session_data.get("title", "")
        if any(word in title.lower() for word in ["eden", "garden", "nature"]):
            suggestions.append("knowledge/environments/")
        if any(word in title.lower() for word in ["christian", "christ", "divine"]):
            suggestions.append("knowledge/traditions/")

    except Exception:
        suggestions = [
            "audio_production_methodology",
            "script_production_workflow",
        ]

    return list(dict.fromkeys(suggestions))  # Remove duplicates preserving order


def collect_session_diagnostics(session_path: Path) -> Dict[str, Any]:
    """Collect all diagnostics for a session."""
    session_name = session_path.name

    diagnostics = {
        "meta": {
            "session": session_name,
            "session_path": str(session_path.relative_to(PROJECT_ROOT)),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "collector_version": "1.0.0"
        }
    }

    # 1. Manifest
    manifest_path = session_path / "manifest.yaml"
    diagnostics["manifest"] = collect_file_content(manifest_path)

    # 2. Scripts
    working_files = session_path / "working_files"
    diagnostics["scripts"] = {
        "production": collect_file_content(working_files / "script_production.ssml"),
        "voice_clean": collect_file_content(working_files / "script_voice_clean.ssml"),
        "script": collect_file_content(working_files / "script.ssml"),
    }

    # 3. Audio files
    output_dir = session_path / "output"
    audio_files = [
        "voice.mp3",
        "voice_enhanced.mp3",
        "binaural_dynamic.wav",
        "sfx_track.wav",
        "session_mixed.wav",
        f"{session_name}_MASTER.mp3",
    ]
    diagnostics["audio"] = {
        name: collect_audio_metadata(output_dir / name)
        for name in audio_files
    }

    # 4. Directory structure
    diagnostics["directory"] = collect_directory_structure(session_path)

    # 5. Log files
    log_paths = [
        session_path / "build.log",
        session_path / "output" / "build.log",
        session_path / "working_files" / "generation.log",
    ]
    logs = {}
    for log_path in log_paths:
        if log_path.exists():
            logs[log_path.name] = collect_file_content(log_path, max_lines=100)
    diagnostics["logs"] = logs

    # 6. Git info
    diagnostics["git"] = collect_git_info(session_path)

    # 7. Environment
    diagnostics["environment"] = collect_environment_snapshot()

    # 8. Audit trail
    diagnostics["audit"] = collect_audit_trail(session_path)

    # 9. Knowledge recommendations
    diagnostics["knowledge_refs"] = suggest_knowledge_refs(manifest_path)

    # 10. Quick summary
    diagnostics["summary"] = generate_summary(diagnostics)

    return diagnostics


def generate_summary(diagnostics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a quick summary of potential issues."""
    summary = {
        "status": "ok",
        "issues": [],
        "warnings": [],
    }

    # Check manifest
    if not diagnostics.get("manifest", {}).get("exists"):
        summary["issues"].append("Missing manifest.yaml")
        summary["status"] = "error"

    # Check scripts
    scripts = diagnostics.get("scripts", {})
    if not scripts.get("voice_clean", {}).get("exists") and not scripts.get("script", {}).get("exists"):
        summary["issues"].append("No SSML script found")
        summary["status"] = "error"

    # Check audio
    audio = diagnostics.get("audio", {})
    if audio.get("voice_enhanced.mp3", {}).get("exists"):
        ffprobe = audio["voice_enhanced.mp3"].get("ffprobe", {})
        if ffprobe and "format" in ffprobe:
            duration = float(ffprobe["format"].get("duration", 0))
            if duration < 60:
                summary["warnings"].append(f"Voice audio very short: {duration:.1f}s")
    else:
        if audio.get("voice.mp3", {}).get("exists"):
            summary["warnings"].append("Using raw voice.mp3 (voice_enhanced.mp3 missing)")
        else:
            summary["warnings"].append("No voice audio generated yet")

    # Check environment
    env = diagnostics.get("environment", {})
    if not env.get("in_venv"):
        summary["warnings"].append("Not running in virtual environment")

    env_vars = env.get("env_vars_set", {})
    if not env_vars.get("GOOGLE_APPLICATION_CREDENTIALS"):
        summary["warnings"].append("GOOGLE_APPLICATION_CREDENTIALS not set")

    # Check disk space
    disk = env.get("disk_space", {})
    if disk.get("free_gb", 100) < 5:
        summary["issues"].append(f"Low disk space: {disk.get('free_gb', 0):.1f} GB free")
        summary["status"] = "warning" if summary["status"] == "ok" else summary["status"]

    # Check audit trail for recent errors
    audit = diagnostics.get("audit", {})
    if audit.get("error_count", 0) > 0:
        summary["warnings"].append(f"{audit['error_count']} errors in audit log")

    if summary["issues"]:
        summary["status"] = "error"
    elif summary["warnings"] and summary["status"] == "ok":
        summary["status"] = "warning"

    return summary


def format_human_readable(diagnostics: Dict[str, Any]) -> str:
    """Format diagnostics for human reading."""
    lines = []

    meta = diagnostics.get("meta", {})
    lines.append("=" * 70)
    lines.append(f"DIAGNOSTIC REPORT: {meta.get('session', 'unknown')}")
    lines.append(f"Collected: {meta.get('collected_at', 'unknown')}")
    lines.append("=" * 70)

    # Summary
    summary = diagnostics.get("summary", {})
    status = summary.get("status", "unknown").upper()
    lines.append(f"\nSTATUS: {status}")

    if summary.get("issues"):
        lines.append("\nISSUES:")
        for issue in summary["issues"]:
            lines.append(f"  [ERROR] {issue}")

    if summary.get("warnings"):
        lines.append("\nWARNINGS:")
        for warning in summary["warnings"]:
            lines.append(f"  [WARN] {warning}")

    # File existence summary
    lines.append("\nFILE STATUS:")

    manifest = diagnostics.get("manifest", {})
    lines.append(f"  manifest.yaml: {'OK' if manifest.get('exists') else 'MISSING'}")

    scripts = diagnostics.get("scripts", {})
    for name, info in scripts.items():
        if info.get("exists"):
            lines.append(f"  {name}: OK ({info.get('size_bytes', 0)} bytes)")

    audio = diagnostics.get("audio", {})
    for name, info in audio.items():
        if info.get("exists"):
            ffprobe = info.get("ffprobe", {})
            duration = ""
            if ffprobe and "format" in ffprobe:
                dur = float(ffprobe["format"].get("duration", 0))
                duration = f" ({dur:.1f}s)"
            lines.append(f"  {name}: OK{duration}")

    # Environment
    lines.append("\nENVIRONMENT:")
    env = diagnostics.get("environment", {})
    lines.append(f"  Python: {env.get('python_version', 'unknown').split()[0]}")
    lines.append(f"  venv: {'active' if env.get('in_venv') else 'NOT ACTIVE'}")

    disk = env.get("disk_space", {})
    if disk:
        lines.append(f"  Disk free: {disk.get('free_gb', 0):.1f} GB ({100 - disk.get('used_percent', 0):.1f}%)")

    # Knowledge refs
    refs = diagnostics.get("knowledge_refs", [])
    if refs:
        lines.append("\nSUGGESTED KNOWLEDGE:")
        for ref in refs[:5]:
            lines.append(f"  - {ref}")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def save_diagnostic_bundle(diagnostics: Dict[str, Any], output_dir: Path):
    """Save diagnostic bundle to directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = output_dir / "diagnostics.json"
    with open(json_path, "w") as f:
        json.dump(diagnostics, f, indent=2, default=str)

    # Save human-readable summary
    summary_path = output_dir / "summary.txt"
    with open(summary_path, "w") as f:
        f.write(format_human_readable(diagnostics))

    return json_path, summary_path


def main():
    parser = argparse.ArgumentParser(
        description="Collect diagnostic information for a Dreamweaving session"
    )
    parser.add_argument(
        "session",
        help="Session path (e.g., sessions/garden-of-eden or just garden-of-eden)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for diagnostic bundle"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON only"
    )

    args = parser.parse_args()

    # Get session path
    session_path = get_session_path(args.session)

    if not session_path.exists():
        print(f"Error: Session path does not exist: {session_path}", file=sys.stderr)
        sys.exit(1)

    # Collect diagnostics
    diagnostics = collect_session_diagnostics(session_path)

    # Output
    if args.json:
        print(json.dumps(diagnostics, indent=2, default=str))
    elif args.output:
        output_dir = Path(args.output)
        json_path, summary_path = save_diagnostic_bundle(diagnostics, output_dir)
        print(f"Diagnostic bundle saved to:")
        print(f"  JSON: {json_path}")
        print(f"  Summary: {summary_path}")
    else:
        print(format_human_readable(diagnostics))


if __name__ == "__main__":
    main()
