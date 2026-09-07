"""Recommend module schemas."""

from pydantic import BaseModel, Field, ConfigDict


class Recommendation(BaseModel):
    rule: str
    module: str
    priority: str = Field(pattern="^(high|medium|low)$")
    title: str
    reason: str
    action_link: str
    computed_at: str


class NotificationResponse(BaseModel):
    id: int
    date: str
    priority: str
    title: str
    body: str
    module: str
    is_read: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None
