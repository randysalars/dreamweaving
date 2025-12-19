---
description: Deploy changes to the salars.net website via Vercel
---

# Deploy Salarsu Website

This workflow deploys changes to the salars.net website hosted on Vercel.

## Prerequisites

- External drive mounted at `/media/rsalars/elements/`
- Changes ready to deploy in the salarsu repository

## Steps

1. Navigate to the salarsu frontend directory:
```bash
cd /home/rsalars/Projects/salarsu/frontend
```

2. Test the build locally (optional but recommended):
// turbo
```bash
npm run build
```

3. Check git status for changes:
// turbo
```bash
git -C /home/rsalars/Projects/salarsu status
```

4. Add all changes:
```bash
git -C /home/rsalars/Projects/salarsu add .
```

5. Commit with a descriptive message:
```bash
git -C /home/rsalars/Projects/salarsu commit -m "Your commit message here"
```

6. Push to main branch (triggers auto-deploy):
```bash
git -C /home/rsalars/Projects/salarsu push origin main
```

7. Vercel will automatically build and deploy. Check deploy status at:
   - Vercel Dashboard: https://vercel.com/randysalars/salars
   - Or via CLI: `vercel list`

## Notes

- Auto-deployment is enabled on push to `main` branch
- Build typically takes 2-3 minutes
- The `rootDirectory` is `frontend` in Vercel config
- Uses `--legacy-peer-deps` for npm installs
