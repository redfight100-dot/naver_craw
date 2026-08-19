from naver_craw.models import SearchResult


def test_search_result_to_dict() -> None:
    result = SearchResult(title="제목", url="https://example.com", source="blog")
    assert result.to_dict() == {
        "title": "제목",
        "url": "https://example.com",
        "description": "",
        "source": "blog",
        "published_at": "",
    }
