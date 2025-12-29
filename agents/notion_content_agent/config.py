import os
import sys
from dotenv import load_dotenv

# Load environment variables from Project Root
# Go up 2 levels: agents -> dreamweaving
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
dotenv_path = os.path.join(project_root, ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Fallback to local .env if root doesn't exist
    load_dotenv()

class Config:
    # Notion Configuration
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    # Default to None so we can prompt the user if missing
    NOTION_DB_ID = os.getenv("NOTION_DB_ID")
    
    # AI Configuration
    # Defaults to using OpenAI API directly as the most stable "Codex" interface
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") # Support for custom endpoints (e.g. Ollama, updates)
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Feature Flags
    ENABLE_MONETIZATION = os.getenv("ENABLE_MONETIZATION", "true").lower() == "true"
    
    # Paths
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(os.getcwd(), "output"))

    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        missing = []
        if not cls.NOTION_TOKEN:
            missing.append("NOTION_TOKEN")
        # We allow NOTION_DB_ID to be missing so we can prompt for it interactively
        # if not cls.NOTION_DB_ID:
        #    missing.append("NOTION_DB_ID")
        
        # We warn but don't fail for OpenAI key if likely using CLI fallback
        if not cls.OPENAI_API_KEY and not cls.OPENAI_BASE_URL:
             print("WARNING: OPENAI_API_KEY not found. Ensure you have alternative authentication if not using API.")
            
        if missing:
            print(f"CRITICAL: Missing required environment variables: {', '.join(missing)}")
            return False
        return True

# Ensure output directory exists
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
