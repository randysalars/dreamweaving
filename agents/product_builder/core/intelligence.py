import logging
from typing import List, Dict
from pydantic import BaseModel, Field

# Assuming the RAG client is available in scripts/generation or we wrap it
# We will use the NotionRAGClient we saw in scripts/generation/rag_client.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../')) # Add project root

from scripts.generation.rag_client import NotionRAGClient

logger = logging.getLogger(__name__)

class DemandSignal(BaseModel):
    topic: str
    evidence_score: float = Field(..., description="0.0 to 1.0 score of demand/interest")
    key_themes: List[str]
    missing_angles: List[str]
    raw_sources: List[Dict] = Field(default_factory=list)

class MarketResearchAgent:
    """
    Simulates market research by querying the Internal Knowledge Base (Notion RAG).
    It looks for 'hot spots' - topics with high density but potentially low structure.
    """
    
    def __init__(self):
        try:
            self.rag = NotionRAGClient()
        except Exception as e:
            logger.warning(f"RAG Client init failed: {e}. Functionality will be limited.")
            self.rag = None

    def analyze_topic(self, topic_query: str) -> DemandSignal:
        """
        Scans the knowledge base for a topic to see if we have enough
        'raw material' and 'interest' to build a product.
        """
        logger.info(f"Analyzing market demand for: {topic_query}")
        
        if not self.rag:
            return DemandSignal(topic=topic_query, evidence_score=0.0, key_themes=[], missing_angles=[])

        # 1. Search for core concepts
        results = self.rag.search(topic_query, limit=10)
        
        if not results:
            return DemandSignal(
                topic=topic_query, 
                evidence_score=0.1, 
                key_themes=["No internal data found"], 
                missing_angles=["Everything"]
            )

        # 2. Analyze density (Heuristic: more results with high relevance = high potential)
        avg_score = sum(r.get('score', 0) for r in results) / len(results) if results else 0
        
        # 3. Extract simulated themes (In a real LLM agent, we'd pass these snippets to an LLM to summarize)
        # For this infra implementation, we'll placeholder the extraction logic
        themes = [r.get('title') for r in results[:3]]
        
        return DemandSignal(
            topic=topic_query,
            evidence_score=min(avg_score * 2, 1.0), # Boost score slightly for potential
            key_themes=themes,
            missing_angles=["Actionable steps", "Systematic frameworks"], # Default assumptions for info products
            raw_sources=results
        )
