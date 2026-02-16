"""Pydantic schemas for the Seira chat endpoint."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Message sender role")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, description="Conversation history")
    url: str | None = Field(None, description="Optional URL for Seira to scrape and analyze")
