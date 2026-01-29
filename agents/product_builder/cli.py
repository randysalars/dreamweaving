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
    
    # ═══════════════════════════════════════════════════════════════
    # AUTO-POST TWITTER LAUNCH THREAD (if requested)
    # ═══════════════════════════════════════════════════════════════
    if getattr(args, 'post_twitter', False):
        logger.info("\n═══ AUTO-POST: TWITTER LAUNCH THREAD ═══")
        
        # Look for social posts JSON
        social_json = output_dir / "marketing" / "zapier_social_posts.json"
        if not social_json.exists():
            social_json = output_dir / "zapier_social_posts.json"
        
        if not social_json.exists():
            logger.warning("   ⚠️ No social media content found. Run 'marketing --social' first.")
        else:
            try:
                from .marketing.x_client import XClient
                
                client = XClient()
                
                if getattr(args, 'dry_run', False):
                    post_result = client.post_from_json(social_json, post_now=True, dry_run=True)
                    logger.info(f"   🧪 [DRY RUN] Would post {post_result.posted_count} tweets")
                else:
                    post_result = client.post_from_json(social_json, post_now=True, dry_run=False)
                    
                    if post_result.success:
                        logger.info(f"   ✅ Posted {post_result.posted_count} tweets!")
                        if post_result.tweet_ids:
                            first_tweet = post_result.tweet_ids[0]
                            logger.info(f"   🔗 View thread: https://twitter.com/i/status/{first_tweet}")
                    else:
                        logger.warning(f"   ⚠️ Some posts failed: {post_result.errors}")
                        
            except ImportError:
                logger.warning("   ⚠️ tweepy not installed. Run: pip install tweepy")
            except ValueError as e:
                logger.warning(f"   ⚠️ X API credentials missing: {e}")
            except Exception as e:
                logger.warning(f"   ⚠️ Twitter posting failed: {e}")


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
        
        # Auto-schedule Twitter post for 6 hours later
        if twitter_count > 0 and not getattr(args, 'no_schedule', False):
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
                from scheduled_twitter_poster import create_schedule_for_product
                
                schedule_time = create_schedule_for_product(product_dir, delay_hours=6)
                logger.info(f"   📅 Twitter auto-post scheduled for {schedule_time.strftime('%Y-%m-%d %H:%M')}")
            except Exception as e:
                logger.warning(f"   ⚠️ Could not schedule Twitter post: {e}")
    
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


def post_twitter_command(args):
    """
    Post Twitter launch thread for a product.
    
    This is a standalone command that can be run independently after:
    1. Marketing content has been generated (marketing --social)
    2. Product has been deployed to production (via Coolify)
    
    Usage:
        product-builder post-twitter --product-dir ./products/my-product
        product-builder post-twitter --product-dir ./products/my-product --dry-run
    """
    from pathlib import Path
    
    product_dir = Path(args.product_dir)
    output_dir = product_dir / "output"
    
    logger.info("🐦 TWITTER LAUNCH THREAD")
    logger.info("=" * 50)
    logger.info(f"   Product: {product_dir.name}")
    
    # Look for social posts JSON
    social_json = output_dir / "marketing" / "zapier_social_posts.json"
    if not social_json.exists():
        social_json = output_dir / "zapier_social_posts.json"
    
    if not social_json.exists():
        logger.error(f"❌ No social media content found!")
        logger.info(f"   Expected: {output_dir}/marketing/zapier_social_posts.json")
        logger.info(f"   Generate with: product-builder marketing --product-dir {product_dir} --social")
        return 1
    
    logger.info(f"   📄 Posts file: {social_json}")
    
    try:
        from .marketing.x_client import XClient
        
        # Initialize client (validates credentials)
        client = XClient()
        logger.info("   ✅ X API credentials loaded")
        
        # Load and preview posts
        import json
        with open(social_json) as f:
            all_posts = json.load(f)
        
        twitter_posts = [p for p in all_posts if p.get('platform') == 'twitter']
        logger.info(f"   📝 Found {len(twitter_posts)} Twitter posts")
        
        # Show preview
        for i, post in enumerate(twitter_posts[:3]):
            content = post.get('content', '')[:60]
            char_count = client.count_twitter_chars(post.get('content', ''))
            logger.info(f"      {i+1}. ({char_count} chars) {content}...")
        if len(twitter_posts) > 3:
            logger.info(f"      ... and {len(twitter_posts) - 3} more")
        
        if args.dry_run:
            logger.info(f"\n🧪 [DRY RUN] Validating posts...")
            result = client.post_from_json(social_json, post_now=True, dry_run=True)
            logger.info(f"   ✅ Would post {result.posted_count} tweets")
            logger.info(f"   All posts validated. Run without --dry-run to post for real.")
        else:
            logger.info(f"\n🚀 Posting to X/Twitter...")
            result = client.post_from_json(social_json, post_now=True, dry_run=False)
            
            if result.success:
                logger.info(f"\n✅ SUCCESS! Posted {result.posted_count} tweets")
                if result.tweet_ids:
                    first_tweet = result.tweet_ids[0]
                    logger.info(f"   🔗 View thread: https://twitter.com/i/status/{first_tweet}")
            else:
                logger.warning(f"\n⚠️ Partial success: {result.posted_count} posted, {result.failed_count} failed")
                if result.errors:
                    for error in result.errors[:3]:
                        logger.error(f"   ❌ {error}")
                return 1
        
        return 0
        
    except ImportError:
        logger.error("❌ tweepy not installed. Run: pip install tweepy")
        return 1
    except ValueError as e:
        logger.error(f"❌ X API credentials missing: {e}")
        logger.info("   Set these in your .env file:")
        logger.info("   X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET")
        return 1
    except Exception as e:
        logger.error(f"❌ Twitter posting failed: {e}")
        return 1


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


def doctor_command(args):
    """Run health checks and diagnose environment issues."""
    from .core.setup import run_doctor
    
    logger.info("🔍 Running health checks...")
    report = run_doctor()
    logger.info(report.format())
    
    if report.failures > 0:
        logger.info("\n💡 Run the fix commands above to resolve issues.")
        return 1
    elif report.warnings > 0:
        logger.info("\n💡 Warnings are optional but recommended to fix.")
        return 0
    else:
        logger.info("\n✨ Everything looks great! You're ready to create products.")
        return 0


def init_command(args):
    """Initialize a new product project with scaffolding."""
    from pathlib import Path
    from .core.setup import init_project
    
    output_dir = Path(args.output) if args.output else None
    
    success, project_path = init_project(
        name=args.name,
        template=getattr(args, 'template', None),
        output_dir=output_dir
    )
    
    if success:
        logger.info(f"✅ Created project: {project_path}")
        logger.info("")
        logger.info("📁 Project structure:")
        logger.info(f"   {project_path}/")
        logger.info(f"   ├── project.json")
        logger.info(f"   ├── README.md")
        logger.info(f"   ├── assets/")
        logger.info(f"   └── output/")
        logger.info(f"       ├── prompts/")
        logger.info(f"       ├── responses/")
        logger.info(f"       ├── visuals/")
        logger.info(f"       └── bonuses/")
        logger.info("")
        logger.info("📋 Next steps:")
        logger.info(f"   1. cd {project_path}")
        logger.info(f"   2. product-builder create --topic \"your topic\" --title \"{args.name}\" --generate-prompts-only")
        logger.info(f"   3. Read prompts in output/prompts/")
        logger.info(f"   4. Write responses to output/responses/")
        logger.info(f"   5. product-builder compile --product-dir . --title \"{args.name}\"")
        return 0
    else:
        logger.error(f"❌ Project already exists: {project_path}")
        logger.info("   Use --output to specify a different location")
        return 1


def env_command(args):
    """Generate environment template file."""
    from pathlib import Path
    from .core.setup import generate_env_template
    
    output_path = Path(args.output)
    
    if output_path.exists() and not args.force:
        logger.error(f"❌ File already exists: {output_path}")
        logger.info("   Use --force to overwrite")
        return 1
    
    generate_env_template(output_path)
    logger.info(f"✅ Created environment template: {output_path}")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info(f"   1. cp {output_path} .env")
    logger.info(f"   2. Fill in your API keys and paths")
    logger.info(f"   3. source .env (or add to your shell profile)")
    
    return 0


def wizard_command(args):
    """Interactive wizard to create a product specification."""
    from pathlib import Path
    from .core.antigravity import run_wizard, ProductSpec
    from .core.setup import init_project
    
    spec = run_wizard()
    
    if spec is None:
        return 1
    
    # Save spec and create project
    output_dir = Path(args.output) if args.output else None
    
    success, project_path = init_project(
        name=spec.title,
        template=None,
        output_dir=output_dir
    )
    
    if not success:
        logger.error(f"❌ Failed to create project (may already exist)")
        return 1
    
    # Save the product spec
    spec_path = project_path / "product_spec.json"
    import json
    spec_path.write_text(json.dumps(spec.to_dict(), indent=2))
    
    logger.info(f"\n✅ Product spec saved: {spec_path}")
    logger.info(f"\n📋 Next: Generate prompts with:")
    logger.info(f"   product-builder create \\")
    logger.info(f"     --topic \"{spec.topic}\" \\")
    logger.info(f"     --title \"{spec.title}\" \\")
    logger.info(f"     --output {project_path} \\")
    logger.info(f"     --generate-prompts-only")
    
    return 0


def responses_command(args):
    """Check the status of responses for prompts."""
    from pathlib import Path
    from .core.antigravity import check_responses, format_response_status
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    statuses = check_responses(product_dir)
    
    if not statuses:
        logger.info("📭 No prompts found in this product.")
        return 0
    
    logger.info(format_response_status(statuses))
    
    # Summary advice
    complete = sum(1 for s in statuses if s.status == "complete")
    pending = sum(1 for s in statuses if s.status == "pending")
    
    if pending == 0 and complete == len(statuses):
        logger.info("\n✨ All responses complete! Ready to compile:")
        logger.info(f"   product-builder compile --product-dir {product_dir} --title \"Your Title\"")
    elif pending > 0:
        logger.info(f"\n📝 {pending} prompts still need responses.")
        logger.info(f"   Export prompts: product-builder export --product-dir {product_dir}")
    
    return 0


