---
description: Query Notion RAG and local knowledge base
arguments:
  - name: query
    description: Search query for knowledge base
    required: true
---

# Knowledge Base Query

Search the Notion RAG and local knowledge base for: **$ARGUMENTS**

## Execution

Run the semantic search:

```bash
python3 -m scripts.ai.notion_embeddings_pipeline --search "$ARGUMENTS"
```

## Alternative Commands

### Get a specific page by title
```bash
python3 -m scripts.ai.notion_knowledge_retriever --page "Page Title"
```

### Keyword search (faster, less semantic)
```bash
python3 -m scripts.ai.notion_knowledge_retriever --search "keyword"
```

### Query a specific database
```bash
python3 -m scripts.ai.notion_knowledge_retriever --db archetypes
```

### Check index statistics
```bash
python3 -m scripts.ai.notion_embeddings_pipeline --stats
```

## Output Format

Present results with:
- Source indicator: 🏠 Local | ☁️ Notion
- Title and relevance score
- Brief excerpt or summary
- Link/path to full content

## Knowledge Locations

| Source | Location |
|--------|----------|
| Notion pages | Indexed in Qdrant vector DB |
| Local exports | `knowledge/notion_export/` |
| Lessons learned | `knowledge/lessons_learned.yaml` |
| Best practices | `knowledge/best_practices.md` |
| Archetypes | `knowledge/archetypes.yaml` |
| Hypnotic patterns | `knowledge/hypnotic_patterns.yaml` |

## See Also

- Serena memory: `notion_rag_integration` for full RAG documentation
- `/board` command to consult the AI Board of Directors
