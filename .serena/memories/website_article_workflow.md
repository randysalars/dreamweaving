# Website Article Creation Workflow

**VERSION:** 1.0
**LAST UPDATED:** 2025-12-10

This documents the complete workflow for creating and deploying articles to salars.net.

---

## Quick Reference

### Command
```
/write-article <path> [title]
```

### Example
```
/write-article dreamweaving/my-new-article "My Article Title"
```

---

## File Locations

| Resource | Path |
|----------|------|
| Website Frontend | `/media/rsalars/elements/Projects/salarsu/frontend/` |
| Article Pages | `/media/rsalars/elements/Projects/salarsu/frontend/app/{category}/{slug}/page.js` |
| Styling Guide | `/home/rsalars/Projects/dreamweaving/docs/WEBPAGE_FORMAT_GUIDE.md` |
| Slash Command | `/home/rsalars/Projects/dreamweaving/.claude/commands/write-article.md` |

---

## Standard Page Template

```jsx
import Link from 'next/link';
import { Metadata } from 'next';

export const metadata = {
  title: '{Title} | Salars Dreamweaver',
  description: '{155 char description}',
  keywords: '{keywords}',
  openGraph: {
    title: '{Title}',
    description: '{Description}',
    type: 'article',
    url: 'https://www.salars.net/{path}',
  },
};

export default function {ComponentName}Page() {
  return (
    <div className='container mx-auto px-4 py-8 max-w-4xl'>
      <Link
        href='{back_link}'
        className='text-primary hover:underline mb-4 inline-block'
      >
        &larr; Back to {Parent}
      </Link>

      <article className='prose prose-lg dark:prose-invert max-w-none'>
        <h1 className='text-4xl md:text-5xl font-bold mb-2 text-foreground'>
          {Title}
        </h1>
        <p className='text-xl text-muted-foreground mb-8 italic'>
          {Subtitle}
        </p>

        <hr className='my-8' />

        {/* Sections */}
        <section className='mb-12'>
          <h2 className='text-3xl font-bold mb-4 text-foreground'>Section Title</h2>
          <p className='text-lg text-foreground mb-4'>Content...</p>
        </section>

        <hr className='my-8' />

        {/* Related Articles - ALWAYS include */}
        <section className='mb-8'>
          <div className='bg-card/70 text-card-foreground border p-6 rounded-lg'>
            <h3 className='text-xl font-semibold mb-3 text-foreground'>Related Articles</h3>
            <ul className='list-disc list-inside text-lg space-y-2'>
              <li>
                <Link href='/path' className='text-primary hover:underline font-semibold'>
                  Title
                </Link>
                {' '}— Description.
              </li>
            </ul>
          </div>
        </section>
      </article>
    </div>
  );
}
```

---

## Styling Classes Quick Reference

### Layout
| Element | Class |
|---------|-------|
| Page container | `container mx-auto px-4 py-8 max-w-4xl` |
| Article wrapper | `prose prose-lg dark:prose-invert max-w-none` |
| Section | `mb-12` |
| Divider | `<hr className='my-8' />` |

### Typography
| Element | Class |
|---------|-------|
| H1 | `text-4xl md:text-5xl font-bold mb-2 text-foreground` |
| Subtitle | `text-xl text-muted-foreground mb-8 italic` |
| H2 | `text-3xl font-bold mb-4 text-foreground` |
| H3 | `text-2xl font-semibold mb-3 text-foreground mt-8` |
| Paragraph | `text-lg text-foreground mb-4` |

### Lists
| Type | Class |
|------|-------|
| Bullet | `list-disc list-inside text-lg text-foreground mb-4 space-y-1` |
| Numbered | `list-decimal list-inside text-lg text-foreground mb-4 space-y-2` |

### Special Elements
| Element | Class |
|---------|-------|
| Blockquote | `border-l-4 border-primary pl-4 my-4 italic text-lg text-foreground` |
| Callout box | `bg-card/50 p-4 rounded-lg border mb-4` |
| Key statement | `font-semibold bg-card/50 p-4 rounded-lg border` |
| Accent box | `bg-primary/10 p-6 rounded-lg border border-primary/30` |
| Related articles | `bg-card/70 text-card-foreground border p-6 rounded-lg` |

### Links
| Type | Class |
|------|-------|
| Internal | `text-primary hover:underline font-semibold` |
| Back nav | `text-primary hover:underline mb-4 inline-block` |
| External | Add `target="_blank" rel="noopener noreferrer"` |

---

## Deployment Process

1. **Create the page file**
   ```bash
   # Create directory if needed
   mkdir -p /media/rsalars/elements/Projects/salarsu/frontend/app/{path}/
   
   # Create page.js with content
   ```

2. **Update any linking pages**
   - Add link in Related Articles section of parent/related pages

3. **Commit and push**
   ```bash
   cd /media/rsalars/elements/Projects/salarsu/frontend
   git add app/{path}/
   git add {modified_files}
   git commit -m "Add article: {title}

   - New article at /{path}
   - {Changes summary}

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   git push origin main
   ```

4. **Verify deployment**
   - Vercel auto-deploys from main branch
   - Check: https://vercel.com/randysalars/salars/deployments
   - Live URL: https://www.salars.net/{path}

---

## Article Categories

| Category | Path Prefix | Back Link |
|----------|-------------|-----------|
| Dreamweaving | `dreamweaving/` | `/dreamweavings` or parent article |
| Spirituality | `spirituality/` | `/spirituality` |
| Consciousness | `consciousness/` | `/consciousness` |
| AI | `ai/` | `/ai` |

---

## Quality Checklist

Before deploying any article:

- [ ] Metadata complete (title, description, keywords, openGraph)
- [ ] URL path is valid (lowercase, hyphens/underscores)
- [ ] H1 title matches page purpose
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] All styling classes from this guide used
- [ ] Blockquotes for Scripture/important quotes
- [ ] Related Articles section at bottom
- [ ] Back navigation link at top
- [ ] Internal links use `<Link>` from next/link
- [ ] External links have target="_blank" rel="noopener noreferrer"
- [ ] Component name is PascalCase
- [ ] File exports default function
- [ ] No TypeScript errors (page.js not page.tsx unless needed)

---

## Examples

### Existing Articles
- `/dreamweaving/christianity_and_hypnosis` - Theology article
- `/dreamweaving/christianity_and_archetypes` - Archetypes article
- `/dreamweaving/forbidden_knowledge` - Forbidden knowledge article

### Pattern for New Articles
1. Match styling of existing articles
2. Use same component structure
3. Cross-link related content
4. Deploy with proper commit message