def preview_prompts_command(args):
    """Preview what prompts would be generated without creating files."""
    from .core.antigravity import preview_prompts, format_prompt_preview
    
    prompts = preview_prompts(
        topic=args.topic,
        title=args.title,
        template=getattr(args, 'template', None),
        chapter_count=args.chapters
    )
    
    logger.info(format_prompt_preview(prompts))
    
    logger.info(f"\n💡 To generate these prompts:")
    logger.info(f"   product-builder create \\")
    logger.info(f"     --topic \"{args.topic}\" \\")
    logger.info(f"     --title \"{args.title}\" \\")
    logger.info(f"     --generate-prompts-only")
    
    return 0


def export_command(args):
    """Export all prompts in a format ready for Antigravity."""
    from pathlib import Path
    from .core.antigravity import generate_antigravity_export
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    export_content = generate_antigravity_export(product_dir)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(export_content)
        logger.info(f"✅ Exported prompts to: {output_path}")
    else:
        # Print to stdout for easy copy
        print(export_content)
    
    return 0


def next_prompt_command(args):
    """Show the next prompt that needs a response."""
    from pathlib import Path
    from .core.antigravity import get_next_prompt, format_next_prompt
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    result = get_next_prompt(product_dir)
    
    if result is None:
        logger.info("🎉 All prompts have responses! Ready to compile:")
        logger.info(f"   product-builder compile --product-dir {product_dir} --title \"Your Title\"")
        return 0
    
    print(format_next_prompt(result))
    
    if args.copy:
        # Try to copy prompt to clipboard
        try:
            import subprocess
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                        stdin=subprocess.PIPE)
            process.communicate(result.prompt_content.encode())
            logger.info("📋 Prompt copied to clipboard!")
        except Exception:
            logger.info("💡 Tip: Install xclip to enable --copy functionality")
    
    return 0


def validate_command(args):
    """Validate a response file for quality."""
    from pathlib import Path
    from .core.antigravity import validate_response, format_validation_result
    
    response_path = Path(args.file)
    
    if not response_path.exists():
        logger.error(f"❌ File not found: {response_path}")
        return 1
    
    result = validate_response(response_path, min_words=args.min_words)
    logger.info(format_validation_result(result, response_path.name))
    
    return 0 if result.is_valid else 1


def validate_all_command(args):
    """Validate all responses in a product."""
    from pathlib import Path
    from .core.antigravity import validate_response, ValidationResult
    
    product_dir = Path(args.product_dir)
    responses_dir = product_dir / "output" / "responses"
    
    if not responses_dir.exists():
        logger.error(f"❌ No responses directory found: {responses_dir}")
        return 1
    
    response_files = sorted(responses_dir.glob("*.response.md"))
    
    if not response_files:
        logger.info("📭 No response files found.")
        return 0
    
    valid_count = 0
    invalid_count = 0
    total_words = 0
    
    logger.info("\n" + "═" * 68)
    logger.info("                    VALIDATING ALL RESPONSES")
    logger.info("═" * 68 + "\n")
    
    for response_file in response_files:
        result = validate_response(response_file, min_words=args.min_words)
        total_words += result.word_count
        
        status = "✅" if result.is_valid else "❌"
        issues = f"({len(result.issues)} issues)" if result.issues else ""
        logger.info(f"  {status} {response_file.name[:40]:40} {result.word_count:,} words {issues}")
        
        if result.is_valid:
            valid_count += 1
        else:
            invalid_count += 1
    
    logger.info("\n" + "═" * 68)
    logger.info(f"  Valid: {valid_count}  |  Invalid: {invalid_count}  |  Total words: {total_words:,}")
    logger.info("═" * 68)
    
    if invalid_count == 0:
        logger.info("\n✨ All responses valid! Ready to compile.")
    else:
        logger.info(f"\n⚠️ {invalid_count} responses need attention.")
    
    return 0 if invalid_count == 0 else 1


def import_command(args):
    """Import a response from a file."""
    from pathlib import Path
    from .core.antigravity import import_response
    
    product_dir = Path(args.product_dir)
    source_file = Path(args.source) if args.source else None
    
    success, message = import_response(
        product_dir=product_dir,
        prompt_slug=args.slug,
        source_file=source_file,
    )
    
    if success:
        logger.info(f"✅ {message}")
        return 0
    else:
        logger.error(f"❌ {message}")
        return 1


def scaffold_command(args):
    """Create a response template for a prompt."""
    from pathlib import Path
    from .core.antigravity import generate_response_template
    
    product_dir = Path(args.product_dir)
    prompts_dir = product_dir / "output" / "prompts"
    responses_dir = product_dir / "output" / "responses"
    
    # Find the prompt file
    prompt_file = prompts_dir / f"{args.slug}.prompt.md"
    
    if not prompt_file.exists():
        logger.error(f"❌ Prompt not found: {prompt_file}")
        logger.info(f"   Available prompts:")
        for pf in sorted(prompts_dir.glob("*.prompt.md")):
            slug = pf.stem.replace(".prompt", "")
            logger.info(f"   - {slug}")
        return 1
    
    # Generate template
    template = generate_response_template(prompt_file)
    
    # Save to responses directory
    responses_dir.mkdir(parents=True, exist_ok=True)
    response_file = responses_dir / f"{args.slug}.response.md"
    
    if response_file.exists() and not args.force:
        logger.error(f"❌ Response file already exists: {response_file}")
        logger.info("   Use --force to overwrite")
        return 1
    
    response_file.write_text(template)
    logger.info(f"✅ Created response template: {response_file}")
    logger.info("")
    logger.info("📝 Next steps:")
    logger.info(f"   1. Open {response_file}")
    logger.info("   2. Replace [placeholder] text with your content")
    logger.info("   3. Run: product-builder validate --file {response_file}")
    
    return 0


def list_bonuses_command(args):
    """List all available bonus types."""
    from .core.antigravity import list_bonus_types
    
    logger.info(list_bonus_types())
    return 0


def bonus_prompts_command(args):
    """Generate prompts for bonus content (Antigravity-native)."""
    from pathlib import Path
    from .core.antigravity import generate_bonus_prompts, BONUS_TYPES
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    # Parse bonus types
    if args.types == "all":
        bonus_types = list(BONUS_TYPES.keys())
    else:
        bonus_types = [t.strip() for t in args.types.split(",")]
    
    # Validate types
    invalid_types = [t for t in bonus_types if t not in BONUS_TYPES]
    if invalid_types:
        logger.error(f"❌ Unknown bonus types: {', '.join(invalid_types)}")
        logger.info(f"   Available: {', '.join(BONUS_TYPES.keys())}")
        return 1
    
    created_prompts = generate_bonus_prompts(
        product_dir=product_dir,
        bonus_types=bonus_types,
        product_title=args.title
    )
    
    logger.info(f"\n✅ Generated {len(created_prompts)} bonus prompts!")
    for prompt_file in created_prompts:
        logger.info(f"   📝 {prompt_file.name}")
    
    logger.info(f"\n📋 Next steps:")
    logger.info(f"   1. Read prompts in: {product_dir}/output/prompts/")
    logger.info(f"   2. Write responses to: {product_dir}/output/responses/")
    logger.info(f"   3. Check status: product-builder responses --product-dir {product_dir}")
    
    return 0


def audio_prompts_command(args):
    """Generate prompts for audio sessions (Antigravity-native)."""
    from pathlib import Path
    from .core.antigravity import generate_audio_prompts
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    # Parse session topics if provided
    session_topics = None
    if args.topics:
        session_topics = [t.strip() for t in args.topics.split(",")]
    
    created_prompts = generate_audio_prompts(
        product_dir=product_dir,
        session_count=args.sessions,
        product_title=args.title,
        session_topics=session_topics
    )
    
    logger.info(f"\n✅ Generated {len(created_prompts)} audio prompts!")
    for prompt_file in created_prompts:
        logger.info(f"   🎤 {prompt_file.name}")
    
    logger.info(f"\n📋 Step 3b Workflow:")
    logger.info(f"   1. Read each prompt in: {product_dir}/output/prompts/audio_*.prompt.md")
    logger.info(f"   2. Write scripts to: {product_dir}/output/responses/audio_*.response.md")
    logger.info(f"   3. Check status: product-builder audio-status --product-dir {product_dir}")
    logger.info(f"   4. Generate audio: product-builder generate-audio --product-dir {product_dir} --all")
    
    return 0


def audio_status_command(args):
    """Show status of audio sessions."""
    from pathlib import Path
    from .core.antigravity import list_audio_sessions, format_audio_sessions
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    sessions = list_audio_sessions(product_dir)
    logger.info(format_audio_sessions(sessions))
    
    return 0


def next_audio_command(args):
    """Show the next audio session that needs work."""
    from pathlib import Path
    from .core.antigravity import get_next_audio_session
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    result = get_next_audio_session(product_dir)
    
    if result is None:
        logger.info("🎉 All audio sessions complete!")
        return 0
    
    session = result["session"]
    
    if result["type"] == "needs_script":
        logger.info(f"\n📝 Next: Write script for '{session['slug']}'")
        logger.info(f"\n   Prompt: {session['prompt_file']}")
        logger.info(f"   Save to: output/responses/{session['slug']}.response.md")
        
        # Show the prompt content
        if session['prompt_file'].exists():
            logger.info("\n" + "─" * 60)
            logger.info(session['prompt_file'].read_text()[:500] + "...")
            logger.info("─" * 60)
    
    elif result["type"] == "needs_audio":
        logger.info(f"\n🎵 Next: Generate audio for '{session['slug']}'")
        logger.info(f"\n   Script: {session['response_file']}")
        logger.info(f"   Words: {session.get('word_count', '?')}")
        logger.info(f"   ~{session.get('estimated_minutes', '?')} minutes")
        logger.info(f"\n   Generate: product-builder generate-audio --product-dir {product_dir} --session {session['slug']}")
    
    return 0


