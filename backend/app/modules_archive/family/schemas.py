"""Family module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    relation: str = Field(..., min_length=1, max_length=30)
    birthday: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    note: str | None = Field(None, max_length=200)


class MemberResponse(BaseModel):
    id: int
    name: str
    relation: str
    birthday: str | None
    note: str | None
    days_to_birthday: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionCreate(BaseModel):
    member_id: int = Field(...)
    date: str = Field(...)
    interaction_type: str = Field(..., pattern="^(call|visit|message|gift|other)$")
    duration_minutes: int | None = Field(None, ge=0, le=1440)
    note: str | None = Field(None, max_length=200)


class InteractionResponse(BaseModel):
    id: int
    member_id: int
    date: str
    interaction_type: str
    duration_minutes: int | None
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpcomingBirthday(BaseModel):
    member_id: int
    name: str
    relation: str
    birthday: str
    days_until: int


class FamilyStats(BaseModel):
    members_count: int
    interactions_30d: int
    upcoming_birthdays: list[UpcomingBirthday]


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None