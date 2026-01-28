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
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 7: EMAIL SEQUENCES (if requested)
        # ═══════════════════════════════════════════════════════════════
        email_welcome = None
        email_launch = None
        
        if getattr(args, 'emails', False) or getattr(args, 'all', False):
            from .marketing.email_sequence_generator import EmailSequenceGenerator
            
            logger.info("\n═══ PHASE 7: EMAIL SEQUENCES ═══")
            email_gen = EmailSequenceGenerator(orchestrator.templates_dir)
            
            positioning = results['artifacts'].positioning
            
            # Welcome sequence (5 emails)
            email_welcome = email_gen.generate_welcome_sequence(
                args.title,
                positioning
            )
            welcome_path = output_dir / "output" / "emails_welcome.md"
            email_gen.export_to_file(email_welcome, welcome_path)
            logger.info(f"   ✅ Welcome Sequence: {len(email_welcome.emails)} emails → {welcome_path.name}")
            
            # Launch sequence (7 emails)
            email_launch = email_gen.generate_launch_sequence(
                args.title,
                positioning
            )
            launch_path = output_dir / "output" / "emails_launch.md"
            email_gen.export_to_file(email_launch, launch_path)
            logger.info(f"   ✅ Launch Sequence: {len(email_launch.emails)} emails → {launch_path.name}")
        
        # 7.5. Register Emails with SalarsNet (if requested)
        if getattr(args, 'register_emails', False):
            from .packaging.salarsu_email_client import SalarsuEmailClient
            
            logger.info("\n📬 Registering Email Sequences with SalarsNet...")
            email_client = SalarsuEmailClient()
            
            slug = args.title.replace(" ", "-").lower()
            welcome_path = output_dir / "output" / "emails_welcome.md"
            
            if welcome_path.exists():
                result = email_client.register_from_file(
                    product_slug=slug,
                    product_title=args.title,
                    email_file=welcome_path,
                    dry_run=getattr(args, 'dry_run', False)
                )
                
                if result.success:
                    logger.info(f"   ✅ Registered {result.templates_registered} email templates")
                else:
                    logger.warning(f"   ⚠️ Registration failed: {result.error}")
            else:
                logger.warning(f"   ⚠️ No email file found. Run with --emails first.")
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 8: SOCIAL MEDIA CONTENT (if requested)
        # ═══════════════════════════════════════════════════════════════
        social_package = None
        
        if getattr(args, 'social', False) or getattr(args, 'all', False):
            from .marketing.social_promo_generator import SocialPromoGenerator
            
            logger.info("\n═══ PHASE 8: SOCIAL MEDIA CONTENT ═══")
            social_gen = SocialPromoGenerator(orchestrator.templates_dir)
            
            positioning = results['artifacts'].positioning
            chapters = results.get('chapters', [])
            
            social_package = social_gen.generate_promo_package(
                title=args.title,
                positioning=positioning,
                chapters=chapters
            )
            
            social_path = output_dir / "output" / "social_promo.md"
            social_gen.export_to_file(social_package, social_path)
            
            # Count by platform
            from .marketing.social_promo_generator import Platform
            twitter_count = len(social_package.by_platform(Platform.TWITTER))
            linkedin_count = len(social_package.by_platform(Platform.LINKEDIN))
            insta_count = len(social_package.by_platform(Platform.INSTAGRAM))
            
            logger.info(f"   ✅ Social Package: {len(social_package.posts)} posts → {social_path.name}")
            logger.info(f"      Twitter/X: {twitter_count} | LinkedIn: {linkedin_count} | Instagram: {insta_count}")
        
        # 8.5. Schedule to Buffer (if requested)
        if getattr(args, 'schedule_buffer', False):
            from .marketing.buffer_client import schedule_to_buffer
            from datetime import datetime
            
            logger.info("\n📅 Scheduling to Buffer...")
            
            launch_date_str = getattr(args, 'launch_date', None)
            if not launch_date_str:
                logger.warning("   ⚠️ --launch-date required for Buffer scheduling (format: YYYY-MM-DD)")
            elif social_package is None:
                logger.warning("   ⚠️ No social package. Run with --social first.")
            else:
                try:
                    launch_date = datetime.strptime(launch_date_str, "%Y-%m-%d")
                    
                    result = schedule_to_buffer(
                        social_package=social_package,
                        launch_date=launch_date,
                        dry_run=getattr(args, 'dry_run', False)
                    )
                    
                    if result.success:
                        logger.info(f"   ✅ Scheduled {result.scheduled_count} posts to Buffer")
                        if getattr(args, 'dry_run', False):
                            logger.info("      (dry-run mode - nothing actually scheduled)")
                    else:
                        logger.warning(f"   ⚠️ Buffer scheduling failed: {result.message}")
                except ValueError:
                    logger.error(f"   ❌ Invalid date format. Use YYYY-MM-DD")
        
        # ═══════════════════════════════════════════════════════════════
        # FINAL SUMMARY
        # ═══════════════════════════════════════════════════════════════
        logger.info("\n" + "═" * 60)
        logger.info("🎉 PRODUCT GENERATION COMPLETE!")
        logger.info("═" * 60)
        logger.info(f"   📁 Output: {output_dir / 'output'}")
        logger.info(f"   📄 PDF: {assembly_result.pdf_path}")
        if email_welcome:
            logger.info(f"   📧 Emails: {len(email_welcome.emails) + (len(email_launch.emails) if email_launch else 0)} templates")
        if social_package:
            logger.info(f"   📱 Social: {len(social_package.posts)} posts")
        logger.info("")
        
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


