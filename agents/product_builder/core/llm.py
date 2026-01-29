"""
LLM Client (Mock Mode Only)
Provides mock responses for testing and development.
Vertex AI has been removed - use Antigravity directly for LLM needs.
"""

import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env explicitly if not loaded
load_dotenv()


class LLMClient:
    """
    Mock LLM client for product builder.
    
    Vertex AI has been removed. This client provides useful mock responses
    for testing the product assembly pipeline without making API calls.
    
    For actual LLM generation, use Antigravity (Claude) directly.
    """
    
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = True  # Always mock mode now
        self.valid = True
        logger.info("✨ LLMClient initialized (Mock Mode - Vertex AI removed)")

    def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        """Generate mock response based on prompt patterns."""
        return self._get_mock_response(prompt)

    def _get_mock_response(self, prompt: str) -> str:
        """Return a contextual mock response for testing."""
        prompt_lower = prompt.lower()
        
        # JSON Structure requests
        if "json" in prompt_lower and "sections" in prompt_lower:
            return '''
```json
{
  "sections": [
    { "title": "Chapter Content", "north_star": "Comprehensive coverage of the topic." }
  ]
}
```
'''
        
        # Worksheet prompts
        if "worksheet" in prompt_lower:
            return '''
## Exercise: Self-Assessment

**Instructions:**
Complete the following reflection.

**1. What is your main goal?**
[_________________________________________________________________]

**2. What obstacles do you face?**
[_________________________________________________________________]

**Action Step:**
[ ] I have identified one immediate action.
'''

        # Audio script prompts
        if "spoken-word" in prompt_lower or "audio recording" in prompt_lower:
            return '''
## Audio Track

[PAUSE: 3 seconds]

**Narrator:**
Welcome. Take a deep breath.
You are here because you are ready for a shift.
Let's begin.
'''

        # Takeaway extraction
        if "extract" in prompt_lower and "takeaway" in prompt_lower:
            return "- Focus on the fundamentals.\n- Practice consistently.\n- Review and refine regularly."

        # Default fallback
        return '''
## Content Section

This section explores the core concepts and practical applications.
By understanding these principles, you gain the foundation for mastery.
'''
