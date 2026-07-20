"""Life goal CRUD service."""

from sqlalchemy.orm import Session

from app.modules.life_planner.models import LifeGoal
from app.modules.life_planner.schemas import GoalCreate, GoalUpdate


def create_goal(db: Session, user_id: int, data: GoalCreate) -> LifeGoal:
    goal = LifeGoal(
        user_id=user_id,
        title=data.title,
        description=data.description,
        category=data.category,
        target_date=data.target_date,
        priority=data.priority,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_goals(db: Session, user_id: int, status: str | None = None) -> list[LifeGoal]:
    query = db.query(LifeGoal).filter(LifeGoal.user_id == user_id)
    if status:
        query = query.filter(LifeGoal.status == status)
    return query.order_by(LifeGoal.priority.desc(), LifeGoal.created_at.desc()).all()


def get_goal(db: Session, user_id: int, goal_id: int) -> LifeGoal | None:
    return (
        db.query(LifeGoal)
        .filter(LifeGoal.id == goal_id, LifeGoal.user_id == user_id)
        .first()
    )


def update_goal(
    db: Session, user_id: int, goal_id: int, data: GoalUpdate
) -> LifeGoal | None:
    goal = get_goal(db, user_id, goal_id)
    if not goal:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, user_id: int, goal_id: int) -> bool:
    goal = get_goal(db, user_id, goal_id)
    if not goal:
        return False
    db.delete(goal)
    db.commit()
    return True
