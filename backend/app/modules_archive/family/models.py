"""Family module models — 仅存公开信息（不存对话/隐私）。"""

from sqlalchemy import Column, String, Integer, ForeignKey, Date
from app.shared.base_model import Base, TimestampMixin


class FamilyMember(Base, TimestampMixin):
    """A family member or close relation (公开元数据)."""

    __tablename__ = "family_members"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    relation = Column(String(30), nullable=False)  # 父/母/兄/姐/...
    birthday = Column(String(10), nullable=True)  # YYYY-MM-DD
    note = Column(String(200), nullable=True)


class Interaction(Base, TimestampMixin):
    """Interaction log (when/how-often, not content)."""

    __tablename__ = "family_interactions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    interaction_type = Column(String(30), nullable=False)  # call/visit/message
    duration_minutes = Column(Integer, nullable=True)
    note = Column(String(200), nullable=True)