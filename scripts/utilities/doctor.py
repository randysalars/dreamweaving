#!/usr/bin/env python3
"""
Dreamweaving Doctor - Unified Diagnostic Tool

Gathers everything needed for troubleshooting in one command.
Outputs both human-readable and JSON formats.

Usage:
    python3 scripts/utilities/doctor.py              # Full report
    python3 scripts/utilities/doctor.py --quick      # Essential checks only
    python3 scripts/utilities/doctor.py --json       # Machine-readable only
    python3 scripts/utilities/doctor.py --fix        # Auto-fix what's possible
    python3 scripts/utilities/doctor.py --session X  # Include session-specific checks
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DIAGNOSTICS_DIR = PROJECT_ROOT / ".ai" / "diagnostics"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def color(text: str, color_code: str) -> str:
    """Apply color to text if terminal supports it."""
    if sys.stdout.isatty():
        return f"{color_code}{text}{Colors.RESET}"
    return text


def run_command(cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
    """Run a command and return (return_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=PROJECT_ROOT
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -2, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -3, "", str(e)


def check_pass(name: str) -> Dict[str, Any]:
    """Return a passing check result."""
    return {"name": name, "status": "pass", "message": "OK"}


def check_warn(name: str, message: str) -> Dict[str, Any]:
    """Return a warning check result."""
    return {"name": name, "status": "warn", "message": message}


def check_fail(name: str, message: str) -> Dict[str, Any]:
    """Return a failing check result."""
    return {"name": name, "status": "fail", "message": message}


# =============================================================================
# System Checks
# =============================================================================

def check_python_version() -> Dict[str, Any]:
    """Check Python version is 3.8+."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    if version.major >= 3 and version.minor >= 8:
        return check_pass(f"Python {version_str}")
    return check_fail("Python version", f"Need 3.8+, got {version_str}")


def check_venv() -> Dict[str, Any]:
    """Check if running in virtual environment."""
    in_venv = sys.prefix != sys.base_prefix
    venv_path = sys.prefix if in_venv else None
    if in_venv:
        return {**check_pass("Virtual environment"), "venv_path": venv_path}
    return check_warn("Virtual environment", "Not in venv (run: source venv/bin/activate)")


def check_ffmpeg() -> Dict[str, Any]:
    """Check FFmpeg installation and version."""
    code, stdout, stderr = run_command(["ffmpeg", "-version"])
    if code != 0:
        return check_fail("FFmpeg", "Not installed or not in PATH")

    # Extract version
    version_line = stdout.split("\n")[0] if stdout else "unknown"
    return {**check_pass("FFmpeg"), "version": version_line}


def check_ffprobe() -> Dict[str, Any]:
    """Check ffprobe availability."""
    code, _, _ = run_command(["ffprobe", "-version"])
    if code != 0:
        return check_fail("ffprobe", "Not installed or not in PATH")
    return check_pass("ffprobe")


def check_disk_space() -> Dict[str, Any]:
    """Check available disk space."""
    try:
        total, used, free = shutil.disk_usage(PROJECT_ROOT)
        free_gb = free / (1024 ** 3)
        total_gb = total / (1024 ** 3)
        percent_free = (free / total) * 100

        result = {
            "name": "Disk space",
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "percent_free": round(percent_free, 1)
        }

        if free_gb < 1:
            return {**result, "status": "fail", "message": f"Only {free_gb:.1f}GB free"}
        elif free_gb < 5:
            return {**result, "status": "warn", "message": f"{free_gb:.1f}GB free (consider cleanup)"}
        return {**result, "status": "pass", "message": f"{free_gb:.1f}GB free"}
    except Exception as e:
        return check_fail("Disk space", str(e))


def check_google_cloud_auth() -> Dict[str, Any]:
    """Check Google Cloud authentication."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not creds_path:
        return check_warn("Google Cloud auth", "GOOGLE_APPLICATION_CREDENTIALS not set")

    if not Path(creds_path).exists():
        return check_fail("Google Cloud auth", f"Credentials file not found: {creds_path}")

    # Try to validate the credentials
    code, stdout, stderr = run_command(
        ["gcloud", "auth", "application-default", "print-access-token"],
        timeout=10
    )

    if code == 0:
        return check_pass("Google Cloud auth")
    return check_warn("Google Cloud auth", "Credentials set but may not be active")


# =============================================================================
# Project Health Checks
# =============================================================================

def check_required_directories() -> Dict[str, Any]:
    """Check required project directories exist."""
    required = [
        "sessions",
        "scripts/core",
        "scripts/utilities",
        "knowledge",
        ".claude/agents",
        "config"
    ]

    missing = []
    for dir_path in required:
        if not (PROJECT_ROOT / dir_path).exists():
            missing.append(dir_path)

    if missing:
        return check_fail("Project directories", f"Missing: {', '.join(missing)}")
    return check_pass("Project directories")


def check_required_files() -> Dict[str, Any]:
    """Check required files exist."""
    required = [
        "CLAUDE.md",
        "requirements.txt",
        "config/voice_config.yaml"
    ]

    missing = []
    for file_path in required:
        if not (PROJECT_ROOT / file_path).exists():
            missing.append(file_path)

    if missing:
        return check_warn("Required files", f"Missing: {', '.join(missing)}")
    return check_pass("Required files")


def check_env_vars() -> Dict[str, Any]:
    """Check important environment variables (names only, not values)."""
    important_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "NOTION_TOKEN",
        "DREAMWEAVING_LOG_LEVEL"
    ]

    present = []
    missing = []

    for var in important_vars:
        if os.environ.get(var):
            present.append(var)
        else:
            missing.append(var)

    result = {
        "name": "Environment variables",
        "present": present,
        "missing": missing
    }

    if "GOOGLE_APPLICATION_CREDENTIALS" in missing:
        return {**result, "status": "warn", "message": f"Missing: {', '.join(missing)}"}
    return {**result, "status": "pass", "message": f"{len(present)}/{len(important_vars)} set"}


