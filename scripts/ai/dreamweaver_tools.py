"""
Dreamweaver MCP Tool Stubs

This module provides the core tool functions that implement the Dreamweaver
workflow patterns described in CLAUDE.md. These are designed to be called
by Claude Code or integrated into an MCP server.

Usage:
    from scripts.ai.dreamweaver_tools import (
        generate_journey_outline,
        generate_ssml_section,
        suggest_audio_bed,
        generate_youtube_package
    )
"""

import json
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional
import yaml


# ==============================================================================
# Enums and Data Types
# ==============================================================================

class DepthLevel(Enum):
    """Journey depth levels from light to deepest."""
    LAYER1 = "Layer1"      # 15-20 min, light
    LAYER2 = "Layer2"      # 20-30 min, medium
    LAYER3 = "Layer3"      # 30-45 min, deep
    IPSISSIMUS = "Ipsissimus"  # 45-60+ min, deepest


class SpeechProfile(Enum):
    """Speech profiles for different journey sections."""
    PRE_TALK = "pre_talk"
    INDUCTION = "induction"
    DEEP_INDUCTION = "deep_induction"
    JOURNEY = "journey"
    HELM_DEEPEST = "helm_deepest"
    INTEGRATION = "integration"
    POST_HYPNOTIC = "post_hypnotic"


class Tone(Enum):
    """Tonal qualities for script generation."""
    CALM = "calm"
    MYSTICAL = "mystical"
    AUTHORITATIVE = "authoritative"
    PLAYFUL = "playful"


class TargetState(Enum):
    """Target brainwave states for audio bed design."""
    RELAXATION = "relaxation"    # Alpha 8-12 Hz
    TRANCE = "trance"            # Low Alpha / High Theta 7-10 Hz
    DEEP_TRANCE = "deep_trance"  # Theta 4-7 Hz
    INTEGRATION = "integration"  # Return to Alpha


# ==============================================================================
# Data Structures
# ==============================================================================

@dataclass
class JourneySection:
    """A single section within a journey outline."""
    id: str
    label: str
    duration_minutes: float
    purpose: str
    archetypes: list[str] = field(default_factory=list)
    speech_profile: str = "journey"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class JourneyOutline:
    """Complete journey outline structure."""
    theme: str
    duration_target: int
    depth_level: str
    sections: list[JourneySection] = field(default_factory=list)
    archetypes_summary: list[str] = field(default_factory=list)
    narrative_arc: str = ""

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "duration_target": self.duration_target,
            "depth_level": self.depth_level,
            "sections": [s.to_dict() for s in self.sections],
            "archetypes_summary": self.archetypes_summary,
            "narrative_arc": self.narrative_arc
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class BinauralTransition:
    """A single binaural beat transition point."""
    time: str  # "MM:SS" format
    freq: float
    state: str


@dataclass
class SfxEvent:
    """A single sound effect event."""
    time: str  # "MM:SS" format
    effect: str
    duration: float


@dataclass
class AudioPlan:
    """Complete audio bed plan."""
    binaural: dict = field(default_factory=dict)
    ambience: dict = field(default_factory=dict)
    sfx_timeline: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ==============================================================================
# Speech Profile Configuration
# ==============================================================================

SPEECH_PROFILES = {
    "pre_talk": {
        "pitch": "0st",
        "rate": "1.0",
        "break_range": "700ms-1.0s",
        "description": "Normal, grounded"
    },
    "induction": {
        "pitch": "-2st",
        "rate": "1.0",
        "break_range": "1.0s-1.7s",
        "description": "Calming, deeper"
    },
    "deep_induction": {
        "pitch": "-2st",
        "rate": "1.0",
        "break_range": "1.7s-2.5s",
        "description": "Very calm"
    },
    "journey": {
        "pitch": "-1st",
        "rate": "1.0",
        "break_range": "1.0s-2.0s",
        "description": "Immersive"
    },
    "helm_deepest": {
        "pitch": "-2st",
        "rate": "1.0",
        "break_range": "2.0s-3.0s",
        "description": "Deepest trance"
    },
    "integration": {
        "pitch": "-1st",
        "rate": "1.0",
        "break_range": "1.5s-2.0s",
        "description": "Returning"
    },
    "post_hypnotic": {
        "pitch": "0st",
        "rate": "1.0",
        "break_range": "700ms-1.0s",
        "description": "Alert, grounded"
    }
}


