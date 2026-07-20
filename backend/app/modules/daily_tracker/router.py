"""Daily log API router."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import ApiResponse
from app.modules.daily_tracker import schemas, services

router = APIRouter(prefix="/api/daily-logs", tags=["daily-logs"])


@router.post("", response_model=ApiResponse)
def create_log(
    payload: schemas.DailyLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new daily log entry for the current user."""
    log = services.create_log(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data=schemas.DailyLogResponse.model_validate(log).model_dump(),
    )


@router.get("", response_model=ApiResponse)
def list_logs(
    target_date: date | None = None,
    activity_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List daily log entries (optionally filtered by date or activity type)."""
    logs = services.get_logs(db, int(current_user.id), target_date, activity_type)
    return ApiResponse(
        success=True,
        data=[schemas.DailyLogResponse.model_validate(l).model_dump() for l in logs],
    )


@router.get("/{log_id}", response_model=ApiResponse)
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single daily log by id."""
    log = services.get_log(db, int(current_user.id), log_id)
    if not log:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(
        success=True,
        data=schemas.DailyLogResponse.model_validate(log).model_dump(),
    )


@router.delete("/{log_id}", response_model=ApiResponse)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a daily log by id."""
    deleted = services.delete_log(db, int(current_user.id), log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(success=True, data={"message": "记录已删除"})


@router.post("/{log_id}/analyze", response_model=ApiResponse)
async def analyze_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run AI analysis on a daily log (returns a coaching feedback string)."""
    feedback = await services.generate_ai_feedback(db, int(current_user.id), log_id)
    if feedback is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(success=True, data={"feedback": feedback})
