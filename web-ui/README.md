This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font).

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Coolify (self-hosted)

This project is deployed via **Coolify** (self-hosted), with a **Postgres** database.

**Full Runbook:** See [docs/COOLIFY_RUNBOOK.md](../docs/COOLIFY_RUNBOOK.md) for complete deployment steps, environment variables, and troubleshooting.

### Quick Checklist

1. Create/attach a **Postgres** service in Coolify.
2. Configure environment variables in Coolify (at minimum `DATABASE_URL`, plus any payment/webhook secrets used by `/api/*` routes).
3. Deploy the `web-ui` service and verify:
   - `/sitemap.xml` loads
   - `/api/track` accepts POSTs (and events land in Postgres)
   - webhooks (PayPal/Stripe/Bitcoin) verify signatures in production

## Version Notes

This project uses cutting-edge versions:

- **Next.js 16.0.8** - Latest major release (Dec 2025)
- **React 19.2.1** - Latest major release with Server Components

When updating dependencies:

1. Check [Next.js release notes](https://nextjs.org/blog) for breaking changes
2. Test thoroughly as these are recent major versions
3. Consider pinning to patch versions for production stability
