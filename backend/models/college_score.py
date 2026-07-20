"""
CollegeScore model for Life Planner application.

Represents college admission score data for different years/provinces/majors.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from shared.base_model import BaseModel


class CollegeScore(BaseModel):
    """
    College admission score model.
    
    Stores min/average/max admission scores and rank for each
    college + major combination in a given year/province.
    
    Attributes:
        year: Admission year (e.g. 2025)
        province: Province name (e.g. "山东")
        college_name: College name (e.g. "北京大学")
        major_name: Major name (e.g. "计算机科学与技术")
        batch: Batch (本科批/本科一批/etc.)
        min_score: Minimum admission score (may be null for some provinces like 山东)
        avg_score: Average admission score (may be null)
        max_score: Maximum admission score (may be null)
        min_rank: Minimum admission rank (位次), the key metric for 山东-style data
        source: Data source identifier (e.g. "sdzk.cn_2025")
    """
    
    __tablename__ = "college_scores"
    
    year = Column(Integer, nullable=False, index=True)
    province = Column(String(50), nullable=False, index=True)
    college_name = Column(String(100), nullable=False, index=True)
    major_name = Column(String(100), nullable=False, index=True)
    batch = Column(String(50), nullable=True)
    min_score = Column(Float, nullable=True)
    avg_score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    min_rank = Column(Integer, nullable=True)
    source = Column(String(100), nullable=True)
    subject_type = Column(String(20), nullable=True)  # 物理/历史/综合/艺术类/etc
    
    # Index for common query pattern: filter by year+province+college
    __table_args__ = (
        Index("idx_year_province_college", "year", "province", "college_name"),
        Index("idx_year_province_major", "year", "province", "major_name"),
    )
    
    def to_dict(self):
        """Convert to dict (extends BaseModel.to_dict)."""
        d = super().to_dict()
        d.update({
            "year": self.year,
            "province": self.province,
            "college_name": self.college_name,
            "major_name": self.major_name,
            "batch": self.batch,
            "min_score": self.min_score,
            "avg_score": self.avg_score,
            "max_score": self.max_score,
            "min_rank": self.min_rank,
            "source": self.source,
            "subject_type": self.subject_type,
        })
        return d
