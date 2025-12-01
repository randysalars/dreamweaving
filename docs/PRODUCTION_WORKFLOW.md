# Production-Ready Workflow Guide

**VERSION:** 3.0 - Google Cloud TTS
**STATUS:** ✅ PRODUCTION READY
**LAST UPDATED:** 2025-11-30

> This is the complete, error-free, automated workflow for creating meditation sessions with Google Cloud TTS Neural2 voices, binaural beats with gamma flashes, video assembly, and YouTube packaging.

## ⚠️ Breaking Changes in V3.0

**Edge TTS (Ava voice) has been removed from the workflow.**

- **Why:** Edge TTS ignores SSML `<break>` tags, making it unsuitable for hypnotic/meditative work
- **New Standard:** Google Cloud TTS Neural2 (respects all SSML breaks)
- **Migration Guide:** See [docs/EDGE_TTS_REMOVAL.md](EDGE_TTS_REMOVAL.md)

---

---

## 🚀 Quick Start: One-Command Production

```bash
# Complete session production in ONE command
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --auto-package
```

**This single command will:**
1. ✅ Generate Ava voice with Edge TTS (free)
2. ✅ Auto-extend voice to target duration (solves Edge TTS limitation)
3. ✅ Generate binaural beats with gamma flash effects
4. ✅ Mix voice + binaural at proper levels
5. ✅ Master audio to -14 LUFS (YouTube standard)
6. ✅ Assemble video with section-timed images
7. ✅ Generate YouTube thumbnail
8. ✅ Create YouTube description and upload guide
9. ✅ Run cleanup to remove intermediate files
10. ✅ Report all deliverables

**Total time:** 5-10 minutes depending on session length.

---

## 📋 Prerequisites

### 1. Session Structure
```bash
sessions/my-session/
├── manifest.yaml          # Enhanced manifest (see template)
├── script.ssml            # SSML meditation script
└── images/uploaded/       # PNG images for video sections
    ├── 01_pretalk.png
    ├── 02_induction.png
    ├── 03_journey.png
    └── ... (as many as needed)
```

### 2. Required manifest.yaml Sections

Your manifest MUST include:

```yaml
session:
  duration: 1800  # Target in seconds

voice:
  provider: "google"  # Google Cloud TTS only
  voice_name: "en-US-Neural2-D"  # Recommended: warm, soothing
  rate: 0.75  # 75% speed for meditation
  pitch: "-2.5st"  # Slightly deeper

sections:
  - {name: "pretalk", start: 0, end: 150}
  - {name: "induction", start: 150, end: 540}
  # ... etc

sound_bed:
  binaural:
    enabled: true
    base_hz: 432
    sections:
      - {start: 0, end: 150, offset_hz: 0.5}
      # ... etc

fx_timeline:  # OPTIONAL gamma flashes
  - type: "gamma_flash"
    time: 1240
    duration_s: 3.0
    freq_hz: 40

youtube:  # OPTIONAL metadata
  title: "My Session Title"
  thumbnail_source: "images/uploaded/05_key_image.png"
  tags: ["meditation", "binaural beats", "432hz"]
```

See `sessions/_template/manifest.yaml` for complete template.

---

## 🎯 Step-by-Step Workflow

### Step 1: Create Session

```bash
# Use the template
cp -r sessions/_template sessions/my-session
cd sessions/my-session
```

### Step 2: Edit Configuration

1. **Edit `manifest.yaml`**:
   - Set session duration
   - Configure binaural sections
   - Add gamma flash if desired
   - Set YouTube metadata

2. **Write `script.ssml`**:
   - Use hypnotic meditation script
   - Don't worry about SSML breaks (they're ignored by Edge TTS)
   - The system will auto-extend to target duration

3. **Add images** to `images/uploaded/`:
   - PNG format recommended
   - Named sequentially: 01_*.png, 02_*.png, etc.
   - One image per section in manifest

### Step 3: Run Production

```bash
# From project root
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --auto-package
```

### Step 4: Verify Output

Check `sessions/my-session/output/`:

```
output/
├── final_mix.mp3                    # Mastered audio
├── youtube_thumbnail.png            # Thumbnail (1280x720)
├── YOUTUBE_DESCRIPTION.md           # Upload description
├── YOUTUBE_PACKAGE_README.md        # Upload guide
└── video/
    └── session_final.mp4            # Complete video
```

---

## 🔧 Advanced Options

### Custom Voice Settings

```bash
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --voice en-US-Neural2-I \
  --target-minutes 31 \
  --carrier-hz 432 \
  --bed-gain-db -28 \
  --voice-gain-db -16 \
  --auto-package
```

### Different Google Cloud TTS Voices

