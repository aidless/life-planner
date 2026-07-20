"""Interest module services."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.interest.models import Interest, InterestActivity
from app.modules.interest.schemas import InterestCreate, ActivityCreate


def create_interest(db: Session, user_id: int, data: InterestCreate) -> Interest:
    i = Interest(
        user_id=user_id,
        name=data.name,
        category=data.category,
        description=data.description,
        weekly_target_hours=data.weekly_target_hours,
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def list_interests(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """List with actual weekly hours."""
    interests = list(
        db.execute(
            select(Interest).where(Interest.user_id == user_id).order_by(Interest.created_at.desc())
        ).scalars()
    )
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    result = []
    for i in interests:
        total_minutes = (
            db.execute(
                select(func.coalesce(func.sum(InterestActivity.duration_minutes), 0))
                .where(
                    InterestActivity.interest_id == i.id,
                    InterestActivity.date >= cutoff,
                )
            ).scalar()
            or 0
        )
        result.append({
            "id": i.id,
            "name": i.name,
            "category": i.category,
            "description": i.description,
            "weekly_target_hours": float(i.weekly_target_hours),
            "actual_weekly_hours": round(float(total_minutes) / 60.0, 1),
            "created_at": i.created_at,
        })
    return result


def create_activity(db: Session, user_id: int, data: ActivityCreate) -> InterestActivity | None:
    i = db.query(Interest).filter(
        Interest.id == data.interest_id,
        Interest.user_id == user_id,
    ).first()
    if not i:
        return None
    a = InterestActivity(
        user_id=user_id,
        interest_id=data.interest_id,
        date=data.date,
        duration_minutes=data.duration_minutes,
        note=data.note,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def list_activities(db: Session, user_id: int, days: int = 30) -> List[InterestActivity]:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    stmt = (
        select(InterestActivity)
        .where(InterestActivity.user_id == user_id, InterestActivity.date >= cutoff)
        .order_by(InterestActivity.date.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
    interests_data = list_interests(db, user_id)
    total_weekly = sum(item["actual_weekly_hours"] for item in interests_data)
    total_target = sum(item["weekly_target_hours"] for item in interests_data)

    # Score: weekly hours vs target (max 100 at 10h)
    score = min(100, round(total_weekly * 10))

    return {
        "total_interests": len(interests_data),
        "weekly_hours": round(total_weekly, 1),
        "weekly_target_hours": round(total_target, 1),
        "score": score,
    }