"""Meaning module API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.meaning import schemas, services
from app.modules.meaning.schemas import ApiResponse

router = APIRouter(prefix="/api/meaning", tags=["meaning"])


@router.post("/values", response_model=ApiResponse)
def create_value(
    payload: schemas.ValueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    v = services.create_value(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.ValueResponse.model_validate(v).model_dump())


@router.get("/values", response_model=ApiResponse)
def list_values(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_values(db, int(current_user.id))
    return ApiResponse(
        success=True,
        data=[schemas.ValueResponse.model_validate(v).model_dump() for v in items],
    )


@router.put("/values/{value_id}", response_model=ApiResponse)
def update_value(
    value_id: int,
    payload: schemas.ValueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    v = services.update_value(db, int(current_user.id), value_id, payload)
    if not v:
        raise HTTPException(status_code=404, detail="价值观不存在")
    return ApiResponse(success=True, data=schemas.ValueResponse.model_validate(v).model_dump())


@router.delete("/values/{value_id}", response_model=ApiResponse)
def delete_value(
    value_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = services.delete_value(db, int(current_user.id), value_id)
    if not ok:
        raise HTTPException(status_code=404, detail="价值观不存在")
    return ApiResponse(success=True, data={"deleted": value_id})


@router.put("/purpose", response_model=ApiResponse)
def upsert_purpose(
    payload: schemas.PurposeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = services.upsert_purpose(db, int(current_user.id), payload.statement)
    return ApiResponse(success=True, data=schemas.PurposeResponse.model_validate(p).model_dump())


@router.get("/purpose", response_model=ApiResponse)
def get_purpose(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = services.get_current_purpose(db, int(current_user.id))
    if not p:
        return ApiResponse(success=True, data=None)
    return ApiResponse(success=True, data=schemas.PurposeResponse.model_validate(p).model_dump())


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.get_stats(db, int(current_user.id)))