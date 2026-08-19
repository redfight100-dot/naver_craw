# AI Context — NAVER Crawler

> 이 문서는 이 저장소를 작업하는 여러 AI 에이전트가 공유하는 **정본 작업 컨텍스트(Canonical Context)** 입니다.
> 새 AI가 작업을 시작하면 먼저 `AGENTS.md`와 이 문서를 읽고, 현재 GitHub `main`의 최신 commit을 기준으로 상태를 다시 확인해야 합니다.

## 1. 프로젝트 목적

`naver_craw`는 NAVER 검색/콘텐츠 데이터를 수집하고 정규화한 뒤, 향후 SEO 분석과 n8n/AI 콘텐츠 자동화까지 연결하기 위한 Python 기반 크롤링 프로젝트입니다.

최종 방향:

```text
NAVER 검색/콘텐츠
      ↓
수집(Crawling)
      ↓
정규화/중복 제거
      ↓
저장(JSON / SQLite / CSV)
      ↓
키워드·SEO 분석
      ↓
n8n / LLM 연동
      ↓
콘텐츠 자동화
```

## 2. 현재 구현 상태

현재 구현은 NAVER 웹 검색을 HTTP로 요청하고 HTML에서 NAVER 콘텐츠 링크를 정규화하는 단계입니다.

구현 파일:

```text
src/naver_craw/
├── __init__.py    # 패키지 버전
├── crawler.py     # requests 기반 NAVER 검색 HTTP 클라이언트
├── parser.py      # BeautifulSoup 기반 HTML 파서
├── models.py      # SearchResult 데이터 모델
└── cli.py         # JSON 출력 CLI

tests/
├── fixtures/naver_search.html
├── test_parser.py
├── test_models.py
├── test_crawler.py
└── test_live.py   # 환경변수로 활성화하는 실서비스 smoke test
```

프로젝트 설정:

- `pyproject.toml`
- `requirements.txt`
- Python `>=3.11`
- `requests>=2.32,<3`
- `beautifulsoup4>=4.12,<5`
- 개발 테스트: `pytest>=8,<9`

CLI:

```bash
naver-craw "아이폰17"
naver-craw "아이폰17" --type blog
naver-craw "아이폰17" --type news
naver-craw "아이폰17" --type cafe
```

## 3. 현재 검색 클라이언트

`SearchType`:

```text
nexearch / blog / news / cafe
```

`NaverCrawler`는 다음을 지원합니다.

- timeout
- GET retry: 429/5xx 중심의 exponential backoff
- `Retry-After` 존중
- 요청 간 최소 간격(`min_interval`)
- 검색 영역 선택
- 입력값 검증

예:

```python
crawler.search("아이폰17", search_type="blog", start=1)
```

## 4. 현재 파서

파서는 다음 영역/selector를 우선 확인한 뒤 fallback으로 `a[href]`를 검사합니다.

```text
li.bx
div.total_wrap
div.api_subject_bx
div.api_txt_lines
```

콘텐츠 URL은 NAVER blog/news/cafe 계열을 중심으로 허용하고, 외부 도메인은 제외하며 URL 중복을 제거합니다.

현재는 실제 NAVER의 모든 서비스별 DOM을 완전히 모델링한 상태가 아닙니다. 실제 응답 HTML을 확보할 수 있는 실행 환경에서 selector와 필드 추출을 다시 검증해야 합니다.

## 5. 실제 검증 상태 — 2026-08-19

### 로컬 단위 테스트

실제 실행 결과:

```text
.......                                                                  [100%]
7 passed in 0.17s
```

검증한 항목:

- fixture HTML에서 blog/news/cafe URL 추출
- 중복 URL 제거
- 외부 URL 제외
- `SearchResult` 직렬화
- 검색 영역별 URL 생성
- 빈 검색어 검증
- 잘못된 검색 영역 검증

### 실제 NAVER HTTP 호출 — 검증 완료

2026-08-19 Windows / Python 3.13.4 로컬 환경(외부 네트워크 허용)에서 최초로 실행에 성공했습니다.
이전 기록에 있던 샌드박스 DNS 제한(`NameResolutionError: Failed to resolve 'search.naver.com'`)은
해당 환경 한정 문제였으며 코드 결함이 아니었습니다.

```text
$ NAVER_LIVE_TEST=1 pytest -q tests/test_live.py -rs
1 passed in 1.46s

HTTP: 200 | content length: 733,337 bytes
Content-Type: text/html; charset=UTF-8
```

인코딩도 정상입니다. `apparent_encoding`과 `utf-8` 강제 파싱 결과가 동일합니다.

### 파서 정확도 — 검증 실패

실서비스 응답 기준으로 파서 출력은 아직 사용 가능한 품질이 아닙니다.
`where=blog`, `query=아이폰17` 결과 26건의 호스트 분포:

```text
m.naver.com       19   ← 검색 결과가 아닌 쇼츠/동영상 링크 (잡음 73%)
blog.naver.com     5
cafe.naver.com     2
```

확인된 결함:

1. `parser.py`의 `_is_naver_content_url()`이 `"m."` prefix 때문에 `m.naver.com`을 통과시킵니다.
   `or`/`and` 우선순위 문제로 `_ALLOWED_HOSTS` 화이트리스트가 사실상 무력화되어 있습니다.
2. 제목에 링크 내부 접근성 텍스트 `"새 창 열림"`이 섞여 들어옵니다.
   `where=news`는 10건 중 9건의 제목이 `"네이버뉴스 새 창 열림"`으로 기사 제목이 아닙니다.
