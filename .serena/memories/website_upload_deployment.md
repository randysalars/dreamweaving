# Website Upload & Deployment Workflow

**VERSION:** 1.0
**LAST UPDATED:** 2025-12-04
**STATUS:** ✅ TESTED & WORKING

This documents the complete workflow for uploading dreamweaving sessions to salars.net and deploying frontend changes to Vercel.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                     DREAMWEAVING WEBSITE STACK                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LOCAL (Dreamweaving Project)          REMOTE (Vercel/salars.net)      │
│  ├── sessions/{name}/                  ├── Vercel Blob (R2)            │
│  │   ├── manifest.yaml                 │   └── Media files             │
│  │   ├── output/                       │       ├── audio/*.mp3         │
│  │   │   ├── *_MASTER.mp3             │       ├── video/*.mp4         │
│  │   │   ├── *_final.mp4              │       ├── thumbnails/*.png    │
│  │   │   └── youtube_package/         │       └── subtitles/*.vtt     │
│  │   │       ├── thumbnail.png        │                                │
│  │   │       └── subtitles.vtt        ├── Neon PostgreSQL             │
│  │   └── images/uploaded/             │   └── dreamweavings table      │
│  │                                     │       ├── id (cuid)           │
│  └── scripts/core/                     │       ├── slug (unique)       │
│      └── upload_to_website.py          │       ├── title, subtitle     │
│                                        │       ├── media URLs          │
│  LOCAL (Salarsu Frontend)              │       ├── chapters (JSONB)    │
│  ├── app/dreamweavings/               │       └── archetypes (JSONB)  │
│  │   ├── page.js (listing)            │                                │
│  │   └── [slug]/page.tsx (detail)     ├── API Routes                  │
│  └── app/api/dreamweavings/           │   ├── GET /api/dreamweavings   │
│      ├── route.js (list/create)       │   └── GET /api/dreamweavings/  │
│      └── [slug]/route.ts (get one)    │       [slug]                  │
│                                        │                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Session Upload (upload_to_website.py)

### Prerequisites

1. **Environment Variables** (in `.env`):
```bash
SALARSU_API_TOKEN=your-api-token
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

2. **Session Requirements**:
   - `manifest.yaml` - Session configuration
   - `output/*_MASTER.mp3` - Final mastered audio
   - `output/*_final.mp4` or `youtube_package/final_video.mp4` - Video (optional)
   - `output/youtube_thumbnail.png` or `youtube_package/thumbnail.png` - Thumbnail
   - `output/youtube_package/subtitles.vtt` - Subtitles (optional)

### Upload Process

```bash
# 1. Dry run first (validates without uploading)
source venv/bin/activate
python3 scripts/core/upload_to_website.py --session sessions/{name}/ --dry-run

# 2. Upload to production
python3 scripts/core/upload_to_website.py --session sessions/{name}/ --no-git
```

### What Happens During Upload

1. **Loads session data** from manifest.yaml
2. **Locates media files** with fallback paths:
   - Audio: `*_MASTER.mp3` → `*_final.mp3` → `final.mp3`
   - Video: `youtube_package/final_video.mp4` → `video/session_final.mp4` → `*_final.mp4`
   - Thumbnail: `youtube_thumbnail.png` → `youtube_package/thumbnail.png` → `images/uploaded/thumbnail.png`
   - Subtitles: `youtube_package/subtitles.vtt` → `output/subtitles.vtt`
3. **Validates session** - Checks required files exist
4. **Auto-detects category** from session name/content
5. **Uploads media** to Vercel Blob (R2 storage)
6. **Creates database record** via API

### Category Detection Keywords

| Category | Keywords |
|----------|----------|
| `nature-forest` | forest, nature, garden, eden, tree |
| `cosmic-space` | cosmic, space, star, astral, galaxy, neural |
| `healing` | healing, restore, repair, wellness |
| `shadow-work` | shadow, dark, unconscious |
| `archetypal` | archetype, journey, guide |
| `sacred-spiritual` | sacred, divine, spiritual, temple, thousand |
| `confidence` | confidence, power, strength, courage, iron, forge |
| `relaxation` | relax, sleep, calm, peace |

### Output

```
UPLOAD COMPLETE
======================================================================
View at: https://www.salars.net/dreamweavings/{slug}
```

---

## Step 2: Frontend Integration

### Required Frontend Components

The salarsu frontend needs these routes:

1. **API Route for List** (`/api/dreamweavings/route.js`):
   - GET: Returns paginated list of published dreamweavings
   - POST: Creates new dreamweaving (authenticated)

2. **API Route for Single** (`/api/dreamweavings/[slug]/route.ts`):
   - GET: Returns single dreamweaving by slug
   - Includes `dreamweavingCategory` relation
   - Increments `view_count`

3. **Listing Page** (`/dreamweavings/page.js`):
   - Fetches from `/api/dreamweavings`
   - Shows thumbnail cards with duration, category
   - Links to individual pages

4. **Detail Page** (`/dreamweavings/[slug]/page.tsx`):
   - Fetches from `/api/dreamweavings/{slug}`
   - Hero with video/audio player
   - Displays chapters, archetypes, tags
   - Safety notice

### TypeScript Interface

```typescript
interface Dreamweaving {
  id: string;
  slug: string;
  title: string;
  subtitle?: string;
  description?: string;
  audio_url?: string;
  video_url?: string;
  thumbnail_url?: string;
  subtitles_url?: string;
  duration_minutes?: number;
  category?: string;
  archetypes?: Array<{ name: string; role?: string }> | string[];
  binaural_config?: Record<string, unknown>;
  chapters?: Array<{ title: string; time: string }>;
  tags?: string;
  status?: string;
  featured?: boolean;
  view_count?: number;
  dreamweavingCategory?: {
    id: string;
    name: string;
    slug: string;
    color?: string;
    icon?: string;
  };
}
```

### Handling JSONB Fields

Archetypes can be objects OR strings - handle both:
```typescript
{dreamweaving.archetypes.map((archetype) => {
  const name = typeof archetype === 'string' ? archetype : archetype.name;
  return <Badge key={name}>{name}</Badge>;
})}
```

Binaural config requires explicit type casting:
```typescript
{(() => {
  const config = dreamweaving.binaural_config as Record<string, unknown>;
  return config.frequency && <span>{String(config.frequency)}Hz</span>;
})()}
```

---

## Step 3: Vercel Deployment

### Automatic Deployment (Recommended)

Vercel auto-deploys from GitHub main branch:

```bash
cd /home/rsalars/Projects/salarsu/frontend
git add .
git commit -m "feat: Add new feature"
git push origin main
# Vercel deploys automatically in 1-2 minutes
```

### Build Configuration

The `build-with-env.sh` script handles build-time environment issues:

```bash
#!/bin/bash
# Dummy DATABASE_URL prevents build errors
export DATABASE_URL="postgresql://dummy:dummy@localhost:5432/dummy"

# Other required env vars
export REDIS_URL="redis://localhost:6379"
export RESEND_API_KEY="re_dummy_key_for_build"

npx prisma generate && npx next build
```

**Key Insight:** DATABASE_URL is only available at runtime (from Neon integration), not build time. Use dummy values for build, real values come from Vercel environment at runtime.

---

## Troubleshooting

### Issue: 404 on dreamweaving page

**Cause:** Missing dynamic route
**Solution:** Create `/app/dreamweavings/[slug]/page.tsx` with proper async params handling

```typescript
export default function DreamweavingPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  // Use async params in Next.js 15
  const [slug, setSlug] = useState<string | null>(null);
  useEffect(() => {
    params.then(p => setSlug(p.slug));
  }, [params]);
}
```

### Issue: TypeScript build errors with Badge component

**Cause:** Badge requires className prop
**Solution:** Add `className=""` to all Badge components

### Issue: Client-side exception with archetypes

**Cause:** Archetypes is objects `{name, role}` not strings
**Solution:** Check type before rendering:
```typescript
const name = typeof archetype === 'string' ? archetype : archetype.name;
```

### Issue: Missing *_MASTER.mp3

**Cause:** Session used non-standard naming (e.g., `final.mp3`)
**Solution:** Copy to expected name:
```bash
cp output/final.mp3 output/{session}_MASTER.mp3
```

### Issue: API returns 401 Unauthorized

**Cause:** Token mismatch between local and Vercel env
**Solution:** Verify `DREAMWEAVING_API_TOKEN` matches in both places

---

## Batch Upload Pattern

For uploading multiple sessions:

```bash
for session in atlas-starship iron-soul-forge forest-of-lost-instincts; do
  echo "=== Uploading $session ==="
  python3 scripts/core/upload_to_website.py --session sessions/$session/ --no-git
  echo ""
done
```

---

## Media File Size Limits

| Type | Max Size | Format |
|------|----------|--------|
| Audio | 100 MB | MP3 (320 kbps) |
| Video | 500 MB | MP4 (H.264) |
| Thumbnail | 10 MB | PNG |
| Subtitles | 1 MB | VTT |

---

## Database Schema Reference

```sql
-- Categories
CREATE TABLE dreamweaving_categories (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  color VARCHAR(7) DEFAULT '#8B5CF6',
  icon VARCHAR(50)
);

-- Dreamweavings
CREATE TABLE dreamweavings (
  id VARCHAR(36) PRIMARY KEY,
  slug VARCHAR(255) UNIQUE NOT NULL,
  title VARCHAR(500) NOT NULL,
  subtitle VARCHAR(500),
  description TEXT,
  audio_url VARCHAR(1000),
  video_url VARCHAR(1000),
  thumbnail_url VARCHAR(1000),
  subtitles_url VARCHAR(1000),
  duration_minutes INTEGER DEFAULT 25,
  category VARCHAR(100) DEFAULT 'archetypal',
  category_id VARCHAR(36) REFERENCES dreamweaving_categories(id),
  archetypes JSONB DEFAULT '[]',
  binaural_config JSONB DEFAULT '{}',
  chapters JSONB DEFAULT '[]',
  tags VARCHAR(1000) DEFAULT '',
  status VARCHAR(50) DEFAULT 'draft',
  featured BOOLEAN DEFAULT FALSE,
  view_count INTEGER DEFAULT 0,
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Quick Reference Commands

```bash
# Upload session
python3 scripts/core/upload_to_website.py --session sessions/{name}/ --no-git

# Dry run (validate only)
python3 scripts/core/upload_to_website.py --session sessions/{name}/ --dry-run

# Override category
python3 scripts/core/upload_to_website.py --session sessions/{name}/ --category cosmic-space

# Git push to trigger Vercel deploy
cd /home/rsalars/Projects/salarsu/frontend && git push origin main

# Check deployment status
# Visit: https://vercel.com/randysalars/salars/deployments
```
