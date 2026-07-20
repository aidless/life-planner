"""init_user_data — 注册新用户时自动注入 30 天示例数据.

Run from anywhere:
    python scripts/init_user_data.py --user-id 123

Or programmatically from auth.register:
    from scripts.init_user_data import init_sample_data
    init_sample_data(db, user_id)
"""

import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Make backend importable
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.modules.auth.models import User

from app.modules.health.models import HealthLog, ExerciseRecord
from app.modules.finance.models import Transaction, Budget, FinancialGoal
from app.modules.habits.models import Habit, HabitCheckin
from app.modules.psychology.models import MoodLog, Reflection
from app.modules.family.models import FamilyMember
from app.modules.interest.models import Interest, InterestActivity
from app.modules.social.models import Contact
from app.modules.learning.models import Book, Course
from app.modules.travel.models import Trip, BucketList
from app.modules.intimacy.models import Relationship, Anniversary
from app.modules.meaning.models import Value, LifePurpose


def init_health(db: Session, user_id: int):
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        steps = random.randint(5000, 12000)
        db.add(HealthLog(
            user_id=user_id,
            date=date,
            weight_kg=70 + random.uniform(-0.5, 0.5),
            sleep_hours=random.uniform(6.5, 8.5),
            exercise_minutes=random.randint(20, 60),
            steps=steps,
            water_ml=random.randint(1500, 3000),
            mood_score=random.randint(6, 10),
        ))
    # 5 exercises
    exercise_types = ["running", "yoga", "swimming", "cycling", "weight"]
    for i, et in enumerate(exercise_types):
        db.add(ExerciseRecord(
            user_id=user_id,
            date=(datetime.now() - timedelta(days=i * 5)).strftime("%Y-%m-%d"),
            exercise_type=et,
            duration_minutes=random.randint(20, 60),
            intensity="moderate",
            calories_burned=random.randint(200, 500),
        ))


