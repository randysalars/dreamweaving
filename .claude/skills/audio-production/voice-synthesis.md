---
name: Voice Synthesis
level: basic
description: Generate voice audio using Google Cloud TTS
---

# Voice Synthesis Skill

## Overview
Convert SSML script to voice audio using Google Cloud Text-to-Speech.

## Prerequisites
- Google Cloud credentials configured
- Virtual environment activated
- Valid SSML script

## Command
```bash
python3 scripts/core/generate_audio_chunked.py \
    sessions/{session}/working_files/script.ssml \
    sessions/{session}/output/voice.mp3 \
    {voice_id}
```

## Voice Options

### Female (Recommended for Hypnosis)
- `en-US-Neural2-A` - Warm, calming (default)
- `en-US-Neural2-C` - Soft, gentle
- `en-US-Neural2-E` - Deep, resonant
- `en-US-Neural2-F` - Clear, articulate

### Male
- `en-US-Neural2-D` - Deep, authoritative
- `en-US-Neural2-I` - Warm, compassionate
- `en-US-Neural2-J` - Rich, mature

## Chunking

Large scripts are automatically chunked:
- Splits at natural break points
- Stays under API byte limits
- Concatenates final output

## Duration Adjustment

If duration doesn't match target:
1. Adjust `speaking_rate` in manifest
2. Regenerate voice audio
3. Rate range: 0.75 - 1.25

## Output
- `output/voice.mp3` - Voice-only audio
- Duration logged to console
