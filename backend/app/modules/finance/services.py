"""Finance module services."""

from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.finance.models import Transaction, Budget, FinancialGoal
from app.modules.finance.schemas import (
    TransactionCreate,
    BudgetCreate,
    GoalCreate,
)


def create_transaction(db: Session, user_id: int, data: TransactionCreate) -> Transaction:
    tx = Transaction(
        user_id=user_id,
        date=data.date,
        type=data.type,
        category=data.category,
        amount=data.amount,
        note=data.note,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def list_transactions(db: Session, user_id: int, month: str | None = None) -> List[Transaction]:
    stmt = select(Transaction).where(Transaction.user_id == user_id)
    if month:
        stmt = stmt.where(Transaction.date.like(f"{month}%"))
    stmt = stmt.order_by(Transaction.date.desc())
    return list(db.execute(stmt).scalars().all())


def create_budget(db: Session, user_id: int, data: BudgetCreate) -> Budget:
    b = Budget(
        user_id=user_id,
        month=data.month,
        category=data.category,
        amount=data.amount,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def list_budgets(db: Session, user_id: int, month: str) -> List[Budget]:
    stmt = select(Budget).where(Budget.user_id == user_id, Budget.month == month)
    return list(db.execute(stmt).scalars().all())


def create_goal(db: Session, user_id: int, data: GoalCreate) -> FinancialGoal:
    g = FinancialGoal(
        user_id=user_id,
        title=data.title,
        target_amount=data.target_amount,
        deadline=data.deadline,
        note=data.note,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def list_goals(db: Session, user_id: int) -> List[FinancialGoal]:
    stmt = (
        select(FinancialGoal)
        .where(FinancialGoal.user_id == user_id)
        .order_by(FinancialGoal.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_stats(db: Session, user_id: int, month: str) -> Dict[str, Any]:
    """Finance score = budget_compliance * 50 + savings_progress * 50."""
    txs = list_transactions(db, user_id, month)
    budgets = list_budgets(db, user_id, month)

    income = sum(t.amount for t in txs if t.type == "income")
    expense = sum(t.amount for t in txs if t.type == "expense")

    # Budget compliance: actual / budget per category
    if budgets:
        budget_total = sum(b.amount for b in budgets)
        actual_total = expense
        compliance = min(1.0, budget_total / max(actual_total, 1)) if actual_total > 0 else 1.0
    else:
        compliance = 1.0  # no budget = perfect compliance

    # Savings progress (avg of all goals)
    goals = list_goals(db, user_id)
    if goals:
        ratios = [float(g.current_amount) / float(g.target_amount) for g in goals]
        clamped = [min(1.0, r) for r in ratios]
        progress = sum(clamped) / len(clamped)
    else:
        progress = 0.0

    return {
        "month": month,
        "income": round(income, 2),
        "expense": round(expense, 2),
        "savings": round(income - expense, 2),
        "budget_compliance": round(compliance, 2),
        "savings_progress": round(progress, 2),
    }