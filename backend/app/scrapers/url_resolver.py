"""URL resolution and link extraction from HTML pages."""

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def extract_article_links(html: str, base_url: str, selectors: list[str] | None = None) -> list[str]:
    """
    Extract article/blog post links from an index page.

    Args:
        html: Raw HTML content.
        base_url: Base URL for resolving relative links.
        selectors: Optional CSS selectors to narrow link extraction.

    Returns:
        List of absolute URLs to follow (depth 2).
    """
    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    seen: set[str] = set()

    # If selectors provided, search within those containers
    if selectors:
        containers = []
        for sel in selectors:
            containers.extend(soup.select(sel))
    else:
        containers = [soup]

    for container in containers:
        for a_tag in container.find_all("a", href=True):
            href = a_tag["href"]
            absolute = urljoin(base_url, href)

            # Filter: only same-domain, skip navigational/login/media links
            if not _is_followable(absolute, base_url):
                continue

            if absolute not in seen:
                seen.add(absolute)
                links.append(absolute)

    return links


def _is_followable(url: str, base_url: str) -> bool:
    """Check if a URL should be followed for deep link scraping."""
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)

    # Must be same domain
    if parsed.netloc and parsed.netloc != base_parsed.netloc:
        return False

    # Must be HTTP(S)
    if parsed.scheme and parsed.scheme not in ("http", "https", ""):
        return False

    # Skip common non-content paths
    skip_patterns = [
        "/login", "/signup", "/register", "/auth", "/account",
        "/contact", "/about", "/privacy", "/terms", "/careers",
        "/tag/", "/category/", "/author/", "/page/",
        ".pdf", ".png", ".jpg", ".gif", ".svg", ".css", ".js",
        "#", "mailto:", "javascript:",
        "twitter.com", "x.com", "discord.com", "t.me",
    ]
    url_lower = url.lower()
    for pattern in skip_patterns:
        if pattern in url_lower:
            return False

    return True


def extract_main_content(html: str) -> str:
    """
    Extract the main readable content from an HTML page.

    Strips navigation, footer, scripts, styles, and returns clean text.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]):
        tag.decompose()

    # Try to find main content area
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_=lambda c: c and ("content" in c.lower() or "post" in c.lower() or "article" in c.lower()))
        or soup.find("body")
    )

    if main is None:
        return soup.get_text(separator="\n", strip=True)

    return main.get_text(separator="\n", strip=True)


def extract_title(html: str) -> str | None:
    """Extract page title from HTML."""
    soup = BeautifulSoup(html, "lxml")

    # Try og:title first, then <title>
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    title = soup.find("title")
    if title:
        return title.get_text(strip=True)

    return None
