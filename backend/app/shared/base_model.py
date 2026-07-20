"""Base model with common columns for all database models."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Abstract base for all models."""
    pass


class TimestampMixin:
    """Mixin that adds id, created_at, and updated_at columns."""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
