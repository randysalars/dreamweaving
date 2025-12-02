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
        # Look for thumbnail-specific images first
        for pattern in ["*thumbnail*", "*helm*", "*scene*05*", "*scene*04*", "*main*"]:
            matches = list(images_dir.glob(pattern))
            if matches:
                return matches[0]
        # Fall back to any PNG/JPG
        for ext in ["*.png", "*.jpg", "*.jpeg"]:
            matches = list(images_dir.glob(ext))
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

    # Determine duration
    if duration is None and manifest:
        if "duration" in manifest:
            dur = manifest["duration"]
            if isinstance(dur, (int, float)):
                minutes = int(dur // 60)
                seconds = int(dur % 60)
                duration = f"{minutes}:{seconds:02d}"
            else:
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
    if template["center_glow"]:
        img = apply_center_glow(img, palette, intensity=0.25)

    # Load fonts
    title_font = get_font("DejaVuSans-Bold", 100)
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
