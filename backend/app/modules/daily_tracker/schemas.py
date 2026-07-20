"""Daily log schemas."""

from datetime import date, datetime
from pydantic import BaseModel, Field


class DailyLogCreate(BaseModel):
    date: date
    activity_type: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    duration_minutes: int = Field(default=0, ge=0)
    mood_level: int | None = Field(default=None, ge=1, le=5)
    energy_level: int | None = Field(default=None, ge=1, le=5)
    notes: str = ""


class DailyLogResponse(BaseModel):
    id: int
    user_id: int
    date: date
    activity_type: str
    description: str
    duration_minutes: int
    mood_level: int | None
    energy_level: int | None
    notes: str
    ai_feedback: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