def generate_audio_command(args):
    """Generate audio from script using TTS."""
    from pathlib import Path
    from .core.antigravity import generate_audio_from_script, list_audio_sessions
    
    product_dir = Path(args.product_dir)
    audio_dir = product_dir / "output" / "audio"
    responses_dir = product_dir / "output" / "responses"
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    # Get sessions to process
    sessions = list_audio_sessions(product_dir)
    
    if args.all:
        # Generate all that have scripts but no audio
        to_generate = [s for s in sessions if s.get("has_script") and not s.get("has_audio")]
    elif args.session:
        # Generate specific session
        to_generate = [s for s in sessions if s["slug"] == args.session]
        if not to_generate:
            logger.error(f"❌ Session not found: {args.session}")
            return 1
    else:
        logger.error("❌ Specify --session <slug> or --all")
        return 1
    
    if not to_generate:
        logger.info("📭 No sessions ready for audio generation.")
        logger.info("   Scripts need to be written first.")
        return 0
    
    logger.info(f"\n🎵 Generating audio for {len(to_generate)} session(s)...")
    
    success_count = 0
    for session in to_generate:
        script_path = session["response_file"]
        output_path = audio_dir / f"{session['slug']}.mp3"
        
        logger.info(f"\n   Processing: {session['slug']}")
        logger.info(f"   Words: {session.get('word_count', '?')}")
        logger.info(f"   ~{session.get('estimated_minutes', '?')} minutes estimated")
        
        # Use XTTS-v2 if available and requested, else fallback
        if args.engine == "xtts":
            from .core.antigravity import generate_audio_xtts, get_xtts_status
            
            xtts_status = get_xtts_status()
            if not xtts_status["available"]:
                logger.error(f"   ❌ XTTS-v2 not available: {xtts_status['message']}")
                logger.info("   Use --engine piper or --engine espeak as fallback")
                continue
            
            logger.info(f"   🎤 Using XTTS-v2 with voice cloning...")
            
            voice_sample = Path(args.voice) if args.voice and args.voice != "en_US-amy-medium" else None
            
            def progress_callback(current, total, msg):
                if current % 20 == 0 or current == total:
                    logger.info(f"   📊 Progress: [{current}/{total}] {msg[:40]}...")
            
            success, message = generate_audio_xtts(
                script_path=script_path,
                output_path=output_path,
                voice_sample=voice_sample,
                speed=args.speed if hasattr(args, 'speed') else 0.88,
                progress_callback=progress_callback
            )
        else:
            success, message = generate_audio_from_script(
                script_path=script_path,
                output_path=output_path,
                voice=args.voice,
                engine=args.engine
            )
        
        if success:
            logger.info(f"   ✅ {message}")
            success_count += 1
        else:
            logger.error(f"   ❌ {message}")
    
    logger.info(f"\n📊 Generated {success_count}/{len(to_generate)} audio files")
    logger.info(f"   Output: {audio_dir}")
    
    return 0 if success_count == len(to_generate) else 1


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3B ENHANCEMENTS: TEMPLATES, VOICES, QUALITY
# ═══════════════════════════════════════════════════════════════════════════


def list_audio_templates_command(args):
    """List available audio generation templates/presets."""
    from .core.antigravity import list_audio_templates
    logger.info(list_audio_templates())
    return 0


def list_voices_command(args):
    """List available TTS voices."""
    from .core.antigravity import list_voices
    logger.info(list_voices())
    return 0


def audio_quality_command(args):
    """Analyze audio quality for a product."""
    from pathlib import Path
    from .core.antigravity import analyze_product_audio, format_audio_quality_report
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    reports, message = analyze_product_audio(product_dir)
    logger.info(f"\n📊 {message}")
    logger.info(format_audio_quality_report(reports))
    
    return 0


def preview_voice_command(args):
    """Preview a voice with sample text."""
    from pathlib import Path
    import subprocess
    import tempfile
    from .core.antigravity import get_voice_by_name, generate_audio_from_script
    
    voice = get_voice_by_name(args.voice)
    
    if not voice:
        logger.error(f"❌ Voice not found: {args.voice}")
        logger.info("   Run: product-builder list-voices")
        return 1
    
    text = args.text or "Welcome to your audio experience. This is a preview of the selected voice."
    
    # Create temp file for preview
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(text)
        script_path = Path(f.name)
    
    output_path = Path(tempfile.mktemp(suffix='.wav'))
    
    logger.info(f"\n🎤 Previewing voice: {voice.name} ({voice.engine})")
    logger.info(f"   Text: \"{text[:50]}...\"")
    
    if voice.engine == "xtts":
        from .core.antigravity import generate_audio_xtts
        success, message = generate_audio_xtts(script_path, output_path, voice.path)
    else:
        success, message = generate_audio_from_script(
            script_path, output_path,
            voice=voice.name,
            engine=voice.engine
        )
    
    if success:
        logger.info(f"   ✅ Preview saved: {output_path}")
        
        # Try to play audio if available
        import shutil
        if shutil.which("mpv"):
            subprocess.run(["mpv", "--no-video", str(output_path)], capture_output=True)
        elif shutil.which("aplay"):
            subprocess.run(["aplay", str(output_path)], capture_output=True)
    else:
        logger.error(f"   ❌ {message}")
    
    # Cleanup
    script_path.unlink(missing_ok=True)
    
    return 0 if success else 1


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3C: VIDEO GENERATION COMMANDS
# ═══════════════════════════════════════════════════════════════════════════



def list_video_templates_command(args):
    """List available video templates."""
    from .core.antigravity import list_video_templates
    logger.info(list_video_templates())
    return 0


def video_prompts_command(args):
    """Generate prompts for video sessions."""
    from pathlib import Path
    from .core.antigravity import generate_video_prompts
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    video_topics = None
    if args.topics:
        video_topics = [t.strip() for t in args.topics.split(",")]
    
    created_prompts = generate_video_prompts(
        product_dir=product_dir,
        video_count=args.videos,
        product_title=args.title,
        video_topics=video_topics,
        template=args.template
    )
    
    logger.info(f"\n✅ Generated {len(created_prompts)} video prompts!")
    for prompt_file in created_prompts:
        logger.info(f"   🎬 {prompt_file.name}")
    
    logger.info(f"\n📋 Step 3c Workflow:")
    logger.info(f"   1. Read prompts in: {product_dir}/output/prompts/video_*.prompt.md")
    logger.info(f"   2. Write scripts to: {product_dir}/output/responses/video_*.response.md")
    logger.info(f"   3. Check: product-builder video-status -d {product_dir}")
    logger.info(f"   4. Audio: product-builder generate-audio -d {product_dir} --all")
    logger.info(f"   5. Images: product-builder fetch-images -d {product_dir}")
    logger.info(f"   6. Render: product-builder render-video -d {product_dir} --all")
    
    return 0


def video_status_command(args):
    """Show status of video sessions."""
    from pathlib import Path
    from .core.antigravity import list_video_sessions, format_video_sessions
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    sessions = list_video_sessions(product_dir)
    logger.info(format_video_sessions(sessions))
    return 0


def next_video_command(args):
    """Show the next video session needing work."""
    from pathlib import Path
    from .core.antigravity import get_next_video_session
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    result = get_next_video_session(product_dir)
    
    if result is None:
        logger.info("🎉 All video sessions complete!")
        return 0
    
    session = result["session"]
    
    if result["type"] == "needs_script":
        logger.info(f"\n📝 Write script for '{session['slug']}'")
        logger.info(f"   Prompt: {session['prompt_file']}")
    elif result["type"] == "needs_audio":
        logger.info(f"\n🎵 Generate audio for '{session['slug']}'")
        logger.info(f"   Run: product-builder generate-audio -d {product_dir} --session {session['slug']}")
    elif result["type"] == "needs_render":
        logger.info(f"\n🎬 Render video for '{session['slug']}'")
        logger.info(f"   Run: product-builder render-video -d {product_dir} --session {session['slug']}")
    
    return 0


def fetch_images_command(args):
    """Fetch stock images for video production."""
    from pathlib import Path
    from .core.antigravity import fetch_stock_image, list_video_sessions
    import re
    
    product_dir = Path(args.product_dir)
    images_dir = product_dir / "output" / "images"
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    sessions = list_video_sessions(product_dir)
    search_terms = []
    
    for session in sessions:
        if session.get("response_file") and session["response_file"].exists():
            content = session["response_file"].read_text()
            matches = re.findall(r'Search:\s*\[([^\]]+)\]', content)
            for match in matches:
                search_terms.append({"term": match, "session": session["slug"]})
    
    if not search_terms:
        logger.info("📭 No image search terms found. Add 'Search: [term]' in scripts.")
        return 0
    
    logger.info(f"\n📷 Fetching {len(search_terms)} images...")
    success_count = 0
    
    for i, item in enumerate(search_terms, 1):
        output_path = images_dir / f"{item['session']}_{i:02d}.jpg"
        logger.info(f"   [{i}/{len(search_terms)}] {item['term'][:40]}...")
        
        success, _ = fetch_stock_image(item["term"], output_path, "unsplash")
        if success:
            success_count += 1
    
    logger.info(f"\n📊 Fetched {success_count}/{len(search_terms)} images → {images_dir}")
    return 0


def render_video_command(args):
    """Render video using Remotion."""
    from pathlib import Path
    from .core.antigravity import render_video_with_remotion, list_video_sessions, get_remotion_status
    
    product_dir = Path(args.product_dir)
    video_dir = product_dir / "output" / "video"
    images_dir = product_dir / "output" / "images"
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    remotion_status = get_remotion_status()
    if not remotion_status["available"]:
        logger.error(f"❌ Remotion not available: {remotion_status['message']}")
        return 1
    
    sessions = list_video_sessions(product_dir)
    
    if args.all:
        to_render = [s for s in sessions if s.get("has_audio") and not s.get("has_video")]
    elif args.session:
        to_render = [s for s in sessions if s["slug"] == args.session]
        if not to_render:
            logger.error(f"❌ Session not found: {args.session}")
            return 1
    else:
        logger.error("❌ Specify --session <slug> or --all")
        return 1
    
    if not to_render:
        logger.info("📭 No sessions ready for video rendering.")
        return 0
    
    logger.info(f"\n🎬 Rendering {len(to_render)} video(s) with Remotion...")
    success_count = 0
    
    for session in to_render:
        output_path = video_dir / f"{session['slug']}.mp4"
        logger.info(f"\n   Processing: {session['slug']}")
        
        success, message = render_video_with_remotion(
            script_path=session["response_file"],
            audio_path=session["audio_file"],
            output_path=output_path,
            composition=args.template,
            images_dir=images_dir if images_dir.exists() else None
        )
        
        if success:
            logger.info(f"   ✅ {message}")
            success_count += 1
        else:
            logger.error(f"   ❌ {message}")
    
    logger.info(f"\n📊 Rendered {success_count}/{len(to_render)} videos → {video_dir}")
    return 0 if success_count == len(to_render) else 1


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3C ENHANCEMENTS: STYLES, QUALITY, THUMBNAILS
# ═══════════════════════════════════════════════════════════════════════════


