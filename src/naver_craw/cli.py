"""Command-line interface."""

from __future__ import annotations

import argparse
import json

from .crawler import NaverCrawler, SearchType


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NAVER search crawler")
    parser.add_argument("query", help="NAVER search query")
    parser.add_argument(
        "--type",
        dest="search_type",
        choices=[item.value for item in SearchType],
        default=SearchType.ALL.value,
        help="Search area: nexearch, blog, news, cafe",
    )
    parser.add_argument("--start", type=int, default=1, help="Search result start position")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds")
    parser.add_argument("--interval", type=float, default=0.5, help="Minimum delay between requests")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results = NaverCrawler(
        timeout=args.timeout,
        min_interval=args.interval,
    ).search(
        args.query,
        start=args.start,
        search_type=args.search_type,
    )
    print(json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
