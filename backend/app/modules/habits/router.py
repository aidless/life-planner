"""Habits module API router."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.habits import schemas, services
from app.modules.habits.schemas import ApiResponse

router = APIRouter(prefix="/api/habits", tags=["habits"])


@router.post("", response_model=ApiResponse)
def create_habit(
    payload: schemas.HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    h = services.create_habit(db, int(current_user.id), payload)
    return ApiResponse(success=True, data={"id": h.id, "name": h.name})


@router.get("", response_model=ApiResponse)
def list_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_habits(db, int(current_user.id))
    return ApiResponse(success=True, data=items)


@router.put("/{habit_id}", response_model=ApiResponse)
def update_habit(
    habit_id: int,
    payload: schemas.HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    h = services.update_habit(db, int(current_user.id), habit_id, payload)
    if not h:
        raise HTTPException(status_code=404, detail="习惯不存在")
    return ApiResponse(success=True, data={"id": h.id, "name": h.name})


@router.post("/{habit_id}/checkin", response_model=ApiResponse)
def checkin(
    habit_id: int,
    payload: schemas.CheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = services.checkin(
        db, int(current_user.id), habit_id, payload.date, payload.completed, payload.note
    )
    if not rec:
        raise HTTPException(status_code=404, detail="习惯不存在")
    return ApiResponse(
        success=True,
        data={
            "habit_id": rec.habit_id,
            "date": rec.date,
            "completed": bool(rec.completed),
        },
    )


@router.get("/{habit_id}/streak", response_model=ApiResponse)
def get_streak(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = services.get_streak(db, int(current_user.id), habit_id)
    return ApiResponse(success=True, data=stats)