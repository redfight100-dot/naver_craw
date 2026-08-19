"""Domain models for NAVER crawling."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class SearchResult:
    """A normalized NAVER search result."""

    title: str
    url: str
    description: str = ""
    source: str = ""
    published_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
