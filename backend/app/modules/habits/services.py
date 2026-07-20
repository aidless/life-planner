"""Habits module services."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.habits.models import Habit, HabitCheckin
from app.modules.habits.schemas import HabitCreate, HabitUpdate


def create_habit(db: Session, user_id: int, data: HabitCreate) -> Habit:
    h = Habit(
        user_id=user_id,
        name=data.name,
        description=data.description,
        category=data.category,
        frequency=data.frequency,
        target_count=data.target_count,
        is_active=1,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


def update_habit(db: Session, user_id: int, habit_id: int, data: HabitUpdate) -> Habit | None:
    h = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()
    if not h:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(h, k, v)
    db.commit()
    db.refresh(h)
    return h


def list_habits(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """List with streak + 30-day completion rate."""
    habits = list(
        db.execute(select(Habit).where(Habit.user_id == user_id).order_by(Habit.created_at.desc())).scalars()
    )
    result = []
    for h in habits:
        stats = _calculate_stats(db, h)
        result.append({
            "id": h.id,
            "name": h.name,
            "description": h.description,
            "category": h.category,
            "frequency": h.frequency,
            "target_count": h.target_count,
            "is_active": h.is_active,
            "streak": stats["current_streak"],
            "completion_rate_30d": stats["completion_rate_30d"],
            "created_at": h.created_at,
        })
    return result


def checkin(db: Session, user_id: int, habit_id: int, date: str, completed: bool, note: str | None) -> HabitCheckin | None:
    h = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()
    if not h:
        return None
    # upsert: delete existing checkin for this date
    existing = (
        db.query(HabitCheckin)
        .filter(
            HabitCheckin.habit_id == habit_id,
            HabitCheckin.date == date,
        )
        .first()
    )
    if existing:
        setattr(existing, "completed", 1 if completed else 0)
        setattr(existing, "note", note)
        db.commit()
        db.refresh(existing)
        return existing
    rec = HabitCheckin(
        habit_id=habit_id,
        user_id=user_id,
        date=date,
        completed=1 if completed else 0,
        note=note,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_streak(db: Session, user_id: int, habit_id: int) -> Dict[str, Any]:
    h = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()
    if not h:
        return {"habit_id": habit_id, "current_streak": 0, "longest_streak": 0, "total_checkins": 0}
    stats = _calculate_stats(db, h)
    return {
        "habit_id": habit_id,
        "current_streak": stats["current_streak"],
        "longest_streak": stats["longest_streak"],
        "total_checkins": stats["total_checkins"],
    }


def _calculate_stats(db: Session, habit: Habit) -> Dict[str, Any]:
    """Compute streak + 30-day completion rate."""
    rows = list(
        db.execute(
            select(HabitCheckin)
            .where(HabitCheckin.habit_id == habit.id, HabitCheckin.completed == 1)
            .order_by(HabitCheckin.date.desc())
        ).scalars()
    )
    if not rows:
        return {"current_streak": 0, "longest_streak": 0, "total_checkins": 0, "completion_rate_30d": 0.0}

    # Current streak: walk back from today
    today = datetime.now().strftime("%Y-%m-%d")
    dates_raw: List[Any] = list({r.date for r in rows})
    dates: List[str] = sorted([str(d) for d in dates_raw], reverse=True)
    current = 0
    cursor = datetime.strptime(today, "%Y-%m-%d")
    for d in dates:
        if d == cursor.strftime("%Y-%m-%d"):
            current += 1
            cursor -= timedelta(days=1)
        else:
            break

    # Longest streak
    sorted_asc: List[str] = sorted(dates)
    longest = 1
    streak = 1
    for i in range(1, len(sorted_asc)):
        prev = datetime.strptime(str(sorted_asc[i - 1]), "%Y-%m-%d")
        cur = datetime.strptime(str(sorted_asc[i]), "%Y-%m-%d")
        if (cur - prev).days == 1:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 1

    # 30-day completion rate
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    last30 = [d for d in dates if d >= cutoff]
    completion = len(last30) / 30.0

    return {
        "current_streak": current,
        "longest_streak": longest,
        "total_checkins": len(rows),
        "completion_rate_30d": round(completion, 2),
    }