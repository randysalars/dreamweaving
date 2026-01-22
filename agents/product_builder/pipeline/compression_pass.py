"""
Compression Pass Agent
Reduces content by 10-20% without losing meaning.
Also generates executive summaries and quickstart guides.
"""

import logging
from pathlib import Path
from typing import Optional

from ..core.llm import LLMClient

logger = logging.getLogger(__name__)


class CompressionPass:
    """
    The final content optimization pass.
    
    - Compresses content by 10-20%
    - Generates "If you only read 20%" summary
    - Generates "30-minute quickstart" version
    """
    
    TARGET_REDUCTION = 0.15  # 15% reduction target
    
    def __init__(self, templates_dir: Path = None):
        self.llm = LLMClient()
        
    def compress(self, content: str) -> str:
        """
        Compress content by removing filler while preserving meaning.
        
        Args:
            content: Original content
            
        Returns:
            Compressed content (10-20% shorter)
        """
        if len(content) < 500:
            return content  # Too short to compress
        
        logger.info(f"🗜️ CompressionPass: Starting with {len(content)} chars")
        
        prompt = f"""
You are an expert editor tasked with COMPRESSING this content by 15%.

## Rules:
1. Remove filler words and phrases
2. Combine redundant sentences
3. Remove obvious statements
4. Keep ALL key insights and examples
5. Preserve the voice and rhythm
6. Do NOT add new content

## Content to Compress:
{content[:4000]}

## Output:
Return ONLY the compressed content. No commentary.
"""
        
        compressed = self.llm.generate(prompt, max_tokens=len(content) // 3)
        
        # Validate compression
        reduction = 1 - (len(compressed) / len(content))
        
        if 0.05 <= reduction <= 0.30:
            logger.info(f"✅ Compressed by {reduction:.0%}: {len(content)} → {len(compressed)} chars")
            return compressed
        else:
            logger.warning(f"⚠️ Compression failed ({reduction:.0%}), returning original")
            return content
    
    def generate_executive_summary(self, content: str, title: str) -> str:
        """
        Generate "If you only read 20%" summary.
        
        Args:
            content: Full product content
            title: Product title
            
        Returns:
            Executive summary (1-2 pages)
        """
        logger.info("📋 Generating executive summary...")
        
        prompt = f"""
Create an EXECUTIVE SUMMARY for "{title}".

This is the "If you only read 20%" version. Someone should get 80% of the value in 20% of the time.

## Full Content Sample:
{content[:6000]}

## Requirements:
1. Maximum 500 words
2. Include the 3-5 most critical insights
3. Include the single most important action step
4. Written in the same voice as the original
5. No fluff - every sentence earns its place

## Output:
Return the executive summary only.
"""
        
        summary = self.llm.generate(prompt, max_tokens=800)
        logger.info(f"✅ Executive summary: {len(summary)} chars")
        return summary
    
    def generate_quickstart(self, content: str, title: str) -> str:
        """
        Generate "30-minute quickstart" guide.
        
        Args:
            content: Full product content
            title: Product title
            
        Returns:
            Quickstart guide
        """
        logger.info("⚡ Generating quickstart guide...")
        
        prompt = f"""
Create a QUICKSTART GUIDE for "{title}".

This is for someone who has 30 minutes and wants their first win.

## Full Content Sample:
{content[:6000]}

## Requirements:
1. Maximum 300 words
2. Focus on ONE immediate action they can take
3. Promise a tangible result within 30 minutes
4. Skip all theory - pure action
5. Include exactly what to do, step by step

## Format:
# 30-Minute Quickstart: [Title]

**Your Goal:** [What they'll achieve]

**Step 1:** [Action]
**Step 2:** [Action]
**Step 3:** [Action]

**You'll Know It Worked When:** [Success marker]

## Output:
Return the quickstart guide only.
"""
        
        quickstart = self.llm.generate(prompt, max_tokens=500)
        logger.info(f"✅ Quickstart guide: {len(quickstart)} chars")
        return quickstart
