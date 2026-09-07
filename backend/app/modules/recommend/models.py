"""Recommend module models."""

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from app.shared.base_model import Base, TimestampMixin


class RecommendationRun(Base, TimestampMixin):
    """One computed recommendation batch (manual open or cron slot)."""

    __tablename__ = "recommendation_runs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    slot = Column(String(20), nullable=False, default="manual")  # manual/morning/evening
    items_json = Column(Text, nullable=False, default="[]")


class Notification(Base, TimestampMixin):
    """High-priority recommendation pushed to the user inbox."""

    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    priority = Column(String(10), nullable=False, default="high")
    title = Column(String(200), nullable=False)
    body = Column(String(1000), nullable=True)
    module = Column(String(50), nullable=False, default="general")
    rule = Column(String(20), nullable=False, default="")
    is_read = Column(Integer, nullable=False, default=0)
