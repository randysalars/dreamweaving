#!/usr/bin/env python3
"""
Notion Embeddings Pipeline for Dreamweaving RAG

Extracts content from the Sacred Digital Dreamweaver Notion workspace,
generates embeddings using sentence-transformers (FREE, local), and stores
them in a vector database for semantic search.

Usage:
    # Initial indexing (full export + embedding)
    python3 -m scripts.ai.notion_embeddings_pipeline --index

    # Incremental update (only changed pages)
    python3 -m scripts.ai.notion_embeddings_pipeline --update

    # Search the knowledge base
    python3 -m scripts.ai.notion_embeddings_pipeline --search "Navigator archetype shadow aspect"

    # Show index statistics
    python3 -m scripts.ai.notion_embeddings_pipeline --stats
"""

import os
import sys
import json
import argparse
import hashlib
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import re
import threading

# Try sentence-transformers first (FREE, local)
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

# OpenAI as fallback (paid)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct,
        Filter, FieldCondition, MatchValue
    )
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "notion_config.yaml"
VECTOR_DB_PATH = PROJECT_ROOT / "knowledge" / "vector_db"
FILE_MANIFEST_PATH = VECTOR_DB_PATH / "file_manifest.json"

# Load .env automatically for local/IDE runs.
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")


def load_config() -> Dict[str, Any]:
    """Load configuration with environment variable resolution."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    def resolve_env(obj):
        if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.environ.get(var_name, obj)
        elif isinstance(obj, dict):
            return {k: resolve_env(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_env(item) for item in obj]
        return obj

    return resolve_env(config)


class NotionEmbeddingsPipeline:
    """
    Pipeline for creating and querying embeddings from Notion content.

    Architecture:
    1. Export content from Notion via notion_knowledge_retriever
    2. Chunk content based on type (full entries, paragraphs, etc.)
    3. Generate embeddings via OpenAI
    4. Store in Qdrant vector database
    5. Enable semantic search across all content

    Args:
        quiet: If True, suppress progress output (useful when called from watcher).
    """

    def __init__(self, quiet: bool = False):
        self.config = load_config()
        self.quiet = quiet
        self._init_clients()
        self._init_collection()

    def _log(self, message: str):
        """Print message unless in quiet mode."""
        if not self.quiet:
            print(message)

    def _init_clients(self):
        """Initialize embedding model and Qdrant clients."""
        if not HAS_QDRANT:
            raise ImportError("qdrant-client not installed. Run: pip install qdrant-client")

        # Prefer sentence-transformers (FREE, local) over OpenAI (paid)
        if HAS_SENTENCE_TRANSFORMERS:
            # Get local embedding settings from config
            local_config = self.config.get("embeddings", {}).get("local", {})
            self.embedding_model = local_config.get("model", "all-MiniLM-L6-v2")
            self.embedding_dims = local_config.get("dimensions", 384)
            self.local_batch_size = local_config.get("batch_size", 32)
            max_threads = local_config.get("max_threads", 2)

            # Limit CPU threads to prevent saturation
            if max_threads > 0:
                import torch
                torch.set_num_threads(max_threads)
                os.environ["OMP_NUM_THREADS"] = str(max_threads)
                os.environ["MKL_NUM_THREADS"] = str(max_threads)
                self._log(f"CPU threads limited to {max_threads}")

            self.sentence_model = SentenceTransformer(self.embedding_model)
            self.use_local = True
            self._log(f"Using local embeddings: {self.embedding_model} (FREE)")
        elif HAS_OPENAI:
            self.openai = OpenAI()
            self.embedding_model = self.config["embeddings"]["model"]
            self.embedding_dims = self.config["embeddings"]["dimensions"]
            self.use_local = False
            self._log(f"Using OpenAI embeddings: {self.embedding_model}")
        else:
            raise ImportError(
                "No embedding backend available. Install one of:\n"
                "  pip install sentence-transformers  # FREE, local\n"
                "  pip install openai                 # Paid API"
            )

        # Qdrant client (local storage)
        db_path = Path(self.config["vector_db"]["path"])
        db_path.mkdir(parents=True, exist_ok=True)
        self.qdrant = QdrantClient(path=str(db_path))

        self.collection_name = self.config["vector_db"]["collection"]

    def _init_collection(self):
        """Initialize or verify the Qdrant collection."""
        collections = self.qdrant.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self._log(f"Creating collection: {self.collection_name}")
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dims,
                    distance=Distance.COSINE
                )
            )

    def index_all_content(self, export_dir: Optional[Path] = None) -> Dict[str, int]:
        """
        Full indexing of all Notion content.

        Args:
            export_dir: Directory containing exported Notion content
                       (from notion_knowledge_retriever --export)

        Returns:
            Statistics about indexed content
        """
        # Use default export directory if not specified
        if export_dir is None:
            export_dir = PROJECT_ROOT / "knowledge" / "notion_export"

        if not export_dir.exists():
            raise FileNotFoundError(
                f"Export directory not found: {export_dir}\n"
                "Run: python3 -m scripts.ai.notion_knowledge_retriever --export knowledge/notion_export/"
            )

        stats = {"pages": 0, "entries": 0, "chunks": 0, "vectors": 0}
        all_points = []

        # Index pages
        pages_dir = export_dir / "pages"
        if pages_dir.exists():
            for md_file in pages_dir.glob("*.md"):
                try:
                    chunks = self._process_page_file(md_file)
                    points = self._create_points(chunks)
                    all_points.extend(points)
                    stats["pages"] += 1
                    stats["chunks"] += len(chunks)
                except Exception as e:
                    self._log(f"Error processing {md_file.name}: {e}")

        # Index database entries
        db_dir = export_dir / "databases"
        if db_dir.exists():
            for db_type_dir in db_dir.iterdir():
                if db_type_dir.is_dir():
                    for md_file in db_type_dir.glob("*.md"):
                        try:
                            chunks = self._process_entry_file(
                                md_file,
                                database=db_type_dir.name
                            )
                            points = self._create_points(chunks)
                            all_points.extend(points)
                            stats["entries"] += 1
                            stats["chunks"] += len(chunks)
                        except Exception as e:
                            self._log(f"Error processing {md_file.name}: {e}")

        # Batch upsert to Qdrant
        if all_points:
            # Process in batches of 100
            batch_size = 100
            for i in range(0, len(all_points), batch_size):
                batch = all_points[i:i + batch_size]
                self.qdrant.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                stats["vectors"] += len(batch)

        # Save index metadata
        self._save_index_metadata(stats, export_dir)

        return stats

    def search(
        self,
        query: str,
        limit: int = 5,
        content_type: Optional[str] = None,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Semantic search across indexed content.

        Args:
            query: Natural language search query
            limit: Maximum results to return
            content_type: Filter by type (page, database_entry)
            score_threshold: Minimum relevance score (0-1)

        Returns:
            List of relevant content chunks with metadata
        """
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]

        # Build filter
        filter_obj = None
        if content_type:
            filter_obj = Filter(
                must=[
                    FieldCondition(
                        key="type",
                        match=MatchValue(value=content_type)
                    )
                ]
            )

        # Search using query_points (Qdrant 1.7+ API)
        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=filter_obj,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True
        )

        return [
            {
                "title": r.payload.get("title", ""),
                "type": r.payload.get("type", ""),
                "database": r.payload.get("database", ""),
                "text": r.payload.get("chunk_text", ""),
                "chunk_index": r.payload.get("chunk_index", 0),
                "url": r.payload.get("url", ""),
                "score": r.score,
            }
            for r in results.points
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index."""
        try:
            collection_info = self.qdrant.get_collection(self.collection_name)

            # Qdrant 1.7+ API uses different attribute names
            points_count = getattr(collection_info, 'points_count', None)
            vectors_count = getattr(collection_info, 'vectors_count', points_count)
            status = getattr(collection_info, 'status', 'unknown')

            return {
                "collection": self.collection_name,
                "points_count": points_count,
                "vectors_count": vectors_count,
                "status": str(status),
                "embedding_model": self.embedding_model,
                "embedding_dims": self.embedding_dims,
            }
        except Exception as e:
            return {"error": str(e)}

    def clear_index(self) -> bool:
        """Delete and recreate the collection."""
        try:
            self.qdrant.delete_collection(self.collection_name)
            self._init_collection()
            # Also clear file manifest
            if FILE_MANIFEST_PATH.exists():
                FILE_MANIFEST_PATH.unlink()
            return True
        except Exception as e:
            self._log(f"Error clearing index: {e}")
            return False

    # ========== Incremental Update Methods ==========

    def load_file_manifest(self) -> Dict[str, Any]:
        """Load the file manifest tracking individual file hashes and vector IDs."""
        if FILE_MANIFEST_PATH.exists():
            try:
                return json.loads(FILE_MANIFEST_PATH.read_text())
            except json.JSONDecodeError:
                self._log("Warning: Failed to parse file manifest, starting fresh")
        return {"files": {}, "last_sync": None, "statistics": {}}

    def save_file_manifest(self, manifest: Dict[str, Any]):
        """Save the file manifest."""
        manifest["last_sync"] = datetime.now().isoformat()
        FILE_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        FILE_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    def get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a single file."""
        return hashlib.md5(filepath.read_bytes()).hexdigest()

    def detect_changes(self, export_dir: Path) -> Dict[str, List[Path]]:
        """
        Detect which files have been added, modified, or deleted since last sync.

        Returns:
            Dictionary with 'added', 'modified', 'deleted' lists of file paths.
        """
        manifest = self.load_file_manifest()
        old_files = manifest.get("files", {})

        # Get current files
        current_files = {}
        for md_file in export_dir.glob("**/*.md"):
            rel_path = str(md_file.relative_to(export_dir))
            current_files[rel_path] = {
                "hash": self.get_file_hash(md_file),
                "size": md_file.stat().st_size,
                "mtime": md_file.stat().st_mtime
            }

        changes = {
            "added": [],
            "modified": [],
            "deleted": []
        }

        # Find added and modified files
        for rel_path, info in current_files.items():
            if rel_path not in old_files:
                changes["added"].append(export_dir / rel_path)
            elif info["hash"] != old_files[rel_path].get("hash"):
                changes["modified"].append(export_dir / rel_path)

        # Find deleted files
        for rel_path in old_files:
            if rel_path not in current_files:
                changes["deleted"].append(rel_path)

        return changes

    def index_incremental(self, export_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Incremental indexing - only process changed files.

        This is MUCH faster than full re-indexing when only a few files changed.

        Args:
            export_dir: Directory containing exported Notion content

        Returns:
            Statistics about the incremental update
        """
        if export_dir is None:
            export_dir = PROJECT_ROOT / "knowledge" / "notion_export"

        if not export_dir.exists():
            raise FileNotFoundError(f"Export directory not found: {export_dir}")

        # Detect changes
        changes = self.detect_changes(export_dir)
        total_changes = len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"])

        if total_changes == 0:
            self._log("No changes detected - index is up to date")
            return {
                "status": "no_changes",
                "added": 0,
                "modified": 0,
                "deleted": 0,
                "vectors_added": 0,
                "vectors_removed": 0
            }

        self._log(f"Detected changes: +{len(changes['added'])} added, "
              f"~{len(changes['modified'])} modified, -{len(changes['deleted'])} deleted")

        manifest = self.load_file_manifest()
        stats = {
            "added": len(changes["added"]),
            "modified": len(changes["modified"]),
            "deleted": len(changes["deleted"]),
            "vectors_added": 0,
            "vectors_removed": 0
        }

        # 1. Delete vectors for modified files
        for filepath in changes["modified"]:
            rel_path = str(filepath.relative_to(export_dir))
            if rel_path in manifest["files"]:
                old_info = manifest["files"][rel_path]
                vector_ids = old_info.get("vector_ids", [])
                if vector_ids:
                    self._delete_vectors_by_ids(vector_ids)
                    stats["vectors_removed"] += len(vector_ids)

        # Handle deleted files
        for rel_path in changes["deleted"]:
            if rel_path in manifest["files"]:
                old_info = manifest["files"][rel_path]
                vector_ids = old_info.get("vector_ids", [])
                if vector_ids:
                    self._delete_vectors_by_ids(vector_ids)
                    stats["vectors_removed"] += len(vector_ids)
                # Remove from manifest
                del manifest["files"][rel_path]

        # 2. Index added and modified files
        files_to_index = changes["added"] + changes["modified"]
        for filepath in files_to_index:
            try:
                rel_path = str(filepath.relative_to(export_dir))

                # Determine if page or database entry
                if "databases" in str(filepath):
                    db_name = filepath.parent.name
                    chunks = self._process_entry_file(filepath, database=db_name)
                else:
                    chunks = self._process_page_file(filepath)

                # Create and upsert points
                points = self._create_points(chunks)
                if points:
                    self.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    stats["vectors_added"] += len(points)

                # Update manifest
                manifest["files"][rel_path] = {
                    "hash": self.get_file_hash(filepath),
                    "size": filepath.stat().st_size,
                    "chunks": len(chunks),
                    "vector_ids": [p.id for p in points]
                }

            except Exception as e:
                self._log(f"Error processing {filepath.name}: {e}")

        # 3. Update statistics
        manifest["statistics"] = {
            "total_files": len(manifest["files"]),
            "total_vectors": sum(len(f.get("vector_ids", [])) for f in manifest["files"].values())
        }

        # 4. Save updated manifest
        self.save_file_manifest(manifest)

        return stats

    def _delete_vectors_by_ids(self, vector_ids: List[str]):
        """Delete specific vectors by their IDs."""
        if not vector_ids:
            return
        try:
            from qdrant_client.models import PointIdsList
            self.qdrant.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=vector_ids)
            )
        except Exception as e:
            self._log(f"Warning: Failed to delete vectors: {e}")

    def rebuild_manifest_from_index(self, export_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Rebuild the file manifest from scratch based on current export files.

        Use this to initialize incremental updates on an existing full index,
        or to repair a corrupted manifest.
        """
        if export_dir is None:
            export_dir = PROJECT_ROOT / "knowledge" / "notion_export"

        self._log("Rebuilding file manifest from export directory...")
        manifest = {"files": {}, "statistics": {}}

        for md_file in export_dir.glob("**/*.md"):
            rel_path = str(md_file.relative_to(export_dir))
            manifest["files"][rel_path] = {
                "hash": self.get_file_hash(md_file),
                "size": md_file.stat().st_size,
                "chunks": 0,  # Unknown without re-processing
                "vector_ids": []  # Unknown without re-indexing
            }

        manifest["statistics"] = {
            "total_files": len(manifest["files"]),
            "total_vectors": 0,  # Unknown
            "manifest_rebuilt": True
        }

        self.save_file_manifest(manifest)
        self._log(f"Manifest rebuilt with {len(manifest['files'])} files")

        return manifest

    def _process_page_file(self, filepath: Path) -> List[Dict]:
        """Process a page markdown file into chunks."""
        with open(filepath) as f:
            content = f.read()

        # Extract metadata from header
        metadata = self._extract_page_metadata(content)

        # Remove metadata section
        content = re.sub(r'^#.*?\n---\n', '', content, flags=re.DOTALL)

        # Chunk content
        chunks = self._chunk_content(
            content,
            metadata["title"],
            chunk_type="page"
        )

        # Add metadata to each chunk
        for chunk in chunks:
            chunk.update(metadata)

        return chunks

    def _process_entry_file(self, filepath: Path, database: str) -> List[Dict]:
        """Process a database entry markdown file."""
        with open(filepath) as f:
            content = f.read()

        # Extract metadata
        metadata = self._extract_entry_metadata(content)
        metadata["database"] = database
        metadata["type"] = "database_entry"

        # For database entries, keep as single chunk
        # This preserves all properties together
        clean_content = self._clean_markdown(content)

        return [{
            "text": clean_content,
            "chunk_index": 0,
            **metadata
        }]

    def _chunk_content(
        self,
        text: str,
        title: str,
        chunk_type: str = "page"
    ) -> List[Dict]:
        """
        Split content into overlapping chunks.

        Strategy:
        - Preserve paragraph boundaries when possible
        - Include title in each chunk for context
        - Create overlap to maintain continuity
        """
        chunk_size = self.config["embeddings"]["chunk_size"]
        overlap = self.config["embeddings"]["chunk_overlap"]

        # Clean text
        text = self._clean_markdown(text)

        # For short content, return as single chunk
        if len(text) <= chunk_size:
            return [{
                "text": f"Title: {title}\n\n{text}",
                "chunk_index": 0,
                "title": title,
                "type": chunk_type
            }]

        chunks = []
        start = 0
        chunk_idx = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at paragraph boundary
            if end < len(text):
                # Look for paragraph break near end
                para_break = text.rfind("\n\n", start + chunk_size // 2, end + 100)
                if para_break > start:
                    end = para_break

            chunk_text = text[start:end].strip()

            if len(chunk_text) > 50:  # Skip tiny chunks
                chunks.append({
                    "text": f"Title: {title}\n\n{chunk_text}",
                    "chunk_index": chunk_idx,
                    "title": title,
                    "type": chunk_type
                })
                chunk_idx += 1

            # Move start with overlap
            start = end - overlap if end < len(text) else len(text)

        return chunks

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model or OpenAI API."""
        if self.use_local:
            # Use sentence-transformers (FREE, local)
            # Show progress bar only if not in quiet mode and processing many texts
            # Use configured batch_size for memory efficiency
            batch_size = getattr(self, 'local_batch_size', 32)
            embeddings = self.sentence_model.encode(
                texts,
                show_progress_bar=not self.quiet and len(texts) > 10,
                convert_to_numpy=True,
                batch_size=batch_size
            )
            return [emb.tolist() for emb in embeddings]
        else:
            # Use OpenAI API (paid)
            batch_size = self.config["embeddings"]["batch_size"]
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                response = self.openai.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )

                all_embeddings.extend([e.embedding for e in response.data])

            return all_embeddings

    def _create_points(self, chunks: List[Dict]) -> List[PointStruct]:
        """Create Qdrant points from chunks with embeddings."""
        if not chunks:
            return []

        # Generate embeddings for all chunks
        texts = [c["text"] for c in chunks]
        embeddings = self._generate_embeddings(texts)

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            # Create deterministic ID from content
            point_id = hashlib.md5(
                f"{chunk.get('title', '')}_{chunk.get('chunk_index', 0)}_{chunk['text'][:100]}".encode()
            ).hexdigest()

            points.append(PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "title": chunk.get("title", ""),
                    "type": chunk.get("type", "unknown"),
                    "database": chunk.get("database", ""),
                    "chunk_text": chunk["text"],
                    "chunk_index": chunk.get("chunk_index", 0),
                    "url": chunk.get("url", ""),
                    "indexed_at": datetime.utcnow().isoformat()
                }
            ))

        return points

    def _extract_page_metadata(self, content: str) -> Dict:
        """Extract metadata from page markdown header."""
        metadata = {
            "title": "Untitled",
            "url": "",
            "type": "page"
        }

        # Extract title from first heading
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1)

        # Extract URL
        url_match = re.search(r'^Source: (.+)$', content, re.MULTILINE)
        if url_match:
            metadata["url"] = url_match.group(1)

        return metadata

    def _extract_entry_metadata(self, content: str) -> Dict:
        """Extract metadata from database entry markdown."""
        metadata = {
            "title": "Untitled",
            "url": "",
            "type": "database_entry"
        }

        # Extract title
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1)

        return metadata

    def _clean_markdown(self, text: str) -> str:
        """Clean markdown for embedding."""
        # Remove frontmatter
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)

        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        return text.strip()

    def _save_index_metadata(self, stats: Dict, export_dir: Path):
        """Save metadata about the indexing run."""
        metadata_path = VECTOR_DB_PATH / "index_metadata.json"

        metadata = {
            "indexed_at": datetime.utcnow().isoformat(),
            "source_dir": str(export_dir),
            "stats": stats,
            "config": {
                "model": self.embedding_model,
                "chunk_size": self.config["embeddings"]["chunk_size"],
                "chunk_overlap": self.config["embeddings"]["chunk_overlap"]
            }
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)


def format_search_results(results: List[Dict], verbose: bool = False) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    lines = [f"\nFound {len(results)} results:\n"]

    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r['title']}")
        lines.append(f"Type: {r['type']}")
        if r.get("database"):
            lines.append(f"Database: {r['database']}")
        lines.append(f"Score: {r['score']:.3f}")

        if verbose:
            lines.append(f"\n{r['text']}\n")
        else:
            # Show truncated preview
            preview = r['text'][:200] + "..." if len(r['text']) > 200 else r['text']
            lines.append(f"\n{preview}\n")

        if r.get("url"):
            lines.append(f"URL: {r['url']}")
        lines.append("---\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Notion Embeddings Pipeline for Dreamweaving RAG"
    )
    parser.add_argument(
        "--index", "-i",
        action="store_true",
        help="Index all exported Notion content"
    )
    parser.add_argument(
        "--export-dir",
        help="Directory containing Notion export (default: knowledge/notion_export/)"
    )
    parser.add_argument(
        "--search", "-s",
        help="Semantic search query"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=5,
        help="Maximum search results (default: 5)"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["page", "database_entry"],
        help="Filter by content type"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show index statistics"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the index (delete all vectors)"
    )
    parser.add_argument(
        "--rebuild-manifest",
        action="store_true",
        help="Rebuild file manifest from export directory (use after cleanup)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Check dependencies
    if not HAS_SENTENCE_TRANSFORMERS and not HAS_OPENAI:
        print("Error: No embedding backend installed.")
        print("Install one of:")
        print("  pip install sentence-transformers  # FREE, local (recommended)")
        print("  pip install openai                 # Paid API")
        sys.exit(1)
    if not HAS_QDRANT:
        print("Error: qdrant-client not installed. Run: pip install qdrant-client")
        sys.exit(1)

    try:
        pipeline = NotionEmbeddingsPipeline()
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        sys.exit(1)

    try:
        if args.index:
            export_dir = Path(args.export_dir) if args.export_dir else None
            print("Indexing Notion content...")
            stats = pipeline.index_all_content(export_dir)

            if args.json:
                print(json.dumps(stats, indent=2))
            else:
                print("\nIndexing complete:")
                print(f"  Pages: {stats['pages']}")
                print(f"  Entries: {stats['entries']}")
                print(f"  Chunks: {stats['chunks']}")
                print(f"  Vectors: {stats['vectors']}")

        elif args.search:
            results = pipeline.search(
                args.search,
                limit=args.limit,
                content_type=args.type
            )

            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(format_search_results(results, args.verbose))

        elif args.stats:
            stats = pipeline.get_stats()
            if args.json:
                print(json.dumps(stats, indent=2))
            else:
                print("\nIndex Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")

        elif args.clear:
            confirm = input("This will delete all indexed content. Continue? (y/N): ")
            if confirm.lower() == "y":
                if pipeline.clear_index():
                    print("Index cleared.")
                else:
                    print("Failed to clear index.")
            else:
                print("Cancelled.")

        elif args.rebuild_manifest:
            export_dir = Path(args.export_dir) if args.export_dir else None
            print("Rebuilding file manifest...")
            manifest = pipeline.rebuild_manifest_from_index(export_dir)

            if args.json:
                print(json.dumps(manifest.get("statistics", {}), indent=2))
            else:
                stats = manifest.get("statistics", {})
                print(f"  Total files: {stats.get('total_files', 0)}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
