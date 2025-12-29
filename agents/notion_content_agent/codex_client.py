import os
import time
import logging
import threading
from typing import List, Optional
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple token bucket rate limiter for API calls."""

    def __init__(self, requests_per_minute: int = 20):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute  # Seconds between requests
        self.last_request_time = 0.0
        self._lock = threading.Lock()

    def wait_if_needed(self) -> float:
        """
        Wait if necessary to comply with rate limit.

        Returns:
            Time waited in seconds
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_request_time
            wait_time = max(0, self.min_interval - elapsed)

            if wait_time > 0:
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                time.sleep(wait_time)

            self.last_request_time = time.time()
            return wait_time


class CodexClient:
    """
    Interface for the Content Generation AI.
    "Codex" here refers to the LLM backend (GPT-4/o1 via OpenAI API).
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-4",
        base_url: str = None,
        requests_per_minute: int = 20
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model

        # Rate limiting
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.total_tokens_used = 0

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

        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

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
            )

            elapsed = time.time() - start_time

            # Track token usage if available
            if hasattr(response, 'usage') and response.usage:
                self.total_tokens_used += response.usage.total_tokens
                logger.info(
                    f"Codex response received in {elapsed:.2f}s "
                    f"(tokens: {response.usage.total_tokens})"
                )
            else:
                logger.info(f"Codex response received in {elapsed:.2f}s")

            return response.choices[0].message.content
        except OpenAIError as e:
            logger.error(f"OpenAI API Error: {e}")
            if "rate_limit" in str(e).lower():
                logger.warning("Rate limit hit. Waiting 60s before retry...")
                time.sleep(60)
                # Retry once after rate limit wait
                return self.generate_article_content(prompt, system_instruction)
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
    def extract_tasks_from_page(self, page_content: str) -> list:
        """
        Uses LLM to analyze a Notion page's content and extract actionable article tasks.
        Returns a list of dicts: identifier, title, instructions, status.
        """
        prompt = (
            "Analyze the following Notion page content and identify any tasks, articles, or topics "
            "that are clearly marked as 'Ready to Write', 'To Do', or represent pending content work. "
            "Ignore items already marked as Done.\n\n"
            "Return ONLY a raw JSON list of objects with these keys: 'title', 'instructions' (context), 'status'.\n"
            "If the page contains a list of links, treat them as research references unless explicitly tasked.\n"
            "If the page just lists concepts, infer if they are article topics.\n\n"
            f"--- PAGE CONTENT ---\n{page_content[:20000]}\n--- END CONTENT ---"
        )
        
        system_instruction = "You are a project manager parsing a document for tasks. Output valid JSON only."
        
        try:
            response_text = self.generate_article_content(prompt, system_instruction)
            # Naive cleanup for Code Blocks if LLM wraps in ```json ... ```
            clean_text = response_text.replace("```json", "").replace("```", "").strip()

            import json
            tasks = json.loads(clean_text)
            if isinstance(tasks, list):
                return tasks
            return []
        except Exception as e:
            logger.warning(f"Failed to extract tasks via LLM: {e}")
            return []

    def categorize_article(
        self,
        title: str,
        content: str,
        available_sections: List[str]
    ) -> str:
        """
        Use AI to categorize an article into an appropriate hub section.

        Args:
            title: Article title
            content: Article content (will use first 1500 chars)
            available_sections: List of existing section names on the hub

        Returns:
            Section name (existing or new suggestion, 2-4 words max)
        """
        if not available_sections:
            available_sections = ["General"]

        sections_str = ", ".join(available_sections)
        content_preview = content[:1500] if len(content) > 1500 else content

        prompt = f"""Categorize this article into the BEST matching section for a website hub page.

Available sections: {sections_str}

IMPORTANT:
- Choose the section that best matches the article's main topic
- If the article is about AI tools/productivity → "AI Productivity" or "Daily Work"
- If the article is about automation/workflows → "Automation"
- If the article is about business strategy → "Strategy"
- If none of these fit well, suggest a NEW specific section name (2-4 words, title case)
- AVOID using "General" unless absolutely nothing else fits

Article Title: {title}
Content Preview: {content_preview}

Return ONLY the section name. Nothing else. No quotes, no explanation."""

        system_instruction = (
            "You categorize articles into topic sections for a website. "
            "Be concise and consistent. Return only the section name."
        )

        try:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # Lower for consistency
                # Note: max_tokens removed for compatibility with newer models (gpt-5.x)
                # The response is naturally short (section name only)
            )

            # Track tokens
            if hasattr(response, 'usage') and response.usage:
                self.total_tokens_used += response.usage.total_tokens

            result = response.choices[0].message.content.strip()
            # Clean up any quotes or extra formatting
            result = result.strip('"\'').strip()
            logger.info(f"Article categorized as: '{result}'")
            return result

        except Exception as e:
            logger.warning(f"Failed to categorize article: {e}. Using 'General'.")
            return "General"
