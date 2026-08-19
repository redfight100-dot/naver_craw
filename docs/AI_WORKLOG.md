# AI Work Log

여러 AI 에이전트가 작업을 이어갈 수 있도록 의미 있는 개발 작업을 시간순으로 기록합니다.

## 2026-08-19 — 프로젝트 초기화 및 1차 크롤러 구현

### 요청
NAVER 크롤러 저장소 개발 시작.

### 확인
기존 `main`은 Luna Chat Coder template이었고 실제 NAVER 크롤러 소스는 존재하지 않았음.

### 구현
- Python package 구조 생성
- `SearchResult` 데이터 모델 생성
- `NaverCrawler` HTTP client 생성
- BeautifulSoup parser 생성
- CLI 생성
- `pyproject.toml` / `requirements.txt` 추가
- parser/model unit test 추가
- README 영문/한글을 프로젝트 문서로 교체
- `docs/AI_CONTEXT.md` 추가

### 초기 검증 상태
- GitHub 소스 반영: 완료
- 실제 로컬 `pytest`: 당시 미실행
- 실제 NAVER HTTP 호출: 미실행
- 현재 응답 DOM 기반 parser 검증: 미완료

---

## 2026-08-19 — 실제 테스트 및 1차 고도화

### 요청
실제 동작 여부를 확인하고 크롤러를 고도화.

### 확인
- ChatGPT sandbox에서 직접 `https://search.naver.com/search.naver?...` 요청을 실행했으나 외부 DNS/network 제한으로 실패.
- 실패 유형: `NameResolutionError: Failed to resolve 'search.naver.com'`
- 따라서 실서비스 NAVER 호출 성공으로 판정하지 않음.

### 변경
- `SearchType` 추가: `nexearch`, `blog`, `news`, `cafe`
- retry/backoff 추가
- HTTP 429/5xx 재시도 및 `Retry-After` 존중
- request pacing(`min_interval`) 추가
- parser selector 후보 강화
- NAVER 콘텐츠 도메인 필터 강화
- 중복 URL 제거
- 검색 영역 선택 CLI 옵션 추가
- 대표 HTML fixture 추가
- crawler unit test 추가
- opt-in live smoke test 추가
- GitHub Actions 테스트 workflow 추가
- `docs/AI_CONTEXT.md`에 검증 결과와 현재 제한사항 반영

### 로컬 테스트
실제 코드 구조와 동일한 테스트 트리를 sandbox에서 구성해 실행:

```text
.......                                                                  [100%]
7 passed in 0.17s
```

### 결과
현재 상태는:

```text
구현: 완료
로컬 단위 테스트: PASS (7/7)
실서비스 NAVER 통합 테스트: 미완료
```

### 다음 작업
1. 외부 네트워크가 허용된 환경에서 `NAVER_LIVE_TEST=1 pytest -q tests/test_live.py -rs` 실행
2. 실제 NAVER 응답 HTML 확보
3. blog/news/cafe 결과 영역별 parser 정확도 검증
4. pagination/limit 구현
5. JSON/CSV/SQLite 저장소 구현
6. SEO 분석 계층 구현
7. n8n/LLM 연동

---

## 2026-08-19 — 로컬 실행 환경 실검증 (Windows / Python 3.13.4)

### 요청
GitHub `main`을 pull 하고, 실제로 테스트를 실행하고, 결과를 기록해서 GitHub에 업로드.

### 확인
- `git pull --ff-only origin main` → `78af92f..78cb157` fast-forward
- 이전 세션이 남긴 "실서비스 NAVER HTTP 호출 미검증" 상태를 그대로 인계받음
- 실행 환경: Windows 11, Python 3.13.4, 외부 네트워크 접근 가능 (이전 샌드박스의 DNS 제한 없음)

### 변경
소스 변경 없음. 검증 실행과 결과 기록만 수행.

### 테스트