# ==============================================================================
# Default Section Templates
# ==============================================================================

DEFAULT_SECTIONS = {
    DepthLevel.LAYER1: [
        JourneySection("pre_talk", "Pre-Talk & Safety", 2, "Ground listener, establish safety", ["Guide"], "pre_talk"),
        JourneySection("induction", "Progressive Relaxation", 4, "Lead into trance state", ["Healer"], "induction"),
        JourneySection("journey", "Main Experience", 8, "Core visualization and experience", ["Guide", "Wise One"], "journey"),
        JourneySection("integration", "Integration", 2, "Process and anchor experience", ["Guide"], "integration"),
        JourneySection("post_hypnotic", "Emergence", 2, "Suggestions and return", ["Guide"], "post_hypnotic"),
    ],
    DepthLevel.LAYER2: [
        JourneySection("pre_talk", "Pre-Talk & Safety", 3, "Ground listener, establish safety", ["Guide", "Protector"], "pre_talk"),
        JourneySection("induction", "Progressive Relaxation", 5, "Lead into trance state", ["Healer"], "induction"),
        JourneySection("deepening", "Deepening", 3, "Intensify trance state", ["Guide"], "deep_induction"),
        JourneySection("journey", "Main Journey", 12, "Core experiential content", ["Guide", "Wise One", "Transformer"], "journey"),
        JourneySection("helm_deepest", "Peak Experience", 4, "Climactic transformation", ["Light Bearer", "Transformer"], "helm_deepest"),
        JourneySection("integration", "Integration", 3, "Process and anchor experience", ["Healer", "Guide"], "integration"),
        JourneySection("post_hypnotic", "Emergence", 3, "Suggestions and return", ["Guide"], "post_hypnotic"),
    ],
    DepthLevel.LAYER3: [
        JourneySection("pre_talk", "Pre-Talk & Safety", 3, "Ground listener, establish safety", ["Guide", "Protector"], "pre_talk"),
        JourneySection("induction", "Progressive Relaxation", 5, "Lead into trance state", ["Healer"], "induction"),
        JourneySection("deepening", "Deepening", 4, "Intensify trance state", ["Guide", "Guardian"], "deep_induction"),
        JourneySection("journey_1", "Journey Part 1", 10, "Setting and initial exploration", ["Guide", "Wise One"], "journey"),
        JourneySection("journey_2", "Journey Part 2", 8, "Deeper exploration and encounters", ["Shadow", "Transformer"], "journey"),
        JourneySection("helm_deepest", "Peak Experience", 5, "Climactic transformation", ["Light Bearer", "Beloved"], "helm_deepest"),
        JourneySection("integration", "Integration", 4, "Process and anchor experience", ["Healer", "Guide"], "integration"),
        JourneySection("post_hypnotic", "Emergence", 3, "Suggestions and return", ["Guide"], "post_hypnotic"),
    ]
}


# ==============================================================================
# Tool Functions
# ==============================================================================

