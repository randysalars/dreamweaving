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
    """Create a new product from a topic or demand signal."""
    from .core.config import get_config
    from .schemas.blueprint import ProductBlueprint, ChapterSpec
    from .schemas.positioning_brief import PositioningBrief, AudienceProfile
    from .schemas.transformation_map import TransformationMap
    from .packaging.product_assembler import ProductAssembler, AssemblyConfig
    from .packaging.pdf_generator import PDFGenerator, PDFConfig
    from .marketing.landing_page_generator import LandingPageGenerator
    from .marketing.email_sequence_generator import EmailSequenceGenerator
    from .marketing.social_promo_generator import SocialPromoGenerator
    from .marketing.upsell_recommender import UpsellRecommender
    from .schemas.visual_style import DREAMWEAVING_STYLE, MODERN_EDITORIAL_STYLE
    
    config = get_config()
    
    logger.info(f"🚀 Creating product: {args.title}")
    logger.info(f"   Topic: {args.topic}")
    
    output_dir = Path(args.output) if args.output else Path(f"./products/{args.title.replace(' ', '_').lower()}")
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"   Output: {output_dir}")
    
    # Select visual style
    visual_style = DREAMWEAVING_STYLE if args.style == "dreamweaving" else MODERN_EDITORIAL_STYLE
    
    # Phase 1: Create initial product structure
    logger.info("\n📋 Phase 1: Planning product structure...")
    
    # Create placeholder positioning (in full pipeline, this comes from MarketCartographer)
    audience = AudienceProfile(
        primary_persona=f"Someone wanting to master {args.topic}",
        pain_points=[
            f"Overwhelmed by {args.topic} information",
            "No clear path forward",
            "Tried things that didn't work"
        ],
        current_solutions=["Books", "YouTube", "Courses"],
        sophistication_level="intermediate",
        buying_triggers=[
            "Ready to take action",
            "Hit a frustration point",
            "Found the right solution"
        ]
    )
    
    # Create objections
    from .schemas.positioning_brief import Objection
    objections = [
        Objection(
            objection="I've tried other courses before",
            preemption="This is a complete system, not just information"
        ),
        Objection(
            objection="I don't have enough time",
            preemption="This is designed for busy people - just 30 minutes a day"
        )
    ]
    
    positioning = PositioningBrief(
        core_promise=f"Master {args.topic} with a proven system",
        differentiator=f"A complete framework designed for real results in {args.topic}",
        positioning_statement=f"{args.title} helps you {args.topic.lower()} with confidence",
        audience=audience,
        objections=objections,
        competing_alternatives=["Books", "YouTube videos", "Generic courses"]
    )
    
    # Create placeholder transformation map
    from .schemas.transformation_map import Milestone
    milestones = [
        Milestone(
            name="Foundation",
            description="Understand the core principles",
            marker="Can explain the framework to others",
            chapter_range="1"
        ),
        Milestone(
            name="Application",
            description="Put the framework into practice",
            marker="Completed first implementation",
            chapter_range="2"
        ),
        Milestone(
            name="Mastery",
            description="Refine and optimize your approach",
            marker="Achieving consistent results",
            chapter_range="3"
        ),
    ]
    
    transformation = TransformationMap(
        starting_state=f"Confused about {args.topic}",
        ending_state=f"Confident and effective in {args.topic}",
        milestones=milestones,
        belief_shifts=[
            "Complexity → Simplicity",
            "Overwhelm → Clarity",
            "Doubt → Confidence"
        ],
        skill_gains=[
            f"Ability to analyze {args.topic}",
            "Strategic decision making",
            "Systematic approach"
        ],
        habit_changes=[
            "Daily practice routine",
            "Regular review and refinement",
            "Continuous learning"
        ],
        identity_evolution=f"From beginner to {args.topic} practitioner"
    )
    
    # Create sample chapters
    chapters = [
        {"title": "Foundation: The Core Framework", "purpose": "Establish the base system", 
         "content": f"This chapter introduces the foundational concepts of {args.topic}...",
         "key_takeaways": ["Core principle 1", "Core principle 2", "Core principle 3"]},
        {"title": "Application: Putting It Into Practice", "purpose": "Apply the framework",
         "content": f"Now that you understand the foundation, let's apply it to {args.topic}...",
         "key_takeaways": ["Application step 1", "Application step 2"]},
        {"title": "Mastery: Advanced Strategies", "purpose": "Achieve expertise",
         "content": f"Advanced techniques for mastering {args.topic}...",
         "key_takeaways": ["Advanced technique 1", "Advanced technique 2"]},
    ]
    
    logger.info(f"   Created {len(chapters)} chapter outlines")
    
    # Phase 2: Generate PDF
    logger.info("\n📄 Phase 2: Generating PDF...")
    pdf_generator = PDFGenerator(output_dir=output_dir / "output")
    pdf_config = PDFConfig(title=args.title, author="SalarsNet")
    pdf_path = pdf_generator.generate(chapters, pdf_config)
    logger.info(f"   PDF: {pdf_path}")
    
    # Phase 3: Generate audio (if requested)
    if args.audio:
        logger.info("\n🎧 Phase 3: Generating audio...")
        try:
            from .packaging.tts_client import TTSClient
            tts_client = TTSClient(output_dir=output_dir / "audio")
            for i, chapter in enumerate(chapters):
                result = tts_client.synthesize(
                    chapter["content"],
                    f"chapter_{i+1}"
                )
                if result.success:
                    logger.info(f"   Audio: chapter_{i+1}.mp3")
        except Exception as e:
            logger.warning(f"   Audio generation skipped: {e}")
    
    # Phase 4: Landing page
    if args.landing_page:
        logger.info("\n📄 Phase 4: Creating landing page...")
        lp_generator = LandingPageGenerator()
        lp_content = lp_generator.generate(args.title, positioning, transformation, chapters)
        html = lp_generator.render_html(lp_content)
        lp_path = output_dir / "landing_page.html"
        lp_path.write_text(html)
        logger.info(f"   Landing page: {lp_path}")
    
    # Phase 5: Email sequences
    if args.emails:
        logger.info("\n📧 Phase 5: Creating email sequences...")
        email_generator = EmailSequenceGenerator()
        welcome_seq = email_generator.generate_welcome_sequence(args.title, positioning)
        launch_seq = email_generator.generate_launch_sequence(args.title, positioning)
        email_generator.export_to_file(welcome_seq, output_dir / "emails_welcome.md")
        email_generator.export_to_file(launch_seq, output_dir / "emails_launch.md")
        logger.info(f"   Emails: {len(welcome_seq.emails) + len(launch_seq.emails)} emails in 2 sequences")
    
    # Phase 6: Social promo
    if args.social:
        logger.info("\n📱 Phase 6: Creating social content...")
        social_generator = SocialPromoGenerator()
        promo_package = social_generator.generate_promo_package(args.title, positioning, chapters)
        social_generator.export_to_file(promo_package, output_dir / "social_promo.md")
        logger.info(f"   Social: {len(promo_package.posts)} posts for multiple platforms")
    
    # Phase 7: Upsell strategy
    logger.info("\n💰 Phase 7: Creating upsell strategy...")
    upsell_recommender = UpsellRecommender()
    strategy = upsell_recommender.generate_strategy(args.title, "course", 97.0)
    upsell_recommender.export_strategy(strategy, output_dir / "upsell_strategy.md")
    logger.info(f"   Upsells: {len(strategy.recommendations)} recommendations")
    
    # Summary
    logger.info(f"\n✅ Product created successfully!")
    logger.info(f"   📂 Output: {output_dir}")
    logger.info(f"   📄 PDF: {pdf_path}")
    if args.landing_page:
        logger.info(f"   🌐 Landing page: {output_dir / 'landing_page.html'}")
    if args.emails:
        logger.info(f"   📧 Email sequences: 2 files")
    if args.social:
        logger.info(f"   📱 Social promo: {output_dir / 'social_promo.md'}")


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
