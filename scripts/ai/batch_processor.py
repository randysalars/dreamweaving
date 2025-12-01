#!/usr/bin/env python3
"""
Batch Processor for Dreamweaving

Process multiple sessions in a single command with parallel or sequential execution.

Usage:
    # Process all sessions
    python3 scripts/ai/batch_processor.py --all

    # Process specific sessions
    python3 scripts/ai/batch_processor.py sessions/session1 sessions/session2

    # Parallel processing (faster but more resource intensive)
    python3 scripts/ai/batch_processor.py --all --parallel --max-workers 2

    # Audio only for all sessions
    python3 scripts/ai/batch_processor.py --all --audio-only

    # Dry run (show what would be processed)
    python3 scripts/ai/batch_processor.py --all --dry-run
"""

import os
import sys
import argparse
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import subprocess
import time


class BatchResult:
    """Result of processing a single session."""

    def __init__(self, session_name: str):
        self.session_name = session_name
        self.status = "pending"
        self.start_time = None
        self.end_time = None
        self.error = None
        self.output = None

    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> Dict:
        return {
            "session": self.session_name,
            "status": self.status,
            "duration_seconds": round(self.duration, 1) if self.duration else None,
            "error": self.error,
        }


class BatchProcessor:
    """Process multiple sessions."""

    def __init__(
        self,
        sessions: List[Path],
        parallel: bool = False,
        max_workers: int = 2,
        audio_only: bool = False,
        headless: bool = True,
        skip_validation: bool = False,
        verbose: bool = True,
    ):
        self.sessions = sessions
        self.parallel = parallel
        self.max_workers = max_workers
        self.audio_only = audio_only
        self.headless = headless
        self.skip_validation = skip_validation
        self.verbose = verbose

        self.results: List[BatchResult] = []
        self.start_time = None
        self.end_time = None

    def log(self, message: str):
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    def process_session(self, session_path: Path) -> BatchResult:
        """Process a single session."""
        result = BatchResult(session_path.name)
        result.start_time = datetime.now()

        try:
            # Build command
            cmd = [
                "python3",
                "scripts/ai/pipeline.py",
                str(session_path),
            ]

            if self.headless:
                cmd.append("--headless")
            if self.audio_only:
                cmd.append("--audio-only")
            if self.skip_validation:
                cmd.append("--skip-validation")
            cmd.append("--quiet")

            self.log(f"Processing: {session_path.name}")

            # Run pipeline
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent.parent),
                timeout=1800,  # 30 minute timeout per session
            )

            result.end_time = datetime.now()

            if proc.returncode == 0:
                result.status = "completed"
                result.output = proc.stdout
                self.log(f"  Completed: {session_path.name} ({result.duration:.1f}s)")
            else:
                result.status = "failed"
                result.error = proc.stderr or proc.stdout
                self.log(f"  Failed: {session_path.name}")

        except subprocess.TimeoutExpired:
            result.status = "timeout"
            result.error = "Processing timed out after 30 minutes"
            result.end_time = datetime.now()
            self.log(f"  Timeout: {session_path.name}")

        except Exception as e:
            result.status = "error"
            result.error = str(e)
            result.end_time = datetime.now()
            self.log(f"  Error: {session_path.name} - {e}")

        return result

    def run(self) -> Dict:
        """Run batch processing."""
        self.start_time = datetime.now()
        self.log(f"Starting batch processing of {len(self.sessions)} sessions")
        self.log(f"Mode: {'parallel' if self.parallel else 'sequential'}")

        if self.parallel:
            self._run_parallel()
        else:
            self._run_sequential()

        self.end_time = datetime.now()

        return self._generate_report()

    def _run_sequential(self):
        """Process sessions one at a time."""
        for session_path in self.sessions:
            result = self.process_session(session_path)
            self.results.append(result)

    def _run_parallel(self):
        """Process sessions in parallel."""
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_session = {
                executor.submit(self.process_session, session): session
                for session in self.sessions
            }

            for future in as_completed(future_to_session):
                result = future.result()
                self.results.append(result)

    def _generate_report(self) -> Dict:
        """Generate batch processing report."""
        total_duration = (self.end_time - self.start_time).total_seconds()

        completed = [r for r in self.results if r.status == "completed"]
        failed = [r for r in self.results if r.status in ["failed", "error", "timeout"]]

        return {
            "timestamp": self.start_time.isoformat(),
            "total_sessions": len(self.sessions),
            "completed": len(completed),
            "failed": len(failed),
            "total_duration_seconds": round(total_duration, 1),
            "average_duration_seconds": round(
                sum(r.duration or 0 for r in self.results) / len(self.results), 1
            ) if self.results else 0,
            "parallel": self.parallel,
            "max_workers": self.max_workers if self.parallel else 1,
            "results": [r.to_dict() for r in self.results],
        }

    def print_summary(self, report: Dict):
        """Print batch summary."""
        print(f"\n{'='*60}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total sessions: {report['total_sessions']}")
        print(f"Completed: {report['completed']}")
        print(f"Failed: {report['failed']}")
        print(f"Total time: {report['total_duration_seconds']:.1f}s")
        print(f"Average per session: {report['average_duration_seconds']:.1f}s")

        if report['failed'] > 0:
            print(f"\n--- FAILED SESSIONS ---")
            for result in report['results']:
                if result['status'] != 'completed':
                    print(f"  {result['session']}: {result['status']}")
                    if result.get('error'):
                        print(f"    Error: {result['error'][:100]}...")


