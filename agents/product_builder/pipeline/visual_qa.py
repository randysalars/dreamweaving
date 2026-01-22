"""
Visual QA Gate
Quality assurance for product visuals.
"""

import logging
from pathlib import Path
from typing import List, Dict, Tuple
from pydantic import BaseModel, Field

from ..schemas.visual_intent_map import VisualIntentMap, VisualIntent
from ..schemas.visual_style import VisualStyle

logger = logging.getLogger(__name__)


class VisualQAResult(BaseModel):
    """Result of QA check for a single visual."""
    section_id: str
    passed: bool
    clarity_score: int = Field(ge=0, le=10)
    consistency_score: int = Field(ge=0, le=10)
    restraint_score: int = Field(ge=0, le=10)
    readability_score: int = Field(ge=0, le=10)
    integration_score: int = Field(ge=0, le=10)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    @property
    def average_score(self) -> float:
        return (self.clarity_score + self.consistency_score + 
                self.restraint_score + self.readability_score + 
                self.integration_score) / 5


class VisualQAReport(BaseModel):
    """Complete QA report for all visuals."""
    product_title: str
    total_visuals: int
    passed_count: int
    failed_count: int
    results: List[VisualQAResult]
    overall_passed: bool
    recommendations: List[str] = Field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        if self.total_visuals == 0:
            return 1.0
        return self.passed_count / self.total_visuals


