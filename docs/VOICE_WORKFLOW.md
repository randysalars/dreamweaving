# ⚠️ DEPRECATED: Voice Generation Workflow

> **⚠️ THIS DOCUMENT IS DEPRECATED**
>
> **USE INSTEAD:** [docs/CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
>
> This document describes Edge TTS workflow which is NOT the canonical method.
> The canonical workflow uses Google Cloud TTS.
>
> This document is kept for historical reference only.
>
> **Last Updated:** 2025-11-28 (Marked as deprecated)

---

**Standard Operating Procedure for Dreamweaving Voice Production**

---

## Voice Configuration

### Primary Voice: en-US-AvaNeural (Microsoft Edge TTS)

**IMPORTANT**: Always use `en-US-AvaNeural` for all Dreamweaving sessions.

**Rationale:**
- User-preferred voice with warm, professional quality
- Excellent for meditation and hypnosis content
- Consistent tone across all sessions
- Free via Edge TTS (no API costs)
- Natural prosody control for trance induction

**Configuration File:** [config/voice_config.yaml](../config/voice_config.yaml)

---

## Quick Validation (Smoke Test)

Run this before long renders to confirm Ava + binaural + SFX are healthy:
```bash
./tests/audio_component_smoke.sh
```
Outputs (in `test_output/`):
- `voice_smoke.mp3`: Ava voice with a 6 Hz bed and a gamma SFX at 2s.
- `binaural_smoke.wav`: 10s, 6 Hz beat.
- `output/audio_summary.json`: Confirms `tts_provider: edge-tts` and SFX metadata.

Success: files render, Ava timbre is audible, 6 Hz pulse is present, SFX is audible near 2s.

---

## Voice Generation Process

### Step 1: Create SSML Script

Use proper prosody tags for different sections:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

  <!-- Pretalk: Normal rate and pitch -->
  <prosody rate="1.0" pitch="0st">
    Welcome text here...
    <break time="2s"/>
  </prosody>

  <!-- Induction: Slower rate, lower pitch for trance -->
  <prosody rate="0.85" pitch="-2st">
    Induction text here...
    <break time="3s"/>
  </prosody>

  <!-- Journey: Moderate slow rate for immersion -->
  <prosody rate="0.91" pitch="-1st">
    Journey content...
  </prosody>

  <!-- Awakening: Gentle return to normal -->
  <prosody rate="0.95" pitch="0st">
    Awakening sequence...
  </prosody>

  <!-- Closing: Normal conversational -->
  <prosody rate="1.0" pitch="0st">
    Closing and anchors...
  </prosody>

</speak>
```

### Step 2: Generate Voice Audio

Use the standardized voice generation script:

```bash
# For new sessions, use the Ava voice generator
python3 generate_voice_ava.py
```

The script will:
1. Parse SSML and extract prosody sections
2. **Convert ALL SSML tags to avoid vocalization:**
   - `<break time="Xs"/>` → Natural punctuation (comma/period/ellipsis based on duration)
   - `<emphasis level="strong">text</emphasis>` → Just "text" (tag removed, content kept)
   - `<!-- comments -->` → Removed completely
   - `<prosody>` → Converted to Edge TTS `--rate` and `--pitch` flags
3. Generate each section with Edge TTS using Ava voice
4. Concatenate sections into single audio file
5. Convert to 48kHz stereo WAV

**CRITICAL - SSML Tag Handling:**
```python
# Break tags are converted based on duration
<break time="1.5s"/>  →  '' (removed, very short)
<break time="2s"/>    →  ', ' (comma for natural pause)
<break time="3s"/>    →  '. ' (period for medium pause)
<break time="5s"/>    →  '... ' (ellipsis for long pause)
```

**DO NOT use these in your SSML script** (they WILL be read aloud):
- ❌ `[pause]`, `[breathe]`, `[silence]`
- ❌ `[PAUSE 2s]`, `[break]`
- ❌ Any square brackets `[` or `]`

**ALWAYS use proper SSML tags:**
- ✅ `<break time="2s"/>`
- ✅ `<emphasis level="strong">word</emphasis>`
- ✅ `<!-- comments -->`

**Output:**
- `working_files/<session_name>_ava.mp3` (intermediate)
- `working_files/<session_name>_ava.wav` (for mastering)

### Step 3: Apply Professional Mastering

```bash
python3 scripts/core/audio/mastering.py working_files/<session_name>_ava.wav
```

This applies the full mastering chain:
- LUFS normalization to -14 LUFS (YouTube standard)
- Warmth EQ (+1.5 dB @ 250 Hz)
- Presence EQ (+1.0 dB @ 3 kHz)
- High shelf (-0.5 dB > 10 kHz)
- Stereo enhancement (5% width)
- Peak limiting (0.95 linear ceiling)

**Output:**
- `working_files/<session_name>_ava_MASTERED.wav` (24-bit, 48kHz)
- `working_files/<session_name>_ava_MASTERED.mp3` (192 kbps)

### Step 4: Generate Dynamic Binaural Beats

Create binaural beats that transition through different brainwave frequencies to guide the session:

```bash
# Generate 8 sections with progressive frequency changes
# Example: Alpha (10 Hz) → Theta (5-6 Hz) → Gamma (40 Hz) → Alpha (10 Hz)

# Pretalk - Alpha 10 Hz
python3 scripts/core/generate_binaural.py --frequency 10 --duration 145 --output temp_audio/01_pretalk_binaural.wav

# Induction - Theta 5 Hz
python3 scripts/core/generate_binaural.py --frequency 5 --duration 145 --output temp_audio/02_induction_binaural.wav

# Neural Garden - Theta 5 Hz
python3 scripts/core/generate_binaural.py --frequency 5 --duration 290 --output temp_audio/03_garden_binaural.wav

# Pathfinder - Theta 5 Hz
python3 scripts/core/generate_binaural.py --frequency 5 --duration 290 --output temp_audio/04_pathfinder_binaural.wav

# Weaver - Theta 6 Hz
python3 scripts/core/generate_binaural.py --frequency 6 --duration 290 --output temp_audio/05_weaver_binaural.wav

# GAMMA BURST - 40 Hz (CRITICAL - insight activation)
python3 scripts/core/generate_binaural.py --frequency 40 --duration 95 --output temp_audio/06_gamma_binaural.wav

# Consolidation - Alpha 10 Hz
python3 scripts/core/generate_binaural.py --frequency 10 --duration 145 --output temp_audio/07_consolidation_binaural.wav

# Awakening - Alpha 10 Hz
python3 scripts/core/generate_binaural.py --frequency 10 --duration 21 --output temp_audio/08_awakening_binaural.wav
```

Then concatenate all sections:

```bash
# Create concat list
cat > temp_audio/binaural_concat.txt << 'EOF'
file '/absolute/path/to/temp_audio/01_pretalk_binaural.wav'
file '/absolute/path/to/temp_audio/02_induction_binaural.wav'
file '/absolute/path/to/temp_audio/03_garden_binaural.wav'
file '/absolute/path/to/temp_audio/04_pathfinder_binaural.wav'
file '/absolute/path/to/temp_audio/05_weaver_binaural.wav'
file '/absolute/path/to/temp_audio/06_gamma_binaural.wav'
file '/absolute/path/to/temp_audio/07_consolidation_binaural.wav'
file '/absolute/path/to/temp_audio/08_awakening_binaural.wav'
EOF

# Concatenate with ffmpeg
ffmpeg -f concat -safe 0 -i temp_audio/binaural_concat.txt -c copy -y temp_audio/binaural_complete.wav
```

**Binaural Frequency Guidelines:**
- **Alpha (8-12 Hz)**: Light awareness, pretalk, awakening
- **Theta (4-7 Hz)**: Deep relaxation, trance, journey states
- **Gamma (40 Hz)**: Insight activation, critical moments (3-5 second bursts)

### Step 5: Generate Ambient Pad (Optional)

Add pink noise for gentle atmospheric support:

```bash
python3 scripts/core/generate_pink_noise.py --duration 1421 --output temp_audio/ambient_pad.wav
```

### Step 6: Place Sound Effects (Optional)

Add sound effects at specific meaningful moments:

```bash
# Singing bowl at anchor teaching moment (e.g., 1410s)
ffmpeg -i sound_effects/singing_bowl.wav -af "adelay=1410000|1410000" -t 1421 -y temp_audio/singing_bowl_timed.wav

# Crystal bells at major transitions (e.g., 290s, 580s, 870s)
ffmpeg -i sound_effects/crystal_bell.wav -af "adelay=290000|290000" -t 1421 -y temp_audio/bell_1.wav
ffmpeg -i sound_effects/crystal_bell.wav -af "adelay=580000|580000" -t 1421 -y temp_audio/bell_2.wav
ffmpeg -i sound_effects/crystal_bell.wav -af "adelay=870000|870000" -t 1421 -y temp_audio/bell_3.wav

# Wind chime at awakening (e.g., 1400s)
ffmpeg -i sound_effects/wind_chime.wav -af "adelay=1400000|1400000" -t 1421 -y temp_audio/wind_chime_timed.wav

# Gamma burst noise to amplify 40 Hz section (e.g., 1160s)
ffmpeg -i sound_effects/gamma_burst_noise.wav -af "adelay=1160000|1160000" -t 1421 -y temp_audio/gamma_noise_timed.wav
```

**Note:** Delay values are in milliseconds (1410s = 1410000ms)

### Step 7: Mix All Audio Layers

Combine voice, binaural beats, ambient pad, and sound effects:

```bash
# Full 9-layer mix (voice + binaural + pad + 6 sound effects)
ffmpeg \
  -i working_files/<session>_ava_MASTERED.wav \
  -i temp_audio/binaural_complete.wav \
  -i temp_audio/ambient_pad.wav \
  -i temp_audio/singing_bowl_timed.wav \
  -i temp_audio/bell_1.wav \
  -i temp_audio/bell_2.wav \
  -i temp_audio/bell_3.wav \
  -i temp_audio/wind_chime_timed.wav \
  -i temp_audio/gamma_noise_timed.wav \
  -filter_complex '[0:a]volume=-2dB[voice];[1:a]volume=-14dB[binaural];[2:a]volume=-18dB[pad];[3:a]volume=-16dB[bowl];[4:a]volume=-16dB[bell1];[5:a]volume=-16dB[bell2];[6:a]volume=-16dB[bell3];[7:a]volume=-16dB[chime];[8:a]volume=-12dB[gamma];[voice][binaural][pad][bowl][bell1][bell2][bell3][chime][gamma]amix=inputs=9:duration=first:normalize=0[mixed]' \
  -map '[mixed]' \
  -c:a pcm_s24le \
  -ar 48000 \
  -y working_files/<session>_ULTIMATE_MIX.wav
```

**Mixing Levels:**
- Voice (mastered -14 LUFS): **-2 dB** (primary, clear)
- Binaural beats (dynamic): **-14 dB** (subtle background)
- Ambient pad: **-18 dB** (gentle support)
- Singing bowl: **-16 dB** (anchor moments)
- Crystal bells: **-16 dB** (transitions)
- Wind chime: **-16 dB** (awakening)
- Gamma burst noise: **-12 dB** (slightly louder for impact)

**Or Simple 2-Layer Mix (voice + binaural only):**

```bash
ffmpeg \
  -i working_files/<session>_ava_MASTERED.wav \
  -i temp_audio/binaural_complete.wav \
  -filter_complex '[0:a]volume=-2dB[voice];[1:a]volume=-14dB[binaural];[voice][binaural]amix=inputs=2:duration=first:normalize=0[mixed]' \
  -map '[mixed]' \
  -c:a pcm_s24le \
  -ar 48000 \
  -y working_files/<session>_VOICE_BINAURAL_MIX.wav
```

### Step 8: Create Final Video with Matched Timing

Generate individual scene videos with exact timing, then combine with audio:

```bash
# Generate timed scene videos (Python script)
python3 << 'EOF'
import subprocess

# Define scenes with durations matching audio sections
scenes = [
    ("scene_01_opening.png", 145),       # Pretalk
    ("scene_02_descent.png", 145),       # Induction
    ("scene_03_neural_garden.png", 290), # Neural Garden
    ("scene_04_pathfinder.png", 290),    # Pathfinder
    ("scene_05_weaver.png", 290),        # Weaver
    ("scene_06_gamma_burst.png", 95),    # Gamma Burst
    ("scene_07_consolidation.png", 145), # Consolidation
    ("scene_08_return.png", 21.522)      # Awakening (exact match)
]

# Generate individual timed videos
for i, (img, dur) in enumerate(scenes, 1):
    cmd = [
        'ffmpeg', '-y', '-loop', '1', '-framerate', '25',
        '-i', f'images/{img}',
        '-t', str(dur),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
        f'temp_audio/scene_{i:02d}.mp4'
    ]
    subprocess.run(cmd, capture_output=True)
EOF

# Create concat list
cat > temp_audio/scenes_concat.txt << 'EOF'
file 'scene_01.mp4'
file 'scene_02.mp4'
file 'scene_03.mp4'
file 'scene_04.mp4'
file 'scene_05.mp4'
file 'scene_06.mp4'
file 'scene_07.mp4'
file 'scene_08.mp4'
EOF

# Combine video scenes with ultimate audio mix
ffmpeg -f concat -safe 0 -i temp_audio/scenes_concat.txt \
  -i working_files/<session>_ULTIMATE_MIX.wav \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -y final_export/<session>_ULTIMATE_FINAL.mp4
```

**IMPORTANT:** Ensure video and audio durations match exactly:
- Sum all scene durations = total audio duration
- Last scene duration should include fractional seconds (e.g., 21.522s)
- Use `-shortest` flag only if you want to trim to shortest stream

---

## Prosody Guidelines

### Rate (Speaking Speed)

- **1.0** - Normal conversational (pretalk, closing)
- **0.95** - Slightly slower (gentle awakening)
- **0.91** - Moderate slow (journey sections)
- **0.85** - Noticeably slower (deep induction)

**Edge TTS Format:** `rate="0.85"` → converted to `-15%`

### Pitch

- **+0st / 0Hz** - Normal pitch (pretalk, closing, awakening)
- **-1st / -1Hz** - Slightly lower (journey)
- **-2st / -2Hz** - Lower for deeper trance (induction)

**Edge TTS Format:** `pitch="-2st"` → converted to `-2Hz`

### Breaks (Pauses)

- **2s** - Short pause between sentences
- **3s** - Medium pause for transition
- **4s** - Longer pause for deep processing
- **5s** - Extended pause for integration

---

## Quality Checklist

Before finalizing voice audio:

**SSML Script Validation:**
- [ ] NO square brackets `[` or `]` anywhere in the script
- [ ] All pauses use proper `<break time="Xs"/>` SSML tags
- [ ] All emphasis uses `<emphasis level="strong">text</emphasis>` tags
- [ ] No `[pause]`, `[breathe]`, `[PAUSE]`, or similar text markers
- [ ] Test: Search script for `[` - should return ZERO results

**Voice Generation:**
- [ ] Voice is `en-US-AvaNeural` (verify in generation logs)
- [ ] All sections have appropriate prosody settings
- [ ] Listen to first 60 seconds - NO script tags are being read aloud
- [ ] Breaks sound natural (not words like "break time equals")
- [ ] No audio artifacts or glitches

**Audio Quality:**
- [ ] LUFS level is -14 LUFS (check mastering output)
- [ ] True peak is below -1.5 dBTP
- [ ] Warmth and presence EQ applied
- [ ] Duration matches expected session length
- [ ] MP3 generated for distribution

**Final Verification:**
- [ ] Play full track - scan for ANY vocalized script tags
- [ ] Check transitions between sections are smooth
- [ ] Verify no XML/SSML tags are being spoken

---

## Common Issues

### Issue: Script tags being read aloud (e.g., "break time equals", "[pause]")

**Symptoms:**
- Voice says "break time equals forward slash"
- Hearing "[PAUSE 2s]" or similar text markers
- XML/SSML tags being vocalized

**Root Cause:** Script contains text markers instead of proper SSML tags, OR break tags aren't being converted properly.

**Solution:**
1. **Check SSML script** - Search for `[` character:
   ```bash
   grep '\[' working_files/voice_script.ssml
   # Should return NO results
   ```

2. **Verify generation script** has break tag conversion (lines 25-43 in generate_voice_v2_ava.py):
   ```python
   # Must handle decimal seconds (1.5s, 6s, etc.)
   content = re.sub(r'<break time="([\d.]+)s"\s*/>', replace_break, content)
   ```

3. **Replace ALL text markers** with proper SSML:
   ```bash
   # Bad (will be read aloud):
   And now... [pause 3s] ...you can relax
   Take a deep breath [breathe]

   # Good (properly converted):
   And now...<break time="3s"/> ...you can relax
   Take a deep breath<break time="2s"/>
   ```

4. **Regenerate voice** after fixing script
5. **Test first 60 seconds** to verify fix worked

### Issue: Wrong voice used

**Solution:** Check generation script. Ensure `voice="en-US-AvaNeural"` parameter.

### Issue: Audio sounds thin or harsh

**Solution:** Verify mastering chain applied. Check for warmth (+1.5 dB @ 250 Hz) and presence (+1.0 dB @ 3 kHz) boosts.

### Issue: Voice getting lost in mix

**Solution:**
1. Check voice is at -16 LUFS before mixing
2. Verify sidechain ducking is enabled
3. Ensure background elements are at proper levels (-28 to -32 LUFS)

### Issue: Unnatural pauses

**Solution:** Review SSML break times. Edge TTS uses actual silence, so breaks should be slightly shorter than with other TTS engines.

---

## File Naming Convention

Always use consistent naming:

```
<session_name>_ava.mp3          # Raw Edge TTS output
<session_name>_ava.wav          # Converted to WAV
<session_name>_ava_MASTERED.wav # After mastering (24-bit)
<session_name>_ava_MASTERED.mp3 # Distribution MP3
```

---

## Example: Complete Voice Generation

```bash
# 1. Create SSML script
nano sessions/my-session/working_files/voice_script.ssml

# 2. Generate voice with Ava
cd sessions/my-session
python3 ../../generate_voice_ava.py

# 3. Master the audio
cd ../..
python3 scripts/core/audio/mastering.py sessions/my-session/working_files/my_session_ava.wav

# 4. Verify outputs
ls -lh sessions/my-session/working_files/*MASTERED*
```

**Expected Results:**
- `my_session_ava_MASTERED.wav` - 24-bit WAV, -14 LUFS
- `my_session_ava_MASTERED.mp3` - 192 kbps MP3

---

## References

- **Voice Config:** [config/voice_config.yaml](../config/voice_config.yaml)
- **Mastering Module:** [scripts/core/audio/mastering.py](../scripts/core/audio/mastering.py)
- **Mixer Module:** [scripts/core/audio/mixer.py](../scripts/core/audio/mixer.py)
- **Example Implementation:** [sessions/neural-network-navigator/generate_voice_v2_ava.py](../sessions/neural-network-navigator/generate_voice_v2_ava.py)

---

**Last Updated:** 2025-11-28
**Voice:** en-US-AvaNeural (Microsoft Edge TTS)
**Standard:** -14 LUFS, 24-bit/48kHz WAV
**Audio Layers:** Voice + Dynamic Binaural + Ambient Pad + Sound Effects (9 layers max)
