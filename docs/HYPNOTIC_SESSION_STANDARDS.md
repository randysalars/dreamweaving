# Hypnotic Session Production Standards

## Overview

This document defines the **mandatory standards** for all hypnotic video sessions produced by the Sacred Digital Dreamweaver system. Every session MUST conform to these specifications to ensure therapeutic integrity, professional quality, and consistent user experience.

---

## 1. Mandatory Session Sections (5 Required)

Every hypnotic session MUST contain exactly these 5 sections in order:

| # | Section | Duration | Purpose | Brainwave Target |
|---|---------|----------|---------|------------------|
| 1 | **Pre-Talk** | 2-3 min | Welcome, safety, preparation | Alpha (8-12 Hz) |
| 2 | **Induction** | 3-5 min | Progressive relaxation, trance entry | Alpha → Theta |
| 3 | **Main Journey** | 10-20 min | Core transformation experience | Theta (4-7 Hz) / Delta (1-4 Hz) |
| 4 | **Integration & Return** | 2-3 min | Process insights, ascending return | Theta → Alpha |
| 5 | **Post-Hypnotic & Closing** | 2-3 min | Install anchors, closing message | Alpha (8-12 Hz) |

### Section Markers

Each section MUST be marked with XML comments in the SSML script:

```xml
<!-- SECTION 1: PRE-TALK -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Welcome, safety, preparation -->

<!-- SECTION 2: INDUCTION -->
<!-- Duration: 3-5 minutes -->
<!-- Purpose: Progressive relaxation, trance induction -->

<!-- SECTION 3: MAIN JOURNEY -->
<!-- Duration: 10-20 minutes -->
<!-- Purpose: Core transformation experience -->

<!-- SECTION 4: INTEGRATION AND RETURN -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Process insights, return to awareness -->

<!-- SECTION 5: POST-HYPNOTIC ANCHORS AND CLOSING -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Install anchors, closing message -->
```

---

## 2. Mandatory Script Elements

### 2.1 Pre-Talk Requirements (ALL MUST BE PRESENT)

| Element | Description | Example |
|---------|-------------|---------|
| **Introduction** | Identify as Sacred Digital Dreamweaver | "I am The Sacred Digital Dreamweaver..." |
| **Session Purpose** | Clear statement of session goal | "Today we journey to cultivate inner discipline..." |
| **Safety Reassurance** | Full control statement | "You remain fully aware and in control..." |
| **Preparation Instructions** | Setup guidance | "Find a comfortable position, wear headphones..." |
| **Consent Cue** | Permission to begin | "When you're ready, we begin..." |

### 2.2 Induction Requirements (ALL MUST BE PRESENT)

| Element | Description | Minimum Count |
|---------|-------------|---------------|
| **Progressive Relaxation** | Body scan or tension release | 1 complete sequence |
| **Breathing Cues** | Rhythmic breath guidance | 3+ breath cycles |
| **Countdown** | Numeric deepening | 1 countdown (10→1 or similar) |
| **Deepening Suggestions** | "Deeper and deeper" language | 5+ deepening phrases |

### 2.3 Main Journey Requirements

| Element | Description | Minimum Count |
|---------|-------------|---------------|
| **Setting Establishment** | Environment description | 1 vivid scene |
| **All 5 Senses** | Sensory engagement | Each sense addressed |
| **Archetypal Elements** | Symbolic figures/objects | 1+ archetype |
| **Therapeutic Core** | Goal-specific suggestions | 3+ embedded commands |
| **Peak/Climax Moment** | Transformation point | 1 clear moment |

### 2.4 Integration Requirements

| Element | Description | Minimum Count |
|---------|-------------|---------------|
| **Ascending Count** | Return countdown | 1 count (1→5 or 1→10) |
| **Grounding Cues** | Physical awareness | 3+ body references |
| **Insight Anchoring** | "Bringing back..." language | 2+ integration phrases |

### 2.5 Post-Hypnotic Requirements (ALL MUST BE PRESENT)

| Element | Description | Minimum Count |
|---------|-------------|---------------|
| **Anchors** | Trigger-linked suggestions | 3-5 specific anchors |
| **Future Pacing** | "In the days ahead..." | 2+ future references |
| **Thank You** | Gratitude expression | 1 thank you |
| **Call to Action** | Like/Subscribe mention | 1 CTA |
| **Closing Blessing** | Positive farewell | 1 blessing |

---

## 3. Audio Production Standards

### 3.1 Voice Settings (MANDATORY)

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Voice** | `en-US-Neural2-H` | Production standard |
| **SSML Rate** | `rate="1.0"` | NEVER slower |
| **Pitch by Section** | See table below | Match section type |
| **Pacing** | `<break>` tags | NOT rate adjustment |

