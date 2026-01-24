
import sys
import logging
from pathlib import Path
import glob
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.product_builder.core.quality_loop import QualityLoop
from agents.product_builder.packaging.product_assembler import ProductAssembler, AssemblyConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("quality_loop_runner")

def load_chapters(manual_content_dir: Path):
    """Loads chapter markdown files and returns list of dicts."""
    chapters = []
    # Find all chapterX.md files
    files = sorted(glob.glob(str(manual_content_dir / "chapter*.md")))
    
    # Sort by number (chapter1, chapter2, ..., chapter10)
    # Default glob sort puts chapter10 before chapter2
    def extract_number(f):
        match = re.search(r'chapter(\d+)', f)
        return int(match.group(1)) if match else 0
    
    files = sorted(files, key=extract_number)
    
    for f_path in files:
        content = Path(f_path).read_text()
        # Extract title from first line "# Chapter X: Title"
        first_line = content.split('\n')[0]
        title = first_line.replace("#", "").strip()
        
        chapters.append({
            "title": title,
            "content": content,
            "filename": f_path # Keep track to save back
        })
        logger.info(f"Loaded: {title}")
        
    return chapters

def save_chapters(chapters):
    """Saves polished content back to files."""
    for ch in chapters:
        path = ch['filename']
        Path(path).write_text(ch['content'])
        logger.info(f"Saved polished content to: {path}")

def main():
    base_dir = Path("/home/rsalars/Projects/dreamweaving")
    product_dir = base_dir / "products/financial_freedom_blueprints"
    manual_content_dir = product_dir / "manual_content"
    output_dir = product_dir / "output"
    pdf_path = output_dir / "Financial_Freedom_Blueprints.pdf"
    templates_dir = base_dir / "agents/product_builder/templates"
    
    logger.info("🚀 Starting Quality Loop on Financial Freedom Blueprints...")
    
    # 1. Load Chapters
    chapters = load_chapters(manual_content_dir)
    
    # 2. Initialize Quality Loop
    loop = QualityLoop(templates_dir)
    
    # 3. Length Guard
    logger.info(f"📏 Checking Length (Target: 100 pages)... Current PDF: {pdf_path}")
    chapters, expanded = loop.ensure_length(str(pdf_path), chapters, target_pages=100)
    
    if expanded:
        logger.info("⚠️ Expanded chapters to meet length requirement.")
        save_chapters(chapters)
    else:
        logger.info("✅ Length requirement met.")

    # 4. Polish Pass
    logger.info("💎 Running 'Make It Better' Polish Pass...")
    chapters = loop.polish_chapters(chapters)
    save_chapters(chapters)
    
    # 5. Re-Assemble PDF
    logger.info("📄 Re-Assembling Final PDF...")
    
    # Using the Assembler
    config = AssemblyConfig(
        title="Financial Freedom Blueprints",
        author="SalarsNet",
        output_dir=output_dir,
        generate_pdf=True,
        generate_visuals=False, # Skip visuals for speed, we assume they exist or use default
        generate_audio=False,
        generate_video=False
    )
    
    assembler = ProductAssembler(templates_dir)
    # We need to map our simple chapters back to what assembler expects (dict)
    # assembler expects dicts with 'title', 'content'
    # load_chapters returns exactly that.
    
    # Note: Visuals might be missing if we use raw Assembler without VisualDirector run.
    # But PDFGenerator handles missing visuals gracefully usually.
    
    result = assembler.assemble(chapters, config)
    
    if result.success:
        logger.info(f"✅ FINAL SUCCESS! PDF: {result.pdf_path}")
    else:
        logger.error(f"❌ Assmebly Failed: {result.errors}")

if __name__ == "__main__":
    main()
