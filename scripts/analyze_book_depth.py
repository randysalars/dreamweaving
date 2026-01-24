
import sys
from pathlib import Path
import re

def analyze_depth():
    base_dir = Path("products/financial_freedom_blueprints/manual_content")
    tracker_path = Path("products/financial_freedom_blueprints/expansion_tracker.md")
    
    print(f"📊 Analyzing Book Depth in {base_dir}...")
    
    total_words = 0
    chapters = []
    
    # Scan chapters
    for i in range(1, 16):
        filename = f"chapter{i}.md"
        path = base_dir / filename
        
        status = "MISSING"
        word_count = 0
        
        if path.exists():
            content = path.read_text()
            word_count = len(content.split())
            
            # Simple heuristic for expansion
            if word_count > 2000:
                status = "✅ EXPANDED"
            elif word_count > 100:
                status = "⚠️ DRAFT"
            else:
                status = "❌ EMPTY"
        
        chapters.append({
            "id": i,
            "status": status,
            "words": word_count
        })
        total_words += word_count

    # Generate Report
    report = "# 📈 Book Expansion Tracker\n\n"
    report += f"**Total Word Count:** {total_words:,} words\n"
    report += f"**Est. Pages:** ~{int(total_words/300)} pages\n"
    report += f"**Target:** 30,000 words (100+ pages)\n\n"
    
    report += "| Chapter | Status | Word Count | Action |\n"
    report += "|---------|--------|------------|--------|\n"
    
    for ch in chapters:
        action = "Needs Expansion" if "DRAFT" in ch['status'] else "Done"
        report += f"| {ch['id']} | {ch['status']} | {ch['words']:,} | {action} |\n"
    
    tracker_path.write_text(report)
    print(report)
    print(f"\nTracker saved to {tracker_path}")

if __name__ == "__main__":
    analyze_depth()
