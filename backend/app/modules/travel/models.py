"""Travel module models."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from app.shared.base_model import Base, TimestampMixin


class Trip(Base, TimestampMixin):
    """A trip the user has taken."""

    __tablename__ = "travel_trips"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    destination = Column(String(100), nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=True)
    cost_cny = Column(Float, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5
    note = Column(String(1000), nullable=True)
    photo_count = Column(Integer, default=0)


class BucketList(Base, TimestampMixin):
    """Places the user wants to visit."""

    __tablename__ = "travel_bucket_list"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    destination = Column(String(100), nullable=False)
    priority = Column(Integer, default=1)  # 1=high, 3=low
    note = Column(String(500), nullable=True)