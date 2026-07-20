"""
DiagnosisReport model for Life Planner application.

Represents AI-generated diagnosis report for an exam with knowledge mastery analysis.
"""

from sqlalchemy import Column, Integer, JSON, String, ForeignKey
from sqlalchemy.orm import relationship
from shared.base_model import BaseModel


class DiagnosisReport(BaseModel):
    """
    Diagnosis report model for exam analysis.
    
    Attributes:
        id: Primary key
        exam_id: Foreign key to Exam
        user_id: Foreign key to User
        knowledge_mastery: JSON array of knowledge points with mastery scores
        weak_points: JSON array of weak knowledge points
        study_suggestions: JSON array of study suggestions
        ai_summary: AI-generated summary text
        created_at: Report creation timestamp
    """
    
    __tablename__ = "diagnosis_reports"
    
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    knowledge_mastery = Column(JSON, nullable=True)
    weak_points = Column(JSON, nullable=True)
    study_suggestions = Column(JSON, nullable=True)
    ai_summary = Column(String(2000), nullable=True)
    
    # Relationships
    exam = relationship("Exam", back_populates="diagnosis_report")
    user = relationship("User", back_populates="diagnosis_reports")
    
    def to_dict(self):
        """Convert diagnosis report to dictionary."""
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "user_id": self.user_id,
            "knowledge_mastery": self.knowledge_mastery,
            "weak_points": self.weak_points,
            "study_suggestions": self.study_suggestions,
            "ai_summary": self.ai_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
