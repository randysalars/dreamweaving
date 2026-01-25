import logging
import sys
from pathlib import Path
from agents.product_builder.pipeline.writers_room import WritersRoom

# Configure logging
logging.basicConfig(level=logging.INFO)

# Setup paths
base_dir = Path("/home/rsalars/Projects/dreamweaving/agents/product_builder")
templates_dir = base_dir / "templates"

print(f"Templates dir: {templates_dir}")

# Instantiate WritersRoom
room = WritersRoom(templates_dir)

# Mock Context
context = {
    "chapter_number": 1,
    "chapter_title": "Debug Chapter",
    "chapter_purpose": "To test context injection.",
    "voice_rules": "Be punchy.",
    "banned_phrases": ["synergy"],
    "key_takeaways": "It works.",
    "product_promise": "Fix bugs.",
    "audience_persona": "Developer",
    "product_name": "Debug Product",
    "thesis": "Debugging is fun."
}

print("RUNNING WRITE_CHAPTER...")
try:
    draft = room.write_chapter(context)
    print("\nSUCCESS! Draft generated:")
    print(draft[:200])
except Exception as e:
    print(f"\nFAILURE: {e}")
