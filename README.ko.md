# NAVER Crawler

Python 기반 NAVER 검색 크롤러입니다.

## 현재 기능

- NAVER 통합/블로그/뉴스/카페 검색 요청
- 검색 결과 URL/제목/출처 정규화
- URL 중복 제거
- HTTP retry/backoff
- 요청 간 최소 간격(rate pacing)
- JSON 출력 CLI
- HTML fixture 기반 parser 테스트
- 수동 실행 가능한 실서비스 smoke test

## 설치

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e '.[dev]'
```

## 사용

전체 검색:

```bash
naver-craw "아이폰17"
```

블로그:

```bash
naver-craw "아이폰17" --type blog
```

뉴스:

```bash
naver-craw "아이폰17" --type news
```

카페:

```bash
naver-craw "아이폰17" --type cafe
```

페이지 시작 위치와 요청 간격:

```bash
naver-craw "아이폰17" --type blog --start 1 --interval 0.5 --timeout 15
```

결과는 UTF-8 JSON으로 출력됩니다.

## 테스트

로컬 단위 테스트:

```bash
pytest -q
```

현재 검증된 핵심 테스트 결과:

```text
7 passed in 0.17s
```

실서비스 smoke test는 외부 네트워크가 허용된 환경에서만 실행합니다.

```bash
NAVER_LIVE_TEST=1 pytest -q tests/test_live.py -rs
```

GitHub Actions에서는 `workflow_dispatch`로 수동 실행할 때 live smoke test를 수행하도록 구성되어 있습니다.

## 개발 구조

```text
src/naver_craw/
├── crawler.py   # HTTP client / retry / pacing / search type
├── parser.py    # HTML → normalized result
├── models.py    # data model
└── cli.py       # CLI

tests/
├── fixtures/naver_search.html
├── test_parser.py
├── test_models.py
├── test_crawler.py
└── test_live.py
```

여러 AI가 이어서 작업할 때는 `docs/AI_CONTEXT.md`와 `docs/AI_WORKLOG.md`를 먼저 확인하세요.

## 현재 알려진 제한

현재 ChatGPT sandbox에서는 `search.naver.com` 외부 DNS 접근이 제한되어 실서비스 호출 성공을 직접 검증하지 못했습니다. 따라서 현재 단계는 **로컬 단위 테스트 PASS / 실서비스 통합 테스트 미완료**입니다.

실제 NAVER 응답 HTML을 확보할 수 있는 환경에서는 selector와 blog/news/cafe 영역별 필드 추출을 추가 검증해야 합니다.

> NAVER 서비스 이용약관, robots 정책 및 대상 페이지의 접근 정책을 준수하여 사용하세요.
