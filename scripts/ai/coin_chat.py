#!/usr/bin/env python3
"""
Coin Knowledge Chat Interface

A conversational AI assistant for rare coin buying decisions,
powered by the Salars.net coin RAG knowledge base.

Usage:
    # Interactive chat mode
    python3 -m scripts.ai.coin_chat

    # Single question mode
    python3 -m scripts.ai.coin_chat --ask "What's a good first Morgan dollar?"

    # Show available topics
    python3 -m scripts.ai.coin_chat --topics
"""

import os
import sys
import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
NOTION_EXPORT_DIR = KNOWLEDGE_DIR / "notion_export" / "pages"
COINS_DIR = KNOWLEDGE_DIR / "coins"

# Load .env for API keys
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

# Try Google Gemini first, then OpenAI
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


SYSTEM_PROMPT = """You are the Salars.net Coin Advisor, a knowledgeable and trustworthy guide for rare coin buying decisions.

Your personality:
- Calm, honest, and helpful
- You focus on decision-making, not just identification
- You help people buy the RIGHT coins for their situation
- You're transparent about what dealers don't always say
- You never push sales - you guide toward smart choices

Your expertise includes:
- Morgan and Peace silver dollars
- Junk silver / constitutional silver
- Coin storage and supplies
- Bullion vs numismatic value
- Buyer psychology and common mistakes
- When to buy vs when to wait

Guidelines:
1. Answer based on the provided knowledge context
2. If the context doesn't cover the question, say so honestly
3. Always consider the buyer's situation (budget, goals, experience)
4. Help reduce anxiety and build confidence
5. When relevant, mention specific categories like "Sleep-Well Coins" or "Learning Coins"
6. Keep responses conversational but substantive
7. If asked about specific products, guide toward the right decision criteria

Remember: You're a trusted advisor, not a salesperson."""


