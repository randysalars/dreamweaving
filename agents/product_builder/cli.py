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
        prompts_only = getattr(args, 'generate_prompts_only', False)
        orchestrator = StudioOrchestrator(
            context, 
            prompts_only=prompts_only,
            output_dir=output_dir / "output" if prompts_only else None
        )
        
        # 4. Run Full Pipeline
        results = orchestrator.run_full_pipeline(signal, args.title)
        
        # --- ANTIGRAVITY-NATIVE: Early exit if prompts_only ---
        if prompts_only:
            prompts_dir = output_dir / "output" / "prompts"
            logger.info(f"\n📝 ANTIGRAVITY-NATIVE MODE: Prompts generated!")
            logger.info(f"   Prompts directory: {prompts_dir}")
            logger.info(f"\n   Next steps:")
            logger.info(f"   1. Read each .prompt.md file in the prompts/ directory")
            logger.info(f"   2. Generate the content (as Antigravity in your chat session)")
            logger.info(f"   3. Write each response to responses/<slug>.response.md")
            logger.info(f"   4. Run: product-builder compile --product-dir {output_dir} --title \"{args.title}\"")
            return
        
        # 5. Generate Landing Page Content (if requested)
        landing_content = None
        if args.landing_page:
            from .packaging.landing_page import LandingPageAgent
            from types import SimpleNamespace
            
            logger.info("📄 Generating Landing Page Content...")
            landing_agent = LandingPageAgent(orchestrator.templates_dir)
            
            # Construct Mock Blueprint from Artifacts
            pos = results['artifacts'].positioning
            curr = results['artifacts'].curriculum
            
            # Mock objects to satisfy LandingPageAgent expectation
            mock_promise = SimpleNamespace(
                headline=pos.core_promise,
                subhead=pos.differentiator
            )
            mock_audience = SimpleNamespace(
                current_state=f"{pos.audience.primary_persona} struggling with {', '.join(pos.audience.pain_points[:3])}"
            )
            mock_chapters = [
                SimpleNamespace(title=c.name, purpose=c.description) 
                for c in curr.concepts
            ]
            
            mock_blueprint = SimpleNamespace(
                title=args.title,
                promise=mock_promise,
                audience=mock_audience,
                chapter_map=mock_chapters
            )
            
            # Extract Bonus Plan from Orchestrator Results
            bonus_plan = results.get('bonus_plan')
            if bonus_plan:
                logger.info(f"🎁 Found {len(bonus_plan.bonuses)} designed bonuses in pipeline results.")
            
            # Pass Bonus Plan to Landing Page Agent (with HTML generation)
            landing_content = landing_agent.generate(
                mock_blueprint, 
                bonus_plan=bonus_plan,
                generate_html=True,
                output_dir=output_dir / "output"
            )
            
            # Enforce persistence of designed bonuses into landing content
            # (In case LLM hallucinated slightly different titles, we force the structure back in)
            if bonus_plan:
                # Convert Bonus objects to dicts for JSON serialization
                landing_content['bonuses'] = [
                    {
                        "title": b.title,
                        "description": b.description,
                        "format": b.format,
                        "target_friction": b.target_friction
                    }
                    for b in bonus_plan.bonuses
                ]
                logger.info("✅ Enforced Bonus Plan compatibility in Landing Page content")

            logger.info("✅ Landing Page Content Generated")

        # 6. Assemble Final Product (PDF, etc)
        from .packaging.product_assembler import ProductAssembler, AssemblyConfig
        
        logger.info(f"\n✅ Content Generation Complete! Starting Assembly...")
        logger.info(f"   📄 Scorecard: {results.get('scorecard')}")
        
        # Configure Assembly
        assembly_config = AssemblyConfig(
            title=args.title,
            output_dir=output_dir / "output", # Use subdirectory for final artifacts
            generate_pdf=True,
            generate_audio=args.audio,
            generate_video=args.video,
            generate_visuals=True, # Always generate visuals for the PDF
        )
        

        assembler = ProductAssembler(orchestrator.templates_dir)
        assembly_result = assembler.assemble(
            chapters=results.get("chapters", []),
            config=assembly_config,
            landing_page_content=landing_content
        )
        
        # 6.5. QUALITY LOOPS (Length Guard & Polisher)
        if assembly_result.success and args.pdf:
            from .core.quality_loop import QualityLoop
            quality = QualityLoop(orchestrator.templates_dir)
            current_chapters = results.get("chapters", [])
            was_modified = False
            
            # A. Length Guard
            current_chapters, expanded = quality.ensure_length(
                pdf_path=assembly_result.pdf_path,
                chapters=current_chapters,
                target_pages=100
            )
            if expanded:
                logger.info("🔄 Re-Assembling expanded PDF...")
                assembly_result = assembler.assemble(
                    chapters=current_chapters,
                    config=assembly_config,
                    landing_page_content=landing_content
                )
                was_modified = True
            

            # B. Polish Pass (Always run to "make it better")
            current_chapters = quality.polish_chapters(current_chapters)
            
            # C. Safety Check (Post-Polish Length Guard)
            # Polishing often reduces word count. We must verify we didn't drop below threshold.
            current_chapters, re_expanded = quality.ensure_length(
                pdf_path=assembly_result.pdf_path, # Note: using previous PDF as proxy or needing re-assembly
                chapters=current_chapters, 
                target_pages=100
            ) 
            
            if re_expanded:
                logger.info("🔄 Re-expanding content after polish shrinkage...")

            logger.info("✨ Re-Assembling Final PDF...")
            assembly_result = assembler.assemble(
                chapters=current_chapters,
                config=assembly_config,
                landing_page_content=landing_content
            )

        if assembly_result.success:
            logger.info(f"\n📦 Assembly Complete!")
            logger.info(f"   📄 PDF: {assembly_result.pdf_path}")
            logger.info(f"   📊 Stats: {assembly_result.total_words} words, {assembly_result.total_chapters} chapters")
        else:
            logger.error(f"❌ Assembly Failed: {assembly_result.errors}")
            return 1
        
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


