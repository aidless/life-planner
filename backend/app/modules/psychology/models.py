"""Psychology module models."""

from sqlalchemy import Column, String, Integer, ForeignKey
from app.shared.base_model import Base, TimestampMixin


class MoodLog(Base, TimestampMixin):
    """Daily mood/energy/stress check-in."""

    __tablename__ = "mood_logs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    mood_score = Column(Integer, nullable=False)  # 1-10
    energy_score = Column(Integer, nullable=True)  # 1-10
    stress_score = Column(Integer, nullable=True)  # 1-10
    note = Column(String(500), nullable=True)


class Reflection(Base, TimestampMixin):
    """Periodic self-reflection."""

    __tablename__ = "reflections"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    prompt = Column(String(200), nullable=True)  # 今日问题
    content = Column(String(2000), nullable=False)
    gratitude = Column(String(500), nullable=True)  # 感恩 3 件事