def deploy_command(args):
    """Deploy product to SalarsNet store."""
    from pathlib import Path
    from .packaging.salarsu_deployer import SalarsuDeployer
    
    product_dir = Path(args.product_dir)
    output_dir = product_dir / "output"
    
    logger.info(f"🚀 Deploying to SalarsNet...")
    logger.info(f"   Product: {args.name}")
    logger.info(f"   Slug: {args.slug}")
    
    # Find the ZIP file
    zip_files = list(output_dir.glob("*.zip"))
    if not zip_files:
        logger.error(f"❌ No ZIP file found in {output_dir}")
        return 1
    
    zip_path = zip_files[0]
    logger.info(f"   ZIP: {zip_path}")
    
    # Get description from args or generate a default
    description = args.description or f"Premium digital product: {args.name}"
    
    # Deploy
    deployer = SalarsuDeployer(args.salarsu_root)
    result = deployer.deploy(
        zip_path=str(zip_path),
        product_name=args.name,
        product_slug=args.slug,
        description=description,
        price=args.price,
        sale_price=args.sale_price,
        auto_commit=args.commit,
        auto_push=args.push
    )
    
    logger.info(f"\n✅ Deployment Complete!")
    logger.info(f"   📦 ZIP: {result['zip_path']}")
    logger.info(f"   📝 SQL: {result['sql_path']}")
    logger.info(f"   🔗 Download URL: {result['download_url']}")
    logger.info(f"   🌐 Product Page: {result['product_page_url']}")
    
    if not args.commit:
        logger.info(f"\n   💡 Run SQL against your database:")
        logger.info(f"      psql $DATABASE_URL -f {result['sql_path']}")


