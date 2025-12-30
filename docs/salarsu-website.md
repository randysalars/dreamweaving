# Salarsu Website (salars.net)

Reference documentation for working with the Salarsu website repository from the dreamweaving project.

## Repository Location

```
/home/rsalars/Projects/salarsu
```

> [!IMPORTANT]
> This is on an external drive. Make sure the drive is mounted before working with the repo.

## Quick Reference

| Property | Value |
|----------|-------|
| **GitHub Repo** | `randysalars/salars` |
| **Primary Branch** | `main` |
| **Framework** | Next.js 16 |
| **React Version** | 19.0.0 |
| **Styling** | TailwindCSS 3.3.2 |
| **Database** | PostgreSQL via Prisma |
| **Deployment** | Coolify (self-hosted) |

---

## Project Structure

```
salarsu/
├── frontend/                 # Main application
│   ├── app/                 # Next.js App Router pages
│   │   ├── api/             # API routes
│   │   ├── about/           # About page
│   │   ├── account/         # User account pages
│   │   ├── cart/            # Shopping cart
│   │   ├── checkout/        # Checkout flow
│   │   ├── dreamweaving/    # Dreamweaving content section
│   │   ├── dreamweavings/   # Dreamweavings list
│   │   ├── xmas/            # Christmas content
│   │   ├── components/      # Page-level components
│   │   ├── hooks/           # React hooks
│   │   ├── lib/             # Utility functions
│   │   ├── layout.js        # Root layout
│   │   ├── page.js          # Homepage
│   │   └── globals.css      # Global styles
│   ├── components/          # Shared components
│   └── package.json         # Frontend dependencies
├── prisma/                   # Database schema
├── scripts/                  # Build & automation scripts
└── package.json             # Root dependencies
```

---

## Common Commands

### Development

```bash
# Navigate to the salarsu repo
cd /home/rsalars/Projects/salarsu/frontend

# Install dependencies
npm install --legacy-peer-deps

# Run development server
npm run dev
```

### Building & Testing

```bash
# Build for production
npm run build

# Run linter
npm run lint

# Run tests
npm test

# Simulate CI pipeline
npm run ci:simulate
```

### Deployment

```bash
# Coolify deployment (typical flow)
# 1) Push changes to the repo branch Coolify tracks
git add .
git commit -m "Your commit message"
git push origin main

# 2) In Coolify, trigger a redeploy for the service (or rely on webhook auto-deploy if configured).
```

---

## Key Technologies

- **Next.js 16** - React framework with App Router
- **React 19** - UI library
- **TailwindCSS** - Utility-first CSS
- **Prisma** - Database ORM
- **Stripe** - Payment processing
- **PayPal** - Alternative payments
- **NextAuth** - Authentication
- **Framer Motion** - Animations
- **Resend** - Email service
- **Redis** - Caching
- **OpenAI** - AI features
- **First-party Analytics** - Events stored in Postgres

---

## Environment Variables

Example env variables needed (from `.env.example`):

```bash
# Database
DATABASE_URL=your_postgres_database_url

# Authentication
NEXTAUTH_URL=https://salars.net
NEXTAUTH_SECRET=your_secret

# Payments
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
PAYPAL_CLIENT_ID=...

# Email
RESEND_API_KEY=re_...

# AI
OPENAI_API_KEY=sk-...

# Backups
CRON_SECRET=your_secure_token_here
AUTO_BACKUP_ENABLED=true
```

---

## Adding New Pages

To add a new page to the website:

1. Create a new directory in `/home/rsalars/Projects/salarsu/frontend/app/`
2. Add a `page.js` or `page.tsx` file
3. Build and test locally with `npm run dev`
4. Commit and push to deploy

Example for a new page at `/newpage`:

```bash
mkdir -p /home/rsalars/Projects/salarsu/frontend/app/newpage
```

```javascript
// /home/rsalars/Projects/salarsu/frontend/app/newpage/page.js
export default function NewPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold">New Page</h1>
      <p>Content goes here...</p>
    </div>
  );
}

export const metadata = {
  title: 'New Page | Salars',
  description: 'Description of the new page',
};
```

---

## Existing Dreamweaving Pages

The website already has dreamweaving-related content:

- `/dreamweaving/` - Main dreamweaving page
- `/dreamweavings/` - List of dreamweavings

These are located at:
- `/home/rsalars/Projects/salarsu/frontend/app/dreamweaving/`
- `/home/rsalars/Projects/salarsu/frontend/app/dreamweavings/`

---

## Git Workflow

```bash
# Check status
git -C /home/rsalars/Projects/salarsu status

# Pull latest changes
git -C /home/rsalars/Projects/salarsu pull origin main

# Push changes
git -C /home/rsalars/Projects/salarsu push origin main

# View recent commits
git -C /home/rsalars/Projects/salarsu log -n 5 --oneline
```

---

## Notes

- The external drive path `/media/rsalars/elements/` must be accessible
- Coolify can auto-deploy on push if a webhook is configured; otherwise redeploy manually in the Coolify UI
- The site uses legacy peer deps (`--legacy-peer-deps`) for npm installs
- API routes have a max duration of 30 seconds configured
