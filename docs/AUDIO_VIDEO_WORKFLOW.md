# ⚠️ DEPRECATED: Dreamweaving Audio & Video Production Workflow

> **⚠️ THIS DOCUMENT IS DEPRECATED**
>
> **USE INSTEAD:** [docs/CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
>
> This document contains outdated and conflicting information.
> It is kept for historical reference only.
>
> **Last Updated:** 2025-11-28 (Marked as deprecated)

---

## Overview

This document outlines the complete workflow for creating dreamweaving sessions with professional audio and video output.

## Production Pipeline

### Phase 1: Voice Generation

1. **Write SSML Script**
   - Create script in `sessions/{session_name}/working_files/voice_script_enhanced_v2.ssml`
   - **CRITICAL**: Validate SSML tags for Edge TTS compatibility
     - Use `level="strong"` or `level="reduced"` for emphasis (NOT "moderate")
     - Test with: `python3 scripts/utilities/validate_ssml.py <script.ssml>`

2. **Generate Voice Audio**
   ```bash
   cd sessions/{session_name}
   python3 generate_voice_v2_ava.py
   ```
   - Output: `working_files/{session}_v2_ava.wav`
   - Voice: en-US-AvaNeural (warm, professional)

3. **Apply Audio Mastering**
   ```bash
   ffmpeg -i working_files/{session}_v2_ava.wav \
     -af "loudnorm=I=-14:TP=-1.5:LRA=11,\
          equalizer=f=250:t=h:width=200:g=1.5,\
          equalizer=f=3000:t=h:width=2000:g=1.0,\
          highshelf=f=10000:g=-0.5,\
          alimiter=limit=0.9:attack=5:release=50" \
     -c:a pcm_s24le -ar 48000 -y \
     working_files/{session}_v2_ava_MASTERED.wav
   ```
   - Target: -14 LUFS (YouTube standard)
   - Professional EQ and limiting applied

### Phase 2: Ultimate Audio Mix

**ALWAYS use the ultimate mix for final video production.**

4. **Create Ultimate Audio Mix**
   ```bash
   cd sessions/{session_name}
   ./create_ultimate_audio.sh
   ```

   This generates a comprehensive 9-layer soundscape:
   - **Layer 1**: Mastered voice (primary, -14 LUFS)
   - **Layer 2**: Dynamic binaural beats (Alpha → Theta → 40Hz Gamma → Alpha)
   - **Layer 3**: Pink noise ambient pad (from cached asset library)
   - **Layer 4-9**: Sound effects at key moments
     - Singing bowls at anchor points
     - Crystal bells at transitions
     - Wind chimes at awakening
     - Gamma burst noise during peak focus

   **Benefits**:
   - Immersive soundscape with professional layering
   - Automatic caching of pink noise (300x faster than regenerating)
   - Consistent audio levels across all elements
   - Sound effects timed to script sections

   Output: `working_files/{session}_ULTIMATE_MIX.wav`

### Phase 3: Video Production

5. **Generate Scene Images** (if needed)
   - Use AI image generation for 8 key scenes:
     - Opening/Pretalk
     - Induction/Descent
     - Main content scenes (3-5 scenes)
     - Consolidation
     - Awakening/Closing
   - Resolution: 1920x1080 minimum
   - Save to: `sessions/{session_name}/images/`

6. **Create Final Video**
   ```bash
   cd sessions/{session_name}
   python3 create_final_v2_ava.py
   ```

   This script:
   - Uses the ultimate mix audio (NOT simple voice+binaural)
   - Creates video with 8 scene images
   - Encodes at 1920x1080 @ 30fps
   - H.264 with AAC audio (YouTube optimized)
   - Adds faststart flag for web streaming

   Output: `final_export/{session}_v2_ava_FINAL.mp4`

## Audio Asset Library

### Automatic Caching

The workflow uses a reusable asset library at `assets/audio/` to speed up production:

- **Pink noise**: Pre-generated, trimmed to needed duration (instant vs 5+ minutes)
- **Sound effects**: Reusable bells, bowls, chimes
- **Binaural patterns**: Common frequencies cached for reuse

### Using the Library

**Search for assets:**
```bash
python3 scripts/utilities/audio_library.py search "bell"
```

**List all assets:**
```bash
python3 scripts/utilities/audio_library.py list
```

**Get asset info:**
```bash
python3 scripts/utilities/audio_library.py info crystal_bell
```

**Verify assets exist:**
```bash
python3 scripts/utilities/audio_library.py verify
```

See [Asset Library README](../assets/README.md) for details.

## Quality Checklist

Before final export, verify:

- [ ] SSML script validated (no invalid tags)
- [ ] Voice audio generated successfully
- [ ] Audio mastering applied (-14 LUFS target)
- [ ] **Ultimate mix created** (not simple voice+binaural)
- [ ] All scene images present in `images/` directory
- [ ] Video duration matches audio duration
- [ ] Final video plays correctly with all audio layers

## Common Issues

### SSML Reading Aloud

**Problem**: Voice reads markup tags like "emphasis on" instead of processing them

**Solution**:
- Validate SSML with `scripts/utilities/validate_ssml.py`
- Use only supported Edge TTS tags
- Emphasis levels: "strong" or "reduced" only (NOT "moderate")

### Pink Noise Takes Too Long

**Problem**: Generating pink noise takes 5+ minutes

**Solution**:
- Asset caching is now automatic in `generate_pink_noise.py`
- Pre-generated 24-minute pink noise is trimmed instantly
- First run generates, subsequent runs use cache (300x faster)

### Audio Levels Inconsistent

**Problem**: Voice too quiet or sound effects too loud

**Solution**:
- Ultimate mix script automatically balances all layers
- Voice: -14 LUFS (primary)
- Binaural: -28 LUFS (subtle background)
- Ambient pad: -32 LUFS (deep background)
- Effects: Timed volume curves for natural blend

## File Structure

```
sessions/{session_name}/
├── working_files/
│   ├── voice_script_enhanced_v2.ssml      # SSML source
│   ├── {session}_v2_ava.wav               # Raw voice
│   ├── {session}_v2_ava_MASTERED.wav      # Mastered voice
│   └── {session}_ULTIMATE_MIX.wav         # Final audio mix ★
├── images/
│   ├── scene_01_opening_FINAL.png
│   ├── scene_02_descent_FINAL.png
│   └── ... (6 more scenes)
├── create_ultimate_audio.sh               # Audio mixing script
├── create_final_v2_ava.py                 # Video creation script
└── final_export/
    └── {session}_v2_ava_FINAL.mp4         # Final deliverable
```

## Best Practices

1. **Always validate SSML** before generating voice
2. **Always use ultimate mix** for final video (not simple voice+binaural)
3. **Use asset library** for pink noise and sound effects (faster, consistent)
4. **Test audio** before starting video encoding (video takes time)
5. **Keep source files** in `working_files/` for future edits
6. **Document timing** of sound effects in session notes

## Advanced Customization

### Custom Binaural Patterns

Edit `create_ultimate_audio.sh` to customize binaural frequencies:
```bash
# Example: Use deeper theta for meditation
python3 ../../scripts/core/generate_binaural.py \
  --duration 300 \
  --frequencies 4.5-4.5 \  # 4.5 Hz theta (was 5 Hz)
  --output temp_audio/induction_binaural.wav
```

### Custom Sound Effect Timing

Modify `create_ultimate_audio.sh` to place effects at specific timestamps:
```bash
# Example: Add bell at 10:30
ffmpeg -i sound_effects/crystal_bell.wav \
  -af "adelay=630000|630000" \  # 10:30 = 630 seconds * 1000ms
  temp_audio/bell_custom.wav
```

### Adding New Assets

Generate and catalog new assets:
```bash
# Generate 30-minute pink noise
python3 scripts/core/generate_pink_noise.py \
  --duration 1800 \
  --output assets/audio/ambient/pink_noise_30min.wav \
  --force-generate

# Add to catalog
Edit assets/audio/LIBRARY_CATALOG.yaml
```

## Troubleshooting

**Video creation fails:**
- Check that ultimate mix exists in `working_files/`
- Verify all image files exist in `images/` directory
- Ensure FFmpeg is installed and up to date

**Audio sounds distorted:**
- Check input levels (should be normalized)
- Verify mastering didn't clip (peak < -1.5 dBTP)
- Test individual stems before mixing

**Wrong audio in video:**
- Confirm `create_final_v2_ava.py` points to `ULTIMATE_MIX.wav`
- Not the old simple voice+binaural mix
- Check the updated workflow uses ultimate mix path

## Future Enhancements

- [ ] Automated SSML validation in generation pipeline
- [ ] Pre-generate binaural patterns for common frequencies
- [ ] Video scene timing synchronized with script sections
- [ ] Automated quality checks before final export
- [ ] Batch processing for multiple sessions
