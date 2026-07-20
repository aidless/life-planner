"""Daily log CRUD service."""

from datetime import date

from sqlalchemy.orm import Session

from app.modules.daily_tracker.models import DailyLog
from app.modules.daily_tracker.schemas import DailyLogCreate
from app.shared.ai_client import ai_client


def create_log(db: Session, user_id: int, data: DailyLogCreate) -> DailyLog:
    log = DailyLog(
        user_id=user_id,
        date=data.date,
        activity_type=data.activity_type,
        description=data.description,
        duration_minutes=data.duration_minutes,
        mood_level=data.mood_level,
        energy_level=data.energy_level,
        notes=data.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_logs(
    db: Session,
    user_id: int,
    target_date: date | None = None,
    activity_type: str | None = None,
) -> list[DailyLog]:
    query = db.query(DailyLog).filter(DailyLog.user_id == user_id)
    if target_date:
        query = query.filter(DailyLog.date == target_date)
    if activity_type:
        query = query.filter(DailyLog.activity_type == activity_type)
    return query.order_by(DailyLog.date.desc(), DailyLog.created_at.desc()).all()


def get_log(db: Session, user_id: int, log_id: int) -> DailyLog | None:
    return (
        db.query(DailyLog)
        .filter(DailyLog.id == log_id, DailyLog.user_id == user_id)
        .first()
    )


def delete_log(db: Session, user_id: int, log_id: int) -> bool:
    log = get_log(db, user_id, log_id)
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True


async def generate_ai_feedback(db: Session, user_id: int, log_id: int) -> str | None:
    log = get_log(db, user_id, log_id)
    if not log:
        return None

    activities = [{
        "activity_type": log.activity_type,
        "description": log.description,
        "duration_minutes": log.duration_minutes,
        "mood_level": log.mood_level,
        "energy_level": log.energy_level,
    }]

    feedback = await ai_client.analyze_daily_log(activities)
    setattr(log, "ai_feedback", feedback)
    db.commit()
    db.refresh(log)
    return feedback
