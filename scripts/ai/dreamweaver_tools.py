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
import random
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
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
    duration_minutes: int = 30,
    environment: str = "sacred_space",
    therapeutic_outcome: str = "healing",
    depth_level: str = "Layer2",
    style: str = "mystical"
) -> AudioPlan:
    """
    Generate an audio bed plan with binaural beats, ambience, and SFX.

    This follows the dreamweaver.suggest_audio_bed pattern from CLAUDE.md.
    Now includes outcome-specific gamma bursts, style-matched SFX, timing jitter,
    and multi-layer binaural for deeper sessions.

    Args:
        target_state: relaxation, trance, deep_trance, or integration
        duration_minutes: Total duration of the journey
        environment: Environment label (e.g., "garden", "temple", "starship")
        therapeutic_outcome: healing, transformation, confidence, relaxation, etc.
        depth_level: Layer1, Layer2, Layer3, or Ipsissimus
        style: cosmic, nature, mystical, technological, elemental

    Returns:
        AudioPlan: Complete audio bed configuration
    """
    # ==========================================================================
    # OUTCOME-SPECIFIC BINAURAL PRESETS (from knowledge/audio/binaural_presets.yaml)
    # ==========================================================================
    outcome_to_preset = {
        "healing": "healing_deep",
        "transformation": "transformation_alchemical",
        "confidence": "confidence_radiant",
        "empowerment": "confidence_radiant",
        "relaxation": "relaxation_gentle",
        "spiritual_growth": "spiritual_transcendence",
        "creativity": "creativity_flow",
        "sleep": "sleep_delta_descent",
        "grief": "healing_gentle",
        "anxiety": "relaxation_gentle",
        "abundance": "abundance_mindset",
        "self_love": "healing_gentle",
        "forgiveness": "healing_deep",
        "focus": "focus_laser",
    }

    # Binaural frequency curves based on therapeutic outcome (more varied than target_state)
    outcome_curves = {
        "healing": {
            "start": 10, "induction": 8, "deep1": 6, "deep2": 4, "deepest": 2,
            "return1": 4, "return2": 6, "end": 10,
            "gamma_burst": True, "gamma_ratio": random.uniform(0.55, 0.65)
        },
        "transformation": {
            "start": 10, "induction": 8, "deep1": 6, "deep2": 4.5, "deepest": 3,
            "return1": 2.5, "return2": 4, "end": 8,
            "gamma_burst": True, "gamma_ratio": random.uniform(0.70, 0.80),
            "double_burst": True, "second_burst_ratio": random.uniform(0.85, 0.92)
        },
        "confidence": {
            "start": 12, "induction": 10, "deep1": 14, "deep2": 10, "deepest": 7,
            "return1": 10, "return2": 12, "end": 14,
            "gamma_burst": True, "gamma_ratio": random.uniform(0.58, 0.68),
            "double_burst": True, "second_burst_ratio": random.uniform(0.78, 0.85)
        },
        "relaxation": {
            "start": 10, "induction": 9, "deep1": 8, "deep2": 7, "deepest": 6,
            "return1": 7, "return2": 8, "end": 10,
            "gamma_burst": False
        },
        "spiritual_growth": {
            "start": 10, "induction": 7.83, "deep1": 6, "deep2": 4, "deepest": 3,
            "return1": 4, "return2": 6, "end": 10,
            "gamma_burst": True, "gamma_ratio": random.uniform(0.60, 0.70)
        },
        "creativity": {
            "start": 10, "induction": 8, "deep1": 7, "deep2": 5, "deepest": 7,
            "return1": 8, "return2": 10, "end": 10,
            "gamma_burst": True, "gamma_ratio": random.uniform(0.50, 0.60)
        },
        "sleep": {
            "start": 8, "induction": 6, "deep1": 4, "deep2": 2.5, "deepest": 1.5,
            "return1": 1.5, "return2": 1.5, "end": 1.5,
            "gamma_burst": False
        },
        "abundance": {
            "start": 10, "induction": 8, "deep1": 6, "deep2": 4, "deepest": 6,
            "return1": 8, "return2": 10, "end": 12,
            "gamma_burst": True, "gamma_ratio": random.uniform(0.65, 0.75)
        },
    }

    # Get outcome curve or fall back to healing
    curve = outcome_curves.get(therapeutic_outcome, outcome_curves["healing"])

    # Add small random variations to frequencies (±0.5 Hz)
    def jitter_freq(freq: float, amount: float = 0.5) -> float:
        return round(freq + random.uniform(-amount, amount), 1)

    # Calculate transition times with slight jitter (±15 seconds)
    def jitter_time(minutes: int, seconds: int = 0, jitter_secs: int = 15) -> str:
        total_secs = minutes * 60 + seconds + random.randint(-jitter_secs, jitter_secs)
        total_secs = max(0, total_secs)  # Don't go negative
        return f"{total_secs // 60}:{total_secs % 60:02d}"

    # Build 8-point binaural progression
    transitions = [
        {"time": "0:00", "freq": curve["start"], "state": "alpha"},
        {"time": jitter_time(duration_minutes // 8), "freq": jitter_freq(curve["induction"]), "state": "low_alpha"},
        {"time": jitter_time(duration_minutes // 4), "freq": jitter_freq(curve["deep1"]), "state": "theta_entry"},
        {"time": jitter_time(duration_minutes * 3 // 8), "freq": jitter_freq(curve["deep2"]), "state": "theta"},
        {"time": jitter_time(duration_minutes // 2), "freq": jitter_freq(curve["deepest"]), "state": "deep_theta"},
        {"time": jitter_time(duration_minutes * 5 // 8), "freq": jitter_freq(curve["return1"]), "state": "theta"},
        {"time": jitter_time(duration_minutes * 3 // 4), "freq": jitter_freq(curve["return2"]), "state": "low_alpha"},
        {"time": f"{duration_minutes - 2}:00", "freq": curve["end"], "state": "alpha"}
    ]

    # Carrier frequency selection (varies by style)
    carrier_frequencies = {
        "cosmic": random.choice([200, 216, 256]),  # Varied cosmic carriers
        "nature": random.choice([174, 196, 220]),  # Grounding frequencies
        "mystical": random.choice([396, 417, 432]),  # Sacred frequencies
        "technological": random.choice([200, 256, 288]),  # Neural frequencies
        "elemental": random.choice([174, 285, 396]),  # Elemental frequencies
    }
    carrier = carrier_frequencies.get(style, 432)

    binaural = {
        "carrier_frequency": carrier,
        "preset": outcome_to_preset.get(therapeutic_outcome, "healing_deep"),
        "start_hz": curve["start"],
        "end_hz": curve["end"],
        "transitions": transitions
    }

    # ==========================================================================
    # MULTI-LAYER BINAURAL FOR DEEPER SESSIONS
    # ==========================================================================
    if depth_level in ("Layer3", "Ipsissimus"):
        # Add secondary delta foundation layer
        binaural["multi_layer"] = {
            "enabled": True,
            "layers": [
                {
                    "name": "delta_foundation",
                    "frequency": 1.5,
                    "carrier_offset": 60,  # 60 Hz above main carrier
                    "level_db": -6
                }
            ]
        }
        if depth_level == "Ipsissimus":
            # Add alpha cushion for deepest work
            binaural["multi_layer"]["layers"].append({
                "name": "alpha_cushion",
                "frequency": 10,
                "carrier_offset": 30,
                "level_db": -8
            })

    # ==========================================================================
    # GAMMA BURST CONFIGURATION (outcome-specific timing)
    # ==========================================================================
    gamma_config = None
    if curve.get("gamma_burst"):
        gamma_time = int(duration_minutes * 60 * curve["gamma_ratio"])
        gamma_config = {
            "enabled": True,
            "bursts": [
                {
                    "time": gamma_time,
                    "frequency": random.choice([40, 42, 44]),  # Slight frequency variation
                    "duration_s": random.uniform(2.5, 4.0),
                    "description": "Primary insight activation"
                }
            ]
        }
        # Add second burst for transformation/confidence
        if curve.get("double_burst"):
            second_time = int(duration_minutes * 60 * curve["second_burst_ratio"])
            gamma_config["bursts"].append({
                "time": second_time,
                "frequency": random.choice([60, 70, 80]),  # Higher gamma for integration
                "duration_s": random.uniform(2.0, 3.5),
                "description": "Integration activation"
            })

    if gamma_config:
        binaural["gamma_bursts"] = gamma_config

    # ==========================================================================
    # ENVIRONMENT-BASED AMBIENCE (expanded)
    # ==========================================================================
    ambience_presets = {
        "garden": {"base": "garden_with_water", "layers": random.sample(["birds", "gentle_wind", "bees", "leaves_rustle"], 2)},
        "temple": {"base": "cathedral_reverb", "layers": random.sample(["distant_bells", "sacred_hum", "monks_chant", "incense_crackle"], 2)},
        "starship": {"base": "ship_ambient", "layers": random.sample(["subtle_engines", "electronic_hum", "scanner_beeps", "life_support"], 2)},
        "forest": {"base": "forest_night", "layers": random.sample(["crickets", "owl", "stream", "frogs", "wind_trees"], 2)},
        "ocean": {"base": "ocean_waves", "layers": random.sample(["seagulls", "wind", "dolphins", "underwater_bubbles"], 2)},
        "cave": {"base": "cave_drip", "layers": random.sample(["underground_stream", "distant_echo", "mineral_resonance"], 2)},
        "mountain": {"base": "mountain_wind", "layers": random.sample(["eagles", "rock_settle", "distant_thunder"], 2)},
        "sacred_space": {"base": "ethereal_pad", "layers": random.sample(["soft_chimes", "breath", "crystal_bowls", "angelic_hum"], 2)},
    }

    ambience = ambience_presets.get(environment, ambience_presets["sacred_space"])

    # ==========================================================================
    # STYLE-MATCHED SFX WITH TIMING JITTER
    # ==========================================================================
    # SFX pools by style
    sfx_pools = {
        "cosmic": ["starfield_sparkle", "ascending_pad", "nebula_pulse", "warp_shimmer", "cosmic_breath"],
        "nature": ["oceanic_whisper", "forest_chime", "water_drop", "leaf_flutter", "birdsong_echo"],
        "mystical": ["golden_bell", "halo_reverb", "crystal_shimmer", "choir_texture", "sacred_drone"],
        "technological": ["data_stream", "neural_pulse", "interface_tone", "quantum_hum", "circuit_cascade"],
        "elemental": ["fire_crackle", "water_flow", "earth_rumble", "wind_gust", "lightning_distant"],
    }

    # Select SFX pool based on style
    pool = sfx_pools.get(style, sfx_pools["mystical"])

    # Generate varied SFX timeline with jitter
    sfx_timeline = []

    # Opening effect (first 30-60 seconds)
    sfx_timeline.append({
        "time": jitter_time(0, 30, jitter_secs=10),
        "effect": random.choice(pool),
        "duration": random.uniform(2.0, 3.5)
    })

    # Induction marker
    sfx_timeline.append({
        "time": jitter_time(duration_minutes // 6),
        "effect": random.choice(pool),
        "duration": random.uniform(3.0, 5.0)
    })

    # Deep journey entry
    sfx_timeline.append({
        "time": jitter_time(duration_minutes // 3),
        "effect": random.choice(pool),
        "duration": random.uniform(3.5, 5.5)
    })

    # Deepest point (helm)
    sfx_timeline.append({
        "time": jitter_time(duration_minutes // 2),
        "effect": random.choice(pool),
        "duration": random.uniform(4.0, 6.0)
    })

    # Integration marker
    sfx_timeline.append({
        "time": jitter_time(duration_minutes * 2 // 3),
        "effect": random.choice(pool),
        "duration": random.uniform(3.0, 4.5)
    })

    # Return phase
    sfx_timeline.append({
        "time": jitter_time(duration_minutes * 5 // 6),
        "effect": random.choice(pool),
        "duration": random.uniform(3.0, 4.0)
    })

    # Awakening chime (always include, but varied)
    awakening_effects = ["awakening_chime", "sunrise_tone", "crystal_clear", "gentle_bell", "return_signal"]
    sfx_timeline.append({
        "time": f"{duration_minutes - random.randint(2, 4)}:00",
        "effect": random.choice(awakening_effects),
        "duration": random.uniform(2.5, 4.0)
    })

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
    audio_plan = suggest_audio_bed(
        duration_minutes=duration_minutes,
        environment="sacred_space",
        therapeutic_outcome="healing",
        depth_level=depth_level,
        style="mystical"
    )
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
    audio = suggest_audio_bed(
        duration_minutes=30,
        environment="garden",
        therapeutic_outcome="spiritual_growth",
        depth_level="Layer2",
        style="nature"
    )
    print("\nGenerated Audio Plan:")
    print(audio.to_json())

    # Get speech profile
    print("\nInduction Speech Profile:")
    print(json.dumps(get_speech_profile_config("induction"), indent=2))
