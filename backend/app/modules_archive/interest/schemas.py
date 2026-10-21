"""Interest module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InterestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)
    weekly_target_hours: float = Field(default=0.0, ge=0, le=168)


class InterestResponse(BaseModel):
    id: int
    name: str
    category: str | None
    description: str | None
    weekly_target_hours: float
    actual_weekly_hours: float = 0.0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityCreate(BaseModel):
    interest_id: int = Field(...)
    date: str = Field(...)
    duration_minutes: int = Field(..., ge=1, le=1440)
    note: str | None = Field(None, max_length=200)


class ActivityResponse(BaseModel):
    id: int
    interest_id: int
    date: str
    duration_minutes: int
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterestStats(BaseModel):
    total_interests: int
    weekly_hours: float
    score: int  # 0-100 based on weekly hours vs target


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None