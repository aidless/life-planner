"""Social module services."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.social.models import Contact, SocialInteraction
from app.modules.social.schemas import ContactCreate, InteractionCreate


RECONNECT_THRESHOLD_DAYS = 30


def create_contact(db: Session, user_id: int, data: ContactCreate) -> Contact:
    c = Contact(
        user_id=user_id,
        name=data.name,
        relation=data.relation,
        closeness=data.closeness,
        note=data.note,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def list_contacts(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """List with last-contact age."""
    contacts = list(
        db.execute(
            select(Contact).where(Contact.user_id == user_id).order_by(Contact.closeness.desc())
        ).scalars()
    )
    today = datetime.now().date()
    result = []
    for c in contacts:
        last = db.execute(
            select(func.max(SocialInteraction.date)).where(
                SocialInteraction.contact_id == c.id,
                SocialInteraction.user_id == user_id,
            )
        ).scalar()
        days_since = None
        needs_reconnect = False
        if last:
            last_date = datetime.strptime(str(last), "%Y-%m-%d").date()
            days_since = (today - last_date).days
            needs_reconnect = bool(
                days_since > RECONNECT_THRESHOLD_DAYS and int(c.closeness) >= 7
            )
        result.append({
            "id": c.id,
            "name": c.name,
            "relation": c.relation,
            "closeness": c.closeness,
            "note": c.note,
            "days_since_last_contact": days_since,
            "needs_reconnect": needs_reconnect,
            "created_at": c.created_at,
        })
    return result


def create_interaction(db: Session, user_id: int, data: InteractionCreate) -> SocialInteraction | None:
    c = db.query(Contact).filter(
        Contact.id == data.contact_id,
        Contact.user_id == user_id,
    ).first()
    if not c:
        return None
    i = SocialInteraction(
        user_id=user_id,
        contact_id=data.contact_id,
        date=data.date,
        interaction_type=data.interaction_type,
        duration_minutes=data.duration_minutes,
        note=data.note,
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def list_interactions(db: Session, user_id: int, days: int = 30) -> List[SocialInteraction]:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    stmt = (
        select(SocialInteraction)
        .where(SocialInteraction.user_id == user_id, SocialInteraction.date >= cutoff)
        .order_by(SocialInteraction.date.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_reconnect_suggestions(db: Session, user_id: int) -> List[Dict[str, Any]]:
    contacts_data = list_contacts(db, user_id)
    suggestions = []
    for c in contacts_data:
        if c["needs_reconnect"]:
            suggestions.append({
                "contact_id": c["id"],
                "name": c["name"],
                "closeness": c["closeness"],
                "days_since_last": c["days_since_last_contact"],
            })
    suggestions.sort(key=lambda x: -x["closeness"])
    return suggestions


def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
    contacts_data = list_contacts(db, user_id)
    close_friends = sum(1 for c in contacts_data if c["closeness"] >= 8)
    interactions_30d = len(list_interactions(db, user_id, days=30))
    reconnect = get_reconnect_suggestions(db, user_id)
    return {
        "contacts_count": len(contacts_data),
        "close_friends": close_friends,
        "interactions_30d": interactions_30d,
        "reconnect_needed": reconnect,
    }