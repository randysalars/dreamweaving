#!/usr/bin/env python3
"""
YouTube Thumbnail Generator for Sacred Digital Dreamweaver

Generates high-CTR thumbnails following expert design principles:
- Instant clarity at 200x112 pixels
- Strong visual hierarchy
- Mobile-first design
- Consistent branding

Usage:
    python3 scripts/core/generate_thumbnail.py sessions/{session}/ [options]

Options:
    --template      Template style (portal_gateway, sacred_symbol, journey_scene, abstract_energy)
    --palette       Color palette (sacred_light, cosmic_journey, garden_eden, ancient_temple)
    --title         Override title text
    --subtitle      Override subtitle text
    --base-image    Path to base image (defaults to first image in images/uploaded/)
    --output        Output path (defaults to output/youtube_thumbnail.png)
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import yaml

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
except ImportError:
    print("ERROR: Pillow library required. Install with: pip install Pillow")
    sys.exit(1)


# =============================================================================
# COLOR PALETTES
# =============================================================================

PALETTES = {
    "sacred_light": {
        "name": "Sacred Light",
        "primary": "#FFD700",      # Gold
        "secondary": "#F4E4BC",    # Warm cream
        "accent": "#FFFFFF",       # Pure white
        "background": "#0A0A1A",   # Deep cosmic blue-black
        "text": "#FFFFFF",
        "text_shadow": "#000000",
        "glow": "#FFD700",
    },
    "cosmic_journey": {
        "name": "Cosmic Journey",
        "primary": "#9B6DFF",      # Mystic purple
        "secondary": "#64B5F6",    # Celestial blue
        "accent": "#FF6B9D",       # Ethereal pink
        "background": "#0D0221",   # Deep space purple
        "text": "#FFFFFF",
        "text_shadow": "#1A0033",
        "glow": "#9B6DFF",
    },
    "garden_eden": {
        "name": "Garden/Eden",
        "primary": "#50C878",      # Emerald green
        "secondary": "#FFD700",    # Sunlight gold
        "accent": "#FFFFFF",       # Divine light
        "background": "#0F2818",   # Forest shadow
        "text": "#FFFFFF",
        "text_shadow": "#0A1A0F",
        "glow": "#50C878",
    },
    "ancient_temple": {
        "name": "Ancient Temple",
        "primary": "#D4AF37",      # Antique gold
        "secondary": "#8B4513",    # Warm bronze
        "accent": "#FFF8DC",       # Candlelight
        "background": "#1A0F0A",   # Temple shadow
        "text": "#FFFFFF",
        "text_shadow": "#0D0805",
        "glow": "#D4AF37",
    },
    "neural_network": {
        "name": "Neural Network",
        "primary": "#00D4FF",      # Electric cyan
        "secondary": "#9B6DFF",    # Neural purple
        "accent": "#FF6B9D",       # Synapse pink
        "background": "#0A0A1A",   # Digital void
        "text": "#FFFFFF",
        "text_shadow": "#000022",
        "glow": "#00D4FF",
    },
    # NEW PALETTES from Viral Thumbnail System color psychology
    "sapphire_depth": {
        "name": "Sapphire Depth",
        "primary": "#1E40AF",      # Deep sapphire blue
        "secondary": "#FFD700",    # Gold accent
        "accent": "#60A5FA",       # Light blue
        "background": "#0A0A1A",   # Cosmic void
        "text": "#FFFFFF",
        "text_shadow": "#000033",
        "glow": "#1E40AF",
    },
    "gold_enlightenment": {
        "name": "Gold Enlightenment",
        "primary": "#FFD700",      # Brilliant gold
        "secondary": "#FFFFFF",    # Pure white
        "accent": "#FEF3C7",       # Warm cream
        "background": "#1A1A0A",   # Dark gold shadow
        "text": "#FFFFFF",
        "text_shadow": "#0A0A00",
        "glow": "#FFD700",
    },
    "amethyst_mystery": {
        "name": "Amethyst Mystery",
        "primary": "#7C3AED",      # Deep violet
        "secondary": "#FFD700",    # Gold accent
        "accent": "#A78BFA",       # Light violet
        "background": "#0D0221",   # Deep purple void
        "text": "#FFFFFF",
        "text_shadow": "#1A0033",
        "glow": "#7C3AED",
    },
    "aurora_healing": {
        "name": "Aurora Healing",
        "primary": "#14B8A6",      # Healing teal
        "secondary": "#C0C0C0",    # Silver
        "accent": "#5EEAD4",       # Light teal
        "background": "#0A1A1A",   # Deep teal shadow
        "text": "#FFFFFF",
        "text_shadow": "#001A1A",
        "glow": "#14B8A6",
    },
    "obsidian_shadow": {
        "name": "Obsidian Shadow",
        "primary": "#1A1A1A",      # Deep obsidian
        "secondary": "#DC2626",    # Ember red
        "accent": "#EF4444",       # Fire red
        "background": "#0A0505",   # Near black
        "text": "#FFFFFF",
        "text_shadow": "#000000",
        "glow": "#DC2626",
    },
    "volcanic_forge": {
        "name": "Volcanic Forge",
        "primary": "#B91C1C",      # Iron red
        "secondary": "#FFD700",    # Molten gold
        "accent": "#F97316",       # Orange flame
        "background": "#1A0A0A",   # Dark forge
        "text": "#FFFFFF",
        "text_shadow": "#0A0000",
        "glow": "#F97316",
    },
    "celestial_blue": {
        "name": "Celestial Blue",
        "primary": "#60A5FA",      # Sky blue
        "secondary": "#FFFFFF",    # Pure white
        "accent": "#93C5FD",       # Light blue
        "background": "#0A0A1A",   # Night sky
        "text": "#FFFFFF",
        "text_shadow": "#000022",
        "glow": "#60A5FA",
    },
}


# =============================================================================
# TEMPLATE CONFIGURATIONS
# =============================================================================

TEMPLATES = {
    "portal_gateway": {
        "name": "Portal Gateway",
        "description": "Luminous center with dark edges, ideal for spiritual journeys",
        "title_position": "top_center",
        "title_y_ratio": 0.15,
        "subtitle_y_offset": 90,
        "badge_zone": True,
        "vignette_strength": 0.6,
        "center_glow": True,
    },
    "sacred_symbol": {
        "name": "Sacred Symbol",
        "description": "Central glowing symbol with title overlay",
        "title_position": "top_center",
        "title_y_ratio": 0.12,
        "subtitle_y_offset": 85,
        "badge_zone": True,
        "vignette_strength": 0.4,
        "center_glow": True,
    },
    "journey_scene": {
        "name": "Journey Scene",
        "description": "Full-frame scene with text overlay in upper area",
        "title_position": "top_left",
        "title_y_ratio": 0.08,
        "subtitle_y_offset": 70,
        "badge_zone": True,
        "vignette_strength": 0.3,
        "center_glow": False,
    },
    "abstract_energy": {
        "name": "Abstract Energy",
        "description": "Flowing energy patterns with centered title",
        "title_position": "center",
        "title_y_ratio": 0.35,
        "subtitle_y_offset": 100,
        "badge_zone": True,
        "vignette_strength": 0.5,
        "center_glow": True,
    },
    # NEW TEMPLATES from Viral Thumbnail System
    "portal_shockwave": {
        "name": "Portal Shockwave",
        "description": "Right silhouette + center portal (highest CTR systemwide)",
        "title_position": "top_left",
        "title_y_ratio": 0.10,
        "subtitle_y_offset": 80,
        "badge_zone": True,
        "vignette_strength": 0.7,
        "center_glow": True,
        "edge_glow": True,
    },
    "archetype_reveal": {
        "name": "Archetype Reveal",
        "description": "Close-up archetype with dramatic aura",
        "title_position": "top_center",
        "title_y_ratio": 0.08,
        "subtitle_y_offset": 75,
        "badge_zone": True,
        "vignette_strength": 0.5,
        "center_glow": False,
        "edge_glow": True,
    },
    "impossible_landscape": {
        "name": "Impossible Landscape",
        "description": "Jaw-dropping scene, no character needed",
        "title_position": "bottom_center",
        "title_y_ratio": 0.75,
        "subtitle_y_offset": 60,
        "badge_zone": True,
        "vignette_strength": 0.4,
        "center_glow": True,
        "fog": True,
    },
    "viewer_pov": {
        "name": "Viewer POV",
        "description": "Viewer hands/silhouette for immersion",
        "title_position": "top_center",
        "title_y_ratio": 0.12,
        "subtitle_y_offset": 85,
        "badge_zone": True,
        "vignette_strength": 0.6,
        "center_glow": True,
    },
    "transformation_shot": {
        "name": "Transformation Shot",
        "description": "Golden rays, crown/halo effect",
        "title_position": "top_center",
        "title_y_ratio": 0.10,
        "subtitle_y_offset": 80,
        "badge_zone": True,
        "vignette_strength": 0.45,
        "center_glow": True,
        "radiant_glow": True,
    },
    "shadow_confrontation": {
        "name": "Shadow Confrontation",
        "description": "Dark mirror reflection, threshold line",
        "title_position": "top_center",
        "title_y_ratio": 0.10,
        "subtitle_y_offset": 80,
        "badge_zone": True,
        "vignette_strength": 0.75,
        "center_glow": False,
        "edge_glow": True,
        "fog": True,
    },
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert hex color to RGBA tuple."""
    rgb = hex_to_rgb(hex_color)
    return (*rgb, alpha)