class CoinKnowledgeSearch:
    """
    Fallback search that works without Qdrant lock.
    Uses keyword-based search on markdown files.
    """
    
    def __init__(self):
        self.knowledge_files = self._load_knowledge_files()
    
    def _load_knowledge_files(self) -> Dict[str, str]:
        """Load all coin-related markdown files."""
        files = {}
        
        # Load from notion export
        if NOTION_EXPORT_DIR.exists():
            for md_file in NOTION_EXPORT_DIR.glob("*.md"):
                # Focus on coin-related files
                name_lower = md_file.name.lower()
                if any(kw in name_lower for kw in [
                    "coin", "silver", "morgan", "peace", "bullion", 
                    "junk", "buy", "supplies", "dealer", "rag dbase"
                ]):
                    try:
                        content = md_file.read_text()
                        files[md_file.stem] = content
                    except Exception:
                        pass
        
        # Load coin guides
        if COINS_DIR.exists():
            for yaml_file in COINS_DIR.glob("*.yaml"):
                try:
                    content = yaml_file.read_text()
                    files[f"yaml_{yaml_file.stem}"] = content
                except Exception:
                    pass
        
        return files
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Simple keyword-based search across knowledge files.
        """
        query_words = set(re.findall(r'\w+', query.lower()))
        
        # Score each file by keyword matches
        scored = []
        for title, content in self.knowledge_files.items():
            content_lower = content.lower()
            
            # Count keyword matches
            score = sum(2 for word in query_words if word in content_lower)
            
            # Bonus for exact phrase
            if query.lower() in content_lower:
                score += 10
            
            if score > 0:
                # Extract relevant snippet
                snippet = self._extract_snippet(content, query_words)
                scored.append({
                    "title": title.replace("_", " ").replace("-", " ").title(),
                    "text": snippet,
                    "score": min(score / 10, 1.0),  # Normalize to 0-1
                    "type": "markdown"
                })
        
        # Sort by score and return top results
        scored.sort(key=lambda x: -x["score"])
        return scored[:limit]
    
    def _extract_snippet(self, content: str, query_words: set, context_chars: int = 500) -> str:
        """Extract the most relevant snippet from content."""
        content_lower = content.lower()
        
        # Find the best position
        best_pos = 0
        best_density = 0
        
        for i in range(0, len(content) - 200, 100):
            chunk = content_lower[i:i+400]
            density = sum(1 for word in query_words if word in chunk)
            if density > best_density:
                best_density = density
                best_pos = i
        
        # Extract snippet around best position
        start = max(0, best_pos - 50)
        end = min(len(content), best_pos + context_chars)
        
        snippet = content[start:end].strip()
        
        # Clean up
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet


class CoinChatInterface:
    """Interactive chat interface for coin knowledge."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.rag = None
        self.fallback_search = None
        self.conversation_history: List[Dict[str, str]] = []
        self._init_search()
        self._init_llm()
    
    def _init_search(self):
        """Initialize search backend (RAG or fallback)."""
        # Try to use RAG first
        try:
            # Suppress warnings during import
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from scripts.ai.notion_embeddings_pipeline import NotionEmbeddingsPipeline
                self.rag = NotionEmbeddingsPipeline(quiet=True)
                if self.verbose:
                    print("Using Qdrant vector search")
        except Exception as e:
            if "already accessed" in str(e) or "locked" in str(e).lower():
                if self.verbose:
                    print("Qdrant database locked, using keyword search fallback")
            else:
                if self.verbose:
                    print(f"Qdrant unavailable ({e}), using keyword search")
            
            # Fall back to keyword search
            self.fallback_search = CoinKnowledgeSearch()
    
    def _init_llm(self):
        """Initialize the LLM backend."""
        if HAS_GEMINI and os.environ.get("GOOGLE_API_KEY"):
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.llm_backend = "gemini"
            if self.verbose:
                print("Using Google Gemini")
        elif HAS_OPENAI and os.environ.get("OPENAI_API_KEY"):
            self.openai = OpenAI()
            self.llm_backend = "openai"
            if self.verbose:
                print("Using OpenAI")
        else:
            raise RuntimeError(
                "No LLM API available. Set GOOGLE_API_KEY or OPENAI_API_KEY."
            )
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """Search the RAG for relevant coin knowledge."""
        if self.rag:
            try:
                results = self.rag.search(query, limit=limit, score_threshold=0.3)
            except Exception as e:
                if self.verbose:
                    print(f"RAG search failed: {e}")
                # Fall back to keyword search
                if not self.fallback_search:
                    self.fallback_search = CoinKnowledgeSearch()
                results = self.fallback_search.search(query, limit=limit)
        else:
            results = self.fallback_search.search(query, limit=limit)
        
        # Filter for coin-related content
        coin_keywords = [
            "coin", "silver", "morgan", "peace", "dollar", "bullion",
            "junk", "numismatic", "buy", "collect", "flip", "capsule",
            "storage", "supplies", "dealer", "grade", "circulated",
            "Sleep-Well", "Learning Coin", "random date"
        ]
        
        # Prioritize coin-related results
        scored_results = []
        for r in results:
            text_lower = (r.get("text", "") + r.get("title", "")).lower()
            coin_score = sum(1 for kw in coin_keywords if kw.lower() in text_lower)
            scored_results.append((coin_score, r))
        
        # Sort by coin relevance, then by original score
        scored_results.sort(key=lambda x: (-x[0], -x[1].get("score", 0)))
        
        return [r for _, r in scored_results]
    
    def build_context(self, results: List[Dict]) -> str:
        """Build context string from search results."""
        if not results:
            return "No specific knowledge found for this query."
        
        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Unknown")
            text = r.get("text", "").strip()
            score = r.get("score", 0)
            
            # Truncate long texts
            if len(text) > 1500:
                text = text[:1500] + "..."
            
            context_parts.append(
                f"[Source {i}: {title}]\n{text}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def generate_response(self, user_query: str, context: str) -> str:
        """Generate a response using the LLM."""
        # Build messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Based on the following knowledge from Salars.net's coin expertise:

{context}

---

User Question: {user_query}

Please provide a helpful, conversational response. If the knowledge doesn't fully answer the question, acknowledge that and share what you can."""}
        ]
        
        if self.llm_backend == "gemini":
            # Gemini uses a different format
            prompt = f"{SYSTEM_PROMPT}\n\n---\n\nKnowledge Context:\n{context}\n\n---\n\nUser: {user_query}\n\nAssistant:"
            response = self.model.generate_content(prompt)
            return response.text
        else:
            # OpenAI format
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question and get a response with sources.
        
        Returns:
            Dict with 'response', 'sources', and 'query'
        """
        # Search for relevant knowledge
        results = self.search_knowledge(question)
        context = self.build_context(results)
        
        if self.verbose:
            print(f"\n🔍 Found {len(results)} relevant sources")
        
        # Generate response
        response = self.generate_response(question, context)
        
        # Track conversation
        self.conversation_history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "sources": [r.get("title", "") for r in results[:3]],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response,
            "sources": [
                {"title": r.get("title", ""), "score": r.get("score", 0)}
                for r in results[:3]
            ],
            "query": question
        }
    
    def chat_loop(self):
        """Run interactive chat loop."""
        print("\n" + "="*60)
        print("🪙  Salars.net Coin Advisor")
        print("="*60)
        print("Ask me anything about buying rare coins, silver, storage,")
        print("or making smart collecting decisions.")
        print("\nType 'quit' to exit, 'clear' to reset conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nGoodbye! Happy collecting. 🪙")
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ("quit", "exit", "q"):
                print("\nGoodbye! Happy collecting. 🪙")
                break
            
            if user_input.lower() == "clear":
                self.conversation_history = []
                print("\n[Conversation cleared]\n")
                continue
            
            if user_input.lower() == "sources":
                if self.conversation_history:
                    last = self.conversation_history[-1]
                    if "sources" in last:
                        print("\nSources from last response:")
                        for s in last["sources"]:
                            print(f"  • {s}")
                        print()
                continue
            
            print("\n🪙 Coin Advisor: ", end="", flush=True)
            
            try:
                result = self.ask(user_input)
                print(result["response"])
                
                # Show sources hint
                if result["sources"]:
                    sources_str = ", ".join(
                        s["title"][:40] + "..." if len(s["title"]) > 40 else s["title"]
                        for s in result["sources"][:2]
                    )
                    print(f"\n  📚 Sources: {sources_str}")
                print()
                
            except Exception as e:
                print(f"\n[Error: {e}]\n")
    
    def get_topics(self) -> List[str]:
        """Get list of available knowledge topics."""
        if self.fallback_search:
            return sorted([
                title for title in self.fallback_search.knowledge_files.keys()
                if len(title) < 80
            ])[:20]
        
        # Sample queries to find topic areas
        test_queries = [
            "Morgan dollar buying guide",
            "coin storage supplies",
            "junk silver",
            "buying confidence",
            "sleep well coins",
            "dealer transparency"
        ]
        
        topics = set()
        for query in test_queries:
            results = self.search_knowledge(query, limit=3)
            for r in results:
                title = r.get("title", "")
                if title and len(title) < 80:
                    topics.add(title)
        
        return sorted(topics)


def main():
    parser = argparse.ArgumentParser(
        description="Chat with the Salars.net coin knowledge base"
    )
    parser.add_argument(
        "--ask", "-a",
        type=str,
        help="Ask a single question (non-interactive)"
    )
    parser.add_argument(
        "--topics", "-t",
        action="store_true",
        help="Show available topics in the knowledge base"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show debug information"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format (with --ask)"
    )
    
    args = parser.parse_args()
    
    try:
        chat = CoinChatInterface(verbose=args.verbose)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if args.topics:
        topics = chat.get_topics()
        print("\n📚 Available Coin Knowledge Topics:\n")
        for topic in topics:
            print(f"  • {topic}")
        print()
        return
    
    if args.ask:
        result = chat.ask(args.ask)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n🪙 Coin Advisor:\n{result['response']}")
            if result["sources"]:
                print("\n📚 Sources:")
                for s in result["sources"]:
                    print(f"  • {s['title']} (relevance: {s['score']:.2f})")
            print()
        return
    
    # Interactive mode
    chat.chat_loop()


if __name__ == "__main__":
    main()
