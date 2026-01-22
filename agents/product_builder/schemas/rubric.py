from typing import List, Dict
from pydantic import BaseModel, Field

class RubricItem(BaseModel):
    criteria: str
    score: int = Field(..., ge=0, le=10, description="0-10 score")
    notes: str

class RubricScore(BaseModel):
    category: str # "Story", "Teaching", "Conversion"
    items: List[RubricItem]
    total_score: int
    passing_score: int
    passed: bool

class AssessmentReport(BaseModel):
    story_score: RubricScore
    teaching_score: RubricScore
    conversion_score: RubricScore
    overall_verdict: str # "SHIP", "REVISE", "FAIL"
    critical_issues: List[str]
