# Velocity E-Commerce Strategy

## Overview

This document describes the "Velocity Catalog" strategy for coins, stamps, and supplies e-commerce. The core philosophy: **movement over variety, cash flow over margin perfection**.

## Core Principles

### The Master Rule
> "You are not selling coins. You are selling liquidity."

Every decision must answer: "Will this move in days, not months?"

### Three Pillars
1. **Fast turnover** (cash flow)
2. **Low dispute risk** (trust)
3. **Easy fulfillment** (time)

## Knowledge Base Structure

### Location: `knowledge/coins/`
| File | Purpose |
|------|---------|
| `morgan_dollar_guide.yaml` | Morgan dollar sorting & pricing |
| `peace_dollar_guide.yaml` | Peace dollar sorting & pricing |
| `junk_silver_guide.yaml` | 90% silver FV math & bundles |
| `mexican_silver_guide.yaml` | Libertads & circulation pesos |
| `bullion_sorting_rules.yaml` | Bullion vs numismatic classification |
| `supplies_catalog.yaml` | Repeat-purchase supplies |

### Location: `knowledge/ecommerce/`
| File | Purpose |
|------|---------|
| `product_catalog.yaml` | Master product structure |
| `pricing_strategy.yaml` | Pricing models & transparency |
| `products/*.yaml` | Individual product definitions |

## Pricing Models

### 1. Spot + Premium (Bullion)
```
Price = Spot price (live) + fixed premium + shipping
Example: Spot + $8.00 per Morgan Dollar
```

### 2. Face Value Multiplier (Junk Silver)
```
Price = Face Value × Multiplier
$1 FV = 0.715 oz silver
If spot = $25, melt = $17.88
Multiplier typically 18×-22×
```

### 3. Silver Content (Mexican/Foreign)
```
Price = Actual silver oz × spot + small premium
```

### 4. Fixed (Supplies)
```
Competitive singles, stronger margin on bundles
```

## MCP Server Tools

The `coin_rag_mcp_server.py` provides these tools:

| Tool | Purpose |
|------|---------|
| `coin_search` | Search knowledge base |
| `coin_key_date_check` | Check if date is key/semi-key |
| `coin_pricing_guide` | Get pricing model for product |
| `coin_bullion_sort` | Classify coin as bullion/numismatic |
| `coin_junk_silver_calc` | Calculate silver content from FV |
| `coin_listing_generator` | Generate listing language |
| `coin_bundle_recommendation` | Get bundle suggestions |

## Bullion vs Numismatic Sorting

### Quick Triage (3 Steps)
1. **Sort by date/mint** → Safe dates vs Questionable vs Key dates
2. **Condition sweep** → Remove shiny/lightly worn from safe pile
3. **Final bullion pile** → Flat detail, gray patina, honest wear

### "Looks Too Nice" Rule
Pull any coin with:
- Strong cartwheel luster
- AU or better appearance
- Clean fields or eye appeal

### Morgan Key Dates (NEVER BULLION)
- Any CC (Carson City) mintmark
- 1893-S, 1894, 1895 (any mint)

### Peace Key Dates (NEVER BULLION)
- 1921 (high relief)
- 1927-D
- 1928
- 1934-S, 1935-S

## Trust Signals

### Silver Trust Block (Every Product)
```
✓ All silver verified by weight & dimensions
✓ Photos show the exact item
✓ Authenticity guaranteed or full refund
✓ Ships within 24-48 hours
```

### Dealer Covenant
```
✓ No hype descriptions.
✓ Defects disclosed.
✓ Photos are of the exact item.
✓ Fair returns.
```

## Landing Pages

Located in salarsu frontend at `app/store/lp/`:

| Page | URL |
|------|-----|
| Silver Stacking Hub | `/store/lp/silver-stacking` |
| Junk Silver | `/store/lp/junk-silver` |
| Morgan Dollars | `/store/lp/morgan-dollars` |
| Preparedness Bundles | `/store/lp/preparedness-silver` |
| Coin Collecting | `/store/lp/coin-collecting` |

## Bundle Strategy

### Why Bundles Work
- Increase average order value
- Reduce decision fatigue
- Feel intentional and curated
- Convert better than singles

### Core Bundles
1. **Starter Silver Stack** - Morgan + $5 FV dimes
2. **Preparedness Stack** - 2 Peace + $10 FV mixed
3. **Sound Money Bundle** - Morgan + Peace + Mexican
4. **Junk Silver Roll Pack** - $20 FV mixed

## Listing Language

### Do Say
- Circulated
- Dates vary
- Bullion-grade
- Priced by silver content

### Never Say
- AU, XF, BU
- Choice, Rare
- Uncirculated
- Key date (for bullion)

## Two Vaults Mental Model

### Vault 1: Liquid Metal
- Junk silver, bullion-grade dollars, rounds & bars
- Strategy: **Sell for SPEED**
- Timing: **Now**

### Vault 2: Historical Value
- Key dates, high-grade, varieties, slabbed
- Strategy: **Sell for OUTCOMES**
- Timing: **Wait for calm markets**

**Golden Rule:** Never cross the streams.

## Integration Points

### From Store Page
The store homepage includes a "Curated Collections" section linking to all landing pages.

### From Footer
A "Shop" section in the footer links to:
- Store
- Silver Stacking
- Junk Silver
- Coin Collecting

### From Notion RAG
The knowledge base was derived from Notion page: "3. Coins, stamps, basic supplies — Curated, not broad"
