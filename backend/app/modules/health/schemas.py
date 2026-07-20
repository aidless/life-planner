"""Health module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class HealthLogCreate(BaseModel):
    """Schema for creating a health log."""

    date: str = Field(..., description="YYYY-MM-DD")
    weight_kg: float | None = Field(None, ge=20, le=300)
    sleep_hours: float | None = Field(None, ge=0, le=24)
    exercise_minutes: int | None = Field(None, ge=0, le=1440)
    steps: int | None = Field(None, ge=0, le=200000)
    water_ml: int | None = Field(None, ge=0, le=10000)
    mood_score: int | None = Field(None, ge=1, le=10)
    notes: str | None = Field(None, max_length=500)


class HealthLogResponse(BaseModel):
    """Schema for health log response."""

    id: int
    date: str
    weight_kg: float | None
    sleep_hours: float | None
    exercise_minutes: int | None
    steps: int | None
    water_ml: int | None
    mood_score: int | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseCreate(BaseModel):
    date: str = Field(...)
    exercise_type: str = Field(..., min_length=1, max_length=50)
    duration_minutes: int = Field(..., ge=1, le=600)
    intensity: str | None = Field(None, pattern="^(light|moderate|intense)$")
    calories_burned: int | None = Field(None, ge=0, le=10000)
    notes: str | None = Field(None, max_length=500)


class ExerciseResponse(BaseModel):
    id: int
    date: str
    exercise_type: str
    duration_minutes: int
    intensity: str | None
    calories_burned: int | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthStats(BaseModel):
    """Aggregated stats over a period."""

    days: int
    avg_steps: float
    avg_sleep_hours: float
    avg_exercise_minutes: float
    avg_weight: float | None
    avg_water_ml: float
    bmi: float | None


class HealthScore(BaseModel):
    """Overall health score 0-100."""

    score: int
    level: str
    components: dict


class ApiResponse(BaseModel):
    """Unified API response envelope."""

    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None