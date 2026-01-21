import sys
import os
import shutil
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Mock Imports to avoid external dependencies during dry run
from agents.product_builder.core.intelligence import DemandSignal
from agents.product_builder.core.blueprinter import ProductArchitect
from agents.product_builder.core.context import ProductContext
from agents.product_builder.pipeline.session_runner import SessionOrchestrator
from agents.product_builder.packaging.landing_page import LandingPageAgent
from agents.product_builder.packaging.marketing import MarketingStrategist

def test_pipeline_dry_run():
    print("🚀 Starting Product Builder Pipeline Dry Run...")
    
    # Setup Output
    output_dir = PROJECT_ROOT / "output" / "products"
    test_slug = "test-wealth-codex"
    if (output_dir / test_slug).exists():
        shutil.rmtree(output_dir / test_slug)
        
    # 1. Intelligence (Simulated)
    print("\n[1] Simulating Intelligence Layer...")
    signal = DemandSignal(
        topic="Wealth Systems", 
        evidence_score=0.9, 
        key_themes=["Systems not goals", "Leverage"], 
        missing_angles=["Actionable"]
    )
    
    # 2. Architect
    print("\n[2] Running Product Architect...")
    architect = ProductArchitect()
    blueprint = architect.generate_blueprint(signal, title_override="The Test Wealth Codex")
    print(f"    Blueprint Created: {blueprint.title}")
    
    # 3. Context Init
    print("\n[3] Initializing Context & Persistence...")
    context = ProductContext(blueprint.slug, base_output_dir=str(output_dir))
    context.blueprint = blueprint
    context.save()
    
    # 4. Pipeline Execution (1 Chapter)
    print("\n[4] Running Session Orchestrator (Chapter 1)...")
    runner = SessionOrchestrator(context)
    runner.run_next_chapter()
    
    # Verify Chapter 1
    chapter_path = context.staging_path / "chapters" / "chapter_01.mdx"
    if chapter_path.exists():
        print("    ✅ Chapter 1 created successfully.")
    else:
        print("    ❌ Chapter 1 failed.")
        return

    # 5. Packaging
    print("\n[5] Generating Packaging...")
    templates_dir = PROJECT_ROOT / "agents" / "product_builder" / "templates"
    lp_agent = LandingPageAgent(templates_dir)
    lp_content = lp_agent.generate(blueprint)
    
    if "# The Test Wealth Codex" in lp_content:
        print("    ✅ Landing Page generated.")
    else:
        print("    ❌ Landing Page content mismatch.")
        
    marketer = MarketingStrategist()
    bundle = marketer.generate_launch_bundle(blueprint)
    if "launch_emails.md" in bundle:
        print("    ✅ Marketing Bundle generated.")
        
    print("\n🎉 Dry Run Complete. System is operational.")

if __name__ == "__main__":
    test_pipeline_dry_run()
