"""HTML parsing helpers for NAVER search pages."""

from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .models import SearchResult

_ALLOWED_HOSTS = {
    "blog.naver.com",
    "m.blog.naver.com",
    "news.naver.com",
    "n.news.naver.com",
    "cafe.naver.com",
}


def _is_naver_content_url(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host in _ALLOWED_HOSTS or host.endswith(".naver.com") and any(
        host.startswith(prefix)
        for prefix in ("blog.", "news.", "cafe.", "m.")
    )


def _clean_title(text: str) -> str:
    return " ".join(text.split())


def parse_search_html(html: str) -> list[SearchResult]:
    """Parse NAVER search HTML into normalized content results.

    The parser prefers result containers/classes but keeps fallback selectors
    because NAVER can change markup between result areas and releases.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[SearchResult] = []
    seen_urls: set[str] = set()

    selectors = [
        "li.bx",
        "div.total_wrap",
        "div.api_subject_bx",
        "div.api_txt_lines",
    ]

    anchors = []
    for selector in selectors:
        for container in soup.select(selector):
            anchors.extend(container.select("a[href]"))

    if not anchors:
        anchors = soup.select("a[href]")

    for anchor in anchors:
        href = anchor.get("href", "").strip()
        title = _clean_title(anchor.get_text(" ", strip=True))
        if not href or not title or href in seen_urls:
            continue
        if not href.startswith(("http://", "https://")) or not _is_naver_content_url(href):
            continue
        if len(title) < 2:
            continue

        seen_urls.add(href)
        source = urlparse(href).hostname or ""
        results.append(SearchResult(title=title, url=href, source=source))

    return results