def run_lint_check() -> Dict[str, Any]:
    """Run flake8 and summarize results."""
    code, stdout, stderr = run_command(
        ["flake8", "scripts/", "--count", "--select=E9,F63,F7,F82", "--show-source"],
        timeout=60
    )

    if code == -2:
        return check_warn("Lint check", "flake8 not installed")

    if code == 0:
        return check_pass("Lint check (critical)")

    # Count issues
    lines = stdout.strip().split("\n") if stdout.strip() else []
    issue_count = len([l for l in lines if l and not l.isdigit()])

    return check_warn("Lint check", f"{issue_count} critical issues found")


def check_sessions_health() -> Dict[str, Any]:
    """Quick scan of session directories."""
    sessions_dir = PROJECT_ROOT / "sessions"
    if not sessions_dir.exists():
        return check_fail("Sessions", "sessions/ directory not found")

    sessions = [d for d in sessions_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

    valid = 0
    issues = []

    for session in sessions[:10]:  # Check first 10 only for speed
        manifest = session / "manifest.yaml"
        if manifest.exists():
            valid += 1
        else:
            issues.append(session.name)

    total = len(sessions)
    result = {
        "name": "Sessions health",
        "total_sessions": total,
        "checked": min(10, total),
        "valid": valid
    }

    if issues:
        return {**result, "status": "warn", "message": f"Missing manifest in: {', '.join(issues[:3])}"}
    return {**result, "status": "pass", "message": f"{total} sessions found, {valid} checked OK"}


# =============================================================================
# Git & Recent Activity
# =============================================================================

def get_recent_commits() -> Dict[str, Any]:
    """Get last 5 git commits."""
    code, stdout, stderr = run_command(
        ["git", "log", "--oneline", "-5"],
        timeout=10
    )

    if code != 0:
        return {"name": "Recent commits", "status": "warn", "message": "Not a git repo or git error"}

    commits = stdout.strip().split("\n") if stdout.strip() else []
    return {
        "name": "Recent commits",
        "status": "pass",
        "commits": commits
    }


def get_modified_files() -> Dict[str, Any]:
    """Get files modified in last 24h."""
    code, stdout, stderr = run_command(
        ["git", "diff", "--name-only", "HEAD@{1.day.ago}..HEAD"],
        timeout=10
    )

    if code != 0:
        # Fallback: just get current status
        code, stdout, stderr = run_command(["git", "status", "--short"])
        if code != 0:
            return {"name": "Modified files", "status": "warn", "message": "Could not determine"}

    files = stdout.strip().split("\n") if stdout.strip() else []
    files = [f for f in files if f]  # Remove empty strings

    return {
        "name": "Modified files (24h)",
        "status": "pass",
        "count": len(files),
        "files": files[:10]  # First 10 only
    }


# =============================================================================
# Session-Specific Checks
# =============================================================================

def check_session(session_path: Path) -> Dict[str, Any]:
    """Run detailed checks on a specific session."""
    if not session_path.exists():
        return {"name": f"Session: {session_path.name}", "status": "fail", "message": "Not found"}

    checks = []

    # Check manifest
    manifest = session_path / "manifest.yaml"
    if manifest.exists():
        checks.append(check_pass("manifest.yaml"))
    else:
        checks.append(check_fail("manifest.yaml", "Missing"))

    # Check scripts
    script_prod = session_path / "working_files" / "script_production.ssml"
    script_clean = session_path / "working_files" / "script_voice_clean.ssml"

    if script_prod.exists():
        checks.append(check_pass("script_production.ssml"))
    else:
        checks.append(check_warn("script_production.ssml", "Not found"))

    if script_clean.exists():
        checks.append(check_pass("script_voice_clean.ssml"))
        # Check for SFX markers that shouldn't be there
        content = script_clean.read_text()
        if "[SFX:" in content:
            checks.append(check_warn("SFX markers", "Found in voice_clean.ssml (should be stripped)"))

    # Check output files
    output_dir = session_path / "output"
    if output_dir.exists():
        voice_enhanced = output_dir / "voice_enhanced.mp3"
        master = list(output_dir.glob("*_MASTER.mp3"))

        if voice_enhanced.exists():
            checks.append(check_pass("voice_enhanced.mp3"))

        if master:
            checks.append(check_pass(f"Master audio: {master[0].name}"))

    return {
        "name": f"Session: {session_path.name}",
        "status": "pass" if all(c["status"] == "pass" for c in checks) else "warn",
        "checks": checks
    }


# =============================================================================
# Fix Functions
# =============================================================================

def apply_fixes(results: Dict[str, Any]) -> List[str]:
    """Apply automatic fixes where possible."""
    fixes_applied = []

    # Fix: Create missing directories
    for check in results.get("project_health", []):
        if check.get("name") == "Project directories" and check.get("status") == "fail":
            for dir_path in ["sessions", "scripts/core", "scripts/utilities", "knowledge", ".claude/agents", "config"]:
                full_path = PROJECT_ROOT / dir_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    fixes_applied.append(f"Created directory: {dir_path}")

    # Fix: Install missing packages
    venv_check = next((c for c in results.get("system", []) if "venv" in c.get("name", "").lower()), None)
    if venv_check and venv_check.get("status") == "pass":
        # Only try to install if we're in a venv
        code, _, _ = run_command(["pip", "install", "-q", "-r", "requirements.txt"], timeout=120)
        if code == 0:
            fixes_applied.append("Installed/updated requirements")

    return fixes_applied


# =============================================================================
# Report Generation
# =============================================================================

def generate_report(quick: bool = False, session: Optional[str] = None) -> Dict[str, Any]:
    """Generate full diagnostic report."""
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "system": [],
        "project_health": [],
        "activity": [],
        "session": None,
        "summary": {
            "pass": 0,
            "warn": 0,
            "fail": 0
        }
    }

    # System checks
    report["system"].append(check_python_version())
    report["system"].append(check_venv())
    report["system"].append(check_ffmpeg())
    report["system"].append(check_ffprobe())
    report["system"].append(check_disk_space())
    report["system"].append(check_google_cloud_auth())

    # Project health
    report["project_health"].append(check_required_directories())
    report["project_health"].append(check_required_files())
    report["project_health"].append(check_env_vars())

    if not quick:
        report["project_health"].append(run_lint_check())
        report["project_health"].append(check_sessions_health())

        # Activity
        report["activity"].append(get_recent_commits())
        report["activity"].append(get_modified_files())

    # Session-specific
    if session:
        session_path = PROJECT_ROOT / "sessions" / session
        report["session"] = check_session(session_path)

    # Calculate summary
    all_checks = report["system"] + report["project_health"] + report.get("activity", [])
    if report["session"]:
        all_checks.append(report["session"])

    for check in all_checks:
        status = check.get("status", "pass")
        if status in report["summary"]:
            report["summary"][status] += 1

    return report


