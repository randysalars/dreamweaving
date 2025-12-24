# Daily GA4 Email Report (Resend)

This repo includes an automated daily email report that pulls key GA4 KPIs and sends them via Resend.

## What the email contains (3–5 sections)

1. **Overview** (DoD + WoW): users, sessions, pageviews, engaged sessions, engagement rate, avg session duration  
2. **Acquisition**: top `source / medium` by sessions (with DoD change)  
3. **Conversions**: donation funnel counts (`donation_cta_click → paypal_opened → donation_success`), plus `donation_abandon` and donation value (sum)  
4. **Top pages**: top paths by views (yesterday)  

## Setup

### 0) Install dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 1) GA4 Data API access

The report uses the GA4 Data API (not Measurement Protocol).

- Create a Google Cloud service account and download its JSON key.
- Grant that service account **Viewer** access (or Analytics read access) to your GA4 property.
- Set:

```bash
export GA_PROPERTY_ID="516328829"  # Salarsnet (numeric GA4 property id)
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
```

### 2) Resend

- Create a Resend API key and verify the sender domain/address you will use in the `from` field.

```bash
export RESEND_API_KEY="re_..."
# Preferred: explicit sender for this report (must be verified in Resend)
export DAILY_ANALYTICS_FROM="Dreamweaving Reports <reports@salars.net>"
# Fallback (used elsewhere in the salarsu stack)
export FROM_EMAIL="Dreamweaving Reports <reports@salars.net>"
export DAILY_ANALYTICS_TO="randy@salrs.nert"
```

### 3) Timezone / site label (optional)

```bash
export DAILY_ANALYTICS_TZ="America/Denver"
export DAILY_ANALYTICS_SITE_NAME="salars.net"
```

## Run it

Dry-run (prints plain-text to stdout):

```bash
source venv/bin/activate
python -m scripts.analytics.daily_ga4_email --dry-run
```

Send:

```bash
python -m scripts.analytics.daily_ga4_email
```

Send (smoke test) even if GA4 Data API vars are not set:

```bash
python -m scripts.analytics.daily_ga4_email --allow-missing-ga
```

Override recipient/sender:

```bash
python -m scripts.analytics.daily_ga4_email --to you@example.com --from "Reports <reports@yourdomain.com>"
```

## Schedule it

The repo includes `cron/daily-ga4-email.sh`. Add it to your crontab:

```bash
crontab -e
```

Example (7:15am daily):

```cron
15 7 * * * /home/rsalars/Projects/dreamweaving/cron/daily-ga4-email.sh
```

If your server timezone is not the recipient timezone, prefer setting `TZ` in crontab or aligning server time.
