"""Health module services."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.health.models import HealthLog, ExerciseRecord
from app.modules.health.schemas import HealthLogCreate, ExerciseCreate


def create_health_log(db: Session, user_id: int, data: HealthLogCreate) -> HealthLog:
    log = HealthLog(
        user_id=user_id,
        date=data.date,
        weight_kg=data.weight_kg,
        sleep_hours=data.sleep_hours,
        exercise_minutes=data.exercise_minutes,
        steps=data.steps,
        water_ml=data.water_ml,
        mood_score=data.mood_score,
        notes=data.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_health_logs(db: Session, user_id: int, days: int = 30) -> List[HealthLog]:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    stmt = (
        select(HealthLog)
        .where(HealthLog.user_id == user_id, HealthLog.date >= cutoff)
        .order_by(HealthLog.date.desc())
    )
    return list(db.execute(stmt).scalars().all())


def create_exercise(db: Session, user_id: int, data: ExerciseCreate) -> ExerciseRecord:
    rec = ExerciseRecord(
        user_id=user_id,
        date=data.date,
        exercise_type=data.exercise_type,
        duration_minutes=data.duration_minutes,
        intensity=data.intensity,
        calories_burned=data.calories_burned,
        notes=data.notes,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def list_exercises(db: Session, user_id: int, days: int = 30) -> List[ExerciseRecord]:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    stmt = (
        select(ExerciseRecord)
        .where(ExerciseRecord.user_id == user_id, ExerciseRecord.date >= cutoff)
        .order_by(ExerciseRecord.date.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_stats(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
    logs = list_health_logs(db, user_id, days)
    if not logs:
        return {
            "days": 0,
            "avg_steps": 0.0,
            "avg_sleep_hours": 0.0,
            "avg_exercise_minutes": 0.0,
            "avg_weight": None,
            "avg_water_ml": 0.0,
            "bmi": None,
        }

    n = len(logs)
    avg_steps = sum(l.steps or 0 for l in logs) / n
    avg_sleep = sum(l.sleep_hours or 0 for l in logs) / n
    avg_exercise = sum(l.exercise_minutes or 0 for l in logs) / n
    avg_water = sum(l.water_ml or 0 for l in logs) / n
    weights = [l.weight_kg for l in logs if l.weight_kg]
    avg_weight = sum(weights) / len(weights) if weights else None

    return {
        "days": n,
        "avg_steps": round(avg_steps, 1),
        "avg_sleep_hours": round(avg_sleep, 1),
        "avg_exercise_minutes": round(avg_exercise, 1),
        "avg_weight": round(avg_weight, 1) if avg_weight else None,
        "avg_water_ml": round(avg_water, 1),
        "bmi": None,  # requires height — not stored yet
    }


def calculate_health_score(db: Session, user_id: int) -> Dict[str, Any]:
    """Health score 0-100 based on steps + sleep + exercise.

    Core insight: health = daily habits, not single metrics.
    """
    stats = get_stats(db, user_id, days=30)

    step_rate = min(1.0, stats["avg_steps"] / 10000.0)
    sleep_rate = min(1.0, stats["avg_sleep_hours"] / 8.0)
    exercise_rate = min(1.0, stats["avg_exercise_minutes"] / 30.0)

    score = round(
        (step_rate * 0.4 + sleep_rate * 0.3 + exercise_rate * 0.3) * 100
    )

    if score >= 80:
        level = "优秀"
    elif score >= 60:
        level = "良好"
    elif score >= 40:
        level = "一般"
    else:
        level = "待提升"

    return {
        "score": score,
        "level": level,
        "components": {
            "steps": {"value": stats["avg_steps"], "rate": round(step_rate, 2), "weight": 0.4},
            "sleep": {"value": stats["avg_sleep_hours"], "rate": round(sleep_rate, 2), "weight": 0.3},
            "exercise": {"value": stats["avg_exercise_minutes"], "rate": round(exercise_rate, 2), "weight": 0.3},
        },
    }