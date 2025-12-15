#!/usr/bin/env python3
"""
Generation Planner

Creates comprehensive execution plans for video generation pipelines.
Plans include pre-flight checks, resource validation, cost estimation,
risk assessment, and execution roadmaps.

This module is the first stage in both nightly_builder and auto_generate
workflows, ensuring all requirements are met before generation begins.

Usage:
    from scripts.ai.generation_planner import GenerationPlanner

    planner = GenerationPlanner(project_root=Path('/path/to/project'))
    plan = planner.create_plan(
        topic="Finding Inner Peace",
        duration_minutes=30,
        mode="standard",
        image_method="sd",
    )

    if plan.has_blockers():
        print(f"Cannot proceed: {plan.blockers}")
    else:
        plan.save(session_path / "working_files" / "generation_plan.yaml")
"""

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class PreflightCheck:
    """Result of a single pre-flight check."""

    name: str
    passed: bool
    message: str
    is_blocker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "is_blocker": self.is_blocker,
        }


@dataclass
class CostEstimate:
    """Cost estimation for the generation pipeline."""

    total_usd: float
    breakdown: Dict[str, float]  # stage -> cost
    mode: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "total_usd": round(self.total_usd, 4),
            "breakdown": {k: round(v, 4) for k, v in self.breakdown.items()},
        }


@dataclass
class PlannedStage:
    """A single stage in the execution plan."""

    name: str
    description: str
    expected_output: str
    estimated_duration_seconds: int
    dependencies: List[str] = field(default_factory=list)
    can_skip: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "expected_output": self.expected_output,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "dependencies": self.dependencies,
            "can_skip": self.can_skip,
        }


@dataclass
class Risk:
    """A potential risk in the generation pipeline."""

    name: str
    severity: str  # low, medium, high
    likelihood: str  # low, medium, high
    mitigation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "severity": self.severity,
            "likelihood": self.likelihood,
            "mitigation": self.mitigation,
        }


@dataclass
class GenerationPlan:
    """Complete execution plan for video generation."""

    created_at: datetime
    topic: str
    session_name: str
    mode: str
    duration_target: int

    # Pre-flight
    preflight_checks: List[PreflightCheck] = field(default_factory=list)

    # Resources
    resources_validated: bool = False
    resource_warnings: List[str] = field(default_factory=list)

    # Knowledge context
    lessons_applied: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)

    # Cost
    cost_estimate: Optional[CostEstimate] = None

    # Feasibility
    feasibility_score: float = 0.0
    feasibility_notes: List[str] = field(default_factory=list)

    # Execution plan
    stages: List[PlannedStage] = field(default_factory=list)

    # Risks
    risks: List[Risk] = field(default_factory=list)
    fallbacks: Dict[str, str] = field(default_factory=dict)

    # Summary
    blockers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def has_blockers(self) -> bool:
        """Check if there are any blockers preventing execution."""
        return len(self.blockers) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary for YAML serialization."""
        return {
            "meta": {
                "session_name": self.session_name,
                "topic": self.topic,
                "mode": self.mode,
                "duration_target": self.duration_target,
                "created_at": self.created_at.isoformat(),
            },
            "preflight": [c.to_dict() for c in self.preflight_checks],
            "resources": {
                "validated": self.resources_validated,
                "warnings": self.resource_warnings,
            },
            "knowledge_context": {
                "lessons_applied": self.lessons_applied,
                "best_practices": self.best_practices,
            },
            "cost_estimate": self.cost_estimate.to_dict() if self.cost_estimate else {},
            "feasibility": {
                "score": round(self.feasibility_score, 2),
                "notes": self.feasibility_notes,
            },
            "stages": [s.to_dict() for s in self.stages],
            "risks": [r.to_dict() for r in self.risks],
            "fallbacks": self.fallbacks,
            "summary": {
                "blockers": self.blockers,
                "warnings": self.warnings,
                "ready_to_execute": not self.has_blockers(),
                "estimated_total_duration_minutes": self._estimate_total_duration(),
            },
        }

    def _estimate_total_duration(self) -> int:
        """Estimate total duration in minutes."""
        total_seconds = sum(s.estimated_duration_seconds for s in self.stages)
        return max(1, total_seconds // 60)

    def to_yaml(self) -> str:
        """Serialize plan to YAML string."""
        header = f"""# Auto-Generated Execution Plan
