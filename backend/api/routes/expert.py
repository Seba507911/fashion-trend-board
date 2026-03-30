"""Expert Report Review API — 시드 데이터 기반 초기 버전.

향후 expert_reports / expert_keywords 테이블로 마이그레이션 예정.
현재는 JSON 시드 데이터를 메모리에 보관하고 리뷰 결과도 메모리 저장.
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import json, copy

router = APIRouter(prefix="/api/expert", tags=["expert"])

# ─── Seed data (WGSN 26SS) ──────────────────────────────────
# 프론트엔드 expertKeywordsData.js와 동일한 데이터.
# 서버 재시작 시 리뷰 결과 초기화됨 (Phase 1).

_KEYWORDS: list[dict] = []
_REVIEWS: dict[str, dict] = {}  # key: "{keyword}_{season}"


def _load_seed():
    """lazy-init: 시드 데이터를 한 번만 로드."""
    global _KEYWORDS
    if _KEYWORDS:
        return
    import importlib.resources as _res
    from pathlib import Path
    seed_path = Path(__file__).parent.parent.parent.parent / "frontend" / "src" / "components" / "expert" / "expertKeywordsData.js"
    if seed_path.exists():
        text = seed_path.read_text(encoding="utf-8")
        # JS 배열을 파이썬으로 파싱 (간이 변환)
        import re
        # export const ... = [ 이후부터 마지막 ]; 까지 추출
        m = re.search(r"=\s*\[", text)
        if m:
            arr_text = text[m.end()-1:]
            # 마지막 ]; 찾기
            end = arr_text.rfind("];")
            if end > 0:
                arr_text = arr_text[:end+1]
            # JS→JSON 변환: trailing commas, single-line comments
            arr_text = re.sub(r"//[^\n]*", "", arr_text)
            arr_text = re.sub(r",\s*([}\]])", r"\1", arr_text)
            # JS null → JSON null (이미 호환), JS property names 따옴표
            # key: value → "key": value
            arr_text = re.sub(r'(\s)(\w+)\s*:', r'\1"\2":', arr_text)
            try:
                _KEYWORDS.extend(json.loads(arr_text))
            except json.JSONDecodeError:
                pass


def _get_filtered(season: str, category: str | None, tier: int | None, pool: str | None) -> list[dict]:
    _load_seed()
    result = []
    for kw in _KEYWORDS:
        if kw.get("season") != season:
            continue
        if category and kw.get("category") != category:
            continue
        if tier is not None and kw.get("tier") != tier:
            continue
        if pool and kw.get("pool") != pool:
            continue
        item = copy.copy(kw)
        # Merge review state
        rkey = f"{kw['keyword']}_{season}"
        if rkey in _REVIEWS:
            item.update(_REVIEWS[rkey])
        result.append(item)
    result.sort(key=lambda x: (-x.get("source_count", 0), x.get("keyword", "")))
    return result


# ─── Routes ──────────────────────────────────────────────────

@router.get("/keywords")
async def get_expert_keywords(
    season: str = Query("26SS"),
    category: Optional[str] = Query(None),
    tier: Optional[int] = Query(None),
    pool: Optional[str] = Query(None),
):
    keywords = _get_filtered(season, category, tier, pool)
    # Tier별 그루핑
    tiers: dict[int, list] = {}
    for kw in keywords:
        t = kw.get("tier", 9)
        tiers.setdefault(t, []).append(kw)
    return {
        "keywords": keywords,
        "total": len(keywords),
        "by_tier": {str(t): len(kws) for t, kws in sorted(tiers.items())},
        "season": season,
    }


@router.get("/keyword/{keyword}/detail")
async def get_expert_keyword_detail(
    keyword: str,
    season: str = Query("26SS"),
):
    _load_seed()
    found = None
    for kw in _KEYWORDS:
        if kw["keyword"] == keyword and kw.get("season") == season:
            found = copy.copy(kw)
            break
    if not found:
        return {"error": "not found"}
    rkey = f"{keyword}_{season}"
    if rkey in _REVIEWS:
        found.update(_REVIEWS[rkey])
    return found


class ReviewBody(BaseModel):
    evaluation: str  # "essential", "reference", "exclude"
    comment: Optional[str] = None
    reviewer: Optional[str] = None
    season: str = "26SS"


@router.post("/keyword/{keyword}/review")
async def post_expert_review(keyword: str, body: ReviewBody):
    _load_seed()
    rkey = f"{keyword}_{body.season}"
    _REVIEWS[rkey] = {
        "review_status": body.evaluation,
        "review_comment": body.comment,
        "reviewer": body.reviewer,
    }
    return {"ok": True, "keyword": keyword, "review_status": body.evaluation}


# ─── Section-level Reviews ───────────────────────────────────

_SECTION_REVIEWS: dict[str, dict] = {}


class SectionReviewBody(BaseModel):
    rating: str  # "fit", "uncertain", "off"
    comment: Optional[str] = None
    reviewer: Optional[str] = None
    season: str = "26SS"


@router.get("/section-reviews")
async def get_section_reviews(season: str = Query("26SS")):
    suffix = f"_{season}"
    reviews = {k: v for k, v in _SECTION_REVIEWS.items() if k.endswith(suffix)}
    return {"reviews": reviews}


@router.post("/section/{section_id}/review")
async def post_section_review(section_id: str, body: SectionReviewBody):
    key = f"{section_id}_{body.season}"
    _SECTION_REVIEWS[key] = {
        "rating": body.rating,
        "comment": body.comment,
        "reviewer": body.reviewer,
    }
    return {"ok": True, "section_id": section_id, "rating": body.rating}
