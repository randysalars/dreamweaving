---
name: generate-manifest
description: Generate manifest.yaml from session description
arguments:
  - name: session
    required: true
    description: Session name or path
agent: manifest-architect
---

# /generate-manifest Command

Generate a complete manifest.yaml from high-level session description.

## Usage
```
/generate-manifest <session>
```

## Example
```
/generate-manifest inner-child-healing
```

## Process

1. **Gather session details**
   - Topic/theme (required)
   - Target duration (default: 30 minutes)
   - Style (healing, confidence, sleep, spiritual, general)
   - Voice preference (or auto-select)

2. **Apply lessons**
   - Check `knowledge/lessons_learned.yaml`
   - Apply relevant insights for topic/style

3. **Generate configuration**
   - Voice selection based on style
   - Section timings based on duration
   - Binaural frequencies per brainwave targets
   - Mixing and mastering settings
   - YouTube metadata

4. **Validate manifest**
   - Check against schema
   - Verify timing consistency
   - Ensure all required fields

5. **Save manifest**
   - Write to `sessions/{session}/manifest.yaml`
   - Report generation complete

## Generated Sections

### Session Metadata
- Name, topic, duration, style

### Voice Configuration
- Provider, voice ID, rate, pitch

### Section Definitions
- Pre-talk, induction, journey, integration, awakening
- Start/end times, brainwave targets

### Sound Bed
- Binaural frequencies
- Pink noise settings
- Additional layers

### Mixing & Mastering
- Voice LUFS, binaural LUFS
- Sidechain ducking
- Target LUFS, true peak

### YouTube Metadata
- Title, subtitle, description
- Tags, thumbnail settings

## Voice Selection Logic

| Style | Default Voice | Rationale |
|-------|---------------|-----------|
| Healing | en-US-Neural2-A | Warm, nurturing |
| Confidence | en-US-Neural2-D | Authoritative |
| Sleep | en-US-Neural2-C | Soft, gentle |
| Spiritual | en-US-Neural2-E | Deep, resonant |
| General | en-US-Neural2-A | Versatile |

## Dependencies

- Session directory must exist
- Schema at `config/manifest.schema.json`
- Voice config at `config/voice_config.yaml`
