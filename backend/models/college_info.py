"""
CollegeInfo model for Life Planner application.

Represents college/university basic information.
"""

from sqlalchemy import Column, Integer, String, DateTime
from shared.base_model import BaseModel


class CollegeInfo(BaseModel):
    """
    College info model for university data.
    
    Attributes:
        id: Primary key
        name: College name (unique)
        code: College code
        province: Province location
        city: City location
        ownership: Ownership type (公办/民办/独立学院)
        level: Education level (本科/专科)
        features: College features (985/211/双一流/普通)
        website: College website URL
        updated_at: Last update timestamp
    """
    
    __tablename__ = "college_info"
    
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), nullable=True)
    province = Column(String(50), nullable=True, index=True)
    city = Column(String(50), nullable=True)
    ownership = Column(String(20), nullable=True)
    level = Column(String(20), nullable=True)
    features = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        """Convert college info to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "province": self.province,
            "city": self.city,
            "ownership": self.ownership,
            "level": self.level,
            "features": self.features,
            "website": self.website,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
