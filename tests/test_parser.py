from naver_craw.parser import parse_search_html


def test_parse_search_html_extracts_naver_links() -> None:
    html = """
    <html><body>
      <a href="https://blog.naver.com/example">예제 블로그</a>
      <a href="https://news.naver.com/article">예제 뉴스</a>
      <a href="https://example.com/nope">제외</a>
    </body></html>
    """

    results = parse_search_html(html)

    assert [item.title for item in results] == ["예제 블로그", "예제 뉴스"]
    assert results[0].url == "https://blog.naver.com/example"
