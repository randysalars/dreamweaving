# CLAUDE: How to Read Notion Pages

When the user asks you to "read", "pull", "fetch", or "check" a Notion page, follow this protocol:

## Quick Decision Tree

```
User wants Notion content
    │
    ├─► Conceptual/semantic search? (e.g., "find shadow healing content")
    │   └─► python3 -m scripts.ai.notion_embeddings_pipeline --search "query"
    │
    ├─► Specific page by exact title?
    │   └─► python3 -m scripts.ai.notion_knowledge_retriever --page "Title"
    │
    ├─► Search by keyword?
    │   └─► python3 -m scripts.ai.notion_knowledge_retriever --search "keyword"
    │
    ├─► Database query (Archetypes, Realms, etc.)?
    │   └─► python3 -m scripts.ai.notion_knowledge_retriever --db <dbname>
    │
    └─► Need fresh data (re-sync from Notion)?
        └─► python3 -m scripts.ai.notion_knowledge_retriever --export knowledge/notion_export/
            python3 -m scripts.ai.notion_embeddings_pipeline --index
```

## Commands Reference

| Task | Command |
|------|---------|
| Semantic search | `python3 -m scripts.ai.notion_embeddings_pipeline --search "query"` |
| Get page by title | `python3 -m scripts.ai.notion_knowledge_retriever --page "Title"` |
| Title keyword search | `python3 -m scripts.ai.notion_knowledge_retriever --search "keyword"` |
| Query database | `python3 -m scripts.ai.notion_knowledge_retriever --db archetypes` |
| Check index stats | `python3 -m scripts.ai.notion_embeddings_pipeline --stats` |
| Full export + reindex | `--export` then `--index` (see above) |

## Where Content Lives

| Content Type | Location |
|--------------|----------|
| Exported markdown | `knowledge/notion_export/` |
| Vector index | `knowledge/vector_db/` |
| Index stats | `knowledge/vector_db/index_metadata.json` |
| Config | `config/notion_config.yaml` |

## Important Notes

1. **Semantic search is preferred** - It's fast, works offline, and finds conceptually related content
2. **Index has 197K+ chunks** - Comprehensive coverage of the entire workspace
3. **Title search is limited** - Notion API only searches titles, not page content (use semantic for full-text)
4. **Re-sync rarely needed** - Index is auto-synced; only force sync if you know content changed recently

---

# Notion RAG Integration for Dreamweaving

## Overview

The Dreamweaving project uses Notion as a canonical knowledge base (Sacred Digital Dreamweaver workspace) with two access methods:

1. **Real-time MCP Access** - Direct queries via Notion MCP server
2. **Semantic Search** - Vector embeddings for conceptual queries

## Quick Reference

### Access Methods

| Method | Use Case | Speed | Capability |
|--------|----------|-------|------------|
| Notion MCP | Direct database queries | Fast | Title-based search only |
| Embeddings | Semantic/conceptual queries | Fast (after indexing) | Full-text semantic |

### Key Files

| File | Purpose |
|------|---------|
| `config/notion_config.yaml` | Database IDs, embedding settings |
| `config/mcp_servers.json` | MCP server configuration |
| `scripts/ai/notion_knowledge_retriever.py` | Direct Notion API access |
| `scripts/ai/notion_embeddings_pipeline.py` | Vector database indexing |
| `scripts/ai/knowledge_tools.py` | High-level query functions |

## Setup Checklist

1. **Create Notion Integration**
   - Visit https://www.notion.so/profile/integrations
   - Create "Dreamweaving RAG" integration
   - Copy token to `.env` as `NOTION_TOKEN`

2. **Grant Integration Access**
   - Open Sacred Digital Dreamweaver page
   - Click ⋮ → Connections → Add integration
   - Repeat for all databases and subpages

3. **Update Database IDs**
   - Get each database ID from Notion URL
   - Add to `config/notion_config.yaml`

4. **Index Content (for semantic search)**
   ```bash
   python3 -m scripts.ai.notion_knowledge_retriever --export knowledge/notion_export/
   python3 -m scripts.ai.notion_embeddings_pipeline --index
   ```

## Database Schema

Six databases in Notion workspace:

### Archetypes
- Name, Shadow Aspect, Light Aspect
- Activation Ritual, Associated Realms, Frequencies
- Visual Prompts, SSML Template

