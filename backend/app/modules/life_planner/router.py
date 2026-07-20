"""Life goal API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import ApiResponse
from app.modules.life_planner import schemas, services

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.post("", response_model=ApiResponse)
def create_goal(
    payload: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = services.create_goal(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data=schemas.GoalResponse.model_validate(goal).model_dump(),
    )


@router.get("", response_model=ApiResponse)
def list_goals(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goals = services.get_goals(db, int(current_user.id), status_filter)
    return ApiResponse(
        success=True,
        data=[schemas.GoalResponse.model_validate(g).model_dump() for g in goals],
    )


@router.get("/{goal_id}", response_model=ApiResponse)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = services.get_goal(db, int(current_user.id), goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    return ApiResponse(
        success=True,
        data=schemas.GoalResponse.model_validate(goal).model_dump(),
    )


@router.put("/{goal_id}", response_model=ApiResponse)
def update_goal(
    goal_id: int,
    payload: schemas.GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = services.update_goal(db, int(current_user.id), goal_id, payload)
    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")
    return ApiResponse(
        success=True,
        data=schemas.GoalResponse.model_validate(goal).model_dump(),
    )


@router.delete("/{goal_id}", response_model=ApiResponse)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = services.delete_goal(db, int(current_user.id), goal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="目标不存在")
    return ApiResponse(success=True, data={"message": "目标已删除"})
