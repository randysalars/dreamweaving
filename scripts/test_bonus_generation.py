import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.product_builder.packaging.bonus_generator import BonusGenerator

logging.basicConfig(level=logging.INFO)

def test_bonus_generation():
    templates_dir = Path("agents/product_builder/templates")
    # Use a temp output for test to avoid messing up specific product folders if they don't exist
    output_dir = Path("./products/financial_freedom_blueprints/output/bonuses_test") 
    
    generator = BonusGenerator(templates_dir, output_dir)
    
    bonuses = [
        {
            "title": "72-Hour Action Plan",
            "format": "pdf",
            "description": "A day-by-day implementation guide."
        },
        {
            "title": "Financial Clarity Worksheet",
            "format": "pdf", # Testing PDF generation for worksheet as well per logic
            "description": "Tools to map your current financial reality."
        }
    ]
    
    print("🚀 Starting Bonus Generation Test...")
    paths = generator.generate(bonuses)
    
    print("\n✅ Generation Complete. Generated Files:")
    for p in paths:
        print(f" - {p}")
        
    # Validation logic could actaually check file size/page count if libraries were available
    # For now, manual verification of the file or log output is key.

if __name__ == "__main__":
    test_bonus_generation()