```bash
# Deep, authoritative male voice
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --voice en-US-Neural2-C \
  --auto-package

# Expressive, engaging female voice
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --voice en-US-Neural2-J \
  --auto-package
```

**Available Voices:**
- **en-US-Neural2-D** (female, warm, soothing) - Default
- **en-US-Neural2-I** (female, calm, nurturing)
- **en-US-Neural2-J** (female, expressive, engaging)
- **en-US-Neural2-C** (male, deep, authoritative)
- **en-US-Neural2-F** (male, warm, reassuring)

See [docs/EDGE_TTS_REMOVAL.md](EDGE_TTS_REMOVAL.md) for voice selection guide.

### Without Video (Audio Only)

```bash
# Audio only with Google Cloud TTS
python3 scripts/core/generate_session_audio.py \
  --ssml sessions/my-session/script.ssml \
  --voice en-US-Neural2-D \
  --target-minutes 30 \
  --match-mode voice_to_target \
  --carrier-hz 432 \
  --output-dir sessions/my-session/output
```

---

## ✅ Quality Checklist

Before uploading to YouTube:

- [ ] Audio duration matches manifest duration
- [ ] Gamma flash present at specified time (if configured)
- [ ] All images appear in video at correct times
- [ ] Thumbnail looks good (1280x720, clear text)
- [ ] Description has proper timestamps
- [ ] Audio loudness is -14 LUFS (YouTube standard)
- [ ] No clipping (check -1.5 dBTP headroom)

---

## 🎥 YouTube Upload Steps

1. Navigate to `sessions/my-session/output/`
2. Open `YOUTUBE_PACKAGE_README.md` for detailed instructions
3. Upload `video/session_final.mp4`
4. Set thumbnail: `youtube_thumbnail.png`
5. Copy description from `YOUTUBE_DESCRIPTION.md`
6. Set category, tags, and publish!

---

## 🧹 Manual Cleanup (if needed)

```bash
# Remove intermediate files
bash scripts/core/cleanup_session_assets.sh sessions/my-session
```

Auto-cleanup runs automatically with `--auto-package` flag.

---

## 🔍 Troubleshooting

### Voice Too Short

**Problem**: Generated voice is shorter than expected.

**Solution**: With Google Cloud TTS, SSML `<break>` tags are respected. Check your SSML for sufficient breaks.

```bash
# Verify SSML
python3 scripts/utilities/validate_ssml.py sessions/my-session/script.ssml

# Set explicit target duration
--target-minutes 30
```

**Note:** Google Cloud TTS respects all SSML timing, so the actual duration matches your script exactly. If you need longer sessions, add more content or `<break>` tags in your SSML.

### Missing Gamma Flash

**Problem**: Gamma flash not heard in audio.

**Solution**: Check `fx_timeline` in manifest.yaml:

```yaml
fx_timeline:
  - type: "gamma_flash"
    time: 1240  # In seconds
    duration_s: 3.0
    freq_hz: 40
```

### Images Not in Video

**Problem**: Video shows black screen instead of images.

**Solution**: 
1. Check images are in `images/uploaded/` as PNG files
2. Check section timing in manifest matches image count
3. Images must be named sequentially

### YouTube Thumbnail Failed

**Problem**: No thumbnail created.

**Solution**:
1. Check DejaVu fonts installed: `ls /usr/share/fonts/truetype/dejavu/`
2. Or specify simpler thumbnail in manifest without text overlay

---

## 📊 Performance Metrics

Typical production times on average hardware:

| Task | Duration |
|------|----------|
| Voice generation (Edge TTS) | 30-60 seconds |
| Voice extension with silence | 5 seconds |
| Binaural generation | 10-30 seconds |
| Audio mixing | 5 seconds |
| Audio mastering | 5 seconds |
| Video assembly | 2-5 minutes |
| YouTube packaging | 5 seconds |
| Cleanup | 2 seconds |
| **TOTAL** | **5-10 minutes** |

---

## 🎓 Best Practices

1. **Always use manifest.yaml** - Don't hardcode settings in scripts
2. **Test audio first** - Listen before creating video
3. **Use descriptive image names** - Helps identify which section
4. **Check gamma flash timing** - Use audio editor to verify placement
5. **Validate manifest** - Use YAML linter before running
6. **Keep session-specific scripts minimal** - Use core scripts when possible

---

## 📚 Related Documentation

- [Enhanced Manifest Template](../sessions/_template/manifest.yaml)
- [SSML Script Guide](../prompts/hypnotic_dreamweaving_instructions.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Core Scripts Reference](../scripts/core/README.md)

---

**Created**: 2025-01-01  
**Maintainer**: Randy Sailer  
**Status**: Production Ready ✅
