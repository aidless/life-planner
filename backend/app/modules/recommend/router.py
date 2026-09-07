"""Recommend module API router."""

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.recommend import services
from app.modules.recommend.schemas import ApiResponse, NotificationResponse
from app.shared.ai_client import ai_client

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


async def _coach_note(items: list[dict]) -> tuple[str | None, str]:
    """LLM polish layer. Returns (note, mode); never raises.

    The LLM only writes copy — all numbers come from rule output,
    and the prompt forbids inventing figures.
    """
    if not items or not ai_client.enabled:
        return None, "rule"
    try:
        digest = [
            {"priority": i["priority"], "title": i["title"], "reason": i["reason"]}
            for i in items[:6]
        ]
        note = await ai_client.analyze(
            "你是人生规划教练。用不超过 120 字给出一句今日行动总建议，"
            "语气直接。只能引用下面材料里的数字，禁止编造任何数字。",
            json.dumps(digest, ensure_ascii=False),
            max_tokens=256,
        )
        return note, "llm"
    except Exception:
        return None, "rule"


@router.get("/today", response_model=ApiResponse)
async def today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.compute_today(db, int(current_user.id))
    note, mode = await _coach_note(items)
    return ApiResponse(success=True, data={
        "items": items,
        "coach_note": note,
        "coach_mode": mode,  # llm | rule
    })


@router.get("/history", response_model=ApiResponse)
def history(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(
        success=True,
        data=services.list_history(db, int(current_user.id), days))


@router.get("/notifications", response_model=ApiResponse)
def notifications(
    unread_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_notifications(db, int(current_user.id), unread_only)
    return ApiResponse(success=True, data=[
        NotificationResponse.model_validate(n).model_dump(mode="json")
        for n in items
    ])


@router.post("/notifications/{notif_id}/read", response_model=ApiResponse)
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = services.mark_read(db, int(current_user.id), notif_id)
    return ApiResponse(success=True, data={"updated": ok})