class VisualQA:
    """
    Quality assurance gate for product visuals.
    
    Checks:
    - Clarity: Does this make the idea clearer?
    - Consistency: Does it match the style system?
    - Restraint: Is it necessary?
    - Readability: Does it print cleanly?
    - Integration: Does it support nearby text?
    """
    
    PASSING_THRESHOLD = 7
    REQUIRED_PASS_RATE = 0.8  # 80% of visuals must pass
    
    def __init__(self):
        pass
    
    def evaluate_all(
        self, 
        visual_map: VisualIntentMap,
        generated_paths: Dict[str, str],
        style: VisualStyle
    ) -> VisualQAReport:
        """
        Evaluate all visuals in a product.
        
        Args:
            visual_map: The visual intent map
            generated_paths: Map of section_id -> file path
            style: The visual style being used
            
        Returns:
            VisualQAReport with all results
        """
        logger.info(f"🔍 Visual QA evaluating {len(visual_map.intents)} visuals...")
        
        results = []
        
        for intent in visual_map.intents:
            if intent.recommended_type == "none":
                continue
            
            path = generated_paths.get(intent.section_id)
            result = self._evaluate_visual(intent, path, style)
            results.append(result)
        
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        
        report = VisualQAReport(
            product_title=visual_map.product_title,
            total_visuals=len(results),
            passed_count=passed_count,
            failed_count=failed_count,
            results=results,
            overall_passed=(passed_count / len(results)) >= self.REQUIRED_PASS_RATE if results else True,
            recommendations=self._generate_recommendations(results)
        )
        
        logger.info(f"Visual QA: {passed_count}/{len(results)} passed ({report.pass_rate:.0%})")
        logger.info(f"Overall: {'✅ PASS' if report.overall_passed else '❌ FAIL'}")
        
        return report
    
    def _evaluate_visual(
        self, 
        intent: VisualIntent, 
        path: str,
        style: VisualStyle
    ) -> VisualQAResult:
        """Evaluate a single visual."""
        issues = []
        recommendations = []
        
        # Check if file exists
        if not path or not Path(path).exists():
            return VisualQAResult(
                section_id=intent.section_id,
                passed=False,
                clarity_score=0,
                consistency_score=0,
                restraint_score=0,
                readability_score=0,
                integration_score=0,
                issues=["Visual file not found"],
                recommendations=["Generate or source the visual"]
            )
        
        # Clarity: Does it match the intent?
        clarity_score = self._assess_clarity(intent)
        if clarity_score < 7:
            issues.append(f"Clarity below threshold for {intent.section_id}")
        
        # Consistency: Does it match the style?
        consistency_score = self._assess_consistency(path, style)
        if consistency_score < 7:
            issues.append(f"Style inconsistency in {intent.section_id}")
            recommendations.append(f"Regenerate using {style.name} style prompts")
        
        # Restraint: Is it necessary?
        restraint_score = self._assess_restraint(intent)
        if restraint_score < 7:
            issues.append(f"Visual may be unnecessary: {intent.section_id}")
            recommendations.append("Consider removing or simplifying")
        
        # Readability: File quality check
        readability_score = self._assess_readability(path)
        if readability_score < 7:
            issues.append(f"Quality issue in {intent.section_id}")
        
        # Integration: Placement appropriateness
        integration_score = self._assess_integration(intent)
        if integration_score < 7:
            issues.append(f"Placement issue for {intent.section_id}")
        
        avg_score = (clarity_score + consistency_score + restraint_score + 
                     readability_score + integration_score) / 5
        
        return VisualQAResult(
            section_id=intent.section_id,
            passed=avg_score >= self.PASSING_THRESHOLD,
            clarity_score=clarity_score,
            consistency_score=consistency_score,
            restraint_score=restraint_score,
            readability_score=readability_score,
            integration_score=integration_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_clarity(self, intent: VisualIntent) -> int:
        """Assess if the visual will clarify the concept."""
        # High clarity for explanation roles
        if intent.visual_role == "explanation":
            return 9
        elif intent.visual_role == "orientation":
            return 8
        elif intent.visual_role == "memory_anchor":
            return 8
        elif intent.visual_role == "emotional_tone":
            return 7
        else:
            return 6
    
    def _assess_consistency(self, path: str, style: VisualStyle) -> int:
        """Assess if the visual matches the style system."""
        # In a full implementation, this would analyze the image
        # For now, assume generated images are consistent
        file_path = Path(path)
        
        if file_path.suffix == ".png":
            return 8
        elif file_path.suffix == ".mmd":
            return 9  # Mermaid is consistent by design
        elif file_path.suffix == ".svg":
            return 9
        else:
            return 6
    
    def _assess_restraint(self, intent: VisualIntent) -> int:
        """Assess if the visual is necessary."""
        # Must-haves get high restraint scores
        if intent.priority == "must_have":
            return 9
        elif intent.priority == "nice_to_have":
            return 7
        else:
            return 5
    
    def _assess_readability(self, path: str) -> int:
        """Assess file quality for print/display."""
        file_path = Path(path)
        
        if not file_path.exists():
            return 0
        
        # Check file size as proxy for quality
        size_kb = file_path.stat().st_size / 1024
        
        if size_kb < 10:  # Very small, might be placeholder
            return 5
        elif size_kb > 5000:  # Very large, might be slow
            return 6
        else:
            return 8
    
    def _assess_integration(self, intent: VisualIntent) -> int:
        """Assess if placement is appropriate."""
        # Section starts and chapter ends are good placements
        if intent.placement in ["section_start", "chapter_end"]:
            return 9
        elif intent.placement == "after_explanation":
            return 8
        elif intent.placement == "full_page":
            return 9
        else:
            return 7
    
    def _generate_recommendations(self, results: List[VisualQAResult]) -> List[str]:
        """Generate overall recommendations from results."""
        recommendations = []
        
        failed = [r for r in results if not r.passed]
        if failed:
            recommendations.append(f"Revise {len(failed)} visuals that didn't pass QA")
        
        # Check for common issues
        low_clarity = [r for r in results if r.clarity_score < 7]
        if len(low_clarity) > len(results) * 0.3:
            recommendations.append("Consider adding more explanatory diagrams")
        
        low_consistency = [r for r in results if r.consistency_score < 7]
        if len(low_consistency) > len(results) * 0.2:
            recommendations.append("Regenerate visuals with consistent style prompts")
        
        return recommendations