def load_manifest(session_path: Path) -> Optional[Dict[str, Any]]:
    """Load session manifest.yaml."""
    manifest_path = session_path / "manifest.yaml"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def find_base_image(session_path: Path) -> Optional[Path]:
    """Find a suitable base image in the session."""
    images_dir = session_path / "images" / "uploaded"
    if images_dir.exists():
        # Valid image extensions
        valid_extensions = {'.png', '.jpg', '.jpeg', '.webp'}

        # Look for thumbnail-specific images first
        for pattern in ["*thumbnail*", "*helm*", "*scene*05*", "*scene*04*", "*main*"]:
            matches = [p for p in images_dir.glob(pattern) if p.suffix.lower() in valid_extensions]
            if matches:
                return sorted(matches)[0]  # Sort for deterministic selection
        # Fall back to any image file
        for ext in ["*.png", "*.jpg", "*.jpeg"]:
            matches = sorted(images_dir.glob(ext))  # Sort for deterministic selection
            if matches:
                return matches[0]
    return None


def get_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a font with fallback to default."""
    font_paths = [
        f"/usr/share/fonts/truetype/dejavu/{font_name}.ttf",
        f"/usr/share/fonts/truetype/liberation/{font_name}.ttf",
        f"/System/Library/Fonts/{font_name}.ttf",
        f"C:/Windows/Fonts/{font_name}.ttf",
    ]

    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    # Try common alternatives
    alternatives = {
        "DejaVuSans-Bold": ["LiberationSans-Bold", "Arial-Bold"],
        "DejaVuSans": ["LiberationSans-Regular", "Arial"],
    }

    for alt in alternatives.get(font_name, []):
        for base in ["/usr/share/fonts/truetype/liberation/", "/System/Library/Fonts/"]:
            alt_path = f"{base}{alt}.ttf"
            if os.path.exists(alt_path):
                return ImageFont.truetype(alt_path, size)

    print(f"Warning: Could not load {font_name}, using default font")
    return ImageFont.load_default()


def get_scaled_font(font_name: str, text: str, max_width: int, max_size: int = 100, min_size: int = 40) -> ImageFont.FreeTypeFont:
    """Get a font scaled to fit text within max_width."""
    # Create a temporary image for measuring
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    for size in range(max_size, min_size - 1, -5):
        font = get_font(font_name, size)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            return font

    # Return minimum size if nothing fits
    return get_font(font_name, min_size)


# =============================================================================
# IMAGE PROCESSING
# =============================================================================

def create_gradient_background(width: int, height: int, palette: Dict) -> Image.Image:
    """Create a gradient background."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    bg_color = hex_to_rgb(palette["background"])
    primary = hex_to_rgb(palette["primary"])

    for y in range(height):
        ratio = y / height
        # Gradient from slightly lighter at top to background at bottom
        r = int(bg_color[0] + (primary[0] - bg_color[0]) * 0.1 * (1 - ratio))
        g = int(bg_color[1] + (primary[1] - bg_color[1]) * 0.1 * (1 - ratio))
        b = int(bg_color[2] + (primary[2] - bg_color[2]) * 0.1 * (1 - ratio))
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    return img


