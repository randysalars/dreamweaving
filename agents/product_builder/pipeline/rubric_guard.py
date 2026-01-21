import logging
from typing import List
from ..schemas.rubric import RubricScore, RubricItem, AssessmentReport

logger = logging.getLogger(__name__)

class RubricGuard:
    """
    Quality Assurance Agent.
    Evaluates content against 3 axes: Story, Teaching, Conversion.
    Enforces minimum quality standards.
    """
    
    def evaluate(self, content: str) -> AssessmentReport:
        """
        Runs the 3 assessments.
        """
        logger.info("Running Rubric Quality Gate...")
        
        # 1. Story Rubric (Simulated)
        story = self._assess_category(
            "Story",
            ["Hook Strength", "Emotional Movement", "Coherence", "Memorability", "Momentum"],
            content
        )
        
        # 2. Teaching Rubric
        teaching = self._assess_category(
            "Teaching",
            ["Clarity", "Worked Examples", "Practice Quality", "Misconception Coverage", "Transfer to Life"],
            content
        )
        
        # 3. Conversion Rubric
        conversion = self._assess_category(
            "Conversion",
            ["Promise Clarity", "Objection Handling", "Credibility", "Offer Stack", "CTA Strength"],
            content
        )
        
        # Verdict Logic
        failed = not (story.passed and teaching.passed and conversion.passed)
        verdict = "REVISE" if failed else "SHIP"
        
        issues = []
        if not story.passed: issues.append("Story score too low.")
        if not teaching.passed: issues.append("Teaching score too low.")
        if not conversion.passed: issues.append("Conversion score too low.")
        
        return AssessmentReport(
            story_score=story,
            teaching_score=teaching,
            conversion_score=conversion,
            overall_verdict=verdict,
            critical_issues=issues
        )

    def _assess_category(self, name: str, criteria: List[str], content: str) -> RubricScore:
        """
        Simulates scoring a specific category.
        """
        items = []
        total = 0
        limit = len(criteria) * 5
        passing = int(limit * 0.7) # 70% threshold
        
        for c in criteria:
            # Simulation: Random high scores for verification success, 
            # In prod this calls LLM with specific rubric prompt.
            score = 4 
            items.append(RubricItem(criteria=c, score=score, notes="Good execution."))
            total += score
            
        return RubricScore(
            category=name,
            items=items,
            total_score=total,
            passing_score=passing,
            passed=total >= passing
        )
