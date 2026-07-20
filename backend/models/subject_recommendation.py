"""
SubjectRecommendation model for Life Planner application.

Represents AI-generated subject combination recommendations based on assessment results.
"""

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from shared.base_model import BaseModel


class SubjectRecommendation(BaseModel):
    """
    Subject recommendation model for Top3 combinations.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        assessment_id: Foreign key to SubjectAssessment
        top3_combinations: JSON array of top 3 combinations with details
        recommended_rank_1: First recommended combination name
        recommended_rank_2: Second recommended combination name
        recommended_rank_3: Third recommended combination name
        created_at: Recommendation creation timestamp
    """
    
    __tablename__ = "subject_recommendations"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("subject_assessments.id"), nullable=False)
    top3_combinations = Column(JSON, nullable=True)
    recommended_rank_1 = Column(String(50), nullable=True)
    recommended_rank_2 = Column(String(50), nullable=True)
    recommended_rank_3 = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subject_recommendations")
    assessment = relationship("SubjectAssessment", back_populates="recommendation")
    
    def to_dict(self):
        """Convert recommendation to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "assessment_id": self.assessment_id,
            "top3_combinations": self.top3_combinations,
            "recommended_rank_1": self.recommended_rank_1,
            "recommended_rank_2": self.recommended_rank_2,
            "recommended_rank_3": self.recommended_rank_3,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
