#!/usr/bin/env python3
"""
Automatic RAG synchronization script.
Exports Notion content and re-indexes vector database.

Usage:
    python3 scripts/ai/rag_auto_sync.py              # Full sync
    python3 scripts/ai/rag_auto_sync.py --check-only # Check for changes without indexing
    python3 scripts/ai/rag_auto_sync.py --force      # Force full re-index

Part of Phase 8: Automatic RAG Indexing System
"""
import os
import sys
import hashlib
import json
import logging
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGAutoSync:
    """Automatic RAG synchronization manager."""

    def __init__(self, export_dir: str = "knowledge/notion_export"):
        self.export_dir = PROJECT_ROOT / export_dir
        self.state_file = self.export_dir / ".sync_state.json"
        self.config_path = PROJECT_ROOT / "config" / "notion_config.yaml"
        self.logs_dir = PROJECT_ROOT / "logs"

        # Ensure directories exist
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Lazy load components
        self._retriever = None
        self._pipeline = None

    @property
    def retriever(self):
        """Lazy load NotionKnowledgeRetriever."""
        if self._retriever is None:
            try:
                from scripts.ai.notion_knowledge_retriever import NotionKnowledgeRetriever
                self._retriever = NotionKnowledgeRetriever()
            except ImportError as e:
                logger.error(f"Failed to import NotionKnowledgeRetriever: {e}")
                raise
        return self._retriever

    @property
    def pipeline(self):
        """Lazy load NotionEmbeddingsPipeline."""
        if self._pipeline is None:
            try:
                from scripts.ai.notion_embeddings_pipeline import NotionEmbeddingsPipeline
                self._pipeline = NotionEmbeddingsPipeline()
            except ImportError as e:
                logger.error(f"Failed to import NotionEmbeddingsPipeline: {e}")
                raise
        return self._pipeline

    def load_config(self) -> Dict[str, Any]:
        """Load sync configuration from notion_config.yaml."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                return config.get("sync", {})
        return {}

    def get_content_hash(self) -> str:
        """Calculate hash of all exported content for change detection."""
        hasher = hashlib.md5()

        md_files = sorted(self.export_dir.glob("**/*.md"))

        for md_file in md_files:
            try:
                hasher.update(md_file.read_bytes())
            except Exception as e:
                logger.warning(f"Failed to hash {md_file}: {e}")

        return hasher.hexdigest()

    def load_state(self) -> Dict[str, Any]:
        """Load previous sync state."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Failed to parse sync state, starting fresh")
        return {}

    def save_state(self, content_hash: str, stats: Dict[str, Any]):
        """Save sync state for future comparisons."""
        state = {
            "last_sync": datetime.now().isoformat(),
            "content_hash": content_hash,
            "pages_count": stats.get("pages", 0),
            "vectors_count": stats.get("vectors", 0)
        }
        self.state_file.write_text(json.dumps(state, indent=2))
        logger.info(f"Sync state saved to {self.state_file}")

    def export_notion_content(self) -> bool:
        """Export latest content from Notion."""
        try:
            logger.info("Exporting Notion content...")
            self.retriever.export_all_content(str(self.export_dir))
            return True
        except Exception as e:
            logger.error(f"Notion export failed: {e}")
            return False

    def check_for_changes(self) -> bool:
        """Check if content has changed since last sync."""
        old_state = self.load_state()
        old_hash = old_state.get("content_hash", "")

        # Export latest content first
        if not self.export_notion_content():
            logger.error("Cannot check for changes - export failed")
            return False

        new_hash = self.get_content_hash()

        if new_hash != old_hash:
            logger.info(f"Content changed: {old_hash[:8] if old_hash else 'none'}... -> {new_hash[:8]}...")
            return True

        logger.info("No content changes detected.")
        return False

    def reindex_vectors(self) -> Dict[str, Any]:
        """Re-index all content in vector database."""
        try:
            logger.info("Re-indexing vector database...")
            self.pipeline.index_all_content()
            return self.pipeline.get_stats()
        except Exception as e:
            logger.error(f"Re-indexing failed: {e}")
            return {"error": str(e)}

    def sync(self, force: bool = False) -> Dict[str, Any]:
        """
        Perform full RAG sync.

        Args:
            force: If True, re-index even if no changes detected.

        Returns:
            Sync statistics.
        """
        logger.info("=" * 60)
        logger.info("RAG AUTO-SYNC STARTING")
        logger.info(f"Export directory: {self.export_dir}")
        logger.info(f"Force mode: {force}")
        logger.info("=" * 60)

        start_time = datetime.now()

        # Check for changes (this also exports content)
        has_changes = self.check_for_changes()

        if not has_changes and not force:
            logger.info("Skipping re-index (no changes). Use --force to override.")
            return {
                "status": "skipped",
                "reason": "no_changes",
                "timestamp": datetime.now().isoformat()
            }

        # Re-index vectors
        stats = self.reindex_vectors()

        if "error" in stats:
            return {
                "status": "failed",
                "error": stats["error"],
                "timestamp": datetime.now().isoformat()
            }

        # Calculate content hash and save state
        content_hash = self.get_content_hash()
        self.save_state(content_hash, stats)

        duration = (datetime.now() - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info(f"SYNC COMPLETE in {duration:.1f}s")
        logger.info(f"Pages: {stats.get('pages', 'N/A')}")
        logger.info(f"Vectors: {stats.get('vectors', 'N/A')}")
        logger.info("=" * 60)

        return {
            "status": "completed",
            "pages": stats.get("pages", 0),
            "vectors": stats.get("vectors", 0),
            "duration_seconds": duration,
            "content_hash": content_hash,
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        state = self.load_state()
        config = self.load_config()

        # Count current files
        md_files = list(self.export_dir.glob("**/*.md"))

        return {
            "last_sync": state.get("last_sync", "Never"),
            "last_hash": state.get("content_hash", "N/A")[:16] + "...",
            "pages_indexed": state.get("pages_count", 0),
            "vectors_indexed": state.get("vectors_count", 0),
            "current_files": len(md_files),
            "auto_sync_enabled": config.get("auto_sync", False),
            "sync_interval_hours": config.get("sync_interval_hours", 24)
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Automatic RAG synchronization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/ai/rag_auto_sync.py              # Full sync (checks changes first)
  python3 scripts/ai/rag_auto_sync.py --force      # Force full re-index
  python3 scripts/ai/rag_auto_sync.py --check-only # Check for changes only
  python3 scripts/ai/rag_auto_sync.py --status     # Show sync status
        """
    )
    parser.add_argument("--check-only", action="store_true",
                        help="Check for changes without re-indexing")
    parser.add_argument("--force", action="store_true",
                        help="Force full re-index even if no changes")
    parser.add_argument("--status", action="store_true",
                        help="Show current sync status")
    parser.add_argument("--export-dir", default="knowledge/notion_export",
                        help="Notion export directory (default: knowledge/notion_export)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    syncer = RAGAutoSync(export_dir=args.export_dir)

    try:
        if args.status:
            result = syncer.get_status()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print("\n📊 RAG Sync Status")
                print("=" * 40)
                for key, value in result.items():
                    print(f"  {key}: {value}")
                print()
        elif args.check_only:
            has_changes = syncer.check_for_changes()
            result = {"has_changes": has_changes}
            if args.json:
                print(json.dumps(result))
            else:
                if has_changes:
                    print("✅ Changes detected - re-indexing recommended")
                else:
                    print("✨ No changes detected")
            sys.exit(0 if has_changes else 1)
        else:
            result = syncer.sync(force=args.force)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["status"] == "completed":
                    print(f"\n✅ Sync completed successfully!")
                    print(f"   Pages: {result.get('pages', 0)}")
                    print(f"   Vectors: {result.get('vectors', 0)}")
                    print(f"   Duration: {result.get('duration_seconds', 0):.1f}s")
                elif result["status"] == "skipped":
                    print(f"\n⏭️  Sync skipped: {result.get('reason', 'unknown')}")
                else:
                    print(f"\n❌ Sync failed: {result.get('error', 'unknown')}")
                    sys.exit(1)
    except Exception as e:
        logger.exception(f"Sync failed with exception: {e}")
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
