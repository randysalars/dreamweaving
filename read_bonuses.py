from pypdf import PdfReader
from pathlib import Path

bonus_dir = Path("products/financial_freedom_blueprints/output/bonuses")
files = [
    "action_workbook.pdf",
    "the_salary_negotiation_blackbook.pdf",
    "the_recessionproof_investing_guide.pdf"
]

print("=== VERIFYING PDF CONTENT ===\n")

for filename in files:
    path = bonus_dir / filename
    if path.exists():
        print(f"\n--- Reading: {filename} ---")
        try:
            reader = PdfReader(path)
            # Read first 2 pages to check headers/content
            for i in range(min(2, len(reader.pages))):
                print(f"[Page {i+1}]")
                text = reader.pages[i].extract_text()
                print(text[:500] + "..." if len(text) > 500 else text)
                print("-" * 20)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    else:
        print(f"MISSING: {filename}")
