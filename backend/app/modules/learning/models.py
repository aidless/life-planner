"""Learning module models."""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text
from app.shared.base_model import Base, TimestampMixin


class Book(Base, TimestampMixin):
    """Book the user is reading or has finished."""

    __tablename__ = "learning_books"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    status = Column(String(20), default="reading")  # reading/finished/paused
    total_pages = Column(Integer, nullable=True)
    current_page = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)  # 1-5
    note = Column(String(500), nullable=True)


class Course(Base, TimestampMixin):
    """Course / class / online training."""

    __tablename__ = "learning_courses"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=True)  # Coursera/慕课/B站/...
    category = Column(String(50), nullable=True)
    status = Column(String(20), default="in_progress")
    progress_percent = Column(Integer, default=0)  # 0-100
    note = Column(String(500), nullable=True)


class StudyTask(Base, TimestampMixin):
    """Discrete study task (chapter / exercise / practice set)."""

    __tablename__ = "study_tasks"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(50), nullable=True)  # math/cs/english/...
    source_type = Column(String(30), default="standalone")
    # standalone | book | course | exam | repetition
    source_ref_id = Column(Integer, nullable=True)  # optional FK to book/course
    estimated_minutes = Column(Integer, nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="todo")
    # todo | in_progress | done | skipped
    priority = Column(String(10), default="medium")  # low|medium|high
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(50), nullable=True)  # e.g. "daily"
    note = Column(Text, nullable=True)