def generate_journey_outline(
    theme: str,
    duration_minutes: int = 30,
    depth_level: str = "Layer2",
    custom_archetypes: Optional[list[str]] = None
) -> JourneyOutline:
    """
    Generate a structured journey outline from a theme.

    This follows the dreamweaver.generate_journey_outline pattern from CLAUDE.md.

    Args:
        theme: High-level theme (e.g., "Garden of Eden Pathworking")
        duration_minutes: Target duration (default 30)
        depth_level: Layer1, Layer2, Layer3, or Ipsissimus
        custom_archetypes: Optional list of specific archetypes to use

    Returns:
        JourneyOutline: Complete structured outline

    Example:
        >>> outline = generate_journey_outline(
        ...     theme="Garden of Eden Pathworking",
        ...     duration_minutes=30,
        ...     depth_level="Layer2"
        ... )
        >>> outline.to_json()
    """
    # Parse depth level
    try:
        depth = DepthLevel(depth_level)
    except ValueError:
        depth = DepthLevel.LAYER2

    # Get default sections for this depth
    if depth == DepthLevel.IPSISSIMUS:
        # Use Layer3 as base, extend durations
        sections = [
            JourneySection(s.id, s.label, s.duration_minutes * 1.5, s.purpose, s.archetypes.copy(), s.speech_profile)
            for s in DEFAULT_SECTIONS[DepthLevel.LAYER3]
        ]
    else:
        sections = [
            JourneySection(s.id, s.label, s.duration_minutes, s.purpose, s.archetypes.copy(), s.speech_profile)
            for s in DEFAULT_SECTIONS.get(depth, DEFAULT_SECTIONS[DepthLevel.LAYER2])
        ]

    # Scale sections to match target duration
    current_total = sum(s.duration_minutes for s in sections)
    scale_factor = duration_minutes / current_total
    for section in sections:
        section.duration_minutes = round(section.duration_minutes * scale_factor, 1)

    # Build archetype summary
    all_archetypes = set()
    for section in sections:
        all_archetypes.update(section.archetypes)
    if custom_archetypes:
        all_archetypes.update(custom_archetypes)

    outline = JourneyOutline(
        theme=theme,
        duration_target=duration_minutes,
        depth_level=depth_level,
        sections=sections,
        archetypes_summary=sorted(list(all_archetypes)),
        narrative_arc=f"A {depth_level} journey exploring {theme} through progressive deepening, transformational experience, and integrated emergence."
    )

    return outline


def get_speech_profile_config(profile: str) -> dict:
    """
    Get the SSML configuration for a speech profile.

    Args:
        profile: Speech profile name (e.g., "induction", "journey")

    Returns:
        dict: Configuration with pitch, rate, break_range, description
    """
    return SPEECH_PROFILES.get(profile, SPEECH_PROFILES["journey"])


def generate_ssml_wrapper(
    content: str,
    profile: str = "journey"
) -> str:
    """
    Wrap content in appropriate SSML tags based on speech profile.

    This follows the dreamweaver.generate_ssml_section pattern.

    Args:
        content: The text content to wrap
        profile: Speech profile (pre_talk, induction, etc.)

    Returns:
        str: Complete SSML speak block
    """
    config = get_speech_profile_config(profile)

    return f'''<speak>
  <prosody rate="{config['rate']}" pitch="{config['pitch']}">
    {content}
  </prosody>
</speak>'''


def suggest_audio_bed(
    target_state: str = "trance",
    duration_minutes: int = 30,
    environment: str = "sacred_space"
) -> AudioPlan:
    """
    Generate an audio bed plan with binaural beats, ambience, and SFX.

    This follows the dreamweaver.suggest_audio_bed pattern from CLAUDE.md.

    Args:
        target_state: relaxation, trance, deep_trance, or integration
        duration_minutes: Total duration of the journey
        environment: Environment label (e.g., "garden", "temple", "starship")

    Returns:
        AudioPlan: Complete audio bed configuration
    """
    # Binaural frequency curves based on target state
    binaural_curves = {
        "relaxation": {"start": 12, "mid": 10, "deep": 8, "end": 10},
        "trance": {"start": 10, "mid": 7, "deep": 5, "end": 8},
        "deep_trance": {"start": 10, "mid": 5, "deep": 4, "end": 7},
        "integration": {"start": 8, "mid": 6, "deep": 4, "end": 10}
    }

    curve = binaural_curves.get(target_state, binaural_curves["trance"])

    # Calculate transition times
    t1 = "0:00"
    t2 = f"{duration_minutes // 4}:00"
    t3 = f"{duration_minutes // 2}:00"
    t4 = f"{3 * duration_minutes // 4}:00"
    t5 = f"{duration_minutes - 2}:00"

    binaural = {
        "carrier_frequency": 200,
        "start_hz": curve["start"],
        "end_hz": curve["end"],
        "transitions": [
            {"time": t1, "freq": curve["start"], "state": "alpha"},
            {"time": t2, "freq": curve["mid"], "state": "low_alpha"},
            {"time": t3, "freq": curve["deep"], "state": "theta"},
            {"time": t4, "freq": curve["mid"], "state": "theta"},
            {"time": t5, "freq": curve["end"], "state": "alpha"}
        ]
    }

    # Environment-based ambience
    ambience_presets = {
        "garden": {"base": "garden_with_water", "layers": ["birds", "gentle_wind"]},
        "temple": {"base": "cathedral_reverb", "layers": ["distant_bells", "sacred_hum"]},
        "starship": {"base": "ship_ambient", "layers": ["subtle_engines", "electronic_hum"]},
        "forest": {"base": "forest_night", "layers": ["crickets", "owl", "stream"]},
        "ocean": {"base": "ocean_waves", "layers": ["seagulls", "wind"]},
        "sacred_space": {"base": "ethereal_pad", "layers": ["soft_chimes", "breath"]}
    }

    ambience = ambience_presets.get(environment, ambience_presets["sacred_space"])

    # Default SFX timeline
    sfx_timeline = [
        {"time": "0:30", "effect": "soft_chime", "duration": 2},
        {"time": f"{duration_minutes // 4}:00", "effect": "deep_bell", "duration": 4},
        {"time": f"{duration_minutes // 2}:00", "effect": "ethereal_tone", "duration": 3},
        {"time": f"{3 * duration_minutes // 4}:00", "effect": "crystal_bowl", "duration": 5},
        {"time": f"{duration_minutes - 3}:00", "effect": "awakening_chime", "duration": 3}
    ]

    return AudioPlan(
        binaural=binaural,
        ambience=ambience,
        sfx_timeline=sfx_timeline
    )


