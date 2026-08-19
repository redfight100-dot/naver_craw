import os

import pytest

from naver_craw.crawler import NaverCrawler, SearchType


@pytest.mark.skipif(
    os.getenv("NAVER_LIVE_TEST") != "1",
    reason="set NAVER_LIVE_TEST=1 to run against the live NAVER service",
)
def test_live_naver_blog_search() -> None:
    results = NaverCrawler(timeout=15, min_interval=0).search(
        "아이폰17",
        search_type=SearchType.BLOG,
    )

    assert results, "NAVER returned no parsed blog results"
    assert all(result.url.startswith("http") for result in results)
