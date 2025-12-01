# Dreamweaving Reusable Asset Library

This directory contains pre-generated audio assets that can be reused across multiple sessions, dramatically speeding up audio generation.

## Directory Structure

```
assets/
  audio/
    ambient/          # Background ambient sounds
    effects/          # Sound effects (bells, chimes, etc.)
    binaural/         # Pre-generated binaural beat patterns
```

## How It Works

### Automatic Caching

The audio generation scripts automatically check for cached assets before generating new ones:

1. **Pink Noise Generation**: When `generate_pink_noise.py` is called:
   - Checks `assets/audio/ambient/` for existing pink noise files
   - If a file long enough is found, trims it to needed duration (instant)
   - Otherwise, generates fresh pink noise and saves for future use

2. **Benefits**:
   - **Speed**: Trimming takes milliseconds vs minutes of generation
   - **Consistency**: Same ambient texture across all sessions
   - **Disk space**: Generate once, reuse many times

### Current Assets

#### Ambient
- `pink_noise_24min.wav` (261 MB) - 23.7 minutes of pink noise
  - Used as ambient pad background
  - Can be trimmed to any duration ≤ 23.7 min

### Usage

Scripts automatically use cached assets. To force regeneration:

```bash
python3 scripts/core/generate_pink_noise.py \
  --duration 1200 \
  --output output.wav \
  --force-generate
```

## Adding New Assets

### Pink Noise (Different Durations)

Generate longer pink noise for future sessions:

```bash
# Generate 30-minute pink noise
python3 scripts/core/generate_pink_noise.py \
  --duration 1800 \
  --output assets/audio/ambient/pink_noise_30min.wav \
  --force-generate
```

### Other Noise Colors

Future expansion could include:
- Brown noise (deeper, rumbling)
- White noise (higher frequency)
- Violet noise (even higher)

### Sound Effects

Common sound effects can be stored in `assets/audio/effects/`:
- Crystal bells
- Singing bowls
- Wind chimes
- Rain sounds
- Ocean waves
- Forest ambience

### Binaural Beats

Pre-generate common binaural patterns in `assets/audio/binaural/`:
- `alpha_10hz_5min.wav` - Common alpha frequency
- `theta_5hz_5min.wav` - Deep meditation
- `gamma_40hz_2min.wav` - Peak focus burst

## Best Practices

1. **Name files descriptively**: Include type and duration
   - Good: `pink_noise_30min.wav`
   - Bad: `ambient_1.wav`

2. **High quality**: Always use 48kHz, 16-bit or 24-bit WAV
   - Matches production quality standards
   - Prevents quality loss on reuse

3. **Document additions**: Update this README when adding assets

4. **Version control**: Large assets (>100MB) may be .gitignored
   - Consider separate asset repository or cloud storage
   - Include generation scripts instead

## Size Considerations

Current total: ~261 MB

Audio files are large but worthwhile:
- **Pink noise 24 min**: 261 MB (saves ~5 min generation time)
- **Pink noise 30 min**: ~320 MB (future-proof for longer sessions)

For very large asset collections (>1GB), consider:
- Separate asset repository
- Cloud storage with download scripts
- Compression for archival

## Future Enhancements

- [ ] Binaural beat pattern library
- [ ] Sound effect collection
- [ ] Multiple noise colors (brown, white, violet)
- [ ] Automated asset management scripts
- [ ] Quality verification on cached assets
- [ ] Cache invalidation/regeneration system
