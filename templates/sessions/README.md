# Session Templates

Pre-configured manifest templates for common hypnotic session types.

## Available Templates

| Template | Theme | Duration | Best For |
|----------|-------|----------|----------|
| `spiritual-journey.yaml` | Spiritual | 30 min | Inner exploration, sacred spaces |
| `nature-sanctuary.yaml` | Nature | 25 min | Grounding, forest/garden themes |
| `cosmic-voyage.yaml` | Cosmic | 35 min | Expansion, space travel |
| `deep-sleep.yaml` | Dreamscape | 45 min | Sleep induction, insomnia |
| `healing-waters.yaml` | Underwater | 28 min | Emotional healing, cleansing |

## Usage

1. **Copy a template to your new session:**
   ```bash
   cp templates/sessions/spiritual-journey.yaml sessions/my-new-session/manifest.yaml
   ```

2. **Customize the manifest:**
   - Update `title` and `description`
   - Adjust `duration` if needed
   - Set your `background` audio path
   - Modify other settings as desired

3. **Create the session structure:**
   ```bash
   ./scripts/utilities/create_new_session.sh "my-new-session"
   ```
   Or manually create:
   ```
   sessions/my-new-session/
   ├── manifest.yaml          # From template
   ├── working_files/
   │   └── script.ssml        # Your SSML script
   ├── images_uploaded/       # Your Midjourney images
   └── output/                # Generated files
   ```

## Template Structure

Each template includes:

- **Basic Info**: Title, description, theme, duration
- **Voice Config**: TTS voice ID, speaking rate, pitch
- **Audio Config**:
  - Binaural beats (frequency, beat rate, volume)
  - Pink noise settings
  - Background audio settings
  - Voice enhancement (warmth, reverb, etc.)
  - Mastering settings
- **Video Config**: Resolution, transitions, timing
- **YouTube Config**: Tags, category, privacy
- **Metadata**: Version, notes, tips

## Customization Tips

### Voice Selection
- `en-US-Neural2-A` - Warm, calming (default for most)
- `en-US-Neural2-C` - Soft, gentle
- `en-US-Neural2-E` - Deep, resonant
- `en-US-Neural2-D` - Deep male voice

### Binaural Frequencies
- **Delta (1-4 Hz)**: Deep sleep
- **Theta (4-8 Hz)**: Meditation, hypnosis
- **Alpha (8-12 Hz)**: Relaxed awareness
- **Beta (12-30 Hz)**: Alert, focused

### Speaking Rate
- `0.75-0.82`: Very slow (sleep, deep trance)
- `0.82-0.90`: Slow (standard hypnosis)
- `0.90-1.0`: Normal pace (lighter content)

## Creating Your Own Template

1. Start with the closest existing template
2. Adjust settings for your specific use case
3. Save to `templates/sessions/your-template.yaml`
4. Add notes in the metadata section