def print_human_report(report: Dict[str, Any]) -> None:
    """Print human-readable report to terminal."""
    print()
    print(color("=" * 60, Colors.BLUE))
    print(color("  DREAMWEAVING DOCTOR - DIAGNOSTIC REPORT", Colors.BOLD))
    print(color("=" * 60, Colors.BLUE))
    print(f"  Timestamp: {report['timestamp']}")
    print()

    def print_section(title: str, checks: List[Dict]) -> None:
        print(color(f"\n{title}", Colors.BOLD))
        print("-" * 40)
        for check in checks:
            status = check.get("status", "pass")
            name = check.get("name", "Unknown")
            message = check.get("message", "")

            if status == "pass":
                icon = color("[PASS]", Colors.GREEN)
            elif status == "warn":
                icon = color("[WARN]", Colors.YELLOW)
            else:
                icon = color("[FAIL]", Colors.RED)

            print(f"  {icon} {name}: {message}")

    print_section("System Checks", report.get("system", []))
    print_section("Project Health", report.get("project_health", []))

    if report.get("activity"):
        print_section("Recent Activity", report.get("activity", []))

    if report.get("session"):
        session_data = report["session"]
        print(color(f"\nSession: {session_data.get('name', 'Unknown')}", Colors.BOLD))
        print("-" * 40)
        for check in session_data.get("checks", []):
            status = check.get("status", "pass")
            name = check.get("name", "Unknown")
            message = check.get("message", "")
            icon = color("[PASS]", Colors.GREEN) if status == "pass" else \
                   color("[WARN]", Colors.YELLOW) if status == "warn" else \
                   color("[FAIL]", Colors.RED)
            print(f"  {icon} {name}: {message}")

    # Summary
    summary = report.get("summary", {})
    print()
    print(color("=" * 60, Colors.BLUE))
    total = summary.get("pass", 0) + summary.get("warn", 0) + summary.get("fail", 0)
    print(f"  SUMMARY: {color(str(summary.get('pass', 0)) + ' passed', Colors.GREEN)}, "
          f"{color(str(summary.get('warn', 0)) + ' warnings', Colors.YELLOW)}, "
          f"{color(str(summary.get('fail', 0)) + ' failed', Colors.RED)}")
    print(color("=" * 60, Colors.BLUE))
    print()


