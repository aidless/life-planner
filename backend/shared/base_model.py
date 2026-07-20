"""
Base model class with common fields for all database models.

Provides:
- id: Primary key (UUID or Integer)
- created_at: Timestamp of creation
- updated_at: Timestamp of last update
- is_deleted: Soft delete flag
"""

from sqlalchemy import Column, DateTime, Boolean, func, Integer
from sqlalchemy.orm import declared_attr
from datetime import datetime
import uuid

from database import Base


class BaseModel(Base):
    """
    Abstract base model with common fields.
    All models should inherit from this class.
    """
    
    __abstract__ = True
    
    # Primary key - using Integer for compatibility with SQLite and PostgreSQL
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    
    # Soft delete
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name automatically from class name."""
        # Convert CamelCase to snake_case
        name = cls.__name__
        return "".join(
            ["_" + c.lower() if c.isupper() else c for c in name]
        ).lstrip("_") + "s"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_deleted": self.is_deleted,
        }
    
    def soft_delete(self):
        """Mark record as deleted (soft delete)."""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft-deleted record."""
        self.is_deleted = False
        self.updated_at = datetime.utcnow()