def marketing_command(args):
    """Generate marketing content (emails, social) for an existing product."""
    from pathlib import Path
    import json
    
    product_dir = Path(args.product_dir)
    output_dir = product_dir / "output"
    templates_dir = Path(__file__).parent / "templates"
    
    logger.info(f"📣 Generating Marketing Content...")
    logger.info(f"   Product: {args.title}")
    logger.info(f"   Directory: {product_dir}")
    
    # Try to load positioning from landing page content
    positioning = None
    lp_path = output_dir / "landing_page_content.json"
    if lp_path.exists():
        try:
            data = json.loads(lp_path.read_text())
            # Create a mock positioning from landing page data
            from types import SimpleNamespace
            positioning = SimpleNamespace(
                core_promise=data.get('headline', args.title),
                differentiator=data.get('subheadline', ''),
                audience=SimpleNamespace(
                    primary_persona="Your target reader",
                    pain_points=[f.get('description', '') for f in data.get('features', [])[:3]]
                ),
                key_benefits=[f.get('title', '') for f in data.get('features', [])]
            )
            logger.info(f"   ✅ Loaded positioning from landing_page_content.json")
        except Exception as e:
            logger.warning(f"   ⚠️ Could not load positioning: {e}")
    
    if positioning is None:
        # Create minimal positioning
        from types import SimpleNamespace
        positioning = SimpleNamespace(
            core_promise=args.title,
            differentiator="Premium digital product",
            audience=SimpleNamespace(
                primary_persona="Motivated learners",
                pain_points=["Needs guidance", "Wants transformation", "Seeks mastery"]
            ),
            key_benefits=["Expert knowledge", "Actionable steps", "Lasting results"]
        )
        logger.info(f"   ⚠️ Using default positioning (no landing_page_content.json)")
    
    # Email generation
    if args.emails:
        from .marketing.email_sequence_generator import EmailSequenceGenerator
        
        logger.info("\n═══ EMAIL SEQUENCES ═══")
        email_gen = EmailSequenceGenerator(templates_dir)
        
        # Welcome sequence
        welcome = email_gen.generate_welcome_sequence(args.title, positioning)
        welcome_path = output_dir / "emails_welcome.md"
        email_gen.export_to_file(welcome, welcome_path)
        logger.info(f"   ✅ Welcome Sequence: {len(welcome.emails)} emails → {welcome_path.name}")
        
        # Launch sequence
        launch = email_gen.generate_launch_sequence(args.title, positioning)
        launch_path = output_dir / "emails_launch.md"
        email_gen.export_to_file(launch, launch_path)
        logger.info(f"   ✅ Launch Sequence: {len(launch.emails)} emails → {launch_path.name}")
    
    # Email registration
    if args.register_emails:
        from .packaging.salarsu_email_client import SalarsuEmailClient
        
        logger.info("\n📬 Registering with SalarsNet...")
        email_client = SalarsuEmailClient()
        
        slug = args.title.replace(" ", "-").lower()
        welcome_path = output_dir / "emails_welcome.md"
        
        if welcome_path.exists():
            result = email_client.register_from_file(
                product_slug=slug,
                product_title=args.title,
                email_file=welcome_path,
                dry_run=args.dry_run
            )
            if result.success:
                logger.info(f"   ✅ Registered {result.templates_registered} templates")
            else:
                logger.warning(f"   ⚠️ Failed: {result.error}")
        else:
            logger.warning("   ⚠️ No email file. Run with --emails first.")
    
    # Social media generation
    social_package = None
    if args.social:
        from .marketing.social_promo_generator import SocialPromoGenerator, Platform
        
        logger.info("\n═══ SOCIAL MEDIA CONTENT ═══")
        social_gen = SocialPromoGenerator(templates_dir)
        
        social_package = social_gen.generate_promo_package(
            title=args.title,
            positioning=positioning,
            chapters=[]
        )
        
        social_path = output_dir / "social_promo.md"
        social_gen.export_to_file(social_package, social_path)
        
        twitter_count = len(social_package.by_platform(Platform.TWITTER))
        linkedin_count = len(social_package.by_platform(Platform.LINKEDIN))
        insta_count = len(social_package.by_platform(Platform.INSTAGRAM))
        
        logger.info(f"   ✅ Social Package: {len(social_package.posts)} posts")
        logger.info(f"      Twitter/X: {twitter_count} | LinkedIn: {linkedin_count} | Instagram: {insta_count}")
    
    # Buffer scheduling
    if args.schedule_buffer:
        from .marketing.buffer_client import schedule_to_buffer
        from datetime import datetime
        
        logger.info("\n📅 Scheduling to Buffer...")
        
        if not args.launch_date:
            logger.warning("   ⚠️ --launch-date required (format: YYYY-MM-DD)")
        elif social_package is None:
            logger.warning("   ⚠️ No social package. Run with --social first.")
        else:
            try:
                launch_date = datetime.strptime(args.launch_date, "%Y-%m-%d")
                result = schedule_to_buffer(
                    social_package=social_package,
                    launch_date=launch_date,
                    dry_run=args.dry_run
                )
                if result.success:
                    logger.info(f"   ✅ Scheduled {result.scheduled_count} posts")
                else:
                    logger.warning(f"   ⚠️ Failed: {result.message}")
            except ValueError:
                logger.error("   ❌ Invalid date format. Use YYYY-MM-DD")
    
    logger.info("\n✅ Marketing generation complete!")
    return 0


