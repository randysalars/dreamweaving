"""
Zapier Webhook Client
Pushes social media posts to Zapier webhooks for automated scheduling.

Setup:
1. Go to zapier.com → Create Zap
2. Trigger: "Webhooks by Zapier" → "Catch Hook"
3. Copy the webhook URL
4. Add to .env: ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/hooks/catch/..."
5. Action: "Twitter" → "Create Tweet" (or X integration)
6. Map fields: content, scheduled_date, etc.
"""

import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ZapierResult:
    """Result of sending posts to Zapier."""
    success: bool
    sent_count: int
    failed_count: int
    message: str
    responses: List[Dict] = None


class ZapierWebhookClient:
    """
    Client for pushing social posts to Zapier webhooks.
    
    Zapier Setup Instructions:
    1. Create new Zap at zapier.com
    2. Trigger: "Webhooks by Zapier" → "Catch Hook"
    3. Copy webhook URL and add to ZAPIER_WEBHOOK_URL env var
    4. Action: Connect your social platform (Twitter/X, LinkedIn, etc.)
    5. Map the incoming data fields to the action
    
    The webhook receives JSON with these fields:
    - platform: twitter, linkedin, instagram, facebook
    - content: The post text
    - scheduled_date: YYYY-MM-DD
    - scheduled_time: HH:MM
    - hashtags: Space-separated hashtags
    - media_url: Optional image URL
    - link: Optional link to include
    """
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("ZAPIER_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError(
                "ZAPIER_WEBHOOK_URL not set. "
                "Get your webhook URL from Zapier and add it to .env"
            )
    
    def send_post(self, post: Dict) -> Dict:
        """Send a single post to Zapier webhook."""
        try:
            response = requests.post(
                self.webhook_url,
                json=post,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"✅ Sent to Zapier: {post.get('platform')} - {post.get('scheduled_date')}")
            return {"success": True, "response": response.json() if response.text else {}}
        except requests.RequestException as e:
            logger.error(f"❌ Zapier error: {e}")
            return {"success": False, "error": str(e)}
    
    def send_posts_from_file(
        self, 
        json_path: Path, 
        platform_filter: str = None,
        dry_run: bool = False
    ) -> ZapierResult:
        """
        Send all posts from a JSON file to Zapier.
        
        Args:
            json_path: Path to zapier_social_posts.json
            platform_filter: Only send posts for this platform (e.g., "twitter")
            dry_run: If True, validate without sending
            
        Returns:
            ZapierResult with summary
        """
        with open(json_path, 'r') as f:
            posts = json.load(f)
        
        if platform_filter:
            posts = [p for p in posts if p.get('platform') == platform_filter]
            logger.info(f"Filtered to {len(posts)} {platform_filter} posts")
        
        sent = 0
        failed = 0
        responses = []
        
        for post in posts:
            if dry_run:
                logger.info(f"[DRY RUN] Would send: {post.get('platform')} - {post.get('post_type')}")
                sent += 1
                continue
            
            result = self.send_post(post)
            responses.append(result)
            
            if result.get("success"):
                sent += 1
            else:
                failed += 1
        
        return ZapierResult(
            success=failed == 0,
            sent_count=sent,
            failed_count=failed,
            message=f"Sent {sent} posts to Zapier" + (f" ({failed} failed)" if failed else ""),
            responses=responses
        )


def push_to_zapier(
    product_dir: str,
    platform: str = None,
    webhook_url: str = None,
    dry_run: bool = False
) -> ZapierResult:
    """
    Convenience function to push a product's social posts to Zapier.
    
    Args:
        product_dir: Path to product directory with output/marketing/
        platform: Optional platform filter (twitter, linkedin, etc.)
        webhook_url: Optional webhook URL (uses env var if not provided)
        dry_run: If True, validate without sending
        
    Returns:
        ZapierResult
    """
    json_path = Path(product_dir) / "output" / "marketing" / "zapier_social_posts.json"
    
    if not json_path.exists():
        return ZapierResult(
            success=False,
            sent_count=0,
            failed_count=0,
            message=f"No posts file found at {json_path}"
        )
    
    client = ZapierWebhookClient(webhook_url)
    return client.send_posts_from_file(json_path, platform, dry_run)


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Push social posts to Zapier webhook")
    parser.add_argument("--product-dir", "-d", required=True, help="Product directory")
    parser.add_argument("--platform", "-p", help="Filter by platform (twitter, linkedin, etc.)")
    parser.add_argument("--webhook-url", "-w", help="Zapier webhook URL")
    parser.add_argument("--dry-run", action="store_true", help="Validate without sending")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    result = push_to_zapier(
        args.product_dir,
        platform=args.platform,
        webhook_url=args.webhook_url,
        dry_run=args.dry_run
    )
    
    print(f"\n{'='*50}")
    print(f"Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"Message: {result.message}")
    print(f"{'='*50}")
