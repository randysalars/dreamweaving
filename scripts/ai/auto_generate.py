#!/usr/bin/env python3
"""
Auto-Generate: Complete Topic-to-YouTube Pipeline

Orchestrates the complete session production from just a topic:
1. Create session directory structure
2. Generate manifest from topic using CreativeWorkflow
3. Generate SSML script (via Claude CLI)
4. Generate stock image search guide (or SD/Midjourney prompts)
5. Generate voice audio
6. Generate binaural beats
7. Mix and master audio
8. Apply hypnotic post-processing
9. Generate VTT subtitles
10. Assemble video (when images available)
11. Package for YouTube
12. Generate optimized YouTube thumbnail (LLM-powered text, auto style selection)
13. Upload to website (salars.net)
14. Cleanup intermediate files
15. Self-improvement/learning (record lessons learned)

Requirements:
    - Claude Code extension for VS Code (uses your Claude subscription)
    - Google Cloud TTS credentials for voice generation

Usage:
    # Standard generation (stock images from Unsplash)
    python3 scripts/ai/auto_generate.py --topic "Finding Inner Peace" --mode standard

    # With custom duration
    python3 scripts/ai/auto_generate.py --topic "Deep Sleep Journey" --duration 45 --mode budget

    # Use Stable Diffusion for local image generation
    python3 scripts/ai/auto_generate.py --topic "Cosmic Journey" --image-method sd

    # Use different stock platform
    python3 scripts/ai/auto_generate.py --topic "Nature Walk" --stock-platform pexels

    # Audio only (skip video)
    python3 scripts/ai/auto_generate.py --topic "Confidence Builder" --audio-only

    # Dry run (just generate manifest and show plan)
    python3 scripts/ai/auto_generate.py --topic "Healing from Grief" --dry-run

Image Methods:
    - stock:     Source from Unsplash/Pexels/Pixabay (default, generates search guide)
    - sd:        Generate locally with Stable Diffusion
    - midjourney: Generate prompts for Midjourney

Cost Optimization Modes:
    - budget:   Minimal AI usage, ~$0.70 total
    - standard: Balanced quality/cost, ~$1.06 total (recommended)
    - premium:  Maximum quality, ~$1.51 total
"""

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image

import requests
import yaml
from dotenv import load_dotenv

# Add project root to path
# NOTE: Import archetype_selector after path setup (below)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
RAG_NO_CONTEXT = "(No canonical knowledge found)"

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")

from scripts.ai.creative_workflow import CreativeWorkflow
from scripts.utilities.estimate_duration import estimate_duration
from scripts.utilities.archetype_selector import ArchetypeSelector, SelectedArchetype

# Recursive improvement agent (lazy-loaded for performance)
_recursive_agent = None

def _get_recursive_agent():
    """Get or create the DreamweaverRecursiveAgent (lazy-loaded)."""
    global _recursive_agent
    if _recursive_agent is None:
        try:
            from scripts.ai.agents.dreamweaver_recursive import DreamweaverRecursiveAgent
            _recursive_agent = DreamweaverRecursiveAgent(project_root=PROJECT_ROOT)
        except ImportError as e:
            print(f"Warning: Could not import recursive agent: {e}")
            return None
    return _recursive_agent

DEFAULT_NOTION_ROOT_PAGE_ID = os.getenv(
    "NOTION_ROOT_PAGE_ID", "1ee2bab3796d80738af6c96bd5077acf"
)
DEFAULT_NOTION_TOPIC_DB_ID = os.getenv(
    "NOTION_TOPIC_DATABASE_ID", "2c22bab3-796d-81fb-bdf8-efd2aab0159e"
)


class NotionTopicManager:
    """Lightweight Notion helper for fetching and marking topics."""

    def __init__(
        self,
        token: Optional[str],
        root_page_id: Optional[str] = None,
        database_id: Optional[str] = None,
        notion_version: str = "2022-06-28",
        timeout: int = 10,
    ):
        self.token = token
        self.root_page_id = root_page_id or DEFAULT_NOTION_ROOT_PAGE_ID
        self.database_id = database_id or DEFAULT_NOTION_TOPIC_DB_ID
        self.notion_version = notion_version
        self.timeout = timeout
        self.session = requests.Session()

    # ---------- Public API ----------
    def get_unused_topics(self) -> List[Dict]:
        """Return all unused topics under the configured root page."""
        if not self.token:
            raise RuntimeError("NOTION_TOKEN is not set; cannot query Notion.")
        topics = self._collect_child_pages(self.root_page_id, path=[])
        unused = []
        for topic in topics:
            page_data = self._get_page(topic["id"])
            if not self._is_used(topic["title"], page_data):
                topic["page"] = page_data
                unused.append(topic)
        return unused

    def pick_random_unused(self) -> Dict:
        """Pick a random unused topic."""
        if not self.token:
            raise RuntimeError("NOTION_TOKEN is not set; cannot query Notion.")

        # Prefer database query if available
        if self.database_id:
            candidates = self._query_unused_database()
            if candidates:
                random.shuffle(candidates)
                return candidates[0]

        # Collect all child pages (structure only), shuffle for randomness
        pages = self._collect_child_pages(self.root_page_id, path=[])
        if not pages:
            raise RuntimeError("No child pages found under the Notion root page.")
        random.shuffle(pages)

        last_page = None
        for topic in pages:
            page_data = self._get_page(topic["id"])
            last_page = page_data
            if not self._is_used(topic["title"], page_data):
                topic["page"] = page_data
                return topic

        # If everything was used, fall back with more context
        last_title = (last_page or {}).get("properties", {}).get(
            "title", {}
        )
        raise RuntimeError(
            "No unused topics available in Notion (all topics appear marked as used)."
        )

    def mark_used(self, topic: Dict) -> bool:
        """Mark a topic as used in Notion (checkbox/status/title prefix)."""
        page_id = topic["id"]
        title = topic["title"]
        page_data = topic.get("page") or self._get_page(page_id)

        # If this is a database row, update via pages endpoint
        if topic.get("is_db_row"):
            updates: Dict = {"properties": {}}

            # Status -> Used (if exists)
            status_prop = self._find_status_property(page_data)
            if status_prop:
                updates["properties"][status_prop] = {"select": {"name": "Used"}}

            # Checkbox Used -> true
            used_checkbox = self._find_checkbox_property(page_data, prefer_name="Used")
            if used_checkbox:
                updates["properties"][used_checkbox] = {"checkbox": True}

            # Used At -> now
            updates["properties"]["Used At"] = {
                "date": {"start": datetime.now().isoformat()}
            }

            resp = self.session.patch(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=self._headers(),
                json=updates,
                timeout=self.timeout,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Failed to mark topic as used (HTTP {resp.status_code}): {resp.text[:200]}"
                )
            return True

        updates: Dict = {"properties": {}}

        # Prefer an explicit checkbox property named "Used"
        used_checkbox = self._find_checkbox_property(page_data, prefer_name="Used")
        if used_checkbox:
            updates["properties"][used_checkbox] = {"checkbox": True}

        # If a Status property has a "Used" option, set it
        status_update = self._build_status_update(page_data)
        if status_update:
            updates["properties"].update(status_update)

        # Fallback: prefix the title to reflect usage
        if not self._title_looks_used(title):
            title_prop = self._find_title_property(page_data)
            if title_prop:
                updates["properties"][title_prop] = {
                    "title": [{"text": {"content": f"✅ {title}"}}]
                }

        if not updates["properties"]:
            return False

        resp = self.session.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=self._headers(),
            json=updates,
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Failed to mark topic as used (HTTP {resp.status_code}): {resp.text[:200]}"
            )
        return True

    # ---------- Internal helpers ----------
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.notion_version,
            "Content-Type": "application/json",
        }

    def _list_children(self, block_id: str) -> List[Dict]:
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        cursor = None
        results: List[Dict] = []
        while True:
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            resp = self.session.get(
                url, headers=self._headers(), params=params, timeout=self.timeout
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Failed to fetch children for block {block_id}: {resp.text[:200]}"
                )
            data = resp.json()
            results.extend(data.get("results", []))
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
        return results

    def _collect_child_pages(self, parent_id: str, path: List[str]) -> List[Dict]:
        collected: List[Dict] = []
        for block in self._list_children(parent_id):
            if block.get("type") != "child_page":
                continue
            title = (block["child_page"].get("title") or "").strip()
            child_path = path + [title or "Untitled"]
            collected.append(
                {"id": block["id"], "title": title, "path": child_path}
            )
            if block.get("has_children"):
                collected.extend(
                    self._collect_child_pages(block["id"], child_path)
                )
        return collected

    def _get_page(self, page_id: str) -> Dict:
        resp = self.session.get(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Failed to fetch page {page_id}: {resp.status_code} {resp.text[:200]}"
            )
        return resp.json()

    def _query_unused_database(self) -> List[Dict]:
        if not self.database_id:
            return []

        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        cursor = None
        results: List[Dict] = []
        while True:
            body = {
                "page_size": 100,
                "filter": {
                    "or": [
                        {"property": "Used", "checkbox": {"equals": False}},
                        {"property": "Status", "select": {"does_not_equal": "Used"}},
                    ]
                },
            }
            if cursor:
                body["start_cursor"] = cursor
            resp = self.session.post(
                url, headers=self._headers(), json=body, timeout=self.timeout
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Failed to query database {self.database_id}: {resp.text[:200]}"
                )
            data = resp.json()
            for row in data.get("results", []):
                props = row.get("properties", {})
                title_prop = self._find_title_property(row, properties_override=props)
                title_text = ""
                if title_prop and props.get(title_prop, {}).get("title"):
                    title_text = "".join(
                        t.get("plain_text", "")
                        for t in props[title_prop].get("title", [])
                    )
                path_text = ""
                if "Path" in props and props["Path"].get("rich_text"):
                    path_text = "".join(
                        t.get("plain_text", "") for t in props["Path"]["rich_text"]
                    )
                results.append(
                    {
                        "id": row["id"],
                        "title": title_text or "Untitled",
                        "path": [path_text] if path_text else [],
                        "page": row,
                        "is_db_row": True,
                    }
                )
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
        return results

    def _title_looks_used(self, title: str) -> bool:
        lowered = (title or "").strip().lower()
        return lowered.startswith(("✅", "[used", "used", "✔", "done", "complete"))

    def _is_used(self, title: str, page_data: Dict) -> bool:
        if self._title_looks_used(title):
            return True

        properties = page_data.get("properties", {}) or {}
        for name, prop in properties.items():
            prop_type = prop.get("type")
            if prop_type == "checkbox" and name.lower() == "used":
                if prop.get("checkbox") is True:
                    return True
            if prop_type == "status":
                status = prop.get("status") or {}
                if (status.get("name") or "").lower() in {
                    "used",
                    "done",
                    "complete",
                    "finished",
                }:
                    return True
        return False

    def _find_checkbox_property(
        self, page_data: Dict, prefer_name: str = "Used"
    ) -> Optional[str]:
        properties = page_data.get("properties", {}) or {}
        preferred_lower = prefer_name.lower()
        for name, prop in properties.items():
            if prop.get("type") == "checkbox" and name.lower() == preferred_lower:
                return name
        for name, prop in properties.items():
            if prop.get("type") == "checkbox":
                return name
        return None

    def _find_title_property(
        self, page_data: Dict, properties_override: Optional[Dict] = None
    ) -> Optional[str]:
        properties = properties_override or page_data.get("properties", {}) or {}
        for name, prop in properties.items():
            if prop.get("type") == "title":
                return name
        return None

    def _find_status_property(self, page_data: Dict) -> Optional[str]:
        properties = page_data.get("properties", {}) or {}
        for name, prop in properties.items():
            if prop.get("type") == "select":
                return name
        return None

    def _build_status_update(self, page_data: Dict) -> Dict:
        properties = page_data.get("properties", {}) or {}
        for name, prop in properties.items():
            if prop.get("type") != "status":
                continue
            options = prop.get("status", {}).get("options", [])
            option_names = {opt.get("name", "").lower(): opt for opt in options}
            for desired in ("used", "done", "complete"):
                if desired in option_names:
                    return {name: {"status": {"name": option_names[desired]["name"]}}}
        return {}