def list_video_styles_command(args):
    """List available video style presets."""
    from .core.antigravity import list_video_styles
    logger.info(list_video_styles())
    return 0


def video_quality_command(args):
    """Analyze video quality for a product."""
    from pathlib import Path
    from .core.antigravity import analyze_product_videos, format_video_quality_report
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    reports, message = analyze_product_videos(product_dir)
    logger.info(f"\n📊 {message}")
    logger.info(format_video_quality_report(reports))
    
    return 0


def list_thumbnail_sizes_command(args):
    """List thumbnail size presets."""
    from .core.antigravity import list_thumbnail_sizes
    logger.info(list_thumbnail_sizes())
    return 0


def generate_thumbnail_command(args):
    """Generate thumbnail from video."""
    from pathlib import Path
    from .core.antigravity import generate_video_thumbnail, generate_all_thumbnails
    
    if args.product_dir:
        # Batch mode: generate thumbnails for all videos
        product_dir = Path(args.product_dir)
        
        if not product_dir.exists():
            logger.error(f"❌ Product directory not found: {product_dir}")
            return 1
        
        success_count, results = generate_all_thumbnails(product_dir, args.size)
        
        logger.info(f"\n🖼️  Generated {success_count} thumbnails:")
        for result in results:
            logger.info(f"   {result}")
        
        return 0 if success_count > 0 else 1
    
    elif args.video:
        # Single video mode
        video_path = Path(args.video)
        
        if not video_path.exists():
            logger.error(f"❌ Video not found: {video_path}")
            return 1
        
        output_path = Path(args.output) if args.output else None
        
        success, message = generate_video_thumbnail(
            video_path,
            output_path,
            text_overlay=args.text,
            size_preset=args.size,
            timestamp=args.timestamp
        )
        
        if success:
            logger.info(f"✅ {message}")
            return 0
        else:
            logger.error(f"❌ {message}")
            return 1
    
    else:
        logger.error("❌ Specify --video or --product-dir")
        return 1


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3D: LANDING PAGE & STORE INTEGRATION COMMANDS
# ═══════════════════════════════════════════════════════════════════════════


def list_categories_command(args):
    """List available digital product categories."""
    from .core.antigravity import list_store_categories
    logger.info(list_store_categories())
    return 0


def landing_prompt_command(args):
    """Generate prompt for landing page content."""
    from pathlib import Path
    import json
    from .core.antigravity import generate_landing_page_prompt
    
    product_dir = Path(args.product_dir)
    config_file = product_dir / "product.json"
    
    if not config_file.exists():
        logger.error(f"❌ product.json not found in {product_dir}")
        return 1
    
    config = json.loads(config_file.read_text())
    
    prompt = generate_landing_page_prompt(
        product_title=config.get("title", product_dir.name),
        product_description=config.get("description", ""),
        category=config.get("category", "wealth"),
        target_price=float(config.get("price", 14.99))
    )
    
    prompts_dir = product_dir / "output" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = prompts_dir / "landing_page.prompt.md"
    prompt_file.write_text(prompt)
    
    logger.info(f"\n✅ Generated landing page prompt: {prompt_file}")
    logger.info(f"\n📋 Step 3d Workflow:")
    logger.info(f"   1. Read prompt: {prompt_file}")
    logger.info(f"   2. Write JSON to: output/responses/landing_page.response.md")
    logger.info(f"   3. Create cover image: output/images/cover.png")
    logger.info(f"   4. Check status: product-builder store-status -d {product_dir}")
    logger.info(f"   5. Generate SQL: product-builder generate-sql -d {product_dir}")
    logger.info(f"   6. Deploy: product-builder deploy-product -d {product_dir}")
    
    return 0


def image_prompt_command(args):
    """Generate prompt for product cover image."""
    from pathlib import Path
    import json
    from .core.antigravity import generate_product_image_prompt
    
    product_dir = Path(args.product_dir)
    config_file = product_dir / "product.json"
    
    if not config_file.exists():
        logger.error(f"❌ product.json not found in {product_dir}")
        return 1
    
    config = json.loads(config_file.read_text())
    
    prompt = generate_product_image_prompt(
        product_title=config.get("title", product_dir.name),
        category=config.get("category", "wealth"),
        style=args.style
    )
    
    prompts_dir = product_dir / "output" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = prompts_dir / "cover_image.prompt.md"
    prompt_file.write_text(prompt)
    
    logger.info(f"\n✅ Generated image prompt: {prompt_file}")
    logger.info(f"\n💡 Use this prompt with Antigravity's generate_image tool")
    logger.info(f"   Save result to: {product_dir}/output/images/cover.png")
    
    return 0


def store_status_command(args):
    """Show store integration status."""
    from pathlib import Path
    from .core.antigravity import get_store_integration_status, format_store_status
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    status = get_store_integration_status(product_dir)
    logger.info(format_store_status(status))
    
    return 0


def generate_sql_command(args):
    """Generate SQL for store integration."""
    from pathlib import Path
    from .core.antigravity import create_product_manifest, generate_store_sql
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    success, manifest = create_product_manifest(product_dir)
    
    if not success:
        logger.error(f"❌ Failed to create manifest: {manifest}")
        return 1
    
    sql = generate_store_sql(manifest)
    
    output_file = product_dir / "output" / "store_insert.sql"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(sql)
    
    logger.info(f"\n✅ Generated SQL: {output_file}")
    logger.info(f"\n📦 Product Manifest:")
    logger.info(f"   Name: {manifest.name}")
    logger.info(f"   Slug: {manifest.slug}")
    logger.info(f"   SKU: {manifest.sku}")
    logger.info(f"   Price: ${manifest.price:.2f}")
    logger.info(f"   Category: {manifest.category}")
    logger.info(f"   Download: {manifest.download_url}")
    
    return 0


def deploy_product_command(args):
    """Deploy product to SalarsNet store."""
    from pathlib import Path
    from .core.antigravity import (
        get_store_integration_status,
        copy_assets_for_deployment,
        create_product_manifest
    )
    
    product_dir = Path(args.product_dir)
    salarsu_path = Path(args.salarsu_path) if args.salarsu_path else Path.home() / "Projects/salarsu"
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    if not salarsu_path.exists():
        logger.error(f"❌ SalarsNet directory not found: {salarsu_path}")
        return 1
    
    # Check status
    status = get_store_integration_status(product_dir)
    
    if not status["ready_for_store"]:
        logger.error(f"❌ Product not ready for store. Missing: {', '.join(status['missing'])}")
        return 1
    
    # Copy assets
    success, actions = copy_assets_for_deployment(product_dir, salarsu_path)
    
    if not success:
        logger.error(f"❌ Failed to copy assets: {actions}")
        return 1
    
    logger.info(f"\n✅ Deployed product to SalarsNet!")
    for action in actions:
        logger.info(f"   📄 {action}")
    
    # Get manifest for final instructions
    _, manifest = create_product_manifest(product_dir)
    
    logger.info(f"\n📋 Next Steps:")
    logger.info(f"   1. Run SQL: psql -f db/seeds/digital_{manifest.slug}.sql")
    logger.info(f"   2. Verify: https://www.salars.net/digital/{manifest.slug}")
    logger.info(f"   3. Deploy: vercel --prod")
    
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3D ENHANCEMENTS: SEO, OG IMAGES, PREFLIGHT
# ═══════════════════════════════════════════════════════════════════════════


def generate_seo_command(args):
    """Generate SEO metadata for a product."""
    from pathlib import Path
    import json
    from .core.antigravity import (
        generate_seo_metadata, format_seo_metadata, export_seo_metadata
    )
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    # Load product info
    config_file = product_dir / "product.json"
    if not config_file.exists():
        logger.error(f"❌ product.json not found in {product_dir}")
        return 1
    
    config = json.loads(config_file.read_text())
    
    seo = generate_seo_metadata(
        product_title=config.get("title", product_dir.name),
        product_description=config.get("description", ""),
        category=config.get("category", "wealth"),
        slug=config.get("slug", product_dir.name),
        price=config.get("price", 0),
    )
    
    logger.info(format_seo_metadata(seo))
    
    # Export to files
    output_dir = product_dir / "output"
    success, message = export_seo_metadata(seo, output_dir)
    
    if success:
        logger.info(f"\n✅ {message}")
    else:
        logger.error(f"\n❌ {message}")
    
    return 0


def list_og_styles_command(args):
    """List OG image style presets."""
    from .core.antigravity import list_og_styles
    logger.info(list_og_styles())
    return 0


def generate_og_command(args):
    """Generate OG images for a product."""
    from pathlib import Path
    from .core.antigravity import generate_product_og_images, generate_og_image
    
    if args.product_dir:
        # Batch mode
        product_dir = Path(args.product_dir)
        
        if not product_dir.exists():
            logger.error(f"❌ Product directory not found: {product_dir}")
            return 1
        
        success_count, results = generate_product_og_images(product_dir)
        
        logger.info(f"\n🖼️  Generated {success_count} OG images:")
        for result in results:
            logger.info(f"   {result}")
        
        return 0 if success_count > 0 else 1
    
    elif args.title:
        # Single image mode
        from pathlib import Path
        output_path = Path(args.output) if args.output else Path(f"og_{args.style}.png")
        
        success, message = generate_og_image(
            title=args.title,
            output_path=output_path,
            subtitle=args.subtitle,
            price=args.price,
            style=args.style,
            sale_badge=args.sale
        )
        
        if success:
            logger.info(f"✅ {message}")
            return 0
        else:
            logger.error(f"❌ {message}")
            return 1
    
    else:
        logger.error("❌ Specify --product-dir or --title")
        return 1


def preflight_check_command(args):
    """Run preflight checks before deployment."""
    from pathlib import Path
    from .core.antigravity import run_preflight_checks, format_preflight_results
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    checks = run_preflight_checks(product_dir)
    logger.info(format_preflight_results(checks))
    
    # Return error if any critical failures
    critical_failures = [c for c in checks if not c.passed and c.severity == "error"]
    return 1 if critical_failures else 0


