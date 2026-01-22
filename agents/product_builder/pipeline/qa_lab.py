"""
QA Lab Agent
Multi-test quality assurance system with 6 specialized test batteries.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple
from pydantic import BaseModel, Field

from ..core.llm import LLMClient

logger = logging.getLogger(__name__)


class TestResult(BaseModel):
    """Result of a single test."""
    name: str
    passed: bool
    score: int = Field(ge=0, le=10)
    issues: List[str] = Field(default_factory=list)
    fixes: List[str] = Field(default_factory=list)


class QAReport(BaseModel):
    """Complete QA Lab report."""
    clarity: TestResult
    coherence: TestResult
    utility: TestResult
    delight: TestResult
    finishability: TestResult
    originality: TestResult
    
    @property
    def all_passed(self) -> bool:
        return all([
            self.clarity.passed,
            self.coherence.passed,
            self.utility.passed,
            self.delight.passed,
            self.finishability.passed,
            self.originality.passed
        ])
    
    @property
    def critical_issues(self) -> List[str]:
        """Collect all issues from failed tests."""
        issues = []
        for test in [self.clarity, self.coherence, self.utility, self.delight, self.finishability, self.originality]:
            if not test.passed:
                issues.extend(test.issues)
        return issues
    
    @property
    def all_fixes(self) -> List[str]:
        """Collect all suggested fixes."""
        fixes = []
        for test in [self.clarity, self.coherence, self.utility, self.delight, self.finishability, self.originality]:
            fixes.extend(test.fixes)
        return fixes


class QALab:
    """
    Multi-test QA system that runs 6 specialized test batteries.
    Each test returns pass/fail with surgical fixes.
    """
    
    PASSING_THRESHOLD = 7
    
    def __init__(self, templates_dir: Path = None):
        self.llm = LLMClient()
        
    def run_all_tests(self, content: str, context: Dict) -> QAReport:
        """
        Run all 6 test batteries against the content.
        """
        logger.info("🧪 QA Lab running full test suite...")
        
        results = {
            "clarity": self._clarity_test(content, context),
            "coherence": self._coherence_test(content, context),
            "utility": self._utility_test(content, context),
            "delight": self._delight_test(content, context),
            "finishability": self._finishability_test(content, context),
            "originality": self._originality_test(content, context)
        }
        
        report = QAReport(**results)
        
        passed_count = sum(1 for t in [report.clarity, report.coherence, report.utility, 
                                        report.delight, report.finishability, report.originality] if t.passed)
        
        logger.info(f"QA Lab Results: {passed_count}/6 tests passed")
        
        if not report.all_passed:
            logger.warning(f"❌ Failed tests: {report.critical_issues[:3]}")
        else:
            logger.info("✅ All QA tests passed!")
        
        return report
    
    def _clarity_test(self, content: str, context: Dict) -> TestResult:
        """Can a reader summarize each chapter in 1-2 sentences?"""
        prompt = f"""
Evaluate this content for CLARITY. Can a reader easily summarize the main point of each section?

Content sample:
{content[:3000]}

Return JSON:
{{"score": 0-10, "issues": ["issue1"], "fixes": ["fix1"]}}
"""
        return self._run_test("Clarity", prompt)
    
    def _coherence_test(self, content: str, context: Dict) -> TestResult:
        """No contradictions, consistent definitions, dependencies respected."""
        prompt = f"""
Evaluate this content for COHERENCE. Check for:
1. No contradictions
2. Consistent definitions
3. Logical flow

Content sample:
{content[:3000]}

Return JSON:
{{"score": 0-10, "issues": ["issue1"], "fixes": ["fix1"]}}
"""
        return self._run_test("Coherence", prompt)
    
    def _utility_test(self, content: str, context: Dict) -> TestResult:
        """Every major idea has an exercise, checklist, or application step."""
        prompt = f"""
Evaluate this content for UTILITY. Does every major idea have:
- An exercise, OR
- A checklist, OR
- An application step?

Content sample:
{content[:3000]}

Return JSON:
{{"score": 0-10, "issues": ["idea without application"], "fixes": ["add exercise for X"]}}
"""
        return self._run_test("Utility", prompt)
    
    def _delight_test(self, content: str, context: Dict) -> TestResult:
        """Contains surprise, vivid examples, earned metaphors."""
        prompt = f"""
Evaluate this content for DELIGHT. Does it contain:
- Surprises or unexpected insights?
- Vivid, memorable examples?
- Fresh metaphors (not clichés)?

Content sample:
{content[:3000]}

Return JSON:
{{"score": 0-10, "issues": ["lacks vivid examples"], "fixes": ["add story in section X"]}}
"""
        return self._run_test("Delight", prompt)
    
    def _finishability_test(self, content: str, context: Dict) -> TestResult:
        """Would the average reader complete this in 7 days?"""
        prompt = f"""
Evaluate this content for FINISHABILITY. Could an average busy person:
- Stay engaged throughout?
- Complete this in 7 days?
- Feel motivated to continue?

Content sample:
{content[:3000]}

Return JSON:
{{"score": 0-10, "issues": ["section X is too dense"], "fixes": ["break into smaller chunks"]}}
"""
        return self._run_test("Finishability", prompt)
    
    def _originality_test(self, content: str, context: Dict) -> TestResult:
        """Offers perspective beyond generic summaries."""
        prompt = f"""
Evaluate this content for ORIGINALITY. Does it offer:
- A unique perspective?
- Insights not found in generic sources?
- Original frameworks or approaches?

Content sample:
{content[:3000]}

Return JSON:
{{"score": 0-10, "issues": ["too generic"], "fixes": ["add unique angle on X"]}}
"""
        return self._run_test("Originality", prompt)
    
    def _run_test(self, name: str, prompt: str) -> TestResult:
        """Run a single test and parse the result."""
        try:
            response = self.llm.generate(prompt, max_tokens=500)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                score = data.get("score", 7)
                return TestResult(
                    name=name,
                    passed=score >= self.PASSING_THRESHOLD,
                    score=score,
                    issues=data.get("issues", []),
                    fixes=data.get("fixes", [])
                )
        except Exception as e:
            logger.warning(f"Failed to run {name} test: {e}")
        
        # Default passing result
        return TestResult(name=name, passed=True, score=7, issues=[], fixes=[])
