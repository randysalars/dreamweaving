"""
Library Manager
Provides semantic access to the Evergreen Knowledge Assets library.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class LibraryManager:
    """
    Manages the Evergreen Knowledge Assets library.
    Provides search and retrieval for reusable components.
    """
    
    def __init__(self, library_path: Path = None):
        if library_path is None:
            library_path = Path(__file__).parent.parent / "library"
        self.library_path = library_path
        self._cache: Dict[str, str] = {}
        
    def get_analogies(self, topic: str = None) -> List[Dict[str, str]]:
        """
        Get analogies from the analogies bank.
        
        Args:
            topic: Optional topic filter (e.g., "money", "habits")
            
        Returns:
            List of analogies with source and metaphor
        """
        content = self._load_file("analogies_bank.md")
        if not content:
            return []
        
        analogies = []
        current_section = ""
        
        for line in content.split("\n"):
            if line.startswith("## "):
                current_section = line[3:].strip()
            elif line.startswith("- **"):
                # Extract analogy
                match = re.match(r"- \*\*(.+?)\*\* → \"(.+?)\"", line)
                if match:
                    analogy = {
                        "concept": match.group(1),
                        "metaphor": match.group(2),
                        "category": current_section
                    }
                    
                    # Filter by topic if provided
                    if topic is None or topic.lower() in current_section.lower():
                        analogies.append(analogy)
        
        return analogies
    
    def get_objection_response(self, objection_type: str) -> Optional[Dict[str, str]]:
        """
        Get a prewritten response to an objection.
        
        Args:
            objection_type: Type like "time", "money", "skepticism"
            
        Returns:
            Dict with objection and response, or None
        """
        content = self._load_file("objections_library.md")
        if not content:
            return None
        
        objections = []
        current_category = ""
        current_objection = ""
        current_response = ""
        
        for line in content.split("\n"):
            if line.startswith("## "):
                current_category = line[3:].strip()
            elif line.startswith("### "):
                # Save previous if exists
                if current_objection and current_response:
                    objections.append({
                        "category": current_category,
                        "objection": current_objection,
                        "response": current_response.strip()
                    })
                current_objection = line[4:].strip().strip('"')
                current_response = ""
            elif line.startswith("**Response**:"):
                current_response = line[13:].strip()
            elif current_response and line.strip() and not line.startswith("#"):
                current_response += " " + line.strip()
        
        # Add last one
        if current_objection and current_response:
            objections.append({
                "category": current_category,
                "objection": current_objection,
                "response": current_response.strip()
            })
        
        # Filter by type
        for obj in objections:
            if objection_type.lower() in obj["category"].lower():
                return obj
        
        return objections[0] if objections else None
    
    def get_glossary_term(self, term: str) -> Optional[str]:
        """Get definition for a term from the glossary."""
        content = self._load_file("glossary.md")
        if not content:
            return None
        
        for line in content.split("\n"):
            if line.lower().startswith(f"**{term.lower()}**"):
                # Extract definition after the colon
                parts = line.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        return None
    
    def _load_file(self, filename: str) -> Optional[str]:
        """Load a file from the library with caching."""
        if filename in self._cache:
            return self._cache[filename]
        
        file_path = self.library_path / filename
        if file_path.exists():
            content = file_path.read_text()
            self._cache[filename] = content
            return content
        
        logger.warning(f"Library file not found: {filename}")
        return None
    
    def list_available_assets(self) -> Dict[str, bool]:
        """List which library assets are available."""
        assets = {
            "analogies_bank.md": False,
            "objections_library.md": False,
            "glossary.md": False,
            "frameworks_deck/": False,
            "exercises_library/": False
        }
        
        for asset in assets:
            path = self.library_path / asset
            assets[asset] = path.exists()
        
        return assets
