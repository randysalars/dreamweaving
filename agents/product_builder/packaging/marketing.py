from typing import Dict
from ..schemas.blueprint import ProductBlueprint

class MarketingStrategist:
    """
    Generates the Launch Campaign assets.
    """
    
    def generate_launch_bundle(self, blueprint: ProductBlueprint) -> Dict[str, str]:
        """
        Returns a dict of filename -> content.
        """
        
        # 1. Email Sequence
        core_angle = blueprint.marketing.core_angles[0] if blueprint.marketing.core_angles else 'The Issue'
        emails = f"""# Launch Sequence for {blueprint.title}

## Email 1: The Problem
Subject: {core_angle}
Body:
Are you tired of {blueprint.audience.current_state}?
...

## Email 2: The Solution
Subject: How to fix it in {blueprint.promise.transformation_timeline}
...
"""

        # 2. Social Hooks
        hooks = f"""# Social Hooks
1. "{blueprint.promise.headline} - A thread 🧵"
2. "Stop doing [Old Way]. Start doing [New Way]."
"""

        return {
            "launch_emails.md": emails,
            "social_hooks.md": hooks
        }
