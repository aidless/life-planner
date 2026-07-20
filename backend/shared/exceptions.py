"""
Custom exception classes for Life Planner API.

Provides standardized exception handling with consistent error response format.
All exceptions inherit from LifePlannerException base class.
"""

from typing import Any, Optional


class LifePlannerException(Exception):
    """
    Base exception class for all Life Planner exceptions.
    
    Attributes:
        code: HTTP status code
        message: Error message
        details: Additional error details
    """
    
    def __init__(
        self,
        code: int = 500,
        message: str = "Internal server error",
        details: Optional[Any] = None,
    ):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to dictionary for API response."""
        return {
            "code": self.code,
            "data": None,
            "message": self.message,
            "details": self.details,
        }


class NotFoundException(LifePlannerException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (id: {resource_id})"
        super().__init__(code=404, message=message)


class UnauthorizedException(LifePlannerException):
    """Exception raised when authentication is required."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code=401, message=message)


class ForbiddenException(LifePlannerException):
    """Exception raised when user doesn't have permission."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(code=403, message=message)


class ValidationException(LifePlannerException):
    """Exception raised when request validation fails."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(code=400, message=message, details=details)


class ConflictException(LifePlannerException):
    """Exception raised when there's a conflict (e.g., duplicate resource)."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(code=409, message=message)


class RateLimitException(LifePlannerException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(code=429, message=message)