def init_finance(db: Session, user_id: int):
    now = datetime.now()
    month = now.strftime("%Y-%m")
    # Transactions (20 笔)
    categories_expense = ["餐饮", "交通", "购物", "娱乐", "学习"]
    categories_income = ["工资", "红包", "投资"]
    for i in range(20):
        date = (now - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        is_expense = random.random() < 0.85
        db.add(Transaction(
            user_id=user_id,
            date=date,
            type="expense" if is_expense else "income",
            category=random.choice(categories_expense if is_expense else categories_income),
            amount=random.uniform(20, 500) if is_expense else random.uniform(1000, 5000),
            note=None,
        ))
    # Budgets
    for cat in categories_expense:
        db.add(Budget(
            user_id=user_id,
            month=month,
            category=cat,
            amount=1500,
        ))
    # Goals
    db.add(FinancialGoal(
        user_id=user_id,
        title="存款 10 万",
        target_amount=100000,
        current_amount=random.randint(20000, 50000),
        deadline="2027-12-31",
    ))


def init_habits(db: Session, user_id: int):
    habits_def = [
        ("晨跑", "健康", 30),
        ("阅读 30 分钟", "学习", 30),
        ("冥想", "心理", 15),
    ]
    for name, cat, target in habits_def:
        h = Habit(
            user_id=user_id,
            name=name,
            description=f"每{cat}，坚持 30 天",
            category=cat,
            frequency="daily",
            target_count=1,
            is_active=1,
        )
        db.add(h)
        db.flush()
        # 25 days checkins
        for i in range(25):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            db.add(HabitCheckin(
                habit_id=h.id,
                user_id=user_id,
                date=date,
                completed=1,
                note=None,
            ))


def init_psychology(db: Session, user_id: int):
    for i in range(20):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        db.add(MoodLog(
            user_id=user_id,
            date=date,
            mood_score=random.randint(5, 9),
            energy_score=random.randint(5, 9),
            stress_score=random.randint(3, 7),
            note=None,
        ))
    # 3 reflections
    prompts = [
        "今天最让我感激的是？",
        "我对未来的期待是什么？",
        "我学到了什么新东西？",
    ]
    for i, p in enumerate(prompts):
        db.add(Reflection(
            user_id=user_id,
            date=(datetime.now() - timedelta(days=i * 7)).strftime("%Y-%m-%d"),
            prompt=p,
            content=f"示例反思内容 #{i + 1}",
            gratitude="家人健康 + 工作顺利 + 学习进步",
        ))


def init_family(db: Session, user_id: int):
    members = [
        ("父亲", "父", "1968-08-12"),
        ("母亲", "母", "1970-12-05"),
        ("姐姐", "姐", "1995-03-20"),
    ]
    for name, rel, bday in members:
        db.add(FamilyMember(
            user_id=user_id,
            name=name,
            relation=rel,
            birthday=bday,
            note=None,
        ))


def init_interest(db: Session, user_id: int):
    interests = [
        ("钢琴", "音乐", 3),
        ("跑步", "运动", 2),
        ("读书", "学习", 2),
    ]
    for name, cat, hours in interests:
        i = Interest(
            user_id=user_id,
            name=name,
            category=cat,
            description=f"每周 {hours} 小时",
            weekly_target_hours=hours,
        )
        db.add(i)
        db.flush()
        # 5 activities
        for j in range(5):
            db.add(InterestActivity(
                user_id=user_id,
                interest_id=i.id,
                date=(datetime.now() - timedelta(days=j * 5)).strftime("%Y-%m-%d"),
                duration_minutes=random.randint(30, 90),
                note=None,
            ))


def init_social(db: Session, user_id: int):
    contacts = [
        ("李四", "朋友", 9),
        ("王五", "同事", 7),
        ("赵六", "同学", 6),
    ]
    for name, rel, close in contacts:
        db.add(Contact(
            user_id=user_id,
            name=name,
            relation=rel,
            closeness=close,
            note=None,
        ))


def init_learning(db: Session, user_id: int):
    books = [
        ("深入理解计算机系统", "Bryant", "reading", 800, 320),
        ("活着", "余华", "finished", 280, 280),
        ("人类简史", "赫拉利", "reading", 440, 100),
    ]
    for title, author, status, total, current in books:
        db.add(Book(
            user_id=user_id,
            title=title,
            author=author,
            category=None,
            status=status,
            total_pages=total,
            current_page=current,
        ))
    db.add(Course(
        user_id=user_id,
        title="CS231n",
        platform="Stanford Online",
        category="AI",
        status="in_progress",
        progress_percent=45,
    ))


def init_travel(db: Session, user_id: int):
    # 2 trips + 5 bucket list items
    trips = [
        ("东京", "2025-04-01", "2025-04-07"),
        ("成都", "2025-10-01", "2025-10-04"),
    ]
    for dest, start, end in trips:
        db.add(Trip(
            user_id=user_id,
            destination=dest,
            start_date=start,
            end_date=end,
            cost_cny=random.uniform(3000, 8000),
            rating=5,
            note=None,
            photo_count=random.randint(20, 50),
        ))
    buckets = ["巴黎", "伦敦", "纽约", "京都", "冰岛"]
    for dest in buckets:
        db.add(BucketList(
            user_id=user_id,
            destination=dest,
            priority=1,
            note=None,
        ))


def init_intimacy(db: Session, user_id: int):
    db.add(Relationship(
        user_id=user_id,
        name="好友 A",
        relation_type="好友",
        anniversary="2024-06-15",
        status="active",
        note=None,
    ))
    db.add(Anniversary(
        user_id=user_id,
        title="相识纪念日",
        date="2024-06-15",
        recurring=1,
        note=None,
    ))


def init_meaning(db: Session, user_id: int):
    values = [
        ("成长", "持续学习与进步", 10),
        ("健康", "身体与心理健康", 9),
        ("家庭", "陪伴家人", 9),
        ("自由", "财务自由 + 时间自由", 8),
        ("贡献", "为他人创造价值", 7),
    ]
    for name, desc, imp in values:
        db.add(Value(
            user_id=user_id,
            name=name,
            description=desc,
            importance=imp,
        ))
    db.add(LifePurpose(
        user_id=user_id,
        statement="用我的研究与产品让 AI 更值得信赖，让家人过上更稳定的生活。",
        version=1,
        is_current=1,
    ))


INIT_TASKS = [
    ("health", init_health),
    ("finance", init_finance),
    ("habits", init_habits),
    ("psychology", init_psychology),
    ("family", init_family),
    ("interest", init_interest),
    ("social", init_social),
    ("learning", init_learning),
    ("travel", init_travel),
    ("intimacy", init_intimacy),
    ("meaning", init_meaning),
]


def init_sample_data(db: Session, user_id: int):
    """Initialize 30 days of sample data for all 11 subdomains.

    Called from auth.register.
    """
    random.seed(user_id)  # Deterministic per user
    for name, fn in INIT_TASKS:
        try:
            fn(db, user_id)
        except Exception as e:
            print(f"Warning: init_{name} failed: {e}")
    db.commit()


def main():
    parser = argparse.ArgumentParser(description="Inject 30-day sample data for an existing user.")
    parser.add_argument("--user-id", type=int, required=True, help="User ID to initialize")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == args.user_id).first()
        if not user:
            print(f"User {args.user_id} not found.")
            sys.exit(1)
        print(f"Injecting sample data for user {user.username} ({user.id})...")
        init_sample_data(db, args.user_id)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()