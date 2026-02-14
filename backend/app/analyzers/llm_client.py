"""LiteLLM wrapper for Gemini Flash with rate limiting, retries, and JSON validation."""

import json
import asyncio
from typing import Any

from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.scrapers.rate_limiter import gemini_limiter
from app.utils.logger import logger

settings = get_settings()


class LLMClient:
    """Async LLM client using LiteLLM with Gemini Flash free tier."""

    def __init__(self):
        self.model = settings.LLM_MODEL
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_requests = 0

    async def generate_json(self, prompt: str, system_prompt: str = "") -> dict[str, Any] | None:
        """
        Send a prompt to Gemini and parse the response as JSON.

        Args:
            prompt: The user prompt with content to analyze.
            system_prompt: Optional system-level instruction.

        Returns:
            Parsed JSON dict, or None if parsing fails after retries.
        """
        # Respect rate limits
        await gemini_limiter.acquire()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            raw_text = await self._call_llm(messages)
            if raw_text is None:
                return None

            parsed = self._parse_json_response(raw_text)
            if parsed is not None:
                self.total_requests += 1
                return parsed

            # If first parse fails, ask LLM to fix the JSON
            logger.warning("Initial JSON parse failed — requesting LLM fix")
            fix_prompt = (
                "The following text should be valid JSON but has syntax errors. "
                "Fix it and return ONLY valid JSON, no explanation:\n\n"
                f"{raw_text[:3000]}"
            )
            await gemini_limiter.acquire()
            fix_text = await self._call_llm([{"role": "user", "content": fix_prompt}])
            if fix_text:
                parsed = self._parse_json_response(fix_text)
                if parsed is not None:
                    self.total_requests += 1
                    return parsed

            logger.error("Failed to get valid JSON after retry")
            return None

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    async def _call_llm(self, messages: list[dict]) -> str | None:
        """Call LiteLLM with retry logic."""
        try:
            response = await acompletion(
                model=self.model,
                messages=messages,
                api_key=settings.GEMINI_API_KEY,
                temperature=0.3,
                max_tokens=8192,
            )

            # Track usage
            usage = response.get("usage", {})
            self.total_prompt_tokens += usage.get("prompt_tokens", 0)
            self.total_completion_tokens += usage.get("completion_tokens", 0)

            content = response["choices"][0]["message"]["content"]
            return content

        except Exception as e:
            error_str = str(e).lower()
            if "rate_limit" in error_str or "429" in error_str:
                logger.warning(f"Gemini rate limit hit, backing off: {e}")
                await asyncio.sleep(10)
            raise

    def _parse_json_response(self, text: str) -> dict[str, Any] | None:
        """Extract and parse JSON from LLM response text."""
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in the text
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                pass

        return None

    @property
    def usage_summary(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "gemini_requests_used": gemini_limiter.total_requests,
        }


# Singleton instance
llm_client = LLMClient()
