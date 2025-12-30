#!/usr/bin/env python3
"""
Spot Price Fetcher

Fetches live silver and gold spot prices via web scraping.
Primary source: APMEX
Fallback: JM Bullion

Features:
- In-memory caching (15 minute TTL)
- Database persistence for cross-process caching
- Graceful fallback between sources
- CLI mode for testing

Usage:
    from scripts.utilities.spot_price_fetcher import get_spot_prices

    prices = get_spot_prices()
    print(f"Silver: ${prices['silver']}")
    print(f"Gold: ${prices['gold']}")

CLI:
    python scripts/utilities/spot_price_fetcher.py
    python scripts/utilities/spot_price_fetcher.py --force
"""

import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
CACHE_TTL_MINUTES = 15
REQUEST_TIMEOUT = 10

# In-memory cache
_cache: Dict[str, Any] = {
    'silver': None,
    'gold': None,
    'source': None,
    'fetched_at': None
}


# =============================================================================
# SCRAPING FUNCTIONS
# =============================================================================

def _parse_price(text: str) -> Optional[float]:
    """Extract numeric price from text like '$29.50' or '29.50'."""
    if not text:
        return None
    # Remove $ and commas, extract number
    match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def _fetch_metals_dev() -> Optional[Dict[str, float]]:
    """
    Fetch spot prices from metals.dev API (free, no key required for basic use).

    This is the primary source - it's a reliable API that provides
    real-time precious metals prices.
    """
    url = "https://api.metals.dev/v1/latest"
    headers = {'User-Agent': DEFAULT_USER_AGENT}

    try:
        logger.debug(f"Fetching spot prices from metals.dev: {url}")
        # metals.dev provides free access for basic queries
        resp = requests.get(
            url,
            params={'api_key': 'demo', 'currency': 'USD', 'unit': 'toz'},
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        if resp.status_code == 200:
            data = resp.json()
            metals = data.get('metals', {})
            silver_price = metals.get('silver')
            gold_price = metals.get('gold')

            if silver_price and gold_price:
                logger.info(f"metals.dev spot prices: Silver=${silver_price}, Gold=${gold_price}")
                return {'silver': float(silver_price), 'gold': float(gold_price)}

        logger.warning(f"metals.dev: Unexpected response {resp.status_code}")
        return None

    except Exception as e:
        logger.error(f"metals.dev fetch failed: {e}")
        return None


def _scrape_goldprice_org() -> Optional[Dict[str, float]]:
    """
    Scrape spot prices from goldprice.org.

    This site provides JSON data embedded in the page that's easy to parse.
    """
    url = "https://www.goldprice.org/"
    headers = {'User-Agent': DEFAULT_USER_AGENT}

    try:
        logger.debug(f"Fetching spot prices from goldprice.org: {url}")
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        # Look for JSON data in script tags
        text = resp.text

        # goldprice.org embeds current prices in JavaScript
        silver_match = re.search(r'"silver_price"\s*:\s*([\d.]+)', text)
        gold_match = re.search(r'"gold_price"\s*:\s*([\d.]+)', text)

        # Also try alternate patterns
        if not silver_match:
            silver_match = re.search(r'silver.*?(\d+\.\d+)\s*/oz', text, re.I)
        if not gold_match:
            gold_match = re.search(r'gold.*?(\d{4}\.\d+)\s*/oz', text, re.I)

        silver_price = float(silver_match.group(1)) if silver_match else None
        gold_price = float(gold_match.group(1)) if gold_match else None

        if silver_price and gold_price:
            logger.info(f"goldprice.org spot prices: Silver=${silver_price}, Gold=${gold_price}")
            return {'silver': silver_price, 'gold': gold_price}
        elif silver_price:
            return {'silver': silver_price, 'gold': None}
        else:
            logger.warning("goldprice.org: Could not parse prices")
            return None

    except Exception as e:
        logger.error(f"goldprice.org scraping failed: {e}")
        return None


def _scrape_apmex() -> Optional[Dict[str, float]]:
    """
    Scrape spot prices from APMEX spot prices page.

    Note: APMEX may block automated requests. This is a fallback.
    """
    # Try the spot prices specific page which may have less protection
    url = "https://www.apmex.com/spot-prices"
    headers = {
        'User-Agent': DEFAULT_USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        logger.debug(f"Fetching spot prices from APMEX: {url}")
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

        if resp.status_code == 403:
            logger.warning("APMEX blocked request (403 Forbidden)")
            return None

        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        silver_price = None
        gold_price = None

        # Look for price data in the page
        for elem in soup.find_all(['span', 'div', 'td']):
            text = elem.get_text().strip()
            if 'silver' in text.lower() and '$' in text:
                price = _parse_price(text)
                if price and 10 < price < 100:
                    silver_price = price
            if 'gold' in text.lower() and '$' in text:
                price = _parse_price(text)
                if price and 1000 < price < 5000:
                    gold_price = price

        if silver_price and gold_price:
            logger.info(f"APMEX spot prices: Silver=${silver_price}, Gold=${gold_price}")
            return {'silver': silver_price, 'gold': gold_price}
        elif silver_price:
            return {'silver': silver_price, 'gold': None}
        else:
            logger.warning("APMEX: Could not parse spot prices from page")
            return None

    except requests.RequestException as e:
        logger.error(f"APMEX request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"APMEX parsing error: {e}")
        return None


def _scrape_jmbullion() -> Optional[Dict[str, float]]:
    """
    Scrape spot prices from JM Bullion homepage (fallback).

    JM Bullion displays spot prices prominently in the header.
    """
    url = "https://www.jmbullion.com/"
    headers = {'User-Agent': DEFAULT_USER_AGENT}

    try:
        logger.debug(f"Fetching spot prices from JM Bullion: {url}")
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        silver_price = None
        gold_price = None

        # JM Bullion typically has spot prices in a header bar
        # Look for elements with metal-specific classes or IDs
        for class_pattern in ['spot-price', 'metal-spot', 'live-price']:
            for elem in soup.find_all(class_=re.compile(class_pattern, re.I)):
                text = elem.get_text().lower()
                price = _parse_price(elem.get_text())
                if 'silver' in text and price and 10 < price < 100:
                    silver_price = price
                elif 'gold' in text and price and 1000 < price < 5000:
                    gold_price = price

        # Alternative: search for price patterns near metal names
        if not silver_price or not gold_price:
            page_text = soup.get_text()
            silver_match = re.search(r'silver.*?\$?([\d,]+\.\d{2})', page_text, re.I)
            gold_match = re.search(r'gold.*?\$?([\d,]+\.\d{2})', page_text, re.I)

            if silver_match and not silver_price:
                price = float(silver_match.group(1).replace(',', ''))
                if 10 < price < 100:
                    silver_price = price
            if gold_match and not gold_price:
                price = float(gold_match.group(1).replace(',', ''))
                if 1000 < price < 5000:
                    gold_price = price

        if silver_price and gold_price:
            logger.info(f"JM Bullion spot prices: Silver=${silver_price}, Gold=${gold_price}")
            return {'silver': silver_price, 'gold': gold_price}
        elif silver_price:
            logger.warning(f"JM Bullion: Got silver (${silver_price}) but not gold")
            return {'silver': silver_price, 'gold': None}
        else:
            logger.warning("JM Bullion: Could not parse spot prices from page")
            return None

    except requests.RequestException as e:
        logger.error(f"JM Bullion request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"JM Bullion parsing error: {e}")
        return None


def _scrape_kitco() -> Optional[Dict[str, float]]:
    """
    Scrape spot prices from Kitco (second fallback).

    Kitco is a reliable metals information site with clear spot displays.
    """
    url = "https://www.kitco.com/"
    headers = {'User-Agent': DEFAULT_USER_AGENT}

    try:
        logger.debug(f"Fetching spot prices from Kitco: {url}")
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        silver_price = None
        gold_price = None

        # Kitco has specific elements for metal prices
        page_text = soup.get_text()

        # Look for silver spot pattern
        silver_match = re.search(r'silver[:\s]+\$?([\d,]+\.\d{2})', page_text, re.I)
        gold_match = re.search(r'gold[:\s]+\$?([\d,]+\.\d{2})', page_text, re.I)

        if silver_match:
            price = float(silver_match.group(1).replace(',', ''))
            if 10 < price < 100:
                silver_price = price

        if gold_match:
            price = float(gold_match.group(1).replace(',', ''))
            if 1000 < price < 5000:
                gold_price = price

        if silver_price and gold_price:
            logger.info(f"Kitco spot prices: Silver=${silver_price}, Gold=${gold_price}")
            return {'silver': silver_price, 'gold': gold_price}
        elif silver_price:
            return {'silver': silver_price, 'gold': None}
        else:
            logger.warning("Kitco: Could not parse spot prices")
            return None

    except Exception as e:
        logger.error(f"Kitco scraping failed: {e}")
        return None


# =============================================================================
# DATABASE CACHING
# =============================================================================

def _get_db_cached_price(metal: str, max_age_minutes: int = 15) -> Optional[Dict[str, Any]]:
    """Get cached price from database if fresh enough."""
    try:
        from scripts.automation.state_db import StateDatabase
        db = StateDatabase()
        cached = db.get_latest_spot_price(metal)
        if cached:
            fetched_at = datetime.fromisoformat(cached['fetched_at'])
            age_minutes = (datetime.now() - fetched_at).total_seconds() / 60
            if age_minutes < max_age_minutes:
                logger.debug(f"Using DB cached {metal} price (age: {age_minutes:.1f} min)")
                return {
                    'price': cached['price_usd'],
                    'source': cached['source'],
                    'fetched_at': cached['fetched_at'],
                    'age_minutes': age_minutes
                }
        return None
    except Exception as e:
        logger.debug(f"DB cache check failed: {e}")
        return None


def _save_to_db_cache(metal: str, price: float, source: str):
    """Save fetched price to database cache."""
    try:
        from scripts.automation.state_db import StateDatabase
        db = StateDatabase()
        db.save_spot_price(metal, price, source)
        logger.debug(f"Saved {metal}=${price} to DB cache (source: {source})")
    except Exception as e:
        logger.warning(f"Failed to save to DB cache: {e}")


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def get_spot_prices(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get current silver and gold spot prices.

    Uses a multi-layer caching strategy:
    1. In-memory cache (fastest, same process)
    2. Database cache (persists across processes)
    3. Fresh scrape from web (APMEX -> JM Bullion -> Kitco)

    Args:
        force_refresh: If True, bypass all caches and fetch fresh data

    Returns:
        {
            'silver': 29.50,           # Price per oz or None
            'gold': 2050.00,           # Price per oz or None
            'source': 'apmex',         # Source site
            'fetched_at': '2025-...',  # ISO timestamp
            'cached': True/False,      # Whether from cache
            'cache_age_minutes': 5.2   # How old the cache is
        }
    """
    global _cache

    now = datetime.now()

    # Check in-memory cache first (unless forcing refresh)
    if not force_refresh and _cache['fetched_at']:
        age_minutes = (now - _cache['fetched_at']).total_seconds() / 60
        if age_minutes < CACHE_TTL_MINUTES:
            logger.debug(f"Using in-memory cache (age: {age_minutes:.1f} min)")
            return {
                'silver': _cache['silver'],
                'gold': _cache['gold'],
                'source': _cache['source'],
                'fetched_at': _cache['fetched_at'].isoformat(),
                'cached': True,
                'cache_age_minutes': round(age_minutes, 1)
            }

    # Check database cache next
    if not force_refresh:
        silver_cached = _get_db_cached_price('silver', CACHE_TTL_MINUTES)
        gold_cached = _get_db_cached_price('gold', CACHE_TTL_MINUTES)

        if silver_cached and gold_cached:
            # Update in-memory cache
            _cache['silver'] = silver_cached['price']
            _cache['gold'] = gold_cached['price']
            _cache['source'] = silver_cached['source']
            _cache['fetched_at'] = datetime.fromisoformat(silver_cached['fetched_at'])

            return {
                'silver': silver_cached['price'],
                'gold': gold_cached['price'],
                'source': silver_cached['source'],
                'fetched_at': silver_cached['fetched_at'],
                'cached': True,
                'cache_age_minutes': round(silver_cached['age_minutes'], 1)
            }

    # Fresh fetch required - try sources in order of reliability
    result = None
    source = None

    # Try metals.dev API first (most reliable)
    result = _fetch_metals_dev()
    if result and result.get('silver'):
        source = 'metals.dev'

    # Fallback to goldprice.org
    if not result or not result.get('silver'):
        result = _scrape_goldprice_org()
        if result and result.get('silver'):
            source = 'goldprice.org'

    # Fallback to APMEX
    if not result or not result.get('silver'):
        result = _scrape_apmex()
        if result and result.get('silver'):
            source = 'apmex'

    # Fallback to Kitco
    if not result or not result.get('silver'):
        result = _scrape_kitco()
        if result and result.get('silver'):
            source = 'kitco'

    # Handle failure case
    if not result or not result.get('silver'):
        logger.error("All spot price sources failed")
        return {
            'silver': None,
            'gold': None,
            'source': None,
            'fetched_at': now.isoformat(),
            'cached': False,
            'error': 'All sources failed - please provide spot price manually'
        }

    # Update caches
    _cache['silver'] = result['silver']
    _cache['gold'] = result.get('gold')
    _cache['source'] = source
    _cache['fetched_at'] = now

    # Save to database
    _save_to_db_cache('silver', result['silver'], source)
    if result.get('gold'):
        _save_to_db_cache('gold', result['gold'], source)

    return {
        'silver': result['silver'],
        'gold': result.get('gold'),
        'source': source,
        'fetched_at': now.isoformat(),
        'cached': False,
        'cache_age_minutes': 0
    }


def get_silver_spot(force_refresh: bool = False) -> Optional[float]:
    """Convenience function to get just the silver spot price."""
    prices = get_spot_prices(force_refresh=force_refresh)
    return prices.get('silver')


def get_gold_spot(force_refresh: bool = False) -> Optional[float]:
    """Convenience function to get just the gold spot price."""
    prices = get_spot_prices(force_refresh=force_refresh)
    return prices.get('gold')


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fetch live spot prices for silver and gold')
    parser.add_argument('--force', '-f', action='store_true', help='Force fresh fetch (bypass cache)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    parser.add_argument('--source', '-s', choices=['metals.dev', 'goldprice', 'apmex', 'jmbullion', 'kitco'],
                       help='Test specific source only')

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    print("\n=== Spot Price Fetcher ===\n")

    if args.source:
        # Test specific source
        print(f"Testing {args.source} only...\n")
        if args.source == 'apmex':
            result = _scrape_apmex()
        elif args.source == 'jmbullion':
            result = _scrape_jmbullion()
        else:
            result = _scrape_kitco()

        if result:
            print(f"Silver: ${result.get('silver', 'N/A')}")
            print(f"Gold: ${result.get('gold', 'N/A')}")
        else:
            print("Failed to fetch from source")
    else:
        # Normal operation
        prices = get_spot_prices(force_refresh=args.force)

        print(f"Silver Spot: ${prices.get('silver', 'N/A')}")
        print(f"Gold Spot: ${prices.get('gold', 'N/A')}")
        print(f"Source: {prices.get('source', 'N/A')}")
        print(f"Fetched: {prices.get('fetched_at', 'N/A')}")
        print(f"Cached: {prices.get('cached', False)}")
        if prices.get('cache_age_minutes'):
            print(f"Cache Age: {prices['cache_age_minutes']} minutes")
        if prices.get('error'):
            print(f"Error: {prices['error']}")

    print()
