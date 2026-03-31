# FTIB 공동작업 세팅 — 단계별 실행 가이드

> Seba(DB/크롤링 담당) + 동료(VLM/셀럽/트렌드 담당)
> 원칙: DB는 Seba만 건드림, 동료는 JSON으로 결과 전달

---

## Step 1: GitHub 레포 정리

### 1-1. 동료를 Collaborator로 초대

```
GitHub > ftib 레포 > Settings > Collaborators > Add people
→ 동료 GitHub 계정 입력 → Invite
```

동료가 이메일에서 초대 수락하면 push 권한 생김.

### 1-2. 브랜치 보호 규칙 설정

main에 직접 push 못하게 막아두면 실수 방지돼.

```
GitHub > ftib 레포 > Settings > Branches > Add rule
Branch name pattern: main
체크:
  ☑ Require a pull request before merging
  ☐ Require approvals (2인이니까 체크 안 해도 됨)
```

이러면 main에는 PR을 통해서만 머지 가능.
귀찮으면 이 단계는 건너뛰고 "약속"으로 대체해도 돼.

### 1-3. data/ 폴더 구조 만들기

동료가 올리는 JSON 파일의 위치를 미리 잡아둬.

```
ftib/
├── backend/db/
│   └── ftib.db                  ← Seba만 수정, Git 추적 (실제 DB 위치)
├── data/
│   ├── vlm/                     ← 동료가 VLM 결과 올리는 곳
│   │   └── .gitkeep
│   ├── celeb/                   ← 동료가 셀럽 데이터 올리는 곳
│   │   └── .gitkeep
│   ├── imports/                 ← Seba가 import 완료한 파일 이동
│   │   └── .gitkeep
│   └── exports/                 ← 데이터 내보내기용
│       └── .gitkeep
```

> **참고**: DB는 `backend/db/ftib.db`에 위치. `data/` 폴더는 JSON 교환용으로만 사용.

```bash
# 로컬에서 실행 (이미 생성 완료됨 — 확인용)
mkdir -p data/vlm data/celeb data/imports data/exports
touch data/vlm/.gitkeep data/celeb/.gitkeep data/imports/.gitkeep data/exports/.gitkeep
git add data/
git commit -m "공동작업용 data 폴더 구조 생성"
git push origin main
```

---

## Step 2: 동료 로컬 환경 세팅

동료에게 아래 순서대로 안내해.

### 2-1. 레포 클론

```bash
git clone https://github.com/[계정]/ftib.git
cd ftib
```

### 2-2. 백엔드 세팅

```bash
cd backend
pip install -r requirements.txt
```

### 2-3. .env 파일 생성

.env는 Git에 안 올라가니까 직접 전달해줘야 해.
슬랙 DM이나 카톡으로 내용 보내주고 동료가 직접 만들면 돼.

```bash
# 프로젝트 루트에 .env 파일 생성
# 내용:
ANTHROPIC_API_KEY=sk-ant-...
```

### 2-4. 프론트엔드 세팅

```bash
cd ../frontend
npm install
```

### 2-5. 로컬 실행 확인

```bash
# 터미널 1: 백엔드
cd backend
uvicorn api.main:app --reload

# 터미널 2: 프론트엔드
cd frontend
npm run dev
```

브라우저에서 `http://localhost:5173` 열어서 화면 나오면 성공.

### 2-6. Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code

# 프로젝트 루트에서 실행
cd ftib
claude
```

첫 실행 시 API 키 입력하라고 나옴.
동료 본인 Anthropic 계정 키를 쓰거나, 회사 키를 공유하거나.

---

## Step 3: Vercel 세팅

### 3-1. 동료를 Vercel 팀에 초대

```
Vercel Dashboard > ftib 프로젝트 > Settings > Members
→ Invite Member → 동료 이메일 입력
```

### 3-2. GitHub 연동 확인

```
Vercel Dashboard > ftib 프로젝트 > Settings > Git
확인할 것:
  ☑ Production Branch: main
  ☑ Preview Deployments: Enabled (PR마다 자동 Preview URL 생성)
