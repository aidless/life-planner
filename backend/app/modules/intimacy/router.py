"""Intimacy module API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.intimacy import schemas, services
from app.modules.intimacy.schemas import ApiResponse

router = APIRouter(prefix="/api/intimacy", tags=["intimacy"])


@router.post("/relationships", response_model=ApiResponse)
def create_relationship(
    payload: schemas.RelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = services.create_relationship(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.RelationshipResponse.model_validate(r).model_dump())


@router.get("/relationships", response_model=ApiResponse)
def list_relationships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.list_relationships(db, int(current_user.id)))


@router.post("/anniversaries", response_model=ApiResponse)
def add_anniversary(
    payload: schemas.AnniversaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = services.create_anniversary(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.AnniversaryResponse.model_validate(a).model_dump())


@router.get("/anniversaries", response_model=ApiResponse)
def list_anniversaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.list_anniversaries(db, int(current_user.id)))


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.get_stats(db, int(current_user.id)))