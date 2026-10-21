"""Social module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    relation: str | None = Field(None, max_length=30)
    closeness: int = Field(default=5, ge=1, le=10)
    note: str | None = Field(None, max_length=200)


class ContactResponse(BaseModel):
    id: int
    name: str
    relation: str | None
    closeness: int
    note: str | None
    days_since_last_contact: int | None = None
    needs_reconnect: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionCreate(BaseModel):
    contact_id: int = Field(...)
    date: str = Field(...)
    interaction_type: str = Field(..., pattern="^(call|message|meet|video|other)$")
    duration_minutes: int | None = Field(None, ge=0, le=1440)
    note: str | None = Field(None, max_length=200)


class InteractionResponse(BaseModel):
    id: int
    contact_id: int
    date: str
    interaction_type: str
    duration_minutes: int | None
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReconnectSuggestion(BaseModel):
    contact_id: int
    name: str
    closeness: int
    days_since_last: int


class SocialStats(BaseModel):
    contacts_count: int
    close_friends: int  # closeness >= 8
    interactions_30d: int
    reconnect_needed: list[ReconnectSuggestion]


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None