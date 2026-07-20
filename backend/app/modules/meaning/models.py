"""Meaning module models — 价值观 + 人生使命."""

from sqlalchemy import Column, String, Integer, ForeignKey, Float
from app.shared.base_model import Base, TimestampMixin


class Value(Base, TimestampMixin):
    """A core personal value (5 values max recommended)."""

    __tablename__ = "meaning_values"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)  # 自由/家庭/成长/...
    description = Column(String(500), nullable=True)
    importance = Column(Integer, default=5)  # 1-10


class LifePurpose(Base, TimestampMixin):
    """User's life purpose / mission statement."""

    __tablename__ = "meaning_purpose"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    statement = Column(String(1000), nullable=False)
    version = Column(Integer, default=1)
    is_current = Column(Integer, default=1)
    # updated_at provided by TimestampMixin (DateTime)