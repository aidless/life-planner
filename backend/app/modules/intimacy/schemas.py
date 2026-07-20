"""Intimacy module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RelationshipCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    relation_type: str = Field(..., min_length=1, max_length=30)
    anniversary: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    note: str | None = Field(None, max_length=500)


class RelationshipResponse(BaseModel):
    id: int
    name: str
    relation_type: str
    anniversary: str | None
    status: str
    note: str | None
    days_to_anniversary: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnniversaryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    recurring: bool = Field(default=True)
    note: str | None = Field(None, max_length=200)


class AnniversaryResponse(BaseModel):
    id: int
    title: str
    date: str
    recurring: bool
    note: str | None
    days_until: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntimacyStats(BaseModel):
    active_relationships: int
    anniversaries_count: int
    upcoming_anniversaries: list  # 列表含 days_until
    score: int  # 0-100


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None