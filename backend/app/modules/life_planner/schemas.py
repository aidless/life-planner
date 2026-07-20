"""Life goal schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    category: str = "general"
    target_date: datetime | None = None
    priority: int = Field(default=1, ge=1, le=3)


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    status: str | None = None
    progress: float | None = None
    target_date: datetime | None = None
    priority: int | None = None


class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    category: str
    status: str
    progress: float
    target_date: datetime | None
    priority: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
