"""
Prompt Interface for Antigravity-Native LLM Architecture.

This module provides the PromptInterface class that writes prompts to files
for Antigravity (the user's chat session) to respond to, rather than calling
an external LLM API.

The workflow is:
1. Pipeline calls write_prompt() → creates .prompt.md file
2. User/Antigravity reads the prompt and writes a .response.md file
3. Pipeline calls read_response() → returns the generated content
"""

import logging
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptInterface:
    """
    Antigravity-Native Prompt Interface.
    
    Instead of calling an external LLM, this class:
    1. Writes prompts to markdown files in a prompts/ directory.
    2. Reads responses from a responses/ directory.
    
    This allows Antigravity (the chat session) to generate content directly.
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the PromptInterface.
        
        Args:
            output_dir: The product output directory (e.g., products/my_product/output/)
        """
        self.output_dir = Path(output_dir)
        self.prompts_dir = self.output_dir / "prompts"
        self.responses_dir = self.output_dir / "responses"
        
        # Create directories
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        
        # Track pending prompts
        self.pending_prompts = []
        
        logger.info(f"✨ PromptInterface initialized (Antigravity-Native Mode)")
        logger.info(f"   Prompts: {self.prompts_dir}")
        logger.info(f"   Responses: {self.responses_dir}")
    
    def write_prompt(self, prompt: str, slug: str, metadata: Optional[dict] = None) -> Path:
        """
        Write a prompt to a file for Antigravity to respond to.
        
        Args:
            prompt: The full prompt text (including all context)
            slug: A unique identifier for this prompt (e.g., "chapter_01_foundation")
            metadata: Optional metadata about the prompt (agent role, chapter info, etc.)
        
        Returns:
            Path to the created prompt file
        """
        prompt_path = self.prompts_dir / f"{slug}.prompt.md"
        response_path = self.responses_dir / f"{slug}.response.md"
        
        # Build the prompt file content
        content = f"""# Prompt: {slug}
Generated: {datetime.now().isoformat()}

## Instructions for Antigravity

Read this prompt carefully and generate the requested content.
Write your response to: `{response_path}`

---

{prompt}

---

## Response Instructions

After generating your response:
1. Create the file: `{response_path}`
2. Write ONLY the generated content (no markdown wrappers unless requested).
3. Run `product-builder compile` to continue the pipeline.
"""
        
        # Write the prompt file
        prompt_path.write_text(content)
        
        # Track this pending prompt
        self.pending_prompts.append({
            "slug": slug,
            "prompt_path": str(prompt_path),
            "response_path": str(response_path),
            "metadata": metadata or {},
            "status": "pending"
        })
        
        logger.info(f"📝 Prompt written: {prompt_path}")
        
        return prompt_path
    
    def read_response(self, slug: str) -> Optional[str]:
        """
        Read a response file if it exists.
        
        Args:
            slug: The unique identifier for the prompt/response
        
        Returns:
            The response content, or None if not yet available
        """
        response_path = self.responses_dir / f"{slug}.response.md"
        
        if response_path.exists():
            content = response_path.read_text().strip()
            logger.info(f"✅ Response read: {response_path}")
            return content
        else:
            logger.warning(f"⏳ Response not yet available: {response_path}")
            return None
    
    def get_pending_prompts(self) -> list:
        """Return list of prompts awaiting responses."""
        pending = []
        for item in self.pending_prompts:
            response_path = Path(item["response_path"])
            if not response_path.exists():
                pending.append(item)
        return pending
    
    def save_manifest(self):
        """Save the prompt manifest for tracking."""
        manifest_path = self.prompts_dir / "manifest.json"
        manifest_path.write_text(json.dumps(self.pending_prompts, indent=2))
        logger.info(f"📋 Prompt manifest saved: {manifest_path}")
    
    def load_manifest(self) -> list:
        """Load the prompt manifest."""
        manifest_path = self.prompts_dir / "manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text())
        return []
    
    def all_responses_ready(self) -> bool:
        """Check if all responses have been provided."""
        manifest = self.load_manifest()
        for item in manifest:
            response_path = Path(item["response_path"])
            if not response_path.exists():
                return False
        return len(manifest) > 0


# Legacy LLMClient wrapper for backward compatibility
class LLMClient:
    """
    Legacy wrapper that delegates to PromptInterface or Mock mode.
    
    This class is kept for backward compatibility with existing code.
    In the new architecture, it will always use PromptInterface when
    generate_prompts_only mode is enabled.
    """
    
    def __init__(self, output_dir: Optional[Path] = None, generate_prompts_only: bool = False):
        self.generate_prompts_only = generate_prompts_only
        self.prompt_interface = None
        
        if generate_prompts_only and output_dir:
            self.prompt_interface = PromptInterface(output_dir)
            logger.info("✨ LLMClient: Delegating to PromptInterface (Antigravity-Native Mode)")
        else:
            # Fall back to mock mode for compatibility
            logger.info("✨ LLMClient: Mock mode (for testing/development)")
    
    def generate(self, prompt: str, slug: str = "default", max_tokens: int = 4000) -> str:
        """
        Generate content or write a prompt for Antigravity.
        
        In generate_prompts_only mode: Writes prompt to file, returns placeholder.
        In mock mode: Returns a mock response.
        """
        if self.prompt_interface:
            # Write prompt to file for Antigravity to respond
            prompt_path = self.prompt_interface.write_prompt(prompt, slug)
            return f"[AWAITING_ANTIGRAVITY_RESPONSE: {prompt_path}]"
        else:
            # Return mock response for testing
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """Return a minimal mock response for testing."""
        prompt_lower = prompt.lower()
        
        # JSON structure requests
        if "json" in prompt_lower and "sections" in prompt_lower:
            return '''{"sections": [{"title": "Chapter Content", "north_star": "Coverage"}]}'''
        
        # Default mock content
        return """
## Generated Content

This is placeholder content generated in mock mode.
To generate real content, use the `--generate-prompts-only` flag and respond as Antigravity.
"""
