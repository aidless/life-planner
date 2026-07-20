"""Travel module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TripCreate(BaseModel):
    destination: str = Field(..., min_length=1, max_length=100)
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    cost_cny: float | None = Field(None, ge=0)
    rating: int | None = Field(None, ge=1, le=5)
    note: str | None = Field(None, max_length=1000)
    photo_count: int | None = Field(None, ge=0)


class TripResponse(BaseModel):
    id: int
    destination: str
    start_date: str
    end_date: str | None
    cost_cny: float | None
    rating: int | None
    note: str | None
    photo_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BucketCreate(BaseModel):
    destination: str = Field(..., min_length=1, max_length=100)
    priority: int = Field(default=1, ge=1, le=3)
    note: str | None = Field(None, max_length=500)


class BucketResponse(BaseModel):
    id: int
    destination: str
    priority: int
    note: str | None
    completed: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TravelStats(BaseModel):
    trips_total: int
    trips_this_year: int
    countries_visited: int  # 简单估算：destination 数量
    bucket_list_size: int
    score: int


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None