"""Decision-recommendation rule engine (pure functions, no DB, no LLM).

Snapshot shape (built by services.collect_snapshot):
{
  "today": "YYYY-MM-DD",
  "habits": [{"name","frequency","is_active","streak",
              "completion_rate_30d","last_checkin_date"|None}],
  "finance": {"income","expense",
              "budgets":[{"category","amount"}],
              "spent_by_category":{cat: amount},
              "goals":[{"title","progress"}]},
  "health": {"has_data": bool, "avg_steps","avg_sleep_hours",
             "avg_exercise_minutes","score","level"},
  "daily": {"has_today_log": bool},
}

Every rule is deterministic in (snapshot) — same input, same output.
Thresholds live in THRESHOLDS so tests and docs reference one source.
"""

from datetime import date

THRESHOLDS = {
    "habit_break_days": 2,      # H1: daily habit gap >= 2 days
    "habit_low_rate": 0.5,      # H2: 30d completion < 50%
    "habit_keep_streak": 7,     # H3: streak >= 7 -> encourage
    "goal_stalled": 0.2,        # F3: savings goal progress < 20%
    "sleep_low": 6.0,           # HE1: avg sleep < 6h
    "steps_low": 3000.0,        # HE2: avg steps < 3000
}

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _gap_days(today: str, last: str | None) -> int | None:
    if not last:
        return None
    try:
        return (date.fromisoformat(today) - date.fromisoformat(last)).days
    except ValueError:
        return None


def evaluate_snapshot(snap: dict) -> list[dict]:
    """Run all rules over a snapshot. Returns priority-sorted recommendations."""
    today = snap.get("today", "")
    out: list[dict] = []

    def rec(rule: str, module: str, priority: str, title: str,
            reason: str, action_link: str) -> dict:
        return {
            "rule": rule, "module": module, "priority": priority,
            "title": title, "reason": reason, "action_link": action_link,
            "computed_at": today,
        }

    habits = [h for h in snap.get("habits", []) if h.get("is_active")]
    fin = snap.get("finance", {}) or {}
    health = snap.get("health", {}) or {}
    daily = snap.get("daily", {}) or {}

    has_any_data = bool(habits) or (fin.get("expense", 0) > 0) \
        or (fin.get("income", 0) > 0) or bool(health.get("has_data"))

    # EMPTY: brand-new user -> single onboarding recommendation
    if not has_any_data:
        out.append(rec(
            "EMPTY", "general", "low",
            "从一条记录开始",
            "你还没有任何数据。先记一笔今日动态，推荐引擎明天就有依据可算。",
            "/daily",
        ))
        return out

    # H1: broken daily streak
    for h in habits:
        if h.get("frequency") != "daily":
            continue
        gap = _gap_days(today, h.get("last_checkin_date"))
        if gap is not None and gap >= THRESHOLDS["habit_break_days"]:
            out.append(rec(
                "H1", "habits", "high",
                f"「{h['name']}」已断连 {gap} 天",
                f"上次打卡 {h['last_checkin_date']}，当前连击 {h.get('streak', 0)} 天。"
                "断连越久重启成本越高，今天补一次就能续上。",
                "/habits",
            ))

    # H2: low 30d completion rate
    for h in habits:
        rate = h.get("completion_rate_30d", 1.0) or 0.0
        if rate < THRESHOLDS["habit_low_rate"]:
            out.append(rec(
                "H2", "habits", "medium",
                f"「{h['name']}」近 30 天完成率 {rate:.0%}",
                f"完成率 {rate:.0%} 低于 "
                f"{THRESHOLDS['habit_low_rate']:.0%}。考虑把目标次数从"
                f"每天 {h.get('target_count', 1)} 次调低，或换个提醒时间。",
                "/habits",
            ))

    # H3: keep a good streak going
    for h in habits:
        if h.get("streak", 0) >= THRESHOLDS["habit_keep_streak"]:
            out.append(rec(
                "H3", "habits", "low",
                f"「{h['name']}」已坚持 {h['streak']} 天",
                f"连击 {h['streak']} 天，超过 "
                f"{THRESHOLDS['habit_keep_streak']} 天鼓励线。保持节奏，别断。",
                "/habits",
            ))

    # F1: over budget by category
    budgets = {b["category"]: b["amount"] for b in fin.get("budgets", [])}
    spent = fin.get("spent_by_category", {}) or {}
    for cat, amount in budgets.items():
        s = spent.get(cat, 0)
        if s > amount:
            out.append(rec(
                "F1", "finance", "high",
                f"「{cat}」本月已超预算 ¥{s:.0f} / ¥{amount:.0f}",
                f"实际支出 ¥{s:.2f}，预算 ¥{amount:.2f}，超支 "
                f"¥{s - amount:.2f}。建议未来 7 天该类目暂停非必要支出。",
                "/finance",
            ))

    # F2: spending but no budget set
    if fin.get("expense", 0) > 0 and not budgets:
        out.append(rec(
            "F2", "finance", "medium",
            f"本月已支出 ¥{fin['expense']:.0f}，但没设预算",
            f"无预算 = 无约束。按上月最大支出类目先设一个本月预算，"
            f"花超自动预警。",
            "/finance",
        ))

    # F3: stalled savings goal
    for g in fin.get("goals", []):
        p = g.get("progress", 1.0)
        if p is not None and p < THRESHOLDS["goal_stalled"]:
            out.append(rec(
                "F3", "finance", "medium",
                f"储蓄目标「{g['title']}」进度 {p:.0%}",
                f"进度 {p:.0%} 低于 "
                f"{THRESHOLDS['goal_stalled']:.0%}。建议设每月自动转入额，"
                "先小后大。",
                "/finance",
            ))

    # HE1/HE2: sleep / steps (only when health data exists)
    if health.get("has_data"):
        sleep = health.get("avg_sleep_hours") or 0
        if sleep < THRESHOLDS["sleep_low"]:
            out.append(rec(
                "HE1", "health", "high",
                f"近 30 天平均睡眠 {sleep:.1f} 小时",
                f"平均睡眠 {sleep:.1f}h 低于 "
                f"{THRESHOLDS['sleep_low']:.0f}h 线。今晚提前 30 分钟上床，"
                "连续 3 天就能看到评分回升。",
                "/health",
            ))
        steps = health.get("avg_steps") or 0
        if steps < THRESHOLDS["steps_low"]:
            out.append(rec(
                "HE2", "health", "medium",
                f"近 30 天平均步数 {steps:.0f}",
                f"平均步数 {steps:.0f} 低于 "
                f"{THRESHOLDS['steps_low']:.0f} 线。每天加 15 分钟步行即可达标。",
                "/health",
            ))

    # D1: no log today
    if not daily.get("has_today_log"):
        out.append(rec(
            "D1", "general", "low",
            "今日还没有记录",
            "今日动态为空。花 1 分钟记一条，推荐引擎靠它了解你。",
            "/daily",
        ))

    out.sort(key=lambda r: (PRIORITY_ORDER[r["priority"]], r["rule"]))
    return out
