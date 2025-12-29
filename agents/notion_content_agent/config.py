import os
import sys
from dotenv import load_dotenv

# Load environment variables from Project Root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
dotenv_path = os.path.join(project_root, ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Fallback to local .env if root doesn't exist
    load_dotenv()

class Config:
    # Notion Configuration
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    # Default to the specific text-based articles DB if not overridden
    NOTION_DB_ID = os.getenv("NOTION_DB_ID", "2d52bab3-796d-802a-a041-e437f5c39f35")
    
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
        if not cls.NOTION_DB_ID:
            missing.append("NOTION_DB_ID")
        
        # We warn but don't fail for OpenAI key if likely using CLI fallback
        if not cls.OPENAI_API_KEY:
            print("WARNING: OPENAI_API_KEY not found. Ensure you have alternative authentication if not using API.")
            
        if missing:
            print(f"CRITICAL: Missing required environment variables: {', '.join(missing)}")
            return False
        return True

# Ensure output directory exists
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
