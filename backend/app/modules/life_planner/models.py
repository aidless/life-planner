"""Life goal model for long-term planning."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.shared.base_model import Base, TimestampMixin


class LifeGoal(Base, TimestampMixin):
    """A long-term life goal with progress tracking."""

    __tablename__ = "life_goals"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(50), default="general")
    status = Column(String(20), default="active")
    progress = Column(Float, default=0.0)
    target_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Integer, default=1)

    user = relationship("User", back_populates="goals")
