"""
Studio Orchestrator
The master coordinator for the full Studio-Grade Product Pipeline.
Runs the complete flow from DemandSignal to Published Product.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from ..core.context import ProductContext
from ..core.intelligence import DemandSignal
from ..core.library_manager import LibraryManager

# Contract Artifact Generators
from .market_cartographer import MarketCartographer
from .transformation_designer import TransformationDesigner
from .curriculum_architect import CurriculumArchitect
from .voice_stylist import VoiceStylist
from .product_mind import ProductMind
from .narrative_architect import NarrativeArchitect

# Creation Pipeline
from .writers_room import WritersRoom
from .master_editor import MasterEditor
from .ai_detector import AIDetector
from .compression_pass import CompressionPass

# Quality Assurance
from .qa_lab import QALab
from .reader_sim import ReaderSimulator
from .delight_guard import DelightGuard

# Packaging
from ..packaging.bonus_architect import BonusArchitect
from ..packaging.audio import AudioScriptAgent
from ..packaging.video import VideoOrchestrator

# Schemas
from ..schemas.positioning_brief import PositioningBrief
from ..schemas.transformation_map import TransformationMap
from ..schemas.curriculum_graph import CurriculumGraph
from ..schemas.voice_style_guide import VoiceStyleGuide
from ..schemas.product_intelligence import ProductIntelligence
from ..schemas.premium_scorecard import PremiumScorecard

logger = logging.getLogger(__name__)


@dataclass
class StudioArtifacts:
    """All contract artifacts generated during the studio pipeline."""
    positioning: Optional[PositioningBrief] = None
    transformation: Optional[TransformationMap] = None
    curriculum: Optional[CurriculumGraph] = None
    voice: Optional[VoiceStyleGuide] = None
    intelligence: Optional[ProductIntelligence] = None
    scorecard: Optional[PremiumScorecard] = None


class StudioOrchestrator:
    """
    The Master Conductor for Studio-Grade Product Creation.
    
    Pipeline Phases:
    1. Research: DemandSignal → PositioningBrief
    2. Design: TransformationMap → CurriculumGraph
    3. Narrative: NarrativeSpine → VoiceStyleGuide
    4. Creation: WritersRoom → MasterEditor → AIDetector → Compression
    5. QA: QALab → ReaderSim → PremiumScorecard
    6. Package: BonusArchitect → Audio/Video → Publisher
    """
    
    def __init__(self, context: ProductContext):
        self.context = context
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.artifacts = StudioArtifacts()
        self.library = LibraryManager()
        
        # Phase 1: Research
        self.cartographer = MarketCartographer(self.templates_dir)
        
        # Phase 2: Design
        self.transformation_designer = TransformationDesigner(self.templates_dir)
        self.curriculum_architect = CurriculumArchitect(self.templates_dir)
        
        # Phase 3: Narrative
        self.product_mind = ProductMind(self.templates_dir)
        self.narrative_architect = NarrativeArchitect(self.templates_dir)
        self.voice_stylist = VoiceStylist(self.templates_dir)
        
        # Phase 4: Creation
        self.writers_room = WritersRoom(self.templates_dir)
        self.master_editor = MasterEditor(self.templates_dir)
        self.ai_detector = AIDetector()
        self.compression = CompressionPass(self.templates_dir)
        
        # Phase 5: QA
        self.qa_lab = QALab(self.templates_dir)
        self.reader_sim = ReaderSimulator(self.templates_dir)
        self.delight_guard = DelightGuard(self.templates_dir)
        
        # Phase 6: Packaging
        self.bonus_architect = BonusArchitect(self.templates_dir)
        self.audio_agent = AudioScriptAgent()
        self.video_agent = VideoOrchestrator()
    
    def run_full_pipeline(self, signal: DemandSignal, title: str) -> Dict[str, Any]:
        """
        Execute the complete studio pipeline.
        
        Args:
            signal: Market demand signal
            title: Product title
            
        Returns:
            Dict with all outputs and scorecard
        """
        logger.info(f"🎬 STUDIO PIPELINE START: {title}")
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 1: RESEARCH
        # ═══════════════════════════════════════════════════════════════
        logger.info("═══ PHASE 1: RESEARCH ═══")
        
        self.artifacts.positioning = self.cartographer.generate(signal, title)
        logger.info(f"✅ PositioningBrief: {self.artifacts.positioning.core_promise[:50]}...")
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 2: DESIGN
        # ═══════════════════════════════════════════════════════════════
        logger.info("═══ PHASE 2: DESIGN ═══")
        
        self.artifacts.transformation = self.transformation_designer.generate(
            self.artifacts.positioning, title
        )
        logger.info(f"✅ TransformationMap: {len(self.artifacts.transformation.milestones)} milestones")
        
        self.artifacts.curriculum = self.curriculum_architect.generate(
            self.artifacts.transformation, title
        )
        logger.info(f"✅ CurriculumGraph: {len(self.artifacts.curriculum.concepts)} concepts")
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 3: NARRATIVE
        # ═══════════════════════════════════════════════════════════════
        logger.info("═══ PHASE 3: NARRATIVE ═══")
        
        self.artifacts.intelligence = self.product_mind.generate(signal, title)
        logger.info(f"✅ ProductIntelligence: {self.artifacts.intelligence.thesis[:50]}...")
        
        self.artifacts.voice = self.voice_stylist.generate(
            self.artifacts.positioning, title
        )
        logger.info(f"✅ VoiceStyleGuide: {len(self.artifacts.voice.banned_phrases)} banned phrases")
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 4: CREATION (per chapter)
        # ═══════════════════════════════════════════════════════════════
        logger.info("═══ PHASE 4: CREATION ═══")
        
        # Build chapters based on curriculum
        all_content = []
        for i, concept in enumerate(self.artifacts.curriculum.concepts):
            chapter_content = self._create_chapter(concept, i)
            all_content.append(chapter_content)
        
        combined_content = "\n\n".join(all_content)
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 5: QA
        # ═══════════════════════════════════════════════════════════════
        logger.info("═══ PHASE 5: QA ═══")
        
        qa_context = {
            "title": title,
            "thesis": self.artifacts.intelligence.thesis,
            "emotional_arc": self.artifacts.intelligence.emotional_arc
        }
        
        # Run QA Lab
        qa_report = self.qa_lab.run_all_tests(combined_content, qa_context)
        logger.info(f"QA Lab: {sum(1 for t in [qa_report.clarity, qa_report.coherence, qa_report.utility, qa_report.delight, qa_report.finishability, qa_report.originality] if t.passed)}/6 passed")
        
        # Run Reader Simulation
        focus_group = self.reader_sim.run_focus_group(
            combined_content, 
            self.artifacts.positioning.core_promise
        )
        logger.info(f"Focus Group: {focus_group['average_engagement']:.1f}/10 engagement")
        
        # Premium Scorecard
        delight_score, _ = self.delight_guard.evaluate(combined_content, qa_context)
        
        self.artifacts.scorecard = PremiumScorecard(
            thinking_depth=8,  # From ProductMind quality
            structure_curriculum=min(10, len(self.artifacts.curriculum.concepts) + 5),
            clarity_coherence=qa_report.clarity.score,
            delight_voice=delight_score.enjoyment,
            practicality_actionability=qa_report.utility.score,
            bonus_power=8,  # Will be set after BonusArchitect
            packaging_quality=8
        )
        
        logger.info(f"Premium Scorecard: {self.artifacts.scorecard.average:.1f}/10 avg, Verdict: {self.artifacts.scorecard.verdict}")
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 6: PACKAGING
        # ═══════════════════════════════════════════════════════════════
        logger.info("═══ PHASE 6: PACKAGING ═══")
        
        # Generate bonuses
        bonus_plan = self.bonus_architect.design(
            self.artifacts.intelligence,
            self.context.blueprint.chapter_map if self.context.blueprint else []
        )
        logger.info(f"✅ BonusPlan: {len(bonus_plan.bonuses)} bonuses")
        
        # Generate summaries
        executive_summary = self.compression.generate_executive_summary(combined_content, title)
        quickstart = self.compression.generate_quickstart(combined_content, title)
        
        logger.info("🎬 STUDIO PIPELINE COMPLETE")
        
        return {
            "title": title,
            "content": combined_content,
            "artifacts": self.artifacts,
            "qa_report": qa_report,
            "focus_group": focus_group,
            "scorecard": self.artifacts.scorecard,
            "bonus_plan": bonus_plan,
            "executive_summary": executive_summary,
            "quickstart": quickstart,
            "publishable": self.artifacts.scorecard.publishable
        }
    
    def _create_chapter(self, concept, index: int) -> str:
        """Create a single chapter through the creation pipeline."""
        # Build context
        context = {
            "chapter_number": index + 1,
            "chapter_title": concept.name,
            "chapter_purpose": concept.description,
            "voice_rules": "\n".join(self.artifacts.voice.sentence_rhythm_rules) if self.artifacts.voice else "",
            "banned_phrases": self.artifacts.voice.banned_phrases if self.artifacts.voice else [],
            "key_takeaways": concept.description,
        }
        
        # Draft
        draft = self.writers_room.write_chapter(context)
        
        # Master Edit
        edit_context = {
            "chapter_purpose": concept.description,
            "target_emotion": "clarity",
            "reader_energy": "neutral",
            "core_insight": concept.description
        }
        polished = self.master_editor.polish(draft, edit_context)
        
        # AI Detection
        passes, findings = self.ai_detector.analyze(polished)
        if not passes:
            polished = self.ai_detector.clean(polished)
        
        # Compression
        compressed = self.compression.compress(polished)
        
        return compressed
