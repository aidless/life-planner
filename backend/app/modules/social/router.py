"""Social module API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.social import schemas, services
from app.modules.social.schemas import ApiResponse

router = APIRouter(prefix="/api/social", tags=["social"])


@router.post("/contacts", response_model=ApiResponse)
def create_contact(
    payload: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = services.create_contact(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.ContactResponse.model_validate(c).model_dump())


@router.get("/contacts", response_model=ApiResponse)
def list_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.list_contacts(db, int(current_user.id)))


@router.post("/interactions", response_model=ApiResponse)
def create_interaction(
    payload: schemas.InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    i = services.create_interaction(db, int(current_user.id), payload)
    if not i:
        raise HTTPException(status_code=404, detail="联系人不存在")
    return ApiResponse(success=True, data=schemas.InteractionResponse.model_validate(i).model_dump())


@router.get("/interactions", response_model=ApiResponse)
def list_interactions(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_interactions(db, int(current_user.id), days)
    return ApiResponse(
        success=True,
        data=[schemas.InteractionResponse.model_validate(i).model_dump() for i in items],
    )


@router.get("/reconnect", response_model=ApiResponse)
def reconnect_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.get_reconnect_suggestions(db, int(current_user.id))
    return ApiResponse(success=True, data=items)


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.get_stats(db, int(current_user.id)))