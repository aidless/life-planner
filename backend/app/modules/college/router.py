"""College module API router.

W3/W5 reports claimed this router was complete; it was not — it only
existed in the legacy ``backend/routers/college.py`` which was removed
in W25. This file is the first honest re-implementation under the
new ``app/modules/`` layout.

Endpoints (7):
  POST /predict           — 5+5+5 colleges (dash/steady/safe)
  GET  /rank              — score → cumulative rank
  GET  /scores            — filtered list of historical score lines
  GET  /colleges          — paginated college list
  GET  /colleges/{id}     — single college detail
  POST /export-pdf        — 2-page A4 PDF report
  GET  /recommendations   — user's saved history
"""

import io
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.models import User
from app.modules.auth.schemas import ApiResponse
from app.modules.college import services
from app.modules.college.schemas import PredictRequest
from app.shared.ai_client import ai_client  # noqa: F401  (kept for future AI recommendations)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/college", tags=["college"])


@router.post("/predict", response_model=ApiResponse)
def predict(payload: PredictRequest, db: Session = Depends(get_db), current_user: User = Depends(__import__("app.dependencies", fromlist=["get_current_user"]).get_current_user)):
    """Predict 5+5+5 colleges based on user score + province."""
    result = services.predict_colleges(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=result)


@router.get("/rank", response_model=ApiResponse)
def get_rank(
    year: int = Query(2025, description="Score year"),
    province: str = Query("山东", description="Province name"),
    score: float = Query(..., description="User score"),
    db: Session = Depends(get_db),
):
    """Reverse-lookup the cumulative rank for a given score."""
    result = services.query_rank(db, year, province, score)
    return ApiResponse(success=True, data=result)


@router.get("/scores", response_model=ApiResponse)
def list_scores(
    year: Optional[int] = None,
    province: Optional[str] = None,
    college: Optional[str] = None,
    major: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Filtered score lookup with pagination."""
    result = services.query_scores_with_filter(
        db, year=year, province=province,
        college_name=college, major_name=major,
        page=page, page_size=page_size,
    )
    return ApiResponse(success=True, data=result)


@router.get("/colleges", response_model=ApiResponse)
def list_colleges(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    province: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Paginated college list with optional filters."""
    result = services.list_colleges(db, page=page, page_size=page_size,
                                    province=province, type=type)
    return ApiResponse(success=True, data=result)


@router.get("/colleges/{college_id}", response_model=ApiResponse)
def get_college(college_id: int, db: Session = Depends(get_db)):
    """Single college detail + recent scores."""
    result = services.get_college_detail(db, college_id)
    if result is None:
        raise HTTPException(status_code=404, detail="院校不存在")
    return ApiResponse(success=True, data=result)


@router.post("/export-pdf", response_class=Response)
def export_pdf(payload: PredictRequest, db: Session = Depends(get_db), current_user: User = Depends(__import__("app.dependencies", fromlist=["get_current_user"]).get_current_user)):
    """Generate a 2-page A4 PDF report.

    Pure-ASCII filename (starlette encodes header values as latin-1,
    which fails on Chinese characters).
    """
    # Lazy import: the legacy PDF service may not exist after W25 cleanup
    try:
        from services.pdf_service import generate_recommendation_pdf
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"PDF service not available: {e}. Run 'W26 PDF service migration'.",
        )

    result = services.predict_colleges(db, int(current_user.id), payload)
    rank_lookup = services.query_rank(
        db, int(payload.year or 2025), payload.province, float(payload.score)
    )

    pdf_bytes = generate_recommendation_pdf(
        user_score=float(payload.score),
        user_rank=int(result.get("user_rank") or 0),
        province=payload.province,
        subject_combination=payload.subject_combination,
        year=int(payload.year or 2025),
        matched_score=rank_lookup.get("matched_score") or 0,
        dash=result.get("dash") or [],
        steady=result.get("steady") or [],
        safe=result.get("safe") or [],
    )

    ascii_filename = f"recommend_{payload.year or 2025}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{ascii_filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.get("/recommendations", response_model=ApiResponse)
def list_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(__import__("app.dependencies", fromlist=["get_current_user"]).get_current_user),
):
    """User's saved college recommendations (history)."""
    rows = services.get_recommendations(db, int(current_user.id))
    return ApiResponse(success=True, data={"items": rows})
