from pathlib import Path

from naver_craw.parser import parse_search_html


FIXTURE = Path(__file__).parent / "fixtures" / "naver_search.html"


def test_parse_search_html_extracts_fixture_results() -> None:
    results = parse_search_html(FIXTURE.read_text(encoding="utf-8"))

    assert [item.title for item in results] == [
        "아이폰17 사용 후기",
        "아이폰17 관련 뉴스",
        "아이폰17 카페 글",
    ]
    assert results[0].source == "blog.naver.com"
    assert results[1].source == "news.naver.com"
    assert results[2].source == "cafe.naver.com"


def test_parse_search_html_deduplicates_urls_and_ignores_external_links() -> None:
    html = """
    <a href="https://blog.naver.com/example">예제 블로그</a>
    <a href="https://blog.naver.com/example">중복 링크</a>
    <a href="https://example.com/nope">외부 사이트</a>
    """

    results = parse_search_html(html)

    assert len(results) == 1
    assert results[0].url == "https://blog.naver.com/example"
