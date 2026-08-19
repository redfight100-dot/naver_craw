# AI Context — NAVER Crawler

> 이 문서는 이 저장소를 작업하는 여러 AI 에이전트가 공유하는 **정본 작업 컨텍스트(Canonical Context)** 입니다.
>
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

현재 1차 구현은 NAVER 웹 검색을 HTTP로 요청하고 HTML에서 NAVER 계열 링크를 정규화하는 최소 기능입니다.

구현 파일:

```text
src/naver_craw/
├── __init__.py    # 패키지 버전
├── crawler.py     # requests 기반 NAVER 검색 HTTP 클라이언트
├── parser.py      # BeautifulSoup 기반 HTML 파서
├── models.py      # SearchResult 데이터 모델
└── cli.py         # JSON 출력 CLI

tests/
├── test_parser.py
└── test_models.py
```

프로젝트 설정:

- `pyproject.toml`
- `requirements.txt`
- Python `>=3.11`
- `requests>=2.32,<3`
- `beautifulsoup4>=4.12,<5`

CLI:

```bash
naver-craw "아이폰17"
```

또는

```bash
python -m naver_craw.cli "아이폰17" --start 1
```

출력 형식은 UTF-8 JSON입니다.

## 3. 현재 데이터 모델

`SearchResult`:

```python
SearchResult(
    title: str,
    url: str,
    description: str = "",
    source: str = "",
    published_at: str = "",
)
```

현재는 제목과 URL 추출이 핵심이며, `description`, `source`, `published_at`은 후속 고도화를 위해 모델에 미리 포함했습니다.

## 4. 현재 파서의 한계

현재 `parser.py`는 범용 `<a>` 태그를 대상으로 다음 NAVER 도메인을 우선 수집합니다.

- `search.naver.com`
- `blog.naver.com`
- `news.naver.com`

현재 파서는 NAVER의 실제 검색 결과 DOM 구조에 강하게 결합되어 있지 않은 대신, 실제 서비스별 필드 추출 정확도는 아직 충분하지 않습니다.

따라서 다음 개발에서는 반드시 **실제 현재 NAVER 응답 HTML을 기준으로 selector를 다시 검증**해야 합니다.

## 5. 실제 테스트 상태

2026-08-19 작업 당시 GitHub 연결을 통한 소스 작성은 완료했습니다.

중요:

- GitHub에 소스 파일/테스트 파일을 반영했습니다.
- 로컬 샌드박스에서 `git clone`을 통한 실제 저장소 materialization/외부 네트워크 기반 실행 검증은 환경 제약으로 완료하지 못했습니다.
- 따라서 "실제 NAVER 검색 호출이 성공했다"고 주장하면 안 됩니다.
- 다음 AI는 반드시 실제 실행 가능한 환경에서 설치 → 테스트 → NAVER 요청 → 응답 HTML 검사까지 수행해야 합니다.

검증 완료와 검증 미완료를 구분해서 기록할 것.

## 6. 작업 이력

### 2026-08-19 — 1차 구현

사용자 요청: `naver_craw` 저장소를 실제 NAVER 크롤러 프로젝트로 개발.

수행한 작업:

1. 기존 저장소를 확인하고, 기존 내용이 Luna Chat Coder 템플릿 중심임을 확인.
2. `src/naver_craw/` 패키지 생성.
3. `SearchResult` 모델 추가.
4. NAVER 검색 HTTP 클라이언트 추가.
5. BeautifulSoup 기반 검색 HTML 파서 추가.
6. CLI 추가.
7. Python 패키지 설정 추가.
8. parser/model 기본 테스트 추가.
9. README 영문/한글을 NAVER Crawler 프로젝트 문서로 교체.

주요 변경 commit:

