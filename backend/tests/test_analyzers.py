"""Tests for LLM analyzer modules."""

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock

from app.analyzers.llm_client import LLMClient


class TestLLMClientJsonParsing:
    """Test JSON extraction from LLM responses."""

    def setup_method(self):
        self.client = LLMClient()

    def test_parse_clean_json(self):
        text = '{"signals": [], "total_signals_found": 0}'
        result = self.client._parse_json_response(text)
        assert result == {"signals": [], "total_signals_found": 0}

    def test_parse_json_with_markdown_fences(self):
        text = '```json\n{"signals": [], "total_signals_found": 0}\n```'
        result = self.client._parse_json_response(text)
        assert result == {"signals": [], "total_signals_found": 0}

    def test_parse_json_with_preamble(self):
        text = 'Here is the analysis:\n{"signals": [{"signal_title": "test"}], "total_signals_found": 1}'
        result = self.client._parse_json_response(text)
        assert result is not None
        assert result["total_signals_found"] == 1

    def test_parse_invalid_json_returns_none(self):
        text = "This is not JSON at all"
        result = self.client._parse_json_response(text)
        assert result is None

    def test_parse_json_with_triple_backticks_no_lang(self):
        text = '```\n{"key": "value"}\n```'
        result = self.client._parse_json_response(text)
        assert result == {"key": "value"}

    def test_parse_nested_json(self):
        data = {
            "narratives": [
                {
                    "title": "DeFi Surge",
                    "product_ideas": [
                        {"title": "Idea 1", "description": "desc"}
                    ],
                }
            ],
            "total_narratives_found": 1,
        }
        text = json.dumps(data)
        result = self.client._parse_json_response(text)
        assert result is not None
        assert result["narratives"][0]["title"] == "DeFi Surge"


class TestLLMClientGenerate:
    """Test the generate_json method with mocked LiteLLM."""

    @pytest.mark.asyncio
    async def test_generate_json_success(self):
        client = LLMClient()
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"signals": [], "total_signals_found": 0}'
                    }
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }

        with patch("app.analyzers.llm_client.acompletion", new_callable=AsyncMock) as mock_llm:
            with patch("app.analyzers.llm_client.gemini_limiter") as mock_limiter:
                mock_limiter.acquire = AsyncMock()
                mock_llm.return_value = mock_response

                result = await client.generate_json("test prompt")

                assert result is not None
                assert result["total_signals_found"] == 0

    @pytest.mark.asyncio
    async def test_generate_json_returns_none_on_failure(self):
        client = LLMClient()

        with patch("app.analyzers.llm_client.acompletion", new_callable=AsyncMock) as mock_llm:
            with patch("app.analyzers.llm_client.gemini_limiter") as mock_limiter:
                mock_limiter.acquire = AsyncMock()
                mock_llm.side_effect = Exception("API error")

                result = await client.generate_json("test prompt")
                assert result is None
