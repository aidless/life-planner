"""Intimacy module models — 仅元数据（不存私密内容）。"""

from sqlalchemy import Column, String, Integer, ForeignKey
from app.shared.base_model import Base, TimestampMixin


class Relationship(Base, TimestampMixin):
    """A significant relationship (公开元数据)."""

    __tablename__ = "intimacy_relationships"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    relation_type = Column(String(30), nullable=False)  # 伴侣/配偶/...
    anniversary = Column(String(10), nullable=True)  # YYYY-MM-DD
    status = Column(String(20), default="active")  # active/ended
    note = Column(String(500), nullable=True)


class Anniversary(Base, TimestampMixin):
    """重要纪念日."""

    __tablename__ = "intimacy_anniversaries"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    recurring = Column(Integer, default=1)  # 0/1
    note = Column(String(200), nullable=True)