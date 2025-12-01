# Voice Configuration - Quick Reference

## ⚠️ IMPORTANT: Always Use Ava Voice

**Primary Voice:** `en-US-AvaNeural` (Microsoft Edge TTS)

This is the **mandatory standard** for all Dreamweaving sessions.

---

## Why This Voice?

1. **User Preference** - Specifically chosen for its warm, professional quality
2. **Cost-Effective** - Free via Edge TTS (no API costs like Google Cloud TTS)
3. **Quality** - Excellent natural prosody for meditation and hypnosis
4. **Consistency** - Same voice across all content maintains brand identity

---

## Quick Start

### Generate Voice for a Session:

```bash
# Use the Ava voice generation script
python3 generate_voice_ava.py
```

### Apply Professional Mastering:

```bash
python3 scripts/core/audio/mastering.py working_files/session_ava.wav
```

---

## Configuration Files

1. **Voice Settings:** [config/voice_config.yaml](config/voice_config.yaml)
   - Primary voice configuration
   - Prosody defaults for each section type
   - Audio processing pipeline settings

2. **Workflow Guide:** [docs/VOICE_WORKFLOW.md](docs/VOICE_WORKFLOW.md)
   - Step-by-step voice generation process
   - Prosody guidelines
   - Quality checklist
   - Troubleshooting

3. **Session Template:** [sessions/_template/manifest.yaml](sessions/_template/manifest.yaml)
   - Pre-configured with Ava voice
   - Default prosody settings
   - Ready to use for new sessions

---

## Example: Neural Network Navigator V2

See the complete implementation:
- **Script:** [sessions/neural-network-navigator/generate_voice_v2_ava.py](sessions/neural-network-navigator/generate_voice_v2_ava.py)
- **Output:** V2 enhanced script with Ava voice + professional mastering

This replaced the Google Cloud TTS voice with Ava while keeping all V2 script improvements.

---

## Voice Specifications

**Engine:** Microsoft Edge TTS
**Voice Name:** `en-US-AvaNeural`
**Type:** Neural voice (AI-generated)
**Gender:** Female
**Characteristics:** Warm, professional, calming
**Best For:** Meditation, hypnosis, guided journeys

---

## Prosody Presets

### Pretalk / Closing
- Rate: `1.0` (normal)
- Pitch: `0st` (neutral)

### Induction (Deep Trance)
- Rate: `0.85` (15% slower)
- Pitch: `-2st` (lower)

### Journey (Immersion)
- Rate: `0.91` (9% slower)
- Pitch: `-1st` (slightly lower)

### Awakening (Gentle Return)
- Rate: `0.95` (5% slower)
- Pitch: `0st` (neutral)

---

## Don't Use These Voices

❌ `en-US-Neural2-A` (Google Cloud - used in old V2, now replaced)
❌ `en-US-JennyNeural` (Edge TTS alternative - not our standard)
❌ Any other voice unless specifically discussed and approved

---

## Questions?

See full documentation:
- [VOICE_WORKFLOW.md](docs/VOICE_WORKFLOW.md) - Complete workflow guide
- [voice_config.yaml](config/voice_config.yaml) - Technical configuration
- [AUTOMATION_STATUS.md](AUTOMATION_STATUS.md) - Project status

---

**Remember:** Consistency is key. Always use `en-US-AvaNeural` for all sessions.