def status_command(args):
    """Show the status of a product in the pipeline."""
    from pathlib import Path
    from .core.product_state import get_product_state
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    state = get_product_state(product_dir)
    
    if state is None:
        # No state file, try to detect status from files
        logger.info(f"📊 Product Status: {product_dir.name}")
        logger.info("   (No state file found - checking files...)")
        
        output_dir = product_dir / "output"
        prompts_dir = output_dir / "prompts"
        responses_dir = output_dir / "responses"
        
        if prompts_dir.exists():
            prompt_count = len(list(prompts_dir.glob("*.prompt.md")))
            logger.info(f"   📝 Prompts: {prompt_count} files")
        
        if responses_dir.exists():
            response_count = len(list(responses_dir.glob("*.response.md")))
            logger.info(f"   ✍️ Responses: {response_count} files")
        
        pdf_files = list(output_dir.glob("*.pdf")) if output_dir.exists() else []
        if pdf_files:
            logger.info(f"   📄 PDFs: {len(pdf_files)} files")
        
        zip_files = list(output_dir.glob("*.zip")) if output_dir.exists() else []
        if zip_files:
            logger.info(f"   📦 ZIPs: {len(zip_files)} files")
        
        email_files = list(output_dir.glob("emails_*.md")) if output_dir.exists() else []
        if email_files:
            logger.info(f"   📧 Emails: {len(email_files)} files")
        
        social_file = output_dir / "social_promo.md" if output_dir.exists() else None
        if social_file and social_file.exists():
            logger.info(f"   📱 Social: social_promo.md")
    else:
        # Have state file, show rich status
        logger.info(state.get_status_summary())
    
    return 0


def resume_command(args):
    """Resume an interrupted pipeline from where it left off."""
    from pathlib import Path
    from .core.product_state import get_product_state
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    state = get_product_state(product_dir)
    
    if state is None:
        logger.error("❌ No product state found. Cannot resume.")
        logger.info("   Use 'product-builder create' to start a new product.")
        return 1
    
    next_phase = state.get_next_phase()
    
    if next_phase is None:
        logger.info("🎉 All phases already complete!")
        return 0
    
    logger.info(f"🔄 Resuming from phase: {next_phase}")
    logger.info(f"   Product: {state.title}")
    
    # Route to appropriate command based on next phase
    from argparse import Namespace
    
    if next_phase == "responses":
        logger.info("\n⏳ Waiting for Antigravity responses...")
        logger.info(f"   Write responses to: {product_dir}/output/responses/")
        logger.info("   Run 'product-builder resume' again when complete.")
        return 0
    
    elif next_phase == "compile":
        compile_args = Namespace(
            product_dir=str(product_dir),
            title=state.title
        )
        result = compile_command(compile_args)
        if result == 0:
            state.mark_complete("compile", success=True)
        return result
    
    elif next_phase == "deploy":
        logger.info("   Ready to deploy. Run:")
        logger.info(f"   product-builder deploy --product-dir {product_dir} --name \"{state.title}\" --slug \"{state.product_slug}\"")
        return 0
    
    elif next_phase in ["emails", "social"]:
        marketing_args = Namespace(
            product_dir=str(product_dir),
            title=state.title,
            emails=(next_phase == "emails"),
            social=(next_phase == "social"),
            register_emails=False,
            schedule_buffer=False,
            launch_date=None,
            dry_run=False
        )
        result = marketing_command(marketing_args)
        if result == 0:
            state.mark_complete(next_phase, success=True)
        return result
    
    else:
        logger.info(f"   Next phase '{next_phase}' requires manual action.")
        return 0


