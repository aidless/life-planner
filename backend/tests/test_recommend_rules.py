"""P5 rule-engine tests — pure functions, no DB, no LLM.

Each rule: trigger case + boundary non-trigger case.
Numbers here are hand-computed fixtures, not copied from implementation.
"""

from app.modules.recommend.rules import evaluate_snapshot, THRESHOLDS


def base_snap(**kw):
    snap = {
        "today": "2026-09-07",
        "habits": [],
        "finance": {"income": 0, "expense": 0, "budgets": [],
                    "spent_by_category": {}, "goals": []},
        "health": {"has_data": False, "avg_steps": 0, "avg_sleep_hours": 0,
                   "avg_exercise_minutes": 0, "score": 0, "level": ""},
        "daily": {"has_today_log": True},
    }
    snap.update(kw)
    return snap


def rules_of(items):
    return [i["rule"] for i in items]


def test_empty_user_gets_onboarding_only():
    items = evaluate_snapshot(base_snap(daily={"has_today_log": False}))
    assert rules_of(items) == ["EMPTY"]


def test_h1_broken_streak_triggers():
    snap = base_snap(habits=[{
        "name": "跑步", "frequency": "daily", "is_active": 1,
        "streak": 0, "completion_rate_30d": 0.9,
        "target_count": 1, "last_checkin_date": "2026-09-04"}])
    items = evaluate_snapshot(snap)
    h1 = [i for i in items if i["rule"] == "H1"]
    assert len(h1) == 1
    assert h1[0]["priority"] == "high"
    assert "3 天" in h1[0]["title"]


def test_h1_gap_one_day_does_not_trigger():
    snap = base_snap(habits=[{
        "name": "跑步", "frequency": "daily", "is_active": 1,
        "streak": 5, "completion_rate_30d": 0.9,
        "target_count": 1, "last_checkin_date": "2026-09-06"}])
    # streak 5 < 7 so H3 must not fire either; only D1-free -> empty
    assert rules_of(evaluate_snapshot(snap)) == []


def test_h1_weekly_habit_ignored():
    snap = base_snap(habits=[{
        "name": "大扫除", "frequency": "weekly", "is_active": 1,
        "streak": 0, "completion_rate_30d": 0.9,
        "target_count": 1, "last_checkin_date": "2026-08-01"}])
    assert "H1" not in rules_of(evaluate_snapshot(snap))


def test_h2_low_completion_triggers():
    snap = base_snap(habits=[{
        "name": "背单词", "frequency": "daily", "is_active": 1,
        "streak": 1, "completion_rate_30d": 0.3,
        "target_count": 1, "last_checkin_date": "2026-09-07"}])
    items = evaluate_snapshot(snap)
    assert "H2" in rules_of(items)


def test_h3_long_streak_encouraged():
    snap = base_snap(habits=[{
        "name": "早起", "frequency": "daily", "is_active": 1,
        "streak": 10, "completion_rate_30d": 1.0,
        "target_count": 1, "last_checkin_date": "2026-09-07"}])
    items = evaluate_snapshot(snap)
    assert "H3" in rules_of(items)
    assert [i for i in items if i["rule"] == "H3"][0]["priority"] == "low"


def test_f1_over_budget_triggers():
    snap = base_snap(finance={
        "income": 10000, "expense": 2500,
        "budgets": [{"category": "餐饮", "amount": 2000}],
        "spent_by_category": {"餐饮": 2500}, "goals": []})
    items = evaluate_snapshot(snap)
    f1 = [i for i in items if i["rule"] == "F1"]
    assert len(f1) == 1 and f1[0]["priority"] == "high"


def test_f2_expense_without_budget_triggers():
    snap = base_snap(finance={
        "income": 5000, "expense": 1200, "budgets": [],
        "spent_by_category": {"交通": 1200}, "goals": []})
    assert "F2" in rules_of(evaluate_snapshot(snap))


def test_f3_stalled_goal_triggers():
    snap = base_snap(finance={
        "income": 8000, "expense": 3000,
        "budgets": [{"category": "餐饮", "amount": 5000}],
        "spent_by_category": {"餐饮": 3000},
        "goals": [{"title": "买车", "progress": 0.1}]})
    assert "F3" in rules_of(evaluate_snapshot(snap))


def test_he1_low_sleep_triggers_only_with_data():
    snap = base_snap(health={
        "has_data": True, "avg_steps": 8000, "avg_sleep_hours": 5.2,
        "avg_exercise_minutes": 30, "score": 60, "level": "良好"})
    assert "HE1" in rules_of(evaluate_snapshot(snap))
    # same numbers but no health data -> silent
    snap2 = base_snap(health={
        "has_data": False, "avg_steps": 8000, "avg_sleep_hours": 5.2,
        "avg_exercise_minutes": 30, "score": 0, "level": ""})
    assert "HE1" not in rules_of(evaluate_snapshot(snap2))


def test_he2_low_steps_triggers():
    snap = base_snap(health={
        "has_data": True, "avg_steps": 1500, "avg_sleep_hours": 7.5,
        "avg_exercise_minutes": 30, "score": 55, "level": "一般"})
    assert "HE2" in rules_of(evaluate_snapshot(snap))


def test_d1_no_log_today_triggers():
    snap = base_snap(
        finance={"income": 8000, "expense": 0, "budgets": [],
                 "spent_by_category": {}, "goals": []},
        daily={"has_today_log": False})
    assert "D1" in rules_of(evaluate_snapshot(snap))


def test_priority_sort_high_first():
    snap = base_snap(
        habits=[{"name": "跑步", "frequency": "daily", "is_active": 1,
                 "streak": 0, "completion_rate_30d": 0.9,
                 "target_count": 1, "last_checkin_date": "2026-09-01"}],
        daily={"has_today_log": False})
    items = evaluate_snapshot(snap)
    pris = [i["priority"] for i in items]
    assert pris == sorted(pris, key={"high": 0, "medium": 1, "low": 2}.get)
    assert items[0]["rule"] == "H1"


def test_thresholds_single_source():
    assert THRESHOLDS["habit_break_days"] == 2
    assert THRESHOLDS["sleep_low"] == 6.0
