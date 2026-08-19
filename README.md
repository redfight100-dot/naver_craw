# NAVER Crawler

A small Python toolkit for normalized NAVER search crawling.

## Features

- NAVER web search requests
- Normalized result titles and URLs
- JSON CLI output
- Parser/model unit tests

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.

## Usage

```bash
naver-craw "iPhone 17"
```

or:

```bash
python -m naver_craw.cli "iPhone 17" --start 1
```

The command writes UTF-8 JSON to stdout.

## Structure

```text
src/naver_craw/
├── crawler.py   # HTTP client
├── parser.py    # HTML → model conversion
├── models.py    # data model
└── cli.py       # command line interface

tests/
├── test_parser.py
└── test_models.py
```

## Roadmap

1. Separate blog/news/cafe extraction
2. Pagination
3. Stronger URL normalization and deduplication
4. SQLite/CSV/JSON storage
5. Retry, rate limiting, and structured logging
6. Keyword/SEO analysis API
7. n8n-friendly JSON output

> Use the crawler in compliance with NAVER terms, robots policies, and the access policies applicable to the target pages.
