# Generate Blog Post from Session

Generate a blog post from a Dreamweaving session for salars.net.

## Usage

```
/generate-blog <session-name> [--type <type>] [--save]
```

## Arguments

- `session-name`: Name of the session directory (required)
- `--type`: Type of blog post (default: experience)
  - `experience`: What to expect from this journey
  - `deep_dive`: Deep exploration of the theme and symbolism
  - `benefits`: Benefits and transformative outcomes
  - `technique`: Hypnotic techniques explained
- `--save`: Save the post to `output/blog_drafts/`

## Process

1. Load the session manifest from `sessions/{session-name}/manifest.yaml`
2. Extract theme, description, archetypes, and desired outcome
3. Generate blog content based on the selected type
4. Create SEO-friendly metadata (title, slug, description, tags)
5. Output as markdown with frontmatter

## Example

```
/generate-blog garden-of-eden-pathworking --type deep_dive --save
```

## Output

The generated blog post includes:
- Frontmatter (title, slug, tags, category, date)
- Engaging content structured for the post type
- SEO meta description (155 characters max)
- Related session reference

## Implementation

```python
from scripts.ai.content import AutoBlogWriter

writer = AutoBlogWriter()
post = writer.generate_from_session(
    session_name=args.session,
    blog_type=args.type
)

if args.save:
    path = writer.save_post(post)
    print(f"Saved to: {path}")
else:
    print(post.to_markdown())
```

## Post Types Explained

### Experience Post
"What to Expect" style - prepares listeners for the journey:
- What happens during the session
- Common experiences and sensations
- How to prepare and integrate

### Deep Dive Post
Explores symbolism and meaning:
- Archetypal analysis
- Cross-tradition connections
- Psychological depth

### Benefits Post
Focuses on transformation:
- Specific benefits by outcome type
- Science of hypnotic transformation
- Cumulative effects

### Technique Post
Educational content:
- Language patterns used
- Trance induction methods
- Audio processing techniques
