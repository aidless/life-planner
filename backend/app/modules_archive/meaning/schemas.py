"""Meaning module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ValueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)
    importance: int = Field(default=5, ge=1, le=10)


class ValueUpdate(BaseModel):
    description: str | None = Field(None, max_length=500)
    importance: int | None = Field(None, ge=1, le=10)


class ValueResponse(BaseModel):
    id: int
    name: str
    description: str | None
    importance: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurposeUpdate(BaseModel):
    statement: str = Field(..., min_length=10, max_length=1000)


class PurposeResponse(BaseModel):
    id: int
    statement: str
    version: int
    is_current: bool
    updated_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeaningStats(BaseModel):
    values_count: int
    has_purpose: bool
    avg_importance: float
    score: int


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None