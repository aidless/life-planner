"""Daily activity log model."""

from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.shared.base_model import Base, TimestampMixin


class DailyLog(Base, TimestampMixin):
    """A daily activity entry tracking what the user did and how they felt."""

    __tablename__ = "daily_logs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    activity_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    duration_minutes = Column(Integer, default=0)
    mood_level = Column(Integer, nullable=True)
    energy_level = Column(Integer, nullable=True)
    notes = Column(Text, default="")
    ai_feedback = Column(Text, default="")

    user = relationship("User", back_populates="daily_logs")