설치:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
# Successfully installed ... naver-craw-0.1.0 pytest-8.4.2 requests-2.34.2 beautifulsoup4-4.15.0
```

단위 테스트 — **PASS**:

```text
....s...                                                                 [100%]
SKIPPED [1] tests\test_live.py:8: set NAVER_LIVE_TEST=1 to run against the live NAVER service
7 passed, 1 skipped in 0.30s
```

실서비스 NAVER smoke test — **PASS (최초 실행 성공)**:

```text
$ NAVER_LIVE_TEST=1 pytest -q tests/test_live.py -rs
.                                                                        [100%]
1 passed in 1.46s
```

실제 HTTP 응답 확인:

```text
HTTP: 200 | content length: 733,337 bytes
Content-Type: text/html; charset=UTF-8
r.encoding: UTF-8 / r.apparent_encoding: utf-8
```

### 결과

**실서비스 HTTP 연결은 검증 완료. 그러나 파서 출력 품질은 불합격입니다.**

`where=blog`, `query=아이폰17` 실제 응답 파싱 결과 26건 중 호스트 분포:

```text
m.naver.com       19   ← 검색 결과가 아닌 쇼츠/동영상 링크 (잡음)
blog.naver.com     5
cafe.naver.com     2
```

확인된 결함 3건:

1. **`_is_naver_content_url()` 호스트 필터 오작동 (HIGH)**
   `parser.py:25-28`의 `"m."` prefix 조건이 `m.blog.naver.com`뿐 아니라 `m.naver.com` 자체를 통과시킵니다.
   그 결과 전체 결과의 **73%(19/26)**가 검색 결과가 아닌 `m.naver.com/shorts?...` 동영상 링크입니다.
   또한 `or` / `and` 우선순위상 `host in _ALLOWED_HOSTS or (endswith and any(startswith))`로 평가되어
   의도한 화이트리스트가 사실상 무력화되어 있습니다.

2. **title에 접근성 텍스트가 섞임 (HIGH)**
   컨테이너 안의 모든 `a[href]`를 수집하기 때문에 링크 내부 숨김 텍스트 `"새 창 열림"`이 제목에 붙습니다.

   ```text
   "아이폰17 프로 자급제 가격 스펙 카메라 장점 새 창 열림"
   "새 창 열림"                       ← 제목이 통째로 접근성 텍스트인 경우
   ```

   `where=news`는 더 심각해서 10건 중 9건의 제목이 기사 제목이 아닌 `"네이버뉴스 새 창 열림"`입니다.

3. **`--type` 옵션이 실제로 영역을 분리하지 못함 (MEDIUM)**
   `where=blog`와 `where=nexearch`의 파싱 결과가 26건/잡음 19건으로 **완전히 동일**합니다.
   현재 파라미터 조합으로는 블로그 탭 전용 결과를 받아오지 못하고 있습니다.

4. **라이브 테스트의 단언이 너무 약함 (HIGH)**
   `tests/test_live.py`는 `assert results`와 `url.startswith("http")`만 확인하므로
   위 잡음 데이터에도 **그대로 통과**합니다. 녹색 신호가 품질을 보증하지 못하는 상태입니다.

인코딩은 문제 없음을 확인했습니다. `apparent_encoding`과 `utf-8` 강제 시 파싱 결과가 동일하며,
CLI 콘솔 출력에서 보이는 깨짐은 Windows 콘솔 코드페이지 문제이지 코드 결함이 아닙니다.

검증 상태 요약:

```text
설치(pip install -e '.[dev]')        : PASS
단위 테스트 (7건)                     : PASS
실서비스 NAVER HTTP 200 수신          : PASS  ← 최초 검증 완료
응답 인코딩 (UTF-8)                   : PASS
파서 추출 정확도                      : FAIL (잡음 73%, 제목 오염)
검색 영역(--type) 분리                : FAIL (blog == nexearch)
```

### 다음 작업
1. `_is_naver_content_url()` 화이트리스트를 명시적 host set 단일 조건으로 수정하고 `m.naver.com` 제외
2. 제목 추출을 anchor 전체 텍스트가 아닌 제목 요소 기준으로 변경, `"새 창 열림"` 등 접근성 텍스트 제거
3. 실제 응답 HTML을 fixture로 보존하고 위 결함에 대한 회귀 테스트 추가 (현재 fixture는 인위적 HTML)
4. `where=blog` 전용 결과를 받기 위한 실제 요청 파라미터 재확인
5. `tests/test_live.py` 단언 강화 — 허용 호스트 검증, 접근성 텍스트 미포함 검증
6. 이후 pagination / 저장소 / SEO 분석 진행

---

## 작업 기록 규칙

새 AI는 기존 기록을 지우지 말고 아래 형식으로 새 항목을 추가합니다.

```markdown
## YYYY-MM-DD — 작업 제목

### 요청

### 확인

### 변경

### 테스트

### 결과

### 다음 작업
```

테스트가 실행되지 않았으면 반드시 `미실행` 또는 `미완료`로 기록합니다.
