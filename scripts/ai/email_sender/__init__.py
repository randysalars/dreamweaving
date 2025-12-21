"""
Dreamweaver Email System

Trust-based email scheduling and segmentation.

Core Philosophy:
- Trust before asking
- Correspondence, not campaigns
- Reply rate > open rate
- Silence is strategic
"""

from .email_scheduler import EmailScheduler, EmailType, Subscriber, EmailRecord

__all__ = [
    "EmailScheduler",
    "EmailType",
    "Subscriber",
    "EmailRecord"
]
