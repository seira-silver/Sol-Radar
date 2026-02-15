"""LiteLLM wrapper for Gemini Flash with rate limiting, retries, and JSON validation."""

import json
import asyncio
import os
from typing import Any

from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.scrapers.rate_limiter import gemini_limiter, xai_limiter
from app.utils.logger import logger

settings = get_settings()


class LLMClient:
    """Async LLM client using LiteLLM with Gemini Flash free tier."""

    def __init__(self):
        self.model = settings.LLM_MODEL
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_requests = 0

    def _active_model(self) -> str:
        # Allow changing model via env without restarting in dev.
        return get_settings().LLM_MODEL

    def _get_api_key(self, model: str) -> str:
        s = get_settings()
        if model.startswith("xai/"):
            return (s.XAI_API_KEY or s.GROK_API_KEY or "").strip()
        return (s.GEMINI_API_KEY or "").strip()

    async def _acquire_limiter(self, model: str) -> None:
        if model.startswith("xai/"):
            await xai_limiter.acquire()
        else:
            await gemini_limiter.acquire()

    async def generate_json(self, prompt: str, system_prompt: str = "") -> dict[str, Any] | None:
        """
        Send a prompt to Gemini and parse the response as JSON.

        Args:
            prompt: The user prompt with content to analyze.
            system_prompt: Optional system-level instruction.

        Returns:
            Parsed JSON dict, or None if parsing fails after retries.
        """
        model = self._active_model()
        api_key = self._get_api_key(model)

        # Respect rate limits (provider-specific)
        await self._acquire_limiter(model)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            raw_text = await self._call_llm(messages, model=model, api_key=api_key)
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
            await self._acquire_limiter(model)
            fix_text = await self._call_llm(
                [{"role": "user", "content": fix_prompt}],
                model=model,
                api_key=api_key,
            )
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
    async def _call_llm(self, messages: list[dict], model: str, api_key: str) -> str | None:
        """Call LiteLLM with retry logic."""
        try:
            # LiteLLM's xAI provider typically reads XAI_API_KEY from env.
            if model.startswith("xai/") and api_key:
                os.environ["XAI_API_KEY"] = api_key

            response = await acompletion(
                model=model,
                messages=messages,
                api_key=api_key or None,
                temperature=0.3,
                max_tokens=8192,
                # Hint to providers that support it to return strict JSON
                response_format={"type": "json_object"},
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
            "xai_requests_used": xai_limiter.total_requests,
        }


# Singleton instance
llm_client = LLMClient()
