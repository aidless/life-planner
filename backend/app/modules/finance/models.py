"""Finance module models."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Date
from app.shared.base_model import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    """Income or expense record."""

    __tablename__ = "finance_transactions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    type = Column(String(10), nullable=False)  # income/expense
    category = Column(String(50), nullable=False)  # 餐饮/交通/工资/...
    amount = Column(Float, nullable=False)
    note = Column(String(200), nullable=True)


class Budget(Base, TimestampMixin):
    """Monthly budget by category."""

    __tablename__ = "finance_budgets"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    month = Column(String(7), nullable=False, index=True)  # YYYY-MM
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)


class FinancialGoal(Base, TimestampMixin):
    """Savings goal."""

    __tablename__ = "finance_goals"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(String(10), nullable=True)  # YYYY-MM-DD
    note = Column(String(500), nullable=True)