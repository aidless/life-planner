"""Dashboard module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DimensionScore(BaseModel):
    """Single dimension health score."""

    key: str
    name: str
    score: int
    level: str  # 优秀 / 良好 / 一般 / 待提升
    components: dict | None = None
    updated_at: datetime | None = None


class NextMilestone(BaseModel):
    title: str
    days_until: int
    category: str
    due_date: str | None = None


class AIRecommendation(BaseModel):
    priority: str  # high / medium / low
    dimension: str
    action: str
    reason: str


class DashboardResponse(BaseModel):
    user_id: int
    average_score: int
    average_level: str
    dimensions: list[DimensionScore]
    next_milestones: list[NextMilestone]
    ai_recommendations: list[AIRecommendation]
    active_modules_count: int  # active subdomains with data
    total_modules: int


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None