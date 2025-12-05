#!/usr/bin/env python3
"""
Full Pipeline Orchestrator for Dreamweaving AI OS

Orchestrates the complete session production pipeline:
1. Validate inputs (manifest, SSML)
2. Generate voice audio
3. Generate/mix audio layers
4. Master final audio
5. Generate VTT subtitles
6. Generate Midjourney prompts
7. Assemble video (when images available)
8. Package for YouTube
9. Run quality scoring

Usage:
    # Full pipeline
    python3 scripts/ai/pipeline.py sessions/{session}

    # Audio only (no video)
    python3 scripts/ai/pipeline.py sessions/{session} --audio-only

    # Skip validation (for debugging)
    python3 scripts/ai/pipeline.py sessions/{session} --skip-validation

    # Headless mode (no prompts)
    python3 scripts/ai/pipeline.py sessions/{session} --headless
"""

import os
import sys
import yaml
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time


class PipelineStage:
    """Represents a pipeline stage with status tracking."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "pending"  # pending, running, completed, failed, skipped
        self.start_time = None
        self.end_time = None
        self.error = None
        self.output = None

    def start(self):
        self.status = "running"
        self.start_time = datetime.now()

    def complete(self, output=None):
        self.status = "completed"
        self.end_time = datetime.now()
        self.output = output

    def fail(self, error: str):
        self.status = "failed"
        self.end_time = datetime.now()
        self.error = error

    def skip(self, reason: str = ""):
        self.status = "skipped"
        self.error = reason

    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class Pipeline:
    """Full production pipeline orchestrator."""

    def __init__(
        self,
        session_path: Path,
        headless: bool = False,
        skip_validation: bool = False,
        audio_only: bool = False,
        verbose: bool = True,
    ):
        self.session_path = session_path
        self.headless = headless
        self.skip_validation = skip_validation
        self.audio_only = audio_only
        self.verbose = verbose

        self.stages: List[PipelineStage] = []
        self.manifest = None
        self.start_time = None
        self.end_time = None

        self._setup_stages()

    def _setup_stages(self):
        """Initialize pipeline stages."""
        self.stages = [
            PipelineStage("validate", "Validate manifest and SSML"),
            PipelineStage("voice", "Generate voice audio"),
            PipelineStage("binaural", "Generate binaural beats"),
            PipelineStage("background", "Process background audio"),
            PipelineStage("mix", "Mix audio layers"),
            PipelineStage("master", "Master final audio"),
            PipelineStage("vtt", "Generate VTT subtitles"),
            PipelineStage("prompts", "Generate Midjourney prompts"),
            PipelineStage("video", "Assemble video"),
            PipelineStage("package", "Create YouTube package"),
            PipelineStage("quality", "Score quality"),
        ]

    def log(self, message: str, level: str = "info"):
        """Log a message."""
        if self.verbose or level in ["error", "warning"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = {
                "info": "",
                "success": "  ",
                "warning": "  ",
                "error": "  ",
            }.get(level, "")
            print(f"[{timestamp}] {prefix}{message}")

    def run(self) -> Dict:
        """Run the full pipeline."""
        self.start_time = datetime.now()
        self.log(f"Starting pipeline for: {self.session_path.name}")

        try:
            # Load manifest first
            self._load_manifest()

            # Run each stage
            for stage in self.stages:
                if self._should_skip_stage(stage):
                    continue

                self.log(f"\n--- {stage.description} ---")
                stage.start()

                try:
                    result = self._run_stage(stage)
                    stage.complete(result)
                    self.log(f"Completed: {stage.name} ({stage.duration:.1f}s)", "success")

                except Exception as e:
                    stage.fail(str(e))
                    self.log(f"Failed: {stage.name} - {e}", "error")

                    # Decide whether to continue or abort
                    if stage.name in ["validate", "voice"]:
                        self.log("Critical stage failed, aborting pipeline", "error")
                        break

        except Exception as e:
            self.log(f"Pipeline error: {e}", "error")

        self.end_time = datetime.now()

        # Generate report
        report = self._generate_report()
        self._save_report(report)

        return report

    def _load_manifest(self):
        """Load session manifest."""
        manifest_path = self.session_path / "manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                self.manifest = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"No manifest.yaml found in {self.session_path}")

    def _should_skip_stage(self, stage: PipelineStage) -> bool:
        """Determine if a stage should be skipped."""
        if stage.name == "validate" and self.skip_validation:
            stage.skip("Validation skipped by flag")
            return True

        if stage.name in ["video", "package"] and self.audio_only:
            stage.skip("Audio-only mode")
            return True

        # Skip video if no images
        if stage.name == "video":
            # Support both canonical sessions/images/uploaded and legacy images_uploaded
            candidate_dirs = [
                self.session_path / "images" / "uploaded",
                self.session_path / "images_uploaded",
            ]
            images_dir = next((d for d in candidate_dirs if d.exists()), None)
            if not images_dir or not list(images_dir.glob("*.png")):
                stage.skip("No images available")
                return True

        return False

    def _run_stage(self, stage: PipelineStage):
        """Run a specific pipeline stage."""
        stage_methods = {
            "validate": self._stage_validate,
            "voice": self._stage_voice,
            "binaural": self._stage_binaural,
            "background": self._stage_background,
            "mix": self._stage_mix,
            "master": self._stage_master,
            "vtt": self._stage_vtt,
            "prompts": self._stage_prompts,
            "video": self._stage_video,
            "package": self._stage_package,
            "quality": self._stage_quality,
        }

        method = stage_methods.get(stage.name)
        if method:
            return method()
        else:
            raise NotImplementedError(f"Stage not implemented: {stage.name}")

    def _run_script(self, script_path: str, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a Python script."""
        cmd = ["python3", script_path] + args
        self.log(f"  Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)  # Project root
        )

        if check and result.returncode != 0:
            raise RuntimeError(f"Script failed: {result.stderr}")

        return result

    def _stage_validate(self):
        """Validate manifest and SSML."""
        # Validate SSML
        ssml_path = self.session_path / "working_files" / "script.ssml"
        if ssml_path.exists():
            result = self._run_script(
                "scripts/utilities/validate_ssml.py",
                [str(ssml_path)]
            )
            self.log(f"  SSML valid")
        else:
            raise FileNotFoundError("No SSML script found")

        # Validate manifest
        if self.manifest:
            required = ["title", "description", "voice"]
            missing = [f for f in required if f not in self.manifest]
            if missing:
                raise ValueError(f"Missing manifest fields: {missing}")
            self.log(f"  Manifest valid")

        return {"ssml": str(ssml_path), "manifest": "valid"}

    def _stage_voice(self):
        """Generate voice audio."""
        ssml_path = self.session_path / "working_files" / "script.ssml"
        output_path = self.session_path / "output" / "voice.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        voice_id = self.manifest.get("voice", {}).get("id", "en-US-Neural2-A")

        result = self._run_script(
            "scripts/core/generate_audio_chunked.py",
            [str(ssml_path), str(output_path), voice_id]
        )

        return {"voice_file": str(output_path)}

    def _stage_binaural(self):
        """Generate binaural beats."""
        output_path = self.session_path / "output" / "binaural.mp3"

        # Get duration from voice or manifest
        voice_path = self.session_path / "output" / "voice.mp3"
        duration = self._get_audio_duration(voice_path)

        if not duration:
            duration = self.manifest.get("duration", 30) * 60

        binaural_config = self.manifest.get("audio", {}).get("binaural", {})
        base_freq = binaural_config.get("base_frequency", 200)
        beat_freq = binaural_config.get("beat_frequency", 4)

        result = self._run_script(
            "scripts/core/generate_binaural.py",
            [
                str(output_path),
                str(int(duration)),
                str(base_freq),
                str(beat_freq)
            ]
        )

        return {"binaural_file": str(output_path)}

    def _stage_background(self):
        """Process background audio."""
        # This stage prepares/selects background audio
        bg_config = self.manifest.get("audio", {}).get("background", {})

        if not bg_config:
            return {"background": "none configured"}

        # Background audio is typically already in resources/
        # Just verify it exists
        bg_path = bg_config.get("path")
        if bg_path:
            full_path = Path(bg_path)
            if not full_path.exists():
                full_path = Path("resources/background_audio") / bg_path
            if full_path.exists():
                return {"background_file": str(full_path)}

        return {"background": "not found"}

    def _stage_mix(self):
        """Mix all audio layers."""
        output_path = self.session_path / "output" / "mixed.mp3"

        result = self._run_script(
            "scripts/core/generate_session_audio.py",
            [str(self.session_path)]
        )

        return {"mixed_file": str(output_path)}

    def _stage_master(self):
        """Master final audio."""
        input_path = self.session_path / "output" / "mixed.mp3"
        output_path = self.session_path / "output" / "final.mp3"

        if not input_path.exists():
            input_path = self.session_path / "output" / "voice.mp3"

        # Mastering is often done as part of the mix script
        # This is a placeholder for dedicated mastering
        if output_path.exists():
            return {"final_file": str(output_path)}

        return {"master": "completed in mix stage"}

    def _stage_vtt(self):
        """Generate VTT subtitles."""
        result = self._run_script(
            "scripts/ai/vtt_generator.py",
            [str(self.session_path)]
        )

        vtt_path = self.session_path / "output" / "subtitles.vtt"
        return {"vtt_file": str(vtt_path)}

    def _stage_prompts(self):
        """Generate Midjourney prompts."""
        result = self._run_script(
            "scripts/ai/prompt_generator.py",
            [str(self.session_path)]
        )

        prompts_path = self.session_path / "working_files" / "midjourney_prompts.yaml"
        return {"prompts_file": str(prompts_path)}

    def _stage_video(self):
        """Assemble video from images and audio."""
        result = self._run_script(
            "scripts/core/package_youtube.py",
            [str(self.session_path)]
        )

        video_path = self.session_path / "output" / "youtube_package" / "video.mp4"
        return {"video_file": str(video_path)}

    def _stage_package(self):
        """Create YouTube package."""
        youtube_dir = self.session_path / "output" / "youtube_package"
        youtube_dir.mkdir(parents=True, exist_ok=True)

        # Copy/generate necessary files
        files = {
            "video": youtube_dir / "video.mp4",
            "thumbnail": youtube_dir / "thumbnail.png",
            "subtitles": youtube_dir / "subtitles.vtt",
            "description": youtube_dir / "description.txt",
        }

        # Generate description
        description = self._generate_youtube_description()
        with open(files["description"], 'w') as f:
            f.write(description)

        return {"package_dir": str(youtube_dir)}

    def _stage_quality(self):
        """Run quality scoring."""
        result = self._run_script(
            "scripts/ai/quality_scorer.py",
            [str(self.session_path), "--json"],
            check=False
        )

        try:
            score_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            score_data = {"error": "Could not parse quality score"}

        # Save report
        report_path = self.session_path / "working_files" / "quality_report.json"
        with open(report_path, 'w') as f:
            json.dump(score_data, f, indent=2)

        overall = score_data.get("overall_score", "N/A")
        return {"quality_score": overall, "report": str(report_path)}

    def _get_audio_duration(self, audio_path: Path) -> Optional[float]:
        """Get audio duration using ffprobe."""
        if not audio_path.exists():
            return None

        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                 '-of', 'json', str(audio_path)],
                capture_output=True, text=True
            )
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception:
            return None

    def _generate_youtube_description(self) -> str:
        """Generate YouTube video description."""
        title = self.manifest.get("title", "Hypnotic Journey")
        description = self.manifest.get("description", "")

        template = f"""{description}

---

This is a guided hypnotic pathworking session designed for deep relaxation and inner transformation.

For best results:
- Use headphones
- Find a quiet, comfortable space
- Allow yourself to fully relax

---

{title}

#hypnosis #meditation #relaxation #guidedmeditation #sleep
"""
        return template

    def _generate_report(self) -> Dict:
        """Generate pipeline execution report."""
        total_duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        report = {
            "session": self.session_path.name,
            "timestamp": self.start_time.isoformat() if self.start_time else None,
            "total_duration_seconds": round(total_duration, 1),
            "status": "completed" if all(s.status in ["completed", "skipped"] for s in self.stages) else "failed",
            "stages": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration": round(s.duration, 1) if s.duration else None,
                    "error": s.error,
                    "output": s.output,
                }
                for s in self.stages
            ],
        }

        return report

    def _save_report(self, report: Dict):
        """Save execution report."""
        report_path = self.session_path / "working_files" / "pipeline_report.yaml"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)

        self.log(f"\nPipeline report saved to: {report_path}")

    def print_summary(self, report: Dict):
        """Print execution summary."""
        print(f"\n{'='*60}")
        print(f"PIPELINE SUMMARY: {report['session']}")
        print(f"{'='*60}")
        print(f"Status: {report['status'].upper()}")
        print(f"Duration: {report['total_duration_seconds']:.1f}s")

        print(f"\nStages:")
        for stage in report["stages"]:
            status_icon = {
                "completed": "",
                "skipped": "",
                "failed": "",
                "pending": "",
            }.get(stage["status"], "?")

            duration = f"({stage['duration']:.1f}s)" if stage.get("duration") else ""
            error = f" - {stage['error']}" if stage.get("error") and stage["status"] == "failed" else ""

            print(f"  {status_icon} {stage['name']}: {stage['status']} {duration}{error}")


def main():
    parser = argparse.ArgumentParser(description='Run full production pipeline')
    parser.add_argument('session_path', help='Path to session directory')
    parser.add_argument('--headless', action='store_true',
                       help='Run without prompts')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip validation stage')
    parser.add_argument('--audio-only', action='store_true',
                       help='Skip video stages')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output')
    args = parser.parse_args()

    session_path = Path(args.session_path)

    if not session_path.exists():
        print(f"Error: Session path does not exist: {session_path}")
        sys.exit(1)

    pipeline = Pipeline(
        session_path=session_path,
        headless=args.headless,
        skip_validation=args.skip_validation,
        audio_only=args.audio_only,
        verbose=not args.quiet,
    )

    report = pipeline.run()
    pipeline.print_summary(report)

    # Exit with appropriate code
    sys.exit(0 if report["status"] == "completed" else 1)


if __name__ == "__main__":
    main()
