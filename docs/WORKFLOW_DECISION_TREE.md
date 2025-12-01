# Workflow Decision Tree

**VERSION:** 1.0
**LAST UPDATED:** 2025-11-28
**PURPOSE:** Help users choose the right workflow for their needs

---

## Quick Decision Guide

**START HERE:** Answer these questions to find your workflow.

```
┌─────────────────────────────────────┐
│ What do you want to create?         │
└──────────────┬──────────────────────┘
               │
               ├── Basic hypnotic audio session
               │   │
               │   └──> Use CANONICAL_WORKFLOW.md
               │       • Voice generation only
               │       • Standard mastering
               │       • Ready in 5-10 minutes
               │
               ├── Enhanced audio with binaural beats
               │   │
               │   ├── Is this an existing session?
               │   │   │
               │   │   ├── Yes → Which session?
               │   │   │   │
               │   │   │   ├── Neural Network Navigator
               │   │   │   │   └──> sessions/neural-network-navigator/
               │   │   │   │       • PRODUCTION_WORKFLOW.md (quick)
               │   │   │   │       • PRODUCTION_MANUAL_V2.md (complete)
               │   │   │   │
               │   │   │   └── Garden of Eden
               │   │   │       └──> sessions/garden-of-eden/
               │   │   │           • AUDIO_PRODUCTION_README.md
               │   │   │
               │   │   └── No → New session
               │   │       └──> 1. CANONICAL_WORKFLOW.md (voice)
               │   │            2. Adapt session-specific scripts
               │   │
               │   │
               └── Video production with images
                   │
                   ├── Is this an existing session?
                   │   │
                   │   ├── Yes → Which session?
                   │   │   │
                   │   │   ├── Neural Network Navigator
                   │   │   │   └──> sessions/neural-network-navigator/
                   │   │   │       • PRODUCTION_MANUAL_V2.md (complete)
                   │   │   │       • create_final_v2_ava.py
                   │   │   │
                   │   │   └── Garden of Eden
                   │   │       └──> sessions/garden-of-eden/
                   │   │           • PRODUCTION_MANUAL.md (complete)
                   │   │           • create_final_video.sh
                   │   │
                   │   └── No → New session
                   │       └──> 1. CANONICAL_WORKFLOW.md (voice)
                   │            2. Create custom video script
                   │            3. Reference session examples
```

---

## Detailed Decision Paths

### Path 1: Basic Hypnotic Audio

**Best for:**
- Quick session creation
- First-time users
- Standard meditation/hypnosis
- No special audio effects needed

