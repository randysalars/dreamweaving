# Auto-Generate Workflow Notes

## Overview

The `/auto-generate` command (or `python3 scripts/ai/auto_generate.py`) produces complete YouTube-ready sessions from just a topic.

## Key Fixes Applied (December 2025)

### 1. Topic/Title Fix
**Problem**: Titles defaulted to generic templates like "Starlight Journey of Abundance" instead of using the user's actual topic.

**Solution** (in `scripts/ai/creative_workflow.py`):
- `_generate_title()` now uses the topic directly if it has 3+ words
- Added `_enhance_topic_title()` for proper title case formatting
- `_generate_setting()` derives setting from topic keywords
- Added `_derive_setting_from_topic()` with 13 themed setting mappings

### 2. Image Method Default
**Problem**: Default `--image-method stock` only generates a guide, not actual images, causing video assembly to fail.

**Solution** (in `scripts/ai/auto_generate.py`):
- Changed default from `'stock'` to `'sd'` (Stable Diffusion)
- Line 141: `image_method: str = 'sd'`
- Line 1155: `parser.add_argument('--image-method', default='sd', ...)`

### 3. Website Upload Update Mode
**Problem**: Re-uploading a session fails with 409 "already exists" error.

**Solution** (in `scripts/core/upload_to_website.py`):
- Added `--update` flag for updating existing records
- Added `update_dreamweaving()` method using PUT
- Note: Website API PUT endpoint still needs implementation on backend

## Standard Workflow

```bash
# Basic usage - topic to YouTube package
python3 scripts/ai/auto_generate.py --topic "Journey to the Land of Endless Prosperity" --mode standard

# With specific duration
python3 scripts/ai/auto_generate.py --topic "Your Topic Here" --duration 30 --mode standard

# Budget mode for testing
python3 scripts/ai/auto_generate.py --topic "Test Session" --mode budget --duration 15
```

## Post-Generation Steps

### If Video is Corrupted (moov atom not found)
```bash
# Delete corrupted video and regenerate
rm -f sessions/{session}/output/video/session_final.mp4

# Regenerate video
python3 scripts/core/assemble_session_video.py \
  --session sessions/{session}/ \
  --audio sessions/{session}/output/{session_slug}_MASTER.mp3

# Verify with ffprobe
ffprobe -v error -show_format sessions/{session}/output/video/session_final.mp4
```

### Upload to Website
```bash
# First upload
python3 scripts/core/upload_to_website.py --session sessions/{session}/ --no-git

# Re-upload (if record exists) - upload files, then check if URLs updated
python3 scripts/core/upload_to_website.py --session sessions/{session}/ --no-git --update
```

## Image Generation Methods

| Method | Command | Notes |
|--------|---------|-------|
| `sd` (default) | `--image-method sd` | Local Stable Diffusion, ~50-60s per image |
| `stock` | `--image-method stock` | Generates guide only, manual sourcing needed |
| `midjourney` | `--image-method midjourney` | Generates prompts only, manual creation needed |
| `pil` | `--image-method pil` | Fast procedural fallback |

## Audio Processing

### Standard Post-Processing
```bash
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/
```

### Voice-Clear Mode (if audio is muddy)
```bash
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/ --voice-clear
```

Voice-clear disables: whisper overlay, subharmonic, double-voice, HF aura, dual reverb, adaptive processing.

## Output Locations

| File | Path |
|------|------|
| Master audio | `sessions/{session}/output/{slug}_MASTER.mp3` |
| Final video | `sessions/{session}/output/video/session_final.mp4` |
| Scene images | `sessions/{session}/images/uploaded/*.png` |
| Auto-generate report | `sessions/{session}/working_files/auto_generate_report.yaml` |

## Cost Breakdown (Standard Mode ~$1.06)

- Manifest generation: $0.05
- Script generation: $0.35
- Image prompts: $0.10
- Voice synthesis (Google TTS): $0.15
- VTT generation: $0.05

## Troubleshooting

### Video shows "moov atom not found"
The video file is incomplete/corrupted. FFmpeg was interrupted before finishing. Delete and regenerate.

### No images for video assembly
Check that `--image-method sd` is being used. If SD fails, images won't be generated and video assembly is skipped.

### 409 error on upload
Record already exists. Use `--update` flag (requires backend PUT endpoint) or manually update via database.

### Audio too quiet/muddy
Try `--voice-clear` mode in post-processing, or check stem levels in mixing (-6dB for voice/binaural).
