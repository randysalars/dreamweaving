"""
Product State Management
Tracks the state of a product through the pipeline for resume capability.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class PhaseStatus:
    """Status of a single pipeline phase."""
    completed_at: Optional[str] = None
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        return self.completed_at is not None and self.success


@dataclass
class ProductState:
    """
    Tracks the complete state of a product through the pipeline.
    Enables resume capability and status reporting.
    """
    product_slug: str
    title: str
    topic: str = ""
    created_at: str = ""
    output_dir: str = ""
    
    # Phase tracking
    phases: Dict[str, Dict] = field(default_factory=dict)
    
    # Artifact paths
    artifacts: Dict[str, str] = field(default_factory=dict)
    
    # Configuration used
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Pipeline phases in order
    PIPELINE_PHASES = [
        "create",      # Generate prompts or content
        "responses",   # Antigravity responses received
        "compile",     # Compile PDF/audio/video
        "deploy",      # Deploy to SalarsNet
        "emails",      # Generate email sequences
        "social",      # Generate social posts
        "register",    # Register emails with SalarsNet
        "schedule"     # Schedule social to Buffer
    ]
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        # Initialize all phases
        for phase in self.PIPELINE_PHASES:
            if phase not in self.phases:
                self.phases[phase] = {"completed_at": None, "success": False, "metadata": {}}
    
    @classmethod
    def load(cls, product_dir: Path) -> Optional['ProductState']:
        """Load state from product directory."""
        state_file = product_dir / "product_state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                return cls(**data)
            except Exception as e:
                logger.warning(f"Could not load product state: {e}")
                return None
        return None
    
    @classmethod
    def create(cls, product_dir: Path, title: str, topic: str = "", **config) -> 'ProductState':
        """Create a new product state."""
        slug = title.replace(" ", "_").lower()
        state = cls(
            product_slug=slug,
            title=title,
            topic=topic,
            output_dir=str(product_dir),
            config=config
        )
        state.save(product_dir)
        return state
    
    def save(self, product_dir: Path = None):
        """Save state to product directory."""
        if product_dir is None:
            product_dir = Path(self.output_dir)
        product_dir.mkdir(parents=True, exist_ok=True)
        state_file = product_dir / "product_state.json"
        state_file.write_text(json.dumps(asdict(self), indent=2, default=str))
        logger.debug(f"Saved product state to {state_file}")
    
    def mark_complete(self, phase: str, success: bool = True, **metadata):
        """Mark a phase as complete."""
        if phase not in self.PIPELINE_PHASES:
            logger.warning(f"Unknown phase: {phase}")
        self.phases[phase] = {
            "completed_at": datetime.now().isoformat(),
            "success": success,
            "metadata": metadata
        }
        # Auto-save
        if self.output_dir:
            self.save(Path(self.output_dir))
    
    def is_complete(self, phase: str) -> bool:
        """Check if a phase is complete."""
        if phase not in self.phases:
            return False
        return self.phases[phase].get("success", False)
    
    def get_next_phase(self) -> Optional[str]:
        """Get the next incomplete phase."""
        for phase in self.PIPELINE_PHASES:
            if not self.is_complete(phase):
                return phase
        return None
    
    def get_status_summary(self) -> str:
        """Get a human-readable status summary."""
        lines = [
            f"Product: {self.title}",
            f"Slug: {self.product_slug}",
            f"Created: {self.created_at[:10] if self.created_at else 'Unknown'}",
            "",
            "Pipeline Status:",
        ]
        
        for phase in self.PIPELINE_PHASES:
            status = self.phases.get(phase, {})
            if status.get("success"):
                icon = "✅"
                time = status.get("completed_at", "")[:16].replace("T", " ")
            elif status.get("completed_at"):
                icon = "❌"
                time = "Failed"
            else:
                icon = "⏳"
                time = "Pending"
            
            phase_name = phase.replace("_", " ").title()
            lines.append(f"  {icon} {phase_name}: {time}")
        
        # Artifacts
        if self.artifacts:
            lines.append("")
            lines.append("Artifacts:")
            for name, path in self.artifacts.items():
                lines.append(f"  📄 {name}: {path}")
        
        # Next step
        next_phase = self.get_next_phase()
        if next_phase:
            lines.append("")
            lines.append(f"Next: Run `product-builder {next_phase} --product-dir {self.output_dir}`")
        else:
            lines.append("")
            lines.append("🎉 All phases complete!")
        
        return "\n".join(lines)
    
    def add_artifact(self, name: str, path: str):
        """Record an artifact path."""
        self.artifacts[name] = path
        if self.output_dir:
            self.save(Path(self.output_dir))


def get_product_state(product_dir: Path, create_if_missing: bool = False, 
                      title: str = None, topic: str = None) -> Optional[ProductState]:
    """
    Get or create product state for a directory.
    
    Args:
        product_dir: Path to product directory
        create_if_missing: Create new state if none exists
        title: Product title (required if creating)
        topic: Product topic (optional)
    
    Returns:
        ProductState or None if not found and not creating
    """
    state = ProductState.load(product_dir)
    if state is None and create_if_missing:
        if not title:
            raise ValueError("Title required when creating new product state")
        state = ProductState.create(product_dir, title, topic or "")
    return state
