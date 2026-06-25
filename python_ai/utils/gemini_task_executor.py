import json
import logging
import functools
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

class GeminiTaskExecutor:
    """
    Centralizes Gemini invocation, retry logic, prompt assembly, and JSON parsing.
    Prevents duplication of API calls across components.
    """
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client

    @functools.lru_cache(maxsize=128)
    def _cached_execute(self, system_instruction: str, prompt: str) -> Optional[Any]:
        if not self.gemini_client:
            logger.warning("GeminiClient is unavailable.")
            return None

        try:
            full_prompt = f"{system_instruction}\n\nTask:\n{prompt}"
            response = self.gemini_client.generate_response(full_prompt)
            return self._parse_json(response)
        except Exception as e:
            logger.error(f"Error executing Gemini task: {e}", exc_info=True)
            return None

    def execute_task(self, system_instruction: str, prompt: str) -> Optional[Any]:
        """
        Executes a prompt against Gemini and parses the response as JSON.
        Returns None if the client is unavailable, execution fails, or parsing fails.
        """
        start_time = time.perf_counter()
        
        result = self._cached_execute(system_instruction, prompt)
        
        duration = time.perf_counter() - start_time
        cache_stats = self._cached_execute.cache_info()
        logger.info(f"Gemini task completed in {duration:.4f}s. Cache stats: {cache_stats}")
        
        return result

    def _parse_json(self, response_text: str) -> Optional[Any]:
        """
        Safely parses JSON responses, stripping any Markdown formatting.
        """
        try:
            cleaned = response_text.strip()
            # Strip Markdown JSON blocks if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}. Raw response: {response_text}")
            return None
