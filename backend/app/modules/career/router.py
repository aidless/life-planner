"""Career module API router (added 2026-07-19 fix B-α)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.career import schemas, services


router = APIRouter(prefix="/api/career", tags=["career"])


@router.post("/applications", response_model=schemas.ApiResponse)
def create_application(
    payload: schemas.JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job application entry."""
    a = services.create_application(db, int(current_user.id), payload)
    return schemas.ApiResponse(
        success=True,
        data=schemas.JobApplicationResponse.model_validate(a).model_dump(),
    )


@router.get("/applications", response_model=schemas.ApiResponse)
def list_applications(
    status: str | None = Query(
        default=None,
        pattern="^(applied|screening|interview_oa|interview_1|interview_2|offer|rejected|withdrawn)$",
    ),
    industry: str | None = Query(default=None, max_length=80),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's job applications with optional filters."""
    items = services.list_applications(
        db, int(current_user.id), status=status, industry=industry
    )
    return schemas.ApiResponse(
        success=True,
        data=[schemas.JobApplicationResponse.model_validate(a).model_dump() for a in items],
    )


@router.get("/applications/{app_id}", response_model=schemas.ApiResponse)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single application by id."""
    a = services.get_application(db, int(current_user.id), app_id)
    if not a:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    return schemas.ApiResponse(
        success=True,
        data=schemas.JobApplicationResponse.model_validate(a).model_dump(),
    )


@router.patch("/applications/{app_id}", response_model=schemas.ApiResponse)
def update_application(
    app_id: int,
    payload: schemas.JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update application status / dates / notes."""
    a = services.update_application(db, int(current_user.id), app_id, payload)
    if not a:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    return schemas.ApiResponse(
        success=True,
        data=schemas.JobApplicationResponse.model_validate(a).model_dump(),
    )


@router.delete("/applications/{app_id}", response_model=schemas.ApiResponse)
def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete application. Prefer status=withdrawn for archival."""
    ok = services.delete_application(db, int(current_user.id), app_id)
    if not ok:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    return schemas.ApiResponse(success=True, data={"deleted": app_id})


@router.get("/stats", response_model=schemas.ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate career stats for dashboard."""
    stats = services.get_career_stats(db, int(current_user.id))
    return schemas.ApiResponse(success=True, data=stats)
