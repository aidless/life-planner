"""Health module models."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from app.shared.base_model import Base, TimestampMixin


class HealthLog(Base, TimestampMixin):
    """Daily health log."""

    __tablename__ = "health_logs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    weight_kg = Column(Float, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    exercise_minutes = Column(Integer, nullable=True)
    steps = Column(Integer, nullable=True)
    water_ml = Column(Integer, nullable=True)
    mood_score = Column(Integer, nullable=True)  # 1-10
    notes = Column(String(500), nullable=True)


class ExerciseRecord(Base, TimestampMixin):
    """Exercise record."""

    __tablename__ = "exercise_records"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    exercise_type = Column(String(50), nullable=False)  # running/yoga/swimming/...
    duration_minutes = Column(Integer, nullable=False)
    intensity = Column(String(20), nullable=True)  # light/moderate/intense
    calories_burned = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True)