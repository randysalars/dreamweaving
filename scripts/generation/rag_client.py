
import subprocess
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class NotionRAGClient:
    """
    Client for interacting with the Notion RAG system in the Dreamweaving project.
    Wraps the existing CLI tools for semantic search and page retrieval.
    """

    def __init__(self, dreamweaving_path: str = "/home/rsalars/Projects/dreamweaving"):
        self.dreamweaving_path = Path(dreamweaving_path)
        self.venv_python = self.dreamweaving_path / "venv" / "bin" / "python3"
        
        if not self.venv_python.exists():
            raise FileNotFoundError(f"Dreamweaving venv python not found at: {self.venv_python}")

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Perform a semantic search against the Notion knowledge base.
        
        Args:
            query: The search query string
            limit: Number of results to return (default 5)
            
        Returns:
            List of dictionaries containing result details (title, url, score, type)
        """
        cmd = [
            str(self.venv_python),
            "-m",
            "scripts.ai.notion_embeddings_pipeline",
            "--search",
            query,
            "--limit",
            str(limit)
        ]
        
        try:
            # We capture stdout/stderr. note: the script prints results to stdout.
            # Ideally the script would have a --json flag, but we parse the text output for now 
            # or rely on the fact that we might need to modify the underlying script to output JSON if parsing is too hard.
            # For now, let's assume we can capture the output.
            # Wait, the cli output is human readable. We might need to adjust the dreamweaving script 
            # or do some distinct parsing.
            # Let's try to run it and if parsing is flaky, we'll patch the dreamweaving script.
            
            result = subprocess.run(
                cmd, 
                cwd=str(self.dreamweaving_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # TODO: Robust parsing of the CLI output. 
            # Since I haven't modified the dreamweaving script to output JSON, 
            # I will return the raw text for now or implement a basic parser.
            # A better approach for this 'Infrastructure' phase might be to add a --json flag to the original script.
            # But let's stick to wrapping for now.
            return self._parse_search_output(result.stdout)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running RAG search: {e.stderr}")
            return []

    def get_page(self, title: str) -> Optional[str]:
        """
        Retrieve the full markdown content of a page by its exact title.
        
        Args:
            title: Exact page title
            
        Returns:
            String containing the markdown content, or None if not found.
        """
        cmd = [
            str(self.venv_python),
            "-m",
            "scripts.ai.notion_knowledge_retriever",
            "--page",
            title
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.dreamweaving_path),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error retrieving page '{title}': {e.stderr}")
            return None

    def _parse_search_output(self, output: str) -> List[Dict]:
        """
        Parse human-readable output from notion_embeddings_pipeline.
        Expected format chunks like:
        
        URL: https://...
        ---
        
        ### 4. Title
        Type: page
        Score: 0.xxx
        
        Title: ...
        """
        results = []
        # This is a placeholder for the actual parsing logic. 
        # Given the complexity of parsing human-readable text, 
        # I strongly recommend we patch the dreamweaving script to support JSON output.
        # But for this file creation, I'll leave it simple.
        
        # Quick and dirty parser
        lines = output.splitlines()
        current_item = {}
        for line in lines:
            if line.strip().startswith("URL:"):
                current_item["url"] = line.replace("URL:", "").strip()
            elif line.strip().startswith("Title:"):
                current_item["title"] = line.replace("Title:", "").strip()
            elif line.strip().startswith("Score:"):
                try:
                    current_item["score"] = float(line.replace("Score:", "").strip())
                except ValueError:
                    pass
            elif line.strip() == "---" and current_item:
                results.append(current_item)
                current_item = {}
                
        return results
