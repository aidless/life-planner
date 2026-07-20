"""Habits module models."""

from sqlalchemy import Column, String, Integer, ForeignKey, Date
from app.shared.base_model import Base, TimestampMixin


class Habit(Base, TimestampMixin):
    """A habit to track."""

    __tablename__ = "habits"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)  # 健康/学习/生活
    frequency = Column(String(20), default="daily")  # daily/weekly
    target_count = Column(Integer, default=1)  # 每天几次
    is_active = Column(Integer, default=1)


class HabitCheckin(Base, TimestampMixin):
    """Daily checkin record."""

    __tablename__ = "habit_checkins"

    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    completed = Column(Integer, default=1)  # 0/1
    note = Column(String(200), nullable=True)