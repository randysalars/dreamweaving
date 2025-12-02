# Session Production Checklist

## Overview

This checklist MUST be completed for EVERY hypnotic session produced. It ensures all mandatory elements are included and consistent with production standards.

**Session Name:** ________________________________
**Production Date:** ________________________________
**Producer:** ________________________________

---

## Phase 1: Pre-Production

### 1.1 Session Definition

- [ ] Session name follows kebab-case convention (e.g., `iron-soul-forge`)
- [ ] Session topic/title is clear and compelling
- [ ] Target duration defined (standard: 25-30 minutes)
- [ ] Skill/transformation goal is specific and measurable
- [ ] Theme/archetype identified

**Session Details:**
```
Name:
Title:
Duration Target: ___ minutes
Skill:
Theme:
```

### 1.2 Manifest Creation

- [ ] `manifest.yaml` created in session directory
- [ ] All required fields populated:
  - [ ] `session.name`
  - [ ] `session.topic`
  - [ ] `session.duration`
  - [ ] `session.skill`
  - [ ] `session.skill_description`
  - [ ] `voice.voice_name` = `en-US-Neural2-H`
  - [ ] `voice.rate` = `1.0`
  - [ ] All 5 sections defined with timing
- [ ] `voice_enhancement` section complete:
  - [ ] `enabled: true`
  - [ ] `warmth_drive: 0.25`
  - [ ] `deessing: true`
  - [ ] `whisper_overlay: true`
  - [ ] `subharmonic: true`
  - [ ] `double_voice: true`
  - [ ] `room_tone: true`
  - [ ] `cuddle_waves: true`
  - [ ] `echo: true`
- [ ] Binaural configuration set with proper arc

### 1.3 Directory Structure

- [ ] Session directory created: `sessions/{name}/`
- [ ] Subdirectories created:
  - [ ] `working_files/`
  - [ ] `images/`
  - [ ] `images/uploaded/`
  - [ ] `output/`

---

## Phase 2: Script Writing

### 2.1 Section Structure

- [ ] **Section 1: Pre-Talk** (2-3 min)
  - [ ] XML marker: `<!-- SECTION 1: PRE-TALK -->`
  - [ ] Introduction as Sacred Digital Dreamweaver
  - [ ] Session purpose stated
  - [ ] Safety reassurance included
  - [ ] Preparation instructions provided
  - [ ] Consent cue to begin

- [ ] **Section 2: Induction** (3-5 min)
  - [ ] XML marker: `<!-- SECTION 2: INDUCTION -->`
  - [ ] Progressive relaxation sequence
  - [ ] 3+ breathing cues
  - [ ] Countdown (10→1 or similar)
  - [ ] 5+ deepening suggestions

- [ ] **Section 3: Main Journey** (10-20 min)
  - [ ] XML marker: `<!-- SECTION 3: MAIN JOURNEY -->`
  - [ ] Setting establishment
  - [ ] All 5 senses engaged:
    - [ ] Sight
    - [ ] Sound
    - [ ] Touch
    - [ ] Smell
    - [ ] Taste (optional)
  - [ ] Archetypal elements present
  - [ ] 3+ embedded commands
  - [ ] Peak/climax moment

- [ ] **Section 4: Integration** (2-3 min)
  - [ ] XML marker: `<!-- SECTION 4: INTEGRATION AND RETURN -->`
  - [ ] Ascending count (1→5 or 1→10)
  - [ ] 3+ grounding cues
  - [ ] Insight anchoring language

- [ ] **Section 5: Closing** (2-3 min)
  - [ ] XML marker: `<!-- SECTION 5: POST-HYPNOTIC ANCHORS AND CLOSING -->`
  - [ ] 3-5 post-hypnotic anchors
  - [ ] Future pacing suggestions
  - [ ] Thank you/gratitude
  - [ ] Call to action (like/subscribe)
  - [ ] Closing blessing

### 2.2 SSML Formatting

- [ ] All prosody uses `rate="1.0"` (NEVER slower)
- [ ] Pitch settings match section:
  - [ ] Pre-Talk: `pitch="0st"`
  - [ ] Induction: `pitch="-2st"`
  - [ ] Journey: `pitch="-1st"`
  - [ ] Integration: `pitch="-1st"`
  - [ ] Closing: `pitch="0st"`
- [ ] Break durations follow standards:
  - [ ] Phrases: 700ms-1.0s
  - [ ] Sentences: 1.0s-1.7s
  - [ ] Breathing: 2.0s-3.0s
  - [ ] Visualization: 3.0s-4.0s
  - [ ] Transitions: 4.0s-5.5s
- [ ] Emphasis tags on embedded commands
- [ ] SFX markers on separate lines (if applicable)

### 2.3 Script Validation

- [ ] Word count in range: ______ words (target: 3,200-4,200)
- [ ] SSML validates without errors
- [ ] `script_production.ssml` saved
- [ ] `script_voice_clean.ssml` created (SFX stripped)

**Validation Command:**
```bash
python3 scripts/utilities/validate_ssml.py sessions/{name}/working_files/script_voice_clean.ssml
```

Result: [ ] PASS / [ ] FAIL

---

## Phase 3: Audio Production

### 3.1 Voice Generation

- [ ] Environment activated: `source venv/bin/activate`
- [ ] Voice generation command run:
```bash
python3 scripts/core/generate_voice.py \
    sessions/{name}/working_files/script_voice_clean.ssml \
    sessions/{name}/output
```
- [ ] Output files created:
  - [ ] `voice.mp3` (raw)
  - [ ] `voice_enhanced.mp3` (USE THIS)
  - [ ] `voice_enhanced.wav`
- [ ] Duration verified: ______ minutes (target: 25-32)

