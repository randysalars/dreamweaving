#!/usr/bin/env python3
"""
Session Directory Structure Validator

Validates that session directories follow the standard template structure.
Can also generate a report of structural issues for migration planning.

Usage:
    python3 validate_session_structure.py sessions/my-session
    python3 validate_session_structure.py --all          # Check all sessions
    python3 validate_session_structure.py --report       # Generate migration report
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Standard session directory structure (from _template)
REQUIRED_DIRS = [
    "output",
    "working_files",
    "images",
]

OPTIONAL_DIRS = [
    "variants",
    "final_export",
    "working_files/stems",
    "images/uploaded",
]

REQUIRED_FILES = [
    "manifest.yaml",
]

RECOMMENDED_FILES = [
    "script.ssml",
    "notes.md",
    "README.md",
]

# Non-standard directories that indicate structural issues
NON_STANDARD_DIRS = [
    "biometric",
    "pre_session",
    "micro_sessions",
    "post_session",
    "hardware_optional",
    "sound_effects",
    "gradients",
    "sounds",
    "__pycache__",
]

# Files that should not be in session root (belong in working_files or output)
MISPLACED_PATTERNS = [
    "*.wav",
    "*.mp3",
    "*.mp4",
    "*.json",
    "*.py",  # One-off scripts should be in scripts/ or archived
    "*.sh",  # Shell scripts should be in scripts/ or archived
]


class SessionValidator:
    """Validates session directory structure against template."""

    def __init__(self, session_path: Path):
        self.session_path = session_path
        self.name = session_path.name
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate(self) -> bool:
        """Run all validation checks. Returns True if session is valid."""
        if not self.session_path.exists():
            self.errors.append(f"Session directory does not exist: {self.session_path}")
            return False

        if not self.session_path.is_dir():
            self.errors.append(f"Path is not a directory: {self.session_path}")
            return False

        self._check_required_dirs()
        self._check_required_files()
        self._check_recommended_files()
        self._check_non_standard_dirs()
        self._check_misplaced_files()
        self._check_manifest()

        return len(self.errors) == 0

    def _check_required_dirs(self):
        """Check that required directories exist."""
        for dir_name in REQUIRED_DIRS:
            dir_path = self.session_path / dir_name
            if not dir_path.exists():
                self.errors.append(f"Missing required directory: {dir_name}/")

    def _check_required_files(self):
        """Check that required files exist."""
        for file_name in REQUIRED_FILES:
            file_path = self.session_path / file_name
            if not file_path.exists():
                self.errors.append(f"Missing required file: {file_name}")

    def _check_recommended_files(self):
        """Check for recommended files."""
        for file_name in RECOMMENDED_FILES:
            file_path = self.session_path / file_name
            if not file_path.exists():
                self.warnings.append(f"Missing recommended file: {file_name}")

    def _check_non_standard_dirs(self):
        """Check for non-standard directories."""
        for item in self.session_path.iterdir():
            if item.is_dir() and item.name in NON_STANDARD_DIRS:
                self.warnings.append(
                    f"Non-standard directory: {item.name}/ "
                    f"(consider moving to working_files/ or archiving)"
                )

    def _check_misplaced_files(self):
        """Check for files that should be in subdirectories."""
        import fnmatch

        for item in self.session_path.iterdir():
            if item.is_file():
                for pattern in MISPLACED_PATTERNS:
                    if fnmatch.fnmatch(item.name, pattern):
                        # Special cases
                        if item.name == "manifest.yaml":
                            continue
                        if item.name == "script.ssml":
                            continue
                        if item.name == "notes.md":
                            continue
                        if item.name == "README.md":
                            continue

                        if pattern == "*.py" or pattern == "*.sh":
                            self.warnings.append(
                                f"Script in root: {item.name} "
                                f"(consider moving to scripts/utilities/ or archiving)"
                            )
                        elif pattern in ["*.wav", "*.mp3", "*.mp4"]:
                            self.warnings.append(
                                f"Media file in root: {item.name} "
                                f"(should be in output/ or working_files/)"
                            )
                        else:
                            self.info.append(
                                f"File in root: {item.name} "
                                f"(consider organizing)"
                            )

    def _check_manifest(self):
        """Check manifest.yaml for required fields."""
        manifest_path = self.session_path / "manifest.yaml"
        if not manifest_path.exists():
            return

        try:
            import yaml

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            if not manifest:
                self.errors.append("manifest.yaml is empty")
                return

            # Check required fields
            if "session" not in manifest:
                self.errors.append("manifest.yaml missing 'session' section")
            else:
                session = manifest["session"]
                if "name" not in session:
                    self.errors.append("manifest.yaml missing 'session.name'")
                if "duration" not in session:
                    self.warnings.append("manifest.yaml missing 'session.duration'")

            if "voice" not in manifest:
                self.warnings.append("manifest.yaml missing 'voice' section")

        except ImportError:
            self.info.append("PyYAML not installed, skipping manifest validation")
        except Exception as e:
            self.errors.append(f"Error reading manifest.yaml: {e}")

    def get_report(self) -> str:
        """Generate a formatted validation report."""
        lines = [f"\n{'='*60}", f"Session: {self.name}", f"Path: {self.session_path}", f"{'='*60}"]

        if self.errors:
            lines.append("\n[ERRORS]")
            for err in self.errors:
                lines.append(f"  - {err}")

        if self.warnings:
            lines.append("\n[WARNINGS]")
            for warn in self.warnings:
                lines.append(f"  - {warn}")

        if self.info:
            lines.append("\n[INFO]")
            for info in self.info:
                lines.append(f"  - {info}")

        if not self.errors and not self.warnings and not self.info:
            lines.append("\n[OK] Session structure is valid")

        status = "INVALID" if self.errors else ("WARNINGS" if self.warnings else "VALID")
        lines.append(f"\nStatus: {status}")

        return "\n".join(lines)


def find_sessions(project_root: Path) -> List[Path]:
    """Find all session directories (excluding _template)."""
    sessions_dir = project_root / "sessions"
    if not sessions_dir.exists():
        return []

    return [
        d for d in sessions_dir.iterdir()
        if d.is_dir() and d.name != "_template" and not d.name.startswith(".")
    ]


def get_project_root() -> Path:
    """Find project root (directory containing sessions/)."""
    script_dir = Path(__file__).parent
    # Go up from scripts/utilities/ to project root
    return script_dir.parent.parent


def main():
    parser = argparse.ArgumentParser(
        description="Validate session directory structure"
    )
    parser.add_argument(
        "session",
        nargs="?",
        help="Path to session directory to validate",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all sessions in the project",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed migration report",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show errors, not warnings or info",
    )

    args = parser.parse_args()

    if not args.session and not args.all:
        parser.print_help()
        sys.exit(1)

    project_root = get_project_root()

    if args.all:
        sessions = find_sessions(project_root)
        if not sessions:
            print("No sessions found")
            sys.exit(0)
    else:
        sessions = [Path(args.session).resolve()]

    total_errors = 0
    total_warnings = 0
    results = []

    for session_path in sessions:
        validator = SessionValidator(session_path)
        is_valid = validator.validate()

        if args.quiet:
            if validator.errors:
                print(f"{session_path.name}: INVALID ({len(validator.errors)} errors)")
                for err in validator.errors:
                    print(f"  - {err}")
        else:
            print(validator.get_report())

        total_errors += len(validator.errors)
        total_warnings += len(validator.warnings)
        results.append((session_path.name, validator))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Sessions checked: {len(sessions)}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")

    valid_count = sum(1 for _, v in results if not v.errors)
    print(f"Valid sessions: {valid_count}/{len(sessions)}")

    if args.report:
        print(f"\n{'='*60}")
        print("MIGRATION RECOMMENDATIONS")
        print(f"{'='*60}")
        for name, validator in results:
            if validator.errors or validator.warnings:
                print(f"\n{name}:")
                if validator.errors:
                    print("  Required fixes:")
                    for err in validator.errors:
                        print(f"    - {err}")
                if validator.warnings:
                    print("  Recommended improvements:")
                    for warn in validator.warnings:
                        print(f"    - {warn}")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
