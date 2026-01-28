"""
Salarsu Deployer - Deploys digital products to the SalarsNet store

Handles:
1. Copy ZIP to public/downloads/products/ (served as static file)
2. Generate product cover image (via DALL-E or placeholder)
3. Generate SQL INSERT for PostgreSQL database (BOTH products AND dreamweavings tables!)
4. Optionally commit and push to git

⚠️ CRITICAL: Digital products require BOTH database tables to be updated:
   - products.digital_file_url - Product catalog URL
   - dreamweavings.audio_url - Love Offering download system URL
   
The download URL pattern is: https://salars.net/downloads/products/{ZipFilename}

Usage:
    from packaging.salarsu_deployer import SalarsuDeployer
    
    deployer = SalarsuDeployer("/path/to/salarsu")
    result = deployer.deploy(
        zip_path="/path/to/Product.zip",
        product_name="Heart Connection Framework",
        product_slug="heart-connection-framework",
        description="Product description...",
        price=47.00,
        sale_price=27.00,
        generate_cover_image=True,
        landing_page_content={...}
    )
"""

import logging
import shutil
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SalarsuDeployer:
    """
    Deploys digital products to the SalarsNet store (salarsu repo).
    
    Digital products are:
    1. Copied to public/downloads/products/ for static file serving
    2. Cover image generated (if requested) and saved to public/images/products/
    3. SQL INSERT generated for BOTH products AND dreamweavings tables
       (Critical: Love Offering downloads use dreamweavings.audio_url)
    4. Optionally git committed and pushed
    
    Download URL pattern: https://salars.net/downloads/products/{ZipFilename}
    """
    
    # Production base URL for download links
    DOWNLOAD_BASE_URL = "https://salars.net/downloads/products"
    
    def __init__(self, salarsu_root: str):
        self.salarsu_root = Path(salarsu_root)
        # FIXED: Use public/downloads/products/ for static file serving
        self.downloads_dir = self.salarsu_root / "public" / "downloads" / "products"
        self.images_dir = self.salarsu_root / "public" / "images" / "products"
        self.sql_dir = self.salarsu_root  # SQL files go in repo root
        
    def deploy(
        self,
        zip_path: str,
        product_name: str,
        product_slug: str,
        description: str,
        price: float,
        sale_price: Optional[float] = None,
        sku: Optional[str] = None,
        landing_page_content: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
        image_alt: Optional[str] = None,
        generate_cover_image: bool = True,
        auto_commit: bool = False,
        auto_push: bool = False
    ) -> Dict[str, Any]:
        """
        Deploy a digital product to the SalarsNet store.
        
        Args:
            zip_path: Path to the product ZIP file
            product_name: Display name of the product
            product_slug: URL-safe slug for the product
            description: Product description for the store
            price: Regular price in USD
            sale_price: Optional sale price in USD
            sku: Optional SKU (auto-generated if not provided)
            landing_page_content: Optional landing page JSON content
            image_url: Optional product image URL (skips generation if provided)
            image_alt: Optional image alt text
            generate_cover_image: If True, generate cover image via DALL-E
            auto_commit: If True, git add and commit the files
            auto_push: If True, also push to origin (requires auto_commit)
            
        Returns:
            Dict with deployment status and file paths
        """
        logger.info(f"🚀 Deploying {product_name} to SalarsNet...")
        
        # Validate ZIP exists
        zip_file = Path(zip_path)
        if not zip_file.exists():
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")
        
        # 1. Ensure directories exist
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Copy ZIP to public/downloads/products/ (static serving)
        dest_filename = zip_file.name
        dest_path = self.downloads_dir / dest_filename
        logger.info(f"📦 Copying {zip_file.name} to {dest_path}")
        shutil.copy(zip_file, dest_path)
        
        # 3. Generate cover image (if not provided)
        image_path = None
        if not image_url and generate_cover_image:
            logger.info(f"🎨 Generating cover image for {product_name}...")
            image_path = self._generate_cover_image(product_name, product_slug, description)
            if image_path:
                image_url = f"/images/products/{product_slug}.png"
                image_alt = image_alt or f"{product_name} cover"
                logger.info(f"   ✅ Image saved: {image_path}")
        
        # 4. Generate SQL INSERT (for BOTH products AND dreamweavings tables!)
        sql_filename = f"{product_slug}.sql"
        sql_path = self.sql_dir / sql_filename
        
        # FIXED: Use absolute URL for static file serving
        download_url = f"{self.DOWNLOAD_BASE_URL}/{dest_filename}"
        
        sql_content = self._generate_sql(
            product_name=product_name,
            product_slug=product_slug,
            description=description,
            price=price,
            sale_price=sale_price,
            sku=sku or self._generate_sku(product_slug),
            download_url=download_url,
            landing_page_content=landing_page_content,
            image_url=image_url,
            image_alt=image_alt
        )
        
        logger.info(f"📝 Writing SQL to {sql_path}")
        with open(sql_path, 'w') as f:
            f.write(sql_content)
        
        # 5. Git operations (optional)
        files_to_commit = [dest_path, sql_path]
        if image_path:
            files_to_commit.append(Path(image_path))
            
        if auto_commit:
            self._git_commit_files(files_to_commit, product_name)
            
            if auto_push:
                self._git_push()
        
        result = {
            "status": "deployed",
            "zip_path": str(dest_path),
            "sql_path": str(sql_path),
            "image_path": str(image_path) if image_path else None,
            "download_url": download_url,
            "image_url": image_url,
            "product_slug": product_slug,
            "product_page_url": f"/store/product/{product_slug}"
        }
        
        logger.info(f"✅ Deployment complete!")
        logger.info(f"   ZIP: {dest_path}")
        logger.info(f"   SQL: {sql_path}")
        if image_path:
            logger.info(f"   Image: {image_path}")
        logger.info(f"   Download URL: {download_url}")
        
        return result
    
    def _generate_cover_image(
        self, 
        product_name: str, 
        product_slug: str, 
        description: str
    ) -> Optional[str]:
        """
        Generate a product cover image using DALL-E.
        
        Returns the path to the generated image, or None if generation failed.
        """
        output_path = self.images_dir / f"{product_slug}.png"
        
        # Create a cover image prompt based on product details
        prompt = self._create_cover_prompt(product_name, description)
        
        try:
            import openai
            
            client = openai.OpenAI()
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            # Download the image
            import requests
            image_url = response.data[0].url
            img_data = requests.get(image_url).content
            
            with open(output_path, 'wb') as f:
                f.write(img_data)
            
            logger.info(f"✅ Cover image generated via DALL-E: {product_slug}")
            return str(output_path)
            
        except ImportError:
            logger.warning("OpenAI not available, skipping cover image generation")
            return None
        except Exception as e:
            logger.warning(f"Cover image generation failed: {e}")
            return None
    
    def _create_cover_prompt(self, product_name: str, description: str) -> str:
        """Create a DALL-E prompt for the product cover image."""
        # Extract key themes from description
        desc_short = description[:200] if len(description) > 200 else description
        
        return f"""A professional, modern book cover design for "{product_name}". 
        
Theme based on: {desc_short}

Style requirements:
- Clean, premium aesthetic suitable for a digital product
- Warm, inviting color palette
- Symbolic imagery representing the product theme
- No text, just visual imagery
- Professional book or product cover composition
- High quality, polished look"""
    
    def _generate_sku(self, slug: str) -> str:
        """Generate a SKU from the product slug."""
        # Take first letters of each word, uppercase, add number
        parts = slug.split('-')
        prefix = ''.join(p[0].upper() for p in parts[:3])
        return f"{prefix}-001"
    
    def _generate_sql(
        self,
        product_name: str,
        product_slug: str,
        description: str,
        price: float,
        sale_price: Optional[float],
        sku: str,
        download_url: str,
        landing_page_content: Optional[Dict[str, Any]],
        image_url: Optional[str],
        image_alt: Optional[str]
    ) -> str:
        """Generate PostgreSQL INSERT statement for the product."""
        
        # Escape single quotes in text fields
        def escape_sql(s: str) -> str:
            if s is None:
                return 'NULL'
            return f"'{s.replace(chr(39), chr(39)+chr(39))}'"
        
        # Format landing page content as JSONB
        if landing_page_content:
            lpc_json = json.dumps(landing_page_content, indent=2)
            lpc_sql = f"'{lpc_json.replace(chr(39), chr(39)+chr(39))}'::jsonb"
        else:
            lpc_sql = "NULL"
        
        # Build SQL for BOTH tables (discovered Jan 28, 2026)
        # The system uses TWO tables for digital products:
        # 1. products.digital_file_url - Product catalog
        # 2. dreamweavings.audio_url - Love Offering download system
        sql = f"""-- {product_name} Product Deployment
-- Generated: {datetime.now().isoformat()}
-- Run this in your Coolify PostgreSQL database (10.0.1.7, database: postgres)
-- 
-- The ZIP file has been copied to: public/downloads/products/
-- Download URL: {download_url}
--
-- ⚠️ CRITICAL: You MUST update BOTH tables for downloads to work!

-- =============================================================================
-- STEP 1: Insert into products table (Product Catalog)
-- =============================================================================
INSERT INTO products (
  name,
  slug,
  description,
  price,
  sale_price,
  sku,
  category,
  status,
  stock_quantity,
  is_digital,
  digital_file_url,
  digital_file_type,
  landing_page_content,
  image_1,
  image_1_alt,
  created_at,
  updated_at
) VALUES (
  {escape_sql(product_name)},
  {escape_sql(product_slug)},
  {escape_sql(description)},
  {price:.2f},
  {f'{sale_price:.2f}' if sale_price else 'NULL'},
  {escape_sql(sku)},
  'digital-products',
  'active',
  999,
  true,
  {escape_sql(download_url)},
  'zip',
  {lpc_sql},
  {escape_sql(image_url) if image_url else "'https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=800'"},
  {escape_sql(image_alt) if image_alt else "'Product image'"},
  NOW(),
  NOW()
)
ON CONFLICT (slug) DO UPDATE SET
  digital_file_url = EXCLUDED.digital_file_url,
  description = EXCLUDED.description,
  updated_at = NOW()
RETURNING id, name, slug, digital_file_url;

-- =============================================================================
-- STEP 2: Insert/Update dreamweavings table (Love Offering Downloads)
-- This is REQUIRED for the Love Offering download flow to work!
-- =============================================================================
INSERT INTO dreamweavings (
  id,
  slug,
  title,
  description,
  audio_url,
  created_at
) VALUES (
  nextval('dreamweavings_id_seq')::text,
  {escape_sql(product_slug)},
  {escape_sql(product_name)},
  {escape_sql(description)},
  {escape_sql(download_url)},
  NOW()
)
ON CONFLICT (slug) DO UPDATE SET
  audio_url = EXCLUDED.audio_url,
  title = EXCLUDED.title,
  description = EXCLUDED.description
RETURNING id, slug, audio_url;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================
-- Check products table:
-- SELECT id, name, slug, is_digital, digital_file_url FROM products WHERE slug = {escape_sql(product_slug)};

-- Check dreamweavings table:
-- SELECT id, slug, audio_url FROM dreamweavings WHERE slug = {escape_sql(product_slug)};

-- Test download URL (should return HTTP 200):
-- curl -sI "{download_url}" | head -3
"""
        return sql
    
    def _git_commit_files(self, files: list, product_name: str):
        """Git add and commit the deployed files."""
        logger.info("📝 Committing to git...")
        
        try:
            # Git add all files
            file_paths = [str(f) for f in files]
            subprocess.run(
                ["git", "add"] + file_paths,
                cwd=self.salarsu_root,
                check=True,
                capture_output=True
            )
            
            # Git commit
            commit_msg = f"feat: Add {product_name} digital product"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.salarsu_root,
                check=True,
                capture_output=True
            )
            
            logger.info(f"✅ Committed: {commit_msg}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git commit failed: {e}")
            if e.stderr:
                logger.error(e.stderr.decode())
    
    def _git_push(self):
        """Push to origin main."""
        logger.info("🚀 Pushing to origin...")
        
        try:
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.salarsu_root,
                check=True,
                capture_output=True
            )
            logger.info("✅ Pushed to origin/main")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git push failed: {e}")
            if e.stderr:
                logger.error(e.stderr.decode())


def deploy_product(
    salarsu_root: str,
    zip_path: str,
    product_name: str,
    product_slug: str,
    description: str,
    price: float,
    sale_price: Optional[float] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to deploy a product.
    
    Example:
        result = deploy_product(
            salarsu_root="/home/rsalars/Projects/salarsu",
            zip_path="/path/to/Product.zip",
            product_name="Heart Connection Framework",
            product_slug="heart-connection-framework",
            description="The complete relationship guide...",
            price=47.00,
            sale_price=27.00,
            auto_commit=True,
            auto_push=True
        )
    """
    deployer = SalarsuDeployer(salarsu_root)
    return deployer.deploy(
        zip_path=zip_path,
        product_name=product_name,
        product_slug=product_slug,
        description=description,
        price=price,
        sale_price=sale_price,
        **kwargs
    )
