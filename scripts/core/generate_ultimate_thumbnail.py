#!/usr/bin/env python3
"""
Ultimate YouTube Thumbnail Generator for Sacred Digital Dreamweaver

Fully automated thumbnail generation combining:
- LLM-powered text optimization (2-5 punchy words)
- Auto style selection (template + palette based on outcome/theme)
- RAG knowledge integration
- Viral micro-effects
- A/B variant generation

This is the recommended entry point for thumbnail generation.

Usage:
    # Fully automatic (reads manifest, optimizes everything)
    python3 scripts/core/generate_ultimate_thumbnail.py sessions/{session}/

    # With variants for A/B testing
    python3 scripts/core/generate_ultimate_thumbnail.py sessions/{session}/ --variants 3

    # Manual overrides
    python3 scripts/core/generate_ultimate_thumbnail.py sessions/{session}/ \\
        --title "FORGE YOUR SOUL" --template portal_shockwave --palette gold_enlightenment
"""

import argparse
import os
import sys
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.core.generate_thumbnail import (
    generate_thumbnail,
    TEMPLATES,
    PALETTES,
    add_sigil_overlay
)
from scripts.ai.thumbnail_text_optimizer import optimize_thumbnail_text, ThumbnailTextSpec
from scripts.ai.thumbnail_style_selector import select_thumbnail_style, ThumbnailStyle


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_manifest(session_path: Path) -> Optional[Dict[str, Any]]:
    """Load session manifest.yaml."""
    manifest_path = session_path / "manifest.yaml"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def extract_session_metadata(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant metadata from manifest for thumbnail generation."""
    # Handle theme which can be string or dict
    raw_theme = manifest.get("theme", "")
    if isinstance(raw_theme, dict):
        theme_str = raw_theme.get("primary", "") or raw_theme.get("name", "") or str(raw_theme)
    else:
        theme_str = str(raw_theme) if raw_theme else ""

    metadata = {
        "title": manifest.get("title", ""),
        "subtitle": manifest.get("subtitle", theme_str),
        "outcome": manifest.get("desired_outcome", manifest.get("outcome", "default")),
        "theme": theme_str,
        "archetypes": [],
        "duration": None,
        "features": []
    }

    # Extract archetypes (handle both string lists and dict lists)
    if "archetypes" in manifest:
        archs = manifest["archetypes"]
        if isinstance(archs, list):
            # Handle list of dicts (with 'name' key) or list of strings
            archetype_names = []
            for arch in archs:
                if isinstance(arch, dict):
                    archetype_names.append(arch.get("name", str(arch)))
                else:
                    archetype_names.append(str(arch))
            metadata["archetypes"] = archetype_names
        elif isinstance(archs, dict):
            metadata["archetypes"] = list(archs.keys())

    # Extract duration
    if "duration" in manifest:
        dur = manifest["duration"]
        if isinstance(dur, (int, float)):
            minutes = int(dur // 60)
            seconds = int(dur % 60)
            metadata["duration"] = f"{minutes}:{seconds:02d}"
        elif isinstance(dur, dict):
            # Extract target_minutes from duration dict
            target_mins = dur.get("target_minutes", dur.get("minutes", 0))
            if target_mins:
                metadata["duration"] = f"{int(target_mins)}:00"
        elif dur:
            metadata["duration"] = str(dur)

    # Extract features
    features = []
    if "binaural" in manifest:
        bin_cfg = manifest["binaural"]
        if isinstance(bin_cfg, dict) and "base_frequency" in bin_cfg:
            features.append(f"{bin_cfg['base_frequency']}Hz")
    if "brainwave_target" in manifest:
        features.append(manifest["brainwave_target"].capitalize())
    metadata["features"] = features

    return metadata


def ensure_output_directories(session_path: Path) -> Dict[str, Path]:
    """Ensure output directories exist and return paths."""
    output_dir = session_path / "output"
    thumbnails_dir = output_dir / "thumbnails"
    youtube_dir = output_dir / "youtube_package"

    output_dir.mkdir(parents=True, exist_ok=True)
    thumbnails_dir.mkdir(parents=True, exist_ok=True)

    return {
        "output": output_dir,
        "thumbnails": thumbnails_dir,
        "youtube_package": youtube_dir if youtube_dir.exists() else None
    }


# =============================================================================
# VARIANT GENERATION
# =============================================================================

def generate_variant_configs(
    base_style: ThumbnailStyle,
    base_text: ThumbnailTextSpec,
    num_variants: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate variant configurations for A/B testing.

    Variants differ in:
    - Color palette (shift to related palettes)
    - Title text (use variants from text optimizer)
    - Template (sometimes)
    """
    variants = []

    # Variant 1: Primary (best guess)
    variants.append({
        "suffix": "v1",
        "template": base_style.template,
        "palette": base_style.palette,
        "title": base_text.title,
        "subtitle": base_text.subtitle,
        "description": "Primary variant (auto-optimized)"
    })

    if num_variants < 2:
        return variants

    # Variant 2: Alternative palette
    palette_alternatives = {
        "sacred_light": "gold_enlightenment",
        "gold_enlightenment": "sacred_light",
        "cosmic_journey": "amethyst_mystery",
        "amethyst_mystery": "cosmic_journey",
        "garden_eden": "aurora_healing",
        "aurora_healing": "celestial_blue",
        "ancient_temple": "obsidian_shadow",
        "obsidian_shadow": "volcanic_forge",
        "volcanic_forge": "gold_enlightenment",
        "neural_network": "sapphire_depth",
        "sapphire_depth": "cosmic_journey",
        "celestial_blue": "sapphire_depth",
    }
    alt_palette = palette_alternatives.get(base_style.palette, "sacred_light")

    # Use first text variant if available
    alt_title = base_text.variants[0] if base_text.variants else base_text.title

    variants.append({
        "suffix": "v2",
        "template": base_style.template,
        "palette": alt_palette,
        "title": alt_title,
        "subtitle": base_text.subtitle,
        "description": f"Color shift variant ({alt_palette})"
    })

    if num_variants < 3:
        return variants

    # Variant 3: Different template + title
    template_alternatives = {
        "portal_gateway": "portal_shockwave",
        "portal_shockwave": "transformation_shot",
        "sacred_symbol": "impossible_landscape",
        "journey_scene": "archetype_reveal",
        "abstract_energy": "portal_shockwave",
        "archetype_reveal": "portal_shockwave",
        "impossible_landscape": "sacred_symbol",
        "viewer_pov": "portal_gateway",
        "transformation_shot": "archetype_reveal",
        "shadow_confrontation": "viewer_pov",
    }
    alt_template = template_alternatives.get(base_style.template, "portal_gateway")

    # Use second text variant if available
    alt_title_2 = base_text.variants[1] if len(base_text.variants) > 1 else base_text.title

    variants.append({
        "suffix": "v3",
        "template": alt_template,
        "palette": base_style.palette,
        "title": alt_title_2,
        "subtitle": None,  # Try without subtitle
        "description": f"Template variant ({alt_template})"
    })

    return variants[:num_variants]


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================

def generate_ultimate_thumbnail(
    session_path: Path,
    num_variants: int = 1,
    title_override: Optional[str] = None,
    template_override: Optional[str] = None,
    palette_override: Optional[str] = None,
    subtitle_override: Optional[str] = None,
    add_sigil: bool = True,
    use_llm: bool = True,
    verbose: bool = True
) -> List[Path]:
    """
    Generate optimized YouTube thumbnail(s) for a session.

    Args:
        session_path: Path to session directory
        num_variants: Number of A/B variants to generate (1-3)
        title_override: Manual title override (skips LLM optimization)
        template_override: Manual template override (skips auto-selection)
        palette_override: Manual palette override (skips auto-selection)
        subtitle_override: Manual subtitle override
        add_sigil: Whether to add branded sigil overlay
        use_llm: Whether to use LLM for text optimization
        verbose: Print progress information

    Returns:
        List of paths to generated thumbnail files
    """
    session_path = Path(session_path)

    if verbose:
        print("=" * 70)
        print("ULTIMATE THUMBNAIL GENERATOR")
        print("=" * 70)
        print(f"Session: {session_path.name}")
        print(f"Variants: {num_variants}")
        print()

    # Load manifest
    manifest = load_manifest(session_path)
    if not manifest:
        print("Warning: No manifest.yaml found, using defaults")
        manifest = {}

    # Extract metadata
    metadata = extract_session_metadata(manifest)

    if verbose:
        print("METADATA EXTRACTED:")
        print(f"  Title: {metadata['title']}")
        print(f"  Outcome: {metadata['outcome']}")
        print(f"  Theme: {metadata['theme']}")
        print(f"  Archetypes: {', '.join(metadata['archetypes']) if metadata['archetypes'] else 'None'}")
        print()

    # Step 1: Optimize title text
    if title_override:
        text_spec = ThumbnailTextSpec(
            title=title_override.upper(),
            subtitle=subtitle_override,
            variants=[]
        )
        if verbose:
            print("TITLE: Using manual override")
    else:
        if verbose:
            print("TITLE OPTIMIZATION...")
        text_spec = optimize_thumbnail_text(
            manifest_title=metadata["title"] or session_path.name.replace("-", " "),
            outcome=metadata["outcome"],
            archetypes=metadata["archetypes"],
            theme=metadata["theme"],
            prefer_llm=use_llm
        )

    if verbose:
        print(f"  Primary: {text_spec.title}")
        if text_spec.subtitle:
            print(f"  Subtitle: {text_spec.subtitle}")
        if text_spec.variants:
            print(f"  Variants: {', '.join(text_spec.variants)}")
        print()

    # Step 2: Select style (template + palette)
    if template_override and palette_override:
        style = ThumbnailStyle(
            template=template_override,
            palette=palette_override,
            reasoning="Manual override"
        )
        if verbose:
            print("STYLE: Using manual override")
    else:
        if verbose:
            print("STYLE SELECTION...")
        style = select_thumbnail_style(
            outcome=metadata["outcome"],
            theme=metadata["theme"],
            archetypes=metadata["archetypes"],
            title=metadata["title"]
        )

        # Apply any overrides
        if template_override:
            style.template = template_override
        if palette_override:
            style.palette = palette_override

    if verbose:
        print(f"  Template: {style.template}")
        print(f"  Palette: {style.palette}")
        print(f"  Reasoning: {style.reasoning}")
        print()

    # Step 3: Generate variant configurations
    variants = generate_variant_configs(style, text_spec, num_variants)

    if verbose:
        print(f"GENERATING {len(variants)} VARIANT(S)...")
        print()

    # Ensure output directories
    dirs = ensure_output_directories(session_path)

    # Step 4: Generate each variant
    generated_paths = []

    for i, variant in enumerate(variants):
        if verbose:
            print(f"--- Variant {i + 1}: {variant['description']} ---")

        # Determine output path
        if len(variants) == 1:
            output_path = dirs["thumbnails"] / "youtube_thumbnail.png"
        else:
            output_path = dirs["thumbnails"] / f"thumbnail_{variant['suffix']}.png"

        # Generate thumbnail
        try:
            result_path = generate_thumbnail(
                session_path=session_path,
                template_name=variant["template"],
                palette_name=variant["palette"],
                title=variant["title"],
                subtitle=variant["subtitle"] if subtitle_override is None else subtitle_override,
                output_path=output_path,
                duration=metadata["duration"],
                features=metadata["features"]
            )

            # Add sigil overlay if requested
            if add_sigil and result_path.exists():
                from PIL import Image
                img = Image.open(result_path)
                palette = PALETTES.get(variant["palette"], PALETTES["sacred_light"])
                img = add_sigil_overlay(img, palette, opacity=0.05, position="bottom_left")
                img = img.convert('RGB')
                img.save(result_path, 'PNG', optimize=True)

            generated_paths.append(result_path)

            if verbose:
                print(f"  Saved: {result_path}")

        except Exception as e:
            print(f"  ERROR: Failed to generate variant {variant['suffix']}: {e}")

    # Step 5: Copy primary variant to standard locations
    if generated_paths:
        primary = generated_paths[0]

        # Copy to output/youtube_thumbnail.png (canonical location)
        canonical_path = dirs["output"] / "youtube_thumbnail.png"
        if canonical_path != primary:
            shutil.copy(primary, canonical_path)
            if verbose:
                print(f"\nCopied primary to: {canonical_path}")

        # Copy to youtube_package if it exists
        if dirs["youtube_package"]:
            package_path = dirs["youtube_package"] / "thumbnail.png"
            shutil.copy(primary, package_path)
            if verbose:
                print(f"Copied to youtube_package: {package_path}")

    if verbose:
        print()
        print("=" * 70)
        print(f"COMPLETE: Generated {len(generated_paths)} thumbnail(s)")
        print("=" * 70)

    return generated_paths


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate optimized YouTube thumbnail(s) for a Dreamweaver session",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Fully automatic
    python3 generate_ultimate_thumbnail.py sessions/iron-soul-forge/

    # Generate 3 variants for A/B testing
    python3 generate_ultimate_thumbnail.py sessions/iron-soul-forge/ --variants 3

    # Manual title override
    python3 generate_ultimate_thumbnail.py sessions/iron-soul-forge/ --title "FORGE YOUR SOUL"

    # Full manual control
    python3 generate_ultimate_thumbnail.py sessions/iron-soul-forge/ \\
        --title "FORGE YOUR SOUL" \\
        --template portal_shockwave \\
        --palette volcanic_forge \\
        --no-sigil

Available Templates:
    portal_gateway, sacred_symbol, journey_scene, abstract_energy,
    portal_shockwave, archetype_reveal, impossible_landscape,
    viewer_pov, transformation_shot, shadow_confrontation

Available Palettes:
    sacred_light, cosmic_journey, garden_eden, ancient_temple, neural_network,
    sapphire_depth, gold_enlightenment, amethyst_mystery, aurora_healing,
    obsidian_shadow, volcanic_forge, celestial_blue
        """
    )

    parser.add_argument("session_path", type=Path, help="Path to session directory")
    parser.add_argument("--variants", "-v", type=int, default=1, choices=[1, 2, 3],
                        help="Number of A/B variants to generate (default: 1)")
    parser.add_argument("--title", "-t", help="Override title text (UPPERCASE)")
    parser.add_argument("--subtitle", "-s", help="Override subtitle text")
    parser.add_argument("--template", choices=list(TEMPLATES.keys()),
                        help="Override template selection")
    parser.add_argument("--palette", choices=list(PALETTES.keys()),
                        help="Override palette selection")
    parser.add_argument("--no-sigil", action="store_true",
                        help="Don't add branded sigil overlay")
    parser.add_argument("--no-llm", action="store_true",
                        help="Use rule-based text optimization only (no LLM)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Minimal output")

    args = parser.parse_args()

    if not args.session_path.exists():
        print(f"ERROR: Session path does not exist: {args.session_path}")
        sys.exit(1)

    results = generate_ultimate_thumbnail(
        session_path=args.session_path,
        num_variants=args.variants,
        title_override=args.title,
        template_override=args.template,
        palette_override=args.palette,
        subtitle_override=args.subtitle,
        add_sigil=not args.no_sigil,
        use_llm=not args.no_llm,
        verbose=not args.quiet
    )

    if not results:
        print("ERROR: No thumbnails were generated")
        sys.exit(1)

    # Print final paths for scripting
    if args.quiet:
        for path in results:
            print(path)


if __name__ == "__main__":
    main()
