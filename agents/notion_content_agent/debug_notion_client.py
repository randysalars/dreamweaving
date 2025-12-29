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
    
    print(f"Testing ID: {db_id}")
    
    try:
        print("Inspecting child: 2d52bab3-796d-80ee-b6d8-f5a75a681746 (Ways to find work)")
        child = client.pages.retrieve("2d52bab3-796d-80ee-b6d8-f5a75a681746")
        pprint(child.get("properties"))
        pprint(child.get("parent"))
    
    except Exception as ie:
        print(f"Inner Error: {ie}")

except Exception as e:
    print(f"Outer Error: {e}")
