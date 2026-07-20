"""Intimacy module services."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.intimacy.models import Relationship, Anniversary
from app.modules.intimacy.schemas import RelationshipCreate, AnniversaryCreate


def create_relationship(db: Session, user_id: int, data: RelationshipCreate) -> Relationship:
    r = Relationship(
        user_id=user_id,
        name=data.name,
        relation_type=data.relation_type,
        anniversary=data.anniversary,
        status="active",
        note=data.note,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def list_relationships(db: Session, user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
    stmt = select(Relationship).where(Relationship.user_id == user_id)
    if active_only:
        stmt = stmt.where(Relationship.status == "active")
    rows = list(db.execute(stmt.order_by(Relationship.anniversary.asc().nullslast())).scalars())

    today = datetime.now().date()
    result = []
    for r in rows:
        days_to = None
        if r.anniversary:
            anniv = datetime.strptime(str(r.anniversary), "%Y-%m-%d").date()
            next_anniv = anniv.replace(year=today.year)
            if next_anniv < today:
                next_anniv = next_anniv.replace(year=today.year + 1)
            days_to = (next_anniv - today).days
        result.append({
            "id": r.id,
            "name": r.name,
            "relation_type": r.relation_type,
            "anniversary": r.anniversary,
            "status": r.status,
            "note": r.note,
            "days_to_anniversary": days_to,
            "created_at": r.created_at,
        })
    return result


def create_anniversary(db: Session, user_id: int, data: AnniversaryCreate) -> Anniversary:
    a = Anniversary(
        user_id=user_id,
        title=data.title,
        date=data.date,
        recurring=1 if data.recurring else 0,
        note=data.note,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def list_anniversaries(db: Session, user_id: int) -> List[Dict[str, Any]]:
    rows = list(
        db.execute(
            select(Anniversary).where(Anniversary.user_id == user_id).order_by(Anniversary.date.asc())
        ).scalars()
    )
    today = datetime.now().date()
    result = []
    for a in rows:
        anniv = datetime.strptime(str(a.date), "%Y-%m-%d").date()
        next_date = anniv.replace(year=today.year)
        if next_date < today:
            next_date = next_date.replace(year=today.year + 1)
        days_until = (next_date - today).days
        result.append({
            "id": a.id,
            "title": a.title,
            "date": a.date,
            "recurring": bool(a.recurring),
            "note": a.note,
            "days_until": days_until,
            "created_at": a.created_at,
        })
    result.sort(key=lambda x: int(str(x["days_until"])) if x["days_until"] is not None else 0)
    return result


def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
    rels = list_relationships(db, user_id, active_only=True)
    annivs = list_anniversaries(db, user_id)
    upcoming = [a for a in annivs if a["days_until"] is not None and a["days_until"] <= 30]

    # Score: 50 for any active relationship + bonus per anniversary
    score = 50 if rels else 0
    score = min(100, score + len(annivs) * 10)

    return {
        "active_relationships": len(rels),
        "anniversaries_count": len(annivs),
        "upcoming_anniversaries": upcoming,
        "score": score,
    }