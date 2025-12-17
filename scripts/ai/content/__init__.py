"""
Content Automation Agents Package.

This package contains automated content generation agents:

- AutoBlogWriter: Generate blog posts from session themes
- NewsletterBuilder: Create email campaigns from recent sessions
- CategoryCurator: Auto-organize and tag content
"""

from .auto_blog_writer import AutoBlogWriter, BlogPost
from .newsletter_builder import NewsletterBuilder, Newsletter
from .category_curator import CategoryCurator, ContentCategory

__all__ = [
    'AutoBlogWriter',
    'BlogPost',
    'NewsletterBuilder',
    'Newsletter',
    'CategoryCurator',
    'ContentCategory',
]
