from pypdf import PdfReader
from pathlib import Path

path = Path("products/financial_freedom_blueprints/output/Financial_Freedom_Blueprints.pdf")

print(f"=== READING MAIN PRODUCT: {path} ===\n")

if path.exists():
    try:
        reader = PdfReader(path)
        print(f"Total Pages: {len(reader.pages)}")
        for i, page in enumerate(reader.pages):
            print(f"\n--- Page {i+1} ---")
            text = page.extract_text()
            print(text[:1000] + "..." if len(text) > 1000 else text)
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File not found.")
