#!/usr/bin/env bash
#
# Scaffold a Chrome DevTools MCP audit report folder.
#
# Usage:
#   ./scripts/utilities/new_devtools_audit.sh "<slug>" [--url "https://..."]
#
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: ./scripts/utilities/new_devtools_audit.sh \"<slug>\" [--url \"https://...\"]"
  exit 1
fi

SLUG="$1"
shift || true

URL=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      URL="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

DATE="$(date +%Y-%m-%d)"
SAFE_SLUG="$(echo "$SLUG" | tr '/' '-' | tr -cs '[:alnum:] _-' ' ' | sed 's/  */ /g' | sed 's/^ *//; s/ *$//')"
SAFE_SLUG="$(echo "$SAFE_SLUG" | tr ' ' '-')"
SAFE_SLUG="${SAFE_SLUG:-audit}"

OUT_DIR="$PROJECT_ROOT/audits/devtools/$DATE/$SAFE_SLUG"
ARTIFACTS_DIR="$OUT_DIR/artifacts"
mkdir -p "$ARTIFACTS_DIR"

REPORT="$OUT_DIR/report.md"
if [[ -f "$REPORT" ]]; then
  echo "Error: report already exists: $REPORT"
  exit 1
fi

cat > "$REPORT" <<EOF
# DevTools MCP Audit: $SAFE_SLUG

- Date: $DATE
- Target URL: ${URL:-"(fill in)"}
- Device profiles: Mobile first, then Desktop
- Cache: Disabled (at least one run)
- Browser profile: Clean (no extensions) recommended

## Scope

- [ ] Performance + trust audit
- [ ] Analytics integrity
- [ ] Checkout initiation (UI + provider scripts)

## Findings (summary)

- High:
- Medium:
- Low:

## Evidence (what you observed)

### Performance + trust
- LCP element + timing:
- CLS sources:
- Render blockers:
- Long tasks / main-thread blocking:
- Console warnings/errors:

### Analytics integrity (Network)
- /api/track counts:
  - page_view:
  - landing_view:
  - cta_click:
- Attribution keys present/persist:
- Duplicates/missing:

### Checkout initiation (Network + Console)
- Provider script loads (Stripe/PayPal) + statuses:
- Checkout-related requests + statuses:
- Duplicate initiations:
- Console errors during flow:

## Recommendations (actionable)

- 1.
- 2.
- 3.

## Notes

- Runbooks:
  - docs/CHROME_DEVTOOLS_MCP.md
  - web-ui/ANALYTICS.md
  - web-ui/PAYMENTS_WEBHOOKS.md

## Post-fix rerun (fill in after changes)

- Date:
- What changed:
- Result deltas:
  - Performance:
  - Analytics:
  - Checkout:
EOF

echo "Created: $REPORT"
echo "Artifacts dir: $ARTIFACTS_DIR"