def prompt_for_topic(
    cli_topic: Optional[str],
    topic_source: str,
    notion_root: Optional[str] = None,
) -> Tuple[str, str]:
    """Resolve the topic via CLI args or interactive selector."""
    # Non-interactive environments: fall back to provided options
    if not sys.stdin.isatty():
        if cli_topic:
            return cli_topic.strip(), "manual"
        if topic_source == "notion":
            return fetch_random_notion_topic(notion_root), "notion"
        # Try Notion if token is available
        if os.getenv("NOTION_TOKEN"):
            return fetch_random_notion_topic(notion_root), "notion"
        raise RuntimeError(
            "No TTY available. Provide --topic or run with --topic-source notion (and NOTION_TOKEN set)."
        )

    if cli_topic and topic_source != "prompt":
        return cli_topic.strip(), topic_source

    if topic_source == "notion" and not cli_topic:
        return fetch_random_notion_topic(notion_root), "notion"

    if cli_topic:
        return cli_topic.strip(), "manual"

    print("\nTopic Selection")
    print("  1) Enter topic manually")
    print("  2) Random unused topic from Notion")

    choice = None
    while choice not in {"1", "2"}:
        try:
            choice = input("Choose 1 or 2 [1]: ").strip() or "1"
        except EOFError:
            # If input is closed mid-prompt, fall back to manual entry prompt
            return prompt_manual_topic(), "manual"

    if choice == "1":
        return prompt_manual_topic(), "manual"

    return fetch_random_notion_topic(notion_root), "notion"


def prompt_manual_topic() -> str:
    """Prompt user for a manual topic with basic validation."""
    while True:
        try:
            topic = input("Enter a video topic: ").strip()
        except EOFError:
            raise RuntimeError("No input available; provide --topic or use --topic-source notion.")
        if not topic:
            print("Topic cannot be empty. Please try again.")
            continue
        if len(topic) < 3:
            print("Topic is too short; please provide at least 3 characters.")
            continue
        if len(topic) > 200:
            print("Topic is too long; keep it under 200 characters.")
            continue
        return topic


def fetch_random_notion_topic(notion_root: Optional[str]) -> str:
    """Fetch and mark a random unused topic from Notion."""
    token = os.getenv("NOTION_TOKEN")
    manager = NotionTopicManager(token=token, root_page_id=notion_root)
    try:
        topic = manager.pick_random_unused()
        manager.mark_used(topic)
        path = " > ".join(topic.get("path", []) or [topic["title"]])
        print(f"Selected Notion topic: {topic['title']} (path: {path})")
        return topic["title"]
    except Exception as exc:
        print(f"[warning] Notion topic retrieval failed: {exc}")
        print("Falling back to manual topic entry.")
        return prompt_manual_topic()


class CostTracker:
    """Track estimated costs for the generation pipeline."""

    # Estimated costs per operation (in USD)
    COSTS = {
        'manifest_generation': 0.05,
        'script_generation': 0.35,
        'voice_synthesis': 0.15,  # Google Cloud TTS
        'image_prompts': 0.10,
        'vtt_generation': 0.05,
        'quality_check': 0.05,
    }

    MODE_MULTIPLIERS = {
        'budget': 0.65,
        'standard': 1.0,
        'premium': 1.4,
    }

    def __init__(self, mode: str = 'standard'):
        self.mode = mode
        self.multiplier = self.MODE_MULTIPLIERS.get(mode, 1.0)
        self.operations: List[Dict] = []

    def add_operation(self, name: str, actual_cost: float = None):
        """Record an operation."""
        estimated = self.COSTS.get(name, 0.0) * self.multiplier
        self.operations.append({
            'name': name,
            'estimated': estimated,
            'actual': actual_cost or estimated,
            'timestamp': datetime.now().isoformat(),
        })

    def get_total(self) -> float:
        """Get total cost."""
        return sum(op['actual'] for op in self.operations)

    def get_report(self) -> Dict:
        """Get cost report."""
        return {
            'mode': self.mode,
            'multiplier': self.multiplier,
            'operations': self.operations,
            'total_usd': round(self.get_total(), 4),
        }


