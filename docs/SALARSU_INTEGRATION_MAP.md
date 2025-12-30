# Salarsu Integration Map

Reference for using dream categories, dreamweavings, and store functionality from the Salarsu project inside this repository.

## Locations
- Salarsu repo: `/home/rsalars/Projects/salarsu`
- Dreamweaving repo (this project): `/home/rsalars/Projects/dreamweaving`
- Salarsu frontend stack: Next (React 19), ESM, Prisma, Postgres (self-hosted via Coolify); path alias `@/` points at `frontend/`.

## Dreamweaving (categories + journeys)
- Data models: `frontend/prisma/schema.prisma`
  - `DreamweavingCategory`: `id`, `name`, `slug`, `description`, `color`, `icon`, `priority/display_order`, `page_source`, `keywords[]`, `parent_id`, timestamps, `children`, `dreamweavings`.
  - `Dreamweaving`: `id`, `slug`, `title`, `subtitle`, `description`, media URLs (`audio_url`, `video_url`, `thumbnail_url`, `subtitles_url`), `duration_minutes`, `category` (slug), `category_id`, JSON fields (`theme`, `archetypes`, `journey_concept`, `youtube_metadata`, `binaural_config`, `chapters`), `tags`, `status`, `featured`, `view_count`, `published_at`, timestamps, relation to `dreamweavingCategory`.
- Migrations: `frontend/migrations/dreamweaving_tables.sql`, `frontend/migrations/002_enhance_categories.sql`.
- API (Next Route Handlers):
  - `frontend/app/api/dreamweavings/route.js`: GET list (filters: `status`, `category`, `featured`, `limit`, `offset`), POST create (requires `DREAMWEAVING_API_TOKEN`).
  - `frontend/app/api/dreamweavings/[slug]/route.ts`: GET single (published unless authed), PATCH/DELETE with `DREAMWEAVING_API_TOKEN`.
  - `frontend/app/api/dreamweavings/categories/route.ts`: GET categories (options: `page_source`, `include_count`, `parent_only`), POST upsert with token.
  - `frontend/app/api/dreamweavings/categories/[slug]/route.ts`: GET category (+children, dreamweavings, pagination), PATCH/DELETE with token.
- Frontend usage patterns:
  - Listing: `frontend/app/dreamweavings/page.js`, `frontend/app/dreamweavings/index/page.tsx` fetch `/api/dreamweavings?status=published`.
  - Detail: `frontend/app/dreamweavings/[slug]/page.tsx` fetches via Prisma (includes category), renders client view `DreamweavingClient.tsx`.
  - Category view: `frontend/app/dreamweavings/category/[slug]/page.tsx` uses `/api/dreamweavings/categories/{slug}` with pagination.
  - Counts hook: `frontend/lib/useCategoryCounts.js` calls `/api/dreamweavings/categories?include_count=true`.
- Seed example: `frontend/insert_dreamweaving.mjs` (Prisma script creating a published journey).

## Store (products, categories, cart, orders)
- Data models: `frontend/prisma/schema.prisma` (and mirror in `/prisma/schema.prisma`)
  - `Product`, `Category`, `Subcategory`, `Tag`/`ProductTag`, `Cart`/`CartItem`, `Order`/`OrderItem`, plus `saved_for_later`.
- API (Next Route Handlers):
  - `frontend/app/api/store/route.js`: GET all products (joins categories/subcategories/tags), POST create product.
  - `frontend/app/api/store/[category]/route.js`: GET products by category id.
  - `frontend/app/api/store/search/route.js`: search products.
  - `frontend/app/api/store/categories/route.js`: categories list.
  - `frontend/app/api/categories/route.js`: categories + subcategories list; POST to add.
  - Cart endpoints under `frontend/app/api/cart/*` (add/update/remove/save-for-later/discount) and order endpoints under `frontend/app/api/orders`.
- Frontend usage patterns:
  - Storefront: `frontend/app/store/page.js` fetches `/api/categories` + `/api/store`.
  - Category page: `frontend/app/store/[category]/page.js` fetches `/api/categories` then `/api/store/{categoryId}`.
  - Product lists/search: `frontend/app/store/products/page.js`, `frontend/app/store/search/page.js`.
- Reusable helpers/config:
  - `frontend/lib/storeConfig.js`: static store category/subcategory metadata + SEO description generators.
  - `frontend/lib/storePageUtils.js`: helper to generate category/subcategory React pages (fetches `/api/categories` + `/api/store/{categoryId}`; filters by tags).
  - `frontend/lib/textUtils.js`: excerpt helpers; `frontend/app/lib/frontendImageUtils` for image fallbacks.
  - Seed data: `store/products.json` (sample products), `store/categories.json` (empty scaffold).

## Shared category config
- `frontend/lib/categoryConfig.js`: master content categories (includes `dreamweavings` entry).
- `frontend/lib/categoryUtils.js`: utilities for category/subcategory pages (breadcrumb helpers, page generators).

## Environment & dependencies
- Required env: `DATABASE_URL` (Postgres), `DREAMWEAVING_API_TOKEN` (protects dreamweaving create/update/delete and unpublished access).
- ESM project (`"type": "module"`); Node >= 18; Prisma Client `^6.11`.
- Path alias `@/` resolves to `frontend/` in Salarsu; adjust imports if reusing modules here.

## Ways to consume from this project
1) **HTTP APIs (fastest)**  
   - Run Salarsu app (or use deployed base) and call the routes above. Reads are public for published dreamweavings/products; writes require `Authorization: Bearer ${DREAMWEAVING_API_TOKEN}` and `DATABASE_URL` configured on the Salarsu side.
2) **Shared database**  
   - Copy `frontend/prisma/schema.prisma` (or SQL migrations) into this project and point both apps at the same `DATABASE_URL`. Use Prisma Client or direct SQL to query `dreamweaving*`, `products`, `categories`, carts, and orders.
3) **Module reuse (code sharing)**  
   - Symlink or `npm link` Salarsu `frontend/lib` into this repo to reuse `categoryConfig.js`, `storeConfig.js`, `storePageUtils.js`, `useCategoryCounts.js`, and UI components under `frontend/app/components`. Update imports to relative paths or mirror the `@/` alias; ensure this project has compatible React/Next/ESM setup if rendering UI.
4) **File-based seeds**  
   - Use `frontend/insert_dreamweaving.mjs` as a template for Prisma seeds; optionally import `store/products.json` for quick store bootstrap.

## Compatibility notes
- UI helpers expect a Next/React environment; if you only need data, prefer API or Prisma access.
- Store APIs mix Prisma and raw SQL; keep migrations in sync before cross-project writes.
- Dreamweaving GET returns only `status=published` unless the token is provided; drafts require auth.
