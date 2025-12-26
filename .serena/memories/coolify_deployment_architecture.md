# Coolify Deployment Architecture for Salarsu

## Overview

The salarsu project is deployed to Coolify from the `frontend/` subdirectory only. This means **root-level files are NOT included in the container**.

## Key Architecture Points

### What Gets Deployed

```
/home/rsalars/Projects/salarsu/
├── scripts/                    ❌ NOT deployed (root level)
├── frontend/                   ✅ DEPLOYED as /app in container
│   ├── app/                    ✅ Next.js app routes
│   ├── scripts/                ✅ Available as /app/scripts/
│   ├── prisma/                 ✅ Prisma schema
│   ├── lib/                    ✅ Shared libraries
│   └── nixpacks.toml           ✅ Build configuration
└── ...
```

### Container Structure

```
/app/                           # Container root (= frontend/)
├── scripts/                    # frontend/scripts/ content
├── app/                        # Next.js routes
├── prisma/                     # Prisma schema
├── node_modules/               # Dependencies
└── ...
```

## Creating Seed Scripts for Coolify

### Rule: Place in `frontend/scripts/`

Any script that needs to run in the Coolify container **MUST** be placed in:
```
/home/rsalars/Projects/salarsu/frontend/scripts/
```

NOT in:
```
/home/rsalars/Projects/salarsu/scripts/  ❌ Won't be deployed!
```

### Seed Script Template

```javascript
// frontend/scripts/seed-something.mjs
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding...');
  
  // Your seeding logic here
  const result = await prisma.yourModel.upsert({
    where: { slug: 'example' },
    create: { /* ... */ },
    update: { /* ... */ },
  });
  
  console.log('✅ Done');
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

### Running Seeds in Coolify

1. **Push the script to `frontend/scripts/`**
   ```bash
   git add frontend/scripts/seed-something.mjs
   git commit -m "Add seed script"
   git push
   ```

2. **Wait for Coolify to redeploy** (or trigger manual redeploy)

3. **Open container terminal in Coolify**
   - Container: `randysalars/salars:main-...`
   - Terminal type: Container terminal (not server)

4. **Run the seed**
   ```bash
   cd /app
   node scripts/seed-something.mjs
   ```

## Nixpacks Configuration

Located at `frontend/nixpacks.toml`:

```toml
[phases.install]
cmds = ["npm install --legacy-peer-deps"]

[phases.build]
cmds = ["npx prisma generate", "npm run build"]

[start]
cmd = "npm run start"
```

## Common Mistakes

| Mistake | Why It Fails | Solution |
|---------|--------------|----------|
| Script in root `scripts/` | Root not deployed | Move to `frontend/scripts/` |
| Importing from `../lib` | Path doesn't exist in container | Use `@/lib` or relative from frontend |
| Missing Prisma client | Not generated in container | Script imports from `@prisma/client` |
| Using `require()` | ESM modules need `import` | Use `.mjs` extension and `import` |

## Environment Variables

The container has access to all environment variables configured in Coolify, including:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `DREAMWEAVING_API_TOKEN` - API authentication
- Other secrets configured in Coolify dashboard

## Example: Dreamweaving Categories Seed

The dreamweaving categories seed script demonstrates this pattern:

**Location:** `frontend/scripts/seed-dreamweaving-categories.mjs`

**Deployment:**
```bash
# Copy if originally in root scripts/
cp scripts/seed-dreamweaving-categories.mjs frontend/scripts/

# Commit and push
git add frontend/scripts/seed-dreamweaving-categories.mjs
git commit -m "Add dreamweaving categories seed to frontend for Coolify"
git push
```

**Execution in container:**
```bash
cd /app
node scripts/seed-dreamweaving-categories.mjs
```

## Alternative: Run Locally Against Production DB

If you need to run a seed quickly without waiting for deploy:

```bash
cd /home/rsalars/Projects/salarsu/frontend
DATABASE_URL="postgresql://user:pass@host/db" node scripts/seed-something.mjs
```

Get the `DATABASE_URL` from Coolify's environment variables.

## Related Files

- Build config: `frontend/nixpacks.toml`
- Prisma schema: `frontend/prisma/schema.prisma`
- Seed scripts: `frontend/scripts/*.mjs`
- API routes: `frontend/app/api/`
