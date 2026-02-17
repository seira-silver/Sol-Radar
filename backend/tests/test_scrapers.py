"""Tests for scraper modules."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.scrapers.url_resolver import (
    extract_article_links,
    extract_main_content,
    extract_title,
    _is_followable,
)
from app.scrapers.rate_limiter import TokenBucketRateLimiter
from app.scrapers.coingecko_scraper import _build_coin_summary
from app.scrapers.github_scraper import _build_repo_summary
from app.utils.helpers import content_hash, build_tweet_url, clean_text, resolve_url


# --- URL Resolver Tests ---


class TestExtractArticleLinks:
    def test_extracts_relative_links(self):
        html = """
        <html><body>
            <a href="/blog/post-1">Post 1</a>
            <a href="/blog/post-2">Post 2</a>
        </body></html>
        """
        links = extract_article_links(html, "https://example.com")
        assert "https://example.com/blog/post-1" in links
        assert "https://example.com/blog/post-2" in links

    def test_extracts_absolute_links(self):
        html = """
        <html><body>
            <a href="https://example.com/blog/post-1">Post 1</a>
        </body></html>
        """
        links = extract_article_links(html, "https://example.com")
        assert "https://example.com/blog/post-1" in links

    def test_skips_navigation_links(self):
        html = """
        <html><body>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
            <a href="/blog/real-post">Real Post</a>
        </body></html>
        """
        links = extract_article_links(html, "https://example.com")
        assert "https://example.com/blog/real-post" in links
        assert "https://example.com/about" not in links
        assert "https://example.com/contact" not in links

    def test_skips_twitter_links(self):
        html = """
        <html><body>
            <a href="https://twitter.com/solana">Twitter</a>
            <a href="/blog/real-post">Real Post</a>
        </body></html>
        """
        links = extract_article_links(html, "https://example.com")
        assert len(links) == 1
        assert "https://example.com/blog/real-post" in links

    def test_deduplicates_links(self):
        html = """
        <html><body>
            <a href="/blog/post-1">Post 1</a>
            <a href="/blog/post-1">Post 1 Again</a>
        </body></html>
        """
        links = extract_article_links(html, "https://example.com")
        assert len(links) == 1


class TestExtractMainContent:
    def test_extracts_article_content(self):
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <nav><a href="/">Home</a></nav>
            <article>
                <h1>Main Article</h1>
                <p>This is the main content of the article.</p>
            </article>
            <footer>Copyright 2025</footer>
        </body>
        </html>
        """
        content = extract_main_content(html)
        assert "Main Article" in content
        assert "main content" in content
        assert "Copyright" not in content

    def test_strips_scripts_and_styles(self):
        html = """
        <html><body>
            <script>alert('hi')</script>
            <style>.hidden{display:none}</style>
            <p>Visible content</p>
        </body></html>
        """
        content = extract_main_content(html)
        assert "alert" not in content
        assert "hidden" not in content
        assert "Visible content" in content


class TestExtractTitle:
    def test_extracts_og_title(self):
        html = '<html><head><meta property="og:title" content="OG Title"></head><body></body></html>'
        assert extract_title(html) == "OG Title"

    def test_extracts_h1(self):
        html = "<html><body><h1>H1 Title</h1></body></html>"
        assert extract_title(html) == "H1 Title"

    def test_extracts_title_tag(self):
        html = "<html><head><title>Page Title</title></head><body></body></html>"
        assert extract_title(html) == "Page Title"

    def test_returns_none_for_empty(self):
        html = "<html><body></body></html>"
        assert extract_title(html) is None


class TestIsFollowable:
    def test_same_domain(self):
        assert _is_followable("https://example.com/blog/post", "https://example.com") is True

    def test_different_domain_rejected(self):
        assert _is_followable("https://other.com/page", "https://example.com") is False

    def test_login_rejected(self):
        assert _is_followable("https://example.com/login", "https://example.com") is False

    def test_pdf_rejected(self):
        assert _is_followable("https://example.com/doc.pdf", "https://example.com") is False


# --- Helper Tests ---


class TestHelpers:
    def test_content_hash_deterministic(self):
        h1 = content_hash("hello world")
        h2 = content_hash("hello world")
        assert h1 == h2

    def test_content_hash_differs_for_different_input(self):
        h1 = content_hash("hello")
        h2 = content_hash("world")
        assert h1 != h2

    def test_build_tweet_url(self):
        url = build_tweet_url("@solana", "12345")
        assert url == "https://x.com/solana/status/12345"

    def test_build_tweet_url_no_at(self):
        url = build_tweet_url("solana", "12345")
        assert url == "https://x.com/solana/status/12345"

    def test_clean_text(self):
        result = clean_text("  hello   world  \n\n  test  ")
        assert result == "hello world test"

    def test_resolve_url(self):
        result = resolve_url("https://example.com/blog", "/blog/post-1")
        assert result == "https://example.com/blog/post-1"


# --- Rate Limiter Tests ---


class TestTokenBucketRateLimiter:
    @pytest.mark.asyncio
    async def test_allows_burst(self):
        limiter = TokenBucketRateLimiter(rate=10.0, max_tokens=5, name="test")
        # Should allow 5 immediate requests
        for _ in range(5):
            await limiter.acquire()

    @pytest.mark.asyncio
    async def test_rate_limits(self):
        import time

        limiter = TokenBucketRateLimiter(rate=2.0, max_tokens=2, name="test")
        # Drain the bucket
        await limiter.acquire()
        await limiter.acquire()

        # Next request should wait
        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.4  # Should wait ~0.5s for a token at rate=2/s


class TestCoinGeckoSummary:
    def test_build_coin_summary_includes_name_and_symbol(self):
        coin = {
            "item": {
                "name": "Solana",
                "symbol": "SOL",
                "market_cap_rank": 5,
                "coingecko_rank": 3,
                "price_btc": 0.00123,
                "score": 42,
                "id": "solana",
            }
        }
        title, summary = _build_coin_summary(coin)
        assert "Solana (SOL)" in title
        assert "CoinGecko trending rank" in summary
        assert "Market cap rank" in summary
        assert "CoinGecko page:" in summary


class TestGithubSummary:
    def test_build_repo_summary_uses_full_name_and_pushed_at(self):
        repo = {
            "full_name": "solana-labs/solana",
            "description": "Solana core protocol",
            "stargazers_count": 1000,
            "forks_count": 200,
            "open_issues_count": 10,
            "language": "Rust",
            "pushed_at": "2026-02-17T00:00:00Z",
            "html_url": "https://github.com/solana-labs/solana",
            "topics": ["solana", "blockchain"],
        }
        readme_snippet = "Solana is a high-performance blockchain."
        title, summary, key = _build_repo_summary(repo, readme_snippet)
        assert "solana-labs/solana" in title
        assert "Solana context" in summary
        assert "Solana is a high-performance blockchain" in summary
        assert "solana-labs/solana" in key
