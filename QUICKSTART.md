# FTIB Quick Start Guide

Claude Code에서 이 프로젝트를 시작할 때 참고하는 빠른 시작 가이드.

## 1. 프로젝트 초기화

```bash
# 프로젝트 디렉토리 생성
mkdir -p fashion-trend-board/{backend/{db,crawlers/brand_crawlers,signals,api/routes,importers},frontend/src/{components,hooks,utils,styles},data/{imports,exports},scripts}

# Python 가상환경
cd fashion-trend-board
python -m venv venv
source venv/bin/activate

# 백엔드 의존성
pip install fastapi uvicorn aiosqlite playwright pydantic pyyaml httpx beautifulsoup4

# Playwright 브라우저 설치
playwright install chromium

# 프론트엔드 초기화
cd frontend
npm create vite@latest . -- --template react
npm install @tanstack/react-query recharts axios tailwindcss
npx tailwindcss init
```

## 2. DB 초기화

```bash
python scripts/init_db.py
```

이 스크립트가 하는 일:
1. `backend/db/ftib.db` 생성
2. `references/schema-detail.md`의 DDL 실행
3. 시드 데이터 투입 (brands, seasons, categories)

## 3. 첫 크롤러 테스트

```bash
# dry-run으로 5개만 테스트
python scripts/run_crawl.py --brand [brand_id] --dry-run --limit 5
```

## 4. 개발 서버 실행

```bash
# 백엔드 (터미널 1)
cd backend && uvicorn api.main:app --reload --port 8000

# 프론트엔드 (터미널 2)
cd frontend && npm run dev
```

## 5. MVP 구축 순서

우선순위대로:

1. **DB 스키마 + 시드** → 가장 먼저
2. **1개 브랜드 크롤러** → 데이터 확보
3. **FastAPI 기본 CRUD** → products 조회
4. **ProductBoard UI** → 카드형 뷰 + 브랜드 탭
5. **네이버 검색량 연동** → 시그널 수집
6. **스코어링 엔진** → 점수 산출
7. **비교 뷰 + 피벗 뷰** → 전략 시각화

---

## Claude Code 작업 패턴

### 새 크롤러 추가할 때
```
1. SKILL.md → 크롤러 작성 가이드 참조
2. references/crawler-guide.md 읽기
3. crawler_config.yaml에 설정 추가
4. brand_crawlers/ 에 파일 생성 (또는 기존 official_mall.py 재사용)
5. run_crawl.py --dry-run으로 테스트
```

### 새 API 엔드포인트 추가할 때
```
1. references/api-endpoints.md 참조
2. backend/api/routes/ 에 라우터 추가
3. backend/api/main.py에 라우터 등록
4. Pydantic 모델 정의 (backend/api/models.py)
```

### 프론트엔드 컴포넌트 추가할 때
```
1. SKILL.md → 프론트엔드 컴포넌트 가이드 참조
2. frontend/src/components/ 에 PascalCase 디렉토리 생성
3. TanStack Query로 API 연동
4. Tailwind CSS로 스타일링
```
