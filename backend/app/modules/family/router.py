"""Family module API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.family import schemas, services
from app.modules.family.schemas import ApiResponse

router = APIRouter(prefix="/api/family", tags=["family"])


@router.post("/members", response_model=ApiResponse)
def create_member(
    payload: schemas.MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = services.create_member(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.MemberResponse.model_validate(m).model_dump())


@router.get("/members", response_model=ApiResponse)
def list_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    members = services.list_members(db, int(current_user.id))
    return ApiResponse(
        success=True,
        data=[schemas.MemberResponse.model_validate(m).model_dump() for m in members],
    )


@router.post("/interactions", response_model=ApiResponse)
def create_interaction(
    payload: schemas.InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    i = services.create_interaction(db, int(current_user.id), payload)
    if not i:
        raise HTTPException(status_code=404, detail="成员不存在")
    return ApiResponse(success=True, data=schemas.InteractionResponse.model_validate(i).model_dump())


@router.get("/interactions", response_model=ApiResponse)
def list_interactions(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_interactions(db, int(current_user.id), days)
    return ApiResponse(
        success=True,
        data=[schemas.InteractionResponse.model_validate(i).model_dump() for i in items],
    )


@router.get("/upcoming", response_model=ApiResponse)
def upcoming_birthdays(
    within_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.get_upcoming_birthdays(db, int(current_user.id), within_days)
    return ApiResponse(success=True, data=items)


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = services.get_stats(db, int(current_user.id))
    return ApiResponse(success=True, data=stats)