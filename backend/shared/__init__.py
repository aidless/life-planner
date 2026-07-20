"""
Shared module for common utilities and base classes.

This package contains shared code used across different modules:
- base_model.py: Base model class with common fields
- exceptions.py: Custom exception classes
- pagination.py: Pagination utilities
- response.py: Standard API response format
"""

from .base_model import BaseModel
from .exceptions import (
    LifePlannerException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
)

__all__ = [
    "BaseModel",
    "LifePlannerException",
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "ValidationException",
]
