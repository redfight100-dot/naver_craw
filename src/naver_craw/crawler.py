"""HTTP client for NAVER search."""

from __future__ import annotations

import time
from enum import StrEnum
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import SearchResult
from .parser import parse_search_html


class SearchType(StrEnum):
    ALL = "nexearch"
    BLOG = "blog"
    NEWS = "news"
    CAFE = "cafe"


class NaverCrawler:
    """Reusable NAVER search client with retry and request pacing."""

    BASE_URL = "https://search.naver.com/search.naver"

    def __init__(
        self,
        timeout: float = 10.0,
        user_agent: str | None = None,
        min_interval: float = 0.5,
    ) -> None:
        self.timeout = timeout
        self.min_interval = max(0.0, min_interval)
        self._last_request_at = 0.0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/151.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def _pace(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        wait = self.min_interval - elapsed
        if wait > 0:
            time.sleep(wait)

    def search(
        self,
        query: str,
        start: int = 1,
        search_type: SearchType | str = SearchType.ALL,
    ) -> list[SearchResult]:
        """Return normalized NAVER search results."""
        query = query.strip()
        if not query:
            raise ValueError("query must not be empty")
        if start < 1:
            raise ValueError("start must be >= 1")

        try:
            search_type = SearchType(search_type)
        except ValueError as exc:
            allowed = ", ".join(item.value for item in SearchType)
            raise ValueError(f"unsupported search_type; choose from: {allowed}") from exc

        params = {"where": search_type.value, "query": query, "start": start}
        self._pace()
        response = self.session.get(
            f"{self.BASE_URL}?{urlencode(params)}",
            timeout=self.timeout,
        )
        self._last_request_at = time.monotonic()
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        return parse_search_html(response.text)
