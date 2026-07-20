"""Travel module API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.travel import schemas, services
from app.modules.travel.schemas import ApiResponse

router = APIRouter(prefix="/api/travel", tags=["travel"])


@router.post("/trips", response_model=ApiResponse)
def create_trip(
    payload: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = services.create_trip(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.TripResponse.model_validate(t).model_dump())


@router.get("/trips", response_model=ApiResponse)
def list_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_trips(db, int(current_user.id))
    return ApiResponse(
        success=True,
        data=[schemas.TripResponse.model_validate(t).model_dump() for t in items],
    )


@router.post("/bucket-list", response_model=ApiResponse)
def add_bucket(
    payload: schemas.BucketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = services.create_bucket(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.BucketResponse.model_validate(b).model_dump())


@router.get("/bucket-list", response_model=ApiResponse)
def list_bucket(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.list_bucket(db, int(current_user.id)))


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.get_stats(db, int(current_user.id)))