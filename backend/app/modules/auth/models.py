"""User model for authentication."""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.shared.base_model import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User account model."""

    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    display_name = Column(String(100), default="")

    goals = relationship("LifeGoal", back_populates="user", cascade="all, delete-orphan")
    daily_logs = relationship("DailyLog", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
