from ..schemas.blueprint import ProductBlueprint, ProductPromise, BuildTarget, MarketingHooks, AudiencePersona, ChapterSpec, PricingModel
from .intelligence import DemandSignal

class ProductArchitect:
    """
    The Orchestrator that turns a DemandSignal into a concrete ProductBlueprint.
    In a full LLM run, this would construct a massive system prompt.
    For this implementation, we provide the structure and 'fill' methods.
    """
    
    def generate_blueprint(self, signal: DemandSignal, title_override: str = None) -> ProductBlueprint:
        """
        Synthesizes a Blueprint from the research signal.
        """
        
        # 1. Define the Promise
        promise = ProductPromise(
            headline=f"Master {signal.topic} in 72 Hours",
            subhead="A systematic approach to solving this recurring problem once and for all.",
            target_audience="Builders and creators who are stuck.",
            transformation_timeline="3 Days"
        )
        
        # 2. structure Audience (Placeholder - usually LLM generated)
        audience = AudiencePersona(
            current_state="Confused and overwhelmed by dispersed information.",
            desired_state=f"Competent and authoritative in {signal.topic}.",
            constraints=["Time poor", " skepticism"],
            fears=["Wasting time", "Looking foolish"],
            language_patterns=["How do I...", "Best practice for..."]
        )
        
        # 3. Map Chapters (Standard Template Strategy for v1)
        chapters = []
        phases = ["Foundations", "Core Mechanics", "Advanced Execution", "Mastery"]
        for i, phase in enumerate(phases):
            chapters.append(ChapterSpec(
                title=f"Phase {i+1}: {phase}",
                purpose=f"Establish the {phase.lower()} of the system.",
                key_takeaways=[f"Understand {phase}", "Apply basic rules"],
                estimated_pages=25,
                source_refs=[s.get('url', '') for s in signal.raw_sources[:2]]
            ))
            
        # 4. Marketing Hooks
        marketing = MarketingHooks(
            core_angles=[f"Why most people fail at {signal.topic}", "The system, not the goal"],
            objections_to_crush=["I don't have time", "I'm not an expert"]
        )

        # 5. Pricing (Default Logic)
        pricing = PricingModel(
            amount=49.00,
            currency="USD",
            model_type="fixed"
        )
        
        return ProductBlueprint(
            title=title_override or f"The {signal.topic} Codex",
            slug=(title_override or signal.topic).lower().replace(" ", "-"),
            promise=promise,
            audience=audience,
            voice_rules=["Authoritative", "Direct", "No fluff"],
            chapter_map=chapters,
            marketing=marketing,
            pricing=pricing,
            build_targets=BuildTarget(target_page_count=100, publish_path=f"/products/{(title_override or signal.topic).lower().replace(' ', '-')}")
        )
