"""Command-line interface."""

from __future__ import annotations

import argparse
import json

from .crawler import NaverCrawler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NAVER search crawler")
    parser.add_argument("query", help="NAVER search query")
    parser.add_argument("--start", type=int, default=1, help="Search result start position")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results = NaverCrawler(timeout=args.timeout).search(args.query, start=args.start)
    print(json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
