"""Finance module API router."""

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.finance import schemas, services
from app.modules.finance.schemas import ApiResponse

router = APIRouter(prefix="/api/finance", tags=["finance"])


@router.post("/transactions", response_model=ApiResponse)
def create_transaction(
    payload: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = services.create_transaction(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data=schemas.TransactionResponse.model_validate(tx).model_dump(),
    )


@router.get("/transactions", response_model=ApiResponse)
def list_transactions(
    month: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txs = services.list_transactions(db, int(current_user.id), month)
    return ApiResponse(
        success=True,
        data=[schemas.TransactionResponse.model_validate(t).model_dump() for t in txs],
    )


@router.post("/budgets", response_model=ApiResponse)
def create_budget(
    payload: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = services.create_budget(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data=schemas.BudgetResponse.model_validate(b).model_dump(),
    )


@router.get("/budgets", response_model=ApiResponse)
def list_budgets(
    month: str = Query(default_factory=lambda: datetime.now().strftime("%Y-%m"), pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bs = services.list_budgets(db, int(current_user.id), month)
    return ApiResponse(
        success=True,
        data=[schemas.BudgetResponse.model_validate(b).model_dump() for b in bs],
    )


@router.post("/goals", response_model=ApiResponse)
def create_goal(
    payload: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    g = services.create_goal(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data={**schemas.GoalResponse.model_validate(g).model_dump(),
              "progress": round(g.current_amount / g.target_amount, 2)
                        if g.target_amount and g.current_amount is not None else 0},
    )


@router.get("/goals", response_model=ApiResponse)
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    gs = services.list_goals(db, int(current_user.id))
    items = []
    for g in gs:
        d = schemas.GoalResponse.model_validate(g).model_dump()
        if g.target_amount and g.current_amount is not None:
            try:
                d["progress"] = round(g.current_amount / g.target_amount, 2)
            except (ZeroDivisionError, TypeError):
                d["progress"] = 0
        else:
            d["progress"] = 0
        items.append(d)
    return ApiResponse(success=True, data=items)


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    month: str = Query(default_factory=lambda: datetime.now().strftime("%Y-%m"), pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = services.get_stats(db, int(current_user.id), month)
    return ApiResponse(success=True, data=stats)