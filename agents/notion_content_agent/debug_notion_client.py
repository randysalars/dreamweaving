import os
import sys
from pprint import pprint

try:
    import notion_client
    print(f"notion_client version: {notion_client.__version__}")
    print(f"notion_client file: {notion_client.__file__}")
except ImportError:
    print("notion_client not found")
except AttributeError:
    print("notion_client has no __version__")
    print(f"notion_client file: {notion_client.__file__}")

try:
    from notion_client import Client
    # We need a real token. The user has one in .env?
    # I will try to load it from the env vars if possible, but for this standalone script 
    # I might fail if I don't load .env.
    # The previous run showed the script has no token access.
    
    # I will rely on the main script's failure to diagnose. 
    # But wait, I can use the existing `notion_adapter.py` functionality if I fix it?
    
    # Let's just create a small script that loads config and tries retrieve.
    from config import Config
    
    if not Config.validate():
        print("Config invalid")
        sys.exit(1)
        
    client = Client(auth=Config.NOTION_TOKEN)
    db_id = Config.NOTION_DB_ID
    
    # Updated ID from user
    db_id = "2d62bab3-796d-80cb-a6d6-c88d76987fa9"
    print(f"Testing ID: {db_id}")
    
    # Scan children
    print(f"\nScanning children of Page {db_id}...")
    
    cursor = None
    count = 0
    found_candidates = []
    
    while True:
        children = client.blocks.children.list(block_id=db_id, start_cursor=cursor)
        
        for block in children.get("results", []):
            count += 1
            btype = block.get("type")
            
            # Print content of check boxes or bullets
            if btype in ["to_do", "bulleted_list_item", "paragraph"]:
                text_objs = block.get(btype, {}).get("rich_text", [])
                plain_text = "".join([t.get("plain_text", "") for t in text_objs])
                checked = block.get(btype, {}).get("checked")
                
                check_mark = "[x]" if checked else "[ ]" if checked is not None else ""
                if "Ready to Write" in plain_text or "Status" in plain_text or "http" in plain_text:
                     print(f"MATCH: {check_mark} {plain_text}")
                     # Print links?
                     for t in text_objs:
                         if t.get("href"):
                             print(f"  -> LINK: {t.get('href')}")

        if not children.get("has_more"):
            break
        cursor = children.get("next_cursor")
        
    print(f"Total blocks scanned: {count}")


except Exception as e:
    print(f"Outer Error: {e}")