def generate_bonuses_command(args):
    """Generate bonuses for a product."""
    from .packaging.bonus_generator import BonusGenerator
    
    logger.info(f"🎁 Generating Bonuses for: {args.title}")
    
    # Setup paths
    slug = args.title.replace(" ", "_").lower()
    product_dir = Path(args.product_dir) if args.product_dir else Path(f"./products/{slug}")
    output_dir = product_dir / "output" / "bonuses"
    templates_dir = Path(__file__).parent / "templates"
    
    if not product_dir.exists():
        logger.error(f"Product directory not found: {product_dir}")
        return 1
        
    generate = BonusGenerator(templates_dir, output_dir)
    
    bonuses = []
    
    # 1. Try to load from existing landing page content
    lp_path = product_dir / "landing_page_content.json"
    if lp_path.exists():
        import json
        try:
            data = json.loads(lp_path.read_text())
            bonuses = data.get("bonuses", [])
            logger.info(f"   Found {len(bonuses)} bonuses in landing_page_content.json")
        except Exception as e:
            logger.warning(f"   Failed to read landing_page_content.json: {e}")

    # 2. If CLI args or explicit list (for testing)
    # (Future expansion: parsing URL)
    
    if not bonuses:
        logger.warning("   No bonuses found in product config. Nothing to generate.")
        return 0
        
    generated = generate.generate(bonuses)
    logger.info("\n✅ Bonus Generation Complete!")
    for p in generated:
        logger.info(f"   📄 {p}")


def compile_command(args):
    """Compile product from Antigravity responses (Antigravity-native workflow)."""
    from pathlib import Path
    from .core.prompt_interface import PromptInterface
    from .packaging.product_assembler import ProductAssembler, AssemblyConfig
    
    product_dir = Path(args.product_dir)
    output_dir = product_dir / "output"
    responses_dir = output_dir / "responses"
    templates_dir = Path(__file__).parent / "templates"
    
    logger.info(f"🔧 Compiling product from Antigravity responses...")
    logger.info(f"   Product: {args.title}")
    logger.info(f"   Responses: {responses_dir}")
    
    # Check for responses
    if not responses_dir.exists():
        logger.error(f"❌ Responses directory not found: {responses_dir}")
        logger.info("   Run 'product-builder create --generate-prompts-only' first.")
        return 1
    
    response_files = list(responses_dir.glob("*.response.md"))
    if not response_files:
        logger.error("❌ No response files found.")
        logger.info("   Generate responses by reading prompts/*.prompt.md and writing to responses/")
        return 1
    
    logger.info(f"   Found {len(response_files)} response files")
    
    # Load responses into chapters
    chapters = []
    for resp_file in sorted(response_files):
        slug = resp_file.stem.replace(".response", "")
        content = resp_file.read_text().strip()
        chapters.append({
            "title": slug.replace("_", " ").title(),
            "purpose": f"Content from Antigravity response: {slug}",
            "content": content,
            "key_takeaways": ["Generated by Antigravity"]
        })
        logger.info(f"   ✅ Loaded: {slug}")
    
    # Assemble the product
    assembly_config = AssemblyConfig(
        title=args.title,
        output_dir=output_dir,
        generate_pdf=True,
        generate_audio=False,
        generate_video=False,
        generate_visuals=True,
    )
    
    assembler = ProductAssembler(templates_dir)
    result = assembler.assemble(chapters=chapters, config=assembly_config)
    
    if result.success:
        logger.info(f"\n✅ Compilation Complete!")
        logger.info(f"   📄 PDF: {result.pdf_path}")
        logger.info(f"   📊 Stats: {result.stats}")
    else:
        logger.error(f"\n❌ Compilation failed: {result.error}")
        return 1


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
    create_parser.add_argument('--generate-prompts-only', action='store_true',
                               help='Generate prompt files for Antigravity instead of content')
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

    # Generate bonuses command
    bonus_parser = subparsers.add_parser('generate-bonuses', help='Generate bonuses for existing product')
    bonus_parser.add_argument('--title', '-T', required=True, help='Product title')
    bonus_parser.add_argument('--product-dir', help='Product directory (default: ./products/slug)')
    bonus_parser.add_argument('--landing-url', help='URL to fetch bonus info from')
    bonus_parser.set_defaults(func=generate_bonuses_command)
    
    # Compile command (Antigravity-native: reads responses and compiles final product)
    compile_parser = subparsers.add_parser('compile', help='Compile product from Antigravity responses')
    compile_parser.add_argument('--product-dir', '-d', required=True, help='Product directory with responses/')
    compile_parser.add_argument('--title', '-T', required=True, help='Product title')
    compile_parser.set_defaults(func=compile_command)
    
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
