# Salars.net Article Deployment Checklist (Read Before You Push)

This workspace (`dreamweaving`) contains generated/working content files, but **salars.net production deploys from the Salarsu website repo**:

- Website repo: `/home/rsalars/Projects/salarsu`
- Next.js app: `/home/rsalars/Projects/salarsu/frontend`
- Deploy: Coolify (push to the branch it tracks, typically `main`)

## Quick decision rule

If the content is meant to appear on `https://salars.net` (or `https://www.salars.net`), the final changes must land in the **Salarsu repo**, not only in `dreamweaving`.

## Before writing new pages

- Confirm you are editing the correct repo:
  - ✅ Production: `/home/rsalars/Projects/salarsu/frontend/app/...`
  - ⚠️ Workspace copy (won’t deploy by itself): `dreamweaving/salarsu/frontend/app/...`
- If you drafted content inside `dreamweaving`, plan the copy/patch step into Salarsu before you consider the work “done”.

## Before committing

- Verify routes exist in Salarsu:
  - `ls /home/rsalars/Projects/salarsu/frontend/app/<route>/page.tsx`
- If the site uses a manual sitemap list, add routes:
  - `/home/rsalars/Projects/salarsu/frontend/app/sitemap.js`
- If the page is referenced from a hub/table, ensure the **hub in Salarsu** links to the new pages (not just the `dreamweaving` copy).

## Deploy flow (the only one that affects production)

```bash
git -C /home/rsalars/Projects/salarsu status
git -C /home/rsalars/Projects/salarsu add -A
git -C /home/rsalars/Projects/salarsu commit -m "Add/Update <topic> pages"
git -C /home/rsalars/Projects/salarsu push origin main
```

Then confirm Coolify redeployed and verify on production:

- `https://www.salars.net/<route>`
- `https://www.salars.net/sitemap.xml` (if applicable)

## Common failure mode (what to check first)

- “It works locally / in this repo, but not on salars.net” almost always means:
  - The changes were committed to `dreamweaving`, not `/home/rsalars/Projects/salarsu`.

