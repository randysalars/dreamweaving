"""
Product Category Detection and Styling

Automatically detects product category from title/topic and provides
appropriate styling, colors, disclaimers, and bonus suggestions.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ProductCategory(Enum):
    FINANCIAL = "financial"
    HEALTH = "health"
    BUSINESS = "business"
    RELATIONSHIPS = "relationships"
    PERSONAL_DEVELOPMENT = "personal_development"
    TECHNOLOGY = "technology"
    CREATIVE = "creative"
    GENERAL = "general"


@dataclass
class CategoryStyling:
    """Visual styling for a product category."""
    primary_color: str
    accent_color: str
    light_bg: str
    heading_color: str
    icon_emoji: str
    gradient_start: str
    gradient_end: str


@dataclass
class CategoryConfig:
    """Complete configuration for a product category."""
    category: ProductCategory
    styling: CategoryStyling
    disclaimer: str
    suggested_bonus_types: List[str]
    color_palette_name: str


# Category keyword mappings
CATEGORY_KEYWORDS = {
    ProductCategory.FINANCIAL: [
        "money", "wealth", "invest", "budget", "salary", "income", "debt",
        "savings", "retirement", "401k", "stock", "crypto", "finance",
        "financial", "freedom", "passive income", "real estate"
    ],
    ProductCategory.HEALTH: [
        "health", "wellness", "nutrition", "diet", "fitness", "exercise",
        "sleep", "mindfulness", "meditation", "yoga", "holistic", "healing",
        "body", "weight", "energy", "vitality", "stress", "anxiety"
    ],
    ProductCategory.BUSINESS: [
        "business", "startup", "entrepreneur", "marketing", "sales", "lead",
        "funnel", "conversion", "ecommerce", "saas", "agency", "consulting",
        "freelance", "productivity", "management", "leadership"
    ],
    ProductCategory.RELATIONSHIPS: [
        "relationship", "dating", "marriage", "love", "communication",
        "family", "parenting", "social", "network", "influence"
    ],
    ProductCategory.PERSONAL_DEVELOPMENT: [
        "growth", "mindset", "habits", "goals", "success", "motivation",
        "confidence", "self", "personal", "development", "life", "purpose"
    ],
    ProductCategory.TECHNOLOGY: [
        "coding", "programming", "software", "ai", "automation", "tech",
        "developer", "app", "web", "data", "cloud", "cyber"
    ],
    ProductCategory.CREATIVE: [
        "writing", "art", "design", "music", "photography", "video",
        "creative", "content", "storytelling", "craft"
    ]
}


# Category styling configurations
CATEGORY_STYLES = {
    ProductCategory.FINANCIAL: CategoryStyling(
        primary_color="#1e3a5f",
        accent_color="#2ecc71",
        light_bg="#f0fdf4",
        heading_color="#1e3a5f",
        icon_emoji="💰",
        gradient_start="#1e3a5f",
        gradient_end="#2c5282"
    ),
    ProductCategory.HEALTH: CategoryStyling(
        primary_color="#1a4731",
        accent_color="#22c55e",
        light_bg="#ecfdf5",
        heading_color="#1a4731",
        icon_emoji="🌿",
        gradient_start="#065f46",
        gradient_end="#10b981"
    ),
    ProductCategory.BUSINESS: CategoryStyling(
        primary_color="#1e293b",
        accent_color="#3b82f6",
        light_bg="#eff6ff",
        heading_color="#1e293b",
        icon_emoji="📈",
        gradient_start="#1e40af",
        gradient_end="#3b82f6"
    ),
    ProductCategory.RELATIONSHIPS: CategoryStyling(
        primary_color="#7c2d12",
        accent_color="#f97316",
        light_bg="#fff7ed",
        heading_color="#7c2d12",
        icon_emoji="💕",
        gradient_start="#c2410c",
        gradient_end="#fb923c"
    ),
    ProductCategory.PERSONAL_DEVELOPMENT: CategoryStyling(
        primary_color="#581c87",
        accent_color="#a855f7",
        light_bg="#faf5ff",
        heading_color="#581c87",
        icon_emoji="🚀",
        gradient_start="#7e22ce",
        gradient_end="#a855f7"
    ),
    ProductCategory.TECHNOLOGY: CategoryStyling(
        primary_color="#0f172a",
        accent_color="#06b6d4",
        light_bg="#ecfeff",
        heading_color="#0f172a",
        icon_emoji="💻",
        gradient_start="#0891b2",
        gradient_end="#22d3ee"
    ),
    ProductCategory.CREATIVE: CategoryStyling(
        primary_color="#831843",
        accent_color="#ec4899",
        light_bg="#fdf2f8",
        heading_color="#831843",
        icon_emoji="🎨",
        gradient_start="#be185d",
        gradient_end="#f472b6"
    ),
    ProductCategory.GENERAL: CategoryStyling(
        primary_color="#374151",
        accent_color="#6366f1",
        light_bg="#f9fafb",
        heading_color="#374151",
        icon_emoji="📚",
        gradient_start="#4f46e5",
        gradient_end="#818cf8"
    )
}


# Category-specific disclaimers
CATEGORY_DISCLAIMERS = {
    ProductCategory.FINANCIAL: (
        "This publication is designed to provide accurate and authoritative information in regard to the "
        "subject matter covered. It is sold with the understanding that the publisher is not engaged in "
        "rendering legal, accounting, or other professional services. If legal advice or other expert "
        "assistance is required, the services of a competent professional should be sought. "
        "Past performance is not indicative of future results. Individual results may vary."
    ),
    ProductCategory.HEALTH: (
        "The content shared in this book is for informational purposes only and is not a substitute for "
        "professional medical advice, diagnosis, or treatment. Always seek the advice of your physician "
        "or other qualified health provider with any questions you may have regarding a medical condition. "
        "Never disregard professional medical advice or delay in seeking it because of something you have read here. "
        "If you think you may have a medical emergency, call your doctor or emergency services immediately."
    ),
    ProductCategory.BUSINESS: (
        "Every effort has been made to accurately represent this product and its potential. There is no guarantee "
        "that you will earn any money using the techniques and ideas in these materials. Examples in these materials "
        "are not to be interpreted as a promise or guarantee of earnings. Earning potential is entirely dependent on "
        "the person using our product, ideas and techniques. Your level of success in attaining similar results "
        "depends on the time you devote, your knowledge and skills, and many other factors."
    ),
    ProductCategory.RELATIONSHIPS: (
        "The advice and strategies contained in this book may not be suitable for every situation. This work is sold "
        "with the understanding that the author is not engaged in rendering psychological, therapeutic, or other "
        "professional services. If professional assistance is required, seek the services of a competent professional. "
        "Individual results and experiences may vary significantly."
    ),
    ProductCategory.GENERAL: (
        "Every effort has been made to accurately represent this product and its potential. Individual results vary and "
        "are not guaranteed. The information provided is for educational and informational purposes only. "
        "You should not rely solely on this information as a substitute for professional advice."
    )
}


# Suggested bonus types by category
CATEGORY_BONUSES = {
    ProductCategory.FINANCIAL: [
        "Budget Template Spreadsheet",
        "Investment Calculator",
        "Debt Payoff Planner",
        "Net Worth Tracker",
        "Spending Audit Worksheet"
    ],
    ProductCategory.HEALTH: [
        "Meal Planning Template",
        "Workout Log",
        "Sleep Tracker",
        "Guided Meditations",
        "Habit Tracker Journal",
        "Quick Reference Cards"
    ],
    ProductCategory.BUSINESS: [
        "Business Plan Template",
        "Marketing Checklist",
        "Email Swipe Files",
        "Sales Script Templates",
        "SOPs Library"
    ],
    ProductCategory.RELATIONSHIPS: [
        "Conversation Starters",
        "Date Ideas List",
        "Communication Worksheets",
        "Conflict Resolution Guide"
    ],
    ProductCategory.PERSONAL_DEVELOPMENT: [
        "Goal Setting Workbook",
        "Daily Reflection Journal",
        "Habit Tracker",
        "Vision Board Template",
        "Affirmations Audio"
    ],
    ProductCategory.TECHNOLOGY: [
        "Code Snippets Library",
        "Cheat Sheets",
        "Project Templates",
        "Tool Comparison Guide"
    ],
    ProductCategory.CREATIVE: [
        "Prompt Library",
        "Template Pack",
        "Inspiration Gallery",
        "Portfolio Templates"
    ]
}


def detect_category(title: str, description: str = "") -> ProductCategory:
    """
    Detect product category from title and description.
    
    Args:
        title: Product title
        description: Optional product description
        
    Returns:
        Detected ProductCategory
    """
    text = f"{title} {description}".lower()
    
    # Count keyword matches for each category
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return ProductCategory.GENERAL
    
    # Return category with highest score
    return max(scores.keys(), key=lambda c: scores[c])


def get_category_config(category: ProductCategory) -> CategoryConfig:
    """Get complete configuration for a category."""
    return CategoryConfig(
        category=category,
        styling=CATEGORY_STYLES.get(category, CATEGORY_STYLES[ProductCategory.GENERAL]),
        disclaimer=CATEGORY_DISCLAIMERS.get(category, CATEGORY_DISCLAIMERS[ProductCategory.GENERAL]),
        suggested_bonus_types=CATEGORY_BONUSES.get(category, CATEGORY_BONUSES.get(ProductCategory.GENERAL, [])),
        color_palette_name=category.value.replace("_", " ").title()
    )


def get_config_for_product(title: str, description: str = "") -> CategoryConfig:
    """
    Get complete category configuration for a product.
    
    Args:
        title: Product title
        description: Optional description
        
    Returns:
        CategoryConfig with styling, disclaimer, and bonus suggestions
    """
    category = detect_category(title, description)
    return get_category_config(category)


# Quick test
if __name__ == "__main__":
    test_products = [
        "Financial Freedom Blueprint",
        "Holistic Wellness Protocol", 
        "The Agency Accelerator",
        "Dating Mastery",
        "Goal Setting Masterclass",
        "Python for Data Science",
        "Creative Writing Workshop"
    ]
    
    for title in test_products:
        config = get_config_for_product(title)
        print(f"{config.styling.icon_emoji} {title}")
        print(f"   Category: {config.category.value}")
        print(f"   Colors: {config.styling.primary_color} / {config.styling.accent_color}")
        print(f"   Bonuses: {', '.join(config.suggested_bonus_types[:2])}...")
        print()
