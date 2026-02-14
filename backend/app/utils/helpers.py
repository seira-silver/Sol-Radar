"""Shared utility functions."""

import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def content_hash(text: str) -> str:
    """SHA-256 hash of text content for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_url(base_url: str, relative_url: str) -> str:
    """Resolve a relative URL against a base URL."""
    return urljoin(base_url, relative_url)


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc


def clean_text(text: str) -> str:
    """Clean scraped text: collapse whitespace, strip."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 15000) -> str:
    """Truncate text to max characters for LLM context windows."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... content truncated ...]"


def build_tweet_url(username: str, tweet_id: str) -> str:
    """Build a Twitter/X URL from username and tweet ID."""
    clean_username = username.lstrip("@")
    return f"https://x.com/{clean_username}/status/{tweet_id}"