### Realms & Mythic Locations
- Name, Energetic Quality, Atmosphere
- Portal Entry, Guardian, Soundscape, Color Palette

### Frequencies & Consciousness Technologies
- Name, Hz Range, Brainwave State
- Effects, SSML Pacing, Binaural Config

### Rituals/Ceremonies/Activations
- Name, Purpose, Duration
- Sequence Steps, Required Elements, Script Template

### Story Elements & Mythic Lore
- Name, Category (Character/Spirit/Symbol/Origin Story)
- Description, Related Archetypes, Related Realms

### Script Components
- Name, Section Type (Pre-talk/Induction/Journey/etc.)
- SSML Template, NLP Patterns, Dependencies

## Usage Commands

### Direct Notion Queries

```bash
# Search workspace by title
python3 -m scripts.ai.notion_knowledge_retriever --search "Navigator"

# Query specific database
python3 -m scripts.ai.notion_knowledge_retriever --db archetypes --filter Guardian

# Get page content
python3 -m scripts.ai.notion_knowledge_retriever --page "Mythic Cosmology"

# Export all content
python3 -m scripts.ai.notion_knowledge_retriever --export knowledge/notion_export/
```

### Semantic Search (requires indexing)

```bash
# Index exported content
python3 -m scripts.ai.notion_embeddings_pipeline --index

# Search semantically
python3 -m scripts.ai.notion_embeddings_pipeline --search "shadow healing transformation"

# Check index stats
python3 -m scripts.ai.notion_embeddings_pipeline --stats
```

### High-Level Knowledge Tools

```bash
# Query all sources
python3 -m scripts.ai.knowledge_tools --query "Navigator shadow healing"

# Get specific archetype
python3 -m scripts.ai.knowledge_tools --archetype Guardian

# Get specific realm
python3 -m scripts.ai.knowledge_tools --realm "Atlantean Crystal Spine"

# Build journey context
python3 -m scripts.ai.knowledge_tools --build-context Navigator "Atlantean Crystal Spine" "Gamma Flash"
```

## Python API

```python
from scripts.ai.knowledge_tools import (
    query_canonical_knowledge,
    get_archetype,
    get_realm,
    get_frequency,
    search_lore,
    build_journey_context
)

# Semantic search
results = query_canonical_knowledge("Navigator shadow healing journey")

# Get specific archetype
navigator = get_archetype("Navigator")
print(navigator["Shadow Aspect"])

# Build complete journey context
context = build_journey_context(
    archetype="Navigator",
    realm="Atlantean Crystal Spine",
    frequency="Gamma Flash"
)
```

## RAG Architecture

```
Notion Workspace ──┬──▶ Notion MCP Server ──▶ Claude Code (real-time)
                   │
                   └──▶ Export → Chunk → Embed → Qdrant ──▶ Semantic Search
```

## Limitations

1. **Notion API Search** - Title-based only, not full-text
2. **Indexing Required** - Semantic search needs initial export + embedding
3. **Manual Sync** - Content changes require re-indexing
4. **Database IDs** - Must be manually configured after creating DBs

## Cost Estimates

| Component | Cost |
|-----------|------|
| Notion API | Free |
| OpenAI Embeddings (initial) | ~$0.50 |
| OpenAI Embeddings (monthly updates) | ~$0.10 |
| Qdrant (local) | Free |

## Troubleshooting

### "Database not found"
- Verify database ID in `config/notion_config.yaml`
- Ensure integration has access to the database

### "NOTION_TOKEN not set"
- Add `NOTION_TOKEN=ntn_xxx` to `.env`
- Or export: `export NOTION_TOKEN=ntn_xxx`

### "No embeddings results"
- Run indexing: `python3 -m scripts.ai.notion_embeddings_pipeline --index`
- Check export exists: `ls knowledge/notion_export/`

### "notion-client not installed"
```bash
pip install notion-client openai qdrant-client pyyaml
```

## References

- [Notion MCP Documentation](https://developers.notion.com/docs/mcp)
- [Official Notion MCP Server](https://github.com/makenotion/notion-mcp-server)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- Config: `config/notion_config.yaml`
- Docs: `docs/MCP_PLUGINS_GUIDE.md` (Section 8)
