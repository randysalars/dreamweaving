---
name: write-article
description: Write an article for salars.net and deploy to Vercel
arguments:
  - name: path
    required: true
    description: URL path for the article (e.g., dreamweaving/my-article)
  - name: title
    required: false
    description: Optional article title (will be extracted from content if not provided)
agent: general-purpose
---

# /write-article Command

Create a new article page for salars.net website and deploy it to Vercel.

## Usage
```
/write-article <path> [title]
```

## Examples
```
/write-article dreamweaving/new-topic "My Article Title"
/write-article spirituality/meditation-guide
```

## Process

### 1. Parse Input
- Extract the URL path (e.g., `dreamweaving/forbidden_knowledge`)
- The path determines the directory structure in `app/` folder
- Validate the path format (lowercase, hyphens or underscores, no special chars)

### 2. Gather Content
Ask the user for the article content. Accept it in any format:
- Plain text with markdown formatting
- Structured outline
- Raw content to be formatted
- Reference URL to adapt

### 3. Determine Article Structure
Based on content, identify:
- Main title (H1)
- Subtitle/tagline (if applicable)
- Major sections (H2)
- Subsections (H3)
- Blockquotes (Scripture, quotes)
- Key callout boxes
- Related articles to link

### 4. Create the Page File

**Location:** `/media/rsalars/elements/Projects/salarsu/frontend/app/{path}/page.js`

**Required Structure:**
```jsx
import Link from 'next/link';
import { Metadata } from 'next';

export const metadata = {
  title: '{Title} | Salars Dreamweaver',
  description: '{155 char description}',
  keywords: '{comma, separated, keywords}',
  openGraph: {
    title: '{Title}',
    description: '{Description}',
    type: 'article',
    url: 'https://www.salars.net/{path}',
  },
};

export default function {PageComponentName}() {
  return (
    <div className='container mx-auto px-4 py-8 max-w-4xl'>
      <Link
        href='{back_link}'
        className='text-primary hover:underline mb-4 inline-block'
      >
        &larr; Back to {Parent Page}
      </Link>

      <article className='prose prose-lg dark:prose-invert max-w-none'>
        {/* Content here */}
      </article>
    </div>
  );
}
```

### 5. Apply Styling Standards

**From docs/WEBPAGE_FORMAT_GUIDE.md:**

| Element | Class |
|---------|-------|
| Page container | `container mx-auto px-4 py-8 max-w-4xl` |
| Article wrapper | `prose prose-lg dark:prose-invert max-w-none` |
| H1 title | `text-4xl md:text-5xl font-bold mb-2 text-foreground` |
| Subtitle | `text-xl text-muted-foreground mb-8 italic` |
| H2 sections | `text-3xl font-bold mb-4 text-foreground` |
| H3 subsections | `text-2xl font-semibold mb-3 text-foreground mt-8` |
| Body paragraph | `text-lg text-foreground mb-4` |
| Lists | `list-disc list-inside text-lg text-foreground mb-4 space-y-1` |
| Ordered lists | `list-decimal list-inside text-lg text-foreground mb-4 space-y-2` |
| Blockquotes | `border-l-4 border-primary pl-4 my-4 italic text-lg text-foreground` |
| Section divider | `<hr className='my-8' />` |
| Section wrapper | `<section className='mb-12'>` |
| Callout box | `bg-card/50 p-4 rounded-lg border mb-4` |
| Key statement | `font-semibold bg-card/50 p-4 rounded-lg border` |
| Primary accent | `bg-primary/10 p-6 rounded-lg border border-primary/30` |
| Related articles | `bg-card/70 text-card-foreground border p-6 rounded-lg` |
| Links | `text-primary hover:underline font-semibold` |
| Back link | `text-primary hover:underline mb-4 inline-block` |

### 6. Add Related Articles Section

At the bottom of every article, include:
```jsx
<section className='mb-8'>
  <div className='bg-card/70 text-card-foreground border p-6 rounded-lg'>
    <h3 className='text-xl font-semibold mb-3 text-foreground'>Related Articles</h3>
    <ul className='list-disc list-inside text-lg space-y-2'>
      <li>
        <Link href='/path/to/article' className='text-primary hover:underline font-semibold'>
          Article Title
        </Link>
        {' '}— Brief description.
      </li>
    </ul>
  </div>
</section>
```

### 7. Update Linking Pages

If the article should be linked from existing pages:
- Identify parent/related pages
- Add link to the new article in their Related Articles sections
- Use consistent link styling

### 8. Deploy to Vercel

```bash
cd /media/rsalars/elements/Projects/salarsu/frontend
git add app/{path}/
git add {any_modified_files}
git commit -m "Add article: {title}

- New article at /{path}
- {Additional changes if any}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin main
```

### 9. Confirm Deployment

Report to user:
- New page URL: `https://www.salars.net/{path}`
- Files created/modified
- Vercel deployment triggered (auto-deploys in 1-2 minutes)

## Article Categories

| Category Path | Parent | Back Link |
|---------------|--------|-----------|
| `dreamweaving/*` | Dreamweaving | `/dreamweavings` or specific parent |
| `spirituality/*` | Spirituality | `/spirituality` |
| `consciousness/*` | Consciousness | `/consciousness` |
| `ai/*` | AI | `/ai` |

## Quality Checklist

Before deploying, verify:
- [ ] Metadata complete (title, description, keywords, openGraph)
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Consistent styling classes used
- [ ] Blockquotes for Scripture/quotes
- [ ] Related Articles section at bottom
- [ ] Back navigation link at top
- [ ] All internal links use `<Link>` component
- [ ] External links have `target="_blank" rel="noopener noreferrer"`
- [ ] Component name is PascalCase and unique
- [ ] File exports default function
