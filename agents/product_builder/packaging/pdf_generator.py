"""
PDF Generator
Creates professional PDF documents from product content.
Supports styled layouts, embedded visuals, and print-ready output.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PDFStyle:
    """Styling configuration for PDF generation."""
    font_family: str = "Inter"
    heading_font: str = "Inter"
    font_size: int = 11
    heading_color: str = "#2D3748"
    text_color: str = "#4A5568"
    accent_color: str = "#9F7AEA"
    page_margin: int = 72  # points (1 inch)
    line_height: float = 1.6


@dataclass
class PDFConfig:
    """Configuration for PDF generation."""
    title: str
    author: str = "SalarsNet"
    style: PDFStyle = None
    include_toc: bool = True
    include_cover: bool = True
    page_size: str = "letter"  # letter, a4
    output_path: str = None
    
    def __post_init__(self):
        if self.style is None:
            self.style = PDFStyle()


class PDFGenerator:
    """
    Generates professional PDFs from product content.
    
    Uses WeasyPrint or ReportLab for rendering.
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("./generated_pdfs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check which PDF libraries are available."""
        self.has_weasyprint = False
        self.has_reportlab = False
        
        try:
            import weasyprint
            self.has_weasyprint = True
            logger.info("WeasyPrint available")
        except ImportError:
            pass
        
        try:
            from reportlab.lib.pagesizes import letter
            self.has_reportlab = True
            logger.info("ReportLab available")
        except ImportError:
            pass
        
        if not self.has_weasyprint and not self.has_reportlab:
            logger.warning("No PDF library available. Install: pip install weasyprint")
    
    def generate(
        self, 
        chapters: List[Dict], 
        config: PDFConfig,
        visuals: Dict[str, str] = None
    ) -> str:
        """
        Generate a PDF from chapters.
        
        Args:
            chapters: List of chapter dicts with title, content, key_takeaways
            config: PDF configuration
            visuals: Map of section_id -> image path
            
        Returns:
            Path to generated PDF
        """
        output_path = config.output_path or str(
            self.output_dir / f"{self._slugify(config.title)}.pdf"
        )
        
        if self.has_weasyprint:
            return self._generate_weasyprint(chapters, config, visuals, output_path)
        
        # Try Puppeteer (Node.js) fallback
        try:
            return self._generate_puppeteer(chapters, config, visuals, output_path)
        except Exception as e:
            logger.warning(f"Puppeteer generation failed: {e}. Falling back to HTML/ReportLab.")
            
        if self.has_reportlab:
            return self._generate_reportlab(chapters, config, visuals, output_path)
        else:
            # Fallback: generate HTML that can be printed to PDF
            return self._generate_html_fallback(chapters, config, visuals, output_path)

    def _generate_puppeteer(
        self, 
        chapters: List[Dict], 
        config: PDFConfig,
        visuals: Dict[str, str],
        output_path: str
    ) -> str:
        """Generate PDF using Puppeteer script."""
        import subprocess
        import os
        
        # 1. Generate HTML source
        html_content = self._build_html(chapters, config, visuals)
        temp_html_path = output_path.replace(".pdf", ".temp.html")
        Path(temp_html_path).write_text(html_content, encoding="utf-8")
        
        # 2. Locate script
        script_path = Path(__file__).parent / "generate_pdf.cjs"
        if not script_path.exists():
            raise FileNotFoundError(f"Puppeteer script not found at {script_path}")
            
        # 3. Call Node.js
        cmd = ["node", str(script_path), temp_html_path, output_path]
        logger.info(f"Running Puppeteer: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Cleanup temp HTML if successful
        if Path(output_path).exists():
             try:
                 os.remove(temp_html_path)
             except:
                 pass
             logger.info(f"✅ PDF generated (Puppeteer): {output_path}")
             return output_path
        else:
            raise RuntimeError(f"Puppeteer finished but PDF not found. Output: {result.stdout} {result.stderr}")
    
    def _generate_weasyprint(
        self, 
        chapters: List[Dict], 
        config: PDFConfig,
        visuals: Dict[str, str],
        output_path: str
    ) -> str:
        """Generate PDF using WeasyPrint."""
        import weasyprint
        
        html = self._build_html(chapters, config, visuals)
        css = self._build_css(config.style)
        
        # Create PDF
        doc = weasyprint.HTML(string=html)
        stylesheet = weasyprint.CSS(string=css)
        doc.write_pdf(output_path, stylesheets=[stylesheet])
        
        logger.info(f"✅ PDF generated: {output_path}")
        return output_path
    
    def _generate_reportlab(
        self, 
        chapters: List[Dict], 
        config: PDFConfig,
        visuals: Dict[str, str],
        output_path: str
    ) -> str:
        """Generate PDF using ReportLab."""
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.colors import HexColor
        
        page_size = A4 if config.page_size == "a4" else letter
        doc = SimpleDocTemplate(output_path, pagesize=page_size)
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            textColor=HexColor(config.style.heading_color)
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=12,
            textColor=HexColor(config.style.heading_color)
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=config.style.font_size,
            leading=config.style.font_size * config.style.line_height,
            textColor=HexColor(config.style.text_color)
        )
        
        # Build content
        story = []
        
        # Cover page
        if config.include_cover:
            story.append(Spacer(1, 3*inch))
            story.append(Paragraph(config.title, title_style))
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"by {config.author}", body_style))
            story.append(PageBreak())
        
        # Chapters
        for chapter in chapters:
            story.append(Paragraph(chapter.get("title", "Chapter"), heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            content = chapter.get("content", "")
            for paragraph in content.split("\n\n"):
                if paragraph.strip():
                    story.append(Paragraph(paragraph, body_style))
                    story.append(Spacer(1, 0.1*inch))
            
            story.append(PageBreak())
        
        doc.build(story)
        logger.info(f"✅ PDF generated: {output_path}")
        return output_path
    
    def _generate_html_fallback(
        self, 
        chapters: List[Dict], 
        config: PDFConfig,
        visuals: Dict[str, str],
        output_path: str
    ) -> str:
        """Generate HTML that can be printed to PDF."""
        html = self._build_html(chapters, config, visuals)
        css = self._build_css(config.style)
        
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{config.title}</title>
    <style>{css}</style>
</head>
<body>
{html}
</body>
</html>
"""
        
        html_path = output_path.replace(".pdf", ".html")
        Path(html_path).write_text(full_html)
        
        logger.info(f"📄 HTML generated (print to PDF): {html_path}")
        return html_path
    
    def _build_html(
        self, 
        chapters: List[Dict], 
        config: PDFConfig,
        visuals: Dict[str, str]
    ) -> str:
        """Build HTML content from chapters."""
        html_parts = []
        
        # Cover
        if config.include_cover:
            html_parts.append(f"""
<div class="cover">
    <h1 class="cover-title">{config.title}</h1>
    <p class="cover-author">by {config.author}</p>
</div>
""")
        
        # Table of Contents
        if config.include_toc:
            toc_items = "\n".join([
                f'<li><a href="#ch-{i}">{ch.get("title", f"Chapter {i+1}")}</a></li>'
                for i, ch in enumerate(chapters)
            ])
            html_parts.append(f"""
<div class="toc">
    <h2>Contents</h2>
    <ol>{toc_items}</ol>
</div>
""")
        
        # Chapters
        for i, chapter in enumerate(chapters):
            title = chapter.get("title", f"Chapter {i+1}")
            content = chapter.get("content", "")
            takeaways = chapter.get("key_takeaways", [])
            
            # Convert content to paragraphs
            paragraphs = "\n".join([
                f"<p>{p}</p>" for p in content.split("\n\n") if p.strip()
            ])
            
            # Key takeaways
            takeaways_html = ""
            if takeaways:
                items = "\n".join([f"<li>{t}</li>" for t in takeaways])
                takeaways_html = f"""
<div class="takeaways">
    <h3>Key Takeaways</h3>
    <ul>{items}</ul>
</div>
"""
            
            # Visual if available
            visual_html = ""
            section_id = f"ch{i+1}_opener"
            if visuals and section_id in visuals:
                visual_html = f'<img src="{visuals[section_id]}" class="chapter-visual" />'
            
            html_parts.append(f"""
<div class="chapter" id="ch-{i}">
    <h2 class="chapter-title">{title}</h2>
    {visual_html}
    <div class="chapter-content">
        {paragraphs}
    </div>
    {takeaways_html}
</div>
""")
        
        return "\n".join(html_parts)
    
    def _build_css(self, style: PDFStyle) -> str:
        """Build CSS for PDF styling."""
        return f"""
@page {{
    size: letter;
    margin: {style.page_margin}pt;
}}

body {{
    font-family: {style.font_family}, system-ui, sans-serif;
    font-size: {style.font_size}pt;
    line-height: {style.line_height};
    color: {style.text_color};
}}

.cover {{
    page-break-after: always;
    text-align: center;
    padding-top: 40%;
}}

.cover-title {{
    font-size: 36pt;
    font-weight: 700;
    color: {style.heading_color};
    margin-bottom: 24pt;
}}

.cover-author {{
    font-size: 18pt;
    color: {style.accent_color};
}}

.toc {{
    page-break-after: always;
}}

.toc h2 {{
    font-size: 24pt;
    color: {style.heading_color};
    margin-bottom: 24pt;
}}

.toc ol {{
    list-style-type: decimal;
    padding-left: 24pt;
}}

.toc li {{
    margin-bottom: 12pt;
}}

.toc a {{
    color: {style.text_color};
    text-decoration: none;
}}

.chapter {{
    page-break-before: always;
}}

.chapter-title {{
    font-size: 24pt;
    font-weight: 700;
    color: {style.heading_color};
    margin-bottom: 24pt;
    border-bottom: 2px solid {style.accent_color};
    padding-bottom: 12pt;
}}

.chapter-content p {{
    margin-bottom: 12pt;
    text-align: justify;
}}

.chapter-visual {{
    max-width: 100%;
    margin: 24pt 0;
}}

.takeaways {{
    background: #f7fafc;
    padding: 24pt;
    border-radius: 8pt;
    margin-top: 24pt;
    border-left: 4pt solid {style.accent_color};
}}

.takeaways h3 {{
    font-size: 14pt;
    color: {style.accent_color};
    margin-bottom: 12pt;
}}

.takeaways ul {{
    list-style-type: disc;
    padding-left: 18pt;
}}

.takeaways li {{
    margin-bottom: 8pt;
}}
"""
    
    def _slugify(self, text: str) -> str:
        """Convert text to a safe filename."""
        return "".join(c if c.isalnum() or c == " " else "" for c in text).replace(" ", "_").lower()
