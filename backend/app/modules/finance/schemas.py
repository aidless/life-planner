"""Finance module schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TransactionCreate(BaseModel):
    date: str = Field(...)
    type: str = Field(..., pattern="^(income|expense)$")
    category: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0)
    note: str | None = Field(None, max_length=200)


class TransactionResponse(BaseModel):
    id: int
    date: str
    type: str
    category: str
    amount: float
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetCreate(BaseModel):
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    category: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0)


class BudgetResponse(BaseModel):
    id: int
    month: str
    category: str
    amount: float

    model_config = ConfigDict(from_attributes=True)


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    target_amount: float = Field(..., gt=0)
    deadline: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    note: str | None = Field(None, max_length=500)


class GoalResponse(BaseModel):
    id: int
    title: str
    target_amount: float
    current_amount: float
    deadline: str | None
    note: str | None
    progress: float | None = None  # computed in router (not stored on model)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FinanceStats(BaseModel):
    month: str
    income: float
    expense: float
    savings: float
    budget_compliance: float  # 0-1
    savings_progress: float  # 0-1


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None
    meta: dict | None = None