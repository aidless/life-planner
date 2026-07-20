"""
Exam model for Life Planner application.

Represents an exam record (e.g., 高三一模) with OCR processing status.
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from shared.base_model import BaseModel


class Exam(BaseModel):
    """
    Exam model for tracking student exams and OCR processing.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        subject: Exam subject (数学/物理/化学)
        exam_name: Exam name (e.g., "2025届高三一模")
        total_score: Total score of the exam
        user_score: User's actual score
        exam_date: Date of the exam
        image_path: Path to original exam image
        status: Processing status (pending/processing/done/failed)
        created_at: Exam creation timestamp
    """
    
    __tablename__ = "exams"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String(50), nullable=False)
    exam_name = Column(String(100), nullable=False)
    total_score = Column(Float, nullable=True)
    user_score = Column(Float, nullable=True)
    exam_date = Column(Date, nullable=True)
    image_path = Column(String(255), nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="exams")
    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")
    diagnosis_report = relationship("DiagnosisReport", back_populates="exam", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert exam to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subject": self.subject,
            "exam_name": self.exam_name,
            "total_score": self.total_score,
            "user_score": self.user_score,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "image_path": self.image_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