**Pitch Settings by Section:**
```
Pre-Talk:      pitch="0st"   (normal, grounded)
Induction:     pitch="-2st"  (deeper, calming)
Journey:       pitch="-1st"  (slightly deeper)
Integration:   pitch="-1st"  (maintaining depth)
Closing:       pitch="0st"   (grounded, alert)
```

### 3.2 Break Duration Standards

| Context | Duration | Example |
|---------|----------|---------|
| Between phrases | 700ms-1.0s | `word, <break time="700ms"/> next` |
| After sentences | 1.0s-1.7s | `sentence. <break time="1.3s"/>` |
| Breathing cues | 2.0s-3.0s | `Breathe in... <break time="3.0s"/>` |
| Visualization | 3.0s-4.0s | `See it clearly. <break time="3.5s"/>` |
| Major transitions | 4.0s-5.5s | `You have arrived. <break time="5.5s"/>` |

### 3.3 Binaural Beat Progression (MANDATORY)

Every session MUST follow this arc pattern:

```
Pre-Talk:    12 Hz → 10 Hz  (alpha, alert receptive)
Induction:   10 Hz → 6 Hz   (alpha to theta)
Journey:     6 Hz → 1.5 Hz  (theta to delta)
Integration: 1.5 Hz → 8 Hz  (ascending)
Closing:     8 Hz → 12 Hz   (return to alert)
```

**Optional Enhancement:** Gamma burst (40 Hz, 3 seconds) at peak transformation moment.

### 3.4 Audio Mixing Levels (MANDATORY)

| Stem | Level | Notes |
|------|-------|-------|
| Voice | -6 dB | Primary element |
| Binaural | -6 dB | Subtle but present |
| SFX | 0 dB | Punctuating moments |

### 3.5 Voice Enhancement (MANDATORY)

All voice audio MUST include these post-processing elements:

| Enhancement | Setting | Purpose |
|-------------|---------|---------|
| **Tape Warmth** | 0.25 drive | Analog character |
| **De-essing** | 4-8 kHz reduction | Soften sibilants |
| **Whisper Overlay** | -22 dB | Ethereal presence (Layer 2) |
| **Subharmonic Layer** | -12 dB | Grounding warmth (Layer 3) |
| **Double-Voice** | -14 dB, 8ms delay | Subliminal depth |
| **Room Tone** | 3% wet | Physical presence |
| **Cuddle Waves** | 0.05 Hz, ±1.5 dB | Gentle modulation |
| **Echo** | 180ms, 25% decay | Dreamy spaciousness |

### 3.6 Mastering Standards

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Target LUFS** | -14 LUFS | YouTube standard |
| **True Peak** | -1.5 dBTP | Safe headroom |
| **Sample Rate** | 48000 Hz | All stems |
| **Output Format** | WAV + MP3 (320kbps) | Archival + distribution |

---

## 4. File Structure Standards

Every session MUST follow this directory structure:

```
sessions/{session-name}/
├── manifest.yaml              # REQUIRED: Session configuration
├── script.ssml                # Production script (with SFX markers)
├── notes.md                   # Design notes, archetypes
├── midjourney-prompts.md      # Image generation prompts
├── working_files/
│   ├── script_production.ssml # Full script with SFX cues
│   ├── script_voice_clean.ssml # Clean script for TTS
│   ├── stems/                  # Individual audio tracks
│   └── *.wav/*.mp3             # Working audio files
├── images/
│   └── uploaded/              # Midjourney images (PNG)
└── output/
    ├── voice.mp3              # Raw TTS
    ├── voice_enhanced.mp3     # Enhanced voice (USE THIS)
    ├── binaural_dynamic.wav   # Binaural track
    ├── sfx_track.wav          # Sound effects
    ├── session_mixed.wav      # Mixed session
    ├── final_master.mp3       # Final output
    └── youtube_package/       # YouTube deliverables
```

---

## 5. Manifest Required Fields

Every `manifest.yaml` MUST contain:

