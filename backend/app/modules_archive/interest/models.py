"""Interest module models."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from app.shared.base_model import Base, TimestampMixin


class Interest(Base, TimestampMixin):
    """An interest / hobby."""

    __tablename__ = "interests"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # 音乐/运动/创作/...
    description = Column(String(500), nullable=True)
    weekly_target_hours = Column(Float, default=0.0)


class InterestActivity(Base, TimestampMixin):
    """Logged activity session."""

    __tablename__ = "interest_activities"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    interest_id = Column(Integer, ForeignKey("interests.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    note = Column(String(200), nullable=True)