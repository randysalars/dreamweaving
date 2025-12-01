---
name: VTT Generation
level: intermediate
description: Generate properly-timed VTT subtitles from SSML
---

# VTT Generation Skill

## Overview
Create WebVTT subtitle files timed to actual audio duration.

## Process

### 1. Parse SSML
- Extract text content
- Identify break tags
- Note prosody settings

### 2. Estimate Timing
- Calculate word duration (WPM)
- Add break durations
- Account for speaking rate

### 3. Scale to Audio
- Get actual audio duration
- Calculate scale factor
- Apply to all timestamps

### 4. Format VTT
```vtt
WEBVTT
Kind: captions
Language: en

1
00:00:00.000 --> 00:00:05.500
Welcome to this healing journey.

2
00:00:06.000 --> 00:00:12.000
Find a comfortable position and
allow your eyes to close.
```

## Key Considerations

### Timing Accuracy
- Parse break tags for pauses
- Scale to actual duration
- Verify key checkpoints

### Readability
- Merge short segments
- Split long lines
- Max 2 lines per caption
- Max ~80 characters per line

### Synchronization
- Match section boundaries
- Align with natural pauses
- Test with video playback

## Command
```bash
python3 scripts/ai/vtt_generator.py sessions/{session}
```

## Output
- `output/subtitles.vtt`
- `output/youtube_package/subtitles.vtt`

## Verification
1. Play video with subtitles
2. Check sync at known points
3. Verify all text included
