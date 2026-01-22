"""
AI Detector Agent
Identifies and flags AI-sounding writing patterns.
"""

import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)


class AIDetector:
    """
    Detects common AI writing patterns and suggests fixes.
    """
    
    # Comprehensive list of AI tells
    AI_TELLS = [
        # Opening clichés
        ("in today's fast-paced world", "Cut or replace with specific context"),
        ("in the modern era", "Be specific about the timeframe"),
        ("in this day and age", "Delete or be specific"),
        
        # Transition padding
        ("it's important to note that", "Just state the fact"),
        ("it's worth mentioning that", "Just mention it"),
        ("it should be noted that", "Delete, just say it"),
        ("needless to say", "If needless, don't say it"),
        
        # Engagement phrases
        ("let's dive in", "Delete or use specific hook"),
        ("let's explore", "Delete or be specific"),
        ("without further ado", "Just begin"),
        ("let's get started", "Just start"),
        
        # Conclusion padding
        ("in conclusion", "Use specific summary or delete"),
        ("to summarize", "Just summarize"),
        ("as we've discussed", "Delete, reader knows"),
        ("to wrap up", "Just wrap up"),
        
        # Hedging overuse
        ("arguably", "Make the argument or don't"),
        ("it could be said that", "Say it or don't"),
        ("one might argue", "Make the argument"),
        
        # Corporate speak
        ("leverage", "Use 'use' instead"),
        ("utilize", "Use 'use' instead"),
        ("synergy", "Be specific about the benefit"),
        ("paradigm shift", "Describe the actual change"),
        
        # Placeholder phrases
        ("at the end of the day", "Be specific"),
        ("when all is said and done", "Delete"),
        ("for all intents and purposes", "Delete"),
        ("due to the fact that", "Use 'because'"),
        ("in order to", "Use 'to'"),
        ("the fact of the matter is", "Just state the fact"),
    ]
    
    def __init__(self):
        pass
    
    def analyze(self, content: str) -> Tuple[bool, List[dict]]:
        """
        Analyze content for AI patterns.
        
        Returns:
            Tuple of (passes, list of findings)
        """
        logger.info("🔍 AIDetector scanning for AI patterns...")
        
        findings = []
        content_lower = content.lower()
        
        for pattern, fix in self.AI_TELLS:
            count = content_lower.count(pattern.lower())
            if count > 0:
                findings.append({
                    "pattern": pattern,
                    "count": count,
                    "fix": fix
                })
        
        # Structural checks
        heading_only_sections = self._check_heading_density(content)
        if heading_only_sections:
            findings.append({
                "pattern": "Too many headings without emotional glue",
                "count": heading_only_sections,
                "fix": "Add transitional sentences between sections"
            })
        
        # Generic example check
        generic_examples = self._check_generic_examples(content)
        if generic_examples:
            findings.append({
                "pattern": "Generic examples detected",
                "count": len(generic_examples),
                "fix": f"Replace generic examples: {', '.join(generic_examples[:2])}"
            })
        
        passes = len(findings) <= 3  # Allow up to 3 minor issues
        
        if not passes:
            logger.warning(f"⚠️ AIDetector found {len(findings)} issues")
        else:
            logger.info("✅ AIDetector passed")
        
        return passes, findings
    
    def _check_heading_density(self, content: str) -> int:
        """Check for sections that are mostly headings with no bridging content."""
        lines = content.split('\n')
        heading_clusters = 0
        consecutive_headings = 0
        
        for line in lines:
            if line.strip().startswith('#'):
                consecutive_headings += 1
                if consecutive_headings >= 3:
                    heading_clusters += 1
            else:
                consecutive_headings = 0
        
        return heading_clusters
    
    def _check_generic_examples(self, content: str) -> List[str]:
        """Detect overly generic examples."""
        generic_patterns = [
            r"for example,\s*(imagine|let's say|suppose)",
            r"consider\s+a\s+(simple|typical|common)\s+example",
            r"think of\s+it\s+like",
        ]
        
        findings = []
        for pattern in generic_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            findings.extend(matches)
        
        return findings
    
    def clean(self, content: str) -> str:
        """
        Apply automatic fixes for egregious patterns.
        """
        cleaned = content
        
        # Direct replacements
        simple_fixes = [
            ("in order to", "to"),
            ("due to the fact that", "because"),
            ("utilize", "use"),
            ("leverage", "use"),
        ]
        
        for pattern, replacement in simple_fixes:
            cleaned = re.sub(
                rf'\b{re.escape(pattern)}\b', 
                replacement, 
                cleaned, 
                flags=re.IGNORECASE
            )
        
        return cleaned
