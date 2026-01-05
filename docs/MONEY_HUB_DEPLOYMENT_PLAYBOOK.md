# Money Hub + Articles: Deployment Playbook (salars.net)

This is the operational checklist for creating and deploying the `/money` hub and its `/money/[slug]` article pages so they show up on `https://salars.net`.

## 0) The most important constraint

`salars.net` is deployed from the **Salarsu website repo**, not this `dreamweaving` repo.

- **Website repo**: `/home/rsalars/Projects/salarsu`
- **Next.js app**: `/home/rsalars/Projects/salarsu/frontend`
- **Deploy**: Coolify (push to branch it tracks, typically `main`)

Reference: `docs/salarsu-website.md`

## 1) Where the Money system lives (in the Salarsu repo)

These are the core files added/used:

- Hub route: `/home/rsalars/Projects/salarsu/frontend/app/money/page.js`
- Article route: `/home/rsalars/Projects/salarsu/frontend/app/money/[slug]/page.js`
- Content registry (all money pages live here): `/home/rsalars/Projects/salarsu/frontend/lib/money/pages.js`
- Wealth page link/card (points to `/money`): `/home/rsalars/Projects/salarsu/frontend/app/wealth/page.js`
- Sitemap includes `/money` routes: `/home/rsalars/Projects/salarsu/frontend/app/sitemap.js`

## 2) How to add a new Money article (the repeatable workflow)

1. Open: `/home/rsalars/Projects/salarsu/frontend/lib/money/pages.js`
2. Add a new object to `moneyPages`:
   - `slug` (URL-safe, hyphenated)
   - `tier` (`1` = core model, `2` = answer page)
   - `title`, `description`
   - `content` (use the same “Direct answer / Mechanism / Implication / Definitions …” structure)
3. Ensure the slug is unique and the hub links to it (the hub lists from `moneyPages`, and the Must-Have list uses `moneyMustHave12Slugs`).
4. (Optional but recommended) Add the slug to `moneyMustHave12Slugs` if it’s part of the “Must-Have 12”.

No extra files are required for the route: the `[slug]` page renders whatever is present in `moneyPages`.

## 3) Critical Next.js routing gotcha (what caused the 404s)

In this codebase/Next.js setup, `params` is a **Promise** in app routes.

If you do:

- `const slug = params.slug`

…then `slug` becomes `undefined`, and the page will 404 for every article.

Correct pattern used in `/home/rsalars/Projects/salarsu/frontend/app/money/[slug]/page.js`:

- `const { slug } = await params;`

Apply the same approach anywhere you read `params` in app routes if you see similar 404 behavior.

## 4) Sitemap (so pages show up in indexing)

Update `/home/rsalars/Projects/salarsu/frontend/app/sitemap.js` to include:

- `'/money'`
- every `'/money/<slug>'` from `moneyPages`

This repo’s sitemap already uses a static route list; money routes were appended using:

- `...moneyPages.map((page) => \`/money/\${page.slug}\`)`

## 5) Local verification before deploy

From `/home/rsalars/Projects/salarsu/frontend`:

```bash
npm run build
npm run start
```

Check:

- `http://localhost:3000/money` loads
- `http://localhost:3000/money/what-is-money` loads (or any slug you added)
- `http://localhost:3000/sitemap.xml` includes `/money` routes

## 6) Deploy to production (Coolify)

From `/home/rsalars/Projects/salarsu`:

```bash
git add -A
git commit -m "Add money hub + articles"
git push origin main
```

Then in Coolify:

- trigger a redeploy (or rely on auto-deploy webhook if configured)

## 7) Post-deploy verification

Verify on production:

- `https://www.salars.net/money` loads
- `https://www.salars.net/money/<some-slug>` loads
- `https://www.salars.net/sitemap.xml` contains `/money` routes

## 8) Troubleshooting checklist

If `/money` hub works but `/money/<slug>` 404s:

- Confirm `/home/rsalars/Projects/salarsu/frontend/app/money/[slug]/page.js` is awaiting `params`:
  - `const { slug } = await params;`
- Confirm the slug exists in `/home/rsalars/Projects/salarsu/frontend/lib/money/pages.js` (`moneyPages`)
- Confirm the fix is committed and deployed (Coolify redeploy happened)

If the page loads but is “empty”:

- Confirm the page object includes `content` (non-empty string) in `moneyPages`
- Confirm ReactMarkdown rendering isn’t blocked by malformed markdown (rare; check logs)

