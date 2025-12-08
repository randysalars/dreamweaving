# On Knowledge Change Hook

## Trigger
This hook should be invoked when files in the `knowledge/` directory are modified during a Claude Code session.

## When to Trigger
- After modifying any `.md`, `.yaml`, or `.json` files in `knowledge/`
- After running Notion export
- After adding new knowledge entries
- After updating `knowledge/lessons_learned.yaml`

## Action

When knowledge files are modified, Claude should:

1. **Notify the user** that knowledge files were changed
2. **Offer to re-index** the RAG vector database

### Suggested Response

```
Knowledge base files were modified. Would you like me to re-index the RAG vector database?

This will update the semantic search index with the new content.

To re-index now:
python3 scripts/ai/rag_auto_sync.py --force
```

### If User Confirms

Run the re-indexing command:

```bash
source venv/bin/activate && python3 scripts/ai/rag_auto_sync.py --force
```

### Alternative: Check Status First

```bash
python3 scripts/ai/rag_auto_sync.py --status
```

## Notes

- The file watcher daemon (`rag_file_watcher.py`) handles this automatically if running
- This hook is for manual sessions where the watcher isn't active
- Re-indexing typically takes 30-60 seconds for full corpus
