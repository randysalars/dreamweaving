"""
Lesson Generator for SalarsNet Video Framework

Converts product content into lesson JSON blueprints that Remotion can render.
Automatically applies the 7-part universal video anatomy.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LearningRole(str, Enum):
    """Pedagogical purpose of a scene."""
    VISUAL_PREVIEW = "visual_preview"
    GOAL_STATEMENT = "goal_statement"
    INTRODUCE_VOCAB = "introduce_vocab"
    EXPLAIN_RULE = "explain_rule"
    CORE_EXPLANATION = "core_explanation"
    REINFORCE = "reinforce"
    GUIDED_PAUSE = "guided_pause"
    CHECK_UNDERSTANDING = "check_understanding"
    NEXT_PREVIEW = "next_preview"
    MOTIVATE = "motivate"


class Template(str, Enum):
    """Available Remotion templates."""
    VISUAL_PREVIEW = "VisualPreview"
    GOAL_STATEMENT = "GoalStatement"
    CORE_EXPLANATION = "CoreExplanation"
    REINFORCEMENT = "Reinforcement"
    GUIDED_PAUSE = "GuidedPause"
    MINI_CHECK = "MiniCheck"
    NEXT_LESSON_PREVIEW = "NextLessonPreview"
    EXPLAINER_DECK = "ExplainerDeck"
    DIAGRAM = "Diagram"
    INFOGRAPHIC = "Infographic"
    KINETIC_KEY_POINT = "KineticKeyPoint"


@dataclass
class Narration:
    """Narration specification for a scene."""
    text: str = ""
    voice_text: str = ""  # Optimized for TTS with pauses
    voice: str = "coqui_en_friendly_01"
    pace: float = 0.85  # Slow for ELL
    audio_path: str = ""


@dataclass
class Visual:
    """Visual element specification."""
    type: str  # icon, image, card, deck, diagram, quiz, text
    key: str = ""
    path: str = ""
    headline: str = ""
    subhead: str = ""
    bullets: List[str] = field(default_factory=list)
    example: str = ""
    prompt: str = ""  # For quiz
    choices: List[str] = field(default_factory=list)
    answer: str = ""


@dataclass
class Scene:
    """Individual scene in a lesson video."""
    id: str
    learning_role: str
    duration_sec: float
    template: str = ""
    narration: Optional[Narration] = None
    visuals: List[Visual] = field(default_factory=list)
    captions_enabled: bool = True
    captions_mode: str = "srt"


@dataclass
class LessonBlueprint:
    """Complete lesson video blueprint."""
    id: str
    title: str
    scenes: List[Scene] = field(default_factory=list)
    fps: int = 30
    resolution: str = "1920x1080"
    theme: str = "salars_clean_01"
    level: str = "beginner"
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            "video": {
                "id": self.id,
                "title": self.title,
                "fps": self.fps,
                "resolution": self.resolution,
                "theme": self.theme,
                "level": self.level
            },
            "scenes": [self._scene_to_dict(s) for s in self.scenes]
        }
    
    def _scene_to_dict(self, scene: Scene) -> Dict:
        result = {
            "id": scene.id,
            "learning_role": scene.learning_role,
            "duration_sec": scene.duration_sec,
            "template": scene.template,
            "captions": {
                "enabled": scene.captions_enabled,
                "mode": scene.captions_mode
            }
        }
        if scene.narration:
            result["narration"] = {
                "text": scene.narration.text,
                "voice_text": scene.narration.voice_text,
                "voice": scene.narration.voice,
                "pace": scene.narration.pace,
                "audio_path": scene.narration.audio_path
            }
        if scene.visuals:
            result["visuals"] = [asdict(v) for v in scene.visuals]
        return result
    
    def to_json(self, path: Path = None) -> str:
        """Export as JSON string, optionally to file."""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2)
        if path:
            path.write_text(json_str)
            logger.info(f"Wrote lesson blueprint to {path}")
        return json_str


class LessonGenerator:
    """
    Generates lesson blueprints from content.
    
    Applies the 7-part universal video anatomy automatically:
    1. Visual Preview (5-10 sec)
    2. Goal Statement (1 sentence)
    3. Core Explanation (2-4 min)
    4. Visual Reinforcement Loop
    5. Guided Pause (5-10 sec)
    6. Mini Check
    7. Next Preview
    """
    
    def __init__(
        self,
        default_pace: float = 0.85,
        max_explanation_duration: float = 240,  # 4 minutes
        default_theme: str = "salars_clean_01"
    ):
        self.default_pace = default_pace
        self.max_explanation_duration = max_explanation_duration
        self.default_theme = default_theme
    
    def generate_from_chapter(
        self,
        chapter_id: str,
        title: str,
        goal: str,
        content: str,
        keywords: List[str] = None,
        check_question: str = None,
        check_answer: str = None,
        next_preview: str = None,
        level: str = "beginner"
    ) -> LessonBlueprint:
        """
        Generate a complete lesson blueprint from chapter content.
        
        Args:
            chapter_id: Unique identifier for the lesson
            title: Lesson title
            goal: Single-sentence learning goal
            content: Main explanation content
            keywords: List of key terms to highlight
            check_question: Comprehension check question
            check_answer: Answer to check question
            next_preview: Preview text for next lesson
            level: Difficulty level
            
        Returns:
            LessonBlueprint ready for Remotion rendering
        """
        keywords = keywords or self._extract_keywords(content)
        
        blueprint = LessonBlueprint(
            id=chapter_id,
            title=title,
            level=level,
            theme=self.default_theme
        )
        
        # 1. Visual Preview
        blueprint.scenes.append(self._create_visual_preview(
            chapter_id, keywords[:3]
        ))
        
        # 2. Goal Statement
        blueprint.scenes.append(self._create_goal_statement(
            chapter_id, goal
        ))
        
        # 3. Core Explanation
        blueprint.scenes.append(self._create_core_explanation(
            chapter_id, content, keywords
        ))
        
        # 4. Reinforcement (optional based on content length)
        if len(content) > 500:
            blueprint.scenes.append(self._create_reinforcement(
                chapter_id, keywords
            ))
        
        # 5. Guided Pause
        blueprint.scenes.append(self._create_guided_pause(chapter_id))
        
        # 6. Mini Check
        if check_question:
            blueprint.scenes.append(self._create_mini_check(
                chapter_id, check_question, check_answer
            ))
        
        # 7. Next Preview
        if next_preview:
            blueprint.scenes.append(self._create_next_preview(
                chapter_id, next_preview
            ))
        
        return blueprint
    
    def _create_visual_preview(
        self, chapter_id: str, icons: List[str]
    ) -> Scene:
        """Create visual preview scene (5-10 sec, no narration)."""
        return Scene(
            id=f"{chapter_id}_s01_preview",
            learning_role=LearningRole.VISUAL_PREVIEW.value,
            template=Template.VISUAL_PREVIEW.value,
            duration_sec=6,
            visuals=[
                Visual(type="icon", key=icon) for icon in icons
            ],
            captions_enabled=False
        )
    
    def _create_goal_statement(self, chapter_id: str, goal: str) -> Scene:
        """Create goal statement scene."""
        return Scene(
            id=f"{chapter_id}_s02_goal",
            learning_role=LearningRole.GOAL_STATEMENT.value,
            template=Template.GOAL_STATEMENT.value,
            duration_sec=8,
            narration=Narration(
                text=goal,
                voice_text=goal,
                pace=self.default_pace
            ),
            visuals=[
                Visual(type="text", headline="Goal", subhead=goal)
            ]
        )
    
    def _create_core_explanation(
        self, chapter_id: str, content: str, keywords: List[str]
    ) -> Scene:
        """Create core explanation scene (2-4 min)."""
        # Estimate duration based on word count (~150 words/min at slow pace)
        word_count = len(content.split())
        duration = min(
            word_count / 100,  # ~100 words/min at 0.85x pace
            self.max_explanation_duration
        )
        
        return Scene(
            id=f"{chapter_id}_s03_explain",
            learning_role=LearningRole.CORE_EXPLANATION.value,
            template=Template.CORE_EXPLANATION.value,
            duration_sec=max(60, duration),  # Minimum 1 minute
            narration=Narration(
                text=content,
                voice_text=self._optimize_for_speech(content),
                pace=self.default_pace
            ),
            visuals=[
                Visual(
                    type="deck",
                    bullets=keywords
                )
            ]
        )
    
    def _create_reinforcement(
        self, chapter_id: str, keywords: List[str]
    ) -> Scene:
        """Create visual reinforcement scene."""
        return Scene(
            id=f"{chapter_id}_s04_reinforce",
            learning_role=LearningRole.REINFORCE.value,
            template=Template.REINFORCEMENT.value,
            duration_sec=30,
            visuals=[
                Visual(type="text", headline=kw) for kw in keywords[:5]
            ],
            captions_enabled=False
        )
    
    def _create_guided_pause(self, chapter_id: str) -> Scene:
        """Create guided pause scene (5-10 sec)."""
        return Scene(
            id=f"{chapter_id}_s05_pause",
            learning_role=LearningRole.GUIDED_PAUSE.value,
            template=Template.GUIDED_PAUSE.value,
            duration_sec=8,
            visuals=[
                Visual(type="text", headline="Pause. Think. Repeat.")
            ],
            captions_enabled=False
        )
    
    def _create_mini_check(
        self, chapter_id: str, question: str, answer: str
    ) -> Scene:
        """Create mini check scene."""
        return Scene(
            id=f"{chapter_id}_s06_check",
            learning_role=LearningRole.CHECK_UNDERSTANDING.value,
            template=Template.MINI_CHECK.value,
            duration_sec=20,
            narration=Narration(
                text=f"Mini check. {question}",
                voice_text=f"Mini check... {question}",
                pace=self.default_pace
            ),
            visuals=[
                Visual(
                    type="quiz",
                    prompt=question,
                    answer=answer
                )
            ]
        )
    
    def _create_next_preview(
        self, chapter_id: str, preview_text: str
    ) -> Scene:
        """Create next lesson preview scene."""
        return Scene(
            id=f"{chapter_id}_s07_next",
            learning_role=LearningRole.NEXT_PREVIEW.value,
            template=Template.NEXT_LESSON_PREVIEW.value,
            duration_sec=10,
            narration=Narration(
                text=preview_text,
                voice_text=preview_text,
                pace=self.default_pace
            ),
            visuals=[
                Visual(type="text", headline="Up Next", subhead=preview_text)
            ]
        )
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract key terms from content (simple heuristic)."""
        # Look for bold markers, capitalized terms, or repeated words
        words = re.findall(r'\b[A-Z][a-z]{3,}\b', content)
        # Deduplicate and limit
        seen = set()
        keywords = []
        for w in words:
            if w.lower() not in seen:
                seen.add(w.lower())
                keywords.append(w)
            if len(keywords) >= 7:
                break
        return keywords if keywords else ["concept", "example", "practice"]
    
    def _optimize_for_speech(self, text: str) -> str:
        """Convert narrative text to voice-optimized script."""
        # Add pauses after periods
        text = re.sub(r'\. ', '... ', text)
        # Add pauses after commas
        text = re.sub(r', ', '... ', text)
        return text


def generate_sample_lesson() -> LessonBlueprint:
    """Generate a sample lesson for testing."""
    generator = LessonGenerator()
    
    return generator.generate_from_chapter(
        chapter_id="ell-restaurant-lesson-01",
        title="Ordering Food: 3 Key Words",
        goal="In this lesson, you will learn three words for ordering food.",
        content="""
        Word one: Menu. A menu shows the food you can order. 
        When you arrive at a restaurant, you can ask: Can I see the menu?
        
        Word two: Order. To order means to ask for food or drinks.
        You can say: I would like to order, please.
        
        Word three: Pay. Pay means to give money for your food.
        At the end, you can ask: Can I pay now?
        """,
        keywords=["menu", "order", "pay"],
        check_question="Which word means the list of food?",
        check_answer="menu",
        next_preview="Next, you will practice a restaurant conversation.",
        level="A1"
    )


if __name__ == "__main__":
    # Generate sample and print
    blueprint = generate_sample_lesson()
    print(blueprint.to_json())
