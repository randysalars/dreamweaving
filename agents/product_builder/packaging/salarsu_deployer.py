"""
Salarsu Deployer - Deploys digital products to the SalarsNet store

Handles:
1. Copy ZIP to content/lead-magnets/ (served via /api/files/lead-magnets/[filename])
2. Generate SQL INSERT for PostgreSQL database
3. Optionally commit and push to git

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
        landing_page_content={...}
    )
"""

import logging
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SalarsuDeployer:
    """
    Deploys digital products to the SalarsNet store (salarsu repo).
    
    Digital products are:
    1. Copied to content/lead-magnets/ for serving via /api/files/lead-magnets/
    2. SQL INSERT generated for the products table
    3. Optionally git committed and pushed
    """
    
    def __init__(self, salarsu_root: str):
        self.salarsu_root = Path(salarsu_root)
        self.content_dir = self.salarsu_root / "content" / "lead-magnets"
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
            image_url: Optional product image URL
            image_alt: Optional image alt text
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
        
        # 1. Ensure content directory exists
        self.content_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Copy ZIP to content/lead-magnets/
        dest_filename = zip_file.name
        dest_path = self.content_dir / dest_filename
        logger.info(f"📦 Copying {zip_file.name} to {dest_path}")
        shutil.copy(zip_file, dest_path)
        
        # 3. Generate SQL INSERT
        sql_filename = f"{product_slug}.sql"
        sql_path = self.sql_dir / sql_filename
        
        download_url = f"/api/files/lead-magnets/{dest_filename}"
        
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
        
        # 4. Git operations (optional)
        if auto_commit:
            self._git_commit(dest_path, sql_path, product_name)
            
            if auto_push:
                self._git_push()
        
        result = {
            "status": "deployed",
            "zip_path": str(dest_path),
            "sql_path": str(sql_path),
            "download_url": download_url,
            "product_slug": product_slug,
            "product_page_url": f"/store/product/{product_slug}"
        }
        
        logger.info(f"✅ Deployment complete!")
        logger.info(f"   ZIP: {dest_path}")
        logger.info(f"   SQL: {sql_path}")
        logger.info(f"   Download URL: {download_url}")
        
        return result
    
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
        
        # Build SQL
        sql = f"""-- {product_name} Product Insert
-- Generated: {datetime.now().isoformat()}
-- Run this in your Coolify PostgreSQL database
-- 
-- The ZIP file has been copied to: content/lead-magnets/
-- It will be served via: {download_url}

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
RETURNING id, name, slug, digital_file_url;

-- Verify with:
-- SELECT id, name, slug, is_digital, digital_file_url FROM products WHERE slug = {escape_sql(product_slug)};
"""
        return sql
    
    def _git_commit(self, zip_path: Path, sql_path: Path, product_name: str):
        """Git add and commit the deployed files."""
        logger.info("📝 Committing to git...")
        
        try:
            # Git add
            subprocess.run(
                ["git", "add", str(zip_path), str(sql_path)],
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
