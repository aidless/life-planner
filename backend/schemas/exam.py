"""
Exam and diagnosis schemas for Life Planner API.

This module defines Pydantic models for:
- Exam upload (image upload and metadata)
- Exam output (exam details with questions)
- Exam status (processing status and progress)
- Diagnosis (AI diagnosis report)
- Exam history (user's exam list)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ExamUpload(BaseModel):
    """Exam upload request schema."""
    
    subject: str = Field(..., description="Exam subject")
    exam_name: str = Field(..., description="Exam name")
    total_score: float = Field(..., description="Total score of the exam")


class ExamOut(BaseModel):
    """Exam detail response schema."""
    
    id: str = Field(..., description="Exam ID")
    user_id: str = Field(..., description="User ID")
    subject: str = Field(..., description="Exam subject")
    exam_name: str = Field(..., description="Exam name")
    total_score: float = Field(..., description="Total score")
    status: str = Field(..., description="Exam status (pending/done/error)")
    questions: List[Dict[str, Any]] = Field(..., description="Exam questions")
    created_at: datetime = Field(..., description="Exam creation time")
    updated_at: datetime = Field(..., description="Exam last update time")
    
    model_config = ConfigDict(from_attributes=True)


class ExamStatus(BaseModel):
    """Exam status response schema."""
    
    status: str = Field(..., description="Exam status (pending/done/error)")
    progress: float = Field(..., description="Processing progress (0-100)")


class DiagnosisOut(BaseModel):
    """Diagnosis report response schema."""
    
    id: str = Field(..., description="Diagnosis report ID")
    exam_id: str = Field(..., description="Exam ID")
    diagnosis_report: Dict[str, Any] = Field(..., description="AI diagnosis report content")
    created_at: datetime = Field(..., description="Diagnosis creation time")
    
    model_config = ConfigDict(from_attributes=True)


class ExamHistoryItem(BaseModel):
    """Exam history item schema."""
    
    exam_id: str = Field(..., description="Exam ID")
    subject: str = Field(..., description="Exam subject")
    exam_name: str = Field(..., description="Exam name")
    date: datetime = Field(..., description="Exam date")
    status: str = Field(..., description="Exam status")
    
    model_config = ConfigDict(from_attributes=True)
