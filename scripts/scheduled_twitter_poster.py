#!/usr/bin/env python3
"""
Scheduled Twitter Poster

This script is meant to be run via cron. It checks for products that:
1. Have a scheduled post time in their .twitter_schedule file
2. The scheduled time has passed
3. Haven't been posted yet

The schedule file is created automatically when marketing content is generated.

Cron setup (runs every 15 minutes):
    */15 * * * * cd /home/rsalars/Projects/dreamweaving && /home/rsalars/Projects/dreamweaving/venv/bin/python scripts/scheduled_twitter_poster.py >> /var/log/twitter_poster.log 2>&1

Alternative: Run every hour
    0 * * * * cd /home/rsalars/Projects/dreamweaving && /home/rsalars/Projects/dreamweaving/venv/bin/python scripts/scheduled_twitter_poster.py >> /var/log/twitter_poster.log 2>&1
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
PRODUCTS_DIR = Path(__file__).parent.parent / "products"
SCHEDULE_FILENAME = ".twitter_schedule"
POSTED_FILENAME = ".twitter_posted"
DELAY_HOURS = 6  # Post 6 hours after product creation


def get_schedule_time(product_dir: Path) -> datetime | None:
    """Get the scheduled post time from the schedule file."""
    schedule_file = product_dir / SCHEDULE_FILENAME
    
    if not schedule_file.exists():
        return None
    
    try:
        data = json.loads(schedule_file.read_text())
        return datetime.fromisoformat(data['post_at'])
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def was_posted(product_dir: Path) -> bool:
    """Check if the product has already been posted to Twitter."""
    posted_file = product_dir / POSTED_FILENAME
    return posted_file.exists()


def mark_as_posted(product_dir: Path, tweet_ids: list[str]):
    """Mark the product as posted with tweet IDs."""
    posted_file = product_dir / POSTED_FILENAME
    posted_file.write_text(json.dumps({
        'posted_at': datetime.now().isoformat(),
        'tweet_ids': tweet_ids
    }, indent=2))


def has_social_content(product_dir: Path) -> bool:
    """Check if the product has social media content ready."""
    output_dir = product_dir / "output"
    social_json = output_dir / "marketing" / "zapier_social_posts.json"
    if not social_json.exists():
        social_json = output_dir / "zapier_social_posts.json"
    return social_json.exists()


def post_for_product(product_dir: Path) -> bool:
    """Post Twitter thread for a product."""
    from agents.product_builder.marketing.x_client import XClient
    
    output_dir = product_dir / "output"
    social_json = output_dir / "marketing" / "zapier_social_posts.json"
    if not social_json.exists():
        social_json = output_dir / "zapier_social_posts.json"
    
    logger.info(f"Posting Twitter thread for: {product_dir.name}")
    
    try:
        client = XClient()
        result = client.post_from_json(social_json, post_now=True, dry_run=False)
        
        if result.success:
            mark_as_posted(product_dir, result.tweet_ids or [])
            logger.info(f"✅ SUCCESS: Posted {result.posted_count} tweets for {product_dir.name}")
            if result.tweet_ids:
                logger.info(f"   Thread: https://twitter.com/i/status/{result.tweet_ids[0]}")
            return True
        else:
            logger.error(f"❌ FAILED: {result.errors}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception posting for {product_dir.name}: {e}")
        return False


def create_schedule_for_product(product_dir: Path, delay_hours: int = DELAY_HOURS):
    """
    Create a schedule file for a product.
    This should be called when marketing content is generated.
    """
    schedule_file = product_dir / SCHEDULE_FILENAME
    post_at = datetime.now() + timedelta(hours=delay_hours)
    
    schedule_file.write_text(json.dumps({
        'created_at': datetime.now().isoformat(),
        'post_at': post_at.isoformat(),
        'delay_hours': delay_hours,
        'product': product_dir.name
    }, indent=2))
    
    logger.info(f"📅 Scheduled Twitter post for {product_dir.name} at {post_at.strftime('%Y-%m-%d %H:%M')}")
    return post_at


def check_and_post_scheduled():
    """Main function: Check for products ready to post and post them."""
    logger.info("=" * 60)
    logger.info("🐦 SCHEDULED TWITTER POSTER - Checking for pending posts...")
    
    if not PRODUCTS_DIR.exists():
        logger.warning(f"Products directory not found: {PRODUCTS_DIR}")
        return
    
    now = datetime.now()
    posted_count = 0
    checked_count = 0
    
    for product_dir in PRODUCTS_DIR.iterdir():
        if not product_dir.is_dir() or product_dir.name.startswith('.'):
            continue
        
        # Skip if already posted
        if was_posted(product_dir):
            continue
        
        # Skip if no schedule file
        schedule_time = get_schedule_time(product_dir)
        if schedule_time is None:
            continue
        
        checked_count += 1
        
        # Skip if no social content
        if not has_social_content(product_dir):
            logger.warning(f"⚠️ {product_dir.name}: Scheduled but no social content found")
            continue
        
        # Check if it's time to post
        if now >= schedule_time:
            logger.info(f"⏰ {product_dir.name}: Time to post! (scheduled: {schedule_time.strftime('%H:%M')})")
            if post_for_product(product_dir):
                posted_count += 1
        else:
            time_until = schedule_time - now
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            logger.info(f"⏳ {product_dir.name}: Posting in {hours}h {minutes}m")
    
    logger.info(f"📊 Checked {checked_count} scheduled products, posted {posted_count}")
    logger.info("=" * 60)
    
    return posted_count


def main():
    """Entry point for scheduled posting."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduled Twitter Poster')
    parser.add_argument('--schedule', metavar='PRODUCT_DIR',
                        help='Schedule a new product for posting (creates .twitter_schedule)')
    parser.add_argument('--delay', type=int, default=DELAY_HOURS,
                        help=f'Delay in hours before posting (default: {DELAY_HOURS})')
    parser.add_argument('--force', metavar='PRODUCT_DIR',
                        help='Force post immediately (skip schedule check)')
    parser.add_argument('--status', action='store_true',
                        help='Show status of all scheduled posts')
    
    args = parser.parse_args()
    
    if args.schedule:
        # Schedule a new product
        product_dir = Path(args.schedule)
        if not product_dir.exists():
            logger.error(f"Product directory not found: {product_dir}")
            sys.exit(1)
        create_schedule_for_product(product_dir, args.delay)
        
    elif args.force:
        # Force post immediately
        product_dir = Path(args.force)
        if not product_dir.exists():
            logger.error(f"Product directory not found: {product_dir}")
            sys.exit(1)
        if not has_social_content(product_dir):
            logger.error(f"No social content found for {product_dir}")
            sys.exit(1)
        post_for_product(product_dir)
        
    elif args.status:
        # Show status
        logger.info("📋 Scheduled Post Status:")
        for product_dir in PRODUCTS_DIR.iterdir():
            if not product_dir.is_dir() or product_dir.name.startswith('.'):
                continue
            
            if was_posted(product_dir):
                posted_file = product_dir / POSTED_FILENAME
                data = json.loads(posted_file.read_text())
                logger.info(f"   ✅ {product_dir.name}: Posted at {data['posted_at']}")
            elif (schedule_time := get_schedule_time(product_dir)):
                now = datetime.now()
                if now >= schedule_time:
                    logger.info(f"   ⚠️ {product_dir.name}: OVERDUE (was {schedule_time})")
                else:
                    time_until = schedule_time - now
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    logger.info(f"   ⏳ {product_dir.name}: In {hours}h {minutes}m ({schedule_time.strftime('%H:%M')})")
            else:
                if has_social_content(product_dir):
                    logger.info(f"   📝 {product_dir.name}: Has content, not scheduled")
                    
    else:
        # Default: check and post scheduled items
        check_and_post_scheduled()


if __name__ == "__main__":
    main()
