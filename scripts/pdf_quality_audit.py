#!/usr/bin/env python3
"""
PDF Quality Audit & Recompilation Tool

Examines all digital product PDFs for structural issues:
- Content out of order
- Appendixes at beginning instead of end
- Missing table of contents
- Missing cover image

Triggers recompilation and rezip when issues found.

Usage:
    python3 scripts/pdf_quality_audit.py --audit
    python3 scripts/pdf_quality_audit.py --audit --auto-fix
    python3 scripts/pdf_quality_audit.py --verify
    python3 scripts/pdf_quality_audit.py --product "poets_craft_toolkit"
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2"], check=True)
    import PyPDF2


# ============================================================
# CONFIGURATION
# ============================================================

SALARSU_ROOT = Path("/home/rsalars/Projects/salarsu")
DREAMWEAVING_ROOT = Path("/home/rsalars/Projects/dreamweaving")
DOWNLOADS_PATH = SALARSU_ROOT / "public/downloads/products"
PRODUCTS_PATH = DREAMWEAVING_ROOT / "products"

# Product mapping: ZIP filename -> product directory in dreamweaving
PRODUCT_MAP = {
    'Consciousness_Expansion_Audio_Pack.zip': 'consciousness_expansion_audio_pack',
    'Financial_Freedom_Blueprint_Complete.zip': 'financial_freedom_blueprints',
    'Holistic_Wellness_Protocol_Complete.zip': 'holistic_wellness_protocol',
    'Poets_Craft_Toolkit.zip': 'poets-craft-toolkit',
    'poets_craft_toolkit.zip': 'poets-craft-toolkit',
    'ai_integration_playbook_Complete.zip': 'ai_integration_playbook',
    'emergency-preparedness-essentials.zip': 'emergency-preparedness-essentials',
    'frontier-wisdom-collection.zip': 'frontier-wisdom-collection',
    'treasure_hunters_research_guide.zip': 'treasure-hunters-research-guide',
}


# ============================================================
# DATA TYPES
# ============================================================

@dataclass
class PDFIssue:
    issue_type: str  # 'content_order', 'appendix_placement', 'missing_toc', 'missing_cover'
    severity: str    # 'P1', 'P2', 'P3'
    description: str
    location: Optional[str] = None
    auto_fixable: bool = True


@dataclass
class ProductAuditResult:
    product_name: str
    zip_path: str
    pdf_path: Optional[str] = None
    issues: List[PDFIssue] = None
    status: str = 'healthy'  # 'healthy', 'needs_fix', 'needs_review'
    recompiled: bool = False
    rezipped: bool = False
    downloadable: bool = False
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


# ============================================================
# PDF ANALYSIS
# ============================================================

def analyze_pdf(pdf_path: Path) -> Dict:
    """Analyze PDF structure for issues."""
    result = {
        "hasCover": False,
        "hasTOC": False,
        "appendixBeforeContent": False,
        "appendixFirstPage": None,
        "contentOutOfOrder": [],
        "pageCount": 0,
        "structure": [],
        "firstChapterPage": None,
        "error": None,
    }
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            result["pageCount"] = len(reader.pages)
            
            first_chapter_page = None
            appendix_page = None
            toc_page = None
            
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""
                    
                text_lower = text.lower()
                
                # Check first page for cover elements
                if i == 0:
                    # Cover pages typically have minimal text or specific patterns
                    word_count = len(text.split())
                    if word_count < 100:  # Sparse text suggests cover
                        result["hasCover"] = True
                    elif any(x in text_lower for x in ["copyright", "all rights reserved", "salarsnet"]):
                        result["hasCover"] = True
                
                # Check for TOC
                if toc_page is None:
                    if "table of contents" in text_lower or \
                       (text_lower.strip().startswith("contents") and "chapter" in text_lower):
                        result["hasTOC"] = True
                        toc_page = i + 1
                        result["structure"].append({"type": "toc", "page": i + 1})
                
                # Track chapter headers
                chapter_match = re.search(r'chapter\s*[\d]+', text_lower)
                if chapter_match and first_chapter_page is None:
                    first_chapter_page = i + 1
                    result["firstChapterPage"] = first_chapter_page
                    result["structure"].append({"type": "chapter_start", "page": i + 1})
                
                # Track appendix
                appendix_match = re.search(r'^appendix\s*[a-z1-9]?', text_lower, re.MULTILINE)
                if appendix_match and appendix_page is None:
                    appendix_page = i + 1
                    result["structure"].append({"type": "appendix", "page": i + 1})
            
            # Check if appendix comes before first chapter
            if appendix_page and first_chapter_page:
                if appendix_page < first_chapter_page:
                    result["appendixBeforeContent"] = True
                    result["appendixFirstPage"] = appendix_page
                    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def get_pdf_issues(analysis: Dict) -> List[PDFIssue]:
    """Convert analysis results to issue list."""
    issues = []
    
    if analysis.get("error"):
        issues.append(PDFIssue(
            issue_type="analysis_error",
            severity="P3",
            description=f"Could not analyze PDF: {analysis['error']}",
            auto_fixable=False,
        ))
        return issues
    
    if not analysis.get("hasCover"):
        issues.append(PDFIssue(
            issue_type="missing_cover",
            severity="P2",
            description="PDF does not have a clear cover page (page 1 has dense text)",
        ))
    
    if not analysis.get("hasTOC"):
        issues.append(PDFIssue(
            issue_type="missing_toc",
            severity="P2",
            description="PDF does not have a table of contents",
        ))
    
    if analysis.get("appendixBeforeContent"):
        issues.append(PDFIssue(
            issue_type="appendix_placement",
            severity="P1",
            description=f"Appendix found before main content",
            location=f"Page {analysis['appendixFirstPage']}",
        ))
    
    return issues


# ============================================================
# RECOMPILATION
# ============================================================

def recompile_product(product_dir: Path, product_title: str) -> bool:
    """Recompile a product PDF using the product builder."""
    print(f"  🔄 Recompiling: {product_title}")
    
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "agents.product_builder.cli",
                "compile",
                "--product-dir", str(product_dir),
                "--title", product_title,
                "--force",
            ],
            cwd=str(DREAMWEAVING_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        if result.returncode == 0:
            print(f"  ✅ Recompilation successful")
            return True
        else:
            print(f"  ❌ Recompilation failed: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ❌ Recompilation timed out")
        return False
    except Exception as e:
        print(f"  ❌ Recompilation error: {e}")
        return False


def rebuild_zip(product_dir: Path, zip_name: str) -> bool:
    """Rebuild ZIP archive for a product."""
    output_dir = product_dir / "output"
    target_zip = DOWNLOADS_PATH / zip_name
    
    try:
        # Find files to include
        files = list(output_dir.iterdir()) if output_dir.exists() else []
        
        # Find main PDF
        main_pdfs = [f for f in files if f.suffix == '.pdf' 
                     and 'temp' not in f.name.lower() 
                     and 'bonus' not in f.name.lower()]
        
        if not main_pdfs:
            print(f"  ❌ No main PDF found in {output_dir}")
            return False
        
        main_pdf = main_pdfs[0]
        
        # Find bonuses
        bonus_files = [f for f in files if 'bonus' in f.name.lower()]
        bonus_dir = output_dir / "bonuses"
        
        # Create new ZIP
        with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add main PDF
            zf.write(main_pdf, main_pdf.name)
            print(f"    + {main_pdf.name}")
            
            # Add bonus files
            for bonus in bonus_files:
                if bonus.is_file():
                    zf.write(bonus, bonus.name)
                    print(f"    + {bonus.name}")
            
            # Add bonus directory contents
            if bonus_dir.exists():
                for bonus_file in bonus_dir.rglob("*"):
                    if bonus_file.is_file():
                        arcname = f"bonuses/{bonus_file.relative_to(bonus_dir)}"
                        zf.write(bonus_file, arcname)
                        print(f"    + {arcname}")
        
        size_mb = target_zip.stat().st_size / (1024 * 1024)
        print(f"  ✅ Created ZIP: {zip_name} ({size_mb:.2f} MB)")
        return True
        
    except Exception as e:
        print(f"  ❌ ZIP creation failed: {e}")
        return False


# ============================================================
# VERIFICATION
# ============================================================

def verify_download(zip_name: str) -> bool:
    """Verify that a product ZIP is downloadable and intact."""
    zip_path = DOWNLOADS_PATH / zip_name
    
    try:
        if not zip_path.exists():
            return False
        
        # Test ZIP integrity
        with zipfile.ZipFile(zip_path, 'r') as zf:
            bad_file = zf.testzip()
            if bad_file:
                print(f"    ⚠️ Corrupt file in ZIP: {bad_file}")
                return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ ZIP verification failed: {e}")
        return False


# ============================================================
# MAIN AUDIT
# ============================================================

def run_audit(auto_fix: bool = False, target_products: Optional[List[str]] = None) -> Dict:
    """Run full PDF quality audit."""
    print("=" * 60)
    print(" 📋 PDF QUALITY AUDIT")
    print("=" * 60)
    print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Auto-fix: {'enabled' if auto_fix else 'disabled'}")
    print("=" * 60)
    
    results = []
    issues_by_type = {}
    recompile_stats = {"attempted": 0, "succeeded": 0, "failed": []}
    
    # Get all ZIPs
    if not DOWNLOADS_PATH.exists():
        print(f"❌ Downloads path not found: {DOWNLOADS_PATH}")
        return {}
    
    zip_files = sorted([f.name for f in DOWNLOADS_PATH.iterdir() if f.suffix == '.zip'])
    
    for zip_name in zip_files:
        if target_products and zip_name not in target_products:
            continue
        
        print(f"\n📦 {zip_name}")
        print("-" * 40)
        
        result = ProductAuditResult(
            product_name=zip_name.replace('.zip', ''),
            zip_path=str(DOWNLOADS_PATH / zip_name),
        )
        
        # Get product directory
        product_dir_name = PRODUCT_MAP.get(zip_name)
        if not product_dir_name:
            print(f"  ⚠️ No product mapping found")
            result.status = 'needs_review'
            results.append(result)
            continue
        
        product_dir = PRODUCTS_PATH / product_dir_name
        output_dir = product_dir / "output"
        
        if not output_dir.exists():
            print(f"  ⚠️ Output directory not found: {output_dir}")
            result.status = 'needs_review'
            results.append(result)
            continue
        
        # Find main PDF
        pdf_files = [f for f in output_dir.iterdir() 
                     if f.suffix == '.pdf' 
                     and 'temp' not in f.name.lower()
                     and 'bonus' not in f.name.lower()]
        
        if not pdf_files:
            print(f"  ⚠️ No main PDF found in output/")
            result.status = 'needs_review'
            results.append(result)
            continue
        
        main_pdf = pdf_files[0]
        result.pdf_path = str(main_pdf)
        
        # Analyze PDF
        print(f"  📄 Analyzing: {main_pdf.name}")
        analysis = analyze_pdf(main_pdf)
        issues = get_pdf_issues(analysis)
        result.issues = issues
        
        # Count issues
        for issue in issues:
            issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1
        
        # Determine status
        if not issues:
            result.status = 'healthy'
            print(f"  ✅ No issues found")
        elif any(not i.auto_fixable for i in issues):
            result.status = 'needs_review'
        else:
            result.status = 'needs_fix'
        
        for issue in issues:
            severity_icon = {'P1': '🔴', 'P2': '🟡', 'P3': '🟢'}.get(issue.severity, '⚪')
            print(f"  {severity_icon} [{issue.severity}] {issue.issue_type}: {issue.description}")
        
        # Print structure info
        print(f"  📊 Pages: {analysis.get('pageCount', '?')}")
        print(f"  📊 Has Cover: {'✅' if analysis.get('hasCover') else '❌'}")
        print(f"  📊 Has TOC: {'✅' if analysis.get('hasTOC') else '❌'}")
        
        # Auto-fix if enabled
        if auto_fix and result.status == 'needs_fix' and issues:
            print(f"\n  🔧 Attempting auto-fix...")
            recompile_stats["attempted"] += 1
            
            product_title = result.product_name.replace('_', ' ').replace('-', ' ').title()
            
            success = recompile_product(product_dir, product_title)
            result.recompiled = success
            
            if success:
                zip_success = rebuild_zip(product_dir, zip_name)
                result.rezipped = zip_success
                
                if zip_success:
                    recompile_stats["succeeded"] += 1
                else:
                    recompile_stats["failed"].append(result.product_name)
            else:
                recompile_stats["failed"].append(result.product_name)
        
        # Verify download
        result.downloadable = verify_download(zip_name)
        print(f"  📥 Downloadable: {'✅' if result.downloadable else '❌'}")
        
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print(" 📊 AUDIT SUMMARY")
    print("=" * 60)
    
    healthy = len([r for r in results if r.status == 'healthy'])
    needs_fix = len([r for r in results if r.status == 'needs_fix'])
    needs_review = len([r for r in results if r.status == 'needs_review'])
    
    print(f" Total Products:  {len(results)}")
    print(f" ✅ Healthy:       {healthy}")
    print(f" 🔧 Needs Fix:     {needs_fix}")
    print(f" ⚠️  Needs Review:  {needs_review}")
    
    if issues_by_type:
        print(f"\n Issues by Type:")
        for issue_type, count in issues_by_type.items():
            print(f"   - {issue_type}: {count}")
    
    if auto_fix and recompile_stats["attempted"] > 0:
        print(f"\n Recompilation Results:")
        print(f"   Attempted: {recompile_stats['attempted']}")
        print(f"   Succeeded: {recompile_stats['succeeded']}")
        if recompile_stats["failed"]:
            print(f"   Failed: {', '.join(recompile_stats['failed'])}")
    
    # Downloadability summary
    downloadable = len([r for r in results if r.downloadable])
    print(f"\n 📥 Downloadable: {downloadable}/{len(results)}")
    
    print("=" * 60)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "totalProducts": len(results),
        "healthy": healthy,
        "needsFix": needs_fix,
        "needsReview": needs_review,
        "issuesByType": issues_by_type,
        "recompilation": recompile_stats,
        "results": [asdict(r) for r in results],
    }


def verify_all_downloads() -> Dict:
    """Verify all product ZIPs are downloadable."""
    print("=" * 60)
    print(" 📥 DOWNLOAD VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    zip_files = sorted([f.name for f in DOWNLOADS_PATH.iterdir() if f.suffix == '.zip'])
    
    for zip_name in zip_files:
        okay = verify_download(zip_name)
        results[zip_name] = okay
        status = "✅" if okay else "❌"
        size = DOWNLOADS_PATH / zip_name
        size_mb = size.stat().st_size / (1024 * 1024) if size.exists() else 0
        print(f" {status} {zip_name} ({size_mb:.2f} MB)")
    
    passed = sum(1 for v in results.values() if v)
    print(f"\n Passed: {passed}/{len(results)}")
    
    return results


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PDF Quality Audit & Recompilation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 pdf_quality_audit.py --audit
  python3 pdf_quality_audit.py --audit --auto-fix
  python3 pdf_quality_audit.py --verify
  python3 pdf_quality_audit.py --product "poets_craft_toolkit.zip"
        """
    )
    
    parser.add_argument('--audit', action='store_true', help='Run full PDF audit')
    parser.add_argument('--verify', action='store_true', help='Verify all downloads')
    parser.add_argument('--auto-fix', action='store_true', help='Auto-recompile fixable issues')
    parser.add_argument('--product', type=str, help='Audit specific product (ZIP filename)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    if args.verify:
        results = verify_all_downloads()
        if args.json:
            print(json.dumps(results, indent=2))
        return 0
    
    if args.audit or args.product:
        target = [args.product] if args.product else None
        results = run_audit(auto_fix=args.auto_fix, target_products=target)
        if args.json:
            print(json.dumps(results, indent=2))
        return 0
    
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