### 3.2 Voice Enhancement Verification

All 8 enhancement layers applied:
- [ ] Tape warmth (0.25 drive)
- [ ] De-essing (4-8 kHz)
- [ ] Whisper overlay (-22 dB)
- [ ] Subharmonic layer (-12 dB)
- [ ] Double-voice (-14 dB, 8ms)
- [ ] Room tone (3% wet)
- [ ] Cuddle waves (0.05 Hz, ±1.5 dB)
- [ ] Echo (180ms, 25% decay)

### 3.3 Binaural Generation

- [ ] Binaural track generated
- [ ] Arc follows standard progression:
  - [ ] Pre-Talk: 12→10 Hz
  - [ ] Induction: 10→6 Hz
  - [ ] Journey: 6→1.5 Hz
  - [ ] Integration: 1.5→8 Hz
  - [ ] Closing: 8→12 Hz
- [ ] Duration matches voice track

### 3.4 Sound Effects (if applicable)

- [ ] SFX cues identified from production script
- [ ] SFX generated/sourced
- [ ] SFX track assembled with correct timing

### 3.5 Mixing

- [ ] Stem levels set:
  - [ ] Voice: -6 dB
  - [ ] Binaural: -6 dB
  - [ ] SFX: 0 dB
- [ ] Mix command run:
```bash
ffmpeg -y \
  -i sessions/{name}/output/voice_enhanced.wav \
  -i sessions/{name}/output/binaural_dynamic.wav \
  -filter_complex "[0:a]volume=-6dB[voice];[1:a]volume=-6dB[bin];[voice][bin]amix=inputs=2:duration=longest:normalize=0[mixed]" \
  -map "[mixed]" -acodec pcm_s16le sessions/{name}/output/session_mixed.wav
```
- [ ] Mix verified:
  - [ ] No clipping (peak < 0 dB)
  - [ ] Binaural audible in quiet sections
  - [ ] Voice remains primary

### 3.6 Mastering

- [ ] Mastering applied:
  - [ ] Target LUFS: -14
  - [ ] True peak: -1.5 dBTP
- [ ] Final output created: `final_master.mp3`
- [ ] Level verification:

**Level Check:**
```bash
ffmpeg -i sessions/{name}/output/final_master.mp3 -af "loudnorm=print_format=summary" -f null - 2>&1
```
- Measured LUFS: ______
- Measured True Peak: ______

---

## Phase 4: Video Production (if applicable)

### 4.1 Image Generation

- [ ] Midjourney prompts created
- [ ] Images generated (7-10 images)
- [ ] Images uploaded to `images/uploaded/`

### 4.2 Video Assembly

- [ ] Video assembled with transitions
- [ ] Subtitles generated (VTT)
- [ ] Final video exported

### 4.3 YouTube Package

- [ ] Title prepared
- [ ] Description written
- [ ] Tags selected
- [ ] Chapters defined
- [ ] Thumbnail created

---

## Phase 5: Final Validation

### 5.1 Standards Validation

Run comprehensive validation:
```bash
python3 scripts/utilities/validate_hypnotic_standards.py sessions/{name}
```

**Results:**
- [ ] Manifest: PASS / FAIL
- [ ] Script Sections: PASS / FAIL
- [ ] Script Elements: PASS / FAIL
- [ ] Audio Settings: PASS / FAIL
- [ ] Output Files: PASS / FAIL

Overall Status: [ ] VALID / [ ] INVALID

### 5.2 Listening Review

- [ ] Full session listened through
- [ ] Voice sounds natural (not robotic)
- [ ] Pacing feels hypnotic
- [ ] Binaural is present but subtle
- [ ] SFX timing is correct
- [ ] No audio artifacts or glitches
- [ ] Safe return to full awareness at end

### 5.3 Cross-Session Consistency Check

Compare with previous sessions:
- [ ] Word count is consistent (±20%)
- [ ] Anchor count is consistent (3-5)
- [ ] All 5 senses covered
- [ ] Section timing is consistent
- [ ] Audio quality is consistent

---

## Phase 6: Sign-Off

### 6.1 Quality Approval

**Pre-Production:**
- Manifest Reviewer: _________________ Date: _______
- Approval: [ ] APPROVED / [ ] REVISE

**Script:**
- Script Reviewer: _________________ Date: _______
- Approval: [ ] APPROVED / [ ] REVISE

**Audio:**
- Audio Reviewer: _________________ Date: _______
- Approval: [ ] APPROVED / [ ] REVISE

**Final:**
- Final Reviewer: _________________ Date: _______
- Approval: [ ] APPROVED / [ ] REVISE

### 6.2 Release Checklist

- [ ] All phases completed
- [ ] All validations passed
- [ ] All files in correct locations
- [ ] Session ready for publication

**Final Approval:**

Signature: _________________________
Date: _________________________

---

## Notes & Issues

_Document any issues encountered, deviations from standards, or lessons learned:_

```




```

---

## Quick Reference

### Voice Settings
```
Voice: en-US-Neural2-H
Rate: 1.0 (normal)
Pitch: 0st/-1st/-2st per section
```

### Audio Levels
```
Voice: -6 dB
Binaural: -6 dB
SFX: 0 dB
Final: -14 LUFS, -1.5 dBTP
```

### Enhancement Stack
```
1. Tape warmth (0.25)
2. De-essing
3. Whisper (-22 dB)
4. Subharmonic (-12 dB)
5. Double-voice (-14 dB)
6. Room tone (3%)
7. Cuddle waves (0.05 Hz)
8. Echo (180ms)
```

### Required Anchors
```
- Physical trigger (breathing, hand on heart)
- Symbolic trigger (visualization)
- Sensory trigger (feeling)
Minimum: 3, Maximum: 7
```
