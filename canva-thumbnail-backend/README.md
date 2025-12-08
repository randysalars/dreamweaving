# Canva Thumbnail Backend

Minimal Node/TypeScript backend that generates YouTube thumbnail variants using Canva Connect plus a RAG/LLM prompt to shape the design spec.

## Setup

1. Copy `.env.example` to `.env` and fill Canva + LLM credentials (optional YouTube tokens for upload).
2. Install deps: `npm install`.
3. Run dev server from this directory: `npm run dev` (build: `npm run build`; prod: `npm start`).

## Environment

Required:
- `CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_REFRESH_TOKEN`, `CANVA_REDIRECT_URI`
- `CANVA_API_BASE_URL` (default `https://api.canva.com`)
- `LLM_API_KEY`, `LLM_API_BASE_URL`
- `PORT` (default `4000`)

Optional:
- `CANVA_BRAND_KIT_ID`, `CANVA_THUMBNAIL_TEMPLATE_ID`
- YouTube upload: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, `YT_API_BASE_URL`

## API

`POST /api/thumbnails/generate`

```json
{
  "videoId": "abc123",
  "title": "Why GPUs Are Changing Everything",
  "topic": "AI hardware",
  "styleHints": ["high contrast", "tech neon"],
  "archetypes": ["curious", "bold"],
  "uploadToYouTube": false
}
```

Response:

```json
{
  "videoId": "abc123",
  "thumbnails": [
    { "variant": 1, "filePath": "thumbnails/abc123-v1.png" }
  ]
}
```

Generated images are saved under `thumbnails/` inside this project. If `uploadToYouTube` is `true` and YouTube tokens are provided, the first variant is uploaded via the Data API.

## Notes

- `applyThumbnailSpecToDesign` expects your Canva template to expose text variables named `TITLE` and `SUBTITLE`. Adjust the variable names if your template differs.
- Export polling is implemented with simple HTTP polling; tune timeouts in `canva/exports.ts` if your account is slower.
- LLM prompt and normalization live in `rag/thumbnailSpec.ts`; tweak defaults to match your brand palette or Dreamweaver rules.
