"""Social module models — 朋友元数据 + 互动记录."""

from sqlalchemy import Column, String, Integer, ForeignKey
from app.shared.base_model import Base, TimestampMixin


class Contact(Base, TimestampMixin):
    """A friend/contact."""

    __tablename__ = "social_contacts"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    relation = Column(String(30), nullable=True)  # 朋友/同事/同学/...
    closeness = Column(Integer, default=5)  # 1-10 亲密度
    note = Column(String(200), nullable=True)


class SocialInteraction(Base, TimestampMixin):
    """Logged interaction (when, not content)."""

    __tablename__ = "social_interactions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("social_contacts.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    interaction_type = Column(String(30), nullable=False)  # call/message/meet
    duration_minutes = Column(Integer, nullable=True)
    note = Column(String(200), nullable=True)