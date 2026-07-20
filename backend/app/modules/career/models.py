"""Career module models (added 2026-07-19 fix B-α).

Job applications tracker — explicit user-validated gap (self-feedback-v1).
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from app.shared.base_model import Base, TimestampMixin


class JobApplication(Base, TimestampMixin):
    """Discrete job application entry."""

    __tablename__ = "job_applications"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Core job info
    company_name = Column(String(200), nullable=False)
    role_title = Column(String(200), nullable=False)
    industry = Column(String(80), nullable=True)  # e.g. "互联网", "金融", "教育"
    location = Column(String(80), nullable=True)  # e.g. "北京", "Remote"

    # Application status
    status = Column(String(20), default="applied")
    # applied | screening | interview_oa | interview_1 | interview_2 | offer | rejected | withdrawn

    # Timeline
    applied_date = Column(DateTime, nullable=False)
    interview_date = Column(DateTime, nullable=True)
    response_deadline = Column(DateTime, nullable=True)
    decision_date = Column(DateTime, nullable=True)

    # Compensation
    salary_offered_annual = Column(Integer, nullable=True)  # k RMB/year
    base_offered_annual = Column(Integer, nullable=True)

    # Notes
    job_description = Column(Text, nullable=True)
    job_url = Column(String(500), nullable=True)
    contacts = Column(Text, nullable=True)  # JSON list of contacts
    notes = Column(Text, nullable=True)
