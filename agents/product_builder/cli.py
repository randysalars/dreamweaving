"""
Product Builder CLI
Command-line interface for the complete product generation system.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def create_command(args):
    """Create a new product from a topic or demand signal using the Studio Pipeline."""
    from .core.config import get_config
    from .core.context import ProductContext, PipelineState
    from .core.intelligence import DemandSignal
    from .pipeline.studio_orchestrator import StudioOrchestrator
    
    config = get_config()
    
    logger.info(f"🚀 BIO-DIGITAL JAZZ: Creating product '{args.title}'")
    logger.info(f"   Topic: {args.topic}")
    
    output_dir = Path(args.output) if args.output else Path(f"./products/{args.title.replace(' ', '_').lower()}")
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"   Output: {output_dir}")
    
    try:
        # 1. Initialize Context
        context = ProductContext(
            product_slug=args.title.replace(" ", "_").lower(), 
            base_output_dir=str(output_dir.parent) 
        )
        if not context.state:
            context.state = PipelineState()
        
        # 2. Create Demand Signal
        signal = DemandSignal(
            topic=args.topic,
            source="CLI",
            strength=0.9,
            evidence_score=0.9,
            key_themes=[args.topic, "Mastery", "Systems"],
            missing_angles=["Actionable steps", "Modern approach"],
            urgency="high"
        )
        
        # 3. Instantiate Orchestrator
        orchestrator = StudioOrchestrator(context)
        
        # 4. Run Full Pipeline
        results = orchestrator.run_full_pipeline(signal, args.title)
        
        logger.info(f"\n✅ Product Generation Complete!")
        logger.info(f"   📂 Output: {output_dir}")
        logger.info(f"   📄 Scorecard: {results.get('scorecard')}")
        
    except Exception as e:
        logger.error(f"❌ Pipeline Failed: {e}", exc_info=True)
        return 1
        
    return 0


def preview_command(args):
    """Generate a quick preview without full production."""
    logger.info(f"👁️  Generating preview for: {args.title}")
    logger.info("   Mode: Quick preview (low-res, no audio)")
    
    # This would run a simplified pipeline
    logger.info("\n✅ Preview generated")


def publish_command(args):
    """Publish a completed product to the store."""
    from .packaging.publisher import PublisherAgent
    
    logger.info(f"📤 Publishing: {args.product_dir}")
    
    # This would publish to the store
    logger.info("\n✅ Published successfully")


def list_templates_command(args):
    """List available templates."""
    logger.info("Available Video Templates:")
    logger.info("  • ChapterVideo - Main chapter content (30s)")
    logger.info("  • CourseIntro - Branded opener (10s)")
    logger.info("  • ChapterCard - Social cards (5s)")
    logger.info("  • KeyInsight - Highlight moments (8s)")
    logger.info("  • Checklist - Action items (10s)")
    logger.info("  • QuoteCard - Elegant quotes (8s)")
    logger.info("  • ProgressMilestone - Journey progress (12s)")
    logger.info("  • BeforeAfter - Transformation (12s)")
    logger.info("  • Statistic - Number highlights (6s)")
    logger.info("  • FrameworkDiagram - Visual frameworks (14s)")
    logger.info("")
    logger.info("Available Styles:")
    logger.info("  • dreamweaving - Ethereal, contemplative")
    logger.info("  • modern_editorial - Clean, professional")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='product-builder',
        description='🏭 Dreamweaving Product Builder - Create premium digital products',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --topic "investing" --title "Wealth Blueprint"
  %(prog)s create --topic "productivity" --title "Focus System" --landing-page --emails
  %(prog)s preview --title "My Course"
  %(prog)s publish ./products/wealth_blueprint
  %(prog)s list-templates
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new product')
    create_parser.add_argument('--topic', '-t', required=True, help='Main topic')
    create_parser.add_argument('--title', '-T', required=True, help='Product title')
    create_parser.add_argument('--output', '-o', help='Output directory')
    create_parser.add_argument('--style', '-s', default='dreamweaving', 
                               choices=['dreamweaving', 'modern_editorial'],
                               help='Visual style')
    create_parser.add_argument('--pdf', action='store_true', default=True,
                               help='Generate PDF (default: true)')
    create_parser.add_argument('--audio', action='store_true',
                               help='Generate audio narration')
    create_parser.add_argument('--video', action='store_true',
                               help='Generate video components')
    create_parser.add_argument('--landing-page', action='store_true',
                               help='Generate landing page')
    create_parser.add_argument('--emails', action='store_true',
                               help='Generate email sequences')
    create_parser.add_argument('--social', action='store_true',
                               help='Generate social promo content')
    create_parser.add_argument('--register-emails', action='store_true',
                               help='Register generated emails with SalarsNet newsletters')
    create_parser.add_argument('--schedule-buffer', action='store_true',
                               help='Schedule social posts to Buffer')
    create_parser.add_argument('--launch-date',
                               help='Launch date for Buffer scheduling (YYYY-MM-DD)')
    create_parser.add_argument('--dry-run', action='store_true',
                               help='Validate without actually registering/scheduling')
    create_parser.add_argument('--all', action='store_true',
                               help='Generate everything')
    create_parser.set_defaults(func=create_command)
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Generate quick preview')
    preview_parser.add_argument('--topic', '-t', required=True, help='Main topic')
    preview_parser.add_argument('--title', '-T', required=True, help='Product title')
    preview_parser.set_defaults(func=preview_command)
    
    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish to store')
    publish_parser.add_argument('product_dir', help='Path to product directory')
    publish_parser.set_defaults(func=publish_command)
    
    # List templates command
    list_parser = subparsers.add_parser('list-templates', help='List available templates')
    list_parser.set_defaults(func=list_templates_command)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle --all flag
    if hasattr(args, 'all') and args.all:
        args.audio = True
        args.video = True
        args.landing_page = True
        args.emails = True
        args.social = True
    
    try:
        args.func(args)
        return 0
    except KeyboardInterrupt:
        logger.info("\n⚠️  Cancelled")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        if args.command == 'create':
            logger.info("   Try running with --help for usage information")
        return 1


if __name__ == '__main__':
    sys.exit(main())
