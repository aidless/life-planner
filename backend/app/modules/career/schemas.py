"""Career module schemas (added 2026-07-19 fix B-α)."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class JobApplicationCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    role_title: str = Field(..., min_length=1, max_length=200)
    industry: str | None = Field(None, max_length=80)
    location: str | None = Field(None, max_length=80)
    job_description: str | None = None
    job_url: str | None = Field(None, max_length=500)
    notes: str | None = None
    salary_offered_annual: int | None = Field(None, ge=0, le=10000)
    base_offered_annual: int | None = Field(None, ge=0, le=10000)


class JobApplicationUpdate(BaseModel):
    status: str | None = Field(
        None,
        pattern="^(applied|screening|interview_oa|interview_1|interview_2|offer|rejected|withdrawn)$",
    )
    interview_date: datetime | None = None
    response_deadline: datetime | None = None
    decision_date: datetime | None = None
    notes: str | None = None
    contacts: str | None = None
    salary_offered_annual: int | None = Field(None, ge=0, le=10000)
    base_offered_annual: int | None = Field(None, ge=0, le=10000)


class JobApplicationResponse(BaseModel):
    id: int
    company_name: str
    role_title: str
    industry: str | None
    location: str | None
    status: str
    applied_date: datetime
    interview_date: datetime | None
    response_deadline: datetime | None
    decision_date: datetime | None
    salary_offered_annual: int | None
    base_offered_annual: int | None
    job_description: str | None
    job_url: str | None
    contacts: str | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerStats(BaseModel):
    total_applications: int
    active: int
    rejected: int
    offers: int
    interview_rate: float  # ratio of applications with at least one interview
    offer_rate: float      # ratio of offers / total


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None
