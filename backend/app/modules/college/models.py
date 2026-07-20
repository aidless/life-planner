"""College module models.

Re-exports SQLAlchemy models from the legacy ``models/`` package.
This keeps a single source of truth for the database schema while
moving the application code to the new ``app/modules/`` layout.
"""

from models.college_score import CollegeScore  # noqa: F401
from models.college_info import CollegeInfo  # noqa: F401
from models.province_rank import ProvinceRank  # noqa: F401
from models.college_recommendation import CollegeRecommendation  # noqa: F401

__all__ = [
    "CollegeScore",
    "CollegeInfo",
    "ProvinceRank",
    "CollegeRecommendation",
]
