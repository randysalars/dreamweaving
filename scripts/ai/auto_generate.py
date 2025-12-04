#!/usr/bin/env python3
"""
Auto-Generate: Complete Topic-to-YouTube Pipeline

Orchestrates the complete session production from just a topic:
1. Create session directory structure
2. Generate manifest from topic using CreativeWorkflow
3. Generate SSML script (placeholder - requires AI integration)
4. Generate Midjourney/SD prompts
5. Generate voice audio
6. Generate binaural beats
7. Mix and master audio
8. Apply hypnotic post-processing
9. Generate VTT subtitles
10. Assemble video (when images available)
11. Package for YouTube
12. Upload to website (salars.net)
13. Cleanup intermediate files
14. Self-improvement/learning (record lessons learned)

Usage:
    # Standard generation
    python3 scripts/ai/auto_generate.py --topic "Finding Inner Peace" --mode standard

    # With custom duration
    python3 scripts/ai/auto_generate.py --topic "Deep Sleep Journey" --duration 45 --mode budget

    # Audio only (skip video)
    python3 scripts/ai/auto_generate.py --topic "Confidence Builder" --audio-only

    # Dry run (just generate manifest and show plan)
    python3 scripts/ai/auto_generate.py --topic "Healing from Grief" --dry-run

Cost Optimization Modes:
    - budget:   Minimal AI usage, ~$0.70 total
    - standard: Balanced quality/cost, ~$1.06 total (recommended)
    - premium:  Maximum quality, ~$1.51 total
"""

import os
import sys
import argparse
import subprocess
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import time
import anthropic
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")

from scripts.ai.creative_workflow import CreativeWorkflow


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
        mode: str = 'standard',
        duration_minutes: int = 30,
        audio_only: bool = False,
        dry_run: bool = False,
        verbose: bool = True,
        session_name: Optional[str] = None,
        skip_upload: bool = False,
        no_cleanup: bool = False,
        no_learning: bool = False,
    ):
        self.topic = topic
        self.mode = mode
        self.duration_minutes = duration_minutes
        self.audio_only = audio_only
        self.dry_run = dry_run
        self.verbose = verbose
        self.skip_upload = skip_upload
        self.no_cleanup = no_cleanup
        self.no_learning = no_learning

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

        # Stage tracking
        self.stages_completed: List[str] = []
        self.stages_failed: List[str] = []

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
        self.log(f"Mode: {self.mode}")
        self.log(f"Duration: {self.duration_minutes} min")
        self.log(f"Session: {self.session_name}")

        if self.dry_run:
            self.log("DRY RUN - No files will be created", "warning")

        try:
            # Stage 1: Create session structure
            self._stage_create_session()

            # Stage 2: Generate manifest
            manifest = self._stage_generate_manifest()

            # Stage 3: Generate SSML script
            self._stage_generate_script()

            # Stage 4: Generate image prompts
            self._stage_generate_prompts()

            if not self.dry_run:
                # Stage 5: Generate voice
                self._stage_generate_voice()

                # Stage 6: Generate binaural
                self._stage_generate_binaural()

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

                    # Stage 12: Package for YouTube
                    self._stage_package_youtube()

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
            self.stages_failed.append(str(e))

        self.end_time = datetime.now()

        # Generate report
        report = self._generate_report()
        self._save_report(report)

        return report

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

        # Build the user prompt with session context
        user_prompt = f"""Generate a complete SSML hypnotic script for the following session:

**Topic:** {self.topic}
**Target Duration:** {self.duration_minutes} minutes
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

        user_prompt += """
**CRITICAL REQUIREMENTS:**
1. The script MUST follow the exact structure from the master prompt:
   - PRE-TALK (2-3 minutes): Welcome, safety, preparation
   - INDUCTION (4-5 minutes): Progressive relaxation, breathing, countdown
   - MAIN JOURNEY (14-16 minutes): The full hypnotic experience with rich sensory detail
   - INTEGRATION (2-3 minutes): Return to awareness
   - CLOSING (2-3 minutes): Post-hypnotic anchors, gratitude

