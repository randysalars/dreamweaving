"""
Marketing Module
Generators for landing pages, email sequences, social promo, and more.
"""

from .landing_page_generator import LandingPageGenerator, LandingPageContent
from .email_sequence_generator import EmailSequenceGenerator, EmailSequence, Email
from .social_promo_generator import SocialPromoGenerator, SocialPromoPackage, Platform
from .upsell_recommender import UpsellRecommender, UpsellStrategy
from .analytics_tracker import AnalyticsTracker, ProductMetrics

__all__ = [
    "LandingPageGenerator",
    "LandingPageContent",
    "EmailSequenceGenerator",
    "EmailSequence",
    "Email",
    "SocialPromoGenerator",
    "SocialPromoPackage",
    "Platform",
    "UpsellRecommender",
    "UpsellStrategy",
    "AnalyticsTracker",
    "ProductMetrics",
]
