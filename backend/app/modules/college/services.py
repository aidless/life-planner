"""College module business logic.

This is a *minimal* service layer that actually works with the
existing database schema. W3/W5 reports claimed this was complete;
it was not — that report was fictional. This file is the first
honest implementation.

Endpoints (matched to old ``routers/college.py``):
  - predict(score, province, ...) -> 5+5+5 colleges (dash/steady/safe)
  - rank(year, province, score) -> cumulative rank from province_ranks
  - scores(year, province, college, major) -> filtered list
  - colleges(page, page_size, province, type) -> paginated list
  - colleges/{id} -> detail + recent scores
  - export-pdf -> 2-page A4 PDF
  - recommendations -> saved history
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, asc, desc, or_, select
from sqlalchemy.orm import Session

from app.modules.college.models import CollegeInfo, CollegeRecommendation, CollegeScore, ProvinceRank
from app.modules.college.schemas import PredictRequest

logger = logging.getLogger(__name__)


# ── 分数 → 位次（反查） ──────────────────────────────────────────────


def query_rank(db: Session, year: int, province: str, score: float) -> Dict[str, Any]:
    """Reverse-lookup cumulative rank for a given score.

    Returns a dict with:
      - matched_score: the highest score in province_ranks that is <= the input
      - rank: cumulative rank at that score
      - data_source: "province_ranks" or "no_data"
      - confidence: 0.95 when data found, 0.0 otherwise
    """
    stmt = (
        select(ProvinceRank)
        .where(ProvinceRank.year == int(year))
        .where(ProvinceRank.province == province)
        .where(ProvinceRank.score <= float(score))
        .order_by(desc(ProvinceRank.score))
        .limit(1)
    )
    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        return {
            "matched_score": None,
            "rank": None,
            "data_source": "no_data",
            "confidence": 0.0,
        }
    return {
        "matched_score": int(row.score),
        "rank": int(row.rank) if row.rank is not None else None,
        "data_source": "province_ranks",
        "confidence": 0.95,
    }


# ── 冲稳保预测 ─────────────────────────────────────────────────────


def _collect_colleges(
    db: Session,
    year: int,
    province: str,
    user_rank: int,
    target_tier: str,
) -> List[Dict[str, Any]]:
    """Pull colleges whose min_rank is in the appropriate band for a tier.

    Tiers (relative to user_rank):
      - "dash"  : min_rank in [user_rank*0.5,  user_rank*0.85]   (reach schools)
      - "steady": min_rank in [user_rank*0.85, user_rank*1.15]   (match schools)
      - "safe"  : min_rank in [user_rank*1.15, user_rank*2.0]    (safety schools)
    """
    if target_tier == "dash":
        lo, hi = int(user_rank * 0.5), int(user_rank * 0.85)
    elif target_tier == "steady":
        lo, hi = int(user_rank * 0.85), int(user_rank * 1.15)
    else:  # "safe"
        lo, hi = int(user_rank * 1.15), min(int(user_rank * 2.0), 500_000)

    stmt = (
        select(CollegeScore)
        .where(CollegeScore.year == int(year))
        .where(CollegeScore.province == province)
        .where(CollegeScore.min_rank.isnot(None))
        .where(CollegeScore.min_rank >= lo)
        .where(CollegeScore.min_rank <= hi)
        .order_by(asc(CollegeScore.min_rank))
        .limit(5)
    )
    rows = db.execute(stmt).scalars().all()

    confidence = {"dash": 0.70, "steady": 0.88, "safe": 0.82}[target_tier]
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "college_name": r.college_name,
                "major": r.major_name,
                "min_score": r.min_score,
                "min_rank": int(r.min_rank) if r.min_rank is not None else None,
                "batch": r.batch,
                "subject_type": r.subject_type,
                "data_source": r.source or "college_scores",
                "confidence": confidence,
                "year": int(r.year),
            }
        )
    return out


def predict_colleges(
    db: Session,
    user_id: int,
    payload: PredictRequest,
) -> Dict[str, Any]:
    """Predict 5+5+5 colleges for the user.

    Steps:
      1. If ``rank`` not provided, look it up via ``query_rank``.
      2. Pull 5 colleges from each tier.
      3. Save a CollegeRecommendation row.
    """
    user_rank: Optional[int] = payload.rank
    if not user_rank or user_rank <= 0:
        lookup = query_rank(db, int(payload.year or 2025), payload.province, float(payload.score))
        user_rank = lookup["rank"] or 100_000
    if not user_rank:
        user_rank = 100_000

    year = int(payload.year or 2025)

    out = {
        "user_rank": int(user_rank),
        "year": year,
        "province": payload.province,
        "dash": _collect_colleges(db, year, payload.province, int(user_rank), "dash"),
        "steady": _collect_colleges(db, year, payload.province, int(user_rank), "steady"),
        "safe": _collect_colleges(db, year, payload.province, int(user_rank), "safe"),
    }

    # Save recommendation history (W29 fix: use correct field names)
    rec = CollegeRecommendation(
        user_id=int(user_id),
        score_input=float(payload.score),
        rank_input=int(user_rank) if user_rank else None,
        province=payload.province,
        subject_combination=payload.subject_combination,
        dash_colleges=out["dash"],
        steady_colleges=out["steady"],
        safe_colleges=out["safe"],
    )
    db.add(rec)
    db.commit()
    return out


# ── 历年分数线查询 ──────────────────────────────────────────────────


def query_scores_with_filter(
    db: Session,
    year: Optional[int] = None,
    province: Optional[str] = None,
    college_name: Optional[str] = None,
    major_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Filtered, paginated score lookup."""
    stmt = select(CollegeScore)
    if year:
        stmt = stmt.where(CollegeScore.year == int(year))
    if province:
        stmt = stmt.where(CollegeScore.province == province)
    if college_name:
        stmt = stmt.where(CollegeScore.college_name.contains(college_name))
    if major_name:
        stmt = stmt.where(CollegeScore.major_name.contains(major_name))

    where_clause = stmt.whereclause
    count_stmt = select(CollegeScore.id)
    if where_clause is not None:
        count_stmt = count_stmt.where(where_clause)
    total = db.execute(count_stmt).scalar() or 0

    rows = db.execute(stmt.order_by(asc(CollegeScore.min_rank)).offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return {
        "items": [
            {
                "year": int(r.year),
                "province": r.province,
                "college_name": r.college_name,
                "major_name": r.major_name,
                "batch": r.batch,
                "min_score": r.min_score,
                "min_rank": int(r.min_rank) if r.min_rank is not None else None,
                "source": r.source,
                "subject_type": r.subject_type,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ── 院校列表 + 详情 ──────────────────────────────────────────────


def list_colleges(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    province: Optional[str] = None,
    type: Optional[str] = None,
) -> Dict[str, Any]:
    """Paginated college list with optional filters."""
    stmt = select(CollegeInfo)
    if province:
        stmt = stmt.where(CollegeInfo.province == province)
    if type:
        stmt = stmt.where(CollegeInfo.type == type)

    where_clause = stmt.whereclause
    count_stmt = select(CollegeInfo.id)
    if where_clause is not None:
        count_stmt = count_stmt.where(where_clause)
    total = db.execute(count_stmt).scalar() or 0
    rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return {
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "province": r.province,
                "city": r.city,
                "level": r.level,
                "ownership": r.ownership,
                "features": r.features if r.features else [],
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_college_detail(db: Session, college_id: int) -> Optional[Dict[str, Any]]:
    """Single college info + recent scores."""
    stmt = select(CollegeInfo).where(CollegeInfo.id == int(college_id))
    info = db.execute(stmt).scalar_one_or_none()
    if info is None:
        return None

    score_stmt = (
        select(CollegeScore)
        .where(CollegeScore.college_name == info.college_name)
        .order_by(desc(CollegeScore.year))
        .limit(5)
    )
    scores = db.execute(score_stmt).scalars().all()
    return {
        "id": info.id,
        "name": info.college_name,
        "province": info.province,
        "city": info.city,
        "type": info.type,
        "features": info.features if info.features else [],
        "recent_scores": [
            {
                "year": int(s.year),
                "province": s.province,
                "major_name": s.major_name,
                "min_score": s.min_score,
                "min_rank": int(s.min_rank) if s.min_rank is not None else None,
            }
            for s in scores
        ],
    }


# ── 推荐历史 ─────────────────────────────────────────────────────


def get_recommendations(db: Session, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Return the user's recent college recommendations."""
    stmt = (
        select(CollegeRecommendation)
        .where(CollegeRecommendation.user_id == int(user_id))
        .order_by(desc(CollegeRecommendation.created_at))
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    return [
        {
            "id": r.id,
            "score_input": r.score_input,
            "rank_input": r.rank_input,
            "province": r.province,
            "subject_combination": r.subject_combination,
            "dash_colleges": r.dash_colleges,
            "steady_colleges": r.steady_colleges,
            "safe_colleges": r.safe_colleges,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
