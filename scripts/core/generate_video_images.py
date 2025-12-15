#!/usr/bin/env python3
"""
Video Image Generator for Sacred Digital Dreamweaver

Extends thumbnail generation to produce all video imagery:
- Title cards (intro screens)
- Section slides (chapter transitions)
- Outro screens (end cards with CTAs)
- Lower thirds (name/info overlays)
- Chapter markers (section dividers)
- Social previews (square format for Instagram/social)
- Scene backgrounds (base images for video assembly)

Uses the same palette and template system as thumbnail generation for
brand consistency across all session imagery.

Usage:
    # Generate all images for a session
    python3 scripts/core/generate_video_images.py sessions/{session}/ --all

    # Generate specific image types
    python3 scripts/core/generate_video_images.py sessions/{session}/ --title-card
    python3 scripts/core/generate_video_images.py sessions/{session}/ --section-slides
    python3 scripts/core/generate_video_images.py sessions/{session}/ --outro

    # With custom options
    python3 scripts/core/generate_video_images.py sessions/{session}/ \\
        --all --palette cosmic_journey --base-image custom.png

Dependencies:
    pip install Pillow pyyaml

Author: Sacred Digital Dreamweaver AI Creative OS
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum
import yaml
import logging

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
except ImportError:
    print("ERROR: Pillow library required. Install with: pip install Pillow")
    sys.exit(1)


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# =============================================================================
# IMAGE TYPE SPECIFICATIONS
# =============================================================================

class ImageType(Enum):
    """Supported video image types with their specifications."""
    THUMBNAIL = "thumbnail"
    TITLE_CARD = "title_card"
    SECTION_SLIDE = "section_slide"
    OUTRO = "outro"
    LOWER_THIRD = "lower_third"
    CHAPTER_MARKER = "chapter_marker"
    SOCIAL_PREVIEW = "social_preview"
    SCENE_BACKGROUND = "scene_background"


@dataclass
class ImageSpec:
    """Specification for an image type."""
    width: int
    height: int
    title_font_size: int
    subtitle_font_size: int
    title_y_ratio: float
    include_badges: bool
    include_branding: bool
    vignette_strength: float
    output_format: str = "PNG"


# Image specifications for each type
IMAGE_SPECS = {
    ImageType.THUMBNAIL: ImageSpec(
        width=1280, height=720,
        title_font_size=100, subtitle_font_size=42,
        title_y_ratio=0.15, include_badges=True, include_branding=True,
        vignette_strength=0.6
    ),
    ImageType.TITLE_CARD: ImageSpec(
        width=1920, height=1080,
        title_font_size=140, subtitle_font_size=56,
        title_y_ratio=0.35, include_badges=False, include_branding=True,
        vignette_strength=0.5
    ),
    ImageType.SECTION_SLIDE: ImageSpec(
        width=1920, height=1080,
        title_font_size=120, subtitle_font_size=48,
        title_y_ratio=0.40, include_badges=True, include_branding=False,
        vignette_strength=0.4
    ),
    ImageType.OUTRO: ImageSpec(
        width=1920, height=1080,
        title_font_size=100, subtitle_font_size=40,
        title_y_ratio=0.25, include_badges=False, include_branding=True,
        vignette_strength=0.5
    ),
    ImageType.LOWER_THIRD: ImageSpec(
        width=1920, height=1080,
        title_font_size=48, subtitle_font_size=32,
        title_y_ratio=0.75, include_badges=False, include_branding=False,
        vignette_strength=0.0, output_format="PNG"  # Needs alpha for overlay
    ),
    ImageType.CHAPTER_MARKER: ImageSpec(
        width=1920, height=1080,
        title_font_size=100, subtitle_font_size=44,
        title_y_ratio=0.42, include_badges=True, include_branding=False,
        vignette_strength=0.45
    ),
    ImageType.SOCIAL_PREVIEW: ImageSpec(
        width=1080, height=1080,
        title_font_size=80, subtitle_font_size=36,
        title_y_ratio=0.40, include_badges=True, include_branding=True,
        vignette_strength=0.5
    ),
    ImageType.SCENE_BACKGROUND: ImageSpec(
        width=1920, height=1080,
        title_font_size=0, subtitle_font_size=0,  # No text
        title_y_ratio=0, include_badges=False, include_branding=False,
        vignette_strength=0.3
    ),
}


# =============================================================================
# COLOR PALETTES (Shared with thumbnail generator)
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
    "volcanic_forge": {
        "name": "Volcanic Forge",
        "primary": "#FF4500",      # Molten orange-red
        "secondary": "#FFD700",    # Forge gold
        "accent": "#FF6347",       # Fire glow
        "background": "#1A0A0A",   # Volcanic shadow
        "text": "#FFFFFF",
        "text_shadow": "#0A0505",
        "glow": "#FF4500",
    },
    "celestial_blue": {
        "name": "Celestial Blue",
        "primary": "#4169E1",      # Royal blue
        "secondary": "#87CEEB",    # Sky blue
        "accent": "#E6E6FA",       # Lavender mist
        "background": "#0A0A1F",   # Night sky
        "text": "#FFFFFF",
        "text_shadow": "#050510",
        "glow": "#4169E1",
    },
}


# =============================================================================
# LAYOUT TEMPLATES
# =============================================================================

TEMPLATES = {
    "centered": {
        "name": "Centered",
        "title_position": "center",
        "center_glow": True,
        "subtitle_y_offset": 100,
    },
    "top_center": {
        "name": "Top Center",
        "title_position": "top_center",
        "center_glow": True,
        "subtitle_y_offset": 90,
    },
    "bottom_left": {
        "name": "Bottom Left",
        "title_position": "bottom_left",
        "center_glow": False,
        "subtitle_y_offset": 50,
    },
    "lower_third_bar": {
        "name": "Lower Third Bar",
        "title_position": "lower_third",
        "center_glow": False,
        "subtitle_y_offset": 40,
    },
    "full_frame": {
        "name": "Full Frame",
        "title_position": "center",
        "center_glow": True,
        "subtitle_y_offset": 80,
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


def find_base_image(session_path: Path, prefer_pattern: str = None) -> Optional[Path]:
    """Find a suitable base image in the session."""
    images_dir = session_path / "images" / "uploaded"
    if not images_dir.exists():
        return None

    # Priority patterns
    patterns = []
    if prefer_pattern:
        patterns.append(prefer_pattern)
    patterns.extend(["*thumbnail*", "*helm*", "*scene*05*", "*main*", "*title*"])

    for pattern in patterns:
        matches = list(images_dir.glob(pattern))
        if matches:
            return matches[0]

    # Fall back to any PNG/JPG
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        matches = sorted(images_dir.glob(ext))
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

    logger.warning(f"Could not load {font_name}, using default font")
    return ImageFont.load_default()


def format_duration(seconds: int) -> str:
    """Format seconds into MM:SS string."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


