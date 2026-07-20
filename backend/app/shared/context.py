"""
Shared user context builder for AI prompts (added 2026-07-19 fix C).

Helper functions that aggregate user data from multiple modules
so AI Coach has actual personalized context (not empty prompt).

This addresses W38-Reflections gap B: AI 能力浅 — coach chat 用空 prompt。
"""

from __future__ import annotations
import json
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.modules.daily_tracker.models import DailyLog


def get_recent_daily_logs(db: Session, user_id: int, days: int = 7, limit: int = 10) -> list:
    """Fetch user's last `days` daily_logs (most recent first)."""
    from sqlalchemy import text
    # Use raw SQL to avoid ORM mapper issues between User/LifeGoal
    cutoff = (datetime.now() - timedelta(days=days)).date().isoformat()
    rows = db.execute(
        text(
            "SELECT date, mood_level, energy_level, notes "
            "FROM daily_logs "
            "WHERE user_id = :uid AND date >= :cutoff "
            "ORDER BY date DESC LIMIT :limit"
        ),
        {"uid": int(user_id), "cutoff": cutoff, "limit": int(limit)},
    ).fetchall()
    return [
        {
            "date": r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date),
            "mood_level": r.mood_level,
            "energy_level": r.energy_level,
            "notes": r.notes,
        }
        for r in rows
    ]


def build_user_summary(db: Session, user_id: int, days: int = 7) -> str:
    """Build a compact text summary of user's recent activity for prompt injection.

    Returns "" if no data available.
    """
    try:
        logs = get_recent_daily_logs(db, user_id, days=days)
    except Exception as e:
        import logging
        logging.warning(f"Failed to fetch daily logs: {e}")
        return ""

    if not logs:
        return ""

    lines = [
        f"用户最近 {len(logs)} 天生活记录摘要 (近 {days} 天内):",
    ]
    mood_levels = []
    energy_levels = []
    for log in logs:
        date = log.get("date", "?")
        mood = log.get("mood_level")
        energy = log.get("energy_level")
        notes = log.get("notes") or ""
        bits = [f"- {date}"]
        if mood is not None:
            bits.append(f"心情 {mood}/10")
            mood_levels.append(mood)
        if energy is not None:
            bits.append(f"精力 {energy}/10")
            energy_levels.append(energy)
        if notes:
            bits.append(f"备注: {notes[:80]}")
        lines.append(" ".join(bits))
    if mood_levels:
        lines.append(f"\n平均心情 {sum(mood_levels) / len(mood_levels):.1f}/10")
    if energy_levels:
        lines.append(f"平均精力 {sum(energy_levels) / len(energy_levels):.1f}/10")
    return "\n".join(lines)


def inject_user_context(system_prompt: str, user_summary: str) -> str:
    """Concatenate user summary into system prompt (if any)."""
    if not user_summary:
        return system_prompt
    return f"{system_prompt}\n\n[用户最近记录]\n{user_summary}"
