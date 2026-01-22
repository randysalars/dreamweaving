from pathlib import Path
from ..schemas.rubric import RubricScore, RubricItem, AssessmentReport
from ..core.llm import LLMClient
from typing import List
import logging

logger = logging.getLogger(__name__)

class RubricGuard:
    """
    Quality Assurance Agent.
    Evaluates content against 3 axes: Story, Teaching, Conversion.
    Enforces minimum quality standards using Real LLM evaluation.
    """
    
    def __init__(self):
        # Locate templates relative to this file
        # This file is in agents/product_builder/pipeline/
        # Templates are in agents/product_builder/templates/
        self.templates_dir = Path(__file__).resolve().parents[1] / "templates"
        self.llm = LLMClient()
        
    def evaluate(self, content: str) -> AssessmentReport:
        """
        Runs the 3 assessments.
        """
        logger.info("Running Rubric Quality Gate (Real Intelligence)...")
        
        # 1. Story Rubric
        logger.info(" assessing Story...")
        story = self._assess_category(
            "Story",
            [
                "Hook Strength: Does it grab attention immediately?", 
                "Emotional Movement: Does the reader feel something?", 
                "Coherence: Does the narrative flow logically?", 
                "Memorability: Is there a sticky concept?", 
                "Momentum: Does it drive the reader forward?"
            ],
            content
        )
        
        # 2. Teaching Rubric
        logger.info(" assessing Teaching...")
        teaching = self._assess_category(
            "Teaching",
            [
                "Clarity: Is the concept explained simply?", 
                "Worked Examples: Are there concrete examples?", 
                "Practice Quality: Is it actionable?", 
                "Misconception Coverage: Does it address common errors?", 
                "Transfer to Life: Can the reader use this?"
            ],
            content
        )
        
        # 3. Conversion Rubric
        logger.info(" assessing Conversion...")
        conversion = self._assess_category(
            "Conversion",
            [
                "Promise Clarity: Is the benefit clear?", 
                "Objection Handling: Does it address doubts?", 
                "Credibility: Does it build trust?", 
                "Offer Stack: Is the value proposition strong?", 
                "CTA Strength: Is the next step clear?"
            ],
            content
        )
        
        # Verdict Logic
        failed = not (story.passed and teaching.passed and conversion.passed)
        verdict = "REVISE" if failed else "SHIP"
        
        issues = []
        if not story.passed: issues.append(f"Story Failed ({story.total_score}/10): {self._extract_critique_summary(story)}")
        if not teaching.passed: issues.append(f"Teaching Failed ({teaching.total_score}/10): {self._extract_critique_summary(teaching)}")
        if not conversion.passed: issues.append(f"Conversion Failed ({conversion.total_score}/10): {self._extract_critique_summary(conversion)}")
        
        return AssessmentReport(
            story_score=story,
            teaching_score=teaching,
            conversion_score=conversion,
            overall_verdict=verdict,
            critical_issues=issues
        )

    def _assess_category(self, name: str, criteria: List[str], content: str) -> RubricScore:
        """
        Calls LLM to score a category.
        """
        template_path = self.templates_dir / "rubric_scoring.md"
        if not template_path.exists():
            logger.error(f"Rubric template not found at {template_path}")
            return self._fallback_score(name, criteria)

        with open(template_path, 'r') as f:
            template = f.read()
            
        context = {
            "category_name": name,
            "criteria_list": "\n- ".join(criteria),
            "content": content
        }
        
        prompt = template.format(**context)
        response = self.llm.generate(prompt)
        
        return self._parse_llm_response(name, criteria, response)

    def _parse_llm_response(self, name: str, criteria: List[str], response: str) -> RubricScore:
        """
        Parses the structured output from the LLM.
        Expected format:
        CRITIQUE: ...
        SCORE: X
        VERDICT: PASS/FAIL
        CRITICAL_ISSUES: ...
        """
        score = 0
        verdict = "FAIL"
        critique = "Parse error"
        
        try:
            lines = response.splitlines()
            for line in lines:
                if line.startswith("SCORE:"):
                    raw_score = line.split("SCORE:")[1].strip()
                    # Handle cases like "7/10"
                    score = int(raw_score.split("/")[0].strip())
                elif line.startswith("VERDICT:"):
                    verdict = line.split("VERDICT:")[1].strip().upper()
                elif line.startswith("CRITIQUE:"):
                    critique = line.split("CRITIQUE:")[1].strip()
                    
        except Exception as e:
            logger.error(f"Failed to parse rubric response: {e}")
            logger.debug(f"Raw Response: {response}")
            
        # Passing threshold is 7
        passed = score >= 7
        if verdict == "PASS" and score < 7: passed = True # Trust LLM verdict if explicit
        if verdict == "FAIL": passed = False
            
        # Create a single summary item since we get an aggregate score from this simple prompt
        items = [
            RubricItem(
                criteria="Overall Category Performance", 
                score=score, 
                notes=critique
            )
        ]
            
        return RubricScore(
            category=name,
            items=items,
            total_score=score,
            passing_score=7,
            passed=passed
        )

    def _extract_critique_summary(self, score: RubricScore) -> str:
        if score.items:
            return score.items[0].notes
        return "Low score."

    def _fallback_score(self, name: str, criteria: List[str]) -> RubricScore:
        """Fallback in case of template error"""
        return RubricScore(
            category=name,
            items=[],
            total_score=0,
            passing_score=7,
            passed=False
        )