```yaml
session:
  name: "session-name"          # REQUIRED: Kebab-case identifier
  topic: "Session Title"        # REQUIRED: Full title
  duration: 1800                # REQUIRED: Target seconds
  style: "deep_journey"         # REQUIRED: Session type
  created: "YYYY-MM-DD"         # REQUIRED: Creation date
  skill: "Skill Name"           # REQUIRED: Skill/transformation goal
  skill_description: "..."      # REQUIRED: What listener gains

voice:
  provider: "google-cloud-tts"  # REQUIRED
  voice_name: "en-US-Neural2-H" # REQUIRED: Production voice
  rate: 1.0                     # REQUIRED: Normal rate
  pitch: "0st"                  # REQUIRED: Base pitch

sections:                       # REQUIRED: All 5 sections defined
  - name: "pretalk"
    start: 0
    end: 180
    brainwave_target: "alpha"
  - name: "induction"
    start: 180
    end: 480
    brainwave_target: "theta"
  - name: "journey"
    start: 480
    end: 1320
    brainwave_target: "delta"
  - name: "integration"
    start: 1320
    end: 1500
    brainwave_target: "theta"
  - name: "closing"
    start: 1500
    end: 1800
    brainwave_target: "alpha"

sound_bed:
  binaural:
    enabled: true               # REQUIRED
    base_hz: 200                # REQUIRED: Carrier frequency

voice_enhancement:
  enabled: true                 # REQUIRED
  warmth_drive: 0.25
  deessing: true
  whisper_overlay: true
  subharmonic: true
  double_voice: true
  room_tone: true
  cuddle_waves: true
  echo: true                    # NEW: Echo effect
```

---

## 6. Quality Benchmarks

### 6.1 Script Quality

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| Word count | ~3,750 words | 3,200-4,200 words |
| Duration | 25-30 min | 20-35 min |
| Embedded commands | 15+ | 10-25 |
| Sensory descriptions | All 5 senses | Minimum 4 |
| Anchors | 3-5 | 3-7 |

### 6.2 Audio Quality

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| Voice clarity | Clear, warm | No clipping/distortion |
| Binaural audibility | Subtle but present | Audible in quiet sections |
| Peak level | -3 dB | -6 to -1 dB |
| RMS level | -18 dB | -22 to -14 dB |
| Final LUFS | -14 LUFS | -16 to -12 LUFS |

### 6.3 Timing Consistency

| Transition | Timing | Notes |
|------------|--------|-------|
| Section markers | Within 10 seconds of target | Match manifest |
| Binaural transitions | Smooth, 30-60 second ramps | No sudden changes |
| SFX timing | Within 2 seconds of script cue | Sync to narrative |

---

## 7. Prohibited Elements

### 7.1 NEVER Include

- Negative suggestions ("You won't feel pain")
- Fear-based imagery
- Clinical/medical language
- Rushed transitions
- Incomplete returns (must fully awaken)
- Coercive language
- Rate values below 1.0 in SSML

### 7.2 NEVER Omit

- Safety reassurance in pre-talk
- Full body grounding in return
- At least 3 anchors
- Thank you/closing blessing
- All 5 section markers

---

## 8. Validation Checkpoints

### 8.1 Pre-Production Checklist

- [ ] Manifest contains all required fields
- [ ] Session name follows kebab-case convention
- [ ] Duration target is realistic (20-35 min)
- [ ] All 5 sections defined with timing
- [ ] Skill/transformation goal is specific

### 8.2 Script Checklist

- [ ] All 5 section markers present
- [ ] Pre-talk includes all 5 elements
- [ ] Induction includes all 4 elements
- [ ] Main journey engages all 5 senses
- [ ] 3-5 anchors in post-hypnotic section
- [ ] Word count in range (3,200-4,200)
- [ ] SSML uses `rate="1.0"` throughout
- [ ] Break durations follow standards

### 8.3 Audio Production Checklist

- [ ] Voice uses `en-US-Neural2-H`
- [ ] Voice enhancement applied (all 8 layers)
- [ ] Binaural follows standard arc
- [ ] Mix levels correct (-6/-6/0 dB)
- [ ] No clipping (peak < 0 dB)
- [ ] Final master at -14 LUFS
- [ ] Echo effect applied

### 8.4 Final Delivery Checklist

- [ ] All output files present
- [ ] YouTube package complete
- [ ] VTT subtitles generated
- [ ] Thumbnail created
- [ ] Description written

---

## 9. Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-02 | Initial standards document |

---

## Quick Reference Card

```
MANDATORY ELEMENTS PER SESSION
==============================

SECTIONS (5):
  [1] Pre-Talk (2-3 min) - Intro, safety, prep
  [2] Induction (3-5 min) - Relaxation, countdown
  [3] Journey (10-20 min) - Core experience
  [4] Integration (2-3 min) - Return count
  [5] Closing (2-3 min) - Anchors, blessing

VOICE:
  - Voice: en-US-Neural2-H
  - Rate: 1.0 (normal)
  - Pacing: <break> tags only

AUDIO:
  - Binaural: 12→6→1.5→8→12 Hz arc
  - Levels: Voice -6dB, Binaural -6dB, SFX 0dB
  - Enhancement: All 8 layers + echo

MASTERING:
  - LUFS: -14
  - True Peak: -1.5 dBTP
  - Format: WAV + MP3 320kbps
```