- 초기 패키지: `d27f73fe1ace6f21113c0d17550685a4dc97940e`
- 모델: `349a950613b7cbb53381af3561a3d21e91754823`
- 파서: `099775dfd8d0dca5100d1cfeb8d9429ae1c9f267`
- 크롤러: `d7155d3cad0713ee866f12dca566014c6693cb9f`
- CLI: `eee35d2bf09c368c3419210f896b446ef1a4d33e`
- dependencies: `64af4395e967c7a0a8852d01be2b3a7f8f43dfb2`
- pyproject: `9deb1c6b1f72c9f4b3930bf839fbbb4cdff8c72f`
- parser test: `bb6f7650c6aa2841fc33537b18b437bc37cf8170`
- model test: `1f77a326b398ff1bea11b303c7e270d1da2a0fdd`
- README.ko: `9caa819805466129c0808dd855e4a45e6ab20c74`
- README: `4fc533b865fbdb3c4282671858303357e3438c98`

## 7. 다음 우선순위

### P0 — 실제 실행 검증

반드시 먼저 수행:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
python -m naver_craw.cli "아이폰17"
```

그 다음 실제 응답 HTML을 저장해서 `parser.py`가 무엇을 추출하는지 확인합니다.

### P1 — 서비스별 파서

다음과 같이 분리하는 것을 권장합니다.

```text
parsers/
├── base.py
├── web.py
├── blog.py
├── news.py
└── cafe.py
```

단순 URL 필터 방식에서 벗어나 검색 결과 영역별로 명시적인 parser를 두어야 합니다.

### P1 — 페이지네이션

`start`를 사용한 연속 검색을 지원하고, 결과 개수와 중복 URL을 관리합니다.

예상 API:

```python
crawler.search(query, start=1, limit=100)
```

### P1 — 저장소

먼저 JSON/CSV를 안정화하고 이후 SQLite를 추가합니다.

권장 계층:

```text
storage/
├── json.py
├── csv.py
└── sqlite.py
```

### P2 — 안정성

- timeout
- retry with backoff
- rate limiting
- structured logging
- request failure classification
- parser failure telemetry

### P2 — SEO 분석

향후 `analysis/`를 분리합니다.

예상 기능:

- 제목 길이
- 핵심 키워드 추출
- 키워드 빈도
- 발행일 분포
- 중복 제목 탐지
- 경쟁 문서 수집/비교

### P3 — n8n/LLM 연동

JSON schema를 안정화하고 n8n Webhook/HTTP Request 노드에서 바로 소비할 수 있게 합니다.

## 8. AI 작업 규칙

여러 AI가 이 저장소를 함께 수정할 수 있으므로 다음 규칙을 지킵니다.

1. 항상 GitHub의 최신 `main` commit을 먼저 확인한다.
2. 이미 구현된 기능을 추측해서 다시 만들지 말고 실제 파일을 읽는다.
3. 실행/테스트하지 않은 내용은 "검증됨"이라고 표현하지 않는다.
4. NAVER DOM selector는 추측하지 말고 실제 응답 HTML을 근거로 수정한다.
5. 한 번에 큰 리팩터링을 하지 말고 기능 단위로 변경한다.
6. 새 의존성을 추가하면 `pyproject.toml`과 `requirements.txt`를 함께 갱신한다.
7. 기능 변경 시 테스트를 같이 추가한다.
8. 기존 Luna Chat Coder skill은 개발 continuity 용도로 보존하되, 프로젝트 자체의 구현 설명은 이 문서를 기준으로 한다.
9. 다음 AI가 이어서 작업할 수 있도록 의미 있는 변경은 `docs/AI_WORKLOG.md`에 기록한다.

## 9. 완료 기준

기능 하나를 "완료"로 표시하려면 가능하면 다음을 확인해야 합니다.

```text
코드 작성
  ↓
단위 테스트
  ↓
실제 HTTP/외부 입력 테스트
  ↓
응답 데이터 검증
  ↓
예외 케이스 테스트
  ↓
문서/작업 이력 갱신
```

외부 네트워크나 NAVER 접근 자체가 불가능하면 그 사실을 명시하고, 테스트 fixture를 추가해 재현 가능한 로컬 테스트를 확보합니다.
