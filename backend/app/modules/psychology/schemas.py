"""Psychology module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MoodCreate(BaseModel):
    date: str = Field(...)
    mood_score: int = Field(..., ge=1, le=10)
    energy_score: int | None = Field(None, ge=1, le=10)
    stress_score: int | None = Field(None, ge=1, le=10)
    note: str | None = Field(None, max_length=500)


class MoodResponse(BaseModel):
    id: int
    date: str
    mood_score: int
    energy_score: int | None
    stress_score: int | None
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReflectionCreate(BaseModel):
    date: str = Field(...)
    prompt: str | None = Field(None, max_length=200)
    content: str = Field(..., min_length=1, max_length=2000)
    gratitude: str | None = Field(None, max_length=500)


class ReflectionResponse(BaseModel):
    id: int
    date: str
    prompt: str | None
    content: str
    gratitude: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PsychologyStats(BaseModel):
    days: int
    avg_mood: float
    avg_energy: float
    avg_stress: float
    score: int  # 0-100


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None