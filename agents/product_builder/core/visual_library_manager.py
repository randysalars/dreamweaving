"""
Visual Library Manager
Manages reusable visual assets for consistent product aesthetics.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)


class VisualAsset:
    """Represents a reusable visual asset."""
    def __init__(self, path: Path, metadata: Dict):
        self.path = path
        self.name = metadata.get("name", path.stem)
        self.category = metadata.get("category", "uncategorized")
        self.tags = metadata.get("tags", [])
        self.usage_count = metadata.get("usage_count", 0)
        self.style = metadata.get("style", "default")
        self.description = metadata.get("description", "")
    
    def to_dict(self) -> Dict:
        return {
            "path": str(self.path),
            "name": self.name,
            "category": self.category,
            "tags": self.tags,
            "usage_count": self.usage_count,
            "style": self.style,
            "description": self.description
        }


class VisualLibraryManager:
    """
    Manages the visual assets library.
    Provides search, retrieval, and usage tracking.
    """
    
    def __init__(self, library_path: Path = None):
        if library_path is None:
            library_path = Path(__file__).parent.parent / "library"
        self.library_path = library_path
        self._index: Dict[str, VisualAsset] = {}
        self._load_index()
    
    def _load_index(self):
        """Load or build the asset index."""
        index_path = self.library_path / "visual_index.json"
        
        if index_path.exists():
            try:
                data = json.loads(index_path.read_text())
                for asset_data in data.get("assets", []):
                    asset = VisualAsset(
                        Path(asset_data["path"]),
                        asset_data
                    )
                    self._index[asset.name] = asset
                logger.info(f"Loaded {len(self._index)} visual assets")
            except Exception as e:
                logger.warning(f"Failed to load visual index: {e}")
        else:
            self._build_index()
    
    def _build_index(self):
        """Build index from filesystem."""
        categories = [
            ("icons/navigation", "icon"),
            ("icons/concepts", "icon"),
            ("diagrams/frameworks", "diagram"),
            ("diagrams/processes", "diagram"),
            ("illustrations/metaphors", "illustration"),
            ("illustrations/section_headers", "illustration"),
            ("callout_templates", "template")
        ]
        
        for subdir, category in categories:
            dir_path = self.library_path / subdir
            if dir_path.exists():
                for file_path in dir_path.iterdir():
                    if file_path.suffix.lower() in [".png", ".svg", ".jpg", ".mmd"]:
                        asset = VisualAsset(file_path, {
                            "name": file_path.stem,
                            "category": category,
                            "tags": [subdir.split("/")[-1]],
                            "style": "default"
                        })
                        self._index[asset.name] = asset
        
        logger.info(f"Built index with {len(self._index)} assets")
    
    def save_index(self):
        """Save the current index to disk."""
        index_path = self.library_path / "visual_index.json"
        data = {
            "assets": [asset.to_dict() for asset in self._index.values()]
        }
        index_path.write_text(json.dumps(data, indent=2))
    
    def find_by_category(self, category: str) -> List[VisualAsset]:
        """Find all assets in a category."""
        return [a for a in self._index.values() if a.category == category]
    
    def find_by_tags(self, tags: List[str]) -> List[VisualAsset]:
        """Find assets matching any of the given tags."""
        return [
            a for a in self._index.values() 
            if any(t in a.tags for t in tags)
        ]
    
    def find_by_style(self, style: str) -> List[VisualAsset]:
        """Find assets matching a visual style."""
        return [a for a in self._index.values() if a.style == style]
    
    def get_asset(self, name: str) -> Optional[VisualAsset]:
        """Get a specific asset by name."""
        return self._index.get(name)
    
    def record_usage(self, name: str):
        """Record that an asset was used (for analytics)."""
        if name in self._index:
            self._index[name].usage_count += 1
    
    def suggest_for_intent(self, intent_type: str, description: str) -> List[VisualAsset]:
        """
        Suggest existing assets that might match a visual intent.
        
        Args:
            intent_type: Type like "metaphor_illustration", "concept_diagram"
            description: Description of what's needed
            
        Returns:
            List of potentially matching assets
        """
        # Map intent types to categories
        type_to_category = {
            "metaphor_illustration": "illustration",
            "concept_diagram": "diagram",
            "map_overview": "diagram",
            "callout": "template",
            "reference_graphic": "template",
            "icon_decoration": "icon"
        }
        
        category = type_to_category.get(intent_type, "illustration")
        matches = self.find_by_category(category)
        
        # Simple keyword matching on description
        keywords = description.lower().split()
        scored = []
        for asset in matches:
            score = sum(1 for kw in keywords if kw in asset.name.lower() or kw in " ".join(asset.tags).lower())
            if score > 0:
                scored.append((asset, score))
        
        # Return top matches
        scored.sort(key=lambda x: x[1], reverse=True)
        return [a for a, _ in scored[:5]]
    
    def get_least_used(self, category: str, limit: int = 5) -> List[VisualAsset]:
        """Get least-used assets in a category (for variety)."""
        assets = self.find_by_category(category)
        assets.sort(key=lambda a: a.usage_count)
        return assets[:limit]
    
    def list_available_styles(self) -> List[str]:
        """List all visual styles with assets."""
        styles_dir = self.library_path / "visual_styles"
        if styles_dir.exists():
            return [f.stem for f in styles_dir.glob("*.json")]
        return []
