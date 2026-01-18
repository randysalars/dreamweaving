# Handoff Contract Protocol for Dreamweaving

## Purpose

This protocol defines how Dreamweaving agents communicate when passing work from one to another. Following this format ensures context is preserved, creative intent is maintained, and production stages flow smoothly.

## Contract Format

```markdown
[Handoff]
From: <Agent Name>
To: <Agent Name>
Session: <session path>
Stage: <current production stage 1-9>
Timestamp: <ISO 8601 datetime>

## Context
- **Session**: sessions/{session-name}/
- **Manifest**: [key manifest fields relevant to task]
- **Prior Outputs**: [what the sending agent produced]
- **Knowledge Referenced**: [lessons_learned, archetypes, patterns used]

## Task
[Specific, actionable task description]

## Creative Intent
[The emotional/transformational goal to preserve]

## Constraints
- [Safety requirements]
- [Theological boundaries]
- [Technical limitations]

## Exit Criteria
- [ ] [Completion checklist]
- [ ] [Validation requirements]
- [ ] [Output files expected]

## Notes
[Any additional context, warnings, or creative guidance]
```

---

## Production Stage Reference

| Stage | Name | Key Agents |
|-------|------|------------|
| 1 | Creative Design | Dreamweaver, Manifest Architect |
| 2 | Voice Script | Script Writer, Quality Control |
| 3 | Audio Generation | Audio Engineer |
| 4 | Audio Mixing | Audio Engineer |
| 5 | Hypnotic Post-Process | Audio Engineer |
| 5.5 | Scene Images | Visual Artist |
| 6 | Video Production | Video Producer |
| 7 | YouTube Packaging | Video Producer |
| 8 | Cleanup | (automated) |
| 9 | Website Upload | (automated) |

---

## Agent-Specific Handoff Patterns

### Dreamweaver → Manifest Architect

```markdown
[Handoff]
From: Dreamweaver
To: Manifest Architect
Session: sessions/{name}/
Stage: 1

## Context
- **User Request**: [original topic/theme]
- **Duration**: [target minutes]
- **Depth Level**: [Layer 1/2/3/Ipsissimus]
- **Knowledge Referenced**: lessons_learned.yaml, archetypes.yaml

## Task
Generate complete manifest.yaml for this session including:
- Session metadata
- Journey structure (sections with durations)
- Archetype selections
- Binaural beat specifications
- Desired outcome mapping

## Creative Intent
[The transformation the listener should experience]

## Constraints
- Must align with Christian theological boundaries
- Safety sections required (pre_talk, integration)
- Total duration: [X] minutes ± 2 minutes

## Exit Criteria
- [ ] manifest.yaml created and valid
- [ ] All required sections defined
- [ ] Outcome mapped to patterns
```

### Manifest Architect → Script Writer

```markdown
[Handoff]
From: Manifest Architect
To: Script Writer
Session: sessions/{name}/
Stage: 1-2

## Context
- **Manifest**: sessions/{name}/manifest.yaml
- **Journey Structure**: [section breakdown]
- **Archetypes**: [selected archetypes]
- **Desired Outcome**: [from manifest]

## Task
Generate SSML script following:
1. Read manifest for structure and timing
2. Consult hypnotic_patterns.yaml for outcome
3. Apply DVE modules per visualization_level
4. Generate script_production.ssml with SFX markers
5. Generate script_voice_clean.ssml for TTS

## Creative Intent
[Preserve the journey's transformational arc]

## Constraints
- Use rate="1.0" always (pacing via breaks)
- Include safety language in pre_talk
- Complete emergence sequence required
- Agency checkpoints every 3-5 minutes

## Exit Criteria
- [ ] script_production.ssml created
- [ ] script_voice_clean.ssml created (no SFX markers)
- [ ] SSML validates without errors
- [ ] Word count appropriate for duration
```

### Script Writer → Quality Control