def generate_youtube_package(
    session_path: str,
    manifest: Optional[dict] = None
) -> dict:
    """
    Generate a YouTube package with title, description, tags, and chapters.

    This follows the dreamweaver.generate_youtube_package pattern.

    Args:
        session_path: Path to session directory
        manifest: Optional pre-loaded manifest dict

    Returns:
        dict: YouTube package with title, description, tags, chapters, thumbnail_prompts
    """
    session_path = Path(session_path)

    # Load manifest if not provided
    if manifest is None:
        manifest_path = session_path / "manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)
        else:
            manifest = {}

    # Extract info from manifest
    title_base = manifest.get("title", session_path.name.replace("-", " ").title())
    theme = manifest.get("theme", "Hypnotic Journey")
    duration = manifest.get("duration_minutes", 30)

    # Generate package structure
    package = {
        "title": f"{title_base} | {duration}-Minute Guided Hypnotic Journey",
        "description": f"""🌙 {title_base}

Embark on a transformative {duration}-minute hypnotic journey exploring {theme}.

✨ What You'll Experience:
• Deep progressive relaxation
• Guided visualization through sacred spaces
• Transformational inner work
• Gentle emergence with anchored benefits

⚠️ Important:
• Listen in a quiet, comfortable space
• Use headphones for full binaural effect
• Do not listen while driving or operating machinery
• This is not a substitute for professional medical or mental health treatment

🎧 Audio Features:
• Professional voice synthesis
• Binaural beats for brainwave entrainment
• Ambient soundscapes
• Strategic sound effects for key moments

💫 Subscribe for more hypnotic journeys and meditative experiences.

#hypnosis #guidedmeditation #binauralbeats #trance #healing #spirituality
""",
        "tags": [
            "hypnosis",
            "guided meditation",
            "binaural beats",
            "theta waves",
            "deep relaxation",
            "hypnotherapy",
            "trance",
            "spiritual journey",
            "visualization",
            "inner work",
            "healing meditation",
            "sacred space",
            theme.lower().replace(" ", "")
        ],
        "chapters": [
            "0:00 Welcome & Safety",
            f"2:00 Progressive Relaxation",
            f"7:00 Deepening",
            f"10:00 Main Journey Begins",
            f"{duration - 8}:00 Peak Experience",
            f"{duration - 5}:00 Integration",
            f"{duration - 2}:00 Gentle Emergence"
        ],
        "thumbnail_prompts": [
            f"Mystical {theme} scene, ethereal light, sacred geometry, 16:9, 8k, cinematic, golden hour lighting, mist and glow particles",
            f"Person in deep meditation, {theme} visualization above, soft divine light rays, peaceful atmosphere, 16:9, photorealistic",
            f"Abstract representation of {theme}, flowing energy, sacred symbols, purple and gold palette, mystical atmosphere, 16:9"
        ]
    }

    return package


