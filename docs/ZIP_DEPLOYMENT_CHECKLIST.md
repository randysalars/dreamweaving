# Digital Product ZIP Deployment Checklist

> **Last Updated**: Jan 28, 2026  
> **Discovered via**: Consciousness Expansion Audio Pack deployment debugging

This checklist covers the complete process for deploying a digital product ZIP to SalarsNet and making it available for download via the Love Offering system.

---

## ⚠️ CRITICAL: Two-Table Architecture

The SalarsNet platform uses **TWO database tables** to track digital product download URLs:

| Table | Column | Purpose |
|-------|--------|---------|
| `products` | `digital_file_url` | Product catalog (store listings) |
| `dreamweavings` | `audio_url` | Love Offering download system |

**Both tables MUST be updated for downloads to work!**

---

## Quick Reference

### Correct File Path
```
/home/rsalars/Projects/salarsu/public/downloads/products/{ZipFilename}.zip
```

### Correct URL Pattern
```
https://salars.net/downloads/products/{ZipFilename}.zip
```

### Production Database
- **Host**: `10.0.1.7`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`

---

## Step-by-Step Deployment

### Phase 1: Create the ZIP Bundle

1. **Build all assets** (audio, PDFs, bonus materials)
2. **Create ZIP** in the dreamweaving output folder:
   ```bash
   cd /home/rsalars/Projects/dreamweaving/products/{product_name}/output
   zip -r {ProductName}.zip *.pdf *.mp3 *.wav *.html bonus/
   ```
3. **Verify ZIP contents**:
   ```bash
   unzip -l {ProductName}.zip
   ```

### Phase 2: Deploy to Salarsu Repository

1. **Copy ZIP to correct location**:
   ```bash
   cp {ProductName}.zip /home/rsalars/Projects/salarsu/public/downloads/products/
   ```

2. **Verify file is in place**:
   ```bash
   ls -lh /home/rsalars/Projects/salarsu/public/downloads/products/{ProductName}.zip
   ```

3. **Commit and push**:
   ```bash
   cd /home/rsalars/Projects/salarsu
   git add public/downloads/products/{ProductName}.zip
   git commit -m "feat: add {ProductName} digital product ZIP"
   git push origin main
   ```

### Phase 3: Update Production Database

**Both tables must be updated!**

#### Option A: Using the Deployer (Recommended)
```python
from packaging.salarsu_deployer import deploy_product

result = deploy_product(
    salarsu_root="/home/rsalars/Projects/salarsu",
    zip_path="/path/to/Product.zip",
    product_name="Consciousness Expansion Audio Pack",
    product_slug="consciousness-expansion-audio-pack",
    description="Your product description...",
    price=29.99,
    auto_commit=True,
    auto_push=True
)
# Then run the generated SQL file against production
```

#### Option B: Manual SQL (Direct Database Update)
```bash
PGPASSWORD='YOUR_PASSWORD' psql -h 10.0.1.7 -p 5432 -U postgres -d postgres -c "
-- Update products table
UPDATE products 
SET digital_file_url = 'https://salars.net/downloads/products/{ProductName}.zip'
WHERE slug = '{product-slug}';

-- Update dreamweavings table
UPDATE dreamweavings 
SET audio_url = 'https://salars.net/downloads/products/{ProductName}.zip'
WHERE slug = '{product-slug}';
"
```

### Phase 4: Trigger Coolify Deployment

The file won't be available until Coolify redeploys the static assets.

**Option A: Wait for auto-deploy** (5-10 minutes after git push)

**Option B: Manual trigger** from Coolify dashboard

**Option C: Use deploy script**:
```bash
./scripts/ops/coolify-trigger-manual-deploy.sh
```

### Phase 5: Verification

1. **Test direct URL** (should return HTTP 200):
   ```bash
   curl -sI "https://www.salars.net/downloads/products/{ProductName}.zip" | head -3
   ```
   Expected: `HTTP/2 200` with `content-type: application/zip`

2. **Test download flow in browser**:
   - Go to product page: `https://www.salars.net/digital/{product-slug}`
   - Click "Download Now"
   - Complete Love Offering flow ($0 is fine)
   - Click download button
   - Verify "downloads remaining" counter decreases
   - Verify ZIP file downloads

3. **Verify both database tables**:
   ```bash
   PGPASSWORD='...' psql -h 10.0.1.7 -p 5432 -U postgres -d postgres -c "
   SELECT id, slug, digital_file_url FROM products WHERE slug = '{product-slug}';
   SELECT id, slug, audio_url FROM dreamweavings WHERE slug = '{product-slug}';
   "
   ```

---

## Common Issues

### Issue: "File not found" after updating products table only
**Cause**: Forgot to update `dreamweavings` table  
**Fix**: Update `dreamweavings.audio_url` with the same URL

### Issue: 404 after git push
**Cause**: Coolify hasn't redeployed yet  
**Fix**: Wait 5-10 minutes or manually trigger deploy

### Issue: Download counter decreases but no file downloads
**Cause**: File not in correct directory  
**Fix**: Ensure file is in `public/downloads/products/` NOT `content/lead-magnets/`

### Issue: ERR_BLOCKED_BY_CLIENT in browser
**Cause**: Ad blocker or browser extension  
**Fix**: This is client-side, not server-side. The download is working.

---

## File Location Reference

| Path | Purpose | Served At |
|------|---------|-----------|
| `public/downloads/products/` | ✅ CORRECT: Static ZIP files | `https://salars.net/downloads/products/` |
| `content/lead-magnets/` | ❌ LEGACY: API-served files | `/api/files/lead-magnets/` |

**Always use `public/downloads/products/` for new products!**

---

## Database Password

The production database password is stored securely. For agents:
```
See: Coolify dashboard → PostgreSQL service → Environment variables
```

---

## Automated Deployment (Future)

The `salarsu_deployer.py` module automates most of this:

```python
from packaging.salarsu_deployer import deploy_product

result = deploy_product(
    salarsu_root="/home/rsalars/Projects/salarsu",
    zip_path="/path/to/output/MyProduct.zip",
    product_name="My Product",
    product_slug="my-product",
    description="Description here...",
    price=29.99,
    sale_price=19.99,
    generate_cover_image=True,
    auto_commit=True,
    auto_push=True
)
```

This will:
1. Copy ZIP to `public/downloads/products/`
2. Generate cover image via DALL-E
3. Generate SQL for BOTH `products` AND `dreamweavings` tables
4. Commit and push to git
5. Return verification queries

---

*Created after debugging the Consciousness Expansion Audio Pack deployment (Jan 28, 2026)*