class AutoGenerator:
    """Complete auto-generation pipeline."""

    def __init__(
        self,
        topic: str,
        topic_source: str = 'manual',
        mode: str = 'standard',
        duration_minutes: int = 30,
        audio_only: bool = False,
        dry_run: bool = False,
        verbose: bool = True,
        session_name: Optional[str] = None,
        skip_upload: bool = False,
        no_cleanup: bool = False,
        no_learning: bool = False,
        image_method: str = 'sd',
        image_performance: str = 'speed',
        stock_platform: str = 'unsplash',
        nightly: bool = False,
        skip_youtube: bool = False,
    ):
        self.topic = topic
        self.mode = mode
        self.duration_minutes = duration_minutes
        self.audio_only = audio_only
        self.dry_run = dry_run
        self.verbose = verbose
        self.topic_source = topic_source
        self.skip_upload = skip_upload
        self.no_cleanup = no_cleanup
        self.no_learning = no_learning
        self.image_method = image_method
        self.image_performance = image_performance
        self.stock_platform = stock_platform
        self.nightly = nightly
        self.skip_youtube = skip_youtube or nightly  # Nightly mode implies skip_youtube

        # Generate session name from topic if not provided
        if session_name:
            self.session_name = session_name
        else:
            self.session_name = self._generate_session_name(topic)

        self.project_root = PROJECT_ROOT
        self.session_path = self.project_root / "sessions" / self.session_name

        self.cost_tracker = CostTracker(mode)
        self.workflow = CreativeWorkflow()
        self.start_time = None
        self.end_time = None
        # Prefer project venv Python if available; fallback to current interpreter
        venv_python = self.project_root / "venv" / "bin" / "python"
        self.python_cmd = os.environ.get("PYTHON_CMD") or (str(venv_python) if venv_python.exists() else sys.executable)

        # Stage tracking
        self.stages_completed: List[str] = []
        self.stages_failed: List[str] = []

        # Recursive improvement tracking
        self.applied_lessons: List[str] = []
        self.lessons_context: str = ""
        self.generation_plan = None

    def _generate_session_name(self, topic: str) -> str:
        """Generate a kebab-case session name from topic."""
        # Remove special characters and convert to kebab-case
        name = topic.lower()
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[\s_]+', '-', name)
        name = name.strip('-')[:40]

        # Add timestamp suffix for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d')
        return f"{name}-{timestamp}"

    def _get_subprocess_env(self):
        """Get environment with proper PYTHONPATH for subprocess calls.
        
        This ensures child processes can import project modules.
        """
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_root)
        return env

    def log(self, message: str, level: str = "info"):
        """Log a message."""
        if self.verbose or level in ["error", "warning"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = {
                "info": "   ",
                "success": " ✓ ",
                "warning": " ⚠ ",
                "error": " ✗ ",
                "stage": ">>>",
            }.get(level, "   ")
            print(f"[{timestamp}] {prefix} {message}")

    def run(self) -> Dict:
        """Run the complete auto-generation pipeline."""
        self.start_time = datetime.now()

        self.log(f"Auto-Generate Pipeline", "stage")
        self.log(f"Topic: {self.topic}")
        self.log(f"Topic Source: {self.topic_source}")
        self.log(f"Mode: {self.mode}")
        self.log(f"Duration: {self.duration_minutes} min")
        self.log(f"Session: {self.session_name}")

        if self.dry_run:
            self.log("DRY RUN - Plan will be created, no generation", "warning")

        try:
            # Stage 0: Create execution plan (ALWAYS runs first)
            plan = self._stage_create_plan()

            if plan.has_blockers():
                self.log(f"Planning found {len(plan.blockers)} blocker(s)", "error")
                for blocker in plan.blockers:
                    self.log(f"  BLOCKER: {blocker}", "error")
                raise RuntimeError(f"Planning found blockers: {plan.blockers}")

            # In dry-run mode, stop after planning
            if self.dry_run:
                self.log("DRY RUN complete - Plan created, stopping", "warning")
                self.end_time = datetime.now()
                return self._generate_plan_only_report(plan)

            # Stage 1: Create session structure
            self._stage_create_session()

            # Save the execution plan now that session directory exists
            if hasattr(self, 'generation_plan') and self.generation_plan:
                plan_path = self.session_path / "working_files" / "generation_plan.yaml"
                self.generation_plan.save(plan_path)
                self.log(f"Plan saved to: {plan_path}", "info")

            # Stage 2: Generate manifest
            manifest = self._stage_generate_manifest()

            # Stage 3: Generate SSML script
            self._stage_generate_script()
            if "generate_script" in self.stages_failed:
                print("STAGE_FATAL: generate_script failed - check Claude CLI/API", file=sys.stderr)
                raise RuntimeError("generate_script failed; aborting pipeline")

            # Stage 4: Generate image prompts
            self._stage_generate_prompts()

            if not self.dry_run:
                # Stage 5: Generate voice
                self._stage_generate_voice()
                if "generate_voice" in self.stages_failed:
                    print("STAGE_FATAL: generate_voice failed - check TTS credentials", file=sys.stderr)
                    raise RuntimeError("generate_voice failed; aborting pipeline (audio stages depend on voice)")

                # Stage 6: Generate binaural
                self._stage_generate_binaural()

                # Stage 6.5: Generate SFX track (if markers exist)
                self._stage_generate_sfx()

                # Stage 7: Mix audio
                self._stage_mix_audio()

                # Stage 8: Hypnotic post-processing
                self._stage_hypnotic_post_process()

                # Stage 9: Generate VTT
                self._stage_generate_vtt()

                if not self.audio_only:
                    # Stage 10: Generate scene images
                    self._stage_generate_images()

                    # Stage 11: Assemble video
                    self._stage_assemble_video()

                    # Stage 12: Package for YouTube (skip in nightly mode)
                    if not self.skip_youtube:
                        self._stage_package_youtube()
                    else:
                        self.log("Skipping YouTube package (nightly mode)", "info")

                    # Stage 12.5: Generate thumbnail
                    self._stage_generate_thumbnail()

                    # Stage 13: Upload to website (optional)
                    if not self.skip_upload:
                        self._stage_upload_website()

                # Stage 14: Cleanup intermediate files (optional)
                if not self.no_cleanup:
                    self._stage_cleanup()

                # Stage 15: Self-improvement/learning (optional)
                if not self.no_learning:
                    self._stage_self_improvement()

        except Exception as e:
            self.log(f"Pipeline failed: {e}", "error")
            # CRITICAL: Print to stderr so nightly builder captures it
            print(f"PIPELINE_FATAL: {e}", file=sys.stderr)
            self.stages_failed.append(str(e))

        self.end_time = datetime.now()

        # Generate report
        report = self._generate_report()
        self._save_report(report)

        return report

    def _stage_create_plan(self) -> 'GenerationPlan':
        """Stage 0: Create execution plan before any generation.

        This is the first stage in the pipeline. It:
        1. Runs pre-flight checks (Claude CLI, Google TTS, FFmpeg, etc.)
        2. Validates resources (disk space, SD model, API tokens)
        3. Consults the knowledge base for relevant lessons
        4. Estimates costs
        5. Assesses topic feasibility
        6. Builds execution roadmap
        7. Identifies risks and fallbacks

        Returns:
            GenerationPlan with all checks, estimates, and roadmap
        """
        self.log("Creating execution plan", "stage")

        from scripts.ai.generation_planner import GenerationPlanner, GenerationPlan

        planner = GenerationPlanner(
            project_root=self.project_root,
            mode=self.mode,
        )

        plan = planner.create_plan(
            topic=self.topic,
            duration_minutes=self.duration_minutes,
            mode=self.mode,
            image_method=self.image_method,
            audio_only=self.audio_only,
            session_name=self.session_name,
        )

        # Store plan for later use
        self.generation_plan = plan

        # Log plan summary
        self.log(f"Pre-flight: {sum(1 for c in plan.preflight_checks if c.passed)}/{len(plan.preflight_checks)} checks passed", "info")

        if plan.cost_estimate:
            self.log(f"Cost estimate: ${plan.cost_estimate.total_usd:.2f} ({plan.cost_estimate.mode} mode)", "info")

        self.log(f"Stages planned: {len(plan.stages)}", "info")
        self.log(f"Feasibility score: {plan.feasibility_score:.0%}", "info")

        if plan.risks:
            self.log(f"Risks identified: {len(plan.risks)}", "info")

        # Log warnings
        for warning in plan.warnings:
            self.log(f"Warning: {warning}", "warning")

        # Log knowledge context (from generation_planner)
        if plan.lessons_applied:
            self.log(f"Lessons from planner: {len(plan.lessons_applied)}", "info")

        # Use recursive improvement agent to get ranked lessons
        try:
            agent = _get_recursive_agent()
            if agent:
                applied = agent.prepare_generation(
                    topic=self.topic,
                    duration_minutes=self.duration_minutes,
                    desired_outcome=None,  # Will be set from manifest later
                )
                self.applied_lessons = applied.lesson_ids
                self.lessons_context = applied.lessons_context

                if self.applied_lessons:
                    self.log(f"Ranked lessons applied: {len(self.applied_lessons)}", "info")
                    # Also add to plan for reference
                    plan.lessons_applied = list(set(plan.lessons_applied + self.applied_lessons))
        except Exception as e:
            self.log(f"Warning: Could not get ranked lessons: {e}", "warning")

        self.stages_completed.append("create_plan")
        self.log("Execution plan created", "success")

        return plan

    def _generate_plan_only_report(self, plan: 'GenerationPlan') -> Dict:
        """Generate report for dry-run mode (plan only, no execution).

        Args:
            plan: The generated execution plan

        Returns:
            Report dict with plan details
        """
        # Save plan to working_files if session directory exists
        plan_path = self.session_path / "working_files" / "generation_plan.yaml"
        if not self.session_path.exists():
            # Create minimal structure for plan storage
            (self.session_path / "working_files").mkdir(parents=True, exist_ok=True)

        plan.save(plan_path)
        self.log(f"Plan saved to: {plan_path}", "success")

        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        return {
            "session_name": self.session_name,
            "topic": self.topic,
            "mode": self.mode,
            "dry_run": True,
            "execution": {
                "started": self.start_time.isoformat() if self.start_time else None,
                "ended": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": int(duration),
            },
            "plan": {
                "path": str(plan_path),
                "ready_to_execute": not plan.has_blockers(),
                "blockers": plan.blockers,
                "warnings": plan.warnings,
                "cost_estimate_usd": plan.cost_estimate.total_usd if plan.cost_estimate else 0,
                "stages_count": len(plan.stages),
                "estimated_duration_minutes": plan._estimate_total_duration(),
                "feasibility_score": plan.feasibility_score,
            },
            "stages": {
                "completed": self.stages_completed,
                "failed": self.stages_failed,
            },
        }

    def _stage_create_session(self):
        """Create session directory structure."""
        self.log("Creating session structure", "stage")

        if self.dry_run:
            self.log(f"Would create: {self.session_path}", "info")
            return

        # Create directories
        dirs = [
            self.session_path,
            self.session_path / "working_files",
            self.session_path / "output",
            self.session_path / "images" / "uploaded",
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        self.stages_completed.append("create_session")
        self.log(f"Created: {self.session_path}", "success")

    def _stage_generate_manifest(self) -> Dict:
        """Generate manifest from topic using CreativeWorkflow."""
        self.log("Generating manifest from topic", "stage")
        self.cost_tracker.add_operation('manifest_generation')

        # NEW: Retrieve canonical knowledge for topic (RAG)
        rag_context = None
        try:
            from scripts.ai.knowledge_tools import get_generation_context
            rag_context = get_generation_context(
                topic=self.topic,
                outcome=getattr(self, 'desired_outcome', None),
                limit=10
            )
            topic_count = len(rag_context.get("topic_knowledge", []))
            if topic_count > 0:
                self.log(f"Retrieved {topic_count} knowledge items from RAG", "info")
        except Exception as e:
            self.log(f"RAG retrieval skipped: {e}", "warning")
            rag_context = None

        # NEW: Retrieve competitor insights for better titles/themes
        competitor_context = None
        try:
            from scripts.ai.knowledge_tools import (
                get_competitor_insights,
                get_seasonal_insights,
                get_title_recommendations
            )

            # Detect category from topic
            topic_lower = self.topic.lower()
            category = None
            for cat in ['meditation', 'hypnosis', 'sleep', 'affirmations', 'binaural_beats', 'spiritual']:
                if cat.replace('_', ' ') in topic_lower or cat in topic_lower:
                    category = cat
                    break

            # Get competitor insights
            competitor_context = get_competitor_insights(category=category, limit=5)
            if competitor_context.get("title_patterns"):
                self.log(f"Retrieved {len(competitor_context['title_patterns'])} title patterns from competitor analysis", "info")

            # Get seasonal insights
            seasonal = get_seasonal_insights()
            if seasonal.get("interest_themes"):
                self.log("Retrieved seasonal trends for current month", "info")
                competitor_context["seasonal"] = seasonal

            # Get title recommendations
            title_recs = get_title_recommendations(
                topic=self.topic,
                outcome=getattr(self, 'desired_outcome', None),
                category=category
            )
            if title_recs.get("suggestions"):
                competitor_context["title_suggestions"] = title_recs

        except Exception as e:
            self.log(f"Competitor context retrieval skipped: {e}", "warning")
            competitor_context = None

        # Use CreativeWorkflow to brainstorm and select best journey
        result = self.workflow.brainstorm_and_create(
            topic=self.topic,
            session_name=self.session_name,
            num_concepts=5,
            duration_minutes=self.duration_minutes,
            save_concepts=not self.dry_run,
        )

        manifest = result['manifest']
        selected = result['selected_concept']

        self.log(f"Selected journey: {selected['title']}", "info")
        self.log(f"Setting: {selected['setting'][:60]}...", "info")
        self.log(f"Score: {selected['score']:.2f}", "info")

        if not self.dry_run:
            # Save manifest
            manifest_path = self.session_path / "manifest.yaml"
            with open(manifest_path, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
            self.log(f"Saved: {manifest_path}", "success")

            # Save RAG context for later stages (script generation, YouTube packaging)
            if rag_context and rag_context.get("topic_knowledge"):
                rag_context_path = self.session_path / "working_files" / "rag_context.yaml"
                rag_context_path.parent.mkdir(parents=True, exist_ok=True)
                with open(rag_context_path, 'w') as f:
                    yaml.dump({
                        'topic': self.topic,
                        'formatted_context': rag_context.get('formatted_context', ''),
                        'topic_knowledge_count': len(rag_context.get('topic_knowledge', [])),
                        'outcome_patterns_count': len(rag_context.get('outcome_patterns', [])),
                    }, f, default_flow_style=False, sort_keys=False)
                self.log("Saved RAG context for script generation", "info")

            # Save competitor context for YouTube packaging
            if competitor_context and competitor_context.get("title_patterns"):
                competitor_context_path = self.session_path / "working_files" / "competitor_context.yaml"
                with open(competitor_context_path, 'w') as f:
                    yaml.dump({
                        'topic': self.topic,
                        'formatted_context': competitor_context.get('formatted_context', ''),
                        'title_patterns': competitor_context.get('title_patterns', []),
                        'tag_recommendations': [t.get('tag') for t in competitor_context.get('tag_recommendations', [])[:15]],
                        'seasonal_themes': competitor_context.get('seasonal', {}).get('interest_themes', {}),
                        'title_suggestions': [s.get('title') for s in competitor_context.get('title_suggestions', {}).get('suggestions', [])],
                    }, f, default_flow_style=False, sort_keys=False)
                self.log("Saved competitor context for YouTube packaging", "info")

        self.stages_completed.append("generate_manifest")
        return manifest

    def _stage_generate_script(self):
        """Generate full SSML script using Claude API."""
        self.log("Generating SSML script", "stage")
        self.cost_tracker.add_operation('script_generation')

        if self.dry_run:
            self.log("Would generate SSML script", "info")
            return

        # Load master prompt for hypnotic script generation
        master_prompt_path = self.project_root / "prompts" / "hypnotic_dreamweaving_instructions.md"
        if not master_prompt_path.exists():
            self.log(f"Master prompt not found: {master_prompt_path}", "error")
            self.stages_failed.append("generate_script")
            return

        master_prompt = master_prompt_path.read_text()

        # Load manifest and concepts for context
        manifest_path = self.session_path / "manifest.yaml"
        concepts_path = self.session_path / "working_files" / "brainstormed_concepts.yaml"

        if not manifest_path.exists():
            self.log("Manifest not found, cannot generate script", "error")
            self.stages_failed.append("generate_script")
            return

        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)

        # Load brainstormed concepts if available
        selected_concept = None
        if concepts_path.exists():
            with open(concepts_path, 'r') as f:
                concepts_data = yaml.safe_load(f)
                if concepts_data and 'concepts' in concepts_data and concepts_data['concepts']:
                    selected_concept = concepts_data['concepts'][0]

        # Extract archetype names
        archetypes = manifest.get('archetypes', [])
        archetype_names = [a.get('name', 'Unknown') for a in archetypes] if archetypes else []

        # NEW: Load or generate RAG context for canonical knowledge injection
        rag_context_str = ""
        rag_context_path = self.session_path / "working_files" / "rag_context.yaml"

        # First try to load saved context from manifest stage
        if rag_context_path.exists():
            try:
                with open(rag_context_path, 'r') as f:
                    saved_context = yaml.safe_load(f)
                    rag_context_str = saved_context.get('formatted_context', '')
                    if rag_context_str and rag_context_str != RAG_NO_CONTEXT:
                        self.log("Loaded RAG context from manifest stage", "info")
            except Exception as e:
                self.log(f"Failed to load saved RAG context: {e}", "warning")

        # If no saved context, generate fresh (e.g., if manifest was pre-existing)
        if not rag_context_str:
            try:
                from scripts.ai.knowledge_tools import get_generation_context
                rag_context = get_generation_context(
                    topic=self.topic,
                    outcome=manifest.get('desired_outcome'),
                    archetypes=archetype_names,
                    limit=10
                )
                rag_context_str = rag_context.get('formatted_context', '')
                if rag_context_str and rag_context_str != RAG_NO_CONTEXT:
                    self.log(f"Retrieved fresh RAG context ({len(rag_context.get('topic_knowledge', []))} items)", "info")
            except Exception as e:
                self.log(f"RAG context retrieval skipped: {e}", "warning")

        # Build the user prompt with session context
        # Target word range to land near the requested duration (accounts for breaks/pauses)
        base_wpm = 130  # hypnotic pace
        pause_multiplier = 1.6  # expected pause inflation vs straight speech
        target_word_count = int((self.duration_minutes * base_wpm) / pause_multiplier)
        min_words = int(target_word_count * 0.9)
        max_words = int(target_word_count * 1.1)

        user_prompt = f"""Generate a complete SSML hypnotic script for the following session:

**Topic:** {self.topic}
**Target Duration:** {self.duration_minutes} minutes
**Target Word Count:** {min_words}-{max_words} words (hypnotic pace ~{base_wpm} wpm with pauses)
**Session Name:** {self.session_name}
"""

        if selected_concept:
            user_prompt += f"""
**Journey Theme:** {selected_concept.get('title', 'Transformative Journey')}
**Setting:** {selected_concept.get('setting', 'A sacred space of transformation')}
"""

        if archetype_names:
            user_prompt += f"""
**Archetypes to incorporate:** {', '.join(archetype_names)}
"""

        # Add section timing from manifest if available
        sections = manifest.get('sections', [])
        if sections:
            user_prompt += "\n**Section Timing:**\n"
            for section in sections:
                name = section.get('name', 'Section')
                duration = section.get('duration_seconds', 0)
                mins = duration // 60
                user_prompt += f"- {name}: {mins} minutes\n"

        # NEW: Inject RAG canonical knowledge context
        if rag_context_str and rag_context_str != RAG_NO_CONTEXT:
            user_prompt += f"""

---
## CANONICAL DREAMWEAVING KNOWLEDGE (from your knowledge base)
Use this context to ensure the script aligns with YOUR established definitions, archetypes, and patterns:

{rag_context_str}
---
"""

        section_timing_note = (
            "Match the Section Timing above within ±10%; expand MAIN JOURNEY and INTEGRATION first if you need more time."
            if sections else
            "Follow the Dreamweaver 5-part arc and keep timings proportional to the target duration."
        )

        user_prompt += f"""
**CRITICAL REQUIREMENTS:**
1. {section_timing_note}
2. Keep total length within {min_words}-{max_words} words to land near {self.duration_minutes} minutes. If you are short, add sensory detail and deepen the MAIN JOURNEY; if long, trim gently.
3. Use rate="1.0" for ALL prosody tags (never use slow rates like 0.85)
4. Use <break time="Xs"/> tags liberally for hypnotic pacing, favoring slightly longer pauses: 2-3s for normal beats, 3-5s for deeper drops, 1s for countdown ticks
5. Include rich sensory language engaging all 5 senses
6. Embed hypnotic suggestions naturally throughout
7. Include 3-5 post-hypnotic anchors in the closing

**SFX MARKERS (REQUIRED):**
- Embed natural language SFX cues using [SFX: ...] (or [[SFX:...]]). Keep each marker concise (<140 chars) and place it exactly where the sound should trigger.
- Provide at least 5 markers covering the journey arc: opening/entry tone, induction ambience, deepening texture, main journey accent(s), and integration/return chime.
- Markers must describe sound character and duration (e.g., "Deep bronze bell, warm, 3s decay"), live on their own line, and avoid SSML tags inside the marker.
- Keep markers within the <speak> body; they'll be stripped for voice synthesis but used to render the SFX track.

**OUTPUT FORMAT:**
Output ONLY the SSML script, starting with <?xml version="1.0" encoding="UTF-8"?>
Do NOT include any explanation or commentary before or after the SSML.
"""

        # Write system prompt to temp file (avoids command line length limits)
        system_prompt_file = self.session_path / "working_files" / "system_prompt.txt"
        system_prompt_file.write_text(master_prompt)

        # Also save user prompt for reference
        user_prompt_file = self.session_path / "working_files" / "script_prompt.txt"
        user_prompt_file.write_text(user_prompt)

        script_content = None
        claude_stdout = ""
        claude_stderr = ""
        result = None
        codex_stdout = ""
        codex_stderr = ""

        # 1) Primary attempt: Claude CLI
        self.log("Using Claude CLI for script generation...", "info")
        try:
            result = subprocess.run(
                [
                    'claude',
                    '-p',
                    '--system-prompt-file', str(system_prompt_file),
                    '--output-format', 'json',
                    '--max-turns', '1',
                    user_prompt
                ],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(self.project_root)
            )

            claude_stdout = result.stdout or ""
            claude_stderr = result.stderr or ""

            if result.returncode == 0 and claude_stdout.strip():
                try:
                    response_data = json.loads(claude_stdout)
                    if response_data.get("is_error") or response_data.get("error"):
                        err_detail = str(
                            response_data.get("error")
                            or response_data.get("result")
                            or response_data.get("message")
                            or ""
                        ).strip()
                        self.log(f"Claude CLI error: {err_detail or 'Unknown error'}", "error")
                    else:
                        script_content = response_data.get('result', '')
                except json.JSONDecodeError as e:
                    self.log(f"Failed to parse Claude response: {e}", "error")
                    if claude_stdout.strip():
                        script_content = claude_stdout
                        self.log("Using raw response (Claude JSON parse failed)", "warning")
            elif result.returncode != 0:
                error_msg = claude_stderr.strip()
                if not error_msg and claude_stdout.strip():
                    try:
                        parsed_stdout = json.loads(claude_stdout)
                        error_msg = str(
                            parsed_stdout.get("error")
                            or parsed_stdout.get("result")
                            or parsed_stdout.get("message")
                            or ""
                        )
                    except json.JSONDecodeError:
                        error_msg = claude_stdout.strip()
                self.log(f"Claude CLI error: {error_msg[:200] if error_msg else 'Unknown error'}", "error")
        except FileNotFoundError:
            self.log("Claude CLI not found - install Claude Code extension", "error")
            self.log("Visit: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code", "info")
        except subprocess.TimeoutExpired:
            self.log("Script generation timed out (5 min limit)", "error")
        except Exception as e:
            self.log(f"Script generation failed: {e}", "error")

        # 2) Fallback: Codex/ChatGPT CLI (only if Claude failed)
        if not script_content:
            codex_cmd = os.environ.get("CODEX_CLI_CMD", "codex")
            system_prompt_text = system_prompt_file.read_text()
            # Enforce JSON output parity with Claude: expect {"result": "<SSML>..."}
            combined_prompt = (
                f"{system_prompt_text}\n\n"
                f"User request:\n{user_prompt}\n\n"
                f"Return ONLY JSON with a single key \"result\" whose value is the SSML starting "
                f"with <?xml version=\"1.0\" encoding=\"UTF-8\"?>. No code fences, no comments.\n\n"
                f"Break pacing bias: prefer slightly longer pauses (2-3s typical, 3-5s for deepening), "
                f"with 1s ticks only for countdowns."
            )
            schema_path = self.session_path / "working_files" / "codex_output_schema.json"
            schema_path.write_text(
                '{"type":"object","properties":{"result":{"type":"string"}},'
                '"required":["result"],"additionalProperties":false}'
            )
            codex_args = [codex_cmd, "exec", "--output-schema", str(schema_path), combined_prompt]
            self.log(f"Claude failed; using Codex/ChatGPT CLI fallback: {' '.join(codex_args[:-1])}", "warning")
            try:
                codex_result = subprocess.run(
                    codex_args,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(self.project_root)
                )
                codex_stdout = codex_result.stdout or ""
                codex_stderr = codex_result.stderr or ""
                if codex_result.returncode == 0 and codex_stdout.strip():
                    try:
                        codex_data = json.loads(codex_stdout)
                        script_content = codex_data.get("result", "")
                        if not script_content and codex_stdout.strip():
                            script_content = codex_stdout
                            self.log("Using raw Codex response (missing result field)", "warning")
                    except json.JSONDecodeError:
                        script_content = codex_stdout
                        self.log("Using raw Codex response (JSON parse failed)", "warning")
                else:
                    codex_err = codex_result.stderr[:200] if codex_result.stderr else 'Unknown error'
                    self.log(f"Codex CLI error: {codex_err}", "error")
            except FileNotFoundError:
                self.log("Codex CLI not found - set CODEX_CLI_CMD or install the VS Code Codex CLI", "error")
            except subprocess.TimeoutExpired:
                self.log("Codex generation timed out (5 min limit)", "error")
            except Exception as e:
                self.log(f"Codex generation failed: {e}", "error")

        if not script_content:
            self.log("No script generated by Claude or Codex", "error")
            self.log(f"Run manually: /generate-script {self.session_name}", "info")
            self.stages_failed.append("generate_script")
            return

        # Save raw outputs for debugging and postmortem recovery
        raw_dir = self.session_path / "working_files"
        if claude_stdout:
            (raw_dir / "claude_raw_stdout.txt").write_text(claude_stdout)
        if claude_stderr:
            (raw_dir / "claude_raw_stderr.txt").write_text(claude_stderr)
        if codex_stdout:
            (raw_dir / "codex_raw_stdout.txt").write_text(codex_stdout)
        if codex_stderr:
            (raw_dir / "codex_raw_stderr.txt").write_text(codex_stderr)

        # Normalize SSML from any available output (stdout/stderr included)
        raw_sources = [
            ("primary_response", script_content),
            ("claude_stdout", claude_stdout),
            ("claude_stderr", claude_stderr),
            ("codex_stdout", codex_stdout),
            ("codex_stderr", codex_stderr),
        ]

        normalized_script = None
        chosen_raw = None
        for label, raw in raw_sources:
            candidate = self._extract_ssml_from_text(raw)
            if candidate:
                normalized_script = candidate
                chosen_raw = raw or ""
                if label != "primary_response":
                    self.log(f"Recovered SSML from {label.replace('_', ' ')}", "warning")
                break

        if not normalized_script:
            self.log("Response doesn't contain valid SSML", "error")
            self.log("Use /generate-script command to create script manually", "info")
            # Remove any partial script artifacts
            for path in [
                self.session_path / "working_files" / "script.ssml",
                self.session_path / "working_files" / "script_voice_clean.ssml",
                self.session_path / "script.ssml",
            ]:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            self.stages_failed.append("generate_script")
            return

        if chosen_raw and '<speak' in chosen_raw and '</speak>' not in chosen_raw:
            self.log("SSML missing </speak>; appended closing tag automatically", "warning")

        script_content = normalized_script

        # Clean up SSML issues from model output
        # Remove markdown fences that Claude sometimes adds
        script_content = re.sub(r'```\w*\n?', '', script_content)

        # Fix malformed break tags: <break time="3.5s/> -> <break time="3.5s"/>
        script_content = re.sub(r'<break\s+time="(\d+\.?\d*s)/>', r'<break time="\1"/>', script_content)

        # Also fix any missing closing quotes before />
        script_content = re.sub(r'time="(\d+\.?\d*s)/>', r'time="\1"/>', script_content)

        # Ensure we end at </speak> - remove any trailing content
        speak_end = script_content.rfind('</speak>')
        if speak_end != -1:
            script_content = script_content[:speak_end + len('</speak>')]

        # Strip whitespace
        script_content = script_content.strip()

        # Save the full script (with any SFX markers)
        script_path = self.session_path / "working_files" / "script.ssml"
        script_path.write_text(script_content)

        marker_count = self._count_sfx_markers(script_content)

        # Create clean version for TTS (strip SFX markers)
        clean_content = re.sub(r'\[\[?SFX:[^\]]*\]\]?\s*', '', script_content, flags=re.IGNORECASE)
        clean_path = self.session_path / "working_files" / "script_voice_clean.ssml"
        clean_path.write_text(clean_content)

        if marker_count == 0:
            self.log("No SFX markers found in generated script; regenerate with `[SFX: ...]` cues (Claude/Codex).", "error")
            self.log(f"Saved script without SFX markers: {script_path}", "warning")
            self.log(f"Created voice-clean script: {clean_path}", "info")
            self.stages_failed.append("generate_script")
            return
        elif marker_count < 4:
            self.log(f"Generated script with low SFX marker count ({marker_count}); target at least one per section.", "warning")
        else:
            self.log(f"Generated script with {marker_count} SFX markers: {script_path}", "success")

        # Estimate duration to catch short/long drafts early
        try:
            duration_estimate = estimate_duration(clean_content, speaking_rate=1.0)
            est_minutes = duration_estimate.get('total_minutes', 0)
            diff_pct = ((est_minutes - self.duration_minutes) / self.duration_minutes) * 100 if self.duration_minutes else 0
            level = "warning" if abs(diff_pct) > 10 else "info"
            self.log(
                f"Estimated script duration: {est_minutes:.1f} min vs target {self.duration_minutes} ({diff_pct:+.0f}%)",
                level
            )
        except Exception as e:
            self.log(f"Duration estimation skipped: {e}", "warning")

        self.log(f"Created voice-clean script: {clean_path}", "success")

        self.stages_completed.append("generate_script")

    def _extract_ssml_from_text(self, raw_text: Optional[str]) -> Optional[str]:
        """Extract and normalize SSML content from a raw model response."""
        if not raw_text:
            return None

        text = raw_text.strip()
        if not text:
            return None

        def _decode_candidate(possible: str) -> str:
            """Best-effort decoding of a JSON-string field."""
            try:
                return json.loads(f'"{possible}"')
            except Exception:
                try:
                    return bytes(possible, "utf-8").decode("unicode_escape")
                except Exception:
                    return possible

        candidates = []

        # Try strict JSON parsing first
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and 'result' in parsed:
                candidates.append(str(parsed['result']))
        except Exception:
            pass

        # If JSON is malformed, try to extract ALL "result" fields manually (CLI prepends other JSON)
        result_field_pattern = r'"result"\s*:\s*"(?P<content>(?:\\.|[^"\\])*)"'
        for match in re.finditer(result_field_pattern, text, re.DOTALL):
            candidates.append(_decode_candidate(match.group("content")))

        # Also grab any raw <speak> blocks that may already be present in the text
        for match in re.finditer(r'<speak[^>]*>.*?</speak>', text, re.DOTALL):
            candidates.append(match.group(0))

        # Fallback to raw text if we found nothing
        if not candidates:
            candidates.append(text)

        # Normalize/unescape each candidate
        normalized_candidates = []
        for cand in candidates:
            cand = cand.replace('\\"', '"')
            cand = cand.replace("\\n", "\n")
            cand = cand.replace("\\t", "\t")
            cand = re.sub(r'```[a-zA-Z0-9]*\n?', '', cand).strip()
            normalized_candidates.append(cand)

        # Prefer candidates with early <speak>/<\?xml> and minimal preamble noise
        def _score(candidate: str):
            has_speak = '<speak' in candidate
            has_end = '</speak>' in candidate
            # Distance from start to first xml/speak tag (lower is better)
            xml_idx = candidate.find('<?xml') if '<?xml' in candidate else float('inf')
            speak_idx = candidate.find('<speak') if has_speak else float('inf')
            return (
                0 if has_speak else 1,
                0 if has_end else 1,
                xml_idx,
                speak_idx,
                len(candidate),
            )

        text = min(normalized_candidates, key=_score)

        # Pull out the actual <speak> block to drop any surrounding chatter
        speak_block = re.search(r'<speak[^>]*>.*?</speak>', text, re.DOTALL)
        if speak_block:
            text = speak_block.group(0)
        elif '<speak' in text and '</speak>' in text:
            start = text.find('<speak')
            end = text.rfind('</speak>') + len('</speak>')
            text = text[start:end]
        elif '<speak' in text:
            # If speak start exists but no closing tag, grab from start
            text = text[text.find('<speak'):]

        # Locate SSML start
        xml_start = text.find('<?xml')
        speak_start = text.find('<speak')

        if xml_start != -1 and (speak_start == -1 or xml_start < speak_start):
            text = text[xml_start:]
        elif speak_start != -1:
            text = '<?xml version="1.0" encoding="UTF-8"?>\n' + text[speak_start:]
        else:
            stripped = text.strip()
            if not stripped:
                return None
            return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<speak>\n' + stripped + '\n</speak>').strip()

        # Ensure we end at </speak> and trim trailing noise
        if '</speak>' in text:
            text = text[: text.rfind('</speak>') + len('</speak>')]
        elif '<speak' in text:
            text = text.rstrip() + '\n</speak>'

        return text.strip() if '<speak' in text else None

    def _count_sfx_markers(self, ssml: str) -> int:
        """Count SFX markers in SSML content."""
        pattern = re.compile(r'\[\[?SFX:[^\]]+\]\]?', re.IGNORECASE)
        return len(pattern.findall(ssml or ""))

    def _stage_generate_prompts(self):
        """Generate Midjourney/SD image prompts."""
        self.log("Generating image prompts", "stage")
        self.cost_tracker.add_operation('image_prompts')

        if self.dry_run:
            self.log("Would generate image prompts", "info")
            return

        try:
            result = subprocess.run(
                [self.python_cmd, "scripts/ai/prompt_generator.py", str(self.session_path)],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                env=self._get_subprocess_env(),
            )

            if result.returncode == 0:
                self.log("Generated image prompts", "success")
                self.stages_completed.append("generate_prompts")
            else:
                self.log(f"Prompt generation warning: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"Prompt generation skipped: {e}", "warning")

    def _stage_generate_voice(self):
        """Generate voice audio from SSML."""
        self.log("Generating voice audio", "stage")
        self.cost_tracker.add_operation('voice_synthesis')

        # Prefer the clean script (no SFX markers) for TTS
        ssml_path = self.session_path / "working_files" / "script_voice_clean.ssml"
        if not ssml_path.exists():
            # Fall back to regular script if clean version doesn't exist
            ssml_path = self.session_path / "working_files" / "script.ssml"

        output_dir = self.session_path / "output"

        if not ssml_path.exists():
            self.log("No SSML script found, skipping voice generation", "warning")
            return

        # Use Coqui TTS (free, open-source alternative to Google Cloud TTS)
        coqui_python = self.project_root / "venv_coqui" / "bin" / "python"
        coqui_script = self.project_root / "scripts" / "core" / "generate_voice_coqui_simple.py"
        
        if not coqui_python.exists():
            self.log("Coqui TTS not installed. Run: python3.11 -m venv venv_coqui && venv_coqui/bin/pip install TTS pydub", "error")
            self.stages_failed.append("generate_voice")
            return

        try:
            self.log("Using Coqui TTS (this may take 10-20 minutes on CPU)...", "info")
            result = subprocess.run(
                [
                    str(coqui_python),
                    str(coqui_script),
                    str(ssml_path),
                    str(output_dir)
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=3600,  # 60 minute timeout for Coqui on CPU (resource-constrained)
                env=self._get_subprocess_env(),
            )

            if result.returncode == 0:
                self.log("Generated voice audio with Coqui TTS", "success")
                self.stages_completed.append("generate_voice")
            else:
                self.log(f"Voice generation error: {result.stderr[:200]}", "error")
                self.stages_failed.append("generate_voice")

        except subprocess.TimeoutExpired:
            self.log("Voice generation timed out (>40 minutes)", "error")
            self.stages_failed.append("generate_voice")
        except Exception as e:
            self.log(f"Voice generation failed: {e}", "error")
            self.stages_failed.append("generate_voice")

    def _get_voice_duration(self) -> float:
        """Get the actual duration of the generated voice file in seconds.

        Returns:
            Duration in seconds, or fallback to self.duration_minutes * 60
        """
        output_dir = self.session_path / "output"

        # Check voice files in preference order
        for name in ["voice_enhanced.wav", "voice_enhanced.mp3", "voice.wav", "voice.mp3"]:
            voice_file = output_dir / name
            if voice_file.exists():
                try:
                    result = subprocess.run(
                        [
                            "ffprobe", "-v", "error",
                            "-show_entries", "format=duration",
                            "-of", "default=noprint_wrappers=1:nokey=1",
                            str(voice_file)
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        duration = float(result.stdout.strip())
                        self.log(f"Voice duration detected: {duration/60:.1f} minutes", "info")
                        return duration
                except (ValueError, subprocess.TimeoutExpired, Exception) as e:
                    self.log(f"Could not read voice duration: {e}", "warning")

        # Fallback to target duration
        self.log(f"Using target duration: {self.duration_minutes} minutes", "info")
        return self.duration_minutes * 60

    def _stage_generate_binaural(self):
        """Generate binaural beats using YAML presets, manifest, or fallback."""
        self.log("Generating binaural beats", "stage")

        output_path = self.session_path / "output" / "binaural_dynamic.wav"

        # Use actual voice duration instead of fixed target
        duration_seconds = self._get_voice_duration()

        manifest_path = self.session_path / "manifest.yaml"
        base_freq = 200  # Hz carrier frequency
        beat_freq = 7    # Hz binaural beat (theta default)
        binaural_preset = None

        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                binaural = manifest.get('sound_bed', {}).get('binaural', {})
                base_freq = binaural.get('base_hz', 200)
                # Check for YAML preset name from knowledge base
                binaural_preset = binaural.get('preset')
                # Use middle of the binaural curve for fallback simplicity
                sections = binaural.get('sections', [])
                if sections:
                    beat_freq = sum(s.get('offset_hz', 7) for s in sections) / len(sections)
            except Exception:
                pass  # Use defaults

        # Priority 1: YAML preset from knowledge base (if specified in manifest)
        if binaural_preset:
            dyn_cmd = [
                self.python_cmd, "scripts/core/generate_dynamic_binaural.py",
                "--yaml-preset", binaural_preset,
                "--duration", str(duration_seconds),
                "--output", str(output_path),
            ]
            try:
                result = subprocess.run(
                    dyn_cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                    timeout=600,
                )
                if result.returncode == 0:
                    self.log(f"Generated binaural from YAML preset: {binaural_preset}", "success")
                    self.stages_completed.append("generate_binaural")
                    return
                else:
                    self.log(f"YAML preset '{binaural_preset}' failed: {result.stderr[:160]}", "warning")
            except Exception as e:
                self.log(f"YAML preset generation failed: {e}", "warning")

        # Priority 2: Manifest sections/progression (existing behavior)
        if manifest_path.exists():
            dyn_cmd = [
                self.python_cmd, "scripts/core/generate_dynamic_binaural.py",
                "--manifest", str(manifest_path),
                "--output", str(output_path),
            ]
            try:
                result = subprocess.run(
                    dyn_cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                    timeout=600,
                )
                if result.returncode == 0:
                    self.log("Generated dynamic binaural from manifest progression", "success")
                    self.stages_completed.append("generate_binaural")
                    return
                else:
                    self.log(f"Dynamic binaural warning: {result.stderr[:160]}", "warning")
            except Exception as e:
                self.log(f"Dynamic binaural generation failed, using fallback: {e}", "warning")

        # Fallback: simple stereo sine pair via FFmpeg
        left_freq = base_freq
        right_freq = base_freq + beat_freq

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency={left_freq}:duration={duration_seconds}",
            "-f", "lavfi",
            "-i", f"sine=frequency={right_freq}:duration={duration_seconds}",
            "-filter_complex", "[0:a][1:a]join=inputs=2:channel_layout=stereo",
            "-ar", "48000",
            "-acodec", "pcm_s24le",
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=180,  # allow a bit more if ffmpeg is slow
            )

            if result.returncode == 0:
                self.log(f"Generated fallback binaural ({left_freq}Hz / {right_freq}Hz)", "success")
                self.stages_completed.append("generate_binaural")
            else:
                self.log(f"Binaural generation warning: {result.stderr[:160]}", "warning")

        except Exception as e:
            self.log(f"Binaural generation skipped: {e}", "warning")

    def _stage_generate_sfx(self):
        """Render SFX track from SSML markers aligned to voice."""
        self.log("Generating SFX track", "stage")

        script_path = self.session_path / "working_files" / "script.ssml"
        output_dir = self.session_path / "output"

        # Use same voice file selection as mixing (including Coqui output)
        voice_file = None
        for name in ["voice_enhanced.wav", "voice_enhanced.mp3", "voice.wav", "voice.mp3", "voice_synth.mp3", "voice_synth.wav"]:
            candidate = output_dir / name
            if candidate.exists():
                voice_file = candidate
                break

        if not script_path.exists():
            self.log("No SSML script with SFX markers found; skipping SFX", "warning")
            return
        if not voice_file:
            self.log("No voice file available yet; skipping SFX", "warning")
            return

        sfx_output = output_dir / "sfx.wav"

        try:
            result = subprocess.run(
                [
                    self.python_cmd, "scripts/core/sfx_sync.py",
                    str(script_path),
                    str(voice_file),
                    str(sfx_output),
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=300,
            )

            if result.returncode == 0 and sfx_output.exists():
                self.log("Rendered SFX track from script markers", "success")
                self.stages_completed.append("generate_sfx")
            else:
                stdout = result.stdout or ""
                stderr = result.stderr or ""
                if "No SFX markers found" in stdout:
                    self.log("No SFX markers found in script; skipping SFX track", "info")
                else:
                    combined = stderr.strip() or stdout.strip()
                    err = combined[:160] if combined else "Unknown SFX generation error"
                    self.log(f"SFX generation warning: {err}", "warning")
        except Exception as e:
            self.log(f"SFX generation skipped: {e}", "warning")

    def _stage_mix_audio(self):
        """Mix audio layers using FFmpeg."""
        self.log("Mixing audio layers", "stage")

        output_dir = self.session_path / "output"
        mixed_file = output_dir / "session_mixed.wav"

        # Find voice file (prefer enhanced, fall back to others including Coqui output)
        voice_file = None
        for name in ["voice_enhanced.wav", "voice_enhanced.mp3", "voice.wav", "voice.mp3", "voice_synth.mp3", "voice_synth.wav"]:
            candidate = output_dir / name
            if candidate.exists():
                voice_file = candidate
                break

        if not voice_file:
            self.log("No voice file found, skipping mix", "warning")
            return

        binaural_file = output_dir / "binaural_dynamic.wav"
        sfx_file = output_dir / "sfx.wav"

        # Build FFmpeg command based on available files
        cmd = ["ffmpeg", "-y"]
        filters = []
        stream_aliases = []

        def add_input(path: Path, alias: str, gain_db: float):
            idx = len(stream_aliases)
            cmd.extend(["-i", str(path)])
            filters.append(f"[{idx}:a]volume={gain_db}dB[{alias}]")
            stream_aliases.append(alias)

        # Always include voice
        add_input(voice_file, "voice", -6.0)

        if binaural_file.exists():
            add_input(binaural_file, "bin", -6.0)
        if sfx_file.exists():
            add_input(sfx_file, "sfx", -12.0)

        if len(stream_aliases) == 1:
            # Voice only - simple volume normalize
            cmd = [
                "ffmpeg", "-y",
                "-i", str(voice_file),
                "-af", "volume=-6dB",
                "-acodec", "pcm_s16le",
                str(mixed_file)
            ]
            self.log("Voice only (no binaural/SFX found)", "warning")
        else:
            amix_inputs = "".join(f"[{a}]" for a in stream_aliases)
            # Use duration=first so final mix matches voice duration (voice is always first input)
            filters.append(f"{amix_inputs}amix=inputs={len(stream_aliases)}:duration=first:normalize=0[mixed]")
            filter_complex = ";".join(filters)
            cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "[mixed]",
                "-acodec", "pcm_s16le",
                str(mixed_file)
            ])
            self.log(f"Mixing stems: {', '.join(stream_aliases)}", "info")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600,
            )

            if result.returncode == 0:
                self.log("Mixed audio layers", "success")
                self.stages_completed.append("mix_audio")
            else:
                self.log(f"Audio mixing error: {result.stderr[:200]}", "error")
                self.stages_failed.append("mix_audio")

        except Exception as e:
            self.log(f"Audio mixing failed: {e}", "error")
            self.stages_failed.append("mix_audio")

    def _stage_hypnotic_post_process(self):
        """Apply hypnotic post-processing (MANDATORY)."""
        self.log("Applying hypnotic post-processing (FFmpeg mode for low memory)", "stage")

        try:
            result = subprocess.run(
                [
                    self.python_cmd, "scripts/core/hypnotic_post_process.py",
                    "--session", str(self.session_path) + "/",
                    "--ffmpeg-only"  # Use FFmpeg mode to avoid OOM on long sessions
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600,
            )

            if result.returncode == 0:
                self.log("Applied hypnotic post-processing", "success")
                self.stages_completed.append("hypnotic_post_process")
            else:
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                self.log(f"Post-processing FAILED: {error_msg}", "error")
                print(f"STAGE_FATAL: hypnotic_post_process failed: {error_msg}", file=sys.stderr)
                self.stages_failed.append("hypnotic_post_process")
                raise RuntimeError(f"Hypnotic post-processing failed (required for MASTER audio): {error_msg}")

        except subprocess.TimeoutExpired:
            self.log("Post-processing timed out after 10 minutes", "error")
            self.stages_failed.append("hypnotic_post_process")
            raise RuntimeError("Hypnotic post-processing timed out")
        except RuntimeError:
            raise  # Re-raise our own errors
        except Exception as e:
            self.log(f"Post-processing failed: {e}", "error")
            self.stages_failed.append("hypnotic_post_process")
            raise RuntimeError(f"Hypnotic post-processing failed: {e}")

    def _stage_generate_vtt(self):
        """Generate VTT subtitles."""
        self.log("Generating VTT subtitles", "stage")
        self.cost_tracker.add_operation('vtt_generation')

        try:
            result = subprocess.run(
                [self.python_cmd, "scripts/ai/vtt_generator.py", str(self.session_path)],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=300,
            )

            if result.returncode == 0:
                self.log("Generated VTT subtitles", "success")
                self.stages_completed.append("generate_vtt")
            else:
                self.log(f"VTT generation warning: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"VTT generation skipped: {e}", "warning")

    def _stage_generate_images(self):
        """Generate scene images using configured method (sd, stock, midjourney, pil, or random)."""
        self.log("Generating scene images", "stage")
        self.log(f"Image method: {self.image_method}", "info")

        method = self.image_method
        success = False

        try:
            # NEW: Use random images from project images folder if method is 'random'
            if method == "random":
                success = self._copy_random_images()
            else:
                success = self._try_generate_images(method)

            # If SD failed, log guidance but don't fail the pipeline
            if not success and method == "sd":
                self.log("SD generation failed - video assembly will be skipped", "warning")
                self.log("To add images manually: place PNGs in images/uploaded/", "info")

        except Exception as e:
            self.log(f"Image generation error: {e}", "warning")

        if success:
            self.stages_completed.append("generate_images")

    def _copy_random_images(self) -> bool:
        """Copy random images from project images folder to session uploaded folder.
        
        Returns:
            True if images were successfully copied, False otherwise.
        """
        source_dir = self.project_root / "images"
        target_dir = self.session_path / "images" / "uploaded"
        
        # Ensure target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all image files from source directory
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
        source_images = []
        for ext in image_extensions:
            source_images.extend(source_dir.glob(ext))
        
        if not source_images:
            self.log(f"No images found in {source_dir}", "error")
            return False
        
        # Determine how many images we need
        # Try to get count from manifest sections, default to 5-8 images
        manifest_path = self.session_path / "manifest.yaml"
        num_images = random.randint(5, 8)  # default
        
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                    sections = manifest.get('sections', [])
                    if sections:
                        num_images = len(sections)
            except Exception as e:
                self.log(f"Could not read manifest for image count: {e}", "warning")
        
        # Don't request more images than we have available
        num_images = min(num_images, len(source_images))
        
        # Randomly select images
        selected_images = random.sample(source_images, num_images)
        
        self.log(f"Copying {num_images} random images from project folder", "info")
        
        # Copy images with sequential naming, converting to PNG format
        copied_count = 0
        for i, source_image in enumerate(selected_images, 1):
            # Create a clean filename: scene_01.png, scene_02.png, etc.
            target_filename = f"scene_{i:02d}.png"
            target_path = target_dir / target_filename

            try:
                # Convert to PNG format for consistency (video assembly expects PNG)
                with Image.open(source_image) as img:
                    # Convert to RGB if needed (handles RGBA, palette modes, etc.)
                    if img.mode in ('RGBA', 'LA'):
                        # Preserve transparency by keeping RGBA
                        img.save(target_path, 'PNG')
                    elif img.mode == 'P':
                        # Palette mode - convert to RGB
                        img = img.convert('RGB')
                        img.save(target_path, 'PNG')
                    else:
                        # RGB or L mode - save directly
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(target_path, 'PNG')
                copied_count += 1
                self.log(f"  [{i}/{num_images}] Converted {source_image.name} -> {target_filename}", "info")
            except Exception as e:
                # Fallback to simple copy if conversion fails
                try:
                    shutil.copy2(source_image, target_path)
                    copied_count += 1
                    self.log(f"  [{i}/{num_images}] Copied {source_image.name} -> {target_filename} (no conversion)", "warning")
                except Exception as copy_error:
                    self.log(f"  Failed to process {source_image.name}: {e}", "warning")
        
        if copied_count > 0:
            self.log(f"Successfully copied {copied_count} images", "success")
            return True
        else:
            self.log("No images were copied", "error")
            return False

    def _try_generate_images(self, method: str) -> bool:
        """Attempt image generation with specified method. Returns True on success."""
        try:
            cmd = [
                self.python_cmd, "scripts/core/generate_scene_images.py",
                str(self.session_path) + "/",
                "--method", method,
            ]

            # Add method-specific arguments
            if method == "stock":
                cmd.extend(["--platform", self.stock_platform, "--stock-guide"])
                self.log(f"Using stock images from {self.stock_platform} (non-interactive)", "info")
            elif method == "sd":
                self.log(f"Using Stable Diffusion for local image generation (performance={self.image_performance})", "info")
                cmd.extend(["--performance", self.image_performance])
            elif method == "midjourney":
                self.log("Generating Midjourney prompts only", "info")
            elif method == "pil":
                self.log("Using PIL procedural image generation", "info")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=3600,  # 60 min for image generation
            )

            stderr = result.stderr or ""
            stdout = result.stdout or ""
            combined_output = (stderr.strip() or stdout.strip())

            if result.returncode == 0:
                # Check if actual images were generated (not just guides/prompts)
                images_dir = self.session_path / "images" / "uploaded"
                has_images = images_dir.exists() and list(images_dir.glob("*.png"))

                if method == "stock":
                    self.log("Generated stock image search guide", "success")
                    self.log(f"Manual step: Source images using {self.session_path}/stock-image-guide.md", "info")
                    return True  # Guide generated successfully
                elif method == "midjourney":
                    self.log("Generated Midjourney prompts", "success")
                    self.log("Manual step: Create images in Midjourney, place in images/uploaded/", "info")
                    return True  # Prompts generated successfully
                elif has_images:
                    self.log(f"Generated scene images ({method})", "success")
                    return True
                else:
                    self.log(f"No images generated by {method}", "warning")
                    return False
            else:
                error_msg = combined_output[:200] if combined_output else 'Unknown error'
                self.log(f"Image generation failed ({method}): {error_msg}", "warning")
                if method in ("sd", "sdxl") and combined_output:
                    lowered = combined_output.lower()
                    if "diffusers" in lowered or "torch" in lowered or "sdxl generator" in lowered:
                        self.log(
                            "Install SD dependencies: pip install diffusers transformers accelerate torch Pillow",
                            "info"
                        )
                return False

        except subprocess.TimeoutExpired:
            self.log(f"Image generation timed out ({method})", "warning")
            if method == "sd":
                # Fast fallback to avoid blank video
                self.log("Falling back to PIL procedural images after SD timeout", "info")
                return self._try_generate_images("pil")
            return False
        except Exception as e:
            self.log(f"Image generation error ({method}): {e}", "warning")
            return False

    def _stage_assemble_video(self):
        """Assemble final video."""
        self.log("Assembling video", "stage")

        # Check if we have images and audio
        images_dir = self.session_path / "images" / "uploaded"
        audio_file = self.session_path / "output" / f"{self.session_name}_MASTER.mp3"

        if not audio_file.exists():
            # Try alternative names
            for f in (self.session_path / "output").glob("*_MASTER.mp3"):
                audio_file = f
                break

        if not images_dir.exists() or not list(images_dir.glob("*.png")):
            self.log("No images found, skipping video assembly", "warning")
            return

        if not audio_file.exists():
            self.log("No master audio found, skipping video assembly", "warning")
            return

        try:
            result = subprocess.run(
                [
                    self.python_cmd, "scripts/core/assemble_session_video.py",
                    "--session", str(self.session_path) + "/",
                    "--audio", str(audio_file)
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=1800,
            )

            if result.returncode == 0:
                self.log("Assembled video", "success")
                self.stages_completed.append("assemble_video")
            else:
                self.log(f"Video assembly warning: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"Video assembly skipped: {e}", "warning")

    def _stage_package_youtube(self):
        """Create YouTube package with SEO context from knowledge base."""
        self.log("Creating YouTube package", "stage")

        try:
            youtube_output_dir = self.session_path / "output" / "youtube_package"
            youtube_output_dir.mkdir(parents=True, exist_ok=True)

            # NEW: Retrieve YouTube SEO context from knowledge base
            seo_context_str = ""
            try:
                from scripts.ai.knowledge_tools import get_youtube_seo_context

                # Load manifest to get outcome
                manifest_path = self.session_path / "manifest.yaml"
                outcome = None
                if manifest_path.exists():
                    with open(manifest_path, 'r') as f:
                        manifest = yaml.safe_load(f)
                        outcome = manifest.get('desired_outcome')

                seo_context = get_youtube_seo_context(
                    topic=self.topic,
                    outcome=outcome
                )
                seo_context_str = seo_context.get('formatted_context', '')

                if seo_context_str and seo_context_str != "(No SEO knowledge found)":
                    self.log("Retrieved SEO knowledge from RAG", "info")

                    # Save SEO context for reference
                    seo_file = youtube_output_dir / "SEO_CONTEXT.md"
                    seo_file.write_text(f"""# YouTube SEO Context from Knowledge Base

Topic: {self.topic}
Outcome: {outcome or 'N/A'}

---

{seo_context_str}

---

*Use this context to optimize your YouTube title, description, tags, and thumbnail.*
*Generated from your Notion knowledge base via RAG.*
""")
                    self.log(f"Saved SEO context: {seo_file.name}", "info")

            except Exception as e:
                self.log(f"SEO context retrieval skipped: {e}", "warning")

            # NEW: Load or retrieve competitor context for YouTube optimization
            competitor_context_str = ""
            try:
                # First try saved context from manifest stage
                competitor_context_path = self.session_path / "working_files" / "competitor_context.yaml"
                if competitor_context_path.exists():
                    with open(competitor_context_path, 'r') as f:
                        saved_context = yaml.safe_load(f)
                        competitor_context_str = saved_context.get('formatted_context', '')
                        if competitor_context_str:
                            self.log("Loaded competitor context from manifest stage", "info")

                # If no saved context, retrieve fresh
                if not competitor_context_str:
                    from scripts.ai.knowledge_tools import (
                        get_competitor_insights,
                        get_tag_recommendations,
                        get_retention_benchmarks
                    )

                    # Get competitor insights
                    insights = get_competitor_insights(limit=5)
                    competitor_context_str = insights.get('formatted_context', '')

                    # Get tag recommendations
                    tags = get_tag_recommendations(topic=self.topic)
                    if tags.get('formatted_context'):
                        competitor_context_str += "\n\n" + tags['formatted_context']

                    # Get retention benchmarks
                    benchmarks = get_retention_benchmarks(
                        duration_minutes=getattr(self, 'duration_minutes', 25)
                    )
                    if benchmarks.get('formatted_context'):
                        competitor_context_str += "\n\n" + benchmarks['formatted_context']

                    if competitor_context_str:
                        self.log("Retrieved fresh competitor context", "info")

                # Save competitor context for reference
                if competitor_context_str:
                    competitor_file = youtube_output_dir / "COMPETITOR_INSIGHTS.md"
                    competitor_file.write_text(f"""# YouTube Competitor Insights

Topic: {self.topic}

---

{competitor_context_str}

---

*Use these insights to optimize your YouTube title, description, tags, and thumbnail.*
*Generated from YouTube competitor analysis.*
""")
                    self.log(f"Saved competitor insights: {competitor_file.name}", "info")

            except Exception as e:
                self.log(f"Competitor context retrieval skipped: {e}", "warning")

            result = subprocess.run(
                [
                    self.python_cmd, "scripts/core/package_youtube.py",
                    "--session", str(self.session_path) + "/",
                    "--output-dir", str(youtube_output_dir),
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=300,
            )

            if result.returncode == 0:
                self.log("Created YouTube package", "success")
                self.stages_completed.append("package_youtube")
            else:
                self.log(f"YouTube packaging warning: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"YouTube packaging skipped: {e}", "warning")

    def _stage_generate_thumbnail(self):
        """Generate optimized YouTube thumbnail using Ultimate Thumbnail Generator."""
        self.log("Generating optimized YouTube thumbnail", "stage")

        try:
            # Use the ultimate thumbnail generator for auto-optimized output
            result = subprocess.run(
                [
                    self.python_cmd, "scripts/core/generate_ultimate_thumbnail.py",
                    str(self.session_path),
                    "--variants", "1",  # Single optimized thumbnail for auto-generation
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=120,
            )

            stdout = result.stdout or ""
            stderr = result.stderr or ""

            if result.returncode == 0:
                self.log("Generated optimized YouTube thumbnail", "success")
                self.stages_completed.append("generate_thumbnail")

                # Check if thumbnail was copied to youtube_package
                youtube_pkg = self.session_path / "output" / "youtube_package"
                if youtube_pkg.exists():
                    thumb_in_pkg = youtube_pkg / "thumbnail.png"
                    if thumb_in_pkg.exists():
                        self.log("Thumbnail copied to youtube_package/", "info")
            else:
                err_msg = stderr[:200] if stderr else stdout[:200] if stdout else "Unknown error"
                self.log(f"Thumbnail generation warning: {err_msg}", "warning")
                # Don't fail the pipeline - thumbnails can be generated manually
                self.log("Use /generate-thumbnail command to create thumbnail manually", "info")

        except subprocess.TimeoutExpired:
            self.log("Thumbnail generation timed out", "warning")
        except FileNotFoundError:
            self.log("Thumbnail generator script not found", "warning")
            self.log("Run: python3 scripts/core/generate_ultimate_thumbnail.py sessions/{session}/", "info")
        except Exception as e:
            self.log(f"Thumbnail generation skipped: {e}", "warning")

    def _stage_upload_website(self):
        """Upload session to salars.net website."""
        self.log("Uploading to website (salars.net)", "stage")

        # Check for required files
        master_audio = None
        for f in (self.session_path / "output").glob("*_MASTER.mp3"):
            master_audio = f
            break

        if not master_audio:
            self.log("No master audio found - cannot upload to website (hypnotic_post_process may have failed)", "error")
            self.stages_failed.append("upload_website")
            return

        try:
            # Need PYTHONPATH for the import to work properly
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root)

            result = subprocess.run(
                [
                    self.python_cmd, "scripts/core/upload_to_website.py",
                    "--session", str(self.session_path) + "/",
                    "--no-git"
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600,
                env=env,
            )

            if result.returncode == 0:
                self.log("Uploaded to website", "success")
                self.stages_completed.append("upload_website")
                # Parse and log the URL if available
                if "salars.net/dreamweavings/" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "salars.net/dreamweavings/" in line:
                            self.log(f"URL: {line.strip()}", "info")
                            break
            else:
                # Capture and log detailed error information
                stdout_output = (result.stdout or "").strip()
                stderr_output = (result.stderr or "").strip()

                # Look for FATAL or error lines in stdout (where upload_to_website.py prints errors)
                error_found = False
                if stdout_output:
                    for line in stdout_output.split('\n'):
                        if 'FATAL' in line or 'Error:' in line or 'error:' in line.lower():
                            self.log(f"Upload error: {line.strip()[:300]}", "error")
                            error_found = True
                            break

                # If no specific error found, log last part of output
                if not error_found:
                    combined = stderr_output or stdout_output
                    snippet = combined[-500:] if combined else "Upload returned non-zero exit code"
                    self.log(f"Website upload failed: {snippet}", "error")

                # Also log stderr if present (for Python tracebacks)
                if stderr_output and stderr_output != stdout_output:
                    self.log(f"Upload stderr: {stderr_output[:500]}", "debug")

                self.stages_failed.append("upload_website")

        except subprocess.TimeoutExpired:
            self.log("Website upload timed out after 10 minutes", "error")
            self.stages_failed.append("upload_website")
        except Exception as e:
            self.log(f"Website upload failed: {e}", "error")
            self.stages_failed.append("upload_website")

    def _stage_cleanup(self):
        """Cleanup intermediate files to save disk space."""
        if self.nightly:
            self.log("Cleaning up ALL files (nightly/aggressive mode)", "stage")
        else:
            self.log("Cleaning up intermediate files", "stage")

        try:
            cmd = [
                self.python_cmd, "scripts/core/cleanup_session.py",
                str(self.session_path) + "/"
            ]
            # In nightly mode, use aggressive cleanup to remove everything
            if self.nightly:
                cmd.append("--aggressive")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=120,
            )

            if result.returncode == 0:
                self.log("Cleaned up intermediate files", "success")
                self.stages_completed.append("cleanup")
                # Parse disk savings if available
                if "saved" in result.stdout.lower() or "freed" in result.stdout.lower():
                    for line in result.stdout.split('\n'):
                        if "saved" in line.lower() or "freed" in line.lower():
                            self.log(f"Space: {line.strip()}", "info")
                            break
            else:
                self.log(f"Cleanup warning: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"Cleanup skipped: {e}", "warning")

    def _stage_self_improvement(self):
        """Record lessons learned and update knowledge base."""
        self.log("Recording lessons learned", "stage")

        lessons_file = self.project_root / "knowledge" / "lessons_learned.yaml"

        # Load existing lessons
        lessons = []
        if lessons_file.exists():
            try:
                with open(lessons_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    lessons = data.get('lessons', [])
            except Exception:
                lessons = []

        # Generate new lesson entry for this session
        new_lesson = {
            'id': f"L{len(lessons) + 1:03d}",
            'date': datetime.now().strftime('%Y-%m-%d'),
            'session': self.session_name,
            'category': 'automation',
            'source': 'auto_generate',
            'summary': f"Auto-generated session from topic: {self.topic}",
            'details': {
                'topic': self.topic,
                'mode': self.mode,
                'duration_target': self.duration_minutes,
                'stages_completed': len(self.stages_completed),
                'stages_failed': len(self.stages_failed),
                'execution_time_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
                'estimated_cost_usd': self.cost_tracker.get_total(),
            },
            'learnings': [],
            'applied': False,
        }

        # Add specific learnings based on pipeline results
        if 'generate_voice' in self.stages_completed:
            new_lesson['learnings'].append("Voice generation successful with Neural2-H")
        if 'hypnotic_post_process' in self.stages_completed:
            new_lesson['learnings'].append("Hypnotic post-processing applied successfully")
        if self.stages_failed:
            new_lesson['learnings'].append(f"Failed stages: {', '.join(self.stages_failed)}")
            new_lesson['category'] = 'debugging'

        # Track which lessons were applied
        if self.applied_lessons:
            new_lesson['applied_lessons'] = self.applied_lessons
            new_lesson['learnings'].append(f"Applied {len(self.applied_lessons)} ranked lessons from recursive improvement system")

        # Append and save
        lessons.append(new_lesson)

        try:
            with open(lessons_file, 'w') as f:
                yaml.dump({'lessons': lessons}, f, default_flow_style=False, sort_keys=False)

            self.log(f"Recorded lesson {new_lesson['id']}", "success")
        except Exception as e:
            self.log(f"Failed to record lesson: {e}", "warning")

        # Record outcome to recursive improvement system
        try:
            agent = _get_recursive_agent()
            if agent and self.applied_lessons:
                # Calculate quality score based on completion rate
                total_stages = len(self.stages_completed) + len(self.stages_failed)
                quality_score = (len(self.stages_completed) / max(total_stages, 1)) * 100 if total_stages > 0 else 50.0

                metrics = {
                    'generation_success': len(self.stages_failed) == 0,
                    'quality_score': quality_score,
                    'stages_completed': self.stages_completed,
                    'stages_failed': self.stages_failed,
                    'execution_time_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
                    'estimated_cost_usd': self.cost_tracker.get_total(),
                }

                # Create AppliedLessons container
                from scripts.ai.agents.dreamweaver_recursive import AppliedLessons
                applied = AppliedLessons(
                    lesson_ids=self.applied_lessons,
                    lessons_context=self.lessons_context,
                    categories={},
                )

                outcome_id = agent.record_generation_outcome(
                    session_name=self.session_name,
                    applied_lessons=applied,
                    metrics=metrics,
                    youtube_video_id=None,  # Set later when video is uploaded to YouTube
                    manifest_path=self.session_path / "manifest.yaml",
                )

                # Update manifest with applied lessons
                agent.update_manifest_with_lessons(
                    manifest_path=self.session_path / "manifest.yaml",
                    applied_lessons=applied,
                )

                self.log(f"Recorded outcome {outcome_id} to recursive improvement system", "success")
        except Exception as e:
            self.log(f"Warning: Could not record recursive improvement outcome: {e}", "warning")

        # Update archetype history for diversity tracking
        self._update_archetype_history()

        self.stages_completed.append("self_improvement")

    def _update_archetype_history(self):
        """Update archetype history for diversity tracking across sessions.

        This ensures the archetype selector can apply recency penalties
        and avoid selecting the same archetypes in consecutive sessions.
        """
        try:
            # Load manifest to get archetypes
            manifest_path = self.session_path / "manifest.yaml"
            if not manifest_path.exists():
                self.log("No manifest found, skipping archetype history update", "warning")
                return

            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)

            archetypes_data = manifest.get('archetypes', [])
            if not archetypes_data:
                self.log("No archetypes in manifest, skipping history update", "info")
                return

            # Get outcome/style from manifest
            session_info = manifest.get('session', {})
            outcome = session_info.get('style', 'transformation')

            # Initialize selector for codex lookup
            selector = ArchetypeSelector(project_root=self.project_root)

            # Convert manifest archetypes to SelectedArchetype objects
            selected_archetypes = []

            for arch_data in archetypes_data:
                arch_name = arch_data.get('name', '')
                arch_role = arch_data.get('role', 'support')

                # Try to find the canonical archetype ID from the codex
                # The codex uses format: family.archetype_name
                arch_id, family = self._lookup_archetype_id(selector, arch_name)

                selected_arch = SelectedArchetype(
                    archetype_id=arch_id,
                    name=arch_name,
                    family=family,
                    role=arch_role,
                    encounter_type='first_encounter',  # Default, will be updated by history
                    relationship_level=1,
                    appearance_section=arch_data.get('appearance_section', 'journey'),
                    templates={},
                    attributes={},
                    description=arch_data.get('description', ''),
                    symbol=arch_data.get('symbol', ''),
                    qualities=arch_data.get('qualities', []),
                )
                selected_archetypes.append(selected_arch)

            # Update history
            selector.update_history(
                session_id=self.session_name,
                archetypes_used=selected_archetypes,
                session_outcome=outcome,
                notes=f"Auto-generated from topic: {self.topic}"
            )

            self.log(f"Updated archetype history with {len(selected_archetypes)} archetypes", "success")

        except Exception as e:
            self.log(f"Failed to update archetype history: {e}", "warning")

    def _lookup_archetype_id(self, selector: ArchetypeSelector, archetype_name: str) -> tuple:
        """Look up the canonical archetype ID from the codex.

        Args:
            selector: ArchetypeSelector instance with loaded codex
            archetype_name: Display name (e.g., "The Great Physician")

        Returns:
            Tuple of (archetype_id, family)
        """
        # Normalize the name for matching
        name_normalized = archetype_name.lower().replace('the ', '').replace(' ', '_')

        # Search codex for matching archetype
        for arch_id, arch_data in selector.codex.items():
            codex_name = arch_data.get('name', '').lower().replace('the ', '').replace(' ', '_')
            if codex_name == name_normalized or name_normalized in arch_id:
                return arch_id, arch_data.get('family', 'general')

        # Fallback: construct ID using family inference
        family = self._infer_archetype_family(archetype_name)
        simple_id = name_normalized
        return f"{family}.{simple_id}", family

    def _infer_archetype_family(self, archetype_name: str) -> str:
        """Infer archetype family from name for history tracking."""
        name_lower = archetype_name.lower()

        # Map common archetypes to families
        family_keywords = {
            'divine_light_healing': ['healer', 'physician', 'healing', 'light'],
            'transformation_alchemy': ['phoenix', 'renewal', 'transformation', 'alchemist'],
            'warrior_power': ['warrior', 'michael', 'strength', 'power', 'guardian'],
            'sacred_feminine': ['mother', 'goddess', 'feminine', 'rose', 'mary'],
            'wisdom_guidance': ['sage', 'wisdom', 'guide', 'mentor', 'teacher'],
            'shadow_integration': ['shadow', 'dark', 'underworld', 'death'],
            'nature_spirits': ['nature', 'forest', 'animal', 'earth', 'green'],
            'cosmic_consciousness': ['cosmic', 'star', 'celestial', 'universal'],
        }

        for family, keywords in family_keywords.items():
            if any(kw in name_lower for kw in keywords):
                return family

        return 'general'

    def _generate_report(self) -> Dict:
        """Generate execution report."""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        report = {
            'session_name': self.session_name,
            'topic': self.topic,
            'topic_source': self.topic_source,
            'mode': self.mode,
            'duration_minutes': self.duration_minutes,
            'audio_only': self.audio_only,
            'dry_run': self.dry_run,
            'execution': {
                'started': self.start_time.isoformat() if self.start_time else None,
                'ended': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': round(duration, 1),
            },
            'stages': {
                'completed': self.stages_completed,
                'failed': self.stages_failed,
                'total': len(self.stages_completed) + len(self.stages_failed),
            },
            'costs': self.cost_tracker.get_report(),
            'outputs': {
                'session_path': str(self.session_path),
                'manifest': str(self.session_path / "manifest.yaml"),
                'script': str(self.session_path / "working_files" / "script.ssml"),
            },
        }

        # Add output files if they exist
        if not self.dry_run:
            output_files = []
            for f in (self.session_path / "output").glob("*"):
                if f.is_file():
                    output_files.append(str(f.relative_to(self.session_path)))
            report['outputs']['files'] = output_files

        return report

    def _save_report(self, report: Dict):
        """Save execution report."""
        if self.dry_run:
            return

        report_path = self.session_path / "working_files" / "auto_generate_report.yaml"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)

        self.log(f"Report saved: {report_path}", "info")

    def print_summary(self, report: Dict):
        """Print execution summary."""
        print("\n" + "=" * 60)
        print(f"AUTO-GENERATE SUMMARY: {report['session_name']}")
        print("=" * 60)

        status = "SUCCESS" if not report['stages']['failed'] else "PARTIAL"
        print(f"Status: {status}")
        print(f"Topic: {report['topic']}")
        print(f"Topic Source: {report.get('topic_source', 'manual')}")
        print(f"Mode: {report['mode']}")
        print(f"Duration: {report['execution']['duration_seconds']:.1f}s")

        print(f"\nStages Completed: {len(report['stages']['completed'])}")
        for stage in report['stages']['completed']:
            print(f"  ✓ {stage}")

        if report['stages']['failed']:
            print(f"\nStages Failed: {len(report['stages']['failed'])}")
            for stage in report['stages']['failed']:
                print(f"  ✗ {stage}")

        # Handle both full report and plan-only report formats
        if 'costs' in report:
            print(f"\nEstimated Cost: ${report['costs']['total_usd']:.2f}")
        elif 'plan' in report:
            # Plan-only report (dry-run mode)
            plan = report['plan']
            print(f"\nPlan Summary:")
            print(f"  Cost Estimate: ${plan.get('cost_estimate_usd', 0):.2f}")
            print(f"  Stages Planned: {plan.get('stages_count', 0)}")
            print(f"  Est. Duration: {plan.get('estimated_duration_minutes', 0)} min")
            print(f"  Feasibility: {plan.get('feasibility_score', 0):.0%}")
            if plan.get('blockers'):
                print(f"\n  Blockers:")
                for blocker in plan['blockers']:
                    print(f"    ✗ {blocker}")
            if plan.get('warnings'):
                print(f"\n  Warnings:")
                for warning in plan['warnings']:
                    print(f"    ⚠ {warning}")
            print(f"\n  Plan saved to: {plan.get('path', 'N/A')}")
            return  # Skip rest of summary for plan-only mode

        if 'outputs' in report:
            print(f"\nSession Path: {report['outputs']['session_path']}")

        if not report['dry_run']:
            print("\nNext Steps:")
            if 'upload_website' in report['stages']['completed']:
                print("  ✓ Session uploaded to salars.net")
            else:
                print("  1. Review/edit the SSML script")
                print("  2. Generate images (if needed)")
                print("  3. Run /build-audio to regenerate audio")
                print("  4. Run /build-video when images are ready")
                print("  5. Upload to website with upload_to_website.py")
            if 'cleanup' in report['stages']['completed']:
                print("  ✓ Intermediate files cleaned up")
            if 'self_improvement' in report['stages']['completed']:
                print("  ✓ Lessons recorded to knowledge base")


def main():
    parser = argparse.ArgumentParser(
        description='Auto-generate complete dreamweaving session from topic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 scripts/ai/auto_generate.py --topic "Finding Inner Peace"
    python3 scripts/ai/auto_generate.py --topic "Deep Sleep" --duration 45 --mode budget
    python3 scripts/ai/auto_generate.py --topic "Cosmic Journey" --image-method sd
    python3 scripts/ai/auto_generate.py --topic "Nature Walk" --stock-platform pexels
    python3 scripts/ai/auto_generate.py --topic "Confidence" --audio-only
    python3 scripts/ai/auto_generate.py --topic "Healing" --dry-run

Note: Requires Claude Code extension for VS Code (uses your Claude subscription).
        """
    )

    parser.add_argument('--topic', '-t', required=False,
                       help='Topic/theme for the session (optional when using interactive selector)')
    parser.add_argument('--topic-source', default='prompt',
                       choices=['prompt', 'manual', 'notion'],
                       help='Topic selection mode: prompt (interactive), manual (use --topic directly), notion (auto-pick unused from Notion)')
    parser.add_argument('--notion-root', default=os.getenv("NOTION_ROOT_PAGE_ID", DEFAULT_NOTION_ROOT_PAGE_ID),
                       help='Root Notion page ID to scan for topics (defaults to Sacred Digital Dreamweaver page)')
    parser.add_argument('--mode', '-m', default='standard',
                       choices=['budget', 'standard', 'premium'],
                       help='Cost optimization mode (default: standard)')
    parser.add_argument('--duration', '-d', type=int, default=30,
                       help='Target duration in minutes (default: 30)')
    parser.add_argument('--name', '-n',
                       help='Custom session name (auto-generated if not provided)')
    parser.add_argument('--audio-only', action='store_true',
                       help='Skip video stages')
    parser.add_argument('--dry-run', action='store_true',
                       help='Plan only, do not create files')
    parser.add_argument('--skip-upload', action='store_true',
                       help='Skip uploading to salars.net website')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Keep all intermediate files (skip cleanup)')
    parser.add_argument('--no-learning', action='store_true',
                       help='Skip recording lessons learned')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimal output')
    parser.add_argument('--json', action='store_true',
                       help='Output report as JSON')
    parser.add_argument('--image-method', default='sd',
                       choices=['stock', 'sd', 'midjourney', 'pil', 'random'],
                       help='Image sourcing method: sd (default, Stable Diffusion), stock (guide only), midjourney (prompts only), pil (fast procedural), random (use existing project images)')
    parser.add_argument('--image-performance', default='speed',
                        choices=['quality', 'balanced', 'speed', 'turbo'],
                        help='Stable Diffusion performance preset (default: speed)')
    parser.add_argument('--stock-platform', default='unsplash',
                       choices=['unsplash', 'pexels', 'pixabay'],
                       help='Stock image platform (default: unsplash)')
    parser.add_argument('--nightly', action='store_true',
                       help='Nightly mode: skip YouTube package, aggressive cleanup (remove everything)')
    parser.add_argument('--skip-youtube', action='store_true',
                       help='Skip YouTube package stage (video/thumbnail still generated)')

    args = parser.parse_args()

    topic, topic_source = prompt_for_topic(
        cli_topic=args.topic,
        topic_source=args.topic_source,
        notion_root=args.notion_root,
    )

    generator = AutoGenerator(
        topic=topic,
        topic_source=topic_source,
        mode=args.mode,
        duration_minutes=args.duration,
        audio_only=args.audio_only,
        dry_run=args.dry_run,
        verbose=not args.quiet,
        session_name=args.name,
        skip_upload=args.skip_upload,
        no_cleanup=args.no_cleanup,
        no_learning=args.no_learning,
        image_method=args.image_method,
        image_performance=args.image_performance,
        stock_platform=args.stock_platform,
        nightly=args.nightly,
        skip_youtube=args.skip_youtube,
    )

    report = generator.run()

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        generator.print_summary(report)

    # Exit code based on success
    sys.exit(0 if not report['stages']['failed'] else 1)


if __name__ == "__main__":
    main()
