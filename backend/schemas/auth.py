"""
Authentication schemas for Life Planner API.

This module defines Pydantic models for:
- User registration (phone, password, nickname, etc.)
- User login (phone, password)
- Token response (JWT token + user info)
- User profile update (nickname, province, etc.)
- User response (user info without sensitive data)
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request schema."""
    
    phone: str = Field(..., description="User phone number", min_length=11, max_length=11, pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., description="User password", min_length=8, max_length=50)
    nickname: str = Field(..., description="User nickname", min_length=1, max_length=50)
    province: Optional[str] = Field(None, description="User province")
    graduation_year: Optional[int] = Field(None, description="User graduation year")


class UserLogin(BaseModel):
    """User login request schema."""
    
    phone: str = Field(..., description="User phone number", min_length=11, max_length=11, pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., description="User password", min_length=8, max_length=50)


class TokenResponse(BaseModel):
    """Token response schema."""
    
    token: str = Field(..., description="JWT access token")
    user: "UserResponse" = Field(..., description="User information")


class UserProfileUpdate(BaseModel):
    """User profile update request schema."""
    
    nickname: Optional[str] = Field(None, description="User nickname", min_length=1, max_length=50)
    province: Optional[str] = Field(None, description="User province")
    subject_combination: Optional[str] = Field(None, description="User subject combination")
    graduation_year: Optional[int] = Field(None, description="User graduation year")


class UserResponse(BaseModel):
    """User response schema (without sensitive data)."""
    
    id: int = Field(..., description="User ID")
    phone: str = Field(..., description="User phone number")
    nickname: str = Field(..., description="User nickname")
    province: Optional[str] = Field(None, description="User province")
    subject_combination: Optional[str] = Field(None, description="User subject combination")
    graduation_year: Optional[int] = Field(None, description="User graduation year")
    created_at: datetime = Field(..., description="User creation time")
    updated_at: datetime = Field(..., description="User last update time")
    
    model_config = ConfigDict(from_attributes=True)
