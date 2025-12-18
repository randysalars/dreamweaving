# Dreamweaver Email Template Canon

## Overview

These email templates implement the Dreamweaver correspondence philosophy:
- **Trust before asking**
- **Correspondence, not campaigns**
- **Silence is strategic**

## Templates

| Template | Purpose | Frequency |
|----------|---------|-----------|
| `initiation.html` | Welcome email (sets expectations) | Once per subscriber |
| `correspondence.html` | Core reflective letters | Every 7-14 days |
| `ritual.html` | Seasonal/sacred moments | 6-8 per year |
| `invitation.html` | Soft product offerings | Maximum 1/month |
| `gift-giver.html` | Gift purchase confirmation | Transactional |
| `gift-recipient.html` | Gift delivery | Transactional |

## System Rules

### Never Do
- Send more than 1 email in 7 days (except transactional)
- Use urgency language ("Limited time!", "Act now!")
- Stack multiple CTAs
- Sell in ritual emails
- Use aggressive re-engagement campaigns
- Over-personalize or announce segmentation

### Always Do
- Write as if to one person
- Make content reply-worthy
- Preserve dignity and choice
- Allow silence as part of the relationship
- Treat replies as sacred

## Variables

Templates use `{{VARIABLE_NAME}}` syntax for dynamic content.

### Common Variables
- `{{MAIN_REFLECTION}}` - Core letter content
- `{{SEASONAL_REFLECTION}}` - Season-specific content
- `{{BLESSING}}` - Short benediction (3-4 lines)
- `{{OFFERING_DESCRIPTION}}` - Product description (2-3 sentences)
- `{{OFFERING_URL}}` - Link to offering

### Gift Variables
- `{{GIFT_NAME}}` - Name of Dreamweaving
- `{{GIFT_DESCRIPTION}}` - Brief description
- `{{RECIPIENT_NAME}}` - Gift recipient
- `{{DELIVERY_DATE}}` - Scheduled delivery

## Email Types by Purpose

### Trust Building (90% of emails)
- Correspondence letters
- Ritual/seasonal emails
- No asks, no links

### Gentle Offering (10% of emails)
- Invitation emails only
- Only after trust established
- One link, one ask

## 12-Month Calendar Reference

| Month | Email Count | Types |
|-------|-------------|-------|
| January | 2 | ritual, correspondence |
| February | 1-2 | correspondence only |
| March | 2 | correspondence, ritual |
| April | 1-2 | ritual, correspondence |
| May | 1 | correspondence |
| June | 2 | correspondence, invitation |
| July | 1 | short correspondence |
| August | 2 | correspondence, invitation |
| September | 2 | correspondence, invitation |
| October | 1-2 | correspondence, ritual |
| November | 2 | correspondence, invitation |
| December | 3 | ritual, correspondence, invitation |

**Total: ~18-22 emails per year** (half of most newsletters)

## Integration with Resend

See `scripts/ai/email/email_scheduler.py` for:
- 7-day enforcement logic
- Segment management
- Calendar automation

## The Core Rule

> "We write when there is something worth sitting with."

If you wouldn't send it even if you could never measure it, don't send it.
