"""Meaning module services."""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.meaning.models import Value, LifePurpose
from app.modules.meaning.schemas import ValueCreate, ValueUpdate, PurposeUpdate


def create_value(db: Session, user_id: int, data: ValueCreate) -> Value:
    v = Value(
        user_id=user_id,
        name=data.name,
        description=data.description,
        importance=data.importance,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def update_value(db: Session, user_id: int, value_id: int, data: ValueUpdate) -> Value | None:
    v = db.query(Value).filter(Value.id == value_id, Value.user_id == user_id).first()
    if not v:
        return None
    for k, val in data.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    db.commit()
    db.refresh(v)
    return v


def list_values(db: Session, user_id: int) -> List[Value]:
    stmt = (
        select(Value)
        .where(Value.user_id == user_id)
        .order_by(Value.importance.desc(), Value.created_at.asc())
    )
    return list(db.execute(stmt).scalars().all())


def delete_value(db: Session, user_id: int, value_id: int) -> bool:
    v = db.query(Value).filter(Value.id == value_id, Value.user_id == user_id).first()
    if not v:
        return False
    db.delete(v)
    db.commit()
    return True


def upsert_purpose(db: Session, user_id: int, statement: str) -> LifePurpose:
    """Mark previous as not-current, create new version."""
    db.query(LifePurpose).filter(
        LifePurpose.user_id == user_id,
        LifePurpose.is_current == 1,
    ).update({"is_current": 0})

    latest_version = db.execute(
        select(func.coalesce(func.max(LifePurpose.version), 0)).where(
            LifePurpose.user_id == user_id
        )
    ).scalar() or 0

    p = LifePurpose(
        user_id=user_id,
        statement=statement,
        version=latest_version + 1,
        is_current=1,
        # updated_at comes from TimestampMixin (auto)
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def get_current_purpose(db: Session, user_id: int) -> LifePurpose | None:
    stmt = (
        select(LifePurpose)
        .where(LifePurpose.user_id == user_id, LifePurpose.is_current == 1)
        .order_by(LifePurpose.version.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
    values = list_values(db, user_id)
    purpose = get_current_purpose(db, user_id)

    avg_importance = (
        sum(v.importance for v in values) / len(values) if values else 0.0
    )
    # Score: values (×15 max) + purpose (×25) capped at 100
    score = min(100, len(values) * 15 + (25 if purpose else 0))

    return {
        "values_count": len(values),
        "has_purpose": purpose is not None,
        "avg_importance": round(avg_importance, 1),
        "score": score,
    }