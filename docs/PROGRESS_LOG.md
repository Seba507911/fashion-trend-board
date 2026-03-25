# FTIB Expert Analysis — Progress Log

> 전문가 리포트 분석 작업의 진행 상황을 추적하는 로그.

---

## 2026-03-23: 전략 수립

### 논의 내용 (Opus 프로젝트 채팅)
- 전문가 리포트 분석의 목표를 재정의
  - ❌ 키워드 빈도 추출 → ✅ 디자이너 의도 + 업계 맥락 + 교차 근거 해석
- 3-레이어 분석 프레임워크 설계
  - L1: 디자이너별 컬렉션 의도
  - L2: 전문가 리포트로 맥락 부여
  - L3: 디자이너 간 교차 비교
- 도구별 역할 분담 결정
  - Claude API 배치(Sonnet): 구조화된 해석 요약 생성
  - NotebookLM: 교차 탐색 및 패턴 발견
  - Opus 채팅: 전략 해석 및 md 정리
  - Claude Code: 파이프라인 코드 작성
- 리포트 타입별 프롬프트 3종 설계 (A: Catwalk, B: Big Ideas, C: Core Item)

### 산출물
- [x] `docs/EXPERT_ANALYSIS_PLAN.md` 작성
- [x] `docs/PROGRESS_LOG.md` 작성

### 다음 단계
- [ ] Claude Code에서 `scripts/expert_report_pipeline.py` 작성
- [ ] 업로드된 4개 리포트로 파일럿 테스트
- [ ] 파일럿 결과 검증 후 프롬프트 튜닝

---

## Backlog

### Phase 1: 파이프라인 구축
- [ ] expert_report_pipeline.py
- [ ] DB 스키마 확장 (designer_season_insights, cross_pattern_log)
- [ ] 파일럿 테스트 (4개 리포트)
- [ ] 프롬프트 튜닝

### Phase 2: 배치 처리
- [ ] WGSN 리포트 폴더 구조 정리
- [ ] 배치 실행
- [ ] 품질 검증

### Phase 3: 교차 분석
- [ ] NotebookLM 프로젝트 구성
- [ ] 교차 패턴 탐색
- [ ] designer_profiles/ 작성

### Phase 4: FTIB 통합
- [ ] Trend Flow에 전문가 시그널 반영
- [ ] keyword_signals 데이터 입력
- [ ] UI 업데이트
