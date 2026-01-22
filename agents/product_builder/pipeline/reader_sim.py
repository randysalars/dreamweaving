import logging
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from ..core.llm import LLMClient
import json

logger = logging.getLogger(__name__)


class PersonaFeedback(BaseModel):
    """Structured feedback from a simulated reader persona."""
    bored_at: List[str] = Field(default_factory=list, description="Sections where they lose interest")
    confused_at: List[str] = Field(default_factory=list, description="Sections that confuse them")
    excited_at: List[str] = Field(default_factory=list, description="Sections that excite them")
    would_skip: List[str] = Field(default_factory=list, description="Sections they'd skip")
    would_share: List[str] = Field(default_factory=list, description="Sections they'd share with others")
    engagement_score: int = Field(ge=1, le=10, default=5)
    would_finish: bool = Field(default=True)
    key_objection: str = Field(default="")


class FocusGroupReport(BaseModel):
    """Consolidated report from all three personas."""
    beginner_bob: PersonaFeedback
    skeptic_sam: PersonaFeedback
    busy_brenda: PersonaFeedback
    
    @property
    def average_engagement(self) -> float:
        return (self.beginner_bob.engagement_score + 
                self.skeptic_sam.engagement_score + 
                self.busy_brenda.engagement_score) / 3
    
    @property
    def all_would_finish(self) -> bool:
        return all([self.beginner_bob.would_finish, 
                   self.skeptic_sam.would_finish, 
                   self.busy_brenda.would_finish])
    
    @property
    def critical_fixes(self) -> List[str]:
        """Aggregate the most important fixes needed."""
        fixes = []
        # Add confused sections from all personas
        for section in set(self.beginner_bob.confused_at + self.skeptic_sam.confused_at):
            fixes.append(f"Clarify: {section}")
        # Add boring sections that multiple personas flagged
        boring = set(self.beginner_bob.bored_at) & set(self.busy_brenda.bored_at)
        for section in boring:
            fixes.append(f"Energize: {section}")
        return fixes[:5]  # Top 5


class ReaderSimulator:
    """
    Simulates a Focus Group of 3 distinct reader personas.
    
    - Beginner Bob: Low patience, needs hand-holding
    - Skeptic Sam: Distrusts claims, demands proof
    - Busy Brenda: Wants fast wins, hates theory
    """
    
    def __init__(self, templates_dir: Path):
        self.template_path = templates_dir / "reader_sim.md"
        self.llm = LLMClient()
        self.personas = [
            {
                "name": "Beginner Bob",
                "short_name": "beginner_bob",
                "description": "New to this topic. Easily overwhelmed by jargon. Needs hand-holding.",
                "reading_style": "Reads slowly, re-reads confusing parts, gives up if lost",
                "triggers": {
                    "bored": "Too much theory without examples",
                    "confused": "Undefined terms, assumed knowledge",
                    "excited": "Clear 'aha' moments, simple frameworks"
                },
                "key_question": "Is this really for beginners like me?"
            },
            {
                "name": "Skeptic Sam",
                "short_name": "skeptic_sam",
                "description": "Burned by many info products. High BS detector. Demands proof.",
                "reading_style": "Skeptical of claims, looks for evidence, mentally argues back",
                "triggers": {
                    "bored": "Generic advice without specifics",
                    "confused": "Logical gaps, unsupported claims",
                    "excited": "Data, case studies, nuanced tradeoffs"
                },
                "key_question": "Where's the proof this actually works?"
            },
            {
                "name": "Busy Brenda",
                "short_name": "busy_brenda",
                "description": "High value on time. Skims content. Wants fast wins.",
                "reading_style": "Scans headings, reads first sentences, skips to action items",
                "triggers": {
                    "bored": "Long intros, excessive context-setting",
                    "confused": "Buried actionable advice",
                    "excited": "Quick wins, templates, checklists"
                },
                "key_question": "Can I get value from this in 30 minutes?"
            }
        ]

    def run_focus_group(self, draft_content: str, product_promise: str) -> Dict[str, Any]:
        """
        Runs the simulation for all personas and returns a consolidated report.
        """
        logger.info("🎭 Running Enhanced Reader Focus Group...")
        
        results = {}
        
        for persona in self.personas:
            logger.info(f"Simulating: {persona['name']}")
            feedback = self._simulate_persona(persona, draft_content, product_promise)
            results[persona["short_name"]] = feedback
        
        report = FocusGroupReport(
            beginner_bob=results.get("beginner_bob", PersonaFeedback()),
            skeptic_sam=results.get("skeptic_sam", PersonaFeedback()),
            busy_brenda=results.get("busy_brenda", PersonaFeedback())
        )
        
        logger.info(f"Focus Group Average Engagement: {report.average_engagement:.1f}/10")
        logger.info(f"All Would Finish: {report.all_would_finish}")
        
        return {
            "summary": self._generate_summary(report),
            "average_engagement": report.average_engagement,
            "all_would_finish": report.all_would_finish,
            "critical_fixes": report.critical_fixes,
            "details": {
                "beginner_bob": report.beginner_bob.model_dump(),
                "skeptic_sam": report.skeptic_sam.model_dump(),
                "busy_brenda": report.busy_brenda.model_dump()
            }
        }
    
    def _simulate_persona(self, persona: Dict, content: str, promise: str) -> PersonaFeedback:
        """Simulate a single persona reading the content."""
        prompt = f"""
You are simulating {persona['name']}: {persona['description']}

Reading Style: {persona['reading_style']}
Key Question: {persona['key_question']}

## Content to Review (first 2000 chars):
{content[:2000]}

## Product Promise:
{promise}

## Your Task:
Read this as {persona['name']} and respond with JSON:

{{
    "bored_at": ["section or topic that bores you"],
    "confused_at": ["section or topic that confuses you"],
    "excited_at": ["section or topic that excites you"],
    "would_skip": ["section you'd skip"],
    "would_share": ["section you'd share with others"],
    "engagement_score": 1-10,
    "would_finish": true/false,
    "key_objection": "Your main complaint or concern"
}}

Be honest and critical. Channel {persona['name']}'s perspective fully.
"""
        
        try:
            response = self.llm.generate(prompt, max_tokens=800)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                return PersonaFeedback(**data)
        except Exception as e:
            logger.warning(f"Failed to parse {persona['name']} simulation: {e}")
        
        # Default feedback
        return PersonaFeedback(
            engagement_score=6,
            would_finish=True,
            key_objection="Unable to fully simulate"
        )
    
    def _generate_summary(self, report: FocusGroupReport) -> str:
        """Generate a human-readable summary."""
        avg = report.average_engagement
        
        if avg >= 8:
            tone = "Strong positive reception"
        elif avg >= 6:
            tone = "Mostly positive, some concerns"
        elif avg >= 4:
            tone = "Mixed reception, significant issues"
        else:
            tone = "Poor reception, major revision needed"
        
        objections = []
        if report.beginner_bob.key_objection:
            objections.append(f"Beginner: {report.beginner_bob.key_objection}")
        if report.skeptic_sam.key_objection:
            objections.append(f"Skeptic: {report.skeptic_sam.key_objection}")
        if report.busy_brenda.key_objection:
            objections.append(f"Busy: {report.busy_brenda.key_objection}")
        
        return f"{tone}. Key concerns: {'; '.join(objections[:2]) if objections else 'None flagged'}"

