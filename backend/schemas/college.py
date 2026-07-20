"""
College prediction and query schemas for Life Planner API.

This module defines Pydantic models for:
- Predict request/response (college prediction based on score)
- Score query (college score lines by year/province/college)
- Rank query (rank query by score and province)
- College list (college list with filters)
- College detail (college information with recent scores)
- Recommendation history (user's college recommendation history)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class PredictRequest(BaseModel):
    """College prediction request schema.

    W29: added score range constraint (0-750) and province non-empty
    to prevent invalid inputs from passing through to the service layer.
    """
    model_config = ConfigDict(from_attributes=True)

    score: float = Field(..., ge=0, le=750, description="User score (0-750)")
    rank: Optional[int] = Field(None, ge=0, le=1_000_000, description="User rank (optional)")
    province: str = Field(..., min_length=1, max_length=50, description="User province")
    subject_combination: str = Field(..., min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=2000, le=2100, description="Prediction year")


class PredictResponse(BaseModel):
    """College prediction response schema."""
    
    dash: List[Dict[str, Any]] = Field(..., description="Dash tier colleges (reach)")
    steady: List[Dict[str, Any]] = Field(..., description="Steady tier colleges (match)")
    safe: List[Dict[str, Any]] = Field(..., description="Safe tier colleges (safety)")


class ScoreQuery(BaseModel):
    """College score query parameters schema."""
    
    year: Optional[int] = Field(None, description="Query year")
    province: Optional[str] = Field(None, description="Query province")
    college: Optional[str] = Field(None, description="Query college name")
    major: Optional[str] = Field(None, description="Query major name")


class RankQuery(BaseModel):
    """Rank query parameters schema."""
    
    year: int = Field(..., description="Query year")
    province: str = Field(..., description="Query province")
    score: float = Field(..., description="Query score")


class CollegeOut(BaseModel):
    """College list item schema."""
    
    id: str = Field(..., description="College ID")
    name: str = Field(..., description="College name")
    features: List[str] = Field(..., description="College features/tags")
    
    model_config = ConfigDict(from_attributes=True)


class CollegeDetail(BaseModel):
    """College detail response schema."""
    
    id: str = Field(..., description="College ID")
    name: str = Field(..., description="College name")
    features: List[str] = Field(..., description="College features/tags")
    recent_scores: List[Dict[str, Any]] = Field(..., description="Recent years score lines")
    
    model_config = ConfigDict(from_attributes=True)


class RecommendationHistoryItem(BaseModel):
    """College recommendation history item schema."""
    
    id: str = Field(..., description="Recommendation ID")
    score_input: Dict[str, Any] = Field(..., description="Score input for recommendation")
    created_at: datetime = Field(..., description="Recommendation creation time")
    
    model_config = ConfigDict(from_attributes=True)
