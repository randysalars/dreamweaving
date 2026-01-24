
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

# Paths
INPUT_HTML = Path("products/financial_freedom_blueprints/output/Financial_Freedom_Blueprints.html")
OUTPUT_PDF = Path("products/financial_freedom_blueprints/output/Financial_Freedom_Blueprints.pdf")
SCRIPT_PATH = Path("agents/product_builder/packaging/generate_pdf.cjs")

if not INPUT_HTML.exists():
    print(f"Error: {INPUT_HTML} not found.")
    sys.exit(1)

print(f"Reading {INPUT_HTML}...")
html = INPUT_HTML.read_text(encoding="utf-8")
soup = BeautifulSoup(html, 'html.parser')

print("Extracting and re-rendering chapters...")
chapters = soup.find_all("div", class_="chapter")

for chapter in chapters:
    content_div = chapter.find("div", class_="chapter-content")
    if content_div:
        # Extract raw text (which is the markdown)
        # Note: Previous generator wrapped it in <p> </p> per line.
        # We need to extract the text and join it back.
        
        # Get all text from paragraphs
        raw_lines = [p.get_text() for p in content_div.find_all("p")]
        raw_markdown = "\n\n".join(raw_lines)
        
        # If no P tags, try get_text directly
        if not raw_lines:
            raw_markdown = content_div.get_text()

        # Render Markdown
        md = MarkdownIt('commonmark', {'breaks': True, 'html': True})
        rendered_html = md.render(raw_markdown)
        
        # Replace content
        # Create new soup for the rendered html
        new_tag = soup.new_tag("div", attrs={"class": "chapter-content"})
        new_tag.append(BeautifulSoup(rendered_html, 'html.parser'))
        
        content_div.replace_with(new_tag)

# Save fixed HTML
FIXED_HTML = INPUT_HTML.with_name("Financial_Freedom_Blueprints.fixed.html")
FIXED_HTML.write_text(str(soup), encoding="utf-8")
print(f"Saved {FIXED_HTML}")

# Run Puppeteer
import subprocess
print("Running Puppeteer...")
cmd = ["node", str(SCRIPT_PATH), str(FIXED_HTML), str(OUTPUT_PDF)]
try:
    subprocess.run(cmd, check=True)
    print(f"✅ PDF Regenerated: {OUTPUT_PDF}")
except subprocess.CalledProcessError as e:
    print(f"❌ PDF Generation Failed: {e}")
