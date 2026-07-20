"""Interest module API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.interest import schemas, services
from app.modules.interest.schemas import ApiResponse

router = APIRouter(prefix="/api/interest", tags=["interest"])


@router.post("", response_model=ApiResponse)
def create_interest(
    payload: schemas.InterestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    i = services.create_interest(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.InterestResponse.model_validate(i).model_dump())


@router.get("", response_model=ApiResponse)
def list_interests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.list_interests(db, int(current_user.id)))


@router.post("/activities", response_model=ApiResponse)
def create_activity(
    payload: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = services.create_activity(db, int(current_user.id), payload)
    if not a:
        raise HTTPException(status_code=404, detail="兴趣不存在")
    return ApiResponse(success=True, data=schemas.ActivityResponse.model_validate(a).model_dump())


@router.get("/activities", response_model=ApiResponse)
def list_activities(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_activities(db, int(current_user.id), days)
    return ApiResponse(
        success=True,
        data=[schemas.ActivityResponse.model_validate(a).model_dump() for a in items],
    )


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.get_stats(db, int(current_user.id)))