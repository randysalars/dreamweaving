---
name: Full Pipeline
level: advanced
description: End-to-end session creation from topic to YouTube package
---

# Full Pipeline Skill

## Overview
Complete automated workflow from user intent to YouTube-ready package.

## Pipeline Stages

### Stage 1: Initialize
```
/new-session {name}
```
- Creates session directory
- Generates manifest stub

### Stage 2: Configure
```
/generate-manifest {session}
```
- User provides topic, duration, style
- AI generates complete manifest

### Stage 3: Script
```
/generate-script {session}
```
- AI generates SSML script
- Uses master prompt
- Validates output

### Stage 4: Visuals (Manual)
- Visual Artist generates Midjourney prompts
- User creates images on Midjourney
- User uploads to `images/uploaded/`

### Stage 5: Build
```
/build-audio {session}
/build-video {session}
```
- Voice synthesis
- Binaural generation
- Mixing and mastering
- Video assembly
- VTT subtitles

### Stage 6: Package
- YouTube thumbnail
- Description and tags
- Upload guide

## One-Command Option
```
/full-build {session}
```
Runs entire pipeline with pause for images.

## Time Estimate
- AI steps: ~5-10 minutes
- Midjourney: ~15-30 minutes (user)
- Audio build: ~10-15 minutes
- Video build: ~5 minutes
- **Total**: ~35-60 minutes

## Quality Gates
- SSML validation before audio
- Loudness check after audio
- VTT sync verification
- Package completeness check