**Workflow:**
1. **Read:** [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
2. **Create session:** `./scripts/utilities/create_new_session.sh "session-name"`
3. **Write SSML script:** `sessions/session-name/script.ssml`
4. **Generate voice:** Google Cloud TTS via `generate_audio_chunked.py`
5. **Apply mastering:** FFmpeg with loudnorm filter
6. **Done!** Production-ready audio in 10-15 minutes

**Time:** 10-15 minutes (after script written)
**Complexity:** ⭐ Easy
**Output:** Professional voice audio, mastered

---

### Path 2: Enhanced Audio (Ultimate Mix)

**Best for:**
- Meditation with binaural beats
- Brainwave entrainment
- Multi-layer soundscapes
- Professional releases

**Workflow:**

#### Option A: Existing Session (Neural Network Navigator)

**Quick (3 commands):**
1. **Read:** `sessions/neural-network-navigator/PRODUCTION_WORKFLOW.md`
2. **Generate voice:** `python3 generate_voice_v2_ava.py`
3. **Create ultimate mix:** `./create_ultimate_audio.sh`
4. **Done!** 9-layer mix with binaural beats

**Time:** 20-30 minutes
**Complexity:** ⭐⭐ Moderate
**Output:** Voice + binaural + effects + ambient pad

**Complete (Full control):**
1. **Read:** `sessions/neural-network-navigator/PRODUCTION_MANUAL_V2.md`
2. Follow complete phase-by-phase instructions
3. Customize audio layers as needed

**Time:** 30-45 minutes
**Complexity:** ⭐⭐⭐ Advanced
**Output:** Full professional production

#### Option B: Existing Session (Garden of Eden)

1. **Read:** `sessions/garden-of-eden/AUDIO_PRODUCTION_README.md`
2. **Generate voice:** Via CANONICAL_WORKFLOW.md
3. **Generate binaural:** `python generate_binaural_beats.py`
4. **Mix audio:** `python mix_audio.py`
5. **Optional:** Add nature sounds

**Time:** 25-35 minutes
**Complexity:** ⭐⭐ Moderate
**Output:** Voice + binaural + optional nature

#### Option C: New Session (Custom)

1. **Generate voice:** Follow CANONICAL_WORKFLOW.md
2. **Study examples:**
   - `sessions/neural-network-navigator/create_ultimate_audio.sh`
   - `sessions/garden-of-eden/create_ultimate_audio.sh`
3. **Adapt scripts:**
   - Copy and modify for your session
   - Adjust timings, frequencies, layers
4. **Document your process:**
   - Create session-specific README
   - Note timings and specifications

**Time:** 1-2 hours (first time)
**Complexity:** ⭐⭐⭐ Advanced
**Output:** Custom ultimate mix

---

### Path 3: Video Production

**Best for:**
- YouTube uploads
- Visual meditation sessions
- Professional distribution
- Sessions with imagery

**Workflow:**

#### Option A: Neural Network Navigator

**Quick:**
1. **Read:** `sessions/neural-network-navigator/PRODUCTION_WORKFLOW.md`
2. **Voice + Ultimate mix:** (See Path 2)
3. **Create video:** `python3 create_final_v2_ava.py`
4. **Done!** 28.7-minute video with 8 scenes

**Time:** 40-60 minutes total
**Complexity:** ⭐⭐⭐ Advanced
**Output:** 1080p MP4 with timed image transitions

**Complete:**
1. **Read:** `sessions/neural-network-navigator/PRODUCTION_MANUAL_V2.md`
2. Follow complete workflow with verification
3. Quality control checks at each phase

**Time:** 60-90 minutes
**Complexity:** ⭐⭐⭐⭐ Expert
**Output:** Broadcast-ready video

#### Option B: Garden of Eden

1. **Read:** `sessions/garden-of-eden/PRODUCTION_MANUAL.md`
2. **Generate images:** (External - Stable Diffusion, etc.)
3. **Create gradient backgrounds:** `python generate_video_background.py`
4. **Composite images:** `python composite_images.py`
5. **Add titles:** Via `create_final_video.sh`
6. **Mix with audio:** Final assembly

**Time:** 90-120 minutes (includes image generation)
**Complexity:** ⭐⭐⭐⭐ Expert
**Output:** Complete 25-minute meditation video

#### Option C: New Session (Custom Video)

1. **Voice generation:** Follow CANONICAL_WORKFLOW.md
2. **Plan video structure:**
   - How many scenes?
   - What duration per scene?
   - What transitions?
3. **Generate/prepare images:**
   - 1920x1080 resolution
   - One per major section
   - Consistent style
4. **Study examples:**
   - Neural Network Navigator: Fixed 8 scenes
   - Garden of Eden: 7 scenes with gradient backgrounds
5. **Create custom video script:**
   - FFmpeg-based composition
   - Timed image overlays
   - Audio sync
6. **Document your process**

**Time:** 2-3 hours (first time)
**Complexity:** ⭐⭐⭐⭐⭐ Expert
**Output:** Custom video production

---

## Comparison Matrix

| Feature | Basic Audio | Enhanced Audio | Video Production |
|---------|-------------|----------------|------------------|
| **Time Required** | 10-15 min | 20-45 min | 60-120 min |
| **Complexity** | ⭐ Easy | ⭐⭐ Moderate | ⭐⭐⭐⭐ Expert |
| **Voice Generation** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Mastering** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Binaural Beats** | ❌ No | ✅ Yes | ✅ Yes |
| **Sound Effects** | ❌ No | ✅ Optional | ✅ Optional |
| **Ambient Pad** | ❌ No | ✅ Optional | ✅ Optional |
| **Visual Elements** | ❌ No | ❌ No | ✅ Yes |
| **YouTube Ready** | ⚠️ Audio only | ⚠️ Audio only | ✅ Full video |
| **Best For** | Quick sessions | Meditation | Professional distribution |

---

## Special Scenarios

### Scenario: "I just want to test my script"

**Recommended:** Basic Audio (Path 1)
1. Follow CANONICAL_WORKFLOW.md quick start
2. Generate voice only
3. Skip mastering for now
4. Listen and iterate

**Why:** Fastest way to hear your script (2-5 minutes)

---

### Scenario: "I want to create a meditation for YouTube"

**Recommended:** Enhanced Audio + Video (Path 2 + Path 3)
1. Write script following hypnotic template
2. Generate voice via CANONICAL_WORKFLOW.md
3. Choose session example closest to your needs:
   - Neural Network Navigator (professional format)
   - Garden of Eden (visual meditation)
4. Adapt scripts for your session
5. Create ultimate mix with binaural beats
6. Generate or commission images
7. Produce video following example workflow

**Why:** YouTube requires video, binaural enhances meditation

**Time:** 3-4 hours total (first session)

---

### Scenario: "I'm creating a series of sessions"

**Recommended:**
1. **First session:** Use complete workflow (Path 1 or 2)
2. **Template your process:**
   - Document your specific steps
   - Create reusable scripts
   - Note your preferences (voice, mastering settings, etc.)
3. **Subsequent sessions:** Use your template
4. **Batch processing:** Use `scripts/utilities/batch_generate.py`

**Why:** Investment in templating pays off over multiple sessions

---

### Scenario: "I need professional quality for sale"

**Recommended:** Complete Enhanced Audio + Video (Path 2 + 3 Complete)
1. Professional voice generation (CANONICAL_WORKFLOW.md)
2. Ultimate mix with all enhancements
3. Professional video production
4. Multiple quality control passes
5. Multiple format exports

**Follow:**
- `sessions/neural-network-navigator/PRODUCTION_MANUAL_V2.md`
- Complete quality checklists
- Professional specifications

**Why:** Sale requires highest quality standards

**Time:** 4-6 hours per session

---

## Troubleshooting Your Choice

### "I'm not sure which path to choose"

**Answer these questions:**

1. **Do you need video?**
   - No → Path 1 or Path 2
   - Yes → Path 3

2. **Do you need binaural beats?**
   - No → Path 1
   - Yes → Path 2 or Path 3

3. **Is this an existing session?**
   - Neural Network Navigator → Use session docs
   - Garden of Eden → Use session docs
   - New session → Follow canonical, then adapt examples

4. **What's your experience level?**
   - Beginner → Path 1 (basic audio)
   - Intermediate → Path 2 (enhanced audio)
   - Advanced → Path 3 (video production)

5. **How much time do you have?**
   - 15 minutes → Path 1
   - 45 minutes → Path 2
   - 2 hours → Path 3

---

### "The workflow seems too complex"

**Start simpler:**
1. Begin with Path 1 (Basic Audio)
2. Master that process
3. Graduate to Path 2 (Enhanced Audio)
4. Finally attempt Path 3 (Video)

**Don't skip steps!** Each path builds on the previous one.

---

### "I followed the wrong workflow"

**Common scenarios:**

**Generated voice with Edge TTS instead of Google Cloud:**
- Not ideal but workable
- Consider regenerating for consistency
- For future: Follow CANONICAL_WORKFLOW.md

**Didn't apply mastering:**
- Generate mastered version now using canonical workflow
- Always master before ultimate mix

**Created duplicate scripts:**
- Use session-specific scripts only
- Refer to WORKFLOW_MAINTENANCE_GUIDE.md
- Follow canonical workflow for base steps

---

## Workflow Evolution Path

### Level 1: Beginner
- **Focus:** Basic audio generation
- **Workflow:** CANONICAL_WORKFLOW.md
- **Goal:** Understand voice generation and mastering
- **Time:** 1-2 sessions

### Level 2: Intermediate
- **Focus:** Enhanced audio with binaural beats
- **Workflow:** Session-specific ultimate mix
- **Goal:** Multi-layer audio production
- **Time:** 3-5 sessions

### Level 3: Advanced
- **Focus:** Complete video production
- **Workflow:** Full production manuals
- **Goal:** Professional YouTube releases
- **Time:** 5-10 sessions

### Level 4: Expert
- **Focus:** Custom workflows and automation
- **Workflow:** Custom scripts and templates
- **Goal:** Efficient series production
- **Time:** 10+ sessions

---

## Quick Reference Card

**Print or bookmark this section for quick decisions:**

| I want to... | Use this workflow | Read this doc |
|--------------|-------------------|---------------|
| Create my first session | Basic Audio | CANONICAL_WORKFLOW.md |
| Add binaural beats | Enhanced Audio | Session AUDIO_PRODUCTION docs |
| Make a YouTube video | Video Production | Session PRODUCTION_MANUAL docs |
| Recreate Neural Navigator | Session-Specific | neural-network-navigator/PRODUCTION_WORKFLOW.md |
| Recreate Garden of Eden | Session-Specific | garden-of-eden/AUDIO_PRODUCTION_README.md |
| Learn the official method | Universal | CANONICAL_WORKFLOW.md |
| Understand terminology | Reference | TERMINOLOGY_GUIDE.md |
| Maintain workflows | Reference | WORKFLOW_MAINTENANCE_GUIDE.md |

---

## Still Stuck?

1. **Start here:** [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
2. **Check:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Review:** This decision tree again
4. **Study:** Existing session examples
5. **Experiment:** Start simple, add complexity gradually

**Remember:** Every expert started with basic audio generation. Don't rush the learning process.

---

**Last Updated:** 2025-11-28
**Version:** 1.0
**Next Review:** 2026-11-28

---

*Choose the right workflow for your needs, then master it.*
