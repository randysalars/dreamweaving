"""
Upsell Recommender
Suggests related products, bundles, and upsell opportunities.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class UpsellType(Enum):
    BUNDLE = "bundle"           # Package products together
    UPGRADE = "upgrade"         # Premium version
    ADDON = "addon"             # Complementary product
    CROSS_SELL = "cross_sell"   # Related product
    DOWNSELL = "downsell"       # Lower-priced alternative


@dataclass
class UpsellRecommendation:
    """Single upsell recommendation."""
    type: UpsellType
    title: str
    description: str
    price_point: str
    timing: str  # When to present
    conversion_hook: str
    products: List[str] = field(default_factory=list)


@dataclass
class UpsellStrategy:
    """Complete upsell strategy for a product."""
    main_product: str
    recommendations: List[UpsellRecommendation]
    total_potential_revenue: str = ""


class UpsellRecommender:
    """
    Recommends upsell and cross-sell opportunities.
    
    Strategies:
    - Order bump (at checkout)
    - Post-purchase upsell
    - Bundle offers
    - Subscription upgrades
    """
    
    # Common upsell patterns by product type
    PATTERNS = {
        "course": {
            "addons": ["Coaching calls", "Community access", "Templates", "Worksheets"],
            "upgrades": ["Lifetime access", "VIP tier", "Certification"],
            "bundles": ["Course bundle", "Complete collection"]
        },
        "ebook": {
            "addons": ["Audio version", "Workbook", "Cheat sheets"],
            "upgrades": ["Video course", "Coaching"],
            "bundles": ["Book bundle", "Library access"]
        },
        "template": {
            "addons": ["Video tutorials", "Support", "Updates"],
            "upgrades": ["Template pack", "Agency license"],
            "bundles": ["Full toolkit"]
        }
    }
    
    def __init__(self):
        pass
    
    def generate_strategy(
        self,
        product_title: str,
        product_type: str,
        price: float,
        existing_products: List[Dict] = None
    ) -> UpsellStrategy:
        """
        Generate complete upsell strategy.
        
        Args:
            product_title: Main product name
            product_type: "course", "ebook", "template", etc.
            price: Main product price
            existing_products: Other products that could be bundled
            
        Returns:
            UpsellStrategy with recommendations
        """
        logger.info(f"💰 Generating upsell strategy for: {product_title}")
        
        recommendations = []
        
        # 1. Order Bump (at checkout)
        recommendations.append(self._generate_order_bump(product_title, product_type, price))
        
        # 2. Post-Purchase Upsell
        recommendations.append(self._generate_post_purchase_upsell(product_title, product_type, price))
        
        # 3. Bundle (if existing products)
        if existing_products:
            recommendations.append(self._generate_bundle(product_title, existing_products, price))
        
        # 4. Downsell (for abandoned carts)
        recommendations.append(self._generate_downsell(product_title, product_type, price))
        
        # 5. Subscription/Recurring
        recommendations.append(self._generate_subscription(product_title, product_type, price))
        
        strategy = UpsellStrategy(
            main_product=product_title,
            recommendations=recommendations,
            total_potential_revenue=f"${price * 2.5:.0f}+"
        )
        
        logger.info(f"✅ Generated {len(recommendations)} upsell recommendations")
        return strategy
    
    def _generate_order_bump(self, title: str, product_type: str, price: float) -> UpsellRecommendation:
        """Generate order bump suggestion."""
        bump_price = price * 0.3  # 30% of main product
        
        addons = self.PATTERNS.get(product_type, self.PATTERNS["course"])["addons"]
        addon = addons[0] if addons else "Quick-Start Guide"
        
        return UpsellRecommendation(
            type=UpsellType.ADDON,
            title=f"{addon} for {title}",
            description=f"Add {addon.lower()} to accelerate your results",
            price_point=f"${bump_price:.0f}",
            timing="At checkout (order bump)",
            conversion_hook=f"YES! Add {addon} for just ${bump_price:.0f}",
            products=[addon]
        )
    
    def _generate_post_purchase_upsell(self, title: str, product_type: str, price: float) -> UpsellRecommendation:
        """Generate post-purchase upsell."""
        upgrades = self.PATTERNS.get(product_type, self.PATTERNS["course"])["upgrades"]
        upgrade = upgrades[0] if upgrades else "Premium Access"
        upgrade_price = price * 2
        
        return UpsellRecommendation(
            type=UpsellType.UPGRADE,
            title=f"{title} - {upgrade}",
            description=f"Upgrade to {upgrade.lower()} for faster results and ongoing support",
            price_point=f"${upgrade_price:.0f}",
            timing="Immediately after purchase (OTO)",
            conversion_hook=f"Wait! Upgrade to {upgrade} for ${upgrade_price:.0f}",
            products=[upgrade]
        )
    
    def _generate_bundle(self, title: str, existing_products: List[Dict], price: float) -> UpsellRecommendation:
        """Generate bundle recommendation."""
        bundle_products = [p.get("title", p.get("name", "Product")) for p in existing_products[:2]]
        total_value = price + sum(p.get("price", price) for p in existing_products[:2])
        bundle_price = total_value * 0.7  # 30% discount
        
        return UpsellRecommendation(
            type=UpsellType.BUNDLE,
            title=f"Complete {title.split()[0]} Bundle",
            description=f"Get {title} plus {', '.join(bundle_products)} at a special bundled price",
            price_point=f"${bundle_price:.0f} (${total_value:.0f} value)",
            timing="On sales page or post-purchase",
            conversion_hook=f"SAVE 30% with the Complete Bundle",
            products=[title] + bundle_products
        )
    
    def _generate_downsell(self, title: str, product_type: str, price: float) -> UpsellRecommendation:
        """Generate downsell for abandoned carts."""
        downsell_price = price * 0.5
        
        return UpsellRecommendation(
            type=UpsellType.DOWNSELL,
            title=f"{title} - Essentials Only",
            description=f"Core content without the extras - perfect for getting started",
            price_point=f"${downsell_price:.0f}",
            timing="Exit intent or abandoned cart (24-48h)",
            conversion_hook=f"Not ready for the full program? Start with Essentials for ${downsell_price:.0f}",
            products=[f"{title} Core"]
        )
    
    def _generate_subscription(self, title: str, product_type: str, price: float) -> UpsellRecommendation:
        """Generate subscription/membership upsell."""
        monthly = price * 0.2
        
        return UpsellRecommendation(
            type=UpsellType.ADDON,
            title=f"{title.split()[0]} Insider Membership",
            description="Monthly updates, live Q&A, community access, and new content",
            price_point=f"${monthly:.0f}/month",
            timing="Post-purchase or as alternative to one-time",
            conversion_hook=f"Join the Insider community for ${monthly:.0f}/month",
            products=["Monthly membership", "Community access", "Live calls"]
        )
    
    def export_strategy(self, strategy: UpsellStrategy, output_path: Path) -> str:
        """Export strategy to markdown."""
        content = f"# Upsell Strategy: {strategy.main_product}\n\n"
        content += f"**Potential Revenue Increase:** {strategy.total_potential_revenue}\n\n"
        content += "---\n\n"
        
        for i, rec in enumerate(strategy.recommendations, 1):
            content += f"## {i}. {rec.type.value.title()}: {rec.title}\n\n"
            content += f"**Price:** {rec.price_point}\n\n"
            content += f"**Timing:** {rec.timing}\n\n"
            content += f"**Hook:** {rec.conversion_hook}\n\n"
            content += f"**Description:** {rec.description}\n\n"
            content += f"**Includes:** {', '.join(rec.products)}\n\n"
            content += "---\n\n"
        
        output_path.write_text(content)
        logger.info(f"✅ Strategy exported: {output_path}")
        return str(output_path)
