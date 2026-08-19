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
