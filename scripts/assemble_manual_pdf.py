
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.product_builder.packaging.pdf_generator import PDFGenerator, PDFConfig

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def assemble():
    logger.info("🧵 Starting Manual Assembly...")
    
    # Paths
    base_dir = Path("products/financial_freedom_blueprints")
    input_dir = base_dir / "manual_content"
    output_dir = base_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "Financial_Freedom_Blueprints.pdf"
    
    # Read Chapters
    chapters = []
    
    # We explicitly list them to ensure order
    files = [f"chapter{i}.md" for i in range(1, 16)]
    
    for filename in files:
        path = input_dir / filename
        if not path.exists():
            logger.warning(f"Missing {filename}")
            continue
            
        text = path.read_text(encoding="utf-8")
        
        # Simple parsing: First line is title (if #), rest is content
        lines = text.splitlines()
        title = filename.replace(".md", "").title()
        content = text
        
        if lines and lines[0].startswith("# "):
            title = lines[0].replace("# ", "").strip()
            content = "\n".join(lines[1:]).strip()
            
        chapters.append({
            "title": title,
            "content": content,
            "key_takeaways": [] # We embedded them in the text
        })
        logger.info(f"   Loaded: {title}")

    # Config
    config = PDFConfig(
        title="Financial Freedom Blueprints",
        author="SalarsNet AI",
        output_path=str(output_file)
    )
    
    # Generator
    generator = PDFGenerator()
    
    logger.info("📄 Generating PDF...")
    try:
        final_path = generator.generate(chapters, config)
        logger.info(f"✅ Success! PDF saved to: {final_path}")
        print(f"OUTPUT_PATH: {final_path}")
    except Exception as e:
        logger.error(f"❌ Generation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    assemble()
