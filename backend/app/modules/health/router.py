"""Health module API router."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.health import schemas, services
from app.modules.health.schemas import ApiResponse

router = APIRouter(prefix="/api/health", tags=["health"])


@router.post("/logs", response_model=ApiResponse)
def create_log(
    payload: schemas.HealthLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = services.create_health_log(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data=schemas.HealthLogResponse.model_validate(log).model_dump(),
    )


@router.get("/logs", response_model=ApiResponse)
def list_logs(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = services.list_health_logs(db, int(current_user.id), days)
    return ApiResponse(
        success=True,
        data=[schemas.HealthLogResponse.model_validate(l).model_dump() for l in logs],
    )


@router.post("/exercises", response_model=ApiResponse)
def create_exercise(
    payload: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = services.create_exercise(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data=schemas.ExerciseResponse.model_validate(rec).model_dump(),
    )


@router.get("/exercises", response_model=ApiResponse)
def list_exercises(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recs = services.list_exercises(db, int(current_user.id), days)
    return ApiResponse(
        success=True,
        data=[schemas.ExerciseResponse.model_validate(r).model_dump() for r in recs],
    )


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = services.get_stats(db, int(current_user.id), days)
    return ApiResponse(success=True, data=stats)


@router.get("/score", response_model=ApiResponse)
def get_health_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score_data = services.calculate_health_score(db, int(current_user.id))
    return ApiResponse(success=True, data=score_data)