def apply_vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Apply vignette effect (dark edges)."""
    width, height = img.size

    # Create radial gradient mask
    mask = Image.new('L', (width, height), 255)
    mask_draw = ImageDraw.Draw(mask)

    center_x, center_y = width // 2, height // 2
    max_dist = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5

    for y in range(height):
        for x in range(width):
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            ratio = dist / max_dist
            # Apply vignette curve
            value = int(255 * (1 - (ratio ** 1.5) * strength))
            mask.putpixel((x, y), max(0, value))

    # Apply Gaussian blur to smooth the vignette
    mask = mask.filter(ImageFilter.GaussianBlur(radius=50))

    # Create dark overlay
    dark = Image.new('RGB', (width, height), (0, 0, 0))

    # Composite
    result = Image.composite(img, dark, mask)
    return result


def apply_center_glow(img: Image.Image, palette: Dict, intensity: float = 0.3) -> Image.Image:
    """Apply a subtle center glow effect."""
    width, height = img.size
    glow_color = hex_to_rgba(palette["glow"], 100)

    # Create glow layer
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    center_x, center_y = width // 2, int(height * 0.45)  # Slightly above center

    # Draw radial glow
    for radius in range(300, 0, -5):
        alpha = int(glow_color[3] * (radius / 300) * intensity)
        glow_draw.ellipse(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            fill=(*glow_color[:3], alpha)
        )

    # Blur the glow
    glow = glow.filter(ImageFilter.GaussianBlur(radius=30))

    # Composite
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    return Image.alpha_composite(img, glow)


# =============================================================================
# NEW VIRAL MICRO-EFFECTS (from Viral Thumbnail System)
# =============================================================================

def apply_edge_glow(
    img: Image.Image,
    palette: Dict,
    intensity: float = 0.3,
    width_ratio: float = 0.08
) -> Image.Image:
    """
    Apply edge framing glow for mobile visibility.
    Creates a rim light effect around the edges.
    """
    width, height = img.size
    glow_color = hex_to_rgba(palette["glow"], int(150 * intensity))

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Create edge glow layer
    edge_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    # Edge width in pixels
    edge_width = int(width * width_ratio)

    # Draw gradient edges
    for i in range(edge_width):
        alpha = int(glow_color[3] * (1 - i / edge_width) * 0.5)
        color = (*glow_color[:3], alpha)

        # Create temporary layer for this edge level
        temp = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)

        # Top edge
        temp_draw.rectangle([(0, i), (width, i + 1)], fill=color)
        # Bottom edge
        temp_draw.rectangle([(0, height - i - 1), (width, height - i)], fill=color)
        # Left edge
        temp_draw.rectangle([(i, 0), (i + 1, height)], fill=color)
        # Right edge
        temp_draw.rectangle([(width - i - 1, 0), (width - i, height)], fill=color)

        edge_layer = Image.alpha_composite(edge_layer, temp)

    # Blur slightly for smoothness
    edge_layer = edge_layer.filter(ImageFilter.GaussianBlur(radius=5))

    return Image.alpha_composite(img, edge_layer)


def apply_atmospheric_fog(
    img: Image.Image,
    density: float = 0.2,
    color: Tuple[int, int, int] = (200, 200, 220)
) -> Image.Image:
    """
    Apply atmospheric fog effect for cinematic depth.
    Creates a subtle misty overlay at the bottom third.
    """
    width, height = img.size

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Create fog layer
    fog = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)

    # Fog gradient from bottom to middle
    fog_start = int(height * 0.5)  # Start fog at 50% height
    fog_end = height

    for y in range(fog_start, fog_end):
        # Gradient: more fog at bottom
        progress = (y - fog_start) / (fog_end - fog_start)
        alpha = int(255 * density * (progress ** 1.5))  # Exponential curve
        fog_draw.rectangle([(0, y), (width, y + 1)], fill=(*color, alpha))

    # Add some noise/variation to fog
    fog = fog.filter(ImageFilter.GaussianBlur(radius=20))

    return Image.alpha_composite(img, fog)


def apply_radiant_glow(
    img: Image.Image,
    palette: Dict,
    intensity: float = 0.4,
    rays: int = 12
) -> Image.Image:
    """
    Apply radiant light rays effect (for transformation_shot template).
    Creates golden rays emanating from center-top.
    """
    width, height = img.size
    glow_color = hex_to_rgba(palette["primary"], int(100 * intensity))

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Create rays layer
    rays_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    rays_draw = ImageDraw.Draw(rays_layer)

    # Ray origin (center-top)
    origin_x, origin_y = width // 2, int(height * 0.2)

    import math

    # Draw light rays
    for i in range(rays):
        angle = (i / rays) * math.pi  # Spread across 180 degrees
        angle += math.pi / 2  # Start from top

        # Ray endpoint (extended beyond image)
        end_x = origin_x + int(math.cos(angle) * width)
        end_y = origin_y + int(math.sin(angle) * height)

        # Draw multiple lines for ray thickness
        for offset in range(-10, 11, 2):
            alpha = int(glow_color[3] * (1 - abs(offset) / 10))
            rays_draw.line(
                [(origin_x + offset, origin_y), (end_x + offset * 2, end_y)],
                fill=(*glow_color[:3], alpha),
                width=3
            )

    # Heavy blur for soft rays
    rays_layer = rays_layer.filter(ImageFilter.GaussianBlur(radius=30))

    return Image.alpha_composite(img, rays_layer)


def add_sigil_overlay(
    img: Image.Image,
    palette: Dict,
    sigil_type: str = "dreamweaver",
    opacity: float = 0.07,
    position: str = "bottom_left"
) -> Image.Image:
    """
    Add branded sigil for universe continuity.
    Sigil appears at ~7% of thumbnail area, semi-transparent.
    """
    width, height = img.size

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Sigil size (7% of area ≈ 26% of width/height)
    sigil_size = int(min(width, height) * 0.15)

    # Create sigil layer
    sigil_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    sigil_draw = ImageDraw.Draw(sigil_layer)

    # Position coordinates
    if position == "bottom_left":
        x, y = int(width * 0.05), int(height * 0.80)
    elif position == "bottom_right":
        x, y = int(width * 0.80), int(height * 0.80)
    elif position == "top_left":
        x, y = int(width * 0.05), int(height * 0.05)
    else:  # top_right
        x, y = int(width * 0.80), int(height * 0.05)

    # Get glow color with opacity
    glow_color = hex_to_rgba(palette["glow"], int(255 * opacity))

    # Draw a simple geometric sigil (spiral/circle pattern)
    # This is a placeholder - could be replaced with actual sigil image
    import math

    center_x, center_y = x + sigil_size // 2, y + sigil_size // 2

    # Outer circle
    sigil_draw.ellipse(
        [(center_x - sigil_size // 2, center_y - sigil_size // 2),
         (center_x + sigil_size // 2, center_y + sigil_size // 2)],
        outline=glow_color,
        width=2
    )

    # Inner spiral pattern
    for i in range(3):
        r = sigil_size // 2 - (i * sigil_size // 8)
        if r > 5:
            sigil_draw.ellipse(
                [(center_x - r, center_y - r),
                 (center_x + r, center_y + r)],
                outline=(*glow_color[:3], glow_color[3] // (i + 1)),
                width=1
            )

    # Central dot
    dot_r = sigil_size // 10
    sigil_draw.ellipse(
        [(center_x - dot_r, center_y - dot_r),
         (center_x + dot_r, center_y + dot_r)],
        fill=glow_color
    )

    # Blur for glow effect
    sigil_layer = sigil_layer.filter(ImageFilter.GaussianBlur(radius=3))

    return Image.alpha_composite(img, sigil_layer)


def process_base_image(
    img: Image.Image,
    width: int,
    height: int,
    darken: float = 0.7,
    blur: float = 0
) -> Image.Image:
    """Process base image for thumbnail use."""
    # Resize to cover
    img_ratio = img.width / img.height
    target_ratio = width / height

    if img_ratio > target_ratio:
        # Image is wider, fit by height
        new_height = height
        new_width = int(height * img_ratio)
    else:
        # Image is taller, fit by width
        new_width = width
        new_height = int(width / img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center crop
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    img = img.crop((left, top, left + width, top + height))

    # Apply blur if requested
    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))

    # Darken
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(darken)

    return img


# =============================================================================
# TEXT RENDERING
# =============================================================================

def draw_text_with_glow(
    img: Image.Image,
    text: str,
    position: Tuple[int, int],
    font: ImageFont.FreeTypeFont,
    text_color: str,
    glow_color: str,
    glow_radius: int = 8
) -> Image.Image:
    """Draw text with a glow effect."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Create glow layers
    for offset in range(glow_radius, 0, -2):
        glow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        alpha = int(180 * (offset / glow_radius))
        color = hex_to_rgba(glow_color, alpha)

        glow_draw.text(position, text, font=font, fill=color)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=offset))

        img = Image.alpha_composite(img, glow_layer)

    # Draw shadow
    shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_pos = (position[0] + 4, position[1] + 4)
    shadow_draw.text(shadow_pos, text, font=font, fill=(0, 0, 0, 180))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.alpha_composite(img, shadow_layer)

    # Draw main text
    text_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text(position, text, font=font, fill=hex_to_rgba(text_color))
    img = Image.alpha_composite(img, text_layer)

    return img