```markdown
[Handoff]
From: Script Writer
To: Quality Control
Session: sessions/{name}/
Stage: 2

## Context
- **Scripts**: working_files/script_production.ssml, script_voice_clean.ssml
- **Manifest**: manifest.yaml
- **Desired Outcome**: [from manifest]

## Task
Validate scripts against:
1. SSML syntax validity
2. Safety clause presence
3. NLP pattern requirements for outcome
4. DVE module placement (if applicable)
5. Theological boundary compliance

## Exit Criteria
- [ ] validate_ssml.py passes
- [ ] validate_nlp.py passes (if applicable)
- [ ] All safety sections present
- [ ] Ready for voice generation
```

### Quality Control → Audio Engineer

```markdown
[Handoff]
From: Quality Control
To: Audio Engineer
Session: sessions/{name}/
Stage: 2-3

## Context
- **Script**: working_files/script_voice_clean.ssml (validated)
- **Binaural Spec**: [from manifest]
- **Duration**: [from manifest]

## Task
Generate audio stems:
1. Voice synthesis from script_voice_clean.ssml
2. Binaural beat track per manifest spec
3. SFX track based on script_production.ssml markers
4. Mix all stems with proper levels

## Technical Requirements
- Voice: Coqui TTS (default) or Google Cloud TTS
- Voice level: -6 dB
- Binaural level: -6 dB
- SFX level: 0 dB
- Target: -14 LUFS final master

## Exit Criteria
- [ ] voice_enhanced.mp3 created
- [ ] binaural_dynamic.wav created
- [ ] sfx_track.wav created (if SFX in script)
- [ ] session_mixed.wav created
- [ ] {name}_MASTER.mp3 created
```

### Audio Engineer → Visual Artist

```markdown
[Handoff]
From: Audio Engineer
To: Visual Artist
Session: sessions/{name}/
Stage: 5-5.5

## Context
- **Audio**: {name}_MASTER.mp3 complete
- **Script**: script_production.ssml (for scene timing)
- **Journey Theme**: [from manifest]

## Task
Generate scene images for video:
1. Analyze script for scene breaks
2. Generate SD prompts or Midjourney prompts
3. Create images at 1920x1080
4. Ensure visual coherence across scenes

## Creative Intent
[Visual style that supports the journey's atmosphere]

## Exit Criteria
- [ ] Scene images in images/uploaded/
- [ ] Thumbnail concept ready
- [ ] Visual style consistent
```

### Visual Artist → Video Producer

```markdown
[Handoff]
From: Visual Artist
To: Video Producer
Session: sessions/{name}/
Stage: 5.5-6

## Context
- **Audio**: {name}_MASTER.mp3
- **Images**: images/uploaded/
- **Script**: script_production.ssml (for timing)

## Task
Assemble final video:
1. Generate VTT subtitles from script
2. Assemble video with image transitions
3. Sync audio and subtitles
4. Create YouTube metadata
5. Generate thumbnail

## Technical Requirements
- Resolution: 1920x1080
- Codec: H.264
- Subtitle format: VTT

## Exit Criteria
- [ ] final_video.mp4 created
- [ ] subtitles.vtt created
- [ ] thumbnail.png created
- [ ] metadata.yaml created
- [ ] youtube_package/ complete
```

---

## Rejection Protocol

If a receiving agent cannot complete the task:

```markdown
[Handoff Rejection]
From: <Receiving Agent>
To: <Sending Agent>
Session: <session path>
Reason: <why the task cannot be completed>

## Blockers
- [What's preventing completion]

## Validation Failures
- [Specific errors from validation scripts]

## Suggestions
- [How to fix the issue]
```

---

## Completion Protocol

When work is complete:

```markdown
[Handoff Complete]
From: <Agent Name>
To: <Next Agent or Dreamweaver>
Session: <session path>
Stage: <completed stage>
Status: complete

## Deliverables
- [Files created]
- [Validation results]

## Quality Checks
- [What was verified]

## Ready For
- [Next stage]
```

---

## Cross-Reference with CLAUDE.md

This protocol integrates with:
- **Production Workflow Stages** in CLAUDE.md
- **Serena Memories**: audio_production_methodology, script_production_workflow
- **Knowledge Base**: lessons_learned.yaml, outcome_registry.yaml
- **Validation Scripts**: validate_ssml.py, validate_nlp.py
