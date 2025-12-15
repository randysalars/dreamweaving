# Trigger Maps

> **Purpose:** Map symptoms to search keywords for fast memory retrieval.

---

## How to Use

When you encounter an issue:
1. Find matching symptom category below
2. Use the keywords to search memory and error catalog
3. Commands:
   ```bash
   # Search memory
   rg -n "keyword1|keyword2" .ai/memory/

   # Search error catalog
   python3 scripts/ai/error_router.py "symptom description"

   # Search Serena memories
   # (read relevant memory via Serena tools)
   ```

---

## Audio Issues

| If You See... | Search For... | Serena Memory |
|---------------|---------------|---------------|
| Silent output | `silent`, `volume`, `mix`, `stems`, `-inf` | `audio_production_methodology` |
| Clipping/distortion | `clipping`, `distortion`, `peaks`, `0dB`, `limiter` | `audio_production_methodology` |
| Binaural inaudible | `binaural`, `inaudible`, `beats`, `-12dB` | `audio_production_methodology` |
| Voice thin/harsh | `enhancement`, `warmth`, `voice.mp3`, `raw` | `audio_production_methodology` |
| Sample rate errors | `sample`, `rate`, `48000`, `44100`, `mismatch` | `audio_production_methodology` |
| FFmpeg errors | `ffmpeg`, `encoder`, `codec`, `filter` | - |

---

## SSML/Script Issues

| If You See... | Search For... | Serena Memory |
|---------------|---------------|---------------|
| TTS reads markers | `sfx`, `markers`, `tts`, `reads`, `spoken` | `script_production_workflow` |
| Robotic voice | `rate`, `robotic`, `mechanical`, `slow`, `0.85` | `voice_pacing_guidelines` |
| Validation fails | `ssml`, `xml`, `tag`, `unclosed`, `validation` | `script_production_workflow` |
| Break too long | `break`, `duration`, `10s`, `pause` | `voice_pacing_guidelines` |
| Wrong pitch | `pitch`, `prosody`, `semitone`, `st` | `voice_pacing_guidelines` |

---

## Environment/Build Issues

| If You See... | Search For... | Serena Memory |
|---------------|---------------|---------------|
| Module not found | `venv`, `module`, `import`, `activate` | - |
| Google auth fails | `google`, `auth`, `credentials`, `401`, `403` | - |
| FFmpeg not found | `ffmpeg`, `command`, `not found`, `path` | - |
| Disk full | `disk`, `space`, `storage`, `full` | - |
| Python version | `python`, `version`, `3.8`, `3.10` | - |
| Dependencies | `pip`, `requirements`, `package`, `install` | - |

---

## Video Issues

| If You See... | Search For... | Serena Memory |
|---------------|---------------|---------------|
| A/V sync | `sync`, `timing`, `offset`, `duration` | - |
| Encoding fails | `encoding`, `h264`, `aac`, `codec` | - |
| VTT wrong | `vtt`, `subtitles`, `captions`, `timing` | - |
| Thumbnail | `thumbnail`, `image`, `1280x720` | - |

---

## Session/Manifest Issues

| If You See... | Search For... | Serena Memory |
|---------------|---------------|---------------|
| Missing manifest | `manifest`, `yaml`, `missing`, `not found` | - |
| Invalid manifest | `schema`, `validation`, `required`, `field` | - |
| Wrong structure | `directory`, `structure`, `output`, `working` | `production_workflow_stages` |

---

## Deployment Issues

| If You See... | Search For... | Serena Memory |
|---------------|---------------|---------------|
| Upload fails | `upload`, `deploy`, `api`, `token` | `website_upload_deployment` |
| Website error | `vercel`, `blob`, `website`, `salars` | `website_upload_deployment` |
| Missing files | `package`, `youtube`, `missing`, `required` | `production_workflow_stages` |

---

## Quick Reference: Common Keyword Combinations

```bash
# Silent audio issues
rg -n "silent|volume|stems|mix|-inf" .ai/memory/

# Voice quality issues
rg -n "rate|robotic|enhancement|warmth" .ai/memory/

# Build/environment issues
rg -n "venv|ffmpeg|google|auth" .ai/memory/

# Deployment issues
rg -n "upload|deploy|vercel|website" .ai/memory/
```

---

## Adding New Triggers

When you encounter a new issue pattern:

1. Add symptom → keywords mapping to this file
2. Create memory card in `.ai/memory/`
3. Add to `.claude/error_catalog.yaml` if common
4. Update `.ai/DEBUGGING.md` if significant

Format:
```
| [symptom description] | `keyword1`, `keyword2`, `keyword3` | [serena_memory] |
```
