"""Learning module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=50)
    total_pages: int | None = Field(None, ge=1, le=10000)


class BookUpdate(BaseModel):
    status: str | None = Field(None, pattern="^(reading|finished|paused)$")
    current_page: int | None = Field(None, ge=0, le=10000)
    rating: int | None = Field(None, ge=1, le=5)
    note: str | None = Field(None, max_length=500)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str | None
    category: str | None
    status: str
    total_pages: int | None
    current_page: int | None
    rating: int | None
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    platform: str | None = Field(None, max_length=50)
    category: str | None = Field(None, max_length=50)


class CourseUpdate(BaseModel):
    status: str | None = Field(None, pattern="^(in_progress|finished|paused|dropped)$")
    progress_percent: int | None = Field(None, ge=0, le=100)
    note: str | None = Field(None, max_length=500)


class CourseResponse(BaseModel):
    id: int
    title: str
    platform: str | None
    category: str | None
    status: str
    progress_percent: int
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningStats(BaseModel):
    books_total: int
    books_finished: int
    courses_total: int
    courses_finished: int
    score: int  # 0-100


class StudyTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    subject: str | None = Field(None, max_length=50)
    source_type: str | None = Field(None, max_length=30)
    source_ref_id: int | None = None
    estimated_minutes: int | None = Field(None, ge=1, le=10000)
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    is_recurring: bool = False
    recurrence_rule: str | None = Field(None, max_length=50)


class StudyTaskUpdate(BaseModel):
    status: str | None = Field(None, pattern="^(todo|in_progress|done|skipped)$")
    priority: str | None = Field(None, pattern="^(low|medium|high)$")
    completed_at: datetime | None = None
    note: str | None = None


class StudyTaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    subject: str | None
    source_type: str
    source_ref_id: int | None
    estimated_minutes: int | None
    status: str
    priority: str
    is_recurring: bool
    recurrence_rule: str | None
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None