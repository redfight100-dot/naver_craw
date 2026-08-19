# NAVER Crawler

Python 기반 NAVER 검색 크롤러의 첫 번째 구현입니다.

## 현재 기능

- NAVER 웹 검색 요청
- 검색 결과 URL/제목 정규화
- JSON 출력 CLI
- 파서/모델 단위 테스트

## 설치

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

## 사용

```bash
naver-craw "아이폰17"
```

또는

```bash
python -m naver_craw.cli "아이폰17" --start 1
```

결과는 UTF-8 JSON으로 출력됩니다.

## 개발 구조

```text
src/naver_craw/
├── crawler.py   # HTTP 요청
├── parser.py    # HTML → 모델 변환
├── models.py    # 데이터 모델
└── cli.py       # CLI

tests/
├── test_parser.py
└── test_models.py
```

## 다음 개발 단계

1. 블로그/뉴스/카페 영역별 추출
2. 페이지네이션
3. 중복 URL 제거 및 정규화 강화
4. SQLite/CSV/JSON 저장소
5. 재시도·레이트리밋·로깅
6. 키워드/SEO 분석 API
7. n8n 연동용 JSON 출력

> NAVER 서비스 이용약관, robots 정책 및 대상 페이지의 접근 정책을 준수하여 사용하세요.
