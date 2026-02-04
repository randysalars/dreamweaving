"""
XMCP Bridge for Dreamweaving Product Builder

Provides XMCP MCP integration for product launch tweets.
Falls back to direct Tweepy API when MCP not available.

Usage:
    from marketing.xmcp_bridge import post_product_launch
    
    result = post_product_launch(
        product_dir="products/my-product",
        use_xmcp=True  # Prefer XMCP when available
    )
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class XMCPPostResult:
    """Result of posting via XMCP or fallback."""
    success: bool
    method: str  # "xmcp" or "tweepy"
    posted_count: int
    failed_count: int
    message: str
    tweet_ids: List[str] = None
    errors: List[str] = None


def check_xmcp_available() -> bool:
    """Check if XMCP MCP server is available."""
    import shutil
    return shutil.which("xmcp-server") is not None


def post_via_xmcp(content: str, reply_to: str = None) -> Dict:
    """
    Post via XMCP MCP tools.
    
    Note: This is a reference for agent usage. The actual posting
    happens via MCP tool calls, not direct Python invocation.
    
    Agent should call:
        post_tweet(text=content, reply_to=reply_to)
    """
    # This function is documentation for the agent workflow
    # Actual posting happens via MCP tool calls
    return {
        "method": "xmcp",
        "tool": "post_tweet",
        "params": {
            "text": content,
            "reply_to": reply_to
        },
        "note": "Execute via MCP: post_tweet(text='...', reply_to='...')"
    }


def post_thread_via_xmcp(tweets: List[str]) -> Dict:
    """
    Post thread via XMCP.
    
    Agent should call:
        create_thread(tweets=[tweet1, tweet2, ...])
    """
    return {
        "method": "xmcp",
        "tool": "create_thread",
        "params": {
            "tweets": tweets
        },
        "note": "Execute via MCP: create_thread(tweets=[...])"
    }


def generate_launch_tweets(product_dir: str) -> List[Dict]:
    """
    Generate launch tweets for a product.
    
    Reads from:
    - output/marketing/zapier_social_posts.json
    - output/marketing/launch_copy.md
    
    Returns list of tweet specs ready for posting.
    """
    product_path = Path(product_dir)
    tweets = []
    
    # Check for zapier format
    zapier_file = product_path / "output" / "marketing" / "zapier_social_posts.json"
    if zapier_file.exists():
        with open(zapier_file, 'r') as f:
            all_posts = json.load(f)
        
        twitter_posts = [p for p in all_posts if p.get('platform') == 'twitter']
        for post in twitter_posts:
            tweets.append({
                "content": post['content'],
                "hashtags": post.get('hashtags', ''),
                "scheduled_date": post.get('scheduled_date'),
                "post_type": post.get('post_type', 'single')
            })
    
    return tweets


def create_launch_workflow(product_dir: str) -> Dict:
    """
    Create a complete launch workflow for XMCP.
    
    Returns workflow spec that agent can execute.
    """
    tweets = generate_launch_tweets(product_dir)
    
    if not tweets:
        return {"error": "No tweets found for product"}
    
    # Group into threads vs singles
    threads = [t for t in tweets if 'thread' in t.get('post_type', '')]
    singles = [t for t in tweets if 'thread' not in t.get('post_type', '')]
    
    workflow = {
        "product_dir": product_dir,
        "total_tweets": len(tweets),
        "workflow_steps": []
    }
    
    # Schedule threads first
    if threads:
        thread_content = [t['content'] for t in threads]
        workflow["workflow_steps"].append({
            "action": "create_thread",
            "tweets": thread_content,
            "xmcp_call": f"create_thread(tweets={thread_content})"
        })
    
    # Then singles with delay
    for i, tweet in enumerate(singles):
        content = tweet['content']
        if tweet.get('hashtags'):
            content += f"\n\n{tweet['hashtags']}"
        
        workflow["workflow_steps"].append({
            "action": "post_tweet",
            "content": content,
            "delay_minutes": i * 30,  # Space out by 30 min
            "xmcp_call": f"post_tweet(text='{content[:50]}...')"
        })
    
    return workflow


# Main entry point for product launches
def post_product_launch(
    product_dir: str,
    use_xmcp: bool = True,
    dry_run: bool = False
) -> XMCPPostResult:
    """
    Post a product's launch tweets.
    
    If use_xmcp=True and XMCP available, generates workflow for agent.
    Otherwise falls back to direct Tweepy API via x_client.py.
    
    Args:
        product_dir: Path to product directory
        use_xmcp: Prefer XMCP MCP tools
        dry_run: Validate without posting
    
    Returns:
        XMCPPostResult with workflow or posting result
    """
    if use_xmcp and check_xmcp_available():
        workflow = create_launch_workflow(product_dir)
        
        if dry_run:
            logger.info(f"[DRY RUN] Would execute XMCP workflow: {len(workflow.get('workflow_steps', []))} steps")
            return XMCPPostResult(
                success=True,
                method="xmcp",
                posted_count=0,
                failed_count=0,
                message=f"Workflow ready: {workflow['total_tweets']} tweets",
                tweet_ids=[]
            )
        
        # Return workflow for agent to execute
        return XMCPPostResult(
            success=True,
            method="xmcp",
            posted_count=0,
            failed_count=0,
            message=f"Execute via XMCP: {json.dumps(workflow, indent=2)}",
            tweet_ids=[]
        )
    
    else:
        # Fallback to Tweepy
        from .x_client import post_to_x
        result = post_to_x(product_dir, dry_run=dry_run)
        return XMCPPostResult(
            success=result.success,
            method="tweepy",
            posted_count=result.posted_count,
            failed_count=result.failed_count,
            message=result.message,
            tweet_ids=result.tweet_ids,
            errors=result.errors
        )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Post product launch via XMCP")
    parser.add_argument("--product-dir", "-d", required=True, help="Product directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate without posting")
    parser.add_argument("--no-xmcp", action="store_true", help="Force Tweepy fallback")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    result = post_product_launch(
        args.product_dir,
        use_xmcp=not args.no_xmcp,
        dry_run=args.dry_run
    )
    
    print(f"\n{'='*50}")
    print(f"Method: {result.method}")
    print(f"Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"Message: {result.message}")
    print(f"{'='*50}")