2. Use rate="1.0" for ALL prosody tags (never use slow rates like 0.85)
3. Use <break time="Xs"/> tags liberally for hypnotic pacing
4. Include rich sensory language engaging all 5 senses
5. Embed hypnotic suggestions naturally throughout
6. Include 3-5 post-hypnotic anchors in the closing

**OUTPUT FORMAT:**
Output ONLY the SSML script, starting with <?xml version="1.0" encoding="UTF-8"?>
Do NOT include any explanation or commentary before or after the SSML.
"""

        # Check for API key - support both direct API and Claude Code environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        if api_key:
            # Use direct Anthropic API if key is available
            self.log("Using Anthropic API for script generation...", "info")
            try:
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=16000,
                    system=master_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                script_content = response.content[0].text
            except anthropic.APIError as e:
                self.log(f"Claude API error: {e}", "error")
                self.stages_failed.append("generate_script")
                return
            except Exception as e:
                self.log(f"API call failed: {e}", "error")
                self.stages_failed.append("generate_script")
                return
        else:
            # No API key - use claude CLI if available (for Claude Code subscription users)
            self.log("No ANTHROPIC_API_KEY found, trying claude CLI...", "info")

            # Save the prompt for reference
            prompt_file = self.session_path / "working_files" / "script_prompt.txt"
            prompt_file.write_text(user_prompt)

            # Save master prompt separately
            system_prompt_file = self.session_path / "working_files" / "system_prompt.txt"
            system_prompt_file.write_text(master_prompt)

            try:
                # Use claude CLI with --print and --system-prompt
                # Pass the user prompt via stdin to avoid command line length limits
                result = subprocess.run(
                    [
                        "claude", "-p",
                        "--system-prompt", master_prompt,
                        "--output-format", "text",
                        user_prompt
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(self.project_root)
                )

                if result.returncode != 0:
                    self.log(f"Claude CLI error: {result.stderr[:200] if result.stderr else 'Unknown error'}", "warning")
                    self.log("Script generation requires manual step", "info")
                    self.log(f"Run: /generate-script {self.session_name}", "info")
                    self.stages_failed.append("generate_script")
                    return

                script_content = result.stdout
            except FileNotFoundError:
                self.log("Claude CLI not found", "error")
                self.log(f"Run: /generate-script {self.session_name}", "info")
                self.stages_failed.append("generate_script")
                return
            except subprocess.TimeoutExpired:
                self.log("Script generation timed out (5 min limit)", "error")
                self.stages_failed.append("generate_script")
                return
            except Exception as e:
                self.log(f"Script generation failed: {e}", "error")
                self.log(f"Run: /generate-script {self.session_name}", "info")
                self.stages_failed.append("generate_script")
                return

        # Clean up the response - ensure it starts with XML declaration
        if not script_content.strip().startswith('<?xml'):
            # Try to find the XML start
            xml_start = script_content.find('<?xml')
            if xml_start != -1:
                script_content = script_content[xml_start:]
            else:
                self.log("Response doesn't contain valid SSML", "error")
                self.log("Use /generate-script command to create script manually", "info")
                self.stages_failed.append("generate_script")
                return

        # Clean up SSML issues from Claude output
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
        self.log(f"Generated script: {script_path}", "success")

        # Create clean version for TTS (strip SFX markers)
        clean_content = re.sub(r'\[SFX:[^\]]*\]\n?', '', script_content)
        clean_path = self.session_path / "working_files" / "script_voice_clean.ssml"
        clean_path.write_text(clean_content)
        self.log(f"Created voice-clean script: {clean_path}", "success")

        self.stages_completed.append("generate_script")

    def _stage_generate_prompts(self):
        """Generate Midjourney/SD image prompts."""
        self.log("Generating image prompts", "stage")
        self.cost_tracker.add_operation('image_prompts')

        if self.dry_run:
            self.log("Would generate image prompts", "info")
            return

        try:
            result = subprocess.run(
                ["python3", "scripts/ai/prompt_generator.py", str(self.session_path)],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
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

        try:
            result = subprocess.run(
                [
                    "python3", "scripts/core/generate_voice.py",
                    str(ssml_path),
                    str(output_dir)
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600,  # 10 minute timeout
            )

            if result.returncode == 0:
                self.log("Generated voice audio", "success")
                self.stages_completed.append("generate_voice")
            else:
                self.log(f"Voice generation error: {result.stderr[:200]}", "error")
                self.stages_failed.append("generate_voice")

        except subprocess.TimeoutExpired:
            self.log("Voice generation timed out", "error")
            self.stages_failed.append("generate_voice")
        except Exception as e:
            self.log(f"Voice generation failed: {e}", "error")
            self.stages_failed.append("generate_voice")

    def _stage_generate_binaural(self):
        """Generate binaural beats using FFmpeg (fast)."""
        self.log("Generating binaural beats", "stage")

        output_path = self.session_path / "output" / "binaural_dynamic.wav"
        duration_seconds = self.duration_minutes * 60

        # Read manifest for binaural settings if available
        manifest_path = self.session_path / "manifest.yaml"
        base_freq = 200  # Hz carrier frequency
        beat_freq = 7    # Hz binaural beat (theta default)

        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                binaural = manifest.get('sound_bed', {}).get('binaural', {})
                base_freq = binaural.get('base_hz', 200)
                # Use middle of the binaural curve for simplicity
                sections = binaural.get('sections', [])
                if sections:
                    # Average beat frequency from sections
                    beat_freq = sum(s.get('offset_hz', 7) for s in sections) / len(sections)
            except Exception:
                pass  # Use defaults

        # Generate stereo binaural with FFmpeg (very fast)
        # Left channel: base_freq, Right channel: base_freq + beat_freq
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
                timeout=120,  # FFmpeg is fast, 2 min timeout is plenty
            )

            if result.returncode == 0:
                self.log(f"Generated binaural beats ({left_freq}Hz / {right_freq}Hz)", "success")
                self.stages_completed.append("generate_binaural")
            else:
                self.log(f"Binaural generation warning: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"Binaural generation skipped: {e}", "warning")

    def _stage_mix_audio(self):
        """Mix audio layers using FFmpeg."""
        self.log("Mixing audio layers", "stage")

        output_dir = self.session_path / "output"
        mixed_file = output_dir / "session_mixed.wav"

        # Find voice file (prefer enhanced, fall back to others)
        voice_file = None
        for name in ["voice_enhanced.wav", "voice_enhanced.mp3", "voice.wav", "voice.mp3"]:
            candidate = output_dir / name
            if candidate.exists():
                voice_file = candidate
                break

        if not voice_file:
            self.log("No voice file found, skipping mix", "warning")
            return

        binaural_file = output_dir / "binaural_dynamic.wav"

        # Build FFmpeg command based on available files
        if binaural_file.exists():
            # Two-stem mix: voice + binaural
            cmd = [
                "ffmpeg", "-y",
                "-i", str(voice_file),
                "-i", str(binaural_file),
                "-filter_complex",
                "[0:a]volume=-6dB[voice];[1:a]volume=-6dB[bin];[voice][bin]amix=inputs=2:duration=longest:normalize=0[mixed]",
                "-map", "[mixed]",
                "-acodec", "pcm_s16le",
                str(mixed_file)
            ]
            self.log("Mixing voice + binaural", "info")
        else:
            # Voice only - just apply volume normalization
            cmd = [
                "ffmpeg", "-y",
                "-i", str(voice_file),
                "-af", "volume=-6dB",
                "-acodec", "pcm_s16le",
                str(mixed_file)
            ]
            self.log("Voice only (no binaural found)", "warning")

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
        self.log("Applying hypnotic post-processing", "stage")

        try:
            result = subprocess.run(
                [
                    "python3", "scripts/core/hypnotic_post_process.py",
                    "--session", str(self.session_path) + "/"
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
                self.log(f"Post-processing warning: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"Post-processing skipped: {e}", "warning")

    def _stage_generate_vtt(self):
        """Generate VTT subtitles."""
        self.log("Generating VTT subtitles", "stage")
        self.cost_tracker.add_operation('vtt_generation')

        try:
            result = subprocess.run(
                ["python3", "scripts/ai/vtt_generator.py", str(self.session_path)],
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
        """Generate scene images using Stable Diffusion."""
        self.log("Generating scene images", "stage")

        try:
            result = subprocess.run(
                [
                    "python3", "scripts/core/generate_scene_images.py",
                    str(self.session_path) + "/"
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=1800,  # 30 min for image generation
            )

            if result.returncode == 0:
                self.log("Generated scene images", "success")
                self.stages_completed.append("generate_images")
            else:
                self.log(f"Image generation skipped: {result.stderr[:100]}", "warning")

        except Exception as e:
            self.log(f"Image generation skipped: {e}", "warning")

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
                    "python3", "scripts/core/assemble_session_video.py",
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
        """Create YouTube package."""
        self.log("Creating YouTube package", "stage")

        try:
            result = subprocess.run(
                [
                    "python3", "scripts/core/package_youtube.py",
                    "--session", str(self.session_path) + "/"
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

    def _stage_upload_website(self):
        """Upload session to salars.net website."""
        self.log("Uploading to website (salars.net)", "stage")

        # Check for required files
        master_audio = None
        for f in (self.session_path / "output").glob("*_MASTER.mp3"):
            master_audio = f
            break

        if not master_audio:
            self.log("No master audio found, skipping website upload", "warning")
            return

        try:
            result = subprocess.run(
                [
                    "python3", "scripts/core/upload_to_website.py",
                    "--session", str(self.session_path) + "/",
                    "--no-git"
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600,
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
                self.log(f"Website upload warning: {result.stderr[:200]}", "warning")

        except subprocess.TimeoutExpired:
            self.log("Website upload timed out", "error")
            self.stages_failed.append("upload_website")
        except Exception as e:
            self.log(f"Website upload skipped: {e}", "warning")

    def _stage_cleanup(self):
        """Cleanup intermediate files to save disk space."""
        self.log("Cleaning up intermediate files", "stage")

        try:
            result = subprocess.run(
                [
                    "python3", "scripts/core/cleanup_session.py",
                    str(self.session_path) + "/"
                ],
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

        # Append and save
        lessons.append(new_lesson)

        try:
            with open(lessons_file, 'w') as f:
                yaml.dump({'lessons': lessons}, f, default_flow_style=False, sort_keys=False)

            self.log(f"Recorded lesson {new_lesson['id']}", "success")
            self.stages_completed.append("self_improvement")
        except Exception as e:
            self.log(f"Failed to record lesson: {e}", "warning")

    def _generate_report(self) -> Dict:
        """Generate execution report."""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        report = {
            'session_name': self.session_name,
            'topic': self.topic,
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
        print(f"Mode: {report['mode']}")
        print(f"Duration: {report['execution']['duration_seconds']:.1f}s")

        print(f"\nStages Completed: {len(report['stages']['completed'])}")
        for stage in report['stages']['completed']:
            print(f"  ✓ {stage}")

        if report['stages']['failed']:
            print(f"\nStages Failed: {len(report['stages']['failed'])}")
            for stage in report['stages']['failed']:
                print(f"  ✗ {stage}")

        print(f"\nEstimated Cost: ${report['costs']['total_usd']:.2f}")

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
    python3 scripts/ai/auto_generate.py --topic "Confidence" --audio-only
    python3 scripts/ai/auto_generate.py --topic "Healing" --dry-run
        """
    )

    parser.add_argument('--topic', '-t', required=True,
                       help='Topic/theme for the session')
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

    args = parser.parse_args()

    generator = AutoGenerator(
        topic=args.topic,
        mode=args.mode,
        duration_minutes=args.duration,
        audio_only=args.audio_only,
        dry_run=args.dry_run,
        verbose=not args.quiet,
        session_name=args.name,
        skip_upload=args.skip_upload,
        no_cleanup=args.no_cleanup,
        no_learning=args.no_learning,
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