def find_all_sessions(sessions_dir: Path) -> List[Path]:
    """Find all valid session directories."""
    sessions = []

    if not sessions_dir.exists():
        return sessions

    for item in sessions_dir.iterdir():
        if item.is_dir():
            # Check if it has a manifest
            manifest_path = item / "manifest.yaml"
            if manifest_path.exists():
                sessions.append(item)

    return sorted(sessions)


def filter_sessions(
    sessions: List[Path],
    status: Optional[str] = None,
    theme: Optional[str] = None,
) -> List[Path]:
    """Filter sessions by criteria."""
    filtered = []

    for session in sessions:
        manifest_path = session / "manifest.yaml"
        if not manifest_path.exists():
            continue

        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)

        # Filter by theme
        if theme and manifest.get('theme', '').lower() != theme.lower():
            continue

        # Filter by completion status
        if status == "incomplete":
            final_audio = session / "output" / "final.mp3"
            if final_audio.exists():
                continue
        elif status == "complete":
            final_audio = session / "output" / "final.mp3"
            if not final_audio.exists():
                continue

        filtered.append(session)

    return filtered


def main():
    parser = argparse.ArgumentParser(description='Batch process multiple sessions')
    parser.add_argument('sessions', nargs='*', help='Session paths to process')
    parser.add_argument('--all', action='store_true',
                       help='Process all sessions in sessions/ directory')
    parser.add_argument('--parallel', action='store_true',
                       help='Process sessions in parallel')
    parser.add_argument('--max-workers', type=int, default=2,
                       help='Maximum parallel workers (default: 2)')
    parser.add_argument('--audio-only', action='store_true',
                       help='Skip video stages')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip validation stage')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be processed without running')
    parser.add_argument('--status', choices=['complete', 'incomplete'],
                       help='Filter sessions by completion status')
    parser.add_argument('--theme', help='Filter sessions by theme')
    parser.add_argument('--output', help='Output path for batch report')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output')
    args = parser.parse_args()

    # Determine sessions to process
    if args.all:
        sessions_dir = Path("sessions")
        sessions = find_all_sessions(sessions_dir)
    elif args.sessions:
        sessions = [Path(s) for s in args.sessions]
    else:
        print("Error: Specify session paths or use --all")
        sys.exit(1)

    # Apply filters
    if args.status or args.theme:
        sessions = filter_sessions(sessions, status=args.status, theme=args.theme)

    # Validate sessions exist
    valid_sessions = []
    for session in sessions:
        if session.exists():
            valid_sessions.append(session)
        else:
            print(f"Warning: Session not found: {session}")

    if not valid_sessions:
        print("No valid sessions to process")
        sys.exit(1)

    # Dry run
    if args.dry_run:
        print(f"\nWould process {len(valid_sessions)} sessions:")
        for session in valid_sessions:
            print(f"  - {session.name}")
        sys.exit(0)

    # Run batch processing
    processor = BatchProcessor(
        sessions=valid_sessions,
        parallel=args.parallel,
        max_workers=args.max_workers,
        audio_only=args.audio_only,
        skip_validation=args.skip_validation,
        verbose=not args.quiet,
    )

    report = processor.run()
    processor.print_summary(report)

    # Save report
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("knowledge") / "batch_reports" / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)
    print(f"\nReport saved to: {output_path}")

    # Exit with appropriate code
    sys.exit(0 if report['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
