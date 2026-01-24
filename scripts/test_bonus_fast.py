import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.product_builder.packaging.bonus_generator import BonusGenerator

logging.basicConfig(level=logging.INFO)

def test_bonus_generation_fast():
    templates_dir = Path("agents/product_builder/templates")
    # Use a temp output for test
    output_dir = Path("./products/financial_freedom_blueprints/output/bonuses_test_fast") 
    
    # Mock WritersRoom to be fast
    with patch("agents.product_builder.packaging.bonus_generator.WritersRoom") as MockWritersRoom:
        # Configure mock instance
        mock_instance = MockWritersRoom.return_value
        # Return 2000 words of dummy text per chapter
        dummy_content = "This is a dummy sentence for testing bonus generation length. " * 200
        mock_instance.write_chapter.return_value = dummy_content
        
        generator = BonusGenerator(templates_dir, output_dir)
        
        # Test Data
        bonuses = [
            {
                "title": "72-Hour Action Plan",
                "format": "pdf",
                "description": "A day-by-day implementation guide."
            }
        ]
        
        print("🚀 Starting FAST Bonus Generation Test...")
        paths = generator.generate(bonuses)
        
        print("\n✅ Generation Complete. Generated Files:")
        for p in paths:
            print(f" - {p}")
            # Verify file exists
            if Path(p).exists():
                print(f"   ✓ File confirmed at {p}")
                size = Path(p).stat().st_size
                print(f"   ✓ File size: {size} bytes")
            else:
                print(f"   ❌ File missing!")

if __name__ == "__main__":
    test_bonus_generation_fast()
