"""Recommend services: snapshot collection, run persistence, notifications."""

import json
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.finance import services as finance_svc
from app.modules.habits import services as habits_svc
from app.modules.habits.models import HabitCheckin
from app.modules.health import services as health_svc
from app.modules.daily_tracker import services as daily_svc
from app.modules.recommend.models import RecommendationRun, Notification
from app.modules.recommend.rules import evaluate_snapshot


def _last_checkin_date(db: Session, user_id: int, habit_id: int) -> str | None:
    stmt = (
        select(HabitCheckin.date)
        .where(HabitCheckin.user_id == user_id,
               HabitCheckin.habit_id == habit_id,
               HabitCheckin.completed == 1)
        .order_by(HabitCheckin.date.desc())
        .limit(1)
    )
    row = db.execute(stmt).scalars().first()
    return row


def collect_snapshot(db: Session, user_id: int,
                     today: str | None = None) -> dict[str, Any]:
    """Gather cross-module stats into the rule-engine input shape."""
    today = today or date.today().isoformat()
    month = today[:7]

    habits = []
    for h in habits_svc.list_habits(db, user_id):
        habits.append({**h, "last_checkin_date": _last_checkin_date(db, user_id, h["id"])})

    txs = finance_svc.list_transactions(db, user_id, month)
    spent: dict[str, float] = {}
    for t in txs:
        if t.type == "expense":
            spent[t.category] = spent.get(t.category, 0) + float(t.amount)
    fin_stats = finance_svc.get_stats(db, user_id, month)
    goals = []
    for g in finance_svc.list_goals(db, user_id):
        prog = (float(g.current_amount) / float(g.target_amount)
                if g.target_amount else 1.0)
        goals.append({"title": g.title, "progress": min(1.0, prog)})

    health_logs = health_svc.list_health_logs(db, user_id, 30)
    h_stats = health_svc.get_stats(db, user_id, 30)
    h_score = health_svc.calculate_health_score(db, user_id)

    today_logs = daily_svc.get_logs(db, user_id,
                                    target_date=date.fromisoformat(today))

    return {
        "today": today,
        "habits": habits,
        "finance": {
            "income": float(fin_stats.get("income", 0)),
            "expense": float(fin_stats.get("expense", 0)),
            "budgets": [{"category": b.category, "amount": float(b.amount)}
                        for b in finance_svc.list_budgets(db, user_id, month)],
            "spent_by_category": spent,
            "goals": goals,
        },
        "health": {
            "has_data": len(health_logs) > 0,
            "avg_steps": float(h_stats.get("avg_steps", 0) or 0),
            "avg_sleep_hours": float(h_stats.get("avg_sleep_hours", 0) or 0),
            "avg_exercise_minutes": float(h_stats.get("avg_exercise_minutes", 0) or 0),
            "score": h_score.get("score", 0),
            "level": h_score.get("level", ""),
        },
        "daily": {"has_today_log": len(today_logs) > 0},
    }


def compute_today(db: Session, user_id: int,
                  today: str | None = None) -> list[dict]:
    """Collect snapshot + run rules. Pure computation, no persistence."""
    return evaluate_snapshot(collect_snapshot(db, user_id, today))


def save_run(db: Session, user_id: int, items: list[dict],
             slot: str, today: str | None = None) -> RecommendationRun:
    """Persist a computed batch; high-priority items fan out to inbox.

    Idempotent per (user, date, slot, rule): re-runs don't duplicate
    same-rule notifications for the same day.
    """
    today = today or date.today().isoformat()
    run = RecommendationRun(user_id=user_id, date=today, slot=slot,
                            items_json=json.dumps(items, ensure_ascii=False))
    db.add(run)
    for it in items:
        if it.get("priority") != "high":
            continue
        exists = db.execute(
            select(Notification.id).where(
                Notification.user_id == user_id,
                Notification.date == today,
                Notification.rule == it.get("rule", ""))
        ).scalars().first()
        if exists:
            continue
        db.add(Notification(
            user_id=user_id, date=today, priority="high",
            title=it.get("title", ""), body=it.get("reason", ""),
            module=it.get("module", "general"), rule=it.get("rule", "")))
    db.commit()
    db.refresh(run)
    return run


def list_history(db: Session, user_id: int, days: int = 7) -> list[dict]:
    stmt = (
        select(RecommendationRun)
        .where(RecommendationRun.user_id == user_id)
        .order_by(RecommendationRun.date.desc(), RecommendationRun.id.desc())
        .limit(days)
    )
    runs = list(db.execute(stmt).scalars().all())
    return [{"date": r.date, "slot": r.slot,
             "items": json.loads(r.items_json or "[]")} for r in runs]


def list_notifications(db: Session, user_id: int,
                       unread_only: bool = False) -> list[Notification]:
    stmt = (select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id.desc()).limit(50))
    if unread_only:
        stmt = stmt.where(Notification.is_read == 0)
    return list(db.execute(stmt).scalars().all())


def mark_read(db: Session, user_id: int, notif_id: int) -> bool:
    n = db.execute(
        select(Notification).where(Notification.id == notif_id,
                                   Notification.user_id == user_id)
    ).scalars().first()
    if not n:
        return False
    n.is_read = 1
    db.commit()
    return True
