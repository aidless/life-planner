"""Psychology module services."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.psychology.models import MoodLog, Reflection
from app.modules.psychology.schemas import MoodCreate, ReflectionCreate


def create_mood(db: Session, user_id: int, data: MoodCreate) -> MoodLog:
    m = MoodLog(
        user_id=user_id,
        date=data.date,
        mood_score=data.mood_score,
        energy_score=data.energy_score,
        stress_score=data.stress_score,
        note=data.note,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def list_moods(db: Session, user_id: int, days: int = 30) -> List[MoodLog]:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    stmt = (
        select(MoodLog)
        .where(MoodLog.user_id == user_id, MoodLog.date >= cutoff)
        .order_by(MoodLog.date.desc())
    )
    return list(db.execute(stmt).scalars().all())


def create_reflection(db: Session, user_id: int, data: ReflectionCreate) -> Reflection:
    r = Reflection(
        user_id=user_id,
        date=data.date,
        prompt=data.prompt,
        content=data.content,
        gratitude=data.gratitude,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def list_reflections(db: Session, user_id: int, limit: int = 20) -> List[Reflection]:
    stmt = (
        select(Reflection)
        .where(Reflection.user_id == user_id)
        .order_by(Reflection.date.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def get_stats(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
    """Psychology score = avg_mood / 10 × 100 (mood is the headline metric)."""
    moods = list_moods(db, user_id, days)
    if not moods:
        return {"days": 0, "avg_mood": 0.0, "avg_energy": 0.0, "avg_stress": 0.0, "score": 0}

    n = len(moods)
    avg_mood = sum(m.mood_score for m in moods) / n
    energies = [m.energy_score for m in moods if m.energy_score]
    avg_energy = sum(energies) / len(energies) if energies else 0.0
    stresses = [m.stress_score for m in moods if m.stress_score]
    avg_stress = sum(stresses) / len(stresses) if stresses else 0.0

    # Mood dominates; energy and stress adjust slightly
    score = round(avg_mood * 10)  # 0-100

    return {
        "days": n,
        "avg_mood": round(avg_mood, 1),
        "avg_energy": round(avg_energy, 1),
        "avg_stress": round(avg_stress, 1),
        "score": min(100, max(0, score)),
    }