# =============================================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================================

def create_gradient_background(
    width: int,
    height: int,
    palette: Dict,
    style: str = "radial"
) -> Image.Image:
    """Create a gradient background."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    bg_color = hex_to_rgb(palette["background"])
    primary = hex_to_rgb(palette["primary"])

    if style == "radial":
        # Radial gradient from center
        center_x, center_y = width // 2, height // 2
        max_dist = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5

        for y in range(height):
            for x in range(width):
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                ratio = min(dist / max_dist, 1.0)
                r = int(primary[0] * 0.2 * (1 - ratio) + bg_color[0] * ratio)
                g = int(primary[1] * 0.2 * (1 - ratio) + bg_color[1] * ratio)
                b = int(primary[2] * 0.2 * (1 - ratio) + bg_color[2] * ratio)
                img.putpixel((x, y), (r, g, b))
    else:
        # Vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(bg_color[0] + (primary[0] - bg_color[0]) * 0.1 * (1 - ratio))
            g = int(bg_color[1] + (primary[1] - bg_color[1]) * 0.1 * (1 - ratio))
            b = int(bg_color[2] + (primary[2] - bg_color[2]) * 0.1 * (1 - ratio))
            draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    return img


def apply_vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Apply vignette effect (dark edges)."""
    if strength <= 0:
        return img

    width, height = img.size

    # Create radial gradient mask
    mask = Image.new('L', (width, height), 255)

    center_x, center_y = width // 2, height // 2
    max_dist = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5

    for y in range(height):
        for x in range(width):
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            ratio = dist / max_dist
            value = int(255 * (1 - (ratio ** 1.5) * strength))
            mask.putpixel((x, y), max(0, value))

    # Apply Gaussian blur to smooth the vignette
    mask = mask.filter(ImageFilter.GaussianBlur(radius=50))

    # Create dark overlay
    dark = Image.new('RGB', (width, height), (0, 0, 0))

    # Composite
    result = Image.composite(img, dark, mask)
    return result


def apply_center_glow(
    img: Image.Image,
    palette: Dict,
    intensity: float = 0.3,
    y_offset: float = 0.0
) -> Image.Image:
    """Apply a subtle center glow effect."""
    width, height = img.size
    glow_color = hex_to_rgba(palette["glow"], 100)

    # Create glow layer
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    center_x = width // 2
    center_y = int(height * (0.45 + y_offset))

    # Draw radial glow
    max_radius = min(width, height) // 2
    for radius in range(max_radius, 0, -5):
        alpha = int(glow_color[3] * (radius / max_radius) * intensity)
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


def process_base_image(
    img: Image.Image,
    width: int,
    height: int,
    darken: float = 0.7,
    blur: float = 0
) -> Image.Image:
    """Process base image for use as background."""
    # Resize to cover
    img_ratio = img.width / img.height
    target_ratio = width / height

    if img_ratio > target_ratio:
        new_height = height
        new_width = int(height * img_ratio)
    else:
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
# TEXT RENDERING FUNCTIONS
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


def draw_lower_third_bar(
    img: Image.Image,
    title: str,
    subtitle: str,
    palette: Dict,
    spec: ImageSpec
) -> Image.Image:
    """Draw a lower third bar overlay."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    width, height = img.size
    bar_height = 120
    bar_y = int(height * 0.75)

    # Create bar layer
    bar_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    bar_draw = ImageDraw.Draw(bar_layer)

    # Draw semi-transparent bar
    primary_rgba = hex_to_rgba(palette["primary"], 200)
    bar_draw.rectangle(
        [(0, bar_y), (width, bar_y + bar_height)],
        fill=(0, 0, 0, 180)
    )

    # Accent line
    bar_draw.rectangle(
        [(0, bar_y), (8, bar_y + bar_height)],
        fill=primary_rgba
    )

    # Title
    title_font = get_font("DejaVuSans-Bold", spec.title_font_size)
    bar_draw.text(
        (40, bar_y + 20),
        title,
        font=title_font,
        fill=hex_to_rgba(palette["text"])
    )

    # Subtitle
    if subtitle:
        subtitle_font = get_font("DejaVuSans", spec.subtitle_font_size)
        bar_draw.text(
            (40, bar_y + 65),
            subtitle,
            font=subtitle_font,
            fill=hex_to_rgba(palette["secondary"])
        )

    return Image.alpha_composite(img, bar_layer)


def draw_branding(
    img: Image.Image,
    palette: Dict,
    position: str = "bottom_right"
) -> Image.Image:
    """Add subtle branding watermark."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    width, height = img.size
    brand_text = "Sacred Digital Dreamweaver"

    brand_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    brand_draw = ImageDraw.Draw(brand_layer)

    font = get_font("DejaVuSans", 20)
    bbox = brand_draw.textbbox((0, 0), brand_text, font=font)
    text_width = bbox[2] - bbox[0]

    if position == "bottom_right":
        x = width - text_width - 30
        y = height - 40
    elif position == "bottom_left":
        x = 30
        y = height - 40
    else:
        x = (width - text_width) // 2
        y = height - 40

    # Draw with low opacity
    brand_draw.text(
        (x, y),
        brand_text,
        font=font,
        fill=hex_to_rgba(palette["text"], 100)
    )

    return Image.alpha_composite(img, brand_layer)


