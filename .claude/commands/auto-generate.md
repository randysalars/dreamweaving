# Auto-Generate Session

Fully automated video generation from topic to YouTube-ready package.

## Usage

```
/auto-generate "<topic>" [--duration 25] [--style healing] [--mode standard]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `topic` | Yes | - | The session topic in quotes |
| `--duration` | No | 25 | Target duration in minutes |
| `--style` | No | healing | Session style (see below) |
| `--mode` | No | standard | Cost optimization mode |

### Styles

| Style | Best For |
|-------|----------|
| `healing` | Restoration, wellness, inner peace |
| `confidence` | Self-esteem, empowerment, strength |
| `spiritual` | Divine connection, higher guidance |
| `sleep` | Deep rest, relaxation, insomnia |
| `custom` | Unique themes (provide more detail in topic) |

### Modes

| Mode | AI Cost | Total | Use Case |
|------|---------|-------|----------|
| `budget` | ~$0.55 | ~$0.70 | Bulk production, testing |
| `standard` | ~$0.91 | ~$1.06 | Production (recommended) |
| `premium` | ~$1.36 | ~$1.51 | High-stakes releases |

## What It Does

Complete pipeline from topic to YouTube-ready video:

1. **Initialize** - Creates session directory, manifest, journey concept
2. **Script** - Generates SSML script with all 8 sections
3. **Audio** - Voice synthesis (Google TTS), binaural beats, SFX
4. **Mix & Master** - FFmpeg mixing + hypnotic post-processing
5. **Images** - Scene images via Stable Diffusion
6. **Video** - Assembles video, generates VTT subtitles
7. **YouTube** - Creates metadata, thumbnail, packages for upload
8. **Validate** - Quality checks (+ Opus QA review in premium mode)

## Output

```
sessions/{generated-name}/output/youtube_package/
├── final_video.mp4      # 1920x1080, H.264
├── thumbnail.png        # 1280x720
├── metadata.yaml        # Title, description, tags, chapters
├── subtitles.vtt        # Timed captions
└── cost_report.json     # Actual costs tracked
```

## Examples

### Basic Usage

```
/auto-generate "Finding Inner Peace Through Nature"
```

### With Options

```
/auto-generate "Building Unshakeable Confidence" --duration 30 --style confidence
```

### Premium Quality

```
/auto-generate "Connecting with Divine Light" --mode premium --style spiritual
```

### Budget Batch Testing

```
/auto-generate "Quick Test Session" --duration 15 --mode budget
```

## Execution

When you run this command, Claude will:

1. Parse your topic and options
2. Execute the auto_generate.py orchestrator
3. Monitor progress through all 7 phases
4. Report results with cost breakdown
5. Provide path to YouTube-ready package

## Batch Generation

For multiple sessions, use the batch generator directly:

```bash
python3 scripts/ai/batch_generate.py --topics-file topics.yaml --mode standard
```

Create a `topics.yaml` file:

```yaml
sessions:
  - topic: "Finding Inner Peace Through Nature"
    duration: 25
    style: healing
  - topic: "Building Confidence"
    duration: 30
    style: confidence
  - topic: "Deep Restorative Sleep"
    duration: 35
    style: sleep
```

## Cost Breakdown

### Standard Mode (~$1.06/session)

| Phase | Tier | Cost |
|-------|------|------|
| Journey Concept | Opus | $0.26 |
| Script Sections | Sonnet/Opus | $0.47 |
| Audio Config | Haiku | $0.002 |
| Image Prompts | Sonnet | $0.05 |
| YouTube Package | Sonnet | $0.07 |
| Validation | Haiku | $0.002 |
| **AI Total** | | **$0.91** |
| Google TTS | External | $0.15 |
| **Total** | | **$1.06** |

## Troubleshooting

### API Key Issues

Ensure environment variables are set:

```bash
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### Generation Failed

Check the error message and:

1. Verify topic is descriptive enough
2. Check API rate limits
3. Review `cost_report.json` for which step failed

### Quality Issues

- Use `--mode premium` for important sessions
- Review and manually refine the generated script
- Re-run specific steps if needed

## Related Commands

| Command | Description |
|---------|-------------|
| `/full-build <session>` | Build existing session |
| `/generate-script <session>` | Generate script only |
| `/build-audio <session>` | Build audio only |
| `/validate <session>` | Validate session |
