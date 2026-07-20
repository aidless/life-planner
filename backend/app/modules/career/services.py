"""Career module services (added 2026-07-19 fix B-α)."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.career.models import JobApplication


def create_application(db: Session, user_id: int, data) -> JobApplication:
    """Create a new job application entry for user."""
    app = JobApplication(
        user_id=user_id,
        company_name=data.company_name,
        role_title=data.role_title,
        industry=data.industry,
        location=data.location,
        job_description=data.job_description,
        job_url=data.job_url,
        notes=data.notes,
        salary_offered_annual=data.salary_offered_annual,
        base_offered_annual=data.base_offered_annual,
        applied_date=datetime.now(),
        status="applied",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def list_applications(
    db: Session,
    user_id: int,
    *,
    status: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 100,
) -> List[JobApplication]:
    """List user's job applications with optional filters."""
    stmt = select(JobApplication).where(JobApplication.user_id == user_id)
    if status:
        stmt = stmt.where(JobApplication.status == status)
    if industry:
        stmt = stmt.where(JobApplication.industry == industry)
    stmt = stmt.order_by(JobApplication.applied_date.desc()).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_application(db: Session, user_id: int, app_id: int) -> Optional[JobApplication]:
    """Get single application by id, scoped to user."""
    app = db.get(JobApplication, app_id)
    if not app or app.user_id != user_id:
        return None
    return app


def update_application(
    db: Session, user_id: int, app_id: int, data
) -> Optional[JobApplication]:
    """Update existing application (status / dates / notes)."""
    app = get_application(db, user_id, app_id)
    if not app:
        return None
    if data.status is not None:
        app.status = data.status
        # Auto-set decision_date when status=offer or rejected
        if data.status in ("offer", "rejected", "withdrawn"):
            if app.decision_date is None:
                app.decision_date = datetime.now()
    if data.interview_date is not None:
        app.interview_date = data.interview_date
    if data.response_deadline is not None:
        app.response_deadline = data.response_deadline
    if data.decision_date is not None:
        app.decision_date = data.decision_date
    if data.notes is not None:
        app.notes = data.notes
    if data.contacts is not None:
        app.contacts = data.contacts
    if data.salary_offered_annual is not None:
        app.salary_offered_annual = data.salary_offered_annual
    if data.base_offered_annual is not None:
        app.base_offered_annual = data.base_offered_annual
    db.commit()
    db.refresh(app)
    return app


def delete_application(db: Session, user_id: int, app_id: int) -> bool:
    """Delete application (rare; prefer status=withdrawn)."""
    app = get_application(db, user_id, app_id)
    if not app:
        return False
    db.delete(app)
    db.commit()
    return True


def get_career_stats(db: Session, user_id: int) -> dict:
    """Aggregate user's career stats for dashboard."""
    apps = list_applications(db, user_id, limit=1000)
    total = len(apps)
    if total == 0:
        return {
            "total_applications": 0,
            "active": 0,
            "rejected": 0,
            "offers": 0,
            "interview_rate": 0.0,
            "offer_rate": 0.0,
        }
    active = sum(1 for a in apps if a.status in ("applied", "screening", "interview_oa", "interview_1", "interview_2"))
    rejected = sum(1 for a in apps if a.status == "rejected")
    offers = sum(1 for a in apps if a.status == "offer")
    interview_count = sum(1 for a in apps if a.status in ("interview_oa", "interview_1", "interview_2", "offer"))
    return {
        "total_applications": total,
        "active": active,
        "rejected": rejected,
        "offers": offers,
        "interview_rate": round(interview_count / total, 2),
        "offer_rate": round(offers / total, 2),
    }
