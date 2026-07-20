"""Psychology module API router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.psychology import schemas, services
from app.modules.psychology.schemas import ApiResponse

router = APIRouter(prefix="/api/psychology", tags=["psychology"])


@router.post("/moods", response_model=ApiResponse)
def create_mood(
    payload: schemas.MoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = services.create_mood(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.MoodResponse.model_validate(m).model_dump())


@router.get("/moods", response_model=ApiResponse)
def list_moods(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    moods = services.list_moods(db, int(current_user.id), days)
    return ApiResponse(
        success=True,
        data=[schemas.MoodResponse.model_validate(m).model_dump() for m in moods],
    )


@router.post("/reflections", response_model=ApiResponse)
def create_reflection(
    payload: schemas.ReflectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = services.create_reflection(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.ReflectionResponse.model_validate(r).model_dump())


@router.get("/reflections", response_model=ApiResponse)
def list_reflections(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_reflections(db, int(current_user.id), limit)
    return ApiResponse(
        success=True,
        data=[schemas.ReflectionResponse.model_validate(r).model_dump() for r in items],
    )


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = services.get_stats(db, int(current_user.id), days)
    return ApiResponse(success=True, data=stats)