"""College module Pydantic schemas.

Re-exports from the legacy ``schemas/college.py`` to keep a single
source of truth during the transition.
"""

# Re-export everything from the legacy module
from schemas.college import (  # noqa: F401
    PredictRequest,
    PredictResponse,
    ScoreQuery,
    RankQuery,
    CollegeOut,
    CollegeDetail,
    RecommendationHistoryItem,
)

__all__ = [
    "PredictRequest",
    "PredictResponse",
    "ScoreQuery",
    "RankQuery",
    "CollegeOut",
    "CollegeDetail",
    "RecommendationHistoryItem",
]
