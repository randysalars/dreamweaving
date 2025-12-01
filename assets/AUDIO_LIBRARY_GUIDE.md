# Audio Library Usage Guide

## Overview

The Dreamweaving audio library provides a centralized collection of reusable audio assets with intelligent management tools.

## Current Assets

### Ambient (Background)
- **pink_noise_24min** (261 MB, 23.7 min) - Pink noise for ambient pads
- **ambient_pad** (283 MB, 28.4 min) - Extended ambient background

### Effects (Sound Effects)
- **crystal_bell** (345 KB, 2s) - Clear crystal bell for transitions
- **singing_bowl** (1.4 MB, 8s) - Tibetan singing bowl with rich harmonics
- **wind_chime** (517 KB, 3s) - Gentle wind chime for awakening
- **gamma_burst_noise** (517 KB, 4s) - High-energy burst for gamma states

## Command-Line Interface

### List All Assets
```bash
python3 scripts/utilities/audio_library.py list
```

### Search by Keyword
```bash
# Find all bell-related assets
python3 scripts/utilities/audio_library.py search bell

# Search by tag
python3 scripts/utilities/audio_library.py list --tag transition

# Search by use case
python3 scripts/utilities/audio_library.py list --use-case meditation
```

### Get Asset Information
```bash
python3 scripts/utilities/audio_library.py info crystal_bell
```

### Get Asset File Path
```bash
# Useful in scripts
BELL_PATH=$(python3 scripts/utilities/audio_library.py path crystal_bell)
ffmpeg -i "$BELL_PATH" ...
```

### Verify Assets
```bash
# Check that all cataloged assets exist
python3 scripts/utilities/audio_library.py verify
```

## Python API

```python
from scripts.utilities.audio_library import AudioLibrary

lib = AudioLibrary()

# Get asset path
bell_path = lib.get_asset_path('crystal_bell')

# Get asset metadata
info = lib.get_asset_info('crystal_bell')
print(f"Duration: {info['duration']}s")

# Search
results = lib.search('transition')
for asset in results:
    print(f"{asset['name']}: {asset['description']}")

# List by tag
transition_sounds = lib.list_by_tag('transition')

# List by use case
meditation_assets = lib.list_by_use_case('meditation')

# Copy to session directory
lib.copy_to_session('crystal_bell', 'sessions/my-session/sounds/bell.wav')
```

## Integration with Scripts

### Automatic Pink Noise Caching
The pink noise generator automatically uses cached assets:

```bash
# This will use cached pink_noise_24min.wav and trim to 10 minutes
python3 scripts/core/generate_pink_noise.py \
  --duration 600 \
  --output output.wav

# Force regeneration
python3 scripts/core/generate_pink_noise.py \
  --duration 600 \
  --output output.wav \
  --force-generate
```

### Using Effects in Session Scripts
Instead of hardcoding paths, use the library:

```bash
# Old way (hardcoded)
ffmpeg -i sessions/my-session/sound_effects/crystal_bell.wav ...

# New way (from library)
BELL=$(python3 scripts/utilities/audio_library.py path crystal_bell)
ffmpeg -i "$BELL" ...
```

## Adding New Assets

### 1. Add the File
```bash
cp my_new_sound.wav assets/audio/effects/
```

### 2. Update the Catalog
Edit `assets/audio/LIBRARY_CATALOG.yaml`:

```yaml
effects:
  my_new_sound:
    file: effects/my_new_sound.wav
    duration: 5  # seconds
    sample_rate: 48000
    channels: 2
    description: Description of the sound
    use_cases:
      - Meditation
      - Focus work
    tags: [ambient, gentle, nature]
    generated: 2025-11-28
```

### 3. Update Search Tags
Add to `by_tag` and `by_use_case` sections:

```yaml
by_tag:
  ambient: [pink_noise_24min, my_new_sound]

by_use_case:
  meditation: [pink_noise_24min, singing_bowl, my_new_sound]
```

### 4. Verify
```bash
python3 scripts/utilities/audio_library.py verify
```

## Asset Organization Best Practices

### Naming Convention
- Use lowercase with underscores: `crystal_bell.wav`
- Include duration for long assets: `pink_noise_24min.wav`
- Be descriptive: `tibetan_singing_bowl.wav` > `bowl1.wav`

### File Formats
- **WAV format** only (lossless)
- **48 kHz sample rate** for ambient/effects
- **44.1 kHz acceptable** for short effects
- **Stereo (2 channels)** preferred
- **16-bit or 24-bit** depth

### Catalog Documentation
Always include:
- `duration` (in seconds)
- `description` (what it sounds like)
- `use_cases` (when to use it)
- `tags` (for searching)
- `generated` date

## Common Use Cases

### Building a Session from Scratch
```python
from scripts.utilities.audio_library import AudioLibrary

lib = AudioLibrary()

# Get all transition sounds
transitions = lib.list_by_tag('transition')

# Get meditation background
bg_path = lib.get_asset_path('pink_noise_24min')

# Get awakening sound
awakening = lib.get_asset_path('wind_chime')
```

### Finding Assets by Characteristic
```bash
# Short sounds for transitions
python3 scripts/utilities/audio_library.py list --tag short

# Resonant sounds for deep states
python3 scripts/utilities/audio_library.py search resonant

# High-energy sounds for peak moments
python3 scripts/utilities/audio_library.py list --tag high-energy
```

## Performance Benefits

**Before Library:**
- Pink noise generation: ~5 minutes
- Searching for effects: Manual file hunting
- Inconsistent naming: Hard to remember paths

**After Library:**
- Pink noise trimming: <1 second (from cache)
- Asset discovery: Instant with search/tags
- Organized catalog: Clear naming and metadata

## Size Considerations

**Current Library Size:** ~545 MB
- Pink noise (24 min): 261 MB
- Ambient pad (28 min): 283 MB
- Effects (5 files): ~3 MB

**Recommendation:** Keep library under 1 GB
- Archive unused assets
- Use compression for backup
- Generate on-demand for very long sessions (>30 min)

## Future Enhancements

- [ ] Binaural beat pattern library (common frequencies cached)
- [ ] Nature sounds collection (rain, ocean, forest)
- [ ] More noise colors (brown, white, violet)
- [ ] Web interface for browsing assets
- [ ] Automatic asset generation scripts
- [ ] Quality verification (check sample rate, channels, etc.)
- [ ] Asset versioning and updates
