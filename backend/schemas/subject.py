"""
Subject selection schemas for Life Planner API.

This module defines Pydantic models for:
- Questions (Holland personality test questions)
- Assessments (user answers and assessment creation)
- Recommendations (subject combination recommendations)
- Combinations (available subject combinations)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class QuestionOut(BaseModel):
    """Question response schema."""
    
    id: str = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    options: List[Dict[str, Any]] = Field(..., description="Question options")
    type: str = Field(..., description="Question type (holland/ability)")
    
    model_config = ConfigDict(from_attributes=True)


class AssessmentCreate(BaseModel):
    """Assessment creation request schema."""
    
    answers: List[Dict[str, Any]] = Field(..., description="User answers to questions")
    target_major: Optional[str] = Field(None, description="Target major for recommendation")


class AssessmentOut(BaseModel):
    """Assessment result response schema."""
    
    id: str = Field(..., description="Assessment ID")
    user_id: str = Field(..., description="User ID")
    holland_result: Dict[str, Any] = Field(..., description="Holland test result")
    ability_scores: Dict[str, Any] = Field(..., description="Ability scores")
    created_at: datetime = Field(..., description="Assessment creation time")
    
    model_config = ConfigDict(from_attributes=True)


class RecommendationOut(BaseModel):
    """Recommendation response schema."""
    
    id: str = Field(..., description="Recommendation ID")
    assessment_id: str = Field(..., description="Assessment ID")
    top3: List[Dict[str, Any]] = Field(..., description="Top 3 recommended combinations")
    combinations_detail: List[Dict[str, Any]] = Field(..., description="Detailed combination info")
    created_at: datetime = Field(..., description="Recommendation creation time")
    
    model_config = ConfigDict(from_attributes=True)


class CombinationOut(BaseModel):
    """Subject combination response schema."""
    
    id: str = Field(..., description="Combination ID")
    name: str = Field(..., description="Combination name")
    coverage_rate: float = Field(..., description="Major coverage rate")
    description: str = Field(..., description="Combination description")
    
    model_config = ConfigDict(from_attributes=True)
