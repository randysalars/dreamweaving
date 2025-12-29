import os
import time
import logging
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

class CodexClient:
    """
    Interface for the Content Generation AI. 
    "Codex" here refers to the LLM backend (GPT-4/o1 via OpenAI API).
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4", base_url: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model
        
        if not self.api_key and not self.base_url:
            logger.warning("No API Key or Base URL provided. CodexClient might fail.")
        
        # Initialize client with optional base_url for flexible backend support
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if (self.api_key or self.base_url) else None

    def generate_article_content(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generates article content from a prompt.
        Authentication: Uses OpenAI API Key.
        """
        if not self.client:
            raise RuntimeError("CodexClient is not initialized with an API Key.")

        default_system = (
            "You are an expert content writer and SEO specialist. "
            "Write comprehensive, high-quality, and engaging articles based on the provided specifications. "
            "Use Markdown formatting."
        )
        
        try:
            logger.info(f"Sending request to Codex (Model: {self.model})...")
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction or default_system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                # Increase max_tokens if needed for very long articles, though models usually handle context well now
            )
            
            elapsed = time.time() - start_time
            logger.info(f"Codex response received in {elapsed:.2f}s")
            
            return response.choices[0].message.content
        except OpenAIError as e:
            logger.error(f"OpenAI API Error: {e}")
            if "rate_limit" in str(e):
                logger.warning("Rate limit hit. Waiting 60s before retry (handled by caller preferably).")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in Codex generation: {e}")
            raise

    def generate_monetization_content(self, context_snippet: str, type: str) -> str:
        """
        Specialized generation for ads or landing page copy.
        """
        prompt = f"Write a high-converting {type} based on this context: '{context_snippet}'"
        return self.generate_article_content(prompt, system_instruction="You are a direct-response copywriter focused on conversion.")