```

이게 켜져 있으면:
- main에 머지 → 자동으로 프로덕션 배포
- PR 올리면 → 자동으로 Preview URL 생성 (동료가 바로 확인 가능)

---

## Step 4: 일일 작업 흐름

### 아침 (작업 시작)

```bash
# 둘 다 각자 실행
git checkout main
git pull origin main
```

최신 코드 + 최신 DB 상태로 시작.

### 낮 (각자 작업)

```bash
# Seba: 새 브랜치에서 작업
git checkout -b seba/nike-crawler-fix

# 동료: 새 브랜치에서 작업
git checkout -b [동료]/vlm-enhancement
```

각자 Claude Code로 작업.

### 저녁 (커밋 + 머지)

#### 순서가 중요해:

```
1단계: 동료가 먼저 커밋 + 푸시
  git add .
  git commit -m "VLM 고도화 프롬프트 적용 + 결과 500장"
  git push origin [동료]/vlm-enhancement
  → GitHub에서 PR 생성

2단계: Seba가 동료 PR 확인
  → Vercel Preview URL에서 화면 확인 (코드 안 봐도 됨)
  → 괜찮으면 Merge 클릭

3단계: Seba가 main pull
  git checkout main
  git pull origin main

4단계: Seba가 동료의 JSON 데이터를 DB에 import
  python scripts/import_vlm_results.py
  (→ data/vlm/*.json 읽어서 backend/db/ftib.db에 적재)
  (→ 완료된 JSON은 data/imports/로 이동)

5단계: Seba가 자기 작업 + DB 업데이트 커밋
  git checkout -b seba/nike-crawler-fix  (또는 기존 브랜치)
  git add .
  git commit -m "Nike 크롤러 수정 + VLM 데이터 import + 크롤링 데이터 추가"
  git push origin seba/nike-crawler-fix
  → PR 생성 → 본인이 머지 (또는 동료 확인 후 머지)

6단계: 동료가 다음날 아침에 pull하면 최신 DB 포함
```

### 시각화하면:

```
동료 작업물 (JSON) ──PR──→ main ──Seba pull──→ DB import
                                              ↓
Seba 작업물 (코드+DB) ──PR──→ main ──동료 pull──→ 최신 상태
```

---

## Step 5: JSON 파일 규격

동료가 올리는 파일 형식을 미리 정해두면 import 스크립트를 한 번만 만들면 돼.

### VLM 결과 파일

파일명: `data/vlm/vlm_YYYYMMDD_NNN.json`
예: `data/vlm/vlm_20260401_500.json` (4월 1일, 500장)

```json
{
  "metadata": {
    "date": "2026-04-01",
    "model": "claude-sonnet-4-20250514",
    "prompt_version": "v2",
    "count": 500
  },
  "results": [
    {
      "source_type": "runway",
      "source_id": 1234,
      "items": [
        {
          "item_type": "jacket",
          "item_subtype": "trench_coat",
          "color_primary": "beige",
          "color_secondary": null,
          "color_tone": "medium",
          "visual_material": "woven_matte",
          "surface_finish": "matte",
          "opacity": "opaque",
          "weight_appearance": "medium",
          "drape": "structured",
          "fit": "oversized",
          "length": "long",
          "notable_details": ["padded_shoulders", "belt_detail"]
        }
      ],
      "overall_silhouette": "oversized",
      "silhouette_details": {
        "shoulder": "sculpted",
        "waist": "belted",
        "hem_volume": "straight"
      },
      "dominant_colors": ["beige", "white"],
      "color_palette_mood": "neutral",
      "pattern": "solid",
      "style_mood": ["tailored", "luxe"],
      "raw_response": "{ ... 원본 API 응답 전체 ... }"
    }
  ]
}
```

### 셀럽 데이터 파일

파일명: `data/celeb/celeb_YYYYMMDD.json`

```json
{
  "metadata": {
    "date": "2026-04-01",
    "collector": "동료이름",
    "count": 15
  },
  "sightings": [
    {
      "person_name": "제니",
      "tier": "T1",
      "keyword": "sheer",
      "image_url": "https://...",
      "source_url": "https://...",
      "sighting_date": "2026-03-28",
      "notes": "공항 패션, 시어 블라우스 착용"
    }
  ],
  "search_volume": [
    {
      "person_name": "제니",
      "tier": "T1",
      "keyword": "sheer",
      "volume": 45000,
      "volume_change_pct": 120.5,
      "is_spike": true,
      "measured_date": "2026-03-28"
    }
  ]
}
```

---

## Step 6: Import 스크립트 (Seba가 만들어두기)

Claude Code에 이렇게 지시하면 돼:

```
data/vlm/ 폴더의 JSON 파일을 읽어서 backend/db/ftib.db의 vlm_labels
테이블에 적재하는 import 스크립트를 만들어줘.
import 완료된 파일은 data/imports/로 이동시켜줘.
data/celeb/ 폴더도 동일하게 celeb_sightings, celeb_search_volume
테이블에 적재하는 스크립트도 만들어줘.
```

스크립트 위치: `scripts/import_vlm_results.py`, `scripts/import_celeb_data.py`

---

## Step 7: 동료에게 전달할 문서

동료가 읽어야 할 문서 목록 (우선순위 순):

```
1순위 (첫날):
  □ 이 문서 (FTIB_COLLABORATION_GUIDE.md) — 작업 흐름 이해
  □ CLAUDE.md — 프로젝트 전체 구조
  □ 로컬 환경 세팅 + 화면 둘러보기

2순위 (첫 주):
  □ PROJECT_OVERVIEW.md — 현황 + 데이터 상태
  □ WGSN_26SS_KEYWORD_MASTER.md — 전문가 분석 초안
  □ VLM_ENHANCEMENT_REVIEW.md — VLM 고도화 방향

3순위 (필요할 때):
  □ BRAND_CRAWL_LIST.md — 크롤링 대상 브랜드
  □ SKILL.md — FTIB 컨셉 상세
```

---

## Step 8: 첫 주 실행 계획

### Day 1 (세팅)

```
□ Seba: GitHub Collaborator 초대
□ Seba: Vercel Team Member 초대
□ Seba: data/ 폴더 구조 생성 + 푸시
□ Seba: .env 내용 동료에게 전달
□ 동료: 레포 클론 + 환경 세팅 + 로컬 실행 확인
□ 동료: Claude Code 설치
□ 동료: 프로젝트 문서 읽기 (CLAUDE.md, 이 문서)
```

### Day 2 (테스트)

```
□ 동료: 테스트 브랜치 만들어서 아무거나 수정 (README 오타 등)
□ 동료: PR 올리기
□ Seba: Vercel Preview URL에서 확인 → 머지
□ 동료: main pull → 최신 상태 확인
→ 이 흐름이 되면 공동작업 준비 완료
```

### Day 3~5 (실제 작업 시작)

```
□ Seba: import 스크립트 작성 (vlm, celeb)
□ Seba: 마켓 크롤링 계속 (새 브랜드 추가)
□ 동료: VLM 고도화 프롬프트 테스트 (샘플 10장)
□ 동료: 결과를 data/vlm/에 JSON으로 커밋
□ Seba: JSON import → DB 적재 확인
□ 함께: 저녁 머지 흐름 1회 실습
```

---

## 문제 상황 대처

### "git pull 했는데 충돌났어"

```bash
# 대부분 같은 파일을 둘 다 수정한 경우
# 해결: 충돌 파일 열어서 수동 해결
git status  # 충돌 파일 확인
# 파일 열면 <<<<<<< HEAD ... >>>>>>> 표시 있음
# 둘 다 살릴 내용으로 편집
git add [파일]
git commit -m "충돌 해결"
```

### "동료가 실수로 main에 직접 push했어"

```bash
# 큰 문제 아님. 그냥 pull 받으면 됨
git pull origin main
# 앞으로 브랜치 쓰자고 다시 약속
```

### "DB가 이상해졌어"

```bash
# Seba가 마지막으로 커밋한 DB로 복원
git checkout main -- backend/db/ftib.db
# 또는 seed 스크립트로 초기화 후 재수집
```

### "Claude Code가 이상한 코드를 넣었어"

```bash
# 커밋 전이면
git checkout -- [파일]  # 변경 취소

# 커밋 후면
git revert [커밋해시]  # 커밋 되돌리기
```

---

## 핵심 요약

```
1. main 직접 push 금지 → 브랜치 + PR
2. DB는 Seba만 수정 → 동료는 JSON으로 전달
3. 매일 저녁: 동료 PR → Seba 머지+import → Seba PR → 머지
4. 매일 아침: 둘 다 git pull로 시작
5. 같은 파일 동시 수정 피하기 → 5분 싱크로 예방
```
