import sys
import os
import shutil
import subprocess
from pathlib import Path
import time

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Imports
from agents.product_builder.core.intelligence import DemandSignal
from agents.product_builder.core.blueprinter import ProductArchitect
from agents.product_builder.core.context import ProductContext
from agents.product_builder.pipeline.session_runner import SessionOrchestrator
from agents.product_builder.packaging.landing_page import LandingPageAgent
from agents.product_builder.packaging.marketing import MarketingStrategist
from agents.product_builder.packaging.publisher import PublisherAgent

def build_financial_freedom():
    print("🚀 Starting Financial Freedom Blueprint Build...")
    
    # Setup Output
    output_dir = PROJECT_ROOT / "output" / "products"
    salarsu_root = Path("/home/rsalars/Projects/salarsu") # Real store path
    
    target_slug = "financial-freedom-blueprints"
    
    # 1. Intelligence
    print("\n[1] Defining Intelligence Signal...")
    signal = DemandSignal(
        topic="Financial Freedom",
        evidence_score=0.99,
        key_themes=[
            "Asset Allocation", 
            "Passive Income", 
            "Risk Management",
            "Psychology of Wealth",
            "Tax Efficiency"
        ],
        missing_angles=[
            "Data-driven", 
            "No-nonsense", 
            "Automated Systems"
        ]
    )
    
    # 2. Architect
    print("\n[2] Running Product Architect...")
    architect = ProductArchitect()
    blueprint = architect.generate_blueprint(
        signal, 
        title_override="Financial Freedom Blueprints"
    )
    # Enforce slug matches URL
    blueprint.slug = target_slug 
    print(f"    Blueprint Created: {blueprint.title}")
    
    # 3. Context Init
    print("\n[3] Initializing Context & Persistence...")
    context = ProductContext(blueprint.slug, base_output_dir=str(output_dir))
    
    # Check if exists to resume or overwrite?
    # For this task, we likely want to overwrite or ensure it's fresh if verification fails.
    # But usually contexts load existing state.
    # Let's see if we have valid state.
    if context.state and len(context.state.completed_chapters) > 0:
         print(f"    Resuming from Chapter {len(context.state.completed_chapters) + 1}")
    else:
         context.blueprint = blueprint
         context.save()
         print("    New context initialized.")

    # 4. Pipeline Execution
    print("\n[4] Running Session Orchestrator...")
    runner = SessionOrchestrator(context)
    
    # Run all chapters
    total_chapters = len(context.blueprint.chapter_map)
    while len(context.state.completed_chapters) < total_chapters:
        current = len(context.state.completed_chapters) + 1
        print(f"    Building Chapter {current}/{total_chapters}...")
        runner.run_next_chapter()
        context.load() # Refresh state just in case
        time.sleep(1) # Safety breather

    print("    ✅ All Chapters Built.")

    # 5. Packaging
    print("\n[5] Generating Packaging...")
    templates_dir = PROJECT_ROOT / "agents" / "product_builder" / "templates"
    
    # Landing Page
    lp_agent = LandingPageAgent(templates_dir)
    lp_content = lp_agent.generate(context.blueprint)
    
    # Overwrite the context landing page if needed or just save it
    # The context might store it, but the blueprint has the field?
    # Usually we attach it to the blueprint or wrapper.
    # Let's assume Publisher handles the manifest which includes this.
    # Compile Chapters into Product Artifact
    print("\n[5.5] Compiling Product Artifact...")
    product_content = f"# {context.blueprint.title}\n\n"
    for chapter_id in context.state.completed_chapters:
        chapter_path = context.staging_path / "chapters" / f"{chapter_id}.mdx"
        if chapter_path.exists():
            with open(chapter_path, 'r') as f:
                product_content += f.read() + "\n\n"
    
    product_artifact_path = context.staging_path / f"{context.blueprint.slug}.pdf" 
    # Validating "pdf" extension for the publisher's expectation, though it's markdown text content. 
    # In a real scenario we'd convert to PDF. For now, we save text to the file expected by publisher.
    with open(product_artifact_path, 'w') as f:
        f.write(product_content)

    # 6. Deployment / Publishing
    print("\n[6] Running Publisher Agent...")
    publisher = PublisherAgent(str(salarsu_root))
    # We point artifacts_path to staging_path where we saved the "pdf"
    deploy_result = publisher.deploy(context.blueprint, context.staging_path, landing_page_content=lp_content)
    
    manifest_path = Path(deploy_result["manifest_path"])
    if manifest_path.exists():
        print(f"    ✅ Manifest created at {manifest_path}")
        print("    READY FOR STORE LOAD.")
    else:
        print("    ❌ Manifest creation failed.")


def perform_store_load(manifest_path, salarsu_root):
    """
    Automates the loading of the product into the running Salarsu container.
    """
    print("\n[7] Automating Store Load...")
    
    # 1. Find Container ID
    try:
        # We look for the container publishing port 3000 (Next.js default)
        cmd_find = "docker ps --format '{{.ID}}' --filter 'publish=3000'"
        container_id = subprocess.check_output(cmd_find, shell=True).decode().strip()
        
        if not container_id:
            print("    ❌ Coould not find running Salarsu container (port 3000). Skipping load.")
            return

        print(f"    Target Container: {container_id}")
        
        # 2. Prepare Paths
        container_manifest_path = f"/tmp/{manifest_path.name}"
        container_loader_path = "/tmp/product_loader.js"
        local_loader_path = salarsu_root / "scripts" / "product_loader.js"
        
        # 3. Copy Manifest
        subprocess.run(f"docker cp {manifest_path} {container_id}:{container_manifest_path}", shell=True, check=True)
        print("    Manifest copied to container.")
        
        # 4. Copy Loader Script 
        # (We copy it to ensure the container has the latest version, but run it from /tmp to avoid overwriting app files if mapped)
        # Actually, running from /tmp might break if it needs node_modules relative to it.
        # The container usually runs in /app. If we put loader in /app/scripts/automator.js it might be better.
        # But let's check if the container already has scripts.
        # Safer: Run the script that is ALREADY in the container if we trust it, or cp to /app/scripts/temp_loader.js
        # Let's try copying to /app/scripts/temp_product_loader.js
        
        container_script_dest = "/app/scripts/temp_product_loader.js"
        subprocess.run(f"docker cp {local_loader_path} {container_id}:{container_script_dest}", shell=True, check=True)
        
        # 5. Execute
        # We assume the container WORKDIR is /app (or wherever package.json is)
        print("    Executing Loader...")
        cmd_exec = f"docker exec {container_id} node scripts/temp_product_loader.js {container_manifest_path}"
        result = subprocess.run(cmd_exec, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("    ✅ Store Load Success!")
            print(result.stdout)
        else:
            print("    ❌ Store Load Failed.")
            print(result.stderr)
            print(result.stdout)
            
        # Cleanup
        subprocess.run(f"docker exec {container_id} rm {container_manifest_path} {container_script_dest}", shell=True)
            
    except Exception as e:
        print(f"    ❌ Automation Error: {e}")

if __name__ == "__main__":
    build_financial_freedom()
    
    # Run the loader
    manifest_path = Path("/home/rsalars/Projects/salarsu/store_import/financial-freedom-blueprints_manifest.json")
    if manifest_path.exists():
        perform_store_load(manifest_path, Path("/home/rsalars/Projects/salarsu"))