3. `where=blog`와 `where=nexearch`의 결과가 완전히 동일합니다. `--type` 옵션이 실제 영역 분리를 못 합니다.
4. `tests/test_live.py`의 단언이 약해서(`assert results` 수준) 위 잡음 데이터에도 통과합니다.

상세 근거는 `docs/AI_WORKLOG.md`의 2026-08-19 로컬 실검증 항목을 참조하십시오.

### 검색 결과 구조에 대한 외부 확인

NAVER 공식 고객센터는 통합검색에서 블로그·카페·뉴스 등의 영역별 검색이 가능하다고 안내하고 있으며, 블로그 검색은 최신순/관련도순 등의 옵션을 제공한다고 설명합니다. citeturn823567search1turn823567search4

또한 NAVER는 검색 노출 결과가 지속적으로 업데이트되고, 기계적 대량 생성이나 검색 품질을 저하시키는 스팸성 행위 등이 제한 대상이 될 수 있다고 안내합니다. citeturn823567search10

## 6. CI

`.github/workflows/test.yml`을 추가했습니다.

- push / pull request: unit tests 자동 실행
- manual `workflow_dispatch`: unit tests + 실서비스 NAVER smoke test 실행

실서비스 smoke test는 다음처럼 수동 실행 환경에서만 동작합니다.

```text
NAVER_LIVE_TEST=1
```

## 7. 작업 이력

### 2026-08-19 — 초기 구현

기존 저장소가 Luna Chat Coder template 중심이라는 것을 확인하고 NAVER 크롤러 프로젝트로 전환했습니다.

주요 구현:

- Python package
- `SearchResult`
- HTTP crawler
- HTML parser
- CLI
- pyproject/requirements
- 기본 tests
- README 전환
- AI 공유 컨텍스트 문서

### 2026-08-19 — 실제 검증 및 고도화

추가 구현:

- `SearchType`: all/blog/news/cafe
- retry/backoff
- `Retry-After` 처리
- 요청 간 최소 간격
- parser selector 후보군 강화
- NAVER 콘텐츠 URL 필터링 강화
- URL deduplication
- HTML fixture 추가
- crawler unit test 추가
- opt-in live test 추가
- GitHub Actions test workflow 추가

로컬 검증:

```text
7 passed in 0.17s
```

실서비스 검증:

```text
미완료 — 현재 sandbox의 외부 DNS/network 제약
```

## 8. 다음 우선순위

### P0 — 실서비스 smoke test (완료)

2026-08-19 실행 성공. HTTP 200 수신 및 단위 테스트 7건 PASS 확인.

```bash
pip install -e '.[dev]'
NAVER_LIVE_TEST=1 pytest -q tests/test_live.py -rs
```

### P0 — parser 정확도 수정 (신규, 최우선)

실서비스 검증에서 드러난 결함을 먼저 해결해야 합니다.

1. `_is_naver_content_url()`을 명시적 host set 단일 조건으로 수정하고 `m.naver.com`을 제외
2. 제목을 anchor 전체 텍스트가 아닌 제목 요소 기준으로 추출하고 접근성 텍스트 제거
3. 실제 응답 HTML을 fixture로 보존하고 위 결함에 대한 회귀 테스트 추가
   (현재 `tests/fixtures/naver_search.html`은 인위적으로 작성된 HTML이라 실제 결함을 잡지 못했습니다)
4. `tests/test_live.py` 단언 강화 — 허용 호스트 검증, 접근성 텍스트 미포함 검증
5. `where=blog` 전용 결과를 받기 위한 실제 요청 파라미터 재확인

### P1 — 서비스별 parser

다음 구조를 권장합니다.

```text
parsers/
├── base.py
├── blog.py
├── news.py
└── cafe.py
```

### P1 — pagination

`limit`, 최대 page 수, 중복 제거, 마지막 페이지 감지를 추가합니다.

### P1 — 저장소

JSON → CSV → SQLite 순으로 추가합니다.

### P2 — 안정성

structured logging, 에러 분류, parser telemetry, 더 세밀한 retry 정책을 추가합니다.

### P2 — SEO 분석

제목 길이, 키워드 빈도, 발행일 분포, 중복 제목, 경쟁 문서 비교 등을 추가합니다.

### P3 — n8n/LLM 연동

안정된 JSON schema를 기준으로 n8n HTTP/Webhook 연동을 추가합니다.

## 9. AI 작업 규칙

1. 항상 최신 `main` commit을 먼저 확인합니다.
2. 실제 파일을 읽고 기존 구현을 재사용합니다.
3. 실행/테스트하지 않은 것은 검증 완료로 기록하지 않습니다.
4. NAVER selector는 추측보다 실제 응답을 우선합니다.
5. 기능 변경 시 테스트를 함께 추가합니다.
6. 새 의존성은 `pyproject.toml`과 `requirements.txt`에 반영합니다.
7. 의미 있는 변경은 `docs/AI_WORKLOG.md`에 기록합니다.
8. 외부 네트워크가 막혀 있으면 그 사실을 명확히 기록하고 fixture 기반 재현성을 확보합니다.

## 10. 완료 기준

```text
코드 작성
  ↓
단위 테스트 통과
  ↓
실제 HTTP/외부 입력 테스트
  ↓
응답 데이터 검증
  ↓
예외 케이스 테스트
  ↓
문서/작업 이력 갱신
```

외부 접근이 불가능하면 실제 통합 테스트는 `미완료`로 유지합니다.
