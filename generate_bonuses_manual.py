
import logging
import sys
from pathlib import Path

# Setup Path
sys.path.append(str(Path(__file__).parent))

from agents.product_builder.packaging.bonus_generator import BonusGenerator

logging.basicConfig(level=logging.INFO)

def generate_manual_bonus():
    base_dir = Path("/home/rsalars/Projects/dreamweaving")
    templates_dir = base_dir / "agents/product_builder/templates"
    output_dir = base_dir / "products/financial_freedom_blueprints/output/bonuses"
    
    generator = BonusGenerator(templates_dir, output_dir)
    
    bonuses = [
        {
            "title": "The 30-Day Budget Bootcamp",
            "format": "pdf",
            "description": "A day-by-day workbook to reset your spending habits. Features daily challenges, tracking sheets, and reflection prompts."
        },
        {
            "title": "The Recession-Proof Investing Guide",
            "format": "pdf",
            "description": "A visual guide to asset allocation, risk management, and how to stay calm when the market crashes. Includes 'The Sleep Well at Night' portfolio model."
        },
        {
            "title": "The Salary Negotiation Blackbook",
            "format": "pdf",
            "description": "Word-for-word scripts to get paid what you are worth. Covers email templates, in-person scripts, and counter-offer strategies."
        }
    ]
    
    print("🚀 Starting Manual Bonus Generation...")
    paths = generator.generate(bonuses)
    
    print("\n✅ Bonus Generation Complete!")
    for p in paths:
        print(f"   📄 {p}")

if __name__ == "__main__":
    generate_manual_bonus()