# ═══════════════════════════════════════════════════════════════════════════
# STEP 4 ENHANCEMENTS: COMPILE STATS, VERIFY, TOC
# ═══════════════════════════════════════════════════════════════════════════


def compile_stats_command(args):
    """Show compilation statistics for a product."""
    from pathlib import Path
    from .core.antigravity import (
        analyze_compiled_content, format_compilation_stats
    )
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    stats = analyze_compiled_content(product_dir)
    
    if stats:
        logger.info(format_compilation_stats(stats))
        return 0
    else:
        logger.error("❌ No compiled content found. Run 'compile' first.")
        return 1


def compile_verify_command(args):
    """Verify compilation integrity."""
    from pathlib import Path
    from .core.antigravity import (
        verify_compilation, format_compile_verification
    )
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    checks = verify_compilation(product_dir)
    logger.info(format_compile_verification(checks))
    
    # Return error if critical failures
    critical = [c for c in checks if not c.passed and c.severity == "error"]
    return 1 if critical else 0


def generate_toc_command(args):
    """Generate table of contents for a product."""
    from pathlib import Path
    import json
    from .core.antigravity import (
        extract_toc_from_responses, format_toc, save_toc_to_file
    )
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    # Get product title
    config_file = product_dir / "product.json"
    if config_file.exists():
        config = json.loads(config_file.read_text())
        title = config.get("title", "Product")
    else:
        title = args.title or "Product"
    
    entries = extract_toc_from_responses(product_dir)
    
    if not entries:
        logger.error("❌ No chapters found. Generate responses first.")
        return 1
    
    logger.info(format_toc(entries, include_sections=not args.chapters_only))
    
    if args.save:
        success, message = save_toc_to_file(product_dir, entries, title)
        if success:
            logger.info(f"\n✅ {message}")
        else:
            logger.error(f"\n❌ {message}")
    
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# STEP 5 ENHANCEMENTS: DRY-RUN, VERIFY, HISTORY
# ═══════════════════════════════════════════════════════════════════════════


def deploy_dry_run_command(args):
    """Preview deployment without making changes."""
    from pathlib import Path
    from .core.antigravity import dry_run_deploy, format_dry_run
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    salarsu_path = Path(args.salarsu_path) if args.salarsu_path else None
    
    success, dry_run = dry_run_deploy(product_dir, salarsu_path)
    
    if success:
        logger.info(format_dry_run(dry_run))
        return 0
    else:
        logger.error("❌ Could not generate dry-run preview. Check product.json exists.")
        return 1


def deploy_verify_command(args):
    """Verify deployment was successful."""
    from pathlib import Path
    from .core.antigravity import (
        verify_deployment, format_deploy_verification
    )
    
    salarsu_path = Path(args.salarsu_path) if args.salarsu_path else None
    
    checks = verify_deployment(args.slug, salarsu_path)
    logger.info(format_deploy_verification(checks))
    
    # Return error if critical failures
    critical = [c for c in checks if not c.passed and c.severity == "error"]
    return 1 if critical else 0


def deploy_history_command(args):
    """Show deployment history for a product."""
    from pathlib import Path
    from .core.antigravity import (
        load_deployment_history, format_deployment_history
    )
    
    salarsu_path = Path(args.salarsu_path) if args.salarsu_path else None
    
    records = load_deployment_history(args.slug, salarsu_path)
    logger.info(format_deployment_history(records))
    
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# STEP 6 ENHANCEMENTS: TEMPLATES, UTM, PREVIEW
# ═══════════════════════════════════════════════════════════════════════════


def list_marketing_templates_command(args):
    """List available marketing templates."""
    from .core.antigravity import format_marketing_templates
    
    logger.info(format_marketing_templates())
    return 0


def generate_utm_command(args):
    """Generate UTM links for a product."""
    from pathlib import Path
    from .core.antigravity import (
        generate_utm_links, format_utm_links, export_utm_links
    )
    
    links = generate_utm_links(
        slug=args.slug,
        campaign=args.campaign
    )
    
    logger.info(format_utm_links(links))
    
    if args.save:
        output_dir = Path(args.output) if args.output else Path.cwd()
        success, message = export_utm_links(links, output_dir)
        if success:
            logger.info(f"\n✅ {message}")
        else:
            logger.error(f"\n❌ {message}")
    
    return 0


def marketing_preview_command(args):
    """Preview and validate marketing content."""
    from pathlib import Path
    from .core.antigravity import (
        preview_marketing_content, format_content_preview
    )
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    preview = preview_marketing_content(product_dir)
    
    if preview:
        logger.info(format_content_preview(preview))
        
        # Return error if issues found
        failed = [c for c in preview.checks if not c.passed]
        return 1 if failed else 0
    else:
        logger.error("❌ No marketing content found. Generate with 'marketing --emails --social' first.")
        return 1


# ═══════════════════════════════════════════════════════════════════════════
# STEP 7 ENHANCEMENTS: SCHEDULE PREVIEW, REGISTRATION STATUS, COUNTDOWN
# ═══════════════════════════════════════════════════════════════════════════


def schedule_preview_command(args):
    """Preview scheduled posts before committing."""
    from pathlib import Path
    from .core.antigravity import (
        generate_schedule_preview, format_schedule_preview
    )
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    preview = generate_schedule_preview(
        product_dir,
        args.launch_date,
        posts_per_day=args.posts_per_day,
        duration_days=args.duration
    )
    
    if preview:
        logger.info(format_schedule_preview(preview))
        return 0
    else:
        logger.error("❌ No social content found. Generate with 'marketing --social' first.")
        return 1


def registration_status_command(args):
    """Check registration status for emails and social."""
    from pathlib import Path
    from .core.antigravity import (
        check_registration_status, format_registration_status
    )
    
    salarsu_path = Path(args.salarsu_path) if args.salarsu_path else None
    
    status = check_registration_status(args.slug, salarsu_path)
    logger.info(format_registration_status(status))
    
    return 0


def launch_countdown_command(args):
    """Show launch countdown with checklist."""
    from pathlib import Path
    from .core.antigravity import (
        generate_launch_countdown, format_launch_countdown
    )
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    countdown = generate_launch_countdown(product_dir, args.launch_date)
    
    if countdown:
        logger.info(format_launch_countdown(countdown))
        return 1 if countdown.ready_percentage < 70 else 0
    else:
        logger.error("❌ Product output not found.")
        return 1


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE AUTOMATION: AUTO-LAUNCH, PRESETS
# ═══════════════════════════════════════════════════════════════════════════


def list_presets_command(args):
    """List available pipeline presets."""
    from .core.antigravity import format_pipeline_presets
    
    logger.info(format_pipeline_presets())
    return 0


