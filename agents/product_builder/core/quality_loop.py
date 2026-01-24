import logging
import math
from pathlib import Path
from typing import List, Dict, Tuple
from .llm import LLMClient

logger = logging.getLogger(__name__)

class QualityLoop:
    """
    Ensures the product meets physical standards (Length) and qualitative standards (Polish).
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """Reads the PDF and returns page count."""
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            return len(reader.pages)
        except ImportError:
            logger.warning("pypdf not installed. Assuming 0 pages.")
            return 0
        except Exception as e:
            logger.error(f"Failed to read PDF length: {e}")
            return 0

    def ensure_length(self, pdf_path: str, chapters: List[Dict], target_pages: int = 100) -> Tuple[List[Dict], bool]:
        """
        Checks if PDF meets target length. If not, expands chapters.
        Returns (New Chapters, Did_Modify_Bool).
        """
        current_pages = self.get_pdf_page_count(pdf_path)
        logger.info(f"📏 Length Check: {current_pages}/{target_pages} pages.")
        
        if current_pages >= target_pages:
            logger.info("✅ Length Target Met.")
            return chapters, False
        
        # Calculate Gap
        # Assumption: Words per page is constant-ish.
        total_words = sum(len(c.get('content', '').split()) for c in chapters)
        if current_pages == 0:
            words_per_page = 300 # Fallback default
        else:
            words_per_page = total_words / current_pages
            
        target_total_words = target_pages * words_per_page
        word_gap = target_total_words - total_words
        words_needed_per_chapter = int(word_gap / len(chapters)) * 1.2 # Add 20% buffer
        
        logger.info(f"⚠️ Length Target Missed. Gap: {word_gap} words. Expanding each chapter by ~{words_needed_per_chapter} words.")
        
        new_chapters = []
        for i, ch in enumerate(chapters):
            logger.info(f"   Expanding Chapter {i+1}...")
            new_content = self._run_expansion(ch, words_needed_per_chapter)
            ch['content'] = new_content
            new_chapters.append(ch)
            
        return new_chapters, True
        
    def polish_chapters(self, chapters: List[Dict]) -> List[Dict]:
        """
        Runs the 'Make it Better' pass on every chapter.
        """
        logger.info("✨ Starting Polishing Pass (Enhancing Quality)...")
        new_chapters = []
        for i, ch in enumerate(chapters):
            logger.info(f"   Polishing Chapter {i+1}: {ch.get('title')}...")
            new_content = self._run_polish(ch)
            ch['content'] = new_content
            new_chapters.append(ch)
        
        return new_chapters

    def _run_expansion(self, chapter: Dict, words_needed: int) -> str:
        template = self._load_template("chapter_expander")
        prompt = template.format(
            chapter_title=chapter.get('title'),
            words_needed=words_needed,
            current_content=chapter.get('content')
        )
        return self.llm.generate(prompt)

    def _run_polish(self, chapter: Dict) -> str:
        template = self._load_template("chapter_polisher")
        prompt = template.format(
            current_content=chapter.get('content')
        )
        return self.llm.generate(prompt)

    def _load_template(self, name: str) -> str:
        path = self.templates_dir / f"{name}.md"
        if path.exists():
            return path.read_text()
        return ""
