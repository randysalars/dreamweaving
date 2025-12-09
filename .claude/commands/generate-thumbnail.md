# Generate Ultimate YouTube Thumbnail

Generate an optimized YouTube thumbnail for a Dreamweaver session using LLM-powered text optimization and auto-style selection.

## Arguments

$ARGUMENTS: Session path (e.g., sessions/iron-soul-forge/)

## Workflow

1. **Load manifest** from the session directory
2. **Extract metadata**: title, outcome, theme, archetypes, duration, features
3. **Optimize title text** using LLM (Claude Haiku) to create 2-5 punchy words
4. **Auto-select style** (template + palette) based on outcome and theme
5. **Generate thumbnail** with viral micro-effects (glow, fog, sigil)
6. **Save outputs** to `output/thumbnails/` and `output/youtube_thumbnail.png`

## Command

```bash
python3 scripts/core/generate_ultimate_thumbnail.py $ARGUMENTS
```

## Options

For multiple A/B variants:
```bash
python3 scripts/core/generate_ultimate_thumbnail.py $ARGUMENTS --variants 3
```

For manual overrides:
```bash
python3 scripts/core/generate_ultimate_thumbnail.py $ARGUMENTS \
    --title "YOUR TITLE" \
    --template portal_shockwave \
    --palette gold_enlightenment
```

## Available Templates

| Template | Description | Best For |
|----------|-------------|----------|
| `portal_gateway` | Luminous center with dark edges | Healing, relaxation |
| `portal_shockwave` | Right silhouette + center portal (highest CTR) | Transformation, empowerment |
| `archetype_reveal` | Close-up with dramatic aura | Confidence, character focus |
| `impossible_landscape` | Jaw-dropping scene | Spiritual growth, realms |
| `transformation_shot` | Golden rays, crown effect | Abundance, manifestation |
| `shadow_confrontation` | Dark mirror reflection | Shadow work |

## Available Palettes

| Palette | Description | Best For |
|---------|-------------|----------|
| `sacred_light` | Gold/cream on cosmic dark | Healing, spiritual |
| `gold_enlightenment` | Brilliant gold + white | Empowerment, confidence |
| `cosmic_journey` | Purple/blue on deep space | Transformation |
| `volcanic_forge` | Iron red + gold | Strength, forging |
| `amethyst_mystery` | Violet + gold | Prophecy, mystery |
| `aurora_healing` | Teal + silver | Healing, calm |
| `celestial_blue` | Sky blue + white | Relaxation, sleep |

## Output

- `output/thumbnails/youtube_thumbnail.png` - Primary thumbnail
- `output/thumbnails/thumbnail_v1.png`, `v2.png`, `v3.png` - Variants (if requested)
- `output/youtube_thumbnail.png` - Canonical location
- `output/youtube_package/thumbnail.png` - If package exists

## Example

For session `sessions/iron-soul-forge/`:
```
Input:  "The Iron Soul Forge - Ancient Alchemy for Inner Strength"
Output: "FORGE YOUR SOUL" (2-5 words, optimized for CTR)
Style:  portal_shockwave + volcanic_forge (auto-selected from outcome/theme)
```
