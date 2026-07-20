"""Learning module API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.learning import schemas, services
from app.modules.learning.schemas import ApiResponse

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.post("/books", response_model=ApiResponse)
def create_book(
    payload: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = services.create_book(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.BookResponse.model_validate(b).model_dump())


@router.get("/books", response_model=ApiResponse)
def list_books(
    status: str | None = Query(default=None, pattern="^(reading|finished|paused)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_books(db, int(current_user.id), status)
    return ApiResponse(
        success=True,
        data=[schemas.BookResponse.model_validate(b).model_dump() for b in items],
    )


@router.put("/books/{book_id}", response_model=ApiResponse)
def update_book(
    book_id: int,
    payload: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = services.update_book(db, int(current_user.id), book_id, payload)
    if not b:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return ApiResponse(success=True, data=schemas.BookResponse.model_validate(b).model_dump())


@router.post("/courses", response_model=ApiResponse)
def create_course(
    payload: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = services.create_course(db, int(current_user.id), payload)
    return ApiResponse(success=True, data=schemas.CourseResponse.model_validate(c).model_dump())


@router.get("/courses", response_model=ApiResponse)
def list_courses(
    status: str | None = Query(default=None, pattern="^(in_progress|finished|paused|dropped)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = services.list_courses(db, int(current_user.id), status)
    return ApiResponse(
        success=True,
        data=[schemas.CourseResponse.model_validate(c).model_dump() for c in items],
    )


@router.put("/courses/{course_id}", response_model=ApiResponse)
def update_course(
    course_id: int,
    payload: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = services.update_course(db, int(current_user.id), course_id, payload)
    if not c:
        raise HTTPException(status_code=404, detail="课程不存在")
    return ApiResponse(success=True, data=schemas.CourseResponse.model_validate(c).model_dump())


@router.get("/stats", response_model=ApiResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(success=True, data=services.get_stats(db, int(current_user.id)))

# ============================================================
# StudyTask endpoints (added 2026-07-19 fix B)
# ============================================================

@router.post("/tasks", response_model=schemas.ApiResponse)
def create_task(
    payload: schemas.StudyTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new discrete study task."""
    t = services.create_study_task(db, int(current_user.id), payload)
    return schemas.ApiResponse(
        success=True,
        data=schemas.StudyTaskResponse.model_validate(t).model_dump(),
    )


@router.get("/tasks", response_model=schemas.ApiResponse)
def list_tasks(
    status: str | None = Query(default=None, pattern="^(todo|in_progress|done|skipped)$"),
    subject: str | None = Query(default=None, max_length=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List study tasks for user, optional filters."""
    items = services.list_study_tasks(db, int(current_user.id), status=status, subject=subject)
    return schemas.ApiResponse(
        success=True,
        data=[schemas.StudyTaskResponse.model_validate(t).model_dump() for t in items],
    )


@router.put("/tasks/{task_id}", response_model=schemas.ApiResponse)
def update_task(
    task_id: int,
    payload: schemas.StudyTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update study task (status / priority / note)."""
    t = services.update_study_task(db, int(current_user.id), task_id, payload)
    if not t:
        raise HTTPException(status_code=404, detail="学习任务不存在")
    return schemas.ApiResponse(
        success=True,
        data=schemas.StudyTaskResponse.model_validate(t).model_dump(),
    )


@router.delete("/tasks/{task_id}", response_model=schemas.ApiResponse)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete study task."""
    ok = services.delete_study_task(db, int(current_user.id), task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="学习任务不存在")
    return schemas.ApiResponse(success=True, data={"deleted": task_id})
