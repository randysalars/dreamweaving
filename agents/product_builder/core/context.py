import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from ..schemas.blueprint import ProductBlueprint

class PipelineState(BaseModel):
    current_session: int = 0
    completed_chapters: list[str] = []
    last_chapter_summary: str = ""
    toc_hash: str = ""
    start_time: datetime = None
    last_updated: datetime = None

class ProductContext:
    """
    Manages the state of a Product Build across sessions.
    Persists data to the product's staging directory.
    """
    
    def __init__(self, product_slug: str, base_output_dir: str = "output/products"):
        self.slug = product_slug
        self.root_path = Path(base_output_dir) / product_slug
        self.staging_path = self.root_path / "staging"
        self.artifacts_path = self.root_path / "artifacts"
        
        self.blueprint: Optional[ProductBlueprint] = None
        self.state: PipelineState = PipelineState()
        self.glossary: Dict[str, str] = {}
        self.toc: list[str] = []
        
        self._ensure_dirs()
        self.load()

    def _ensure_dirs(self):
        self.staging_path.mkdir(parents=True, exist_ok=True)
        self.artifacts_path.mkdir(parents=True, exist_ok=True)
        (self.staging_path / "chapters").mkdir(exist_ok=True)
        (self.staging_path / "diagrams").mkdir(exist_ok=True)

    def load(self):
        """Load state from disk."""
        blueprint_path = self.root_path / "blueprint.yaml"
        if blueprint_path.exists():
            with open(blueprint_path, 'r') as f:
                data = yaml.safe_load(f)
                self.blueprint = ProductBlueprint(**data)
        
        state_path = self.staging_path / "state.json"
        if state_path.exists():
            with open(state_path, 'r') as f:
                self.state = PipelineState(**json.load(f))
                
        glossary_path = self.staging_path / "glossary.json"
        if glossary_path.exists():
            with open(glossary_path, 'r') as f:
                self.glossary = json.load(f)

    def save(self):
        """Persist state to disk."""
        if self.blueprint:
            with open(self.root_path / "blueprint.yaml", 'w') as f:
                # Dump with enum support if needed, generally model_dump is robust
                yaml.dump(self.blueprint.model_dump(mode='json'), f)
        
        self.state.last_updated = datetime.utcnow()
        if not self.state.start_time:
            self.state.start_time = self.state.last_updated
            
        with open(self.staging_path / "state.json", 'w') as f:
            json.dump(self.state.model_dump(mode='json'), f, indent=2)
            
        with open(self.staging_path / "glossary.json", 'w') as f:
            json.dump(self.glossary, f, indent=2)

    def update_chapter(self, chapter_id: str, content: str, summary: str):
        """Save chapter content and update state."""
        chapter_path = self.staging_path / "chapters" / f"{chapter_id}.mdx"
        with open(chapter_path, 'w') as f:
            f.write(content)
            
        if chapter_id not in self.state.completed_chapters:
            self.state.completed_chapters.append(chapter_id)
            
        self.state.last_chapter_summary = summary
        self.save()

    def get_session_context(self) -> str:
        """
        Returns a context string for the LLM for the current session.
        Includes Blueprint highlights, Glossary, and Last Summary.
        """
        if not self.blueprint:
            return "No blueprint loaded."
            
        context = []
        context.append(f"# Product Blueprint: {self.blueprint.title}")
        context.append(f"Promise: {self.blueprint.promise.headline}")
        context.append(f"Audience: {self.blueprint.promise.target_audience}")
        context.append(f"Voice Rules: {', '.join(self.blueprint.voice_rules)}")
        
        if self.state.last_chapter_summary:
            context.append(f"\n## Previous Chapter Summary\n{self.state.last_chapter_summary}")
            
        if self.glossary:
            context.append("\n## Glossary Terms")
    # Limit glossary context
            for term, defn in list(self.glossary.items())[:10]: 
                context.append(f"- {term}: {defn}")
                
        return "\n".join(context)
