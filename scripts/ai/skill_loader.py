#!/usr/bin/env python3
"""
Skill Loader - Dynamic loading of tiered Claude skills for Dreamweaving.

This module provides functionality to load appropriate skills based on:
- Task type (script writing, audio production, video assembly, etc.)
- Context (safety triggers, session attributes, etc.)
- Tier requirements (always, triggered, task-specific, conditional)

The 4-tier skill taxonomy:
- Tier 1 (Neural Core): Always loaded - hypnotic-language, symbolic-mapping, audio-somatic
- Tier 2 (Safety): Triggered on specific conditions - psychological-stability, christian-discernment, ethical-framing
- Tier 3 (Production): Task-specific - ssml-generation, voice-synthesis, audio-mixing, video-assembly, youtube-packaging
- Tier 4 (Growth): Conditional - analytics-learning, feedback-integration
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class Tier(Enum):
    """Skill tier levels."""
    NEURAL_CORE = 1
    SAFETY = 2
    PRODUCTION = 3
    GROWTH = 4


class LoadPolicy(Enum):
    """When skills should be loaded."""
    ALWAYS = "always"
    TRIGGERED = "triggered"
    TASK_SPECIFIC = "task-specific"
    CONDITIONAL = "conditional"


@dataclass
class Skill:
    """Represents a loaded skill with its metadata and content."""
    name: str
    tier: Tier
    load_policy: LoadPolicy
    description: str
    path: Path
    content: str
    sub_skills: List['Skill'] = field(default_factory=list)
    version: str = "1.0.0"

    def __repr__(self):
        return f"Skill({self.name}, Tier {self.tier.value}, {self.load_policy.value})"


@dataclass
class SkillContext:
    """Context for determining which skills to load."""
    task_type: str  # script_writing, audio_production, video_assembly, etc.
    session_attributes: Dict = field(default_factory=dict)
    safety_triggers: Set[str] = field(default_factory=set)
    depth_level: str = "Layer2"
    desired_outcome: Optional[str] = None


class SkillLoader:
    """
    Loads and manages skills based on task context.

    Usage:
        loader = SkillLoader()
        skills = loader.load_for_task(SkillContext(task_type="script_writing"))

        # Get specific tier skills
        tier1_skills = loader.get_tier_skills(Tier.NEURAL_CORE)

        # Check if safety triggered
        if loader.is_safety_triggered(context):
            safety_skills = loader.get_tier_skills(Tier.SAFETY)
    """

    SKILLS_ROOT = Path(__file__).parent.parent.parent / ".claude" / "skills"

    # Safety trigger patterns
    SAFETY_TRIGGERS = {
        "dissociation_language": [
            "floating away", "leaving body", "dissolving", "disappearing",
            "losing", "nothing", "empty", "gone", "can't feel"
        ],
        "depth_concern": [
            "Layer3", "Ipsissimus", "helm_deep_trance", "ego dissolution"
        ],
        "theological_concern": [
            "spirit guide", "the universe provides", "higher self",
            "inner god", "becoming divine", "entity"
        ],
        "trauma_adjacent": [
            "trauma", "abuse", "wounded", "broken", "damaged"
        ],
        "overwhelm_indicators": [
            "overwhelming", "flooding", "too much", "can't handle"
        ]
    }

    # Task to tier3 skill mapping
    TASK_SKILL_MAP = {
        "script_writing": ["ssml-generation"],
        "audio_production": ["voice-synthesis", "audio-mixing"],
        "voice_synthesis": ["voice-synthesis"],
        "audio_mixing": ["audio-mixing"],
        "video_assembly": ["video-assembly"],
        "youtube_packaging": ["youtube-packaging"],
        "session_creation": ["session-creation"],
        "full_build": ["session-creation", "ssml-generation", "voice-synthesis",
                       "audio-mixing", "video-assembly", "youtube-packaging"],
    }

    # Outcome to tier1 emphasis mapping
    OUTCOME_EMPHASIS = {
        "healing": {
            "hypnotic-language": ["deepening/fractionation", "suggestion/metaphor-framing"],
            "symbolic-mapping": ["archetypes/healer", "symbols/elemental"],
            "audio-somatic": ["breath-regulation", "somatic-anchoring"]
        },
        "transformation": {
            "hypnotic-language": ["deepening/time-distortion", "deepening/fractionation"],
            "symbolic-mapping": ["archetypes/guide", "theological-filters"],
            "audio-somatic": ["arousal-control"]
        },
        "confidence": {
            "hypnotic-language": ["suggestion/indirect-suggestion", "suggestion/values-alignment"],
            "symbolic-mapping": ["symbols/elemental"],
            "audio-somatic": ["somatic-anchoring"]
        },
        "relaxation": {
            "hypnotic-language": ["induction/soft-entry", "emergence/grounding"],
            "audio-somatic": ["breath-regulation", "somatic-anchoring"]
        },
        "spiritual_growth": {
            "hypnotic-language": ["deepening/imagery-coupling"],
            "symbolic-mapping": ["theological-filters", "archetypes"],
            "audio-somatic": ["arousal-control"]
        }
    }

    def __init__(self, skills_root: Optional[Path] = None):
        """Initialize the skill loader."""
        self.skills_root = skills_root or self.SKILLS_ROOT
        self._skill_cache: Dict[str, Skill] = {}

    def load_for_task(self, context: SkillContext) -> List[Skill]:
        """
        Load all appropriate skills for a given task context.

        Args:
            context: The task context determining skill selection

        Returns:
            List of loaded skills
        """
        skills = []

        # Always load Tier 1 (Neural Core)
        skills.extend(self.get_tier_skills(Tier.NEURAL_CORE))

        # Check for Tier 2 (Safety) triggers
        if self.is_safety_triggered(context):
            skills.extend(self.get_tier_skills(Tier.SAFETY))

        # Load Tier 3 (Production) based on task
        if context.task_type in self.TASK_SKILL_MAP:
            for skill_name in self.TASK_SKILL_MAP[context.task_type]:
                skill = self._load_skill(f"tier3-production/{skill_name}")
                if skill:
                    skills.append(skill)

        # Load Tier 4 (Growth) if analytics/learning context
        if context.task_type in ["analytics", "feedback", "learning"]:
            skills.extend(self.get_tier_skills(Tier.GROWTH))

        return skills

    def get_tier_skills(self, tier: Tier) -> List[Skill]:
        """
        Get all skills from a specific tier.

        Args:
            tier: The tier to load skills from

        Returns:
            List of skills from that tier
        """
        tier_paths = {
            Tier.NEURAL_CORE: "tier1-neural-core",
            Tier.SAFETY: "tier2-safety",
            Tier.PRODUCTION: "tier3-production",
            Tier.GROWTH: "tier4-growth"
        }

        tier_path = self.skills_root / tier_paths[tier]
        skills = []

        if not tier_path.exists():
            return skills

        # Load main SKILL.md for tier if exists
        main_skill = tier_path / "SKILL.md"
        if main_skill.exists():
            skill = self._load_skill_file(main_skill, tier)
            if skill:
                skills.append(skill)

        # Load sub-skill directories
        for subdir in tier_path.iterdir():
            if subdir.is_dir():
                subskill = self._load_skill(f"{tier_paths[tier]}/{subdir.name}")
                if subskill:
                    skills.append(subskill)

        return skills

    def is_safety_triggered(self, context: SkillContext) -> bool:
        """
        Check if any safety triggers are present in the context.

        Args:
            context: The task context to check

        Returns:
            True if safety skills should be loaded
        """
        # Explicit safety triggers
        if context.safety_triggers:
            return True

        # Depth-based triggers
        if context.depth_level in ["Layer3", "Ipsissimus"]:
            return True

        # Outcome-based triggers
        if context.desired_outcome in ["healing", "transformation", "spiritual_growth"]:
            return True

        # Session attribute triggers
        if context.session_attributes.get("trauma_adjacent", False):
            return True
        if context.session_attributes.get("first_time_listener", False):
            return True

        return False

    def check_content_safety(self, content: str) -> Dict[str, List[str]]:
        """
        Scan content for safety trigger patterns.

        Args:
            content: The text content to scan

        Returns:
            Dict mapping trigger categories to matched patterns
        """
        triggers_found = {}
        content_lower = content.lower()

        for category, patterns in self.SAFETY_TRIGGERS.items():
            matches = [p for p in patterns if p in content_lower]
            if matches:
                triggers_found[category] = matches

        return triggers_found

    def get_skill_emphasis(self, outcome: str) -> Dict[str, List[str]]:
        """
        Get recommended sub-skill emphasis for a given outcome.

        Args:
            outcome: The desired session outcome

        Returns:
            Dict mapping tier1 skills to emphasized sub-skills
        """
        return self.OUTCOME_EMPHASIS.get(outcome, {})

    def _load_skill(self, skill_path: str) -> Optional[Skill]:
        """Load a skill from a relative path."""
        if skill_path in self._skill_cache:
            return self._skill_cache[skill_path]

        full_path = self.skills_root / skill_path
        skill_file = full_path / "SKILL.md"

        if not skill_file.exists():
            return None

        # Determine tier from path
        tier = self._path_to_tier(skill_path)
        skill = self._load_skill_file(skill_file, tier)

        if skill:
            # Load sub-skills
            skill.sub_skills = self._load_sub_skills(full_path, tier)
            self._skill_cache[skill_path] = skill

        return skill

    def _load_skill_file(self, path: Path, tier: Tier) -> Optional[Skill]:
        """Load and parse a single SKILL.md file."""
        try:
            content = path.read_text()

            # Parse YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                else:
                    frontmatter = {}
                    body = content
            else:
                frontmatter = {}
                body = content

            return Skill(
                name=frontmatter.get("name", path.parent.name),
                tier=tier,
                load_policy=LoadPolicy(frontmatter.get("load_policy", "task-specific")),
                description=frontmatter.get("description", ""),
                version=frontmatter.get("version", "1.0.0"),
                path=path,
                content=body
            )
        except Exception as e:
            print(f"Error loading skill from {path}: {e}")
            return None

    def _load_sub_skills(self, parent_path: Path, tier: Tier) -> List[Skill]:
        """Load all sub-skills from a skill directory."""
        sub_skills = []

        for item in parent_path.iterdir():
            if item.is_dir():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    skill = self._load_skill_file(skill_file, tier)
                    if skill:
                        sub_skills.append(skill)
                else:
                    # Check for individual .md files
                    for md_file in item.glob("*.md"):
                        skill = self._load_skill_file(md_file, tier)
                        if skill:
                            sub_skills.append(skill)
            elif item.suffix == ".md" and item.name != "SKILL.md":
                skill = self._load_skill_file(item, tier)
                if skill:
                    sub_skills.append(skill)

        return sub_skills

    def _path_to_tier(self, path: str) -> Tier:
        """Convert a skill path to its tier."""
        if "tier1" in path or "neural-core" in path:
            return Tier.NEURAL_CORE
        elif "tier2" in path or "safety" in path:
            return Tier.SAFETY
        elif "tier3" in path or "production" in path:
            return Tier.PRODUCTION
        elif "tier4" in path or "growth" in path:
            return Tier.GROWTH
        return Tier.PRODUCTION  # Default

    def get_skill_summary(self) -> str:
        """
        Get a summary of all available skills.

        Returns:
            Formatted string summarizing all skills
        """
        lines = ["# Skill System Summary\n"]

        for tier in Tier:
            skills = self.get_tier_skills(tier)
            tier_name = {
                Tier.NEURAL_CORE: "Tier 1: Neural Core (Always)",
                Tier.SAFETY: "Tier 2: Safety (Triggered)",
                Tier.PRODUCTION: "Tier 3: Production (Task-Specific)",
                Tier.GROWTH: "Tier 4: Growth (Conditional)"
            }[tier]

            lines.append(f"\n## {tier_name}\n")

            for skill in skills:
                lines.append(f"- **{skill.name}**: {skill.description}")
                for sub in skill.sub_skills:
                    lines.append(f"  - {sub.name}")

        return "\n".join(lines)


# Convenience functions for direct use
def load_skills_for_script_writing(outcome: Optional[str] = None) -> List[Skill]:
    """Load skills needed for script writing tasks."""
    loader = SkillLoader()
    context = SkillContext(
        task_type="script_writing",
        desired_outcome=outcome
    )
    return loader.load_for_task(context)


def load_skills_for_audio_production() -> List[Skill]:
    """Load skills needed for audio production tasks."""
    loader = SkillLoader()
    context = SkillContext(task_type="audio_production")
    return loader.load_for_task(context)


def load_skills_for_full_build(manifest: Dict) -> List[Skill]:
    """Load all skills needed for a full session build."""
    loader = SkillLoader()
    context = SkillContext(
        task_type="full_build",
        desired_outcome=manifest.get("session", {}).get("desired_outcome"),
        depth_level=manifest.get("session", {}).get("depth_level", "Layer2"),
        session_attributes=manifest.get("session", {})
    )
    return loader.load_for_task(context)


def check_script_safety(script_content: str) -> Dict[str, List[str]]:
    """Check a script for safety concerns."""
    loader = SkillLoader()
    return loader.check_content_safety(script_content)


if __name__ == "__main__":
    # Demo/test the skill loader
    loader = SkillLoader()
    print(loader.get_skill_summary())

    print("\n--- Testing skill loading for script writing ---")
    context = SkillContext(
        task_type="script_writing",
        desired_outcome="healing",
        depth_level="Layer2"
    )
    skills = loader.load_for_task(context)
    print(f"Loaded {len(skills)} skills:")
    for skill in skills:
        print(f"  {skill}")

    print("\n--- Testing safety trigger detection ---")
    test_content = """
    You feel yourself floating away from your body...
    dissolving into the light...
    """
    triggers = loader.check_content_safety(test_content)
    print(f"Safety triggers found: {triggers}")