# =============================================================================
# IMAGE GENERATORS
# =============================================================================

def generate_title_card(
    session_path: Path,
    palette: Dict,
    spec: ImageSpec,
    title: str,
    subtitle: Optional[str] = None,
    base_image_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> Path:
    """Generate a title card (intro screen)."""
    width, height = spec.width, spec.height

    # Load or create base
    if base_image_path and base_image_path.exists():
        base_img = Image.open(base_image_path)
        img = process_base_image(base_img, width, height, darken=0.5, blur=2)
    else:
        base_image_path = find_base_image(session_path, "*title*")
        if base_image_path:
            base_img = Image.open(base_image_path)
            img = process_base_image(base_img, width, height, darken=0.5, blur=2)
        else:
            img = create_gradient_background(width, height, palette, "radial")

    # Apply effects
    img = apply_vignette(img, spec.vignette_strength)
    img = apply_center_glow(img, palette, intensity=0.35)

    # Draw title
    title_font = get_font("DejaVuSans-Bold", spec.title_font_size)
    subtitle_font = get_font("DejaVuSans", spec.subtitle_font_size)

    # Calculate positions
    img_rgba = img.convert('RGBA')
    temp_draw = ImageDraw.Draw(img_rgba)

    title_bbox = temp_draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = int(height * spec.title_y_ratio)

    img = draw_text_with_glow(
        img_rgba, title, (title_x, title_y),
        title_font, palette["text"], palette["glow"], glow_radius=12
    )

    # Draw subtitle
    if subtitle:
        subtitle_bbox = temp_draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + TEMPLATES["centered"]["subtitle_y_offset"]

        img = draw_text_with_glow(
            img, subtitle, (subtitle_x, subtitle_y),
            subtitle_font, palette["secondary"], palette["glow"], glow_radius=6
        )

    # Add branding
    if spec.include_branding:
        img = draw_branding(img, palette, "bottom_right")

    # Save
    if output_path is None:
        output_dir = session_path / "output" / "video_images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "title_card.png"

    img = img.convert('RGB')
    img.save(output_path, spec.output_format, optimize=True)

    logger.info(f"Generated title card: {output_path}")
    return output_path


def generate_section_slide(
    session_path: Path,
    palette: Dict,
    spec: ImageSpec,
    section_name: str,
    section_number: int,
    total_sections: int,
    description: Optional[str] = None,
    duration: Optional[str] = None,
    base_image_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> Path:
    """Generate a section/chapter slide."""
    width, height = spec.width, spec.height

    # Load or create base
    if base_image_path and base_image_path.exists():
        base_img = Image.open(base_image_path)
        img = process_base_image(base_img, width, height, darken=0.6)
    else:
        img = create_gradient_background(width, height, palette, "radial")

    # Apply effects
    img = apply_vignette(img, spec.vignette_strength)
    img = apply_center_glow(img, palette, intensity=0.25, y_offset=-0.05)

    # Section number badge
    badge_font = get_font("DejaVuSans-Bold", 36)
    section_label = f"SECTION {section_number} OF {total_sections}"

    img_rgba = img.convert('RGBA')
    img = draw_badge(
        img_rgba, section_label, (60, 60),
        badge_font, hex_to_rgba(palette["primary"], 220),
        "#FFFFFF", None, (25, 15)
    )

    # Section title
    title_font = get_font("DejaVuSans-Bold", spec.title_font_size)
    temp_draw = ImageDraw.Draw(img)

    title_bbox = temp_draw.textbbox((0, 0), section_name.upper(), font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = int(height * spec.title_y_ratio)

    img = draw_text_with_glow(
        img, section_name.upper(), (title_x, title_y),
        title_font, palette["text"], palette["glow"], glow_radius=10
    )

    # Description
    if description:
        subtitle_font = get_font("DejaVuSans", spec.subtitle_font_size)
        desc_bbox = temp_draw.textbbox((0, 0), description, font=subtitle_font)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = (width - desc_width) // 2
        desc_y = title_y + TEMPLATES["centered"]["subtitle_y_offset"]

        img = draw_text_with_glow(
            img, description, (desc_x, desc_y),
            subtitle_font, palette["secondary"], palette["glow"], glow_radius=5
        )

    # Duration badge
    if duration and spec.include_badges:
        badge_font_small = get_font("DejaVuSans-Bold", 28)
        img = draw_badge(
            img, duration, (width - 150, height - 70),
            badge_font_small, (0, 0, 0, 220),
            "#FFFFFF", palette["primary"], (20, 10)
        )

    # Save
    if output_path is None:
        output_dir = session_path / "output" / "video_images" / "sections"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"section_{section_number:02d}_{section_name.lower().replace(' ', '_')}.png"

    img = img.convert('RGB')
    img.save(output_path, spec.output_format, optimize=True)

    logger.info(f"Generated section slide: {output_path}")
    return output_path


def generate_outro(
    session_path: Path,
    palette: Dict,
    spec: ImageSpec,
    title: str,
    cta_text: str = "Subscribe for More Journeys",
    secondary_cta: str = "Like & Comment",
    base_image_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> Path:
    """Generate an outro/end screen."""
    width, height = spec.width, spec.height

    # Load or create base
    if base_image_path and base_image_path.exists():
        base_img = Image.open(base_image_path)
        img = process_base_image(base_img, width, height, darken=0.5, blur=3)
    else:
        img = create_gradient_background(width, height, palette, "radial")

    # Apply effects
    img = apply_vignette(img, spec.vignette_strength)
    img = apply_center_glow(img, palette, intensity=0.3)

    img_rgba = img.convert('RGBA')

    # "Thank You" or session title
    title_font = get_font("DejaVuSans-Bold", spec.title_font_size)
    temp_draw = ImageDraw.Draw(img_rgba)

    title_text = f"Thank You for Journeying"
    title_bbox = temp_draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = int(height * 0.20)

    img = draw_text_with_glow(
        img_rgba, title_text, (title_x, title_y),
        title_font, palette["text"], palette["glow"], glow_radius=10
    )

    # Session title as subtitle
    subtitle_font = get_font("DejaVuSans", spec.subtitle_font_size)
    subtitle_bbox = temp_draw.textbbox((0, 0), title, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + 100

    img = draw_text_with_glow(
        img, title, (subtitle_x, subtitle_y),
        subtitle_font, palette["secondary"], palette["glow"], glow_radius=5
    )

    # CTA buttons zone (for YouTube end screen)
    # Left box: Subscribe
    box_y = int(height * 0.55)
    box_width = 400
    box_height = 180

    # Draw placeholder boxes for YouTube end screen elements
    cta_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    cta_draw = ImageDraw.Draw(cta_layer)

    # Subscribe box area (left)
    left_box_x = width // 4 - box_width // 2
    cta_draw.rounded_rectangle(
        [(left_box_x, box_y), (left_box_x + box_width, box_y + box_height)],
        radius=12,
        outline=hex_to_rgba(palette["primary"], 150),
        width=3
    )

    # Video recommendation box (right)
    right_box_x = 3 * width // 4 - box_width // 2
    cta_draw.rounded_rectangle(
        [(right_box_x, box_y), (right_box_x + box_width, box_y + box_height)],
        radius=12,
        outline=hex_to_rgba(palette["primary"], 150),
        width=3
    )

    img = Image.alpha_composite(img, cta_layer)

    # CTA text below boxes
    cta_font = get_font("DejaVuSans-Bold", 36)
    cta_bbox = temp_draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_width = cta_bbox[2] - cta_bbox[0]
    cta_x = (width - cta_width) // 2
    cta_y = box_y + box_height + 40

    img = draw_text_with_glow(
        img, cta_text, (cta_x, cta_y),
        cta_font, palette["primary"], palette["glow"], glow_radius=6
    )

    # Secondary CTA
    secondary_font = get_font("DejaVuSans", 28)
    secondary_bbox = temp_draw.textbbox((0, 0), secondary_cta, font=secondary_font)
    secondary_width = secondary_bbox[2] - secondary_bbox[0]
    secondary_x = (width - secondary_width) // 2
    secondary_y = cta_y + 60

    text_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text(
        (secondary_x, secondary_y),
        secondary_cta,
        font=secondary_font,
        fill=hex_to_rgba(palette["text"], 180)
    )
    img = Image.alpha_composite(img, text_layer)

    # Branding
    if spec.include_branding:
        img = draw_branding(img, palette, "bottom_center")

    # Save
    if output_path is None:
        output_dir = session_path / "output" / "video_images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "outro.png"

    img = img.convert('RGB')
    img.save(output_path, spec.output_format, optimize=True)

    logger.info(f"Generated outro: {output_path}")
    return output_path


def generate_lower_third(
    session_path: Path,
    palette: Dict,
    spec: ImageSpec,
    name: str,
    description: str = "",
    output_path: Optional[Path] = None
) -> Path:
    """Generate a lower third overlay (transparent PNG)."""
    width, height = spec.width, spec.height

    # Create transparent base
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    # Draw lower third bar
    img = draw_lower_third_bar(img, name, description, palette, spec)

    # Save as PNG with transparency
    if output_path is None:
        output_dir = session_path / "output" / "video_images" / "lower_thirds"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = name.lower().replace(' ', '_').replace('/', '_')[:30]
        output_path = output_dir / f"lower_third_{safe_name}.png"

    img.save(output_path, 'PNG')

    logger.info(f"Generated lower third: {output_path}")
    return output_path


def generate_chapter_marker(
    session_path: Path,
    palette: Dict,
    spec: ImageSpec,
    chapter_name: str,
    chapter_number: int,
    timestamp: str,
    base_image_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> Path:
    """Generate a chapter marker image."""
    width, height = spec.width, spec.height

    # Load or create base
    if base_image_path and base_image_path.exists():
        base_img = Image.open(base_image_path)
        img = process_base_image(base_img, width, height, darken=0.65)
    else:
        img = create_gradient_background(width, height, palette, "radial")

    # Apply effects
    img = apply_vignette(img, spec.vignette_strength)
    img = apply_center_glow(img, palette, intensity=0.2)

    img_rgba = img.convert('RGBA')

    # Chapter number circle
    circle_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    circle_draw = ImageDraw.Draw(circle_layer)

    circle_x = width // 2
    circle_y = int(height * 0.35)
    circle_radius = 80

    # Glowing circle
    for r in range(circle_radius + 20, circle_radius, -2):
        alpha = int(100 * ((circle_radius + 20 - r) / 20))
        circle_draw.ellipse(
            [(circle_x - r, circle_y - r), (circle_x + r, circle_y + r)],
            fill=hex_to_rgba(palette["glow"], alpha)
        )

    circle_draw.ellipse(
        [(circle_x - circle_radius, circle_y - circle_radius),
         (circle_x + circle_radius, circle_y + circle_radius)],
        fill=hex_to_rgba(palette["primary"], 230)
    )

    # Chapter number in circle
    number_font = get_font("DejaVuSans-Bold", 72)
    number_text = str(chapter_number)
    number_bbox = circle_draw.textbbox((0, 0), number_text, font=number_font)
    number_width = number_bbox[2] - number_bbox[0]
    number_height = number_bbox[3] - number_bbox[1]
    number_x = circle_x - number_width // 2
    number_y = circle_y - number_height // 2 - 5

    circle_draw.text(
        (number_x, number_y),
        number_text,
        font=number_font,
        fill=hex_to_rgba("#FFFFFF")
    )

    img = Image.alpha_composite(img_rgba, circle_layer)

    # Chapter name
    title_font = get_font("DejaVuSans-Bold", spec.title_font_size)
    temp_draw = ImageDraw.Draw(img)

    title_bbox = temp_draw.textbbox((0, 0), chapter_name.upper(), font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = int(height * 0.55)

    img = draw_text_with_glow(
        img, chapter_name.upper(), (title_x, title_y),
        title_font, palette["text"], palette["glow"], glow_radius=8
    )

    # Timestamp badge
    if spec.include_badges:
        badge_font = get_font("DejaVuSans-Bold", 32)
        timestamp_x = (width - 100) // 2
        timestamp_y = int(height * 0.70)

        img = draw_badge(
            img, timestamp, (timestamp_x, timestamp_y),
            badge_font, (0, 0, 0, 200),
            "#FFFFFF", palette["primary"], (25, 12)
        )

    # Save
    if output_path is None:
        output_dir = session_path / "output" / "video_images" / "chapters"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = chapter_name.lower().replace(' ', '_')[:30]
        output_path = output_dir / f"chapter_{chapter_number:02d}_{safe_name}.png"

    img = img.convert('RGB')
    img.save(output_path, spec.output_format, optimize=True)

    logger.info(f"Generated chapter marker: {output_path}")
    return output_path


def generate_social_preview(
    session_path: Path,
    palette: Dict,
    spec: ImageSpec,
    title: str,
    subtitle: Optional[str] = None,
    features: Optional[List[str]] = None,
    base_image_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> Path:
    """Generate a square social media preview image."""
    width, height = spec.width, spec.height  # 1080x1080

    # Load or create base
    if base_image_path and base_image_path.exists():
        base_img = Image.open(base_image_path)
        img = process_base_image(base_img, width, height, darken=0.55)
    else:
        base_image_path = find_base_image(session_path)
        if base_image_path:
            base_img = Image.open(base_image_path)
            img = process_base_image(base_img, width, height, darken=0.55)
        else:
            img = create_gradient_background(width, height, palette, "radial")

    # Apply effects
    img = apply_vignette(img, spec.vignette_strength)
    img = apply_center_glow(img, palette, intensity=0.3)

    # Title
    title_font = get_font("DejaVuSans-Bold", spec.title_font_size)
    img_rgba = img.convert('RGBA')
    temp_draw = ImageDraw.Draw(img_rgba)

    # Word wrap title for square format
    words = title.upper().split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = temp_draw.textbbox((0, 0), test_line, font=title_font)
        if bbox[2] - bbox[0] > width - 100:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    title_y = int(height * spec.title_y_ratio)
    line_height = spec.title_font_size + 20

    for i, line in enumerate(lines):
        line_bbox = temp_draw.textbbox((0, 0), line, font=title_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        line_y = title_y + i * line_height

        img_rgba = draw_text_with_glow(
            img_rgba, line, (line_x, line_y),
            title_font, palette["text"], palette["glow"], glow_radius=10
        )

    img = img_rgba

    # Subtitle
    if subtitle:
        subtitle_font = get_font("DejaVuSans", spec.subtitle_font_size)
        subtitle_bbox = temp_draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + len(lines) * line_height + 30

        img = draw_text_with_glow(
            img, subtitle, (subtitle_x, subtitle_y),
            subtitle_font, palette["secondary"], palette["glow"], glow_radius=5
        )

    # Feature badges at bottom
    if features and spec.include_badges:
        badge_font = get_font("DejaVuSans-Bold", 28)
        feature_text = " • ".join(features[:3])
        badge_bbox = temp_draw.textbbox((0, 0), feature_text, font=badge_font)
        badge_width = badge_bbox[2] - badge_bbox[0]
        badge_x = (width - badge_width) // 2 - 20
        badge_y = height - 100

        img = draw_badge(
            img, feature_text, (badge_x, badge_y),
            badge_font, hex_to_rgba(palette["primary"], 220),
            "#FFFFFF", None, (25, 12)
        )

    # Branding
    if spec.include_branding:
        img = draw_branding(img, palette, "bottom_center")

    # Save
    if output_path is None:
        output_dir = session_path / "output" / "video_images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "social_preview.png"

    img = img.convert('RGB')
    img.save(output_path, spec.output_format, optimize=True)

    logger.info(f"Generated social preview: {output_path}")
    return output_path


def generate_scene_background(
    session_path: Path,
    palette: Dict,
    spec: ImageSpec,
    scene_number: int,
    base_image_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> Path:
    """Generate a scene background (no text, for video composition).

    Each scene gets a unique variation through:
    - Different gradient center positions
    - Varied color intensities
    - Different glow positions and intensities
    - Subtle noise patterns for texture
    """
    import random
    import math

    width, height = spec.width, spec.height

    # Seed randomness with scene_number for reproducibility but variation
    random.seed(scene_number * 42 + hash(str(session_path.name)))

    # Load or create base
    if base_image_path and base_image_path.exists():
        base_img = Image.open(base_image_path)
        img = process_base_image(base_img, width, height, darken=0.8)
    else:
        # Create varied gradient per scene
        img = _create_varied_gradient(width, height, palette, scene_number)

    # Apply effects with scene-based variation
    vignette_strength = spec.vignette_strength * (0.8 + random.random() * 0.4)  # ±20%
    img = apply_vignette(img, vignette_strength)

    # Vary glow intensity and position per scene
    glow_intensity = 0.10 + (scene_number % 5) * 0.03  # 0.10 to 0.22
    img = _apply_varied_glow(img, palette, scene_number, intensity=glow_intensity)

    # Add subtle noise/grain for texture (varies per scene)
    img = _add_subtle_noise(img, intensity=0.02 + (scene_number % 3) * 0.01)

    # Save
    if output_path is None:
        output_dir = session_path / "output" / "video_images" / "backgrounds"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"scene_{scene_number:02d}_background.png"

    img = img.convert('RGB')
    img.save(output_path, spec.output_format, optimize=True)

    logger.info(f"Generated scene background {scene_number}: {output_path}")
    return output_path


def _create_varied_gradient(width: int, height: int, palette: Dict, scene_number: int) -> Image.Image:
    """Create a gradient with scene-based variation in center position and colors."""
    import random
    import math

    img = Image.new('RGB', (width, height))

    bg_color = hex_to_rgb(palette["background"])
    primary = hex_to_rgb(palette["primary"])
    secondary = hex_to_rgb(palette.get("secondary", palette["primary"]))

    # Vary gradient center position based on scene (creates visual variety)
    # Scene 1: center, Scene 2: upper-left, Scene 3: upper-right, etc.
    center_offsets = [
        (0.5, 0.5),    # Scene 1: center
        (0.35, 0.4),   # Scene 2: upper-left
        (0.65, 0.4),   # Scene 3: upper-right
        (0.4, 0.6),    # Scene 4: lower-left
        (0.6, 0.55),   # Scene 5: lower-right
        (0.5, 0.35),   # Scene 6: upper-center
        (0.45, 0.65),  # Scene 7: lower-center
    ]
    offset_idx = (scene_number - 1) % len(center_offsets)
    cx_ratio, cy_ratio = center_offsets[offset_idx]
    center_x = int(width * cx_ratio)
    center_y = int(height * cy_ratio)

    # Vary color blend between primary and secondary based on scene
    color_blend = (scene_number % 3) / 3.0  # 0, 0.33, or 0.66
    mixed_primary = tuple(
        int(primary[i] * (1 - color_blend) + secondary[i] * color_blend)
        for i in range(3)
    )

    # Vary intensity based on scene
    intensity_factor = 0.15 + (scene_number % 5) * 0.03  # 0.15 to 0.27

    max_dist = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5

    for y in range(height):
        for x in range(width):
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            ratio = min(dist / max_dist, 1.0)
            r = int(mixed_primary[0] * intensity_factor * (1 - ratio) + bg_color[0] * ratio)
            g = int(mixed_primary[1] * intensity_factor * (1 - ratio) + bg_color[1] * ratio)
            b = int(mixed_primary[2] * intensity_factor * (1 - ratio) + bg_color[2] * ratio)
            img.putpixel((x, y), (r, g, b))

    return img


def _apply_varied_glow(img: Image.Image, palette: Dict, scene_number: int, intensity: float = 0.15) -> Image.Image:
    """Apply center glow with scene-based position variation."""
    width, height = img.size
    glow_color = hex_to_rgba(palette.get("glow", palette["primary"]), 100)

    # Vary glow position per scene
    glow_offsets = [
        (0.5, 0.45),   # Center-upper
        (0.4, 0.5),    # Left-center
        (0.6, 0.5),    # Right-center
        (0.5, 0.55),   # Center-lower
        (0.45, 0.4),   # Upper-left
    ]
    offset_idx = (scene_number - 1) % len(glow_offsets)
    gx_ratio, gy_ratio = glow_offsets[offset_idx]

    center_x = int(width * gx_ratio)
    center_y = int(height * gy_ratio)

    # Create glow layer
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Draw radial glow with varied radius
    max_radius = 250 + (scene_number % 4) * 30  # 250 to 340
    for radius in range(max_radius, 0, -5):
        alpha = int(glow_color[3] * (radius / max_radius) * intensity)
        glow_draw.ellipse(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            fill=(*glow_color[:3], alpha)
        )

    # Blur the glow
    glow = glow.filter(ImageFilter.GaussianBlur(radius=25 + scene_number * 2))

    # Composite
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    return Image.alpha_composite(img, glow)


def _add_subtle_noise(img: Image.Image, intensity: float = 0.02) -> Image.Image:
    """Add subtle noise for texture variation."""
    import random

    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            # Add subtle noise (±intensity * 255)
            noise = int((random.random() - 0.5) * 2 * intensity * 255)
            r = max(0, min(255, r + noise))
            g = max(0, min(255, g + noise))
            b = max(0, min(255, b + noise))
            pixels[x, y] = (r, g, b)

    return img


# =============================================================================
# BATCH GENERATION
# =============================================================================

def generate_all_images(
    session_path: Path,
    palette_name: str = "sacred_light",
    base_image_path: Optional[Path] = None,
) -> Dict[str, List[Path]]:
    """Generate all video images for a session."""

    palette = PALETTES.get(palette_name, PALETTES["sacred_light"])
    manifest = load_manifest(session_path)

    generated = {
        "title_card": [],
        "section_slides": [],
        "outro": [],
        "lower_thirds": [],
        "chapter_markers": [],
        "social_preview": [],
        "scene_backgrounds": [],
    }

    # Extract metadata from manifest
    if manifest:
        title = manifest.get("title", session_path.name.replace("-", " ").title())
        subtitle = manifest.get("description", "")[:80] if manifest.get("description") else None
        sections = manifest.get("sections", [])
        duration = manifest.get("duration", 30)

        # Extract features
        features = []
        if manifest.get("audio", {}).get("binaural", {}).get("enabled"):
            base_freq = manifest.get("audio", {}).get("binaural", {}).get("base_frequency", 200)
            features.append(f"{base_freq}Hz")
        if manifest.get("youtube", {}).get("tags"):
            tags = manifest["youtube"]["tags"]
            for tag in ["theta", "alpha", "delta", "gamma"]:
                if any(tag in t.lower() for t in tags):
                    features.append(tag.capitalize())
                    break
        features.append(f"{duration} min")
    else:
        title = session_path.name.replace("-", " ").title()
        subtitle = "Sacred Digital Dreamweaver Journey"
        sections = []
        features = ["Binaural", "Meditation"]
        duration = 30

    logger.info("=" * 70)
    logger.info("GENERATING VIDEO IMAGES")
    logger.info("=" * 70)
    logger.info(f"Session: {session_path.name}")
    logger.info(f"Palette: {palette['name']}")
    logger.info(f"Title: {title}")
    logger.info("-" * 70)

    # 1. Title Card
    title_card = generate_title_card(
        session_path, palette, IMAGE_SPECS[ImageType.TITLE_CARD],
        title, subtitle, base_image_path
    )
    generated["title_card"].append(title_card)

    # 2. Section Slides
    if sections:
        for i, section in enumerate(sections):
            section_name = section.get("description", section.get("name", f"Section {i+1}"))
            start = section.get("start", 0)
            end = section.get("end", start + 60)
            section_duration = format_duration(end - start)

            slide = generate_section_slide(
                session_path, palette, IMAGE_SPECS[ImageType.SECTION_SLIDE],
                section_name, i + 1, len(sections),
                section.get("brainwave_target", "").replace("_", " → ").title(),
                section_duration, base_image_path
            )
            generated["section_slides"].append(slide)
    else:
        # Generate default section slides
        default_sections = ["Introduction", "Induction", "Journey", "Integration", "Closing"]
        for i, name in enumerate(default_sections):
            slide = generate_section_slide(
                session_path, palette, IMAGE_SPECS[ImageType.SECTION_SLIDE],
                name, i + 1, len(default_sections),
                None, None, base_image_path
            )
            generated["section_slides"].append(slide)

    # 3. Outro
    outro = generate_outro(
        session_path, palette, IMAGE_SPECS[ImageType.OUTRO],
        title, "Subscribe for More Sacred Journeys",
        "Like • Comment • Share", base_image_path
    )
    generated["outro"].append(outro)

    # 4. Lower Thirds
    lower_thirds_data = [
        (title, subtitle[:60] if subtitle else "Guided Hypnotic Journey"),
        ("Sacred Digital Dreamweaver", "youtube.com/@sacreddigitaldreamweaver"),
    ]
    for name, desc in lower_thirds_data:
        lt = generate_lower_third(
            session_path, palette, IMAGE_SPECS[ImageType.LOWER_THIRD],
            name, desc
        )
        generated["lower_thirds"].append(lt)

    # 5. Chapter Markers (from sections)
    if sections:
        for i, section in enumerate(sections[:10]):  # Limit to 10 chapters
            chapter_name = section.get("description", section.get("name", f"Chapter {i+1}"))
            timestamp = format_duration(section.get("start", i * 180))

            marker = generate_chapter_marker(
                session_path, palette, IMAGE_SPECS[ImageType.CHAPTER_MARKER],
                chapter_name, i + 1, timestamp, base_image_path
            )
            generated["chapter_markers"].append(marker)

    # 6. Social Preview
    social = generate_social_preview(
        session_path, palette, IMAGE_SPECS[ImageType.SOCIAL_PREVIEW],
        title, subtitle, features[:3], base_image_path
    )
    generated["social_preview"].append(social)

    # 7. Scene Backgrounds (5 default scenes)
    for i in range(1, 6):
        bg = generate_scene_background(
            session_path, palette, IMAGE_SPECS[ImageType.SCENE_BACKGROUND],
            i, base_image_path
        )
        generated["scene_backgrounds"].append(bg)

    # Summary
    logger.info("=" * 70)
    logger.info("VIDEO IMAGES GENERATED")
    logger.info("=" * 70)
    total = sum(len(v) for v in generated.values())
    logger.info(f"Total images: {total}")
    for img_type, paths in generated.items():
        if paths:
            logger.info(f"  {img_type}: {len(paths)}")
    logger.info(f"Output directory: {session_path / 'output' / 'video_images'}")
    logger.info("=" * 70)

    return generated


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate video images for Sacred Digital Dreamweaver sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Image Types:
  --all              Generate all image types (recommended)
  --title-card       Intro screen with title
  --section-slides   Chapter transition slides
  --outro            End screen with CTAs
  --lower-thirds     Transparent overlay bars
  --chapter-markers  Chapter number cards
  --social-preview   Square format for social media
  --scene-backgrounds Plain backgrounds for video

Palettes:
  sacred_light     - Gold/cream on cosmic dark (default)
  cosmic_journey   - Purple/blue on deep space
  garden_eden      - Emerald/gold on forest shadow
  ancient_temple   - Antique gold on temple shadow
  neural_network   - Cyan/purple on digital void
  volcanic_forge   - Red-gold on volcanic shadow
  celestial_blue   - Royal blue on night sky

Examples:
  # Generate all images for a session
  python3 generate_video_images.py sessions/garden-of-eden/ --all

  # Generate only title card and outro with cosmic palette
  python3 generate_video_images.py sessions/neural-network/ \\
      --title-card --outro --palette cosmic_journey

  # Use a specific base image
  python3 generate_video_images.py sessions/atlas/ --all \\
      --base-image sessions/atlas/images/uploaded/main.png
        """
    )

    parser.add_argument("session_path", type=Path, help="Path to session directory")

    # Image type flags
    parser.add_argument("--all", "-a", action="store_true",
                        help="Generate all image types")
    parser.add_argument("--title-card", action="store_true",
                        help="Generate title card")
    parser.add_argument("--section-slides", action="store_true",
                        help="Generate section/chapter slides")
    parser.add_argument("--outro", action="store_true",
                        help="Generate outro screen")
    parser.add_argument("--lower-thirds", action="store_true",
                        help="Generate lower third overlays")
    parser.add_argument("--chapter-markers", action="store_true",
                        help="Generate chapter marker images")
    parser.add_argument("--social-preview", action="store_true",
                        help="Generate social media preview")
    parser.add_argument("--scene-backgrounds", action="store_true",
                        help="Generate scene background images")

    # Options
    parser.add_argument("--palette", "-p",
                        choices=list(PALETTES.keys()),
                        default="sacred_light",
                        help="Color palette (default: sacred_light)")
    parser.add_argument("--base-image", "-i", type=Path,
                        help="Base image to use for all generated images")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.session_path.exists():
        logger.error(f"Session path does not exist: {args.session_path}")
        sys.exit(1)

    palette = PALETTES.get(args.palette, PALETTES["sacred_light"])
    base_image = args.base_image

    # Determine which images to generate
    generate_flags = {
        "title_card": args.title_card or args.all,
        "section_slides": args.section_slides or args.all,
        "outro": args.outro or args.all,
        "lower_thirds": args.lower_thirds or args.all,
        "chapter_markers": args.chapter_markers or args.all,
        "social_preview": args.social_preview or args.all,
        "scene_backgrounds": args.scene_backgrounds or args.all,
    }

    # If no specific flags, default to --all
    if not any(generate_flags.values()):
        generate_flags = {k: True for k in generate_flags}

    # Load manifest for metadata
    manifest = load_manifest(args.session_path)

    if manifest:
        title = manifest.get("title", args.session_path.name.replace("-", " ").title())
        subtitle = manifest.get("description", "")[:80] if manifest.get("description") else None
        sections = manifest.get("sections", [])
    else:
        title = args.session_path.name.replace("-", " ").title()
        subtitle = "Sacred Digital Dreamweaver Journey"
        sections = []

    logger.info("=" * 70)
    logger.info("VIDEO IMAGE GENERATOR")
    logger.info("=" * 70)
    logger.info(f"Session: {args.session_path.name}")
    logger.info(f"Palette: {palette['name']}")

    generated_count = 0

    # Generate requested images
    if generate_flags["title_card"]:
        generate_title_card(
            args.session_path, palette, IMAGE_SPECS[ImageType.TITLE_CARD],
            title, subtitle, base_image
        )
        generated_count += 1

    if generate_flags["section_slides"]:
        if sections:
            for i, section in enumerate(sections):
                section_name = section.get("description", section.get("name", f"Section {i+1}"))
                start = section.get("start", 0)
                end = section.get("end", start + 60)
                duration = format_duration(end - start)

                generate_section_slide(
                    args.session_path, palette, IMAGE_SPECS[ImageType.SECTION_SLIDE],
                    section_name, i + 1, len(sections),
                    section.get("brainwave_target", "").replace("_", " → ").title(),
                    duration, base_image
                )
                generated_count += 1
        else:
            default_sections = ["Introduction", "Induction", "Journey", "Integration", "Closing"]
            for i, name in enumerate(default_sections):
                generate_section_slide(
                    args.session_path, palette, IMAGE_SPECS[ImageType.SECTION_SLIDE],
                    name, i + 1, len(default_sections), None, None, base_image
                )
                generated_count += 1

    if generate_flags["outro"]:
        generate_outro(
            args.session_path, palette, IMAGE_SPECS[ImageType.OUTRO],
            title, "Subscribe for More Sacred Journeys",
            "Like • Comment • Share", base_image
        )
        generated_count += 1

    if generate_flags["lower_thirds"]:
        generate_lower_third(
            args.session_path, palette, IMAGE_SPECS[ImageType.LOWER_THIRD],
            title, subtitle[:60] if subtitle else "Guided Hypnotic Journey"
        )
        generated_count += 1

    if generate_flags["chapter_markers"]:
        if sections:
            for i, section in enumerate(sections[:10]):
                chapter_name = section.get("description", section.get("name", f"Chapter {i+1}"))
                timestamp = format_duration(section.get("start", i * 180))

                generate_chapter_marker(
                    args.session_path, palette, IMAGE_SPECS[ImageType.CHAPTER_MARKER],
                    chapter_name, i + 1, timestamp, base_image
                )
                generated_count += 1

    if generate_flags["social_preview"]:
        features = []
        if manifest:
            if manifest.get("audio", {}).get("binaural", {}).get("enabled"):
                features.append(f"{manifest.get('audio', {}).get('binaural', {}).get('base_frequency', 200)}Hz")
            features.append(f"{manifest.get('duration', 30)} min")
        generate_social_preview(
            args.session_path, palette, IMAGE_SPECS[ImageType.SOCIAL_PREVIEW],
            title, subtitle, features, base_image
        )
        generated_count += 1

    if generate_flags["scene_backgrounds"]:
        for i in range(1, 6):
            generate_scene_background(
                args.session_path, palette, IMAGE_SPECS[ImageType.SCENE_BACKGROUND],
                i, base_image
            )
            generated_count += 1

    logger.info("=" * 70)
    logger.info(f"✓ Generated {generated_count} images")
    logger.info(f"  Output: {args.session_path / 'output' / 'video_images'}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
