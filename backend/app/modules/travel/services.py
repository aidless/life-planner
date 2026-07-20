"""Travel module services."""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.travel.models import Trip, BucketList
from app.modules.travel.schemas import TripCreate, BucketCreate


def create_trip(db: Session, user_id: int, data: TripCreate) -> Trip:
    t = Trip(
        user_id=user_id,
        destination=data.destination,
        start_date=data.start_date,
        end_date=data.end_date,
        cost_cny=data.cost_cny,
        rating=data.rating,
        note=data.note,
        photo_count=data.photo_count or 0,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def list_trips(db: Session, user_id: int) -> List[Trip]:
    stmt = (
        select(Trip)
        .where(Trip.user_id == user_id)
        .order_by(Trip.start_date.desc())
    )
    return list(db.execute(stmt).scalars().all())


def create_bucket(db: Session, user_id: int, data: BucketCreate) -> BucketList:
    b = BucketList(
        user_id=user_id,
        destination=data.destination,
        priority=data.priority,
        note=data.note,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def list_bucket(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """List bucket items with completion status."""
    rows = list(
        db.execute(
            select(BucketList).where(BucketList.user_id == user_id).order_by(BucketList.priority.asc())
        ).scalars()
    )
    trip_destinations = {
        t.destination for t in list_trips(db, user_id)
    }
    result = []
    for b in rows:
        result.append({
            "id": b.id,
            "destination": b.destination,
            "priority": b.priority,
            "note": b.note,
            "completed": b.destination in trip_destinations,
            "created_at": b.created_at,
        })
    return result


def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
    trips = list_trips(db, user_id)
    bucket = list_bucket(db, user_id)
    year = datetime.now().year
    trips_this_year = sum(1 for t in trips if t.start_date.startswith(str(year)))
    countries = len({t.destination for t in trips})

    # Score: trips per year (×25 max)
    score = min(100, trips_this_year * 25)

    return {
        "trips_total": len(trips),
        "trips_this_year": trips_this_year,
        "countries_visited": countries,
        "bucket_list_size": len(bucket),
        "score": score,
    }