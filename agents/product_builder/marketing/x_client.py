"""
Twitter/X Direct Posting Client
Posts directly to X using the v2 API.

Setup:
1. Go to https://developer.x.com
2. Create a project and app
3. Get your API keys (API Key, API Secret, Access Token, Access Token Secret)
4. Add to .env:
   X_API_KEY="..."
   X_API_SECRET="..."
   X_ACCESS_TOKEN="..."
   X_ACCESS_TOKEN_SECRET="..."

Free tier: 500 tweets/month
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import tweepy (Twitter SDK)
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logger.warning("tweepy not installed. Run: pip install tweepy")


@dataclass
class PostResult:
    """Result of posting to X."""
    success: bool
    posted_count: int
    failed_count: int
    message: str
    tweet_ids: List[str] = None
    errors: List[str] = None


class XClient:
    """
    Client for posting directly to X (Twitter) using v2 API.
    
    Requires tweepy: pip install tweepy
    
    Environment variables needed:
    - X_API_KEY (also called Consumer Key)
    - X_API_SECRET (also called Consumer Secret)
    - X_ACCESS_TOKEN
    - X_ACCESS_TOKEN_SECRET
    """
    
    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        access_token: str = None,
        access_token_secret: str = None
    ):
        if not TWEEPY_AVAILABLE:
            raise ImportError("Please install tweepy: pip install tweepy")
        
        self.api_key = api_key or os.getenv("X_API_KEY")
        self.api_secret = api_secret or os.getenv("X_API_SECRET")
        self.access_token = access_token or os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("X_ACCESS_TOKEN_SECRET")
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError(
                "Missing X API credentials. Set environment variables:\n"
                "X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET\n"
                "Get them from: https://developer.x.com"
            )
        
        # Create client
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
    
    # Twitter URL shortening: all URLs count as 23 characters
    TWITTER_URL_LENGTH = 23
    TWITTER_MAX_CHARS = 280
    
    @staticmethod
    def count_twitter_chars(text: str) -> int:
        """
        Count characters as Twitter does (weighted char counting).
        
        Twitter Rules:
        - All URLs (http/https) count as 23 characters regardless of actual length
        - Characters outside the BMP (emojis, etc.) count as 2 characters
        - Everything else counts as 1 character
        
        Returns:
            Effective character count for Twitter
        """
        import re
        
        # Find all URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        # Remove URLs from text for counting
        text_without_urls = re.sub(url_pattern, '', text)
        
        # Twitter counts non-BMP characters (emojis, etc.) as 2 chars
        char_count = 0
        for ch in text_without_urls:
            if ord(ch) > 0xFFFF:
                char_count += 2  # Non-BMP (most emojis)
            else:
                char_count += 1
        
        # Add 23 chars per URL
        char_count += len(urls) * XClient.TWITTER_URL_LENGTH
        
        return char_count
    
    def validate_tweet(self, text: str) -> tuple[bool, str, int]:
        """
        Validate tweet content before posting.
        
        Returns:
            (is_valid, error_message, char_count)
        """
        char_count = self.count_twitter_chars(text)
        
        if char_count > self.TWITTER_MAX_CHARS:
            return (
                False, 
                f"Tweet exceeds {self.TWITTER_MAX_CHARS} chars ({char_count} chars). "
                f"Content will be truncated or rejected.",
                char_count
            )
        
        return (True, "", char_count)
    
    def post_tweet(self, text: str, reply_to: str = None, allow_truncate: bool = False) -> Dict:
        """
        Post a single tweet.
        
        Args:
            text: Tweet content (max 280 chars, URLs count as 23)
            reply_to: Tweet ID to reply to (for threads)
            allow_truncate: If True, truncate long tweets; if False, error on over-limit
            
        Returns:
            Dict with tweet_id or error
        """
        try:
            is_valid, error_msg, char_count = self.validate_tweet(text)
            
            if not is_valid:
                if allow_truncate:
                    # Smart truncation: preserve URLs at the end
                    import re
                    url_pattern = r'https?://[^\s]+$'
                    url_match = re.search(url_pattern, text)
                    
                    if url_match:
                        # URL at end - truncate before it
                        url = url_match.group()
                        text_before = text[:url_match.start()].rstrip()
                        # Calculate how much space we have: 280 - 23 (url) - 3 (...)
                        max_text = self.TWITTER_MAX_CHARS - self.TWITTER_URL_LENGTH - 4
                        if len(text_before) > max_text:
                            text_before = text_before[:max_text] + "..."
                        text = f"{text_before} {url}"
                    else:
                        # No URL at end - simple truncation
                        text = text[:277] + "..."
                    
                    logger.warning(f"Tweet truncated from {char_count} to {self.count_twitter_chars(text)} chars")
                else:
                    logger.error(f"❌ Tweet rejected: {error_msg}")
                    return {"success": False, "error": error_msg, "char_count": char_count}
            
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to
            )
            
            tweet_id = response.data['id']
            logger.info(f"✅ Posted tweet: {tweet_id} ({char_count} chars)")
            return {"success": True, "tweet_id": tweet_id, "char_count": char_count}
            
        except tweepy.TweepyException as e:
            logger.error(f"❌ Tweet failed: {e}")
            return {"success": False, "error": str(e)}
    
    def post_thread(self, tweets: List[str], delay_seconds: float = 2.0) -> PostResult:
        """
        Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts
            delay_seconds: Delay between tweets (avoid rate limits)
            
        Returns:
            PostResult with summary
        """
        tweet_ids = []
        errors = []
        reply_to = None
        
        for i, text in enumerate(tweets):
            result = self.post_tweet(text, reply_to=reply_to)
            
            if result.get("success"):
                tweet_ids.append(result["tweet_id"])
                reply_to = result["tweet_id"]  # Chain the thread
            else:
                errors.append(f"Tweet {i+1}: {result.get('error')}")
            
            # Delay to avoid rate limits
            if i < len(tweets) - 1:
                time.sleep(delay_seconds)
        
        return PostResult(
            success=len(errors) == 0,
            posted_count=len(tweet_ids),
            failed_count=len(errors),
            message=f"Posted {len(tweet_ids)}/{len(tweets)} tweets",
            tweet_ids=tweet_ids,
            errors=errors if errors else None
        )
    
    def post_from_json(
        self, 
        json_path: Path, 
        post_now: bool = False,
        dry_run: bool = False
    ) -> PostResult:
        """
        Post Twitter content from a JSON file.
        
        Supports two formats:
        1. Flat list: [{"platform": "twitter", "content": "..."}]
        2. Thread object: {"platform": "twitter", "thread": [{"tweet": "..."}]}
        
        Args:
            json_path: Path to JSON file
            post_now: If True, post immediately (ignore scheduled dates)
            dry_run: If True, validate without posting
            
        Returns:
            PostResult
        """
        with open(json_path, 'r') as f:
            raw = json.load(f)
        
        # Normalize: handle both flat list and nested thread formats
        if isinstance(raw, dict):
            # Nested thread format: {"platform": "twitter", "thread": [{"tweet": "..."}]}
            if 'thread' in raw and isinstance(raw['thread'], list):
                texts = []
                for item in raw['thread']:
                    if isinstance(item, dict):
                        texts.append(item.get('tweet', item.get('content', '')))
                    elif isinstance(item, str):
                        texts.append(item)
                
                if not texts:
                    return PostResult(
                        success=True,
                        posted_count=0,
                        failed_count=0,
                        message="Thread found but no tweet content"
                    )
                
                logger.info(f"Found thread with {len(texts)} tweets")
                
                if dry_run:
                    for i, text in enumerate(texts):
                        logger.info(f"[DRY RUN] Tweet {i+1}/{len(texts)}: {text[:80]}...")
                    return PostResult(
                        success=True,
                        posted_count=len(texts),
                        failed_count=0,
                        message=f"[DRY RUN] Would post thread of {len(texts)} tweets",
                        tweet_ids=[f"dry_run_{i}" for i in range(len(texts))]
                    )
                
                return self.post_thread(texts)
            
            # Single post object: {"platform": "twitter", "content": "..."}
            elif 'content' in raw:
                all_posts = [raw]
            else:
                return PostResult(
                    success=False,
                    posted_count=0,
                    failed_count=0,
                    message=f"Unrecognized JSON format in {json_path}"
                )
        elif isinstance(raw, list):
            all_posts = raw
        else:
            return PostResult(
                success=False,
                posted_count=0,
                failed_count=0,
                message=f"Unexpected JSON type in {json_path}: {type(raw).__name__}"
            )
        
        # Process flat list format
        twitter_posts = [p for p in all_posts if isinstance(p, dict) and p.get('platform') == 'twitter']
        
        if not twitter_posts:
            return PostResult(
                success=True,
                posted_count=0,
                failed_count=0,
                message="No Twitter posts found in file"
            )
        
        logger.info(f"Found {len(twitter_posts)} Twitter posts")
        
        # Group by scheduled date for threads
        by_date = {}
        for post in twitter_posts:
            date = post.get('scheduled_date', 'unknown')
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(post)
        
        tweet_ids = []
        errors = []
        
        for date, posts in by_date.items():
            # Check if this is a thread (multiple posts same date/time)
            is_thread = len([p for p in posts if 'thread' in p.get('post_type', '')]) > 0
            
            if is_thread or len(posts) > 1:
                # Post as thread
                texts = [p['content'] for p in posts]
                if dry_run:
                    logger.info(f"[DRY RUN] Would post thread of {len(texts)} tweets for {date}")
                    tweet_ids.extend([f"dry_run_{i}" for i in range(len(texts))])
                else:
                    result = self.post_thread(texts)
                    tweet_ids.extend(result.tweet_ids or [])
                    if result.errors:
                        errors.extend(result.errors)
            else:
                # Single post
                for post in posts:
                    content = post['content']
                    if post.get('hashtags'):
                        content += f"\n\n{post['hashtags']}"
                    
                    if dry_run:
                        logger.info(f"[DRY RUN] Would post: {content[:50]}...")
                        tweet_ids.append("dry_run")
                    else:
                        result = self.post_tweet(content)
                        if result.get("success"):
                            tweet_ids.append(result["tweet_id"])
                        else:
                            errors.append(result.get("error"))
        
        return PostResult(
            success=len(errors) == 0,
            posted_count=len(tweet_ids),
            failed_count=len(errors),
            message=f"Posted {len(tweet_ids)} tweets" + (f" ({len(errors)} failed)" if errors else ""),
            tweet_ids=tweet_ids,
            errors=errors if errors else None
        )


def post_to_x(
    product_dir: str,
    post_now: bool = False,
    dry_run: bool = False
) -> PostResult:
    """
    Convenience function to post a product's Twitter content.
    
    Args:
        product_dir: Path to product directory
        post_now: Post immediately (ignore schedule)
        dry_run: Validate without posting
        
    Returns:
        PostResult
    """
    json_path = Path(product_dir) / "output" / "marketing" / "zapier_social_posts.json"
    
    if not json_path.exists():
        return PostResult(
            success=False,
            posted_count=0,
            failed_count=0,
            message=f"No posts file at {json_path}"
        )
    
    client = XClient()
    return client.post_from_json(json_path, post_now, dry_run)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Post to X/Twitter")
    parser.add_argument("--product-dir", "-d", required=True, help="Product directory")
    parser.add_argument("--post-now", action="store_true", help="Post immediately")
    parser.add_argument("--dry-run", action="store_true", help="Validate without posting")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    result = post_to_x(args.product_dir, args.post_now, args.dry_run)
    
    print(f"\n{'='*50}")
    print(f"Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"Message: {result.message}")
    if result.tweet_ids:
        print(f"Tweet IDs: {result.tweet_ids[:5]}...")
    if result.errors:
        print(f"Errors: {result.errors}")
    print(f"{'='*50}")
