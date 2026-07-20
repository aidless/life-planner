"""Habits module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=50)
    frequency: str = Field(default="daily", pattern="^(daily|weekly)$")
    target_count: int = Field(default=1, ge=1, le=10)


class HabitUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=50)
    target_count: int | None = Field(None, ge=1, le=10)
    is_active: int | None = Field(None, ge=0, le=1)


class HabitResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str | None
    frequency: str
    target_count: int
    is_active: int
    streak: int = 0
    completion_rate_30d: float = 0.0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckinCreate(BaseModel):
    date: str = Field(...)
    completed: bool = Field(default=True)
    note: str | None = Field(None, max_length=200)


class StreakResponse(BaseModel):
    habit_id: int
    current_streak: int
    longest_streak: int
    total_checkins: int


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None