def save_report(report: Dict[str, Any]) -> Path:
    """Save report to diagnostics directory."""
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    report_path = DIAGNOSTICS_DIR / f"{timestamp}.json"

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report_path


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Dreamweaving Doctor - Unified Diagnostic Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/utilities/doctor.py              # Full report
  python3 scripts/utilities/doctor.py --quick      # Essential checks only
  python3 scripts/utilities/doctor.py --json       # Machine-readable only
  python3 scripts/utilities/doctor.py --fix        # Auto-fix what's possible
  python3 scripts/utilities/doctor.py --session eden-garden  # Include session checks
        """
    )

    parser.add_argument("--quick", action="store_true", help="Run essential checks only")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix issues")
    parser.add_argument("--session", type=str, help="Include session-specific checks")
    parser.add_argument("--save", action="store_true", help="Save report to .ai/diagnostics/")

    args = parser.parse_args()

    # Generate report
    report = generate_report(quick=args.quick, session=args.session)

    # Apply fixes if requested
    if args.fix:
        fixes = apply_fixes(report)
        report["fixes_applied"] = fixes
        if fixes and not args.json:
            print(color("\nFixes Applied:", Colors.BOLD))
            for fix in fixes:
                print(f"  - {fix}")

    # Output
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_report(report)

    # Save if requested
    if args.save:
        saved_path = save_report(report)
        if not args.json:
            print(f"Report saved to: {saved_path}")

    # Exit code based on results
    if report["summary"]["fail"] > 0:
        sys.exit(1)
    elif report["summary"]["warn"] > 0:
        sys.exit(0)  # Warnings are OK
    sys.exit(0)


if __name__ == "__main__":
    main()
