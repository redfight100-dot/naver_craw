from types import SimpleNamespace

import pytest

from naver_craw.crawler import NaverCrawler, SearchType


class FakeResponse:
    apparent_encoding = "utf-8"
    encoding = "utf-8"
    text = '<a href="https://blog.naver.com/example">예제</a>'

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self) -> None:
        self.headers = {}
        self.calls: list[tuple[str, dict, float]] = []

    def mount(self, *_args, **_kwargs) -> None:
        return None

    def get(self, url: str, *, timeout: float):
        self.calls.append((url, {}, timeout))
        return FakeResponse()


def test_search_builds_expected_area_url() -> None:
    crawler = NaverCrawler(min_interval=0)
    fake = FakeSession()
    crawler.session = fake  # type: ignore[assignment]

    results = crawler.search("테스트", search_type=SearchType.BLOG)

    assert results[0].url == "https://blog.naver.com/example"
    assert "where=blog" in fake.calls[0][0]
    assert "query=%ED%85%8C%EC%8A%A4%ED%8A%B8" in fake.calls[0][0]


@pytest.mark.parametrize("value", ["", "   "])
def test_search_rejects_empty_query(value: str) -> None:
    with pytest.raises(ValueError, match="query must not be empty"):
        NaverCrawler().search(value)


def test_search_rejects_invalid_area() -> None:
    with pytest.raises(ValueError, match="unsupported search_type"):
        NaverCrawler().search("테스트", search_type="invalid")
