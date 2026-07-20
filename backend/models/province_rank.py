"""
ProvinceRank model for Life Planner application.

Represents the score-to-rank conversion data (一分一段表) for different provinces/years.
"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from shared.base_model import BaseModel


class ProvinceRank(BaseModel):
    """
    Province rank model for score-to-rank conversion.
    
    Attributes:
        id: Primary key
        year: Exam year
        province: Province name
        score: Total score
        rank: Corresponding rank
        batch_category: Batch category (物理类/历史类/etc.)
        updated_at: Last update timestamp
    """
    
    __tablename__ = "province_ranks"
    
    year = Column(Integer, nullable=False, index=True)
    province = Column(String(50), nullable=False, index=True)
    score = Column(Integer, nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    batch_category = Column(String(50), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Index for common query pattern
    __table_args__ = (
        Index("idx_year_province_score", "year", "province", "score"),
    )
    
    def to_dict(self):
        """Convert province rank to dictionary."""
        return {
            "id": self.id,
            "year": self.year,
            "province": self.province,
            "score": self.score,
            "rank": self.rank,
            "batch_category": self.batch_category,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