def draw_badge(
    img: Image.Image,
    text: str,
    position: Tuple[int, int],
    font: ImageFont.FreeTypeFont,
    bg_color: Tuple[int, int, int, int] = (0, 0, 0, 200),
    text_color: str = "#FFFFFF",
    border_color: Optional[str] = None,
    padding: Tuple[int, int] = (20, 10)
) -> Image.Image:
    """Draw a badge with background."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    badge_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge_layer)

    # Calculate text size
    bbox = badge_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Badge rectangle
    x, y = position
    rect_coords = [
        (x - padding[0], y - padding[1]),
        (x + text_width + padding[0], y + text_height + padding[1])
    ]

    # Draw background
    badge_draw.rounded_rectangle(
        rect_coords,
        radius=8,
        fill=bg_color
    )

    # Draw border if specified
    if border_color:
        badge_draw.rounded_rectangle(
            rect_coords,
            radius=8,
            outline=hex_to_rgba(border_color),
            width=2
        )

    # Draw text
    badge_draw.text(position, text, font=font, fill=hex_to_rgba(text_color))

    return Image.alpha_composite(img, badge_layer)


# =============================================================================
# MAIN THUMBNAIL GENERATION
# =============================================================================

def generate_thumbnail(
    session_path: Path,
    template_name: str = "portal_gateway",
    palette_name: str = "sacred_light",
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    base_image_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    duration: Optional[str] = None,
    features: Optional[list] = None,
) -> Path:
    """Generate a YouTube thumbnail for the session."""

    # Dimensions
    width, height = 1280, 720

    # Get template and palette
    template = TEMPLATES.get(template_name, TEMPLATES["portal_gateway"])
    palette = PALETTES.get(palette_name, PALETTES["sacred_light"])

    print("=" * 70)
    print("GENERATING YOUTUBE THUMBNAIL")
    print("=" * 70)
    print(f"Session: {session_path.name}")
    print(f"Template: {template['name']}")
    print(f"Palette: {palette['name']}")

    # Load manifest for metadata
    manifest = load_manifest(session_path)

    # Determine title and subtitle
    if title is None:
        if manifest and "title" in manifest:
            title = manifest["title"].upper()
        else:
            title = session_path.name.replace("-", " ").upper()

    if subtitle is None:
        if manifest and "subtitle" in manifest:
            subtitle = manifest["subtitle"]
        elif manifest and "theme" in manifest:
            subtitle = manifest["theme"]

    # Ensure subtitle is a string (theme can be a dict)
    if subtitle is not None:
        if isinstance(subtitle, dict):
            subtitle = subtitle.get("primary", "") or subtitle.get("name", "") or ""
        else:
            subtitle = str(subtitle) if subtitle else None

    # Determine duration
    if duration is None and manifest:
        if "duration" in manifest:
            dur = manifest["duration"]
            if isinstance(dur, (int, float)):
                minutes = int(dur // 60)
                seconds = int(dur % 60)
                duration = f"{minutes}:{seconds:02d}"
            elif isinstance(dur, dict):
                # Extract target_minutes from duration dict
                target_mins = dur.get("target_minutes", dur.get("minutes", 0))
                if target_mins:
                    duration = f"{int(target_mins)}:00"
            elif dur:
                duration = str(dur)

    # Determine features
    if features is None and manifest:
        features = []
        if "binaural" in manifest:
            bin_cfg = manifest["binaural"]
            if isinstance(bin_cfg, dict) and "base_frequency" in bin_cfg:
                features.append(f"{bin_cfg['base_frequency']}Hz")
        if "brainwave_target" in manifest:
            features.append(manifest["brainwave_target"].capitalize())

    # Find or load base image
    if base_image_path is None:
        base_image_path = find_base_image(session_path)

    # Create base
    if base_image_path and base_image_path.exists():
        print(f"Base image: {base_image_path}")
        base_img = Image.open(base_image_path)
        img = process_base_image(base_img, width, height, darken=0.6)
    else:
        print("No base image found, using gradient background")
        img = create_gradient_background(width, height, palette)

    # Apply vignette
    img = apply_vignette(img, template["vignette_strength"])

    # Apply center glow
    if template.get("center_glow", False):
        img = apply_center_glow(img, palette, intensity=0.25)

    # Apply new viral micro-effects based on template
    if template.get("edge_glow", False):
        img = apply_edge_glow(img, palette, intensity=0.3)

    if template.get("fog", False):
        img = apply_atmospheric_fog(img, density=0.15)

    if template.get("radiant_glow", False):
        img = apply_radiant_glow(img, palette, intensity=0.35)

    # Load fonts with auto-scaling for title
    # Leave 120px margin on each side (60px safe zone * 2)
    max_title_width = width - 120
    title_font = get_scaled_font("DejaVuSans-Bold", title, max_title_width, max_size=100, min_size=50)
    subtitle_font = get_font("DejaVuSans", 42)
    badge_font = get_font("DejaVuSans-Bold", 32)

    # Calculate title position
    img_rgba = img.convert('RGBA')
    temp_draw = ImageDraw.Draw(img_rgba)

    title_bbox = temp_draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]

    title_y = int(height * template["title_y_ratio"])

    if template["title_position"] == "top_center":
        title_x = (width - title_width) // 2
    elif template["title_position"] == "top_left":
        title_x = 60
    elif template["title_position"] == "center":
        title_x = (width - title_width) // 2
    elif template["title_position"] == "bottom_center":
        title_x = (width - title_width) // 2
    else:
        title_x = (width - title_width) // 2

    # Draw title with glow
    img = draw_text_with_glow(
        img_rgba,
        title,
        (title_x, title_y),
        title_font,
        palette["text"],
        palette["glow"],
        glow_radius=10
    )

    # Draw subtitle if present
    if subtitle:
        temp_draw = ImageDraw.Draw(img)
        subtitle_bbox = temp_draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

        subtitle_y = title_y + template["subtitle_y_offset"]

        if template["title_position"] in ["top_center", "center"]:
            subtitle_x = (width - subtitle_width) // 2
        else:
            subtitle_x = 60

        img = draw_text_with_glow(
            img,
            subtitle,
            (subtitle_x, subtitle_y),
            subtitle_font,
            palette["secondary"],
            palette["glow"],
            glow_radius=6
        )

    # Draw badges
    if template["badge_zone"]:
        # Duration badge (bottom right)
        if duration:
            duration_x = width - 150
            duration_y = height - 70
            img = draw_badge(
                img,
                duration,
                (duration_x, duration_y),
                badge_font,
                bg_color=(0, 0, 0, 220),
                text_color="#FFFFFF",
                border_color=palette["primary"]
            )

        # Feature badge (bottom left)
        if features:
            feature_text = " • ".join(features[:2])  # Limit to 2 features
            img = draw_badge(
                img,
                feature_text,
                (50, height - 70),
                badge_font,
                bg_color=hex_to_rgba(palette["primary"], 230),
                text_color="#FFFFFF",
            )

    # Determine output path
    if output_path is None:
        output_dir = session_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "youtube_thumbnail.png"

    # Save
    img = img.convert('RGB')
    img.save(output_path, 'PNG', optimize=True)

    # Also save to youtube_package if it exists
    youtube_package_dir = session_path / "output" / "youtube_package"
    if youtube_package_dir.exists():
        package_thumbnail = youtube_package_dir / "thumbnail.png"
        img.save(package_thumbnail, 'PNG', optimize=True)
        print(f"Also saved to: {package_thumbnail}")

    print()
    print("✓ THUMBNAIL GENERATED")
    print(f"  Output: {output_path}")
    print(f"  Size: 1280x720 (16:9)")
    print(f"  Title: {title}")
    if subtitle:
        print(f"  Subtitle: {subtitle}")
    if duration:
        print(f"  Duration: {duration}")
    if features:
        print(f"  Features: {', '.join(features)}")
    print("=" * 70)

    return output_path


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube thumbnail for Sacred Digital Dreamweaver session",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Templates:
  portal_gateway   - Luminous center with dark edges (default)
  sacred_symbol    - Central glowing symbol focus
  journey_scene    - Full-frame scene with text overlay
  abstract_energy  - Flowing energy patterns

Palettes:
  sacred_light     - Gold/cream on cosmic dark (default)
  cosmic_journey   - Purple/blue on deep space
  garden_eden      - Emerald/gold on forest shadow
  ancient_temple   - Antique gold on temple shadow
  neural_network   - Cyan/purple on digital void

Examples:
  python3 generate_thumbnail.py sessions/garden-of-eden/
  python3 generate_thumbnail.py sessions/neural-network/ --template abstract_energy --palette neural_network
  python3 generate_thumbnail.py sessions/atlas/ --title "ATLAS" --subtitle "Journey to the Stars"
        """
    )

    parser.add_argument("session_path", type=Path, help="Path to session directory")
    parser.add_argument("--template", "-t",
                        choices=list(TEMPLATES.keys()),
                        default="portal_gateway",
                        help="Thumbnail template style")
    parser.add_argument("--palette", "-p",
                        choices=list(PALETTES.keys()),
                        default="sacred_light",
                        help="Color palette")
    parser.add_argument("--title", help="Override title text")
    parser.add_argument("--subtitle", help="Override subtitle text")
    parser.add_argument("--base-image", "-i", type=Path, help="Path to base image")
    parser.add_argument("--output", "-o", type=Path, help="Output path")
    parser.add_argument("--duration", "-d", help="Duration string (e.g., '25:30')")
    parser.add_argument("--features", "-f", nargs="+", help="Feature badges (e.g., '432Hz' 'Theta')")

    args = parser.parse_args()

    if not args.session_path.exists():
        print(f"ERROR: Session path does not exist: {args.session_path}")
        sys.exit(1)

    generate_thumbnail(
        session_path=args.session_path,
        template_name=args.template,
        palette_name=args.palette,
        title=args.title,
        subtitle=args.subtitle,
        base_image_path=args.base_image,
        output_path=args.output,
        duration=args.duration,
        features=args.features,
    )


if __name__ == "__main__":
    main()