# ==============================================================================
# File Operations
# ==============================================================================

def save_outline(outline: JourneyOutline, session_path: str) -> str:
    """Save journey outline to session directory."""
    path = Path(session_path) / "outline.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        f.write(outline.to_json())

    return str(path)


def save_audio_plan(audio_plan: AudioPlan, session_path: str) -> str:
    """Save audio plan to session working files."""
    path = Path(session_path) / "working_files" / "audio_plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        f.write(audio_plan.to_json())

    return str(path)


def save_youtube_package(package: dict, session_path: str) -> str:
    """Save YouTube package as markdown."""
    path = Path(session_path) / "youtube_package.md"

    content = f"""# YouTube Package

## Title
{package['title']}

## Description
{package['description']}

## Tags
{', '.join(package['tags'])}

## Chapters
{chr(10).join(package['chapters'])}

## Thumbnail Prompts

"""
    for i, prompt in enumerate(package['thumbnail_prompts'], 1):
        content += f"### Option {i}\n{prompt}\n\n"

    with open(path, "w") as f:
        f.write(content)

    return str(path)


# ==============================================================================
# Convenience Functions
# ==============================================================================

def create_session_scaffold(
    session_name: str,
    theme: str,
    duration_minutes: int = 30,
    depth_level: str = "Layer2",
    base_path: str = "sessions"
) -> dict:
    """
    Create a complete session scaffold with all standard files.

    Args:
        session_name: Kebab-case session name
        theme: Journey theme
        duration_minutes: Target duration
        depth_level: Depth level
        base_path: Base sessions directory

    Returns:
        dict: Paths to all created files
    """
    session_path = Path(base_path) / session_name

    # Create directories
    (session_path / "working_files" / "script_sections").mkdir(parents=True, exist_ok=True)
    (session_path / "images" / "uploaded").mkdir(parents=True, exist_ok=True)
    (session_path / "output").mkdir(parents=True, exist_ok=True)

    # Generate and save outline
    outline = generate_journey_outline(theme, duration_minutes, depth_level)
    outline_path = save_outline(outline, str(session_path))

    # Generate and save audio plan
    audio_plan = suggest_audio_bed("trance", duration_minutes, "sacred_space")
    audio_path = save_audio_plan(audio_plan, str(session_path))

    # Generate and save YouTube package
    youtube_package = generate_youtube_package(str(session_path), {
        "title": theme,
        "theme": theme,
        "duration_minutes": duration_minutes
    })
    youtube_path = save_youtube_package(youtube_package, str(session_path))

    # Create notes.md
    notes_path = session_path / "notes.md"
    notes_content = f"""# {theme}

## Design Notes

**Theme:** {theme}
**Duration:** {duration_minutes} minutes
**Depth Level:** {depth_level}

## Archetypes
{chr(10).join(f"- {a}" for a in outline.archetypes_summary)}

## Narrative Arc
{outline.narrative_arc}

## Special Considerations
- [Add any special notes here]

## Changelog
- {os.popen('date +%Y-%m-%d').read().strip()}: Initial creation
"""
    with open(notes_path, "w") as f:
        f.write(notes_content)

    return {
        "session_path": str(session_path),
        "outline": outline_path,
        "audio_plan": audio_path,
        "youtube_package": youtube_path,
        "notes": str(notes_path)
    }


# ==============================================================================
# Main Entry Point (for testing)
# ==============================================================================

if __name__ == "__main__":
    # Demo usage
    print("Dreamweaver Tools Demo")
    print("=" * 50)

    # Generate outline
    outline = generate_journey_outline(
        theme="Garden of Eden Pathworking",
        duration_minutes=30,
        depth_level="Layer2"
    )
    print("\nGenerated Outline:")
    print(outline.to_json())

    # Generate audio plan
    audio = suggest_audio_bed("deep_trance", 30, "garden")
    print("\nGenerated Audio Plan:")
    print(audio.to_json())

    # Get speech profile
    print("\nInduction Speech Profile:")
    print(json.dumps(get_speech_profile_config("induction"), indent=2))
