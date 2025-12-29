import re
import os
import logging

logger = logging.getLogger(__name__)

class MonetizationEngine:
    TRIGGER_PHRASE = r"make the most cash in the least amount of time"

    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.ad_template = self._load_template("inline_ad.md")
        self.lp_template = self._load_template("landing_page.md")

    def _load_template(self, filename: str) -> str:
        try:
            path = os.path.join(self.template_dir, filename)
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Template {filename} not found.")
            return ""

    def detect_monetization_sections(self, text_content: str) -> bool:
        """
        Scans text for the revenue-focused trigger phrase.
        Case-insensitive.
        """
        if not text_content:
            return False
            
        # Check for user specific trigger phrase
        found = bool(re.search(self.TRIGGER_PHRASE, text_content, re.IGNORECASE))
        if found:
            logger.info("Monetization trigger detected in content specs.")
        return found

    def generate_monetization_elements(self, topic: str, content_context: str = "") -> dict:
        """
        Generates the raw markdown for ads and landing pages based on the topic.
        Does NOT inject them; just returns the blocks.
        """
        # Simple formatting for now - could use AI to customize these further
        # In a real scenario, 'product_name' would come from a product DB or AI recommendation
        product_rec = "Dreamweaving Pro System"
        
        ad_content = self.ad_template.format(topic=topic)
        lp_content = self.lp_template.format(topic=topic, product_name=product_rec)
        
        return {
            "inline_ad": ad_content,
            "landing_page": lp_content,
            "product_recommendation": product_rec
        }

    def inject_placeholders(self, text_content: str) -> str:
        """
        If we wanted to modify the SOURCE formatting specs, we'd do it here.
        But typically we inject into the *generated* content.
        """
        return text_content
