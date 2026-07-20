"""Auth request/response schemas using Pydantic."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration request."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=8, max_length=100)
    display_name: str = Field(default="", max_length=100)


class UserLogin(BaseModel):
    """Schema for login request."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(BaseModel):
    """Schema for user data in API responses."""

    id: int
    username: str
    email: str
    display_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for auth token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ApiResponse(BaseModel):
    """Unified API response envelope."""

    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None
