"""Dashboard module API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.dashboard.services import build_dashboard
from app.modules.dashboard.schemas import ApiResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=ApiResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dashboard = build_dashboard(int(current_user.id), db)
    return ApiResponse(success=True, data=dashboard.model_dump(mode="json"))