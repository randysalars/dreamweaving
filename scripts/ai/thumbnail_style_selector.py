#!/usr/bin/env python3
"""
Thumbnail Style Selector for Sacred Digital Dreamweaver

Automatically selects optimal template and color palette based on session metadata.
Uses mappings derived from the Viral Thumbnail System and knowledge base.

Key Mappings:
- Outcome → Template (e.g., healing → portal_gateway)
- Outcome → Palette (e.g., empowerment → gold_enlightenment)
- Theme keywords → Palette overrides (e.g., "eden" → garden_eden)
- Archetypes → Visual style hints

Usage:
    from scripts.ai.thumbnail_style_selector import select_thumbnail_style

    style = select_thumbnail_style(
        outcome="empowerment",
        theme="Iron Soul Forge",
        archetypes=["Forge-Father", "Alchemist"]
    )

    print(style.template)  # "portal_shockwave"
    print(style.palette)   # "gold_enlightenment"
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ThumbnailStyle:
    """Selected thumbnail style configuration."""
    template: str
    palette: str
    reasoning: str = ""
    micro_effects: List[str] = field(default_factory=list)
    focal_element: Optional[str] = None
    color_accents: List[str] = field(default_factory=list)


# =============================================================================
# TEMPLATE MAPPINGS (from Viral Thumbnail System)
# =============================================================================

# Templates available (existing + new from viral system)
AVAILABLE_TEMPLATES = {
    # Existing templates
    "portal_gateway": {
        "description": "Luminous center with dark edges, spiritual journeys",
        "best_for": ["healing", "spiritual_growth", "relaxation", "sleep"],
        "focal_style": "center_glow"
    },
    "sacred_symbol": {
        "description": "Central glowing symbol focus",
        "best_for": ["spiritual_growth", "clarity", "transformation"],
        "focal_style": "symbol_center"
    },
    "journey_scene": {
        "description": "Full-frame scene with text overlay",
        "best_for": ["confidence", "abundance", "default"],
        "focal_style": "scene_wide"
    },
    "abstract_energy": {
        "description": "Flowing energy patterns with centered title",
        "best_for": ["empowerment", "transformation", "shadow_work"],
        "focal_style": "dynamic_flow"
    },

    # NEW templates from Viral Thumbnail System
    "portal_shockwave": {
        "description": "Right silhouette + center portal (highest CTR)",
        "best_for": ["empowerment", "transformation", "spiritual_growth"],
        "focal_style": "right_subject_portal"
    },
    "archetype_reveal": {
        "description": "Close-up archetype with dramatic aura",
        "best_for": ["empowerment", "confidence", "shadow_work"],
        "focal_style": "character_focus"
    },
    "impossible_landscape": {
        "description": "Jaw-dropping scene, no character",
        "best_for": ["spiritual_growth", "abundance", "clarity"],
        "focal_style": "scene_dramatic"
    },
    "viewer_pov": {
        "description": "Viewer hands/silhouette in frame",
        "best_for": ["transformation", "shadow_work", "healing"],
        "focal_style": "first_person"
    },
    "transformation_shot": {
        "description": "Golden rays, crown/halo effect",
        "best_for": ["transformation", "abundance", "spiritual_growth"],
        "focal_style": "radiant_figure"
    },
    "shadow_confrontation": {
        "description": "Dark mirror reflection, threshold",
        "best_for": ["shadow_work", "transformation", "healing"],
        "focal_style": "mirror_duality"
    }
}

# Primary outcome → template mapping
OUTCOME_TEMPLATE_MAP = {
    "healing": "portal_gateway",
    "transformation": "portal_shockwave",
    "empowerment": "portal_shockwave",
    "confidence": "archetype_reveal",
    "relaxation": "portal_gateway",
    "spiritual_growth": "impossible_landscape",
    "abundance": "transformation_shot",
    "clarity": "sacred_symbol",
    "sleep": "portal_gateway",
    "shadow_work": "shadow_confrontation",
    "default": "portal_gateway"
}


# =============================================================================
# PALETTE MAPPINGS (existing + new from Viral System color psychology)
# =============================================================================

AVAILABLE_PALETTES = {
    # Existing palettes
    "sacred_light": {
        "description": "Gold/cream on cosmic dark",
        "colors": {"primary": "#FFD700", "secondary": "#F4E4BC", "background": "#0A0A1A"},
        "best_for": ["healing", "spiritual_growth", "confidence", "abundance"]
    },
    "cosmic_journey": {
        "description": "Purple/blue on deep space",
        "colors": {"primary": "#9B6DFF", "secondary": "#64B5F6", "background": "#0D0221"},
        "best_for": ["transformation", "spiritual_growth", "clarity"]
    },
    "garden_eden": {
        "description": "Emerald/gold on forest shadow",
        "colors": {"primary": "#50C878", "secondary": "#FFD700", "background": "#0F2818"},
        "best_for": ["healing", "relaxation", "abundance"]
    },
    "ancient_temple": {
        "description": "Antique gold on temple shadow",
        "colors": {"primary": "#D4AF37", "secondary": "#8B4513", "background": "#1A0F0A"},
        "best_for": ["shadow_work", "transformation", "spiritual_growth"]
    },
    "neural_network": {
        "description": "Cyan/purple on digital void",
        "colors": {"primary": "#00D4FF", "secondary": "#9B6DFF", "background": "#0A0A1A"},
        "best_for": ["clarity", "transformation", "empowerment"]
    },

    # NEW palettes from Viral Thumbnail System color psychology
    "sapphire_depth": {
        "description": "Sapphire Blue + Gold (discovery, depth)",
        "colors": {"primary": "#1E40AF", "secondary": "#FFD700", "background": "#0A0A1A"},
        "best_for": ["spiritual_growth", "clarity", "relaxation"]
    },
    "gold_enlightenment": {
        "description": "Gold + White (transformation, enlightenment)",
        "colors": {"primary": "#FFD700", "secondary": "#FFFFFF", "background": "#1A1A0A"},
        "best_for": ["empowerment", "confidence", "abundance", "transformation"]
    },
    "amethyst_mystery": {
        "description": "Violet + Gold (prophecy, mystery)",
        "colors": {"primary": "#7C3AED", "secondary": "#FFD700", "background": "#0D0221"},
        "best_for": ["spiritual_growth", "clarity", "shadow_work"]
    },
    "aurora_healing": {
        "description": "Teal + Silver (emotion, healing)",
        "colors": {"primary": "#14B8A6", "secondary": "#C0C0C0", "background": "#0A1A1A"},
        "best_for": ["healing", "relaxation", "clarity"]
    },
    "obsidian_shadow": {
        "description": "Black + Ember (shadow work)",
        "colors": {"primary": "#1A1A1A", "secondary": "#DC2626", "background": "#0A0505"},
        "best_for": ["shadow_work", "transformation"]
    },
    "volcanic_forge": {
        "description": "Iron Red + Gold (strength, forging)",
        "colors": {"primary": "#B91C1C", "secondary": "#FFD700", "background": "#1A0A0A"},
        "best_for": ["empowerment", "confidence", "shadow_work"]
    },
    "celestial_blue": {
        "description": "Soft blue + white (peace, heavenly)",
        "colors": {"primary": "#60A5FA", "secondary": "#FFFFFF", "background": "#0A0A1A"},
        "best_for": ["relaxation", "sleep", "healing", "spiritual_growth"]
    }
}

# Primary outcome → palette mapping
OUTCOME_PALETTE_MAP = {
    "healing": "aurora_healing",
    "transformation": "cosmic_journey",
    "empowerment": "gold_enlightenment",
    "confidence": "gold_enlightenment",
    "relaxation": "celestial_blue",
    "spiritual_growth": "amethyst_mystery",
    "abundance": "sacred_light",
    "clarity": "sapphire_depth",
    "sleep": "celestial_blue",
    "shadow_work": "obsidian_shadow",
    "default": "sacred_light"
}


# =============================================================================
# THEME KEYWORD DETECTION
# =============================================================================

# Theme keywords that override default selections
THEME_PALETTE_OVERRIDES = {
    # Nature/Eden themes
    r"\b(eden|garden|forest|nature|tree|leaf|green)\b": "garden_eden",

    # Cosmic/Space themes
    r"\b(cosmic|star|galaxy|universe|astral|space|celestial|nebula)\b": "cosmic_journey",

    # Temple/Ancient themes
    r"\b(temple|ancient|ruins|tomb|pyramid|stone|ritual)\b": "ancient_temple",

    # Fire/Forge themes
    r"\b(forge|fire|iron|flame|volcanic|ember|burn|metal)\b": "volcanic_forge",

    # Ocean/Water themes
    r"\b(ocean|sea|water|wave|atlantis|aqua|deep)\b": "sapphire_depth",

    # Neural/Tech themes
    r"\b(neural|network|brain|tech|digital|cyber|quantum)\b": "neural_network",

    # Shadow themes
    r"\b(shadow|dark|mirror|night|obsidian|void)\b": "obsidian_shadow",

    # Light/Divine themes
    r"\b(light|divine|angel|heaven|sacred|holy|christ)\b": "sacred_light",

    # Purple/Mystic themes
    r"\b(mystic|prophecy|vision|seer|oracle|violet|amethyst)\b": "amethyst_mystery",
}

THEME_TEMPLATE_OVERRIDES = {
    # Portal themes
    r"\b(portal|gate|door|threshold|passage|entry)\b": "portal_shockwave",

    # Mirror/Shadow themes
    r"\b(mirror|shadow|reflection|duality|dark)\b": "shadow_confrontation",

    # Landscape themes
    r"\b(realm|world|land|kingdom|dimension)\b": "impossible_landscape",

    # Character themes
    r"\b(archetype|character|guide|master|figure)\b": "archetype_reveal",

    # Transformation themes
    r"\b(transform|become|evolve|emerge|rise|ascend)\b": "transformation_shot",
}


# =============================================================================
# ARCHETYPE STYLE MAPPINGS
# =============================================================================

# Archetype names → visual style hints
ARCHETYPE_VISUAL_HINTS = {
    # Fire/Forge archetypes
    "forge-father": {"palette": "volcanic_forge", "template": "archetype_reveal", "effects": ["edge_glow", "ember_particles"]},
    "alchemist": {"palette": "gold_enlightenment", "template": "transformation_shot", "effects": ["center_glow", "sigil"]},

    # Water/Healing archetypes
    "harmonic weaver": {"palette": "aurora_healing", "template": "portal_gateway", "effects": ["center_glow", "fog"]},
    "healer": {"palette": "aurora_healing", "template": "portal_gateway", "effects": ["center_glow"]},

    # Cosmic archetypes
    "navigator": {"palette": "sapphire_depth", "template": "impossible_landscape", "effects": ["fog", "sigil"]},
    "starweaver": {"palette": "cosmic_journey", "template": "impossible_landscape", "effects": ["center_glow", "particles"]},
    "soul star": {"palette": "gold_enlightenment", "template": "transformation_shot", "effects": ["radiant_glow"]},

    # Shadow archetypes
    "mirror sage": {"palette": "obsidian_shadow", "template": "shadow_confrontation", "effects": ["fog", "edge_glow"]},
    "dreamwarden": {"palette": "obsidian_shadow", "template": "shadow_confrontation", "effects": ["fog"]},
    "shadow guide": {"palette": "obsidian_shadow", "template": "shadow_confrontation", "effects": ["edge_glow"]},

    # Wisdom archetypes
    "silent prophet": {"palette": "amethyst_mystery", "template": "sacred_symbol", "effects": ["sigil", "fog"]},
    "oracle": {"palette": "amethyst_mystery", "template": "sacred_symbol", "effects": ["sigil"]},
    "guardian": {"palette": "ancient_temple", "template": "archetype_reveal", "effects": ["edge_glow"]},

    # Nature archetypes
    "earthkeeper": {"palette": "garden_eden", "template": "impossible_landscape", "effects": ["fog"]},
    "greenman": {"palette": "garden_eden", "template": "impossible_landscape", "effects": ["fog", "particles"]},
}


# =============================================================================
# MICRO-EFFECTS RECOMMENDATIONS
# =============================================================================

EFFECT_RECOMMENDATIONS = {
    "healing": ["center_glow", "fog", "soft_vignette"],
    "transformation": ["edge_glow", "particles", "sigil"],
    "empowerment": ["edge_glow", "sigil", "strong_vignette"],
    "confidence": ["edge_glow", "center_glow"],
    "relaxation": ["fog", "soft_vignette", "center_glow"],
    "spiritual_growth": ["sigil", "fog", "particles"],
    "abundance": ["center_glow", "particles", "radiant_glow"],
    "clarity": ["center_glow", "sigil"],
    "sleep": ["fog", "soft_vignette"],
    "shadow_work": ["strong_vignette", "fog", "edge_glow"],
    "default": ["center_glow", "vignette"]
}


# =============================================================================
# MAIN SELECTION FUNCTIONS
# =============================================================================

def _normalize_outcome(outcome: str) -> str:
    """Normalize outcome string."""
    return outcome.lower().replace(" ", "_").replace("-", "_")


def _detect_theme_override(
    text: str,
    override_map: Dict[str, str]
) -> Optional[str]:
    """Check if text matches any theme keywords."""
    text_lower = text.lower()
    for pattern, value in override_map.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return value
    return None


def _get_archetype_hints(archetypes: List[str]) -> Dict[str, Any]:
    """Get visual hints from archetypes."""
    hints = {}

    for arch in archetypes:
        arch_key = arch.lower().replace("_", " ").replace("-", " ").strip()

        # Check exact match
        if arch_key in ARCHETYPE_VISUAL_HINTS:
            arch_hints = ARCHETYPE_VISUAL_HINTS[arch_key]
            hints["palette"] = arch_hints.get("palette")
            hints["template"] = arch_hints.get("template")
            hints["effects"] = arch_hints.get("effects", [])
            break

        # Check partial match
        for key, value in ARCHETYPE_VISUAL_HINTS.items():
            if key in arch_key or arch_key in key:
                hints["palette"] = value.get("palette")
                hints["template"] = value.get("template")
                hints["effects"] = value.get("effects", [])
                break

        if hints:
            break

    return hints


def select_thumbnail_style(
    outcome: str = "default",
    theme: str = "",
    archetypes: Optional[List[str]] = None,
    title: str = "",
    prefer_viral_templates: bool = True
) -> ThumbnailStyle:
    """
    Select optimal thumbnail style based on session metadata.

    Args:
        outcome: Session outcome (healing, transformation, etc.)
        theme: Session theme or description
        archetypes: List of archetype names
        title: Session title (used for keyword detection)
        prefer_viral_templates: If True, prefer new viral templates over legacy

    Returns:
        ThumbnailStyle with selected template, palette, and effects

    Example:
        >>> style = select_thumbnail_style(
        ...     outcome="empowerment",
        ...     theme="Iron Soul Forge",
        ...     archetypes=["Forge-Father"]
        ... )
        >>> print(style.template)  # "portal_shockwave" or "archetype_reveal"
        >>> print(style.palette)   # "volcanic_forge" (due to "Iron" keyword)
    """
    outcome = _normalize_outcome(outcome)
    archetypes = archetypes or []

    # Combine text for keyword detection
    all_text = f"{theme} {title} {' '.join(archetypes)}"

    # Start with outcome-based defaults
    template = OUTCOME_TEMPLATE_MAP.get(outcome, "portal_gateway")
    palette = OUTCOME_PALETTE_MAP.get(outcome, "sacred_light")
    effects = EFFECT_RECOMMENDATIONS.get(outcome, ["center_glow", "vignette"])

    reasoning_parts = [f"Outcome '{outcome}' maps to template '{template}' and palette '{palette}'"]

    # Check for theme-based overrides
    theme_palette = _detect_theme_override(all_text, THEME_PALETTE_OVERRIDES)
    if theme_palette:
        palette = theme_palette
        reasoning_parts.append(f"Theme keyword detected, overriding palette to '{palette}'")

    theme_template = _detect_theme_override(all_text, THEME_TEMPLATE_OVERRIDES)
    if theme_template:
        template = theme_template
        reasoning_parts.append(f"Theme keyword detected, overriding template to '{template}'")

    # Check for archetype-based hints
    arch_hints = _get_archetype_hints(archetypes)
    if arch_hints:
        if arch_hints.get("palette"):
            palette = arch_hints["palette"]
            reasoning_parts.append(f"Archetype style detected, using palette '{palette}'")
        if arch_hints.get("template"):
            template = arch_hints["template"]
            reasoning_parts.append(f"Archetype style detected, using template '{template}'")
        if arch_hints.get("effects"):
            effects = arch_hints["effects"]

    # Get color accents from selected palette
    color_accents = []
    if palette in AVAILABLE_PALETTES:
        colors = AVAILABLE_PALETTES[palette]["colors"]
        color_accents = [colors["primary"], colors["secondary"]]

    return ThumbnailStyle(
        template=template,
        palette=palette,
        reasoning=" | ".join(reasoning_parts),
        micro_effects=effects,
        focal_element=archetypes[0] if archetypes else None,
        color_accents=color_accents
    )


def get_available_templates() -> Dict[str, Dict]:
    """Get all available templates with descriptions."""
    return AVAILABLE_TEMPLATES.copy()


def get_available_palettes() -> Dict[str, Dict]:
    """Get all available palettes with descriptions."""
    return AVAILABLE_PALETTES.copy()


def get_template_info(template_name: str) -> Optional[Dict]:
    """Get info about a specific template."""
    return AVAILABLE_TEMPLATES.get(template_name)


def get_palette_info(palette_name: str) -> Optional[Dict]:
    """Get info about a specific palette."""
    return AVAILABLE_PALETTES.get(palette_name)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI for testing style selection."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Select thumbnail style based on session metadata"
    )
    parser.add_argument("--outcome", "-o", default="default", help="Session outcome")
    parser.add_argument("--theme", "-t", default="", help="Session theme")
    parser.add_argument("--archetypes", "-a", nargs="+", help="Archetype names")
    parser.add_argument("--title", default="", help="Session title")
    parser.add_argument("--list-templates", action="store_true", help="List all templates")
    parser.add_argument("--list-palettes", action="store_true", help="List all palettes")

    args = parser.parse_args()

    if args.list_templates:
        print("\nAVAILABLE TEMPLATES:")
        print("=" * 60)
        for name, info in AVAILABLE_TEMPLATES.items():
            print(f"\n{name}:")
            print(f"  Description: {info['description']}")
            print(f"  Best for: {', '.join(info['best_for'])}")
        return

    if args.list_palettes:
        print("\nAVAILABLE PALETTES:")
        print("=" * 60)
        for name, info in AVAILABLE_PALETTES.items():
            print(f"\n{name}:")
            print(f"  Description: {info['description']}")
            print(f"  Best for: {', '.join(info['best_for'])}")
            colors = info['colors']
            print(f"  Primary: {colors['primary']}, Secondary: {colors['secondary']}")
        return

    style = select_thumbnail_style(
        outcome=args.outcome,
        theme=args.theme,
        archetypes=args.archetypes,
        title=args.title
    )

    print("\n" + "=" * 60)
    print("THUMBNAIL STYLE SELECTION")
    print("=" * 60)
    print(f"\nInput:")
    print(f"  Outcome: {args.outcome}")
    print(f"  Theme: {args.theme or '(none)'}")
    print(f"  Archetypes: {', '.join(args.archetypes) if args.archetypes else '(none)'}")
    print(f"  Title: {args.title or '(none)'}")
    print()
    print(f"Selected Style:")
    print(f"  Template: {style.template}")
    print(f"  Palette: {style.palette}")
    print(f"  Effects: {', '.join(style.micro_effects)}")
    if style.focal_element:
        print(f"  Focal Element: {style.focal_element}")
    print(f"  Color Accents: {', '.join(style.color_accents)}")
    print()
    print(f"Reasoning: {style.reasoning}")
    print("=" * 60)


if __name__ == "__main__":
    main()
