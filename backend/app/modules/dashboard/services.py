"""Dashboard module services — 12 维度健康度聚合."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.orm import Session

# Subdomain services
from app.modules.health.services import calculate_health_score
from app.modules.finance.services import get_stats as finance_stats
from app.modules.habits.services import list_habits
from app.modules.psychology.services import get_stats as psychology_stats
from app.modules.family.services import list_members, get_upcoming_birthdays
from app.modules.interest.services import list_interests, get_stats as interest_stats
from app.modules.social.services import list_contacts, get_reconnect_suggestions
from app.modules.learning.services import list_books, list_courses
from app.modules.travel.services import list_trips, list_bucket
from app.modules.intimacy.services import list_relationships, list_anniversaries
from app.modules.meaning.services import list_values, get_current_purpose

from app.modules.dashboard.schemas import (
    DashboardResponse,
    DimensionScore,
    NextMilestone,
    AIRecommendation,
)


def _level_for(score: int) -> str:
    if score >= 80:
        return "优秀"
    if score >= 60:
        return "良好"
    if score >= 40:
        return "一般"
    return "待提升"


def build_dashboard(user_id: int, db: Session) -> DashboardResponse:
    """Aggregate 12 dimension health from all subdomains."""
    dimensions: List[DimensionScore] = []

    # 1. 健康 (P0)
    try:
        health_data = calculate_health_score(db, user_id)
        dimensions.append(DimensionScore(
            key="health",
            name="健康",
            score=health_data["score"],
            level=health_data["level"],
            components=health_data.get("components"),
        ))
    except Exception:
        dimensions.append(DimensionScore(key="health", name="健康", score=0, level="待提升"))

    # 2. 财务 (P0)
    try:
        month = datetime.now().strftime("%Y-%m")
        fin = finance_stats(db, user_id, month)
        fin_score = int(fin["budget_compliance"] * 50 + fin["savings_progress"] * 50)
        dimensions.append(DimensionScore(
            key="finance",
            name="财务",
            score=fin_score,
            level=_level_for(fin_score),
            components={"budget_compliance": fin["budget_compliance"], "savings_progress": fin["savings_progress"]},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="finance", name="财务", score=0, level="待提升"))

    # 3. 习惯 (P0)
    try:
        habits = list_habits(db, user_id)
        if habits:
            avg_completion = sum(h.get("completion_rate_30d", 0) for h in habits) / len(habits)
            habit_score = int(avg_completion * 100)
            dimensions.append(DimensionScore(
                key="habits",
                name="习惯",
                score=habit_score,
                level=_level_for(habit_score),
                components={"habit_count": len(habits), "avg_completion": round(avg_completion, 2)},
            ))
        else:
            dimensions.append(DimensionScore(key="habits", name="习惯", score=0, level="待提升"))
    except Exception:
        dimensions.append(DimensionScore(key="habits", name="习惯", score=0, level="待提升"))

    # 4. 心理 (P1)
    try:
        psy = psychology_stats(db, user_id, days=30)
        dimensions.append(DimensionScore(
            key="psychology",
            name="心理",
            score=psy["score"],
            level=_level_for(psy["score"]),
            components={"avg_mood": psy["avg_mood"], "avg_energy": psy["avg_energy"]},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="psychology", name="心理", score=0, level="待提升"))

    # 5. 家庭 (P1)
    try:
        members = list_members(db, user_id)
        upcoming_birthdays = get_upcoming_birthdays(db, user_id, within_days=30)
        family_score = min(100, len(members) * 15 + len(upcoming_birthdays) * 10)
        dimensions.append(DimensionScore(
            key="family",
            name="家庭",
            score=family_score,
            level=_level_for(family_score),
            components={"members": len(members), "upcoming_birthdays": len(upcoming_birthdays)},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="family", name="家庭", score=0, level="待提升"))

    # 6. 兴趣 (P1)
    try:
        interests = list_interests(db, user_id)
        interest_data = interest_stats(db, user_id)
        dimensions.append(DimensionScore(
            key="interest",
            name="兴趣",
            score=interest_data["score"],
            level=_level_for(interest_data["score"]),
            components={"total_interests": len(interests), "weekly_hours": interest_data["weekly_hours"]},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="interest", name="兴趣", score=0, level="待提升"))

    # 7. 社交 (P1)
    try:
        contacts = list_contacts(db, user_id)
        reconnect = get_reconnect_suggestions(db, user_id)
        social_score = min(100, len(contacts) * 5 + len(reconnect) * 8)
        dimensions.append(DimensionScore(
            key="social",
            name="社交",
            score=social_score,
            level=_level_for(social_score),
            components={"contacts": len(contacts), "reconnect_needed": len(reconnect)},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="social", name="社交", score=0, level="待提升"))

    # 8. 学习 (P2)
    try:
        books = list_books(db, user_id)
        courses = list_courses(db, user_id)
        learning_score = min(100, sum(1 for b in books if b.status == "finished") * 4 + sum(1 for c in courses if c.status == "finished") * 12)
        dimensions.append(DimensionScore(
            key="learning",
            name="学习",
            score=learning_score,
            level=_level_for(learning_score),
            components={"books_total": len(books), "courses_total": len(courses)},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="learning", name="学习", score=0, level="待提升"))

    # 9. 旅行 (P2)
    try:
        trips = list_trips(db, user_id)
        bucket = list_bucket(db, user_id)
        year = datetime.now().year
        trips_this_year = sum(1 for t in trips if t.start_date.startswith(str(year)))
        travel_score = min(100, trips_this_year * 25)
        dimensions.append(DimensionScore(
            key="travel",
            name="旅行",
            score=travel_score,
            level=_level_for(travel_score),
            components={"trips_total": len(trips), "this_year": trips_this_year, "bucket": len(bucket)},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="travel", name="旅行", score=0, level="待提升"))

    # 10. 亲密 (P2)
    try:
        rels = list_relationships(db, user_id, active_only=True)
        annivs = list_anniversaries(db, user_id)
        intimacy_score = (50 if rels else 0) + min(50, len(annivs) * 10)
        dimensions.append(DimensionScore(
            key="intimacy",
            name="亲密",
            score=intimacy_score,
            level=_level_for(intimacy_score),
            components={"relationships": len(rels), "anniversaries": len(annivs)},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="intimacy", name="亲密", score=0, level="待提升"))

    # 11. 意义 (P2)
    try:
        values = list_values(db, user_id)
        purpose = get_current_purpose(db, user_id)
        meaning_score = min(100, len(values) * 15 + (25 if purpose else 0))
        dimensions.append(DimensionScore(
            key="meaning",
            name="意义",
            score=meaning_score,
            level=_level_for(meaning_score),
            components={"values_count": len(values), "has_purpose": purpose is not None},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="meaning", name="意义", score=0, level="待提升"))

    # 12. 学业/职业 (P0 - aggregating from existing modules)
    # Uses life_planner goals count + daily_logs count
    try:
        from app.modules.life_planner.models import LifeGoal
        from app.modules.daily_tracker.models import DailyLog
        from sqlalchemy import select, func
        goals_count = db.execute(
            select(func.count(LifeGoal.id)).where(LifeGoal.user_id == user_id)
        ).scalar() or 0
        logs_count = db.execute(
            select(func.count(DailyLog.id)).where(DailyLog.user_id == user_id)
        ).scalar() or 0
        career_score = min(100, logs_count * 2 + goals_count * 6)
        dimensions.append(DimensionScore(
            key="career",
            name="学业/职业",
            score=career_score,
            level=_level_for(career_score),
            components={"daily_logs": logs_count, "goals": goals_count},
        ))
    except Exception:
        dimensions.append(DimensionScore(key="career", name="学业/职业", score=0, level="待提升"))

    # 整体平均
    if dimensions:
        avg_score = int(sum(d.score for d in dimensions) / len(dimensions))
        avg_level = _level_for(avg_score)
    else:
        avg_score = 0
        avg_level = "待提升"

    # 即将到来的里程碑
    milestones: List[NextMilestone] = []
    today = datetime.now().date()

    try:
        for b in get_upcoming_birthdays(db, user_id, within_days=30):
            milestones.append(NextMilestone(
                title=f"{b['name']} ({b['relation']}) 生日",
                days_until=b["days_until"],
                category="family",
                due_date=b["birthday"],
            ))
    except Exception:
        pass

    try:
        for a in list_anniversaries(db, user_id):
            if a.get("days_until") is not None and a["days_until"] <= 30:
                milestones.append(NextMilestone(
                    title=a["title"],
                    days_until=a["days_until"],
                    category="intimacy",
                    due_date=a["date"],
                ))
                if len(milestones) >= 10:
                    break
    except Exception:
        pass

    milestones.sort(key=lambda m: m.days_until)

    # AI 推荐（基于最低 2 个维度）
    sorted_dims = sorted(dimensions, key=lambda d: d.score)
    recommendations: List[AIRecommendation] = []
    for d in sorted_dims[:3]:
        if d.score < 60:
            priority = "high" if d.score < 40 else "medium"
            action = _suggest_action(d.key)
            reason = f"{d.name} 维度得分 {d.score}，建议优先提升"
            recommendations.append(AIRecommendation(
                priority=priority,
                dimension=d.name,
                action=action,
                reason=reason,
            ))

    return DashboardResponse(
        user_id=user_id,
        average_score=avg_score,
        average_level=avg_level,
        dimensions=dimensions,
        next_milestones=milestones,
        ai_recommendations=recommendations,
        active_modules_count=sum(1 for d in dimensions if d.score > 0),
        total_modules=len(dimensions),
    )


def _suggest_action(key: str) -> str:
    suggestions = {
        "health": "每天 8000 步 + 7 小时睡眠 + 30 分钟运动",
        "finance": "设置月度预算 + 1 个储蓄目标",
        "habits": "创建 1 个每日习惯（晨跑/阅读/冥想任选）",
        "psychology": "每天花 5 分钟记录心情 + 反思 1 件感恩的事",
        "family": "查看家人生日 → 安排联系",
        "interest": "列出 3 个爱好 → 每周各投入 1 小时",
        "social": "30 天未联系的朋友 → 发送 1 条消息",
        "learning": "本月读 1 本书 或 完成 1 门课程",
        "travel": "从心愿单选 1 个目的地 → 计划行程",
        "intimacy": "记录伴侣/家人纪念日 → 提前准备礼物",
        "meaning": "列出 5 个核心价值观 + 写 1 句人生使命",
        "career": "创建 1 个短期学习目标 + 1 个长期职业目标",
    }
    return suggestions.get(key, f"提升 {key} 维度")