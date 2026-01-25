"""
PDF Generator
Creates professional PDF documents from product content.
Supports styled layouts, embedded visuals, and print-ready output.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
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
            logger.info("✅ WeasyPrint available")
        except ImportError:
            pass
        
        try:
            import reportlab
            from reportlab.lib.pagesizes import letter
            self.has_reportlab = True
            logger.info("✅ ReportLab available")
        except ImportError as e:
            logger.warning(f"⚠️ ReportLab not found ({e}). Install: pip install reportlab")
        
        if not self.has_weasyprint and not self.has_reportlab:
            logger.warning("❌ No PDF library available. Falling back to HTML only.")
    
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
            logger.info("ℹ️ Falling back to ReportLab engine...")
            return self._generate_reportlab(chapters, config, visuals, output_path)
        else:
            logger.warning("❌ ReportLab not found. Falling back to HTML.")
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
                 # os.remove(temp_html_path)
                 logger.info(f"ℹ️ Kept temp HTML for debugging: {temp_html_path}")
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
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
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
        
        # Copyright page
        copyright_style = ParagraphStyle(
            'Copyright',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=HexColor('#666666')
        )
        disclaimer_text = self._get_disclaimer(config.title)
        
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(f"<b>{config.title}</b>", copyright_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("By Randy Salars", copyright_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "Copyright 2026 Ranmon Inc<br/>"
            "31 Bear Mountain Rd<br/>"
            "Silver City, NM 88061<br/>"
            "salars.net",
            copyright_style
        ))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("<b>Disclaimer</b>", copyright_style))
        story.append(Paragraph(disclaimer_text, copyright_style))
        story.append(PageBreak())
        
        # Chapters
        for i, chapter in enumerate(chapters):
            # Chapter Title
            story.append(self._parse_markdown_line(f"# {chapter.get('title', 'Chapter')}", config, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Content Parsing
            content = chapter.get("content", "")
            story.extend(self._parse_markdown_to_story(content, config, styles))
            
            # Key Takeaways
            takeaways = chapter.get("key_takeaways", [])
            if takeaways:
                story.append(Spacer(1, 0.2*inch))
                story.append(self._parse_markdown_line("### Key Takeaways", config, styles))
                for t in takeaways:
                     story.append(self._parse_markdown_line(f"* {t}", config, styles))

            story.append(PageBreak())
        
        doc.build(story)
        logger.info(f"✅ PDF generated: {output_path}")
        return output_path

    def _parse_markdown_to_story(self, text: str, config: PDFConfig, styles: Any) -> List[Any]:
        """Convert Markdown text to ReportLab Flowables."""
        from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem
        
        flowables = []
        lines = text.split('\n')
        
        # Simple iterator
        for line in lines:
            line = line.strip()
            if not line:
                flowables.append(Spacer(1, 0.1 * 72)) # Small spacer
                continue
                
            flowables.append(self._parse_markdown_line(line, config, styles))
            
        return flowables

    def _parse_markdown_line(self, line: str, config: PDFConfig, styles: Any) -> Any:
        """Parse a single line of markdown into a Paragraph."""
        from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem
        from reportlab.lib.colors import HexColor
        from reportlab.lib.styles import ParagraphStyle
        import re
        
        # Inline Formatting (Bold, Italic)
        # Convert **text** to <b>text</b>
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        # Convert *text* to <i>text</i> - handle carefully vs bullets
        if not line.startswith('* '):
             line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)
             
        # Headers
        if line.startswith('# '):
            style = ParagraphStyle(
                'H1', parent=styles['Heading1'], 
                fontSize=24, spaceAfter=12, textColor=HexColor(config.style.heading_color)
            )
            return Paragraph(line[2:], style)
            
        if line.startswith('## '):
            style = ParagraphStyle(
                'H2', parent=styles['Heading2'], 
                fontSize=18, spaceAfter=10, textColor=HexColor(config.style.heading_color)
            )
            return Paragraph(line[3:], style)
            
        if line.startswith('### '):
            style = ParagraphStyle(
                'H3', parent=styles['Heading3'],
                fontSize=14, spaceAfter=8, textColor=HexColor(config.style.accent_color)
            )
            return Paragraph(line[4:], style)

        # Lists (Simple Bullet simulation)
        if line.startswith('* ') or line.startswith('- '):
            style = ParagraphStyle(
                'Bullet', parent=styles['Normal'],
                fontSize=config.style.font_size,
                textColor=HexColor(config.style.text_color),
                leftIndent=20,
                bulletIndent=10
            )
            # Use ReportLab's bullet char
            return Paragraph(f"• {line[2:]}", style)
            
        # Normal Text
        style = ParagraphStyle(
            'Body', parent=styles['Normal'],
            fontSize=config.style.font_size,
            leading=config.style.font_size * config.style.line_height,
            textColor=HexColor(config.style.text_color)
        )
        return Paragraph(line, style)
    
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
        
        # Copyright Page
        disclaimer_text = self._get_disclaimer(config.title)
        html_parts.append(f"""
<div class="copyright-page">
    <p><strong>{config.title}</strong></p>
    <p>By Randy Salars</p>
    <p>Copyright 2026 Ranmon Inc<br>
    31 Bear Mountain Rd<br>
    Silver City, NM 88061<br>
    <a href="https://salars.net">salars.net</a></p>
    
    <div class="disclaimer">
        <h4>Disclaimer</h4>
        <p>{disclaimer_text}</p>
    </div>
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
            
            # Convert content from Markdown to HTML
            try:
                from markdown_it import MarkdownIt
                md = MarkdownIt('commonmark', {'breaks': True, 'html': True})
                # Add table support if possible or stick to commonmark
                html_content = md.render(content)
                paragraphs = html_content
            except ImportError:
                logger.warning("Markdown library not found. Falling back to plain text.")
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

.copyright-page {{
    page-break-after: always;
    font-size: 10pt;
    color: #718096;
    margin-top: 400pt; /* Push to bottom of page */
}}

.disclaimer {{
    margin-top: 24pt;
    font-style: italic;
    border-top: 1px solid #cbd5e0;
    padding-top: 12pt;
    font-size: 9pt;
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

    def _get_disclaimer(self, title: str) -> str:
        """Get appropriate disclaimer based on title/topic."""
        t = title.lower()
        
        if "invest" in t or "wealth" in t or "crypto" in t or "budget" in t or "money" in t or "salary" in t:
            return (
                "This publication is designed to provide accurate and authoritative information in regard to the "
                "subject matter covered. It is sold with the understanding that the publisher is not engaged in "
                "rendering legal, accounting, or other professional services. If legal advice or other expert "
                "assistance is required, the services of a competent professional should be sought. "
                "Past performance is not indicative of future results."
            )
            
        if "health" in t or "diet" in t or "fitness" in t or "body" in t:
            return (
                "The content shared in this book is for informational purposes only and is not a substitute for "
                "professional medical advice, diagnosis, or treatment. Always seek the advice of your physician "
                "or other qualified health provider with any questions you may have regarding a medical condition."
            )
            
        # Default Business/General Disclaimer
        return (
            "Every effort has been made to accurately represent this product and its potential. "
            "There is no guarantee that you will earn any money using the techniques and ideas in these materials. "
            "Examples in these materials are not to be interpreted as a promise or guarantee of earnings. "
            "Earning potential is entirely dependent on the person using our product, ideas and techniques."
        )
