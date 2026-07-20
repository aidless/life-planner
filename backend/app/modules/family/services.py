"""Family module services."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.family.models import FamilyMember, Interaction
from app.modules.family.schemas import MemberCreate, InteractionCreate


def create_member(db: Session, user_id: int, data: MemberCreate) -> FamilyMember:
    m = FamilyMember(
        user_id=user_id,
        name=data.name,
        relation=data.relation,
        birthday=data.birthday,
        note=data.note,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def list_members(db: Session, user_id: int) -> List[FamilyMember]:
    stmt = (
        select(FamilyMember)
        .where(FamilyMember.user_id == user_id)
        .order_by(FamilyMember.birthday.asc().nullslast())
    )
    return list(db.execute(stmt).scalars().all())


def create_interaction(db: Session, user_id: int, data: InteractionCreate) -> Interaction | None:
    """Verify member belongs to user first."""
    member = db.query(FamilyMember).filter(
        FamilyMember.id == data.member_id,
        FamilyMember.user_id == user_id,
    ).first()
    if not member:
        return None
    i = Interaction(
        user_id=user_id,
        member_id=data.member_id,
        date=data.date,
        interaction_type=data.interaction_type,
        duration_minutes=data.duration_minutes,
        note=data.note,
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def list_interactions(db: Session, user_id: int, days: int = 30) -> List[Interaction]:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    stmt = (
        select(Interaction)
        .where(Interaction.user_id == user_id, Interaction.date >= cutoff)
        .order_by(Interaction.date.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_upcoming_birthdays(db: Session, user_id: int, within_days: int = 30) -> List[Dict[str, Any]]:
    """Compute upcoming birthdays in next N days (ignore year, use MM-DD)."""
    members = list_members(db, user_id)
    today = datetime.now().date()
    result = []
    for m in members:
        if not m.birthday:
            continue
        bday = datetime.strptime(str(m.birthday), "%Y-%m-%d").date()
        # This year's birthday
        next_bday = bday.replace(year=today.year)
        if next_bday < today:
            next_bday = next_bday.replace(year=today.year + 1)
        days_until = (next_bday - today).days
        if days_until <= within_days:
            result.append({
                "member_id": m.id,
                "name": m.name,
                "relation": m.relation,
                "birthday": m.birthday,
                "days_until": days_until,
            })
    result.sort(key=lambda x: int(str(x["days_until"])))
    return result


def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
    members = list_members(db, user_id)
    interactions_30d = len(list_interactions(db, user_id, days=30))
    upcoming = get_upcoming_birthdays(db, user_id, within_days=30)
    return {
        "members_count": len(members),
        "interactions_30d": interactions_30d,
        "upcoming_birthdays": upcoming,
    }