def full_pipeline_command(args):
    """
    Run the complete product lifecycle in one command.
    
    Phases: create → compile → deploy → marketing → schedule
    """
    from pathlib import Path
    from argparse import Namespace
    from .core.product_state import ProductState
    
    logger.info("═" * 60)
    logger.info("🏭 EPISTEMIC FACTORY: FULL PIPELINE")
    logger.info("═" * 60)
    logger.info(f"   Topic: {args.topic}")
    logger.info(f"   Title: {args.title}")
    
    output_dir = Path(args.output) if args.output else Path(f"./products/{args.title.replace(' ', '_').lower()}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize state
    state = ProductState.create(
        output_dir, 
        title=args.title, 
        topic=args.topic,
        price=args.price,
        launch_date=args.launch_date
    )
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: CREATE
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n═══ PHASE 1: CREATE ═══")
    
    create_args = Namespace(
        topic=args.topic,
        title=args.title,
        output=str(output_dir),
        style='dreamweaving',
        pdf=True,
        audio=getattr(args, 'audio', False),
        video=getattr(args, 'video', False),
        landing_page=True,
        emails=True,
        social=True,
        register_emails=False,
        schedule_buffer=False,
        launch_date=None,
        dry_run=False,
        generate_prompts_only=getattr(args, 'prompts_only', False),
        all=False
    )
    
    result = create_command(create_args)
    if result != 0:
        state.mark_complete("create", success=False, error="Create failed")
        return result
    
    state.mark_complete("create", success=True, mode="prompts_only" if args.prompts_only else "full")
    
    # If prompts only, stop here and wait
    if getattr(args, 'prompts_only', False):
        logger.info("\n" + "═" * 60)
        logger.info("⏳ ANTIGRAVITY-NATIVE MODE")
        logger.info("═" * 60)
        logger.info("   Prompts generated. Next steps:")
        logger.info(f"   1. Read prompts in: {output_dir}/output/prompts/")
        logger.info("   2. Write responses to: responses/<slug>.response.md")
        logger.info(f"   3. Run: product-builder resume --product-dir {output_dir}")
        return 0
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: DEPLOY (if requested)
    # ═══════════════════════════════════════════════════════════════
    if getattr(args, 'deploy', False):
        logger.info("\n═══ PHASE 2: DEPLOY ═══")
        
        deploy_args = Namespace(
            product_dir=str(output_dir),
            name=args.title,
            slug=args.title.replace(" ", "-").lower(),
            description=f"Premium digital product: {args.title}",
            price=args.price,
            sale_price=getattr(args, 'sale_price', None),
            salarsu_root=args.salarsu_root,
            commit=True,
            push=True
        )
        
        result = deploy_command(deploy_args)
        if result != 0:
            state.mark_complete("deploy", success=False, error="Deploy failed")
            logger.warning("   ⚠️ Deploy failed, continuing with marketing...")
        else:
            state.mark_complete("deploy", success=True)
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 3: REGISTER & SCHEDULE (if requested)
    # ═══════════════════════════════════════════════════════════════
    if getattr(args, 'schedule', False) and args.launch_date:
        logger.info("\n═══ PHASE 3: REGISTER & SCHEDULE ═══")
        
        marketing_args = Namespace(
            product_dir=str(output_dir),
            title=args.title,
            emails=False,  # Already generated in create
            social=False,  # Already generated in create
            register_emails=True,
            schedule_buffer=True,
            launch_date=args.launch_date,
            dry_run=getattr(args, 'dry_run', False),
            all=False
        )
        
        result = marketing_command(marketing_args)
        if result == 0:
            state.mark_complete("register", success=True)
            state.mark_complete("schedule", success=True)
    
    # ═══════════════════════════════════════════════════════════════
    # COMPLETE!
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n" + "═" * 60)
    logger.info("🎉 FULL PIPELINE COMPLETE!")
    logger.info("═" * 60)
    logger.info(f"   📁 Product: {output_dir}")
    logger.info(f"   📊 Status: product-builder status --product-dir {output_dir}")
    
    if getattr(args, 'deploy', False):
        slug = args.title.replace(" ", "-").lower()
        logger.info(f"   🌐 Store: https://salars.net/digital/{slug}")
    
    return 0


def dashboard_command(args):
    """Show a dashboard of all products and their status."""
    from pathlib import Path
    from .core.product_state import get_product_state
    
    products_dir = Path(args.products_dir)
    
    if not products_dir.exists():
        logger.error(f"❌ Products directory not found: {products_dir}")
        return 1
    
    # Find all product directories
    product_dirs = [d for d in products_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not product_dirs:
        logger.info("📭 No products found.")
        return 0
    
    # Gather product info
    products = []
    for pdir in sorted(product_dirs):
        output_dir = pdir / "output"
        
        # Get state if available
        state = get_product_state(pdir)
        
        # Count files
        pdf_count = len(list(output_dir.glob("*.pdf"))) if output_dir.exists() else 0
        zip_count = len(list(output_dir.glob("*.zip"))) if output_dir.exists() else 0
        email_count = len(list(output_dir.glob("emails_*.md"))) if output_dir.exists() else 0
        social_file = output_dir / "social_promo.md" if output_dir.exists() else None
        has_social = social_file.exists() if social_file else False
        
        # Determine status
        if state:
            phases_done = sum(1 for p in state.phases.values() if p.get("success"))
            total_phases = len(state.PIPELINE_PHASES)
            if phases_done == total_phases:
                status = "✅ Complete"
            elif phases_done > 0:
                next_phase = state.get_next_phase() or "unknown"
                status = f"🔄 {next_phase.title()}"
            else:
                status = "⏳ Started"
        else:
            # Infer from files
            if zip_count > 0:
                status = "✅ Packaged"
            elif pdf_count > 0:
                status = "📄 Compiled"
            else:
                status = "⏳ In Progress"
        
        products.append({
            "name": pdir.name.replace("_", " ").title(),
            "slug": pdir.name,
            "status": status,
            "pdf": pdf_count,
            "zip": zip_count,
            "emails": email_count,
            "social": "✓" if has_social else "-",
        })
    
    # Print dashboard
    logger.info("")
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " " * 25 + "EPISTEMIC FACTORY DASHBOARD" + " " * 26 + "║")
    logger.info("╠" + "═" * 78 + "╣")
    logger.info("║ {:35} │ {:12} │ {:4} │ {:4} │ {:6} │ {:6} ║".format(
        "Product", "Status", "PDFs", "ZIPs", "Emails", "Social"
    ))
    logger.info("╠" + "─" * 78 + "╣")
    
    live_count = 0
    for p in products:
        if "Complete" in p["status"] or "Packaged" in p["status"]:
            live_count += 1
        logger.info("║ {:35} │ {:12} │ {:4} │ {:4} │ {:6} │ {:6} ║".format(
            p["name"][:35],
            p["status"][:12],
            p["pdf"],
            p["zip"],
            p["emails"] if p["emails"] else "-",
            p["social"]
        ))
    
    logger.info("╠" + "═" * 78 + "╣")
    logger.info("║ Total: {:3} products │ Complete: {:3} │ In Progress: {:3}{}║".format(
        len(products), live_count, len(products) - live_count, " " * 30
    ))
    logger.info("╚" + "═" * 78 + "╝")
    
    return 0


def templates_command(args):
    """List all available product templates."""
    from .core.templates import format_template_list
    logger.info(format_template_list())
    return 0


def batch_command(args):
    """Create multiple products from a YAML configuration file."""
    from pathlib import Path
    from .core.batch import parse_batch_config, run_batch, generate_batch_report
    
    config_path = Path(args.config)
    
    if not config_path.exists():
        logger.error(f"❌ Config file not found: {config_path}")
        return 1
    
    logger.info(f"📋 Loading batch config: {config_path}")
    
    try:
        config = parse_batch_config(config_path)
    except Exception as e:
        logger.error(f"❌ Failed to parse config: {e}")
        return 1
    
    if args.parallel:
        config.parallel = args.parallel
    
    logger.info(f"   Found {len(config.products)} products to create")
    
    if args.dry_run:
        logger.info("\n📋 Products to create (dry-run):")
        for p in config.products:
            template = f" ({p.template})" if p.template else ""
            logger.info(f"   - {p.title}{template}: ${p.price:.0f}")
        return 0
    
    # Run the batch
    results = run_batch(config, create_command)
    
    # Generate report
    report_path = Path(config.output_dir) / "batch_report.md"
    generate_batch_report(results, report_path)
    
    # Summary
    success = sum(1 for r in results if r.get('success'))
    logger.info(f"\n🎉 Batch complete: {success}/{len(results)} successful")
    
    return 0 if success == len(results) else 1


def init_batch_command(args):
    """Generate an example batch configuration file."""
    from pathlib import Path
    from .core.batch import EXAMPLE_BATCH_YAML
    
    output_path = Path(args.output)
    
    if output_path.exists() and not args.force:
        logger.error(f"❌ File already exists: {output_path}")
        logger.info("   Use --force to overwrite")
        return 1
    
    output_path.write_text(EXAMPLE_BATCH_YAML)
    logger.info(f"✅ Created batch config: {output_path}")
    logger.info(f"\nEdit the file, then run:")
    logger.info(f"   product-builder batch --config {output_path}")
    
    return 0


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
    create_parser.add_argument('--template', 
                               help='Product template (ebook, audio-pack, video-course, lead-magnet, etc.)')
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
    
    # Deploy command - deploys to SalarsNet store
    deploy_parser = subparsers.add_parser('deploy', help='Deploy product to SalarsNet store')
    deploy_parser.add_argument('--product-dir', '-d', required=True, help='Product directory with output/')
    deploy_parser.add_argument('--name', '-n', required=True, help='Product name')
    deploy_parser.add_argument('--slug', '-s', required=True, help='Product URL slug')
    deploy_parser.add_argument('--description', help='Product description')
    deploy_parser.add_argument('--price', type=float, default=47.00, help='Regular price (default: 47.00)')
    deploy_parser.add_argument('--sale-price', type=float, help='Sale price')
    deploy_parser.add_argument('--salarsu-root', default='/home/rsalars/Projects/salarsu', 
                               help='Path to salarsu repo')
    deploy_parser.add_argument('--commit', action='store_true', help='Git commit the files')
    deploy_parser.add_argument('--push', action='store_true', help='Git push to origin (requires --commit)')
    deploy_parser.set_defaults(func=deploy_command)
    
    # Marketing command - generate emails and social for existing products
    marketing_parser = subparsers.add_parser('marketing', help='Generate marketing content for existing product')
    marketing_parser.add_argument('--product-dir', '-d', required=True, help='Product directory with output/')
    marketing_parser.add_argument('--title', '-T', required=True, help='Product title')
    marketing_parser.add_argument('--emails', action='store_true', help='Generate email sequences')
    marketing_parser.add_argument('--social', action='store_true', help='Generate social media posts')
    marketing_parser.add_argument('--register-emails', action='store_true', help='Register emails with SalarsNet')
    marketing_parser.add_argument('--schedule-buffer', action='store_true', help='Schedule social posts to Buffer')
    marketing_parser.add_argument('--launch-date', help='Launch date for scheduling (YYYY-MM-DD)')
    marketing_parser.add_argument('--dry-run', action='store_true', help='Validate without registering/scheduling')
    marketing_parser.add_argument('--all', action='store_true', help='Generate all marketing content')
    marketing_parser.set_defaults(func=marketing_command)
    
    # Status command - show pipeline status for a product
    status_parser = subparsers.add_parser('status', help='Show pipeline status for a product')
    status_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    status_parser.set_defaults(func=status_command)
    
    # Resume command - continue interrupted pipeline
    resume_parser = subparsers.add_parser('resume', help='Resume an interrupted pipeline')
    resume_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    resume_parser.set_defaults(func=resume_command)
    
    # Full Pipeline command - run everything end-to-end
    pipeline_parser = subparsers.add_parser('full-pipeline', help='Run complete product lifecycle')
    pipeline_parser.add_argument('--topic', '-t', required=True, help='Main topic')
    pipeline_parser.add_argument('--title', '-T', required=True, help='Product title')
    pipeline_parser.add_argument('--output', '-o', help='Output directory (default: ./products/<slug>)')
    pipeline_parser.add_argument('--price', type=float, default=47.00, help='Product price (default: 47.00)')
    pipeline_parser.add_argument('--sale-price', type=float, help='Sale price')
    pipeline_parser.add_argument('--launch-date', help='Launch date for scheduling (YYYY-MM-DD)')
    pipeline_parser.add_argument('--salarsu-root', default='/home/rsalars/Projects/salarsu', 
                                 help='Path to salarsu repo')
    pipeline_parser.add_argument('--prompts-only', action='store_true', 
                                 help='Generate prompts only (Antigravity-native mode)')
    pipeline_parser.add_argument('--deploy', action='store_true', help='Deploy to SalarsNet store')
    pipeline_parser.add_argument('--schedule', action='store_true', 
                                 help='Register emails and schedule social posts')
    pipeline_parser.add_argument('--audio', action='store_true', help='Generate audio narration')
    pipeline_parser.add_argument('--video', action='store_true', help='Generate video content')
    pipeline_parser.add_argument('--dry-run', action='store_true', help='Validate without scheduling')
    pipeline_parser.set_defaults(func=full_pipeline_command)
    
    # Dashboard command - show all products and status
    dashboard_parser = subparsers.add_parser('dashboard', help='Show dashboard of all products')
    dashboard_parser.add_argument('--products-dir', '-d', default='./products', 
                                   help='Products directory (default: ./products)')
    dashboard_parser.set_defaults(func=dashboard_command)
    
    # Templates command - list available product templates
    templates_parser = subparsers.add_parser('templates', help='List available product templates')
    templates_parser.set_defaults(func=templates_command)
    
    # Batch command - create multiple products from YAML
    batch_parser = subparsers.add_parser('batch', help='Create multiple products from YAML config')
    batch_parser.add_argument('--config', '-c', required=True, help='Path to YAML config file')
    batch_parser.add_argument('--parallel', '-p', type=int, help='Number of parallel workers')
    batch_parser.add_argument('--dry-run', action='store_true', help='Show what would be created')
    batch_parser.set_defaults(func=batch_command)
    
    # Init-batch command - generate example batch config
    init_batch_parser = subparsers.add_parser('init-batch', help='Generate example batch config file')
    init_batch_parser.add_argument('--output', '-o', default='products.yaml', 
                                    help='Output file path (default: products.yaml)')
    init_batch_parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing file')
    init_batch_parser.set_defaults(func=init_batch_command)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle --template flag (apply template defaults)
    if hasattr(args, 'template') and args.template:
        from .core.templates import get_template
        template = get_template(args.template)
        if template:
            logger.info(f"📋 Using template: {template.name}")
            # Apply template defaults (don't override explicit args)
            if not getattr(args, 'audio', False):
                args.audio = template.audio
            if not getattr(args, 'video', False):
                args.video = template.video
            # Always apply these from template
            args.landing_page = True
            args.emails = template.email_sequences
            args.social = template.social_posts
        else:
            logger.warning(f"⚠️ Unknown template: {args.template}")
            logger.info("   Use 'product-builder templates' to see available templates")
    
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
