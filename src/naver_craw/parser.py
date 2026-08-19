"""HTML parsing helpers for NAVER search pages."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .models import SearchResult


def parse_search_html(html: str) -> list[SearchResult]:
    """Parse NAVER search HTML into normalized results.

    The parser intentionally uses resilient selectors and skips malformed
    entries so a minor page-layout change does not discard the whole result.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[SearchResult] = []

    for anchor in soup.select("a"):
        href = anchor.get("href")
        title = anchor.get_text(" ", strip=True)
        if not href or not title:
            continue
        if "search.naver.com" not in href and "blog.naver.com" not in href and "news.naver.com" not in href:
            continue
        if any(item.url == href for item in results):
            continue
        results.append(SearchResult(title=title, url=href))

    return results
