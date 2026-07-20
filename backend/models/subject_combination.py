"""
SubjectCombination model for Life Planner application.

Represents the 12 possible subject combinations and their coverage rates.
"""

from sqlalchemy import Column, Integer, String, Float, Text
from shared.base_model import BaseModel


class SubjectCombination(BaseModel):
    """
    Subject combination model with coverage rate information.
    
    Attributes:
        id: Primary key
        name: Combination name (e.g., "物理+化学+生物")
        compulsory_1: First compulsory subject (物理/历史)
        optional_2: Two optional subjects (化学/生物/地理/政治)
        coverage_rate: Major coverage rate (0.00~1.00)
        description: Combination description
        career_directions: Career directions for this combination
    """
    
    __tablename__ = "subject_combinations"
    
    name = Column(String(50), unique=True, nullable=False)
    compulsory_1 = Column(String(10), nullable=False)
    optional_2 = Column(String(20), nullable=False)
    coverage_rate = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    career_directions = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert combination to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "compulsory_1": self.compulsory_1,
            "optional_2": self.optional_2,
            "coverage_rate": self.coverage_rate,
            "description": self.description,
            "career_directions": self.career_directions,
        }
