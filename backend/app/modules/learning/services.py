"""Learning module services."""

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.learning.models import Book, Course
from app.modules.learning.schemas import BookCreate, BookUpdate, CourseCreate, CourseUpdate


def create_book(db: Session, user_id: int, data: BookCreate) -> Book:
    b = Book(
        user_id=user_id,
        title=data.title,
        author=data.author,
        category=data.category,
        status="reading",
        total_pages=data.total_pages,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def update_book(db: Session, user_id: int, book_id: int, data: BookUpdate) -> Book | None:
    b = db.query(Book).filter(Book.id == book_id, Book.user_id == user_id).first()
    if not b:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(b, k, v)
    db.commit()
    db.refresh(b)
    return b


def list_books(db: Session, user_id: int, status: str | None = None) -> List[Book]:
    stmt = select(Book).where(Book.user_id == user_id)
    if status:
        stmt = stmt.where(Book.status == status)
    stmt = stmt.order_by(Book.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def create_course(db: Session, user_id: int, data: CourseCreate) -> Course:
    c = Course(
        user_id=user_id,
        title=data.title,
        platform=data.platform,
        category=data.category,
        status="in_progress",
        progress_percent=0,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def update_course(db: Session, user_id: int, course_id: int, data: CourseUpdate) -> Course | None:
    c = db.query(Course).filter(Course.id == course_id, Course.user_id == user_id).first()
    if not c:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


def list_courses(db: Session, user_id: int, status: str | None = None) -> List[Course]:
    stmt = select(Course).where(Course.user_id == user_id)
    if status:
        stmt = stmt.where(Course.status == status)
    stmt = stmt.order_by(Course.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
    books = list_books(db, user_id)
    courses = list_courses(db, user_id)
    books_finished = sum(1 for b in books if b.status == "finished")
    courses_finished = sum(1 for c in courses if c.status == "finished")

    # Score: books (×4) + courses (×12) capped at 100
    score = min(100, books_finished * 4 + courses_finished * 12)

    return {
        "books_total": len(books),
        "books_finished": books_finished,
        "courses_total": len(courses),
        "courses_finished": courses_finished,
        "score": score,
    }

# ============================================================
# StudyTask CRUD (added 2026-07-19 fix B)
# ============================================================

def create_study_task(db: Session, user_id: int, data) -> "StudyTask":
    """Create a new study task for user."""
    from datetime import datetime
    from app.modules.learning.models import StudyTask
    task = StudyTask(
        user_id=user_id,
        title=data.title,
        description=data.description,
        subject=data.subject,
        source_type=data.source_type or "standalone",
        source_ref_id=data.source_ref_id,
        estimated_minutes=data.estimated_minutes,
        priority=data.priority,
        is_recurring=data.is_recurring,
        recurrence_rule=data.recurrence_rule,
        status="todo",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_study_tasks(db: Session, user_id: int, status: str | None = None, subject: str | None = None) -> list:
    """List study tasks for user, optional filters."""
    from sqlalchemy import select
    from app.modules.learning.models import StudyTask
    stmt = select(StudyTask).where(StudyTask.user_id == user_id)
    if status:
        stmt = stmt.where(StudyTask.status == status)
    if subject:
        stmt = stmt.where(StudyTask.subject == subject)
    stmt = stmt.order_by(StudyTask.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def update_study_task(db: Session, user_id: int, task_id: int, data) -> "StudyTask | None":
    """Update study task status/note; auto-set completed_at when status=done."""
    from datetime import datetime
    from app.modules.learning.models import StudyTask
    task = db.get(StudyTask, task_id)
    if not task or task.user_id != user_id:
        return None
    if data.status is not None:
        task.status = data.status
        if data.status == "done" and task.completed_at is None:
            task.completed_at = datetime.now()
    if data.priority is not None:
        task.priority = data.priority
    if data.note is not None:
        task.note = data.note
    db.commit()
    db.refresh(task)
    return task


def delete_study_task(db: Session, user_id: int, task_id: int) -> bool:
    """Delete study task."""
    from app.modules.learning.models import StudyTask
    task = db.get(StudyTask, task_id)
    if not task or task.user_id != user_id:
        return False
    db.delete(task)
    db.commit()
    return True
