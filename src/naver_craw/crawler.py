"""HTTP client for NAVER search."""

from __future__ import annotations

from urllib.parse import urlencode

import requests

from .models import SearchResult
from .parser import parse_search_html


class NaverCrawler:
    """Small, reusable NAVER search crawler."""

    BASE_URL = "https://search.naver.com/search.naver"

    def __init__(self, timeout: float = 10.0, user_agent: str | None = None) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/151.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            }
        )

    def search(self, query: str, start: int = 1) -> list[SearchResult]:
        """Return normalized results from a NAVER web search."""
        if not query.strip():
            raise ValueError("query must not be empty")
        if start < 1:
            raise ValueError("start must be >= 1")

        params = {"where": "nexearch", "query": query, "start": start}
        response = self.session.get(
            f"{self.BASE_URL}?{urlencode(params)}", timeout=self.timeout
        )
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        return parse_search_html(response.text)
