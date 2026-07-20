"""
CollegeRecommendation model for Life Planner application.

Represents AI-generated college recommendation results (dash/steady/safe tiers).
"""

from sqlalchemy import Column, Integer, Float, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from shared.base_model import BaseModel


class CollegeRecommendation(BaseModel):
    """
    College recommendation model for dash/steady/safe tiers.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        score_input: User's input score
        rank_input: User's input rank (optional)
        province: User's province
        subject_combination: User's subject combination
        dash_colleges: JSON array of dash tier colleges
        steady_colleges: JSON array of steady tier colleges
        safe_colleges: JSON array of safe tier colleges
        created_at: Recommendation creation timestamp
    """
    
    __tablename__ = "college_recommendations"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    score_input = Column(Float, nullable=False)
    rank_input = Column(Integer, nullable=True)
    province = Column(String(50), nullable=False)
    subject_combination = Column(String(50), nullable=True)
    dash_colleges = Column(JSON, nullable=True)
    steady_colleges = Column(JSON, nullable=True)
    safe_colleges = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="college_recommendations")
    
    def to_dict(self):
        """Convert college recommendation to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "score_input": self.score_input,
            "rank_input": self.rank_input,
            "province": self.province,
            "subject_combination": self.subject_combination,
            "dash_colleges": self.dash_colleges,
            "steady_colleges": self.steady_colleges,
            "safe_colleges": self.safe_colleges,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