# Created: {self.created_at.isoformat()}
# Topic: "{self.topic}"
# Session: {self.session_name}

"""
        return header + yaml.dump(
            self.to_dict(), default_flow_style=False, sort_keys=False, allow_unicode=True
        )

    def save(self, path: Path) -> None:
        """Save plan to YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_yaml(), encoding="utf-8")

    @classmethod
    def from_yaml(cls, path: Path) -> "GenerationPlan":
        """Load plan from YAML file."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        meta = data.get("meta", {})

        plan = cls(
            created_at=datetime.fromisoformat(meta.get("created_at", datetime.now().isoformat())),
            topic=meta.get("topic", ""),
            session_name=meta.get("session_name", ""),
            mode=meta.get("mode", "standard"),
            duration_target=meta.get("duration_target", 30),
        )

        # Preflight
        for check_data in data.get("preflight", []):
            plan.preflight_checks.append(
                PreflightCheck(
                    name=check_data.get("name", ""),
                    passed=check_data.get("passed", False),
                    message=check_data.get("message", ""),
                    is_blocker=check_data.get("is_blocker", False),
                )
            )

        # Resources
        resources = data.get("resources", {})
        plan.resources_validated = resources.get("validated", False)
        plan.resource_warnings = resources.get("warnings", [])

        # Knowledge context
        knowledge = data.get("knowledge_context", {})
        plan.lessons_applied = knowledge.get("lessons_applied", [])
        plan.best_practices = knowledge.get("best_practices", [])

        # Cost estimate
        cost_data = data.get("cost_estimate", {})
        if cost_data:
            plan.cost_estimate = CostEstimate(
                total_usd=cost_data.get("total_usd", 0.0),
                breakdown=cost_data.get("breakdown", {}),
                mode=cost_data.get("mode", "standard"),
            )

        # Feasibility
        feasibility = data.get("feasibility", {})
        plan.feasibility_score = feasibility.get("score", 0.0)
        plan.feasibility_notes = feasibility.get("notes", [])

        # Stages
        for stage_data in data.get("stages", []):
            plan.stages.append(
                PlannedStage(
                    name=stage_data.get("name", ""),
                    description=stage_data.get("description", ""),
                    expected_output=stage_data.get("expected_output", ""),
                    estimated_duration_seconds=stage_data.get("estimated_duration_seconds", 0),
                    dependencies=stage_data.get("dependencies", []),
                    can_skip=stage_data.get("can_skip", False),
                )
            )

        # Risks
        for risk_data in data.get("risks", []):
            plan.risks.append(
                Risk(
                    name=risk_data.get("name", ""),
                    severity=risk_data.get("severity", "low"),
                    likelihood=risk_data.get("likelihood", "low"),
                    mitigation=risk_data.get("mitigation", ""),
                )
            )

        # Fallbacks
        plan.fallbacks = data.get("fallbacks", {})

        # Summary
        summary = data.get("summary", {})
        plan.blockers = summary.get("blockers", [])
        plan.warnings = summary.get("warnings", [])

        return plan


# =============================================================================
# Generation Planner
# =============================================================================


class GenerationPlanner:
    """Creates execution plans for video generation pipelines."""

    # Base costs per operation (USD)
    BASE_COSTS = {
        "manifest_generation": 0.05,
        "script_generation": 0.35,
        "voice_synthesis": 0.15,
        "image_prompts": 0.10,
        "vtt_generation": 0.05,
        "quality_check": 0.05,
        "sd_images": 0.00,  # Local, no API cost
        "pil_images": 0.00,  # Local, no API cost
        "video_assembly": 0.00,
        "mastering": 0.00,
    }

    # Mode multipliers
    MODE_MULTIPLIERS = {
        "budget": 0.65,
        "standard": 1.0,
        "premium": 1.4,
    }

    # Stage definitions with timing estimates (seconds)
    STAGE_DEFINITIONS = [
        ("create_session", "Create directory structure", 2, []),
        ("generate_manifest", "AI-generate session manifest", 30, ["create_session"]),
        ("generate_script", "Generate SSML script via Claude", 120, ["generate_manifest"]),
        ("generate_prompts", "Generate image prompts", 15, ["generate_manifest"]),
        ("generate_voice", "Synthesize voice audio", 180, ["generate_script"]),
        ("generate_binaural", "Generate binaural beats", 30, ["generate_voice"]),
        ("generate_sfx", "Generate sound effects", 20, ["generate_script"]),
        ("mix_audio", "Mix all audio stems", 60, ["generate_voice", "generate_binaural"]),
        ("hypnotic_post_process", "Apply psychoacoustic mastering", 90, ["mix_audio"]),
        ("generate_vtt", "Generate VTT subtitles", 30, ["generate_script"]),
        ("generate_images", "Generate scene images", 600, ["generate_prompts"]),  # SD is slow
        ("assemble_video", "Assemble final video", 120, ["generate_images", "hypnotic_post_process"]),
        ("package_youtube", "Create YouTube package", 30, ["assemble_video"]),
        ("generate_thumbnail", "Generate thumbnail", 45, ["generate_manifest"]),
        ("upload_website", "Upload to website", 60, ["assemble_video"]),
        ("cleanup", "Remove intermediate files", 10, ["upload_website"]),
        ("self_improvement", "Record lessons learned", 15, ["cleanup"]),
    ]

    def __init__(
        self,
        project_root: Optional[Path] = None,
        mode: str = "standard",
    ):
        """Initialize the planner.

        Args:
            project_root: Root directory of the project
            mode: Cost optimization mode (budget, standard, premium)
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.mode = mode
        self.multiplier = self.MODE_MULTIPLIERS.get(mode, 1.0)

    def create_plan(
        self,
        topic: str,
        duration_minutes: int = 30,
        mode: str = "standard",
        image_method: str = "sd",
        audio_only: bool = False,
        session_name: Optional[str] = None,
    ) -> GenerationPlan:
        """Create a complete execution plan.

        Args:
            topic: Session topic
            duration_minutes: Target duration
            mode: Cost optimization mode
            image_method: Image generation method (sd, pil, stock, midjourney)
            audio_only: If True, skip video stages
            session_name: Optional session name (auto-generated if not provided)

        Returns:
            GenerationPlan with all checks, estimates, and roadmap
        """
        # Generate session name if not provided
        if not session_name:
            session_name = self._generate_session_name(topic)

        # Create plan object
        plan = GenerationPlan(
            created_at=datetime.now(),
            topic=topic,
            session_name=session_name,
            mode=mode,
            duration_target=duration_minutes,
        )

        # 1. Pre-flight checks
        plan.preflight_checks = self._run_preflight_checks(image_method)

        # Collect blockers from pre-flight
        for check in plan.preflight_checks:
            if not check.passed and check.is_blocker:
                plan.blockers.append(f"{check.name}: {check.message}")

        # 2. Resource validation
        plan.resources_validated, plan.resource_warnings = self._validate_resources(image_method)
        plan.warnings.extend(plan.resource_warnings)

        # 3. Knowledge base consultation
        plan.lessons_applied, plan.best_practices = self._consult_knowledge_base(topic)

        # 4. Cost estimation
        plan.cost_estimate = self._estimate_costs(mode, image_method, audio_only)

        # 5. Feasibility assessment
        plan.feasibility_score, plan.feasibility_notes = self._assess_feasibility(
            topic, duration_minutes
        )

        # 6. Build execution roadmap
        plan.stages = self._build_execution_roadmap(
            session_name, image_method, audio_only
        )

        # 7. Risk assessment and fallbacks
        plan.risks = self._assess_risks(image_method, audio_only)
        plan.fallbacks = self._define_fallbacks()

        return plan

    def _generate_session_name(self, topic: str) -> str:
        """Generate a kebab-case session name from topic."""
        import re

        name = topic.lower()
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[\s_]+", "-", name)
        name = name.strip("-")[:40]
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{name}-{timestamp}"

    def _run_preflight_checks(self, image_method: str) -> List[PreflightCheck]:
        """Run all pre-flight checks."""
        checks = []

        # Check Claude CLI
        checks.append(self._check_claude_cli())

        # Check Google TTS credentials
        checks.append(self._check_google_tts())

        # Check FFmpeg
        checks.append(self._check_ffmpeg())

        # Check disk space
        checks.append(self._check_disk_space())

        # Check SD model (if using SD)
        if image_method == "sd":
            checks.append(self._check_sd_model())

        # Check Python venv
        checks.append(self._check_python_venv())

        return checks

    def _check_claude_cli(self) -> PreflightCheck:
        """Check if Claude CLI is available."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version = result.stdout.strip().split("\n")[0] if result.stdout else "unknown"
                return PreflightCheck(
                    name="claude_cli",
                    passed=True,
                    message=f"Claude CLI available ({version})",
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return PreflightCheck(
            name="claude_cli",
            passed=False,
            message="Claude CLI not found or not responding",
            is_blocker=True,
        )

    def _check_google_tts(self) -> PreflightCheck:
        """Check if Google TTS credentials are configured."""
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        if creds_path and Path(creds_path).exists():
            return PreflightCheck(
                name="google_tts",
                passed=True,
                message="Google TTS credentials found",
            )

        # Check default locations
        default_paths = [
            Path.home() / ".config" / "gcloud" / "application_default_credentials.json",
            self.project_root / "credentials" / "google-tts.json",
        ]

        for path in default_paths:
            if path.exists():
                return PreflightCheck(
                    name="google_tts",
                    passed=True,
                    message=f"Google TTS credentials found at {path}",
                )

        return PreflightCheck(
            name="google_tts",
            passed=False,
            message="Google TTS credentials not found (GOOGLE_APPLICATION_CREDENTIALS not set)",
            is_blocker=True,
        )

    def _check_ffmpeg(self) -> PreflightCheck:
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version_line = result.stdout.split("\n")[0] if result.stdout else "unknown"
                return PreflightCheck(
                    name="ffmpeg",
                    passed=True,
                    message=f"FFmpeg available ({version_line[:50]})",
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return PreflightCheck(
            name="ffmpeg",
            passed=False,
            message="FFmpeg not found",
            is_blocker=True,
        )

    def _check_disk_space(self, required_gb: float = 1.0) -> PreflightCheck:
        """Check if there's enough disk space."""
        try:
            sessions_path = self.project_root / "sessions"
            sessions_path.mkdir(exist_ok=True)

            total, used, free = shutil.disk_usage(sessions_path)
            free_gb = free / (1024**3)

            if free_gb >= required_gb:
                return PreflightCheck(
                    name="disk_space",
                    passed=True,
                    message=f"{free_gb:.1f}GB available (need {required_gb}GB)",
                )
            else:
                return PreflightCheck(
                    name="disk_space",
                    passed=False,
                    message=f"Only {free_gb:.1f}GB available (need {required_gb}GB)",
                    is_blocker=True,
                )
        except Exception as e:
            return PreflightCheck(
                name="disk_space",
                passed=False,
                message=f"Could not check disk space: {e}",
                is_blocker=False,
            )

    def _check_sd_model(self) -> PreflightCheck:
        """Check if Stable Diffusion model is available."""
        sd_model_paths = [
            Path.home() / "sd-webui" / "models" / "Stable-diffusion" / "sd-v1-5-pruned-emaonly.safetensors",
            Path.home() / ".cache" / "huggingface" / "hub" / "models--runwayml--stable-diffusion-v1-5",
            self.project_root / "models" / "sd-v1-5-pruned-emaonly.safetensors",
        ]

        for path in sd_model_paths:
            if path.exists():
                return PreflightCheck(
                    name="sd_model",
                    passed=True,
                    message=f"SD model found at {path}",
                )

        return PreflightCheck(
            name="sd_model",
            passed=False,
            message="SD model not found (will auto-download on first use)",
            is_blocker=False,  # Not a blocker, will download
        )

    def _check_python_venv(self) -> PreflightCheck:
        """Check if running in the project's virtual environment."""
        venv_path = self.project_root / "venv"

        if venv_path.exists():
            # Check if current Python is from venv
            current_python = Path(sys.executable)
            if str(venv_path) in str(current_python):
                return PreflightCheck(
                    name="python_venv",
                    passed=True,
                    message="Running in project venv",
                )
            else:
                return PreflightCheck(
                    name="python_venv",
                    passed=True,
                    message=f"Venv exists at {venv_path} (not currently active)",
                )

        return PreflightCheck(
            name="python_venv",
            passed=False,
            message="Project venv not found",
            is_blocker=False,
        )

    def _validate_resources(self, image_method: str) -> tuple[bool, List[str]]:
        """Validate available resources."""
        warnings = []
        validated = True

        # Check if SD is CPU-only
        if image_method == "sd":
            try:
                import torch

                if not torch.cuda.is_available():
                    warnings.append("SD model is CPU-only (expect ~60s per image)")
            except ImportError:
                warnings.append("PyTorch not installed (SD may not work)")
                validated = False

        # Check for Notion token (for RAG context)
        if not os.environ.get("NOTION_TOKEN"):
            warnings.append("NOTION_TOKEN not set (RAG context will be limited)")

        # Check for website upload tokens
        if not os.environ.get("SALARSU_API_TOKEN"):
            warnings.append("SALARSU_API_TOKEN not set (website upload will fail)")

        return validated, warnings

    def _consult_knowledge_base(self, topic: str) -> tuple[List[str], List[str]]:
        """Consult the knowledge base for relevant lessons and practices."""
        lessons = []
        practices = []

        # Read lessons_learned.yaml
        lessons_path = self.project_root / "knowledge" / "lessons_learned.yaml"
        if lessons_path.exists():
            try:
                data = yaml.safe_load(lessons_path.read_text(encoding="utf-8"))
                # Get recent high-priority lessons
                for lesson in data.get("lessons", [])[:5]:
                    if lesson.get("priority", "low") in ["high", "critical"]:
                        lessons.append(f"{lesson.get('lesson', '')} ({lesson.get('date', '')})")
            except Exception:
                pass

        # Read best_practices.md for topic-relevant practices
        practices_path = self.project_root / "knowledge" / "best_practices.md"
        if practices_path.exists():
            try:
                content = practices_path.read_text(encoding="utf-8")
                # Extract bullet points from best practices
                for line in content.split("\n"):
                    if line.strip().startswith("- ") and len(practices) < 5:
                        practices.append(line.strip()[2:])
            except Exception:
                pass

        # Add default practices if none found
        if not practices:
            practices = [
                "Use rate=1.0 for all SSML (achieve pacing via breaks)",
                "Voice at -6dB, binaural at -6dB, SFX at 0dB",
                "Apply hypnotic post-processing to all sessions",
            ]

        return lessons, practices

    def _estimate_costs(
        self, mode: str, image_method: str, audio_only: bool
    ) -> CostEstimate:
        """Estimate costs for the pipeline."""
        multiplier = self.MODE_MULTIPLIERS.get(mode, 1.0)
        breakdown = {}

        # Always included
        breakdown["manifest_generation"] = self.BASE_COSTS["manifest_generation"] * multiplier
        breakdown["script_generation"] = self.BASE_COSTS["script_generation"] * multiplier
        breakdown["voice_synthesis"] = self.BASE_COSTS["voice_synthesis"]  # Fixed TTS cost
        breakdown["vtt_generation"] = self.BASE_COSTS["vtt_generation"] * multiplier

        # Image costs depend on method
        if not audio_only:
            if image_method == "sd":
                breakdown["sd_images"] = 0.00  # Local
            elif image_method == "pil":
                breakdown["pil_images"] = 0.00  # Local
            else:
                breakdown["image_prompts"] = self.BASE_COSTS["image_prompts"] * multiplier

        total = sum(breakdown.values())

        return CostEstimate(
            total_usd=total,
            breakdown=breakdown,
            mode=mode,
        )

    def _assess_feasibility(
        self, topic: str, duration_minutes: int
    ) -> tuple[float, List[str]]:
        """Assess topic feasibility."""
        score = 0.8  # Base score
        notes = []

        # Check topic length
        words = topic.split()
        if len(words) < 3:
            score -= 0.1
            notes.append("Topic is short; may need enhancement")
        elif len(words) > 15:
            score -= 0.05
            notes.append("Topic is long; may need simplification")

        # Check duration
        if duration_minutes < 15:
            score -= 0.1
            notes.append("Short duration may limit journey depth")
        elif duration_minutes > 45:
            score -= 0.05
            notes.append("Long duration increases generation time")
        else:
            notes.append(f"{duration_minutes}min duration is standard")

        # Check for common theme keywords
        topic_lower = topic.lower()
        theme_keywords = {
            "healing": 0.05,
            "peace": 0.05,
            "nature": 0.05,
            "journey": 0.03,
            "meditation": 0.05,
            "relaxation": 0.05,
            "sleep": 0.03,
            "confidence": 0.03,
            "transformation": 0.03,
        }

        for keyword, boost in theme_keywords.items():
            if keyword in topic_lower:
                score += boost
                notes.append(f"'{keyword}' theme has strong knowledge base support")
                break

        # Cap score at 1.0
        score = min(1.0, score)

        return score, notes

    def _build_execution_roadmap(
        self, session_name: str, image_method: str, audio_only: bool
    ) -> List[PlannedStage]:
        """Build the execution roadmap."""
        stages = []
        session_path = f"sessions/{session_name}"

        for name, description, duration, deps in self.STAGE_DEFINITIONS:
            # Skip video stages if audio_only
            if audio_only and name in [
                "generate_images",
                "assemble_video",
                "package_youtube",
                "generate_thumbnail",
            ]:
                continue

            # Adjust image stage timing based on method
            if name == "generate_images":
                if image_method == "pil":
                    duration = 30  # PIL is fast
                elif image_method == "sd":
                    duration = 600  # SD is slow on CPU
                elif image_method == "stock":
                    duration = 60  # Just generates guide

            # Determine expected output
            output_map = {
                "create_session": f"{session_path}/",
                "generate_manifest": "manifest.yaml, brainstormed_concepts.yaml",
                "generate_script": "script.ssml, script_voice_clean.ssml",
                "generate_prompts": "midjourney-prompts.md or image prompts",
                "generate_voice": "voice.mp3, voice_enhanced.mp3",
                "generate_binaural": "binaural_dynamic.wav",
                "generate_sfx": "sfx_track.wav",
                "mix_audio": "session_mixed.wav",
                "hypnotic_post_process": f"{session_name}_MASTER.mp3",
                "generate_vtt": "subtitles.vtt",
                "generate_images": "images/uploaded/*.png",
                "assemble_video": "video/session_final.mp4",
                "package_youtube": "youtube_package/",
                "generate_thumbnail": "youtube_thumbnail.png",
                "upload_website": f"salars.net/dreamweavings/{session_name}",
                "cleanup": "Intermediate files removed",
                "self_improvement": "lessons_learned.yaml updated",
            }

            stages.append(
                PlannedStage(
                    name=name,
                    description=description,
                    expected_output=output_map.get(name, ""),
                    estimated_duration_seconds=duration,
                    dependencies=deps,
                    can_skip=name in ["cleanup", "self_improvement", "upload_website"],
                )
            )

        return stages

    def _assess_risks(self, image_method: str, audio_only: bool) -> List[Risk]:
        """Assess risks for the pipeline."""
        risks = []

        # Claude rate limiting
        risks.append(
            Risk(
                name="claude_rate_limit",
                severity="medium",
                likelihood="low",
                mitigation="Retry with exponential backoff",
            )
        )

        # Script validation failure
        risks.append(
            Risk(
                name="script_validation_fail",
                severity="high",
                likelihood="low",
                mitigation="Auto-fix common SSML issues, retry generation",
            )
        )

        # TTS failure
        risks.append(
            Risk(
                name="tts_failure",
                severity="high",
                likelihood="low",
                mitigation="Retry with alternative voice",
            )
        )

        # SD-specific risks
        if image_method == "sd" and not audio_only:
            risks.append(
                Risk(
                    name="sd_generation_slow",
                    severity="low",
                    likelihood="high",
                    mitigation="Use PIL fallback if >10min per image",
                )
            )
            risks.append(
                Risk(
                    name="sd_memory_error",
                    severity="medium",
                    likelihood="medium",
                    mitigation="Fall back to PIL procedural images",
                )
            )

        # Video assembly risks
        if not audio_only:
            risks.append(
                Risk(
                    name="video_assembly_fail",
                    severity="medium",
                    likelihood="low",
                    mitigation="Retry with different FFmpeg settings",
                )
            )

        return risks

    def _define_fallbacks(self) -> Dict[str, str]:
        """Define fallback strategies for each stage."""
        return {
            "generate_script": "Use codex fallback if Claude fails",
            "generate_voice": "Retry with alternative Neural2 voice",
            "generate_images": "Fall back to PIL procedural images",
            "generate_binaural": "Use pre-generated binaural template",
            "mix_audio": "Mix voice-only if stems fail",
            "assemble_video": "Create static image video as fallback",
            "upload_website": "Skip upload, manual upload later",
        }
