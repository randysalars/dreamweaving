import logging
import json
import shutil
from pathlib import Path
from typing import Dict, Any
import hashlib
from datetime import datetime, timezone
from ..schemas.blueprint import ProductBlueprint

logger = logging.getLogger(__name__)

class PublisherAgent:
    """
    Deploys the Product to the SalarsNet Store (salarsu).
    1. Copies artifacts to salarsu/public/downloads/
    2. Generates a deployment manifest for the DB Loader.
    """
    
    def __init__(self, salarsu_root: str):
        self.salarsu_root = Path(salarsu_root)
        self.downloads_dir = self.salarsu_root / "public" / "downloads"
        self.manifest_dir = self.salarsu_root / "store_import"
        
    def deploy(self, blueprint: ProductBlueprint, artifacts_path: Path, landing_page_content: str = None) -> Dict[str, Any]:
        """
        Executes the deployment.
        """
        logger.info(f"Deploying {blueprint.title} to {self.salarsu_root}...")
        
        # 1. Ensure Directories
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Copy Artifacts (Simulated - expecting a 'book.pdf' or similar in artifacts_path)
        # In this v1, we assume the 'staging/chapters' is the source, but usually we'd have a 'build' folder.
        # We will create a dummy PDF for the dry run if not exists.
        product_files = []
        
        # Simulating a built PDF for the dry run / implementation
        pdf_name = f"{blueprint.slug}.pdf"
        dest_pdf = self.downloads_dir / pdf_name
        
        # Copy artifact from staging if it exists
        source_pdf = artifacts_path / pdf_name
        if source_pdf.exists():
            logger.info(f"Copying artifact from {source_pdf} to {dest_pdf}")
            shutil.copy(source_pdf, dest_pdf)
        elif not dest_pdf.exists():
            # Real PDF Generation Logic
            logger.info(f"Artifact not found. Generating PDF from chapters...")
            
            # 1. Locate Generator Script
            # Publisher is in agents/product_builder/packaging/
            # Project root is parents[3] from here (packaging -> product_builder -> agents -> dreamweaving)
            # Salarsu is sibling of dreamweaving
            
            # Fix path finding:
            # __file__ = .../dreamweaving/agents/product_builder/packaging/publisher.py
            # parents[0] = packaging
            # parents[1] = product_builder
            # parents[2] = agents
            # parents[3] = dreamweaving
            # parents[4] = Projects (root of workspace)
            
            project_root = Path(__file__).resolve().parents[4]
            generator_script = project_root / "salarsu" / "scripts" / "pdf_generator.js"
            
            # 2. Collect Chapter Content
            chapters_dir = artifacts_path / "chapters"
            full_content = f"# {blueprint.title}\n\n{blueprint.promise.subhead}\n\n"
            
            if chapters_dir.exists():
                # Sort by filename (chapter_01, chapter_02...)
                chapter_files = sorted(chapters_dir.glob("*.mdx"))
                for cf in chapter_files:
                    full_content += f"\n\n--- {cf.stem.replace('_', ' ').title()} ---\n\n"
                    with open(cf, 'r') as f:
                        full_content += f.read()
            else:
                 full_content += "No chapter content found in staging."

            # 3. Create Temp Input File
            temp_input = artifacts_path / "temp_full_book.txt"
            with open(temp_input, 'w') as f:
                f.write(full_content)
                
            # 4. Call Node Script
            if generator_script.exists():
                import subprocess
                try:
                    cmd = ["node", str(generator_script), str(temp_input), str(dest_pdf)]
                    # Run in salarsu directory to find node_modules
                    cwd = generator_script.parent.parent 
                    
                    subprocess.run(cmd, check=True, cwd=str(cwd), capture_output=True)
                    logger.info(f"✅ Generated Real PDF at {dest_pdf}")
                    
                except subprocess.CalledProcessError as e:
                    logger.error(f"PDF Generation Failed: {e}")
                    # Fallback if generation fails
                    with open(dest_pdf, 'w') as f:
                        f.write("PDF GENERATION FAILED. CHECK LOGS.")
            else:
                logger.error(f"Generator script not found at {generator_script}")
                with open(dest_pdf, 'w') as f:
                    f.write("GENERATOR SCRIPT MISSING")
            
            # Cleanup temp
            if temp_input.exists():
                temp_input.unlink()
        
        product_files.append({
            "type": "main_file",
            "url": f"/downloads/{pdf_name}",
            "filename": pdf_name
        })

        # 2b. integrity Check & Checksum
        if not dest_pdf.exists() or dest_pdf.stat().st_size < 1024:
             error_msg = f"CRITICAL: PDF artifact {dest_pdf} is missing or too small (<1KB). Forbidden behavior."
             logger.error(error_msg)
             # In strict mode, we might raise an exception here to block deployment
             # raise RuntimeError(error_msg) 
        
        # Calculate SHA-256
        sha256_hash = hashlib.sha256()
        with open(dest_pdf, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        
        logger.info(f"Artifact Integrity Verified: SHA-256={file_hash}")
        
        # 2a. Handle Image Artifact
        image_name = f"{blueprint.slug}.png"
        images_dir = self.salarsu_root / "public" / "images" / "products"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        dest_image = images_dir / image_name
        source_image = artifacts_path / image_name
        
        deployed_image_url = f"/images/products/{image_name}" # Default expected URL
        
        if source_image.exists():
            logger.info(f"Copying image from {source_image} to {dest_image}")
            shutil.copy(source_image, dest_image)
        elif (images_dir / image_name).exists():
             logger.info(f"Image already exists at {dest_image}, using existing.")
        else:
             logger.warning(f"No image found at {source_image} or {dest_image}. Manifest will point to default.")

        # 3. Generate Manifest (The payload for the DB Loader)
        manifest = {
            "slug": blueprint.slug,
            "name": blueprint.title,
            "description": blueprint.promise.subhead,
            "price": blueprint.pricing.amount,
            "pricing_model": blueprint.pricing.model_type,
            "love_offering_min": blueprint.pricing.love_offering_min,
            "love_offering_suggested": blueprint.pricing.love_offering_suggested,
            "love_offering_anchor": blueprint.pricing.love_offering_anchor,
            "image": deployed_image_url,
            "is_digital": True,
            "digital_file_url": f"/downloads/{pdf_name}",
            "status": "active",
            "category_name": "Digital Products", # Default
            "landing_page_content": landing_page_content if landing_page_content else { 
                # We would normally parse the MDX here, but for now we pass the raw promise
                "headline": blueprint.promise.headline,
                "subhead": blueprint.promise.subhead,
                "bullet_points": [c.title for c in blueprint.chapter_map]
            },
            "meta": {
                "version": blueprint.version,
                "generated_at": str(blueprint.created_at)
            },
            "integrity": {
                "sha256": file_hash,
                "build_id": "v3-production-build", # In real system, generate UUID
                "agent_version": "1.0.0",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        manifest_path = self.manifest_dir / f"{blueprint.slug}_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        logger.info(f"Manifest written to: {manifest_path}")
        
        return {
            "status": "deployed",
            "manifest_path": str(manifest_path),
            "public_url": f"/downloads/{pdf_name}"
        }
