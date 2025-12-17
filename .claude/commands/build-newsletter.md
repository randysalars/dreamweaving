# Build Newsletter Campaign

Generate an email newsletter from Dreamweaving sessions.

## Usage

```
/build-newsletter [--type <type>] [--sessions <list>] [--theme <theme>] [--save]
```

## Arguments

- `--type`: Newsletter type (default: weekly)
  - `weekly`: Weekly digest of recent sessions
  - `new_release`: Single session announcement
  - `theme`: Themed collection of sessions
- `--sessions`: Comma-separated list of session names (for new_release or theme)
- `--theme`: Theme name for themed newsletters (e.g., "Shadow Work", "Cosmic Journeys")
- `--save`: Save the newsletter to `output/newsletters/`

## Process

1. Collect sessions based on type:
   - Weekly: Last 7 days of sessions
   - New Release: Specified session
   - Theme: Sessions matching theme
2. Generate compelling subject line
3. Create HTML and plain text versions
4. Include preview text for email clients
5. Add featured session highlights

## Examples

```bash
# Weekly digest
/build-newsletter --type weekly --save

# New session announcement
/build-newsletter --type new_release --sessions garden-of-eden-pathworking

# Themed collection
/build-newsletter --type theme --theme "Shadow Work" --save
```

## Output

The newsletter includes:
- Subject line optimized for open rates
- Preview text (first 90 characters in email preview)
- HTML version with styling
- Plain text fallback
- Featured session(s) with descriptions
- Call-to-action links

## Implementation

```python
from scripts.ai.content import NewsletterBuilder

builder = NewsletterBuilder()

# Weekly digest
newsletter = builder.build_weekly_digest()

# New release
newsletter = builder.build_new_release("session-name")

# Themed
newsletter = builder.build_themed_newsletter("Shadow Work")

if args.save:
    html_path, txt_path = builder.save_newsletter(newsletter)
    print(f"Saved HTML: {html_path}")
    print(f"Saved TXT: {txt_path}")
```

## Newsletter Structure

### Weekly Digest
- Greeting with week summary
- Featured session (highest impact)
- Additional sessions list
- Closing with CTA

### New Release
- Announcement headline
- Session description
- Key benefits
- What to expect
- Listen now CTA

### Themed Collection
- Theme introduction
- Curated session list with descriptions
- Why this theme matters
- Exploration invitation

## Email Best Practices Applied

- Subject lines under 50 characters
- Preview text optimized for mobile
- Single clear CTA per section
- Mobile-responsive HTML
- Plain text alternative for accessibility
