"""
SubjectAssessment model for Life Planner application.

Represents a user's subject selection assessment (Holland test + ability self-assessment).
"""

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from shared.base_model import BaseModel


class SubjectAssessment(BaseModel):
    """
    Subject assessment model for Holland test and ability evaluation.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        answers: JSON array of 20 question answers
        holland_result: JSON with Holland type scores (R/I/A/S/E/C)
        ability_scores: JSON with ability self-assessment scores
        target_major: Target major (optional)
        created_at: Assessment creation timestamp
    """
    
    __tablename__ = "subject_assessments"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    answers = Column(JSON, nullable=False)
    holland_result = Column(JSON, nullable=True)
    ability_scores = Column(JSON, nullable=True)
    target_major = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subject_assessments")
    recommendation = relationship("SubjectRecommendation", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert assessment to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "answers": self.answers,
            "holland_result": self.holland_result,
            "ability_scores": self.ability_scores,
            "target_major": self.target_major,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
