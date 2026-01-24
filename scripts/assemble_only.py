
import sys
import logging
from pathlib import Path
import glob
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.product_builder.packaging.product_assembler import ProductAssembler, AssemblyConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("assembler")

def load_chapters(manual_content_dir: Path):
    """Loads chapter markdown files and returns list of dicts."""
    chapters = []
    files = sorted(glob.glob(str(manual_content_dir / "chapter*.md")))
    
    def extract_number(f):
        match = re.search(r'chapter(\d+)', f)
        return int(match.group(1)) if match else 0
    
    files = sorted(files, key=extract_number)
    
    for f_path in files:
        content = Path(f_path).read_text()
        first_line = content.split('\n')[0]
        title = first_line.replace("#", "").strip()
        
        # Simple extraction of key takeaways (heuristic)
        takeaways = []
        if "## Key Takeaways" in content:
            # logic to extract if needed, but assembler handles raw content
            pass
            
        chapters.append({
            "title": title,
            "content": content,
            "key_takeaways": [] # Assembler ensures this key exists
        })
        logger.info(f"Loaded: {title}")
        
    return chapters

def main():
    base_dir = Path("/home/rsalars/Projects/dreamweaving")
    product_dir = base_dir / "products/financial_freedom_blueprints"
    manual_content_dir = product_dir / "manual_content"
    output_dir = product_dir / "output"
    templates_dir = base_dir / "agents/product_builder/templates"
    
    logger.info("📦 Starting Manual Assembly (No AI)...")
    
    chapters = load_chapters(manual_content_dir)
    logger.info(f"Loaded {len(chapters)} chapters.")
    
    config = AssemblyConfig(
        title="Financial Freedom Blueprints",
        author="SalarsNet",
        output_dir=output_dir,
        generate_pdf=True,
        generate_visuals=False,
        generate_audio=False,
        generate_video=False
    )
    
    assembler = ProductAssembler(templates_dir)
    result = assembler.assemble(chapters, config)
    
    if result.success:
        logger.info(f"✅ SUCCESS! PDF: {result.pdf_path}")
    else:
        logger.error(f"❌ Failed: {result.errors}")

if __name__ == "__main__":
    main()