def auto_launch_command(args):
    """
    Complete product from topic to live in one command.
    
    Runs: create → audio → video → seo → deploy → marketing → schedule
    """
    from pathlib import Path
    from argparse import Namespace
    from .core.antigravity import (
        get_pipeline_preset, create_pipeline_progress, format_progress_bar,
        verify_create_phase, verify_deploy_phase, format_phase_verification,
        generate_pipeline_summary, format_pipeline_summary
    )
    from .core.product_state import ProductState
    
    # Apply preset if provided
    preset = None
    if args.preset:
        preset = get_pipeline_preset(args.preset)
        if not preset:
            logger.error(f"❌ Unknown preset: {args.preset}")
            logger.info("   Use 'product-builder list-presets' to see available presets")
            return 1
        logger.info(f"📋 Using preset: {preset.name}")
    
    # Determine settings (preset -> args -> defaults)
    audio = getattr(args, 'audio', False) or (preset and preset.audio) or False
    video = getattr(args, 'video', False) or (preset and preset.video) or False
    deploy = getattr(args, 'deploy', False) or (preset and preset.deploy) or False
    schedule = getattr(args, 'schedule', False) or (preset and preset.schedule) or False
    price = args.price or (preset and preset.price) or 47.00
    sale_price = getattr(args, 'sale_price', None) or (preset and preset.sale_price)
    
    slug = args.title.replace(" ", "-").lower()
    output_dir = Path(args.output) if args.output else Path(f"./products/{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build phase list
    enabled_phases = ["create"]
    if audio:
        enabled_phases.append("audio")
    if video:
        enabled_phases.append("video")
    enabled_phases.append("seo")
    if deploy:
        enabled_phases.append("deploy")
    enabled_phases.append("marketing")
    if schedule and args.launch_date:
        enabled_phases.append("schedule")
    
    progress = create_pipeline_progress(enabled_phases)
    
    logger.info("═" * 70)
    logger.info("🚀 AUTO-LAUNCH: COMPLETE PRODUCT PIPELINE")
    logger.info("═" * 70)
    logger.info(f"   Topic: {args.topic}")
    logger.info(f"   Title: {args.title}")
    logger.info(f"   Preset: {args.preset or 'custom'}")
    logger.info(f"   Phases: {' → '.join(enabled_phases)}")
    logger.info("═" * 70)
    
    # Initialize state
    state = ProductState.create(
        output_dir, 
        title=args.title, 
        topic=args.topic,
        price=price,
        launch_date=args.launch_date
    )
    
    phase_idx = 0
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: CREATE
    # ═══════════════════════════════════════════════════════════════
    progress.current_phase = "create"
    progress.current_index = phase_idx
    logger.info(f"\n{format_progress_bar(progress, 'Creating product content...')}")
    logger.info("═══ PHASE 1: CREATE ═══")
    
    create_args = Namespace(
        topic=args.topic,
        title=args.title,
        output=str(output_dir),
        style='dreamweaving',
        pdf=True,
        audio=False,  # We'll do audio separately
        video=False,  # We'll do video separately
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
        progress.phase_results["create"] = False
        progress.errors.append("Create failed")
        state.mark_complete("create", success=False, error="Create failed")
        logger.error("❌ Create phase failed")
        return result
    
    progress.phase_results["create"] = True
    state.mark_complete("create", success=True)
    phase_idx += 1
    
    # Verify create phase
    output_subdir = output_dir / "output"
    verification = verify_create_phase(output_subdir)
    logger.info(format_phase_verification(verification))
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: AUDIO (if enabled)
    # ═══════════════════════════════════════════════════════════════
    if audio and "audio" in enabled_phases:
        progress.current_phase = "audio"
        progress.current_index = phase_idx
        logger.info(f"\n{format_progress_bar(progress, 'Generating audio...')}")
        logger.info("═══ PHASE 2: AUDIO ═══")
        
        try:
            audio_args = Namespace(
                product_dir=str(output_dir),
                voice="shimmer",
                output=str(output_subdir / "audio"),
                list_voices=False,
                dry_run=getattr(args, 'dry_run', False)
            )
            result = audio_generate_command(audio_args)
            progress.phase_results["audio"] = result == 0
        except Exception as e:
            logger.warning(f"   ⚠️ Audio generation skipped: {e}")
            progress.phase_results["audio"] = False
        
        phase_idx += 1
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 3: VIDEO (if enabled)
    # ═══════════════════════════════════════════════════════════════
    if video and "video" in enabled_phases:
        progress.current_phase = "video"
        progress.current_index = phase_idx
        logger.info(f"\n{format_progress_bar(progress, 'Generating video...')}")
        logger.info("═══ PHASE 3: VIDEO ═══")
        
        try:
            video_args = Namespace(
                product_dir=str(output_dir),
                style="professional",
                output=str(output_subdir / "video"),
                dry_run=getattr(args, 'dry_run', False)
            )
            result = video_generate_command(video_args)
            progress.phase_results["video"] = result == 0
        except Exception as e:
            logger.warning(f"   ⚠️ Video generation skipped: {e}")
            progress.phase_results["video"] = False
        
        phase_idx += 1
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 4: SEO
    # ═══════════════════════════════════════════════════════════════
    progress.current_phase = "seo"
    progress.current_index = phase_idx
    logger.info(f"\n{format_progress_bar(progress, 'Creating SEO metadata...')}")
    logger.info("═══ PHASE 4: SEO & METADATA ═══")
    
    try:
        from .core.antigravity import generate_seo_metadata, generate_utm_links
        
        # Generate SEO
        import json
        seo = generate_seo_metadata(args.title, args.topic)
        seo_file = output_subdir / "seo_metadata.json"
        seo_file.write_text(json.dumps({
            "meta_title": seo.meta_title,
            "meta_description": seo.meta_description,
            "keywords": seo.keywords,
            "og_title": seo.og_title,
            "og_description": seo.og_description,
        }, indent=2))
        logger.info(f"   ✅ SEO metadata: {seo_file.name}")
        
        # Generate UTM links
        utm = generate_utm_links(slug)
        utm_file = output_subdir / "utm_links.json"
        utm_file.write_text(json.dumps({
            "twitter": utm.twitter,
            "linkedin": utm.linkedin,
            "instagram": utm.instagram,
            "email": utm.email,
            "newsletter": utm.newsletter,
        }, indent=2))
        logger.info(f"   ✅ UTM links: {utm_file.name}")
        
        progress.phase_results["seo"] = True
    except Exception as e:
        logger.warning(f"   ⚠️ SEO generation error: {e}")
        progress.phase_results["seo"] = False
    
    phase_idx += 1
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 5: DEPLOY (if enabled)
    # ═══════════════════════════════════════════════════════════════
    if deploy and "deploy" in enabled_phases:
        progress.current_phase = "deploy"
        progress.current_index = phase_idx
        logger.info(f"\n{format_progress_bar(progress, 'Deploying to store...')}")
        logger.info("═══ PHASE 5: DEPLOY ═══")
        
        deploy_args = Namespace(
            product_dir=str(output_dir),
            name=args.title,
            slug=slug,
            description=f"Premium digital product: {args.title}",
            price=price,
            sale_price=sale_price,
            salarsu_root=getattr(args, 'salarsu_root', '/home/rsalars/Projects/salarsu'),
            commit=True,
            push=True
        )
        
        result = deploy_command(deploy_args)
        progress.phase_results["deploy"] = result == 0
        
        if result == 0:
            verification = verify_deploy_phase(slug)
            logger.info(format_phase_verification(verification))
        
        phase_idx += 1
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 6: MARKETING
    # ═══════════════════════════════════════════════════════════════
    progress.current_phase = "marketing"
    progress.current_index = phase_idx
    logger.info(f"\n{format_progress_bar(progress, 'Generating marketing content...')}")
    logger.info("═══ PHASE 6: MARKETING ═══")
    
    marketing_args = Namespace(
        product_dir=str(output_dir),
        title=args.title,
        emails=True,
        social=True,
        register_emails=False,
        schedule_buffer=False,
        launch_date=None,
        dry_run=False,
        all=False
    )
    
    result = marketing_command(marketing_args)
    progress.phase_results["marketing"] = result == 0
    phase_idx += 1
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 7: SCHEDULE (if enabled)
    # ═══════════════════════════════════════════════════════════════
    if schedule and args.launch_date and "schedule" in enabled_phases:
        progress.current_phase = "schedule"
        progress.current_index = phase_idx
        logger.info(f"\n{format_progress_bar(progress, 'Scheduling content...')}")
        logger.info("═══ PHASE 7: REGISTER & SCHEDULE ═══")
        
        schedule_args = Namespace(
            product_dir=str(output_dir),
            title=args.title,
            emails=False,
            social=False,
            register_emails=True,
            schedule_buffer=True,
            launch_date=args.launch_date,
            dry_run=getattr(args, 'dry_run', False),
            all=False
        )
        
        result = marketing_command(schedule_args)
        progress.phase_results["schedule"] = result == 0
        phase_idx += 1
    
    # ═══════════════════════════════════════════════════════════════
    # COMPLETE - GENERATE SUMMARY
    # ═══════════════════════════════════════════════════════════════
    progress.current_index = phase_idx
    
    summary = generate_pipeline_summary(
        title=args.title,
        slug=slug,
        output_dir=output_subdir,
        progress=progress,
        launch_date=args.launch_date
    )
    
    logger.info(format_pipeline_summary(summary))
    
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# QUALITY INTELLIGENCE: CLI COMMANDS
# ═══════════════════════════════════════════════════════════════════════════


def quality_check_command(args):
    """Run comprehensive quality check on a product."""
    from pathlib import Path
    from .core.antigravity import generate_quality_report, format_quality_report
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    report = generate_quality_report(product_dir)
    
    if report:
        logger.info(format_quality_report(report))
        return 0 if report.passed else 1
    else:
        logger.error("❌ No product content found.")
        return 1


def readability_score_command(args):
    """Analyze readability of content."""
    from pathlib import Path
    from .core.antigravity import calculate_readability, format_readability_score
    
    # Handle file or directory
    path = Path(args.path)
    
    if path.is_file():
        text = path.read_text()
    elif path.is_dir():
        # Collect all markdown files
        text = ""
        output_dir = path / "output"
        search_dir = output_dir if output_dir.exists() else path
        for md_file in search_dir.glob("**/*.md"):
            text += md_file.read_text() + "\n\n"
    else:
        logger.error(f"❌ Path not found: {path}")
        return 1
    
    if not text.strip():
        logger.error("❌ No text content found.")
        return 1
    
    score = calculate_readability(text)
    logger.info(format_readability_score(score))
    
    return 0


def content_density_command(args):
    """Analyze content density and value metrics."""
    from pathlib import Path
    from .core.antigravity import analyze_content_density, format_content_density
    
    # Handle file or directory
    path = Path(args.path)
    
    if path.is_file():
        text = path.read_text()
    elif path.is_dir():
        # Collect all markdown files
        text = ""
        output_dir = path / "output"
        search_dir = output_dir if output_dir.exists() else path
        for md_file in search_dir.glob("**/*.md"):
            text += md_file.read_text() + "\n\n"
    else:
        logger.error(f"❌ Path not found: {path}")
        return 1
    
    if not text.strip():
        logger.error("❌ No text content found.")
        return 1
    
    density = analyze_content_density(text)
    logger.info(format_content_density(density))
    
    return 0


def completeness_check_command(args):
    """Check product completeness."""
    from pathlib import Path
    from .core.antigravity import check_product_completeness, format_completeness_check
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    check = check_product_completeness(product_dir)
    logger.info(format_completeness_check(check))
    
    return 0 if check.completeness_score >= 70 else 1


def quality_gate_command(args):
    """Check if product passes quality gate for deployment."""
    from pathlib import Path
    from .core.antigravity import check_quality_gate, format_quality_gate
    
    product_dir = Path(args.product_dir)
    
    if not product_dir.exists():
        logger.error(f"❌ Product directory not found: {product_dir}")
        return 1
    
    threshold = args.threshold if hasattr(args, 'threshold') else None
    gate = check_quality_gate(product_dir, threshold)
    logger.info(format_quality_gate(gate))
    
    # Return 0 if passed, 1 if failed (for CI/CD integration)
    return 0 if gate.passed else 1


def main():
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
    deploy_parser.add_argument('--post-twitter', action='store_true', 
                               help='Auto-post Twitter launch thread after deployment')
    deploy_parser.add_argument('--dry-run', action='store_true', 
                               help='Validate Twitter posts without actually posting')
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
    
    # Post Twitter command - standalone Twitter/X posting (independent of deploy)
    twitter_parser = subparsers.add_parser('post-twitter', 
        help='Post Twitter launch thread (run after Coolify deployment)')
    twitter_parser.add_argument('--product-dir', '-d', required=True, 
                                help='Product directory with marketing content')
    twitter_parser.add_argument('--dry-run', action='store_true', 
                                help='Validate and preview without actually posting')
    twitter_parser.set_defaults(func=post_twitter_command)
    
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
    
    # Doctor command - run health checks
    doctor_parser = subparsers.add_parser('doctor', help='Check environment health and diagnose issues')
    doctor_parser.set_defaults(func=doctor_command)
    
    # Init command - initialize new project
    init_parser = subparsers.add_parser('init', help='Initialize a new product project')
    init_parser.add_argument('name', help='Product name')
    init_parser.add_argument('--template', '-t', help='Product template to use')
    init_parser.add_argument('--output', '-o', help='Output directory (default: ./products/<slug>)')
    init_parser.set_defaults(func=init_command)
    
    # Env command - generate environment template
    env_parser = subparsers.add_parser('env', help='Generate environment variables template')
    env_parser.add_argument('--output', '-o', default='.env.template', 
                            help='Output file path (default: .env.template)')
    env_parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing file')
    env_parser.set_defaults(func=env_command)
    
    # Wizard command - interactive product creation wizard
    wizard_parser = subparsers.add_parser('wizard', help='Interactive product creation wizard')
    wizard_parser.add_argument('--output', '-o', help='Output directory for new project')
    wizard_parser.set_defaults(func=wizard_command)
    
    # Responses command - check status of prompt responses
    responses_parser = subparsers.add_parser('responses', help='Check status of responses to prompts')
    responses_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    responses_parser.set_defaults(func=responses_command)
    
    # Preview-prompts command - preview prompts before creating
    preview_parser = subparsers.add_parser('preview-prompts', help='Preview prompts before generating')
    preview_parser.add_argument('--topic', '-t', required=True, help='Product topic')
    preview_parser.add_argument('--title', '-T', required=True, help='Product title')
    preview_parser.add_argument('--template', help='Product template')
    preview_parser.add_argument('--chapters', type=int, default=10, help='Number of chapters (default: 10)')
    preview_parser.set_defaults(func=preview_prompts_command)
    
    # Export command - export prompts for Antigravity
    export_parser = subparsers.add_parser('export', help='Export prompts for Antigravity (copy-paste ready)')
    export_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    export_parser.add_argument('--output', '-o', help='Output file (default: print to stdout)')
    export_parser.set_defaults(func=export_command)
    
    # Next-prompt command - show next prompt needing response
    next_parser = subparsers.add_parser('next-prompt', help='Show next prompt needing a response')
    next_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    next_parser.add_argument('--copy', '-c', action='store_true', help='Copy prompt to clipboard')
    next_parser.set_defaults(func=next_prompt_command)
    
    # Validate command - validate a single response
    validate_parser = subparsers.add_parser('validate', help='Validate a response file')
    validate_parser.add_argument('--file', '-f', required=True, help='Response file to validate')
    validate_parser.add_argument('--min-words', type=int, default=1500, help='Minimum word count (default: 1500)')
    validate_parser.set_defaults(func=validate_command)
    
    # Validate-all command - validate all responses in a product
    validate_all_parser = subparsers.add_parser('validate-all', help='Validate all responses in a product')
    validate_all_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    validate_all_parser.add_argument('--min-words', type=int, default=1500, help='Min word count (default: 1500)')
    validate_all_parser.set_defaults(func=validate_all_command)
    
    # Import command - import a response from a file
    import_parser = subparsers.add_parser('import', help='Import a response from a file')
    import_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    import_parser.add_argument('--slug', '-s', required=True, help='Prompt slug (e.g., chapter_01)')
    import_parser.add_argument('--source', required=True, help='Source file to import')
    import_parser.set_defaults(func=import_command)
    
    # Scaffold command - create response template
    scaffold_parser = subparsers.add_parser('scaffold', help='Create a response template for a prompt')
    scaffold_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    scaffold_parser.add_argument('--slug', '-s', required=True, help='Prompt slug (e.g., chapter_01)')
    scaffold_parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing file')
    scaffold_parser.set_defaults(func=scaffold_command)
    
    # List-bonuses command - show available bonus types
    list_bonus_parser = subparsers.add_parser('list-bonuses', help='List available bonus types')
    list_bonus_parser.set_defaults(func=list_bonuses_command)
    
    # Bonus-prompts command - generate prompts for bonuses
    bonus_prompts_parser = subparsers.add_parser('bonus-prompts', help='Generate prompts for bonus content')
    bonus_prompts_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    bonus_prompts_parser.add_argument('--types', '-t', required=True, 
                                      help='Comma-separated bonus types or "all"')
    bonus_prompts_parser.add_argument('--title', help='Product title (auto-detected if not provided)')
    bonus_prompts_parser.set_defaults(func=bonus_prompts_command)
    
    # Audio-prompts command - generate prompts for audio sessions
    audio_prompts_parser = subparsers.add_parser('audio-prompts', help='Generate prompts for audio sessions')
    audio_prompts_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    audio_prompts_parser.add_argument('--sessions', '-n', type=int, required=True, help='Number of audio sessions')
    audio_prompts_parser.add_argument('--title', help='Product title')
    audio_prompts_parser.add_argument('--topics', help='Comma-separated session topics (optional)')
    audio_prompts_parser.set_defaults(func=audio_prompts_command)
    
    # Audio-status command - show status of audio sessions
    audio_status_parser = subparsers.add_parser('audio-status', help='Show status of audio sessions')
    audio_status_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    audio_status_parser.set_defaults(func=audio_status_command)
    
    # Next-audio command - show next audio session needing work
    next_audio_parser = subparsers.add_parser('next-audio', help='Show next audio session needing work')
    next_audio_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    next_audio_parser.set_defaults(func=next_audio_command)
    
    # Generate-audio command - generate audio from scripts
    gen_audio_parser = subparsers.add_parser('generate-audio', help='Generate audio from scripts using TTS')
    gen_audio_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    gen_audio_parser.add_argument('--session', '-s', help='Specific session slug to generate')
    gen_audio_parser.add_argument('--all', '-a', action='store_true', help='Generate all ready sessions')
    gen_audio_parser.add_argument('--voice', default='en_US-amy-medium', 
                                  help='Voice model or path to voice sample for XTTS')
    gen_audio_parser.add_argument('--engine', default='xtts', choices=['xtts', 'piper', 'espeak'], 
                                  help='TTS engine: xtts (best quality), piper, espeak (default: xtts)')
    gen_audio_parser.add_argument('--speed', type=float, default=0.88,
                                  help='Speed adjustment for XTTS (0.88 = slightly slower, good for meditations)')
    gen_audio_parser.set_defaults(func=generate_audio_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3B ENHANCEMENTS SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # List-audio-templates command
    list_templates_parser = subparsers.add_parser('list-audio-templates',
                                                   help='List audio generation templates/presets')
    list_templates_parser.set_defaults(func=list_audio_templates_command)
    
    # List-voices command
    list_voices_parser = subparsers.add_parser('list-voices',
                                                help='List available TTS voices')
    list_voices_parser.set_defaults(func=list_voices_command)
    
    # Audio-quality command
    audio_quality_parser = subparsers.add_parser('audio-quality',
                                                  help='Analyze audio quality for a product')
    audio_quality_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    audio_quality_parser.set_defaults(func=audio_quality_command)
    
    # Preview-voice command
    preview_voice_parser = subparsers.add_parser('preview-voice',
                                                  help='Preview a voice with sample text')
    preview_voice_parser.add_argument('--voice', '-v', required=True, help='Voice name to preview')
    preview_voice_parser.add_argument('--text', '-t', help='Text to speak (default: sample text)')
    preview_voice_parser.set_defaults(func=preview_voice_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3C: VIDEO GENERATION SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # List-video-templates command
    list_vid_tmpl_parser = subparsers.add_parser('list-video-templates', 
                                                  help='List available video templates')
    list_vid_tmpl_parser.set_defaults(func=list_video_templates_command)
    
    # Video-prompts command
    video_prompts_parser = subparsers.add_parser('video-prompts', 
                                                  help='Generate prompts for video sessions')
    video_prompts_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    video_prompts_parser.add_argument('--videos', '-n', type=int, required=True, help='Number of videos')
    video_prompts_parser.add_argument('--title', help='Product title')
    video_prompts_parser.add_argument('--topics', help='Comma-separated video topics')
    video_prompts_parser.add_argument('--template', default='chapter_video',
                                      help='Video template (default: chapter_video)')
    video_prompts_parser.set_defaults(func=video_prompts_command)
    
    # Video-status command
    video_status_parser = subparsers.add_parser('video-status', help='Show video session status')
    video_status_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    video_status_parser.set_defaults(func=video_status_command)
    
    # Next-video command
    next_video_parser = subparsers.add_parser('next-video', help='Show next video needing work')
    next_video_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    next_video_parser.set_defaults(func=next_video_command)
    
    # Fetch-images command
    fetch_images_parser = subparsers.add_parser('fetch-images', 
                                                 help='Fetch stock images from Unsplash')
    fetch_images_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    fetch_images_parser.set_defaults(func=fetch_images_command)
    
    # Render-video command
    render_video_parser = subparsers.add_parser('render-video', 
                                                 help='Render video using Remotion')
    render_video_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    render_video_parser.add_argument('--session', '-s', help='Specific session slug to render')
    render_video_parser.add_argument('--all', '-a', action='store_true', help='Render all ready sessions')
    render_video_parser.add_argument('--template', default='ChapterVideo',
                                     help='Remotion composition to use (default: ChapterVideo)')
    render_video_parser.set_defaults(func=render_video_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3C ENHANCEMENTS SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # List-video-styles command
    list_styles_parser = subparsers.add_parser('list-video-styles',
                                                help='List video style presets')
    list_styles_parser.set_defaults(func=list_video_styles_command)
    
    # Video-quality command
    video_quality_parser = subparsers.add_parser('video-quality',
                                                  help='Analyze video quality for a product')
    video_quality_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    video_quality_parser.set_defaults(func=video_quality_command)
    
    # List-thumbnail-sizes command
    list_thumb_parser = subparsers.add_parser('list-thumbnail-sizes',
                                               help='List thumbnail size presets')
    list_thumb_parser.set_defaults(func=list_thumbnail_sizes_command)
    
    # Generate-thumbnail command
    gen_thumb_parser = subparsers.add_parser('generate-thumbnail',
                                              help='Generate thumbnails from videos')
    gen_thumb_parser.add_argument('--product-dir', '-d', help='Product directory (batch mode)')
    gen_thumb_parser.add_argument('--video', '-v', help='Single video file')
    gen_thumb_parser.add_argument('--output', '-o', help='Output path (single video mode)')
    gen_thumb_parser.add_argument('--size', '-s', default='youtube',
                                  choices=['youtube', 'social', 'square', 'story', 'twitter'],
                                  help='Size preset (default: youtube)')
    gen_thumb_parser.add_argument('--text', '-t', help='Text overlay on thumbnail')
    gen_thumb_parser.add_argument('--timestamp', type=float, help='Timestamp to capture (seconds)')
    gen_thumb_parser.set_defaults(func=generate_thumbnail_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3D: LANDING PAGE & STORE INTEGRATION SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # List-categories command
    list_cat_parser = subparsers.add_parser('list-categories', 
                                             help='List digital product categories')
    list_cat_parser.set_defaults(func=list_categories_command)
    
    # Landing-prompt command
    landing_prompt_parser = subparsers.add_parser('landing-prompt',
                                                   help='Generate landing page content prompt')
    landing_prompt_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    landing_prompt_parser.set_defaults(func=landing_prompt_command)
    
    # Image-prompt command
    image_prompt_parser = subparsers.add_parser('image-prompt',
                                                 help='Generate cover image prompt')
    image_prompt_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    image_prompt_parser.add_argument('--style', default='premium_digital',
                                     choices=['premium_digital', 'minimalist', 'mystical', 'practical', 'vibrant'],
                                     help='Image style (default: premium_digital)')
    image_prompt_parser.set_defaults(func=image_prompt_command)
    
    # Store-status command
    store_status_parser = subparsers.add_parser('store-status',
                                                 help='Show store integration status')
    store_status_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    store_status_parser.set_defaults(func=store_status_command)
    
    # Generate-sql command
    gen_sql_parser = subparsers.add_parser('generate-sql',
                                            help='Generate SQL for store integration')
    gen_sql_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    gen_sql_parser.set_defaults(func=generate_sql_command)
    
    # Deploy-product command
    deploy_parser = subparsers.add_parser('deploy-product',
                                           help='Deploy product to SalarsNet store')
    deploy_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    deploy_parser.add_argument('--salarsu-path', help='Path to SalarsNet repo (default: ~/Projects/salarsu)')
    deploy_parser.set_defaults(func=deploy_product_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3D ENHANCEMENTS SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Generate-seo command
    gen_seo_parser = subparsers.add_parser('generate-seo',
                                            help='Generate SEO metadata for a product')
    gen_seo_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    gen_seo_parser.set_defaults(func=generate_seo_command)
    
    # List-og-styles command
    list_og_parser = subparsers.add_parser('list-og-styles',
                                            help='List OG image style presets')
    list_og_parser.set_defaults(func=list_og_styles_command)
    
    # Generate-og command
    gen_og_parser = subparsers.add_parser('generate-og',
                                           help='Generate OG images for social sharing')
    gen_og_parser.add_argument('--product-dir', '-d', help='Product directory (batch mode)')
    gen_og_parser.add_argument('--title', '-t', help='Image title (single mode)')
    gen_og_parser.add_argument('--subtitle', help='Subtitle (single mode)')
    gen_og_parser.add_argument('--price', type=float, help='Price to display')
    gen_og_parser.add_argument('--output', '-o', help='Output path (single mode)')
    gen_og_parser.add_argument('--style', '-s', default='default',
                               choices=['default', 'minimal', 'promo', 'dreamweaving'],
                               help='Style preset (default: default)')
    gen_og_parser.add_argument('--sale', action='store_true', help='Add sale badge')
    gen_og_parser.set_defaults(func=generate_og_command)
    
    # Preflight-check command
    preflight_parser = subparsers.add_parser('preflight-check',
                                              help='Run pre-deployment verification')
    preflight_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    preflight_parser.set_defaults(func=preflight_check_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 4 ENHANCEMENTS SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Compile-stats command
    compile_stats_parser = subparsers.add_parser('compile-stats',
                                                  help='Show compilation statistics')
    compile_stats_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    compile_stats_parser.set_defaults(func=compile_stats_command)
    
    # Compile-verify command
    compile_verify_parser = subparsers.add_parser('compile-verify',
                                                   help='Verify compilation integrity')
    compile_verify_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    compile_verify_parser.set_defaults(func=compile_verify_command)
    
    # Generate-toc command
    gen_toc_parser = subparsers.add_parser('generate-toc',
                                            help='Generate table of contents')
    gen_toc_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    gen_toc_parser.add_argument('--title', '-t', help='Product title (if not in product.json)')
    gen_toc_parser.add_argument('--save', '-s', action='store_true', help='Save TOC to output/')
    gen_toc_parser.add_argument('--chapters-only', action='store_true', help='Chapters only (no sections)')
    gen_toc_parser.set_defaults(func=generate_toc_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 5 ENHANCEMENTS SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Deploy-dry-run command
    deploy_dry_parser = subparsers.add_parser('deploy-dry-run',
                                               help='Preview deployment without changes')
    deploy_dry_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    deploy_dry_parser.add_argument('--salarsu-path', help='Path to SalarsNet repo')
    deploy_dry_parser.set_defaults(func=deploy_dry_run_command)
    
    # Deploy-verify command
    deploy_verify_parser = subparsers.add_parser('deploy-verify',
                                                  help='Verify deployment was successful')
    deploy_verify_parser.add_argument('--slug', '-s', required=True, help='Product slug')
    deploy_verify_parser.add_argument('--salarsu-path', help='Path to SalarsNet repo')
    deploy_verify_parser.set_defaults(func=deploy_verify_command)
    
    # Deploy-history command
    deploy_history_parser = subparsers.add_parser('deploy-history',
                                                   help='Show deployment history')
    deploy_history_parser.add_argument('--slug', '-s', required=True, help='Product slug')
    deploy_history_parser.add_argument('--salarsu-path', help='Path to SalarsNet repo')
    deploy_history_parser.set_defaults(func=deploy_history_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 6 ENHANCEMENTS SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # List-marketing-templates command
    mkt_templates_parser = subparsers.add_parser('list-marketing-templates',
                                                  help='List available marketing templates')
    mkt_templates_parser.set_defaults(func=list_marketing_templates_command)
    
    # Generate-utm command
    gen_utm_parser = subparsers.add_parser('generate-utm',
                                            help='Generate UTM links for tracking')
    gen_utm_parser.add_argument('--slug', '-s', required=True, help='Product slug')
    gen_utm_parser.add_argument('--campaign', '-c', help='Campaign name (default: launch-MMYYYY)')
    gen_utm_parser.add_argument('--save', action='store_true', help='Save to files')
    gen_utm_parser.add_argument('--output', '-o', help='Output directory')
    gen_utm_parser.set_defaults(func=generate_utm_command)
    
    # Marketing-preview command
    mkt_preview_parser = subparsers.add_parser('marketing-preview',
                                                help='Preview and validate marketing content')
    mkt_preview_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    mkt_preview_parser.set_defaults(func=marketing_preview_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 7 ENHANCEMENTS SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Schedule-preview command
    sched_preview_parser = subparsers.add_parser('schedule-preview',
                                                  help='Preview scheduled posts')
    sched_preview_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    sched_preview_parser.add_argument('--launch-date', '-l', required=True, help='Launch date (YYYY-MM-DD)')
    sched_preview_parser.add_argument('--posts-per-day', '-p', type=int, default=3, help='Posts per day')
    sched_preview_parser.add_argument('--duration', type=int, default=7, help='Duration in days')
    sched_preview_parser.set_defaults(func=schedule_preview_command)
    
    # Registration-status command
    reg_status_parser = subparsers.add_parser('registration-status',
                                               help='Check email/social registration status')
    reg_status_parser.add_argument('--slug', '-s', required=True, help='Product slug')
    reg_status_parser.add_argument('--salarsu-path', help='Path to SalarsNet repo')
    reg_status_parser.set_defaults(func=registration_status_command)
    
    # Launch-countdown command
    countdown_parser = subparsers.add_parser('launch-countdown',
                                              help='Show launch countdown with checklist')
    countdown_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    countdown_parser.add_argument('--launch-date', '-l', required=True, help='Launch date (YYYY-MM-DD)')
    countdown_parser.set_defaults(func=launch_countdown_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PIPELINE AUTOMATION SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # List-presets command
    presets_parser = subparsers.add_parser('list-presets',
                                            help='List available pipeline presets')
    presets_parser.set_defaults(func=list_presets_command)
    
    # Auto-launch command
    launch_parser = subparsers.add_parser('auto-launch',
                                           help='Complete product from topic to live in one command')
    launch_parser.add_argument('--topic', '-t', required=True, help='Main topic')
    launch_parser.add_argument('--title', '-T', required=True, help='Product title')
    launch_parser.add_argument('--preset', '-p', help='Pipeline preset (quick, standard, premium, enterprise)')
    launch_parser.add_argument('--output', '-o', help='Output directory')
    launch_parser.add_argument('--price', type=float, help='Product price')
    launch_parser.add_argument('--sale-price', type=float, help='Sale price')
    launch_parser.add_argument('--launch-date', '-l', help='Launch date (YYYY-MM-DD)')
    launch_parser.add_argument('--audio', action='store_true', help='Generate audio')
    launch_parser.add_argument('--video', action='store_true', help='Generate video')
    launch_parser.add_argument('--deploy', action='store_true', help='Deploy to store')
    launch_parser.add_argument('--schedule', action='store_true', help='Register and schedule')
    launch_parser.add_argument('--salarsu-root', default='/home/rsalars/Projects/salarsu', help='SalarsNet path')
    launch_parser.add_argument('--prompts-only', action='store_true', help='Generate prompts only')
    launch_parser.add_argument('--dry-run', action='store_true', help='Validate only')
    launch_parser.set_defaults(func=auto_launch_command)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # QUALITY INTELLIGENCE SUBPARSERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Quality-check command (comprehensive)
    quality_parser = subparsers.add_parser('quality-check',
                                            help='Run comprehensive quality analysis')
    quality_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    quality_parser.set_defaults(func=quality_check_command)
    
    # Readability-score command
    readability_parser = subparsers.add_parser('readability-score',
                                                help='Analyze text readability')
    readability_parser.add_argument('--path', '-p', required=True, help='File or directory to analyze')
    readability_parser.set_defaults(func=readability_score_command)
    
    # Content-density command
    density_parser = subparsers.add_parser('content-density',
                                            help='Analyze content value density')
    density_parser.add_argument('--path', '-p', required=True, help='File or directory to analyze')
    density_parser.set_defaults(func=content_density_command)
    
    # Completeness-check command
    completeness_parser = subparsers.add_parser('completeness-check',
                                                 help='Check product completeness')
    completeness_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    completeness_parser.set_defaults(func=completeness_check_command)
    
    # Quality-gate command (deploy blocker)
    gate_parser = subparsers.add_parser('quality-gate',
                                         help='Check quality gate for deployment')
    gate_parser.add_argument('--product-dir', '-d', required=True, help='Product directory')
    gate_parser.add_argument('--threshold', '-t', type=float, default=70, help='Minimum score (0-100)')
    gate_parser.set_defaults(func=quality_gate_command)
    
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
