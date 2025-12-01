# Audio Library Quick Reference

## Quick Commands

```bash
# List everything
python3 scripts/utilities/audio_library.py list

# Search for asset
python3 scripts/utilities/audio_library.py search KEYWORD

# Get asset details
python3 scripts/utilities/audio_library.py info ASSET_NAME

# Get file path (for scripts)
python3 scripts/utilities/audio_library.py path ASSET_NAME

# Verify library
python3 scripts/utilities/audio_library.py verify
```

## Available Assets

| Asset | Type | Duration | Size | Best For |
|-------|------|----------|------|----------|
| `pink_noise_24min` | Ambient | 23.7 min | 261 MB | Background pad |
| `ambient_pad` | Ambient | 28.4 min | 283 MB | Extended sessions |
| `crystal_bell` | Effect | 2s | 345 KB | Transitions |
| `singing_bowl` | Effect | 8s | 1.4 MB | Deep moments |
| `wind_chime` | Effect | 3s | 517 KB | Awakening |
| `gamma_burst_noise` | Effect | 4s | 517 KB | Peak focus |

## Common Searches

```bash
# Transition sounds
python3 scripts/utilities/audio_library.py list --tag transition

# Meditation assets  
python3 scripts/utilities/audio_library.py list --use-case meditation

# Short effects
python3 scripts/utilities/audio_library.py list --tag short

# Background sounds
python3 scripts/utilities/audio_library.py list --tag background
```

## In Your Scripts

### Bash
```bash
# Get asset path
BELL=$(python3 scripts/utilities/audio_library.py path crystal_bell)

# Use with ffmpeg
ffmpeg -i "$BELL" -af "adelay=1000|1000" output.wav
```

### Python
```python
from scripts.utilities.audio_library import AudioLibrary

lib = AudioLibrary()
path = lib.get_asset_path('crystal_bell')
info = lib.get_asset_info('crystal_bell')
```

## Pink Noise (Auto-Cached)

```bash
# Automatically uses cached asset if available
python3 scripts/core/generate_pink_noise.py \
  --duration SECONDS \
  --output OUTPUT.wav

# Force regeneration (skip cache)
python3 scripts/core/generate_pink_noise.py \
  --duration SECONDS \
  --output OUTPUT.wav \
  --force-generate
```

## Adding Assets

1. Copy file: `cp sound.wav assets/audio/effects/`
2. Edit: `assets/audio/LIBRARY_CATALOG.yaml`
3. Verify: `python3 scripts/utilities/audio_library.py verify`

## Documentation

- **Quick Start:** `assets/README.md`
- **Full Guide:** `assets/AUDIO_LIBRARY_GUIDE.md`
- **Catalog:** `assets/audio/LIBRARY_CATALOG.yaml`
- **Summary:** `AUDIO_CACHING_SUMMARY.md`
