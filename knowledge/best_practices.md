# Best Practices - Dreamweaving Production

**Version**: 1.0
**Last Updated**: 2025-12-01
**Status**: Initial - will be auto-updated as lessons accumulate

---

## Content Creation

### Topics & Themes
- Prioritize healing, inner work, and transformation themes
- Story-based journeys typically outperform abstract experiences
- Consider seasonal/timely themes for initial engagement boost

### Duration
- **Standard**: 25-35 minutes (optimal for YouTube retention)
- **Short**: 15-20 minutes (for busy listeners)
- **Extended**: 45-60 minutes (for deep work sessions)

### Script Structure
1. Pre-talk (2-3 min) - Build rapport and set expectations
2. Induction (3-5 min) - Guide into relaxed state
3. Journey (10-20 min) - Main therapeutic content
4. Integration (2-3 min) - Process and anchor
5. Awakening (1-2 min) - Gentle return

---

## Audio Production

### Voice Selection

| Style | Recommended | Rationale |
|-------|-------------|-----------|
| Healing | en-US-Neural2-A | Warm, nurturing |
| Confidence | en-US-Neural2-D | Authoritative |
| Sleep | en-US-Neural2-C | Soft, gentle |
| Spiritual | en-US-Neural2-E | Deep, resonant |

### Speaking Rate
- **Pre-talk**: 1.0 (normal)
- **Induction**: 0.90
- **Journey**: 0.85 (slow, hypnotic)
- **Integration**: 0.85
- **Awakening**: 0.90 → 1.0 (gradual return)

### Binaural Frequencies

| Section | Frequency | Brainwave |
|---------|-----------|-----------|
| Pre-talk | 14 Hz | Beta |
| Induction | 10 Hz | Alpha |
| Journey | 6 Hz | Theta |
| Integration | 8 Hz | Alpha |
| Awakening | 12 Hz | Alpha/Beta |

### Loudness Standards
- Voice: -16 LUFS
- Binaural: -28 LUFS (12dB below voice)
- Final Mix: -14 LUFS (YouTube standard)
- True Peak: -1.5 dBTP max

---

## Quality Assurance

### Pre-Generation
- [ ] SSML validates without errors
- [ ] Manifest passes schema validation
- [ ] All 5 sections defined
- [ ] Duration reasonable (5-60 min)

### Post-Audio
- [ ] Loudness within ±1 LUFS of target
- [ ] True peak under limit
- [ ] Duration within 30s of target
- [ ] No clipping or distortion

### Pre-Publish
- [ ] Video plays correctly
- [ ] VTT subtitles synced
- [ ] Thumbnail compelling
- [ ] Description complete
- [ ] Safety disclaimer included

---

## Engagement Optimization

### Thumbnail
- Clear focal point
- Space for title text
- High contrast for small display
- Evoke curiosity/benefit

### Description
- Hook in first 2 lines
- Include timestamps
- Safety disclaimer
- Relevant hashtags

### Tags
- Primary: hypnosis, guided meditation
- Topic-specific: healing, confidence, sleep, etc.
- Long-tail: specific benefits

---

## Common Issues & Solutions

### SSML Validation Fails
- Run auto-fix: `validate_ssml.py --fix`
- Check for unclosed tags
- Verify break durations < 10s

### Audio Too Loud/Quiet
- Adjust speaking rate if duration wrong
- Re-master with correct target LUFS
- Check input levels

### Video Sync Issues
- Verify audio duration
- Recalculate VTT timing
- Re-mux if needed

---

## Learning Integration

When creating new sessions:
1. Check `lessons_learned.yaml` for relevant insights
2. Apply high-confidence lessons automatically
3. Consider medium-confidence lessons
4. Document which lessons were applied
5. Track outcome for future learning

---

*This document is automatically updated as the Learning Agent discovers new insights from analytics and feedback.*
