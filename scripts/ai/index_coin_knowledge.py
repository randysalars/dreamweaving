#!/usr/bin/env python3
"""
Index Coin Knowledge YAML Files

Indexes the structured YAML coin guides into the RAG vector database,
making them searchable alongside Notion content.

Usage:
    # Index all coin YAML files
    python3 -m scripts.ai.index_coin_knowledge

    # Index and show what was added
    python3 -m scripts.ai.index_coin_knowledge --verbose
"""

import os
import sys
import argparse
import hashlib
import yaml
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
COINS_DIR = PROJECT_ROOT / "knowledge" / "coins"

# Import RAG pipeline
try:
    from scripts.ai.notion_embeddings_pipeline import NotionEmbeddingsPipeline
except ImportError:
    sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.ai.notion_embeddings_pipeline import NotionEmbeddingsPipeline

try:
    from qdrant_client.models import PointStruct
except ImportError:
    print("Error: qdrant-client not installed. Run: pip install qdrant-client")
    sys.exit(1)


def yaml_to_text(data: Any, prefix: str = "", depth: int = 0) -> str:
    """
    Convert YAML data structure to readable text for embedding.
    
    This flattens nested structures into human-readable sentences
    that work well with semantic search.
    """
    lines = []
    indent = "  " * depth
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Convert snake_case to readable
            readable_key = key.replace("_", " ").title()
            
            if isinstance(value, (dict, list)):
                lines.append(f"{indent}{readable_key}:")
                lines.append(yaml_to_text(value, prefix=readable_key, depth=depth + 1))
            elif isinstance(value, str) and len(value) > 100:
                # Long text - treat as paragraph
                lines.append(f"{indent}{readable_key}: {value}")
            else:
                lines.append(f"{indent}{readable_key}: {value}")
    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # Extract key info from dict items
                item_text = ", ".join(
                    f"{k}: {v}" for k, v in item.items() 
                    if not k.startswith("_")
                )
                lines.append(f"{indent}- {item_text}")
            else:
                lines.append(f"{indent}- {item}")
    
    else:
        lines.append(f"{indent}{data}")
    
    return "\n".join(lines)


def process_coin_yaml(filepath: Path) -> List[Dict]:
    """
    Process a coin YAML file into chunks for embedding.
    
    Returns list of chunks, each containing:
    - text: The content to embed
    - title: Source title
    - type: Content type
    - database: Category
    """
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    if not data:
        return []
    
    chunks = []
    filename = filepath.stem
    
    # Get top-level metadata
    name = data.get("name", filename.replace("_", " ").title())
    category = data.get("category", "coins")
    description = data.get("description", "")
    
    # Create overview chunk
    overview_parts = [
        f"Title: {name}",
        f"Category: {category}",
    ]
    if description:
        overview_parts.append(f"\nDescription: {description}")
    
    # Add main content sections
    main_sections = []
    for key, value in data.items():
        if key in ("entry_id", "name", "category", "description", "version", "created"):
            continue
        
        section_text = yaml_to_text({key: value})
        if len(section_text) > 50:  # Skip tiny sections
            main_sections.append(section_text)
    
    # Create chunks based on content size
    full_content = "\n\n".join(overview_parts + main_sections)
    
    # If content is small enough, keep as one chunk
    if len(full_content) < 2000:
        chunks.append({
            "text": full_content,
            "title": name,
            "type": "coin_knowledge",
            "database": category,
            "source_file": str(filepath.name),
            "chunk_index": 0
        })
    else:
        # Split into logical chunks
        # First chunk: overview + description
        chunks.append({
            "text": "\n\n".join(overview_parts),
            "title": f"{name} - Overview",
            "type": "coin_knowledge",
            "database": category,
            "source_file": str(filepath.name),
            "chunk_index": 0
        })
        
        # Subsequent chunks: major sections
        for i, section in enumerate(main_sections):
            if len(section) > 100:  # Skip tiny sections
                chunks.append({
                    "text": f"Source: {name}\n\n{section}",
                    "title": f"{name} - Section {i+1}",
                    "type": "coin_knowledge",
                    "database": category,
                    "source_file": str(filepath.name),
                    "chunk_index": i + 1
                })
    
    return chunks


def index_coin_knowledge(verbose: bool = False) -> Dict[str, Any]:
    """
    Index all coin YAML files into the RAG vector database.
    
    Returns statistics about the indexing operation.
    """
    if not COINS_DIR.exists():
        print(f"Error: Coins directory not found: {COINS_DIR}")
        return {"error": "Directory not found"}
    
    yaml_files = list(COINS_DIR.glob("*.yaml")) + list(COINS_DIR.glob("*.yml"))
    
    if not yaml_files:
        print("No YAML files found in coins directory")
        return {"files": 0, "chunks": 0, "vectors": 0}
    
    print(f"Found {len(yaml_files)} coin knowledge files")
    
    # Initialize RAG pipeline
    rag = NotionEmbeddingsPipeline(quiet=not verbose)
    
    all_chunks = []
    stats = {
        "files": 0,
        "chunks": 0,
        "vectors": 0,
        "file_details": []
    }
    
    for filepath in yaml_files:
        try:
            chunks = process_coin_yaml(filepath)
            all_chunks.extend(chunks)
            stats["files"] += 1
            stats["chunks"] += len(chunks)
            stats["file_details"].append({
                "file": filepath.name,
                "chunks": len(chunks)
            })
            
            if verbose:
                print(f"  ✓ {filepath.name}: {len(chunks)} chunks")
                
        except Exception as e:
            print(f"  ✗ Error processing {filepath.name}: {e}")
    
    if not all_chunks:
        print("No chunks generated")
        return stats
    
    # Generate embeddings and create points
    print(f"\nGenerating embeddings for {len(all_chunks)} chunks...")
    
    texts = [c["text"] for c in all_chunks]
    embeddings = rag._generate_embeddings(texts)
    
    points = []
    for chunk, embedding in zip(all_chunks, embeddings):
        # Create deterministic ID
        point_id = hashlib.md5(
            f"coin_yaml_{chunk['source_file']}_{chunk['chunk_index']}_{chunk['text'][:100]}".encode()
        ).hexdigest()
        
        points.append(PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "title": chunk["title"],
                "type": chunk["type"],
                "database": chunk["database"],
                "chunk_text": chunk["text"],
                "chunk_index": chunk["chunk_index"],
                "source_file": chunk["source_file"],
                "indexed_at": datetime.utcnow().isoformat()
            }
        ))
    
    # Upsert to Qdrant
    print(f"Upserting {len(points)} vectors to database...")
    
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        rag.qdrant.upsert(
            collection_name=rag.collection_name,
            points=batch
        )
        stats["vectors"] += len(batch)
    
    print(f"\n✅ Indexed {stats['files']} files, {stats['chunks']} chunks, {stats['vectors']} vectors")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Index coin YAML knowledge into RAG"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available coin knowledge files without indexing"
    )
    
    args = parser.parse_args()
    
    if args.list:
        yaml_files = list(COINS_DIR.glob("*.yaml")) + list(COINS_DIR.glob("*.yml"))
        print("\n📚 Available Coin Knowledge Files:\n")
        for f in sorted(yaml_files):
            size_kb = f.stat().st_size / 1024
            print(f"  • {f.name} ({size_kb:.1f} KB)")
        print()
        return
    
    index_coin_knowledge(verbose=args.verbose)


if __name__ == "__main__":
    main()
