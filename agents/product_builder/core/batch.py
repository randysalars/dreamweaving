"""
Batch Processing
Create multiple products from a YAML configuration file.
"""

import yaml
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)


@dataclass
class BatchProduct:
    """A product to create in a batch."""
    topic: str
    title: str
    template: Optional[str] = None
    price: float = 47.00
    sale_price: Optional[float] = None
    launch_date: Optional[str] = None
    deploy: bool = False
    schedule: bool = False


@dataclass
class BatchConfig:
    """Configuration for batch product creation."""
    defaults: Dict[str, Any]
    products: List[BatchProduct]
    parallel: int = 1
    output_dir: str = "./products"
    salarsu_root: str = "/home/rsalars/Projects/salarsu"


def parse_batch_config(config_path: Path) -> BatchConfig:
    """Parse a YAML batch configuration file."""
    with open(config_path) as f:
        data = yaml.safe_load(f)
    
    defaults = data.get('defaults', {})
    products_data = data.get('products', [])
    
    products = []
    for p in products_data:
        # Apply defaults
        product_dict = {**defaults, **p}
        products.append(BatchProduct(
            topic=product_dict.get('topic', ''),
            title=product_dict.get('title', ''),
            template=product_dict.get('template'),
            price=product_dict.get('price', 47.00),
            sale_price=product_dict.get('sale_price'),
            launch_date=product_dict.get('launch_date'),
            deploy=product_dict.get('deploy', False),
            schedule=product_dict.get('schedule', False),
        ))
    
    return BatchConfig(
        defaults=defaults,
        products=products,
        parallel=data.get('parallel', 1),
        output_dir=data.get('output_dir', './products'),
        salarsu_root=data.get('salarsu_root', '/home/rsalars/Projects/salarsu'),
    )


def create_single_product(product: BatchProduct, config: BatchConfig, 
                          create_func, progress_lock: threading.Lock,
                          progress: Dict[str, str]) -> Dict[str, Any]:
    """Create a single product in the batch."""
    from argparse import Namespace
    
    slug = product.title.replace(" ", "_").lower()
    output_path = Path(config.output_dir) / slug
    
    with progress_lock:
        progress[product.title] = "🔄 Creating..."
    
    try:
        args = Namespace(
            topic=product.topic,
            title=product.title,
            output=str(output_path),
            template=product.template,
            style='dreamweaving',
            pdf=True,
            audio=False,
            video=False,
            landing_page=True,
            emails=True,
            social=True,
            register_emails=False,
            schedule_buffer=False,
            launch_date=product.launch_date,
            dry_run=False,
            generate_prompts_only=True,  # Batch always uses prompts-only for Antigravity
            all=False,
        )
        
        result = create_func(args)
        
        if result == 0:
            with progress_lock:
                progress[product.title] = "✅ Complete"
            return {"title": product.title, "success": True, "path": str(output_path)}
        else:
            with progress_lock:
                progress[product.title] = "❌ Failed"
            return {"title": product.title, "success": False, "error": "Create failed"}
            
    except Exception as e:
        with progress_lock:
            progress[product.title] = f"❌ Error: {str(e)[:30]}"
        return {"title": product.title, "success": False, "error": str(e)}


def run_batch(config: BatchConfig, create_func) -> List[Dict[str, Any]]:
    """Run batch product creation."""
    results = []
    progress = {}
    progress_lock = threading.Lock()
    
    logger.info(f"\n🏭 BATCH PROCESSING: {len(config.products)} products")
    logger.info(f"   Parallelism: {config.parallel}")
    logger.info(f"   Output: {config.output_dir}")
    logger.info("")
    
    # Initialize progress
    for product in config.products:
        progress[product.title] = "⏳ Pending"
    
    # Print initial status
    _print_batch_status(progress)
    
    if config.parallel <= 1:
        # Sequential processing
        for product in config.products:
            result = create_single_product(
                product, config, create_func, progress_lock, progress
            )
            results.append(result)
            _print_batch_status(progress)
    else:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=config.parallel) as executor:
            futures = {
                executor.submit(
                    create_single_product, 
                    product, config, create_func, progress_lock, progress
                ): product 
                for product in config.products
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                _print_batch_status(progress)
    
    return results


def _print_batch_status(progress: Dict[str, str]):
    """Print current batch progress."""
    logger.info("\n" + "─" * 60)
    for title, status in progress.items():
        logger.info(f"  {status:15} {title[:40]}")
    logger.info("─" * 60)


def generate_batch_report(results: List[Dict[str, Any]], output_path: Path):
    """Generate a report of batch processing."""
    success_count = sum(1 for r in results if r.get('success'))
    fail_count = len(results) - success_count
    
    report = [
        "# Batch Processing Report",
        "",
        f"**Total:** {len(results)} products",
        f"**Success:** {success_count}",
        f"**Failed:** {fail_count}",
        "",
        "## Products",
        "",
    ]
    
    for r in results:
        status = "✅" if r.get('success') else "❌"
        report.append(f"- {status} **{r['title']}**")
        if r.get('path'):
            report.append(f"  - Path: `{r['path']}`")
        if r.get('error'):
            report.append(f"  - Error: {r['error']}")
    
    report.append("")
    report.append("## Next Steps")
    report.append("")
    report.append("1. Review prompts in each product's `output/prompts/` directory")
    report.append("2. Generate responses with Antigravity")
    report.append("3. Run `product-builder compile` for each product")
    report.append("4. Run `product-builder deploy` to publish")
    
    output_path.write_text("\n".join(report))
    logger.info(f"\n📋 Report saved: {output_path}")


# Example YAML configuration
EXAMPLE_BATCH_YAML = """# Batch Product Configuration
# Save this as products.yaml and run:
# product-builder batch --config products.yaml

defaults:
  price: 47.00
  template: ebook
  deploy: false

products:
  - topic: "meditation for beginners"
    title: "The Mindfulness Manual"
    price: 29.99
    
  - topic: "stoic philosophy for modern life"
    title: "Daily Stoic Wisdom"
    
  - topic: "productivity and focus"
    title: "The Focus Framework"
    template: mini-course
    price: 19.00
    
  - topic: "financial independence"
    title: "Wealth Building Blueprint"
    template: premium-ebook
    price: 67.00

# Optional settings
parallel: 2
output_dir: ./products
"""
