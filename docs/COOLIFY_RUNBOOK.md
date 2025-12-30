# Coolify Deployment Runbook - Dreamweaving Web-UI

Quick reference for deploying the dreamweaving web-ui on Coolify (self-hosted).

## Quick Deploy Checklist

```
[ ] 1. Push code to main branch
[ ] 2. Verify env vars in Coolify dashboard
[ ] 3. Trigger redeploy (or wait for auto-deploy)
[ ] 4. Verify: /sitemap.xml loads
[ ] 5. Verify: /api/track accepts POSTs
```

---

## Project Structure

```
dreamweaving/
├── web-ui/                    ✅ Deployed to Coolify
│   ├── src/app/               Next.js app routes
│   ├── src/components/        React components
│   └── package.json           Dependencies
├── frontend/                  ❌ Legacy/API only (not for Coolify)
└── ...                        Python scripts (local only)
```

**Note:** The `web-ui/` directory is the Next.js application deployed to Coolify.

---

## Environment Variables

### Required (Critical)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |

### Payments (if using payment features)

| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | Stripe public key |
| `PAYPAL_CLIENT_ID` | PayPal client ID |
| `PAYPAL_CLIENT_SECRET` | PayPal secret |
| `NEXT_PUBLIC_BITCOIN_ADDRESS` | BTC address |

### Webhooks

| Variable | Description |
|----------|-------------|
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing |
| `PAYPAL_WEBHOOK_ID` | PayPal webhook ID |

---

## Deployment Commands

### Deploy New Code

```bash
# From local machine
cd /home/rsalars/Projects/dreamweaving/web-ui
git add .
git commit -m "Your changes"
git push origin main
# Coolify auto-deploys on push
```

### Local Testing Before Deploy

```bash
cd /home/rsalars/Projects/dreamweaving/web-ui
npm install
npm run build
npm run start
# Visit http://localhost:3000
```

---

## Post-Deployment Verification

### 1. Check Sitemap

```bash
curl https://your-domain.com/sitemap.xml
```

### 2. Test Tracking API

```bash
curl -X POST https://your-domain.com/api/track \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "page": "/"}'
```

### 3. Verify Database Connection

Check Coolify logs for any database connection errors.

---

## Coolify Setup Steps

### 1. Create PostgreSQL Service

1. Coolify Dashboard → Add Service → PostgreSQL
2. Configure database name, user, password
3. Note the connection URL

### 2. Create Next.js Service

1. Coolify Dashboard → Add Service → Application
2. Connect GitHub repo
3. Set build directory: `web-ui`
4. Set environment variables (see above)

### 3. Configure Environment Variables

In Coolify Dashboard → Service → Environment:

```
DATABASE_URL=postgresql://...
NODE_ENV=production
```

---

## Troubleshooting

### Build Fails

```bash
# Test build locally first
cd /home/rsalars/Projects/dreamweaving/web-ui
npm run build

# Common issues:
# - TypeScript errors
# - Missing dependencies
# - Environment variable issues
```

### Database Connection Failed

1. Check `DATABASE_URL` is set correctly
2. Verify PostgreSQL service is running in Coolify
3. Check network rules between services

### API Routes Return 500

1. Check Coolify logs
2. Verify webhook secrets match
3. Check for missing environment variables

---

## Version Info

| Package | Version |
|---------|---------|
| Next.js | 16.0.8+ |
| React | 19.2.1 |
| Node.js | 20.x |

**Note:** These are cutting-edge versions. Test thoroughly after updates.

---

## Related Documentation

- [web-ui/README.md](../web-ui/README.md) - Project setup
- [Salarsu Coolify Runbook](/home/rsalars/Projects/salarsu/frontend/docs/COOLIFY_RUNBOOK.md) - Full runbook reference

---

**Last Updated:** 2025-12-30
