"""Exam schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    question_number: int
    topic: str = ""
    knowledge_point: str = ""
    correct: bool = False
    my_answer: str = ""
    correct_answer: str = ""
    difficulty: str = "medium"
    score_value: float = 0.0


class QuestionResponse(BaseModel):
    id: int
    exam_id: int
    question_number: int
    topic: str
    knowledge_point: str
    correct: bool
    my_answer: str
    correct_answer: str
    difficulty: str
    score_value: float
    ai_analysis: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ExamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=100)
    exam_date: datetime
    total_score: float
    score: float
    full_score: float = 100.0
    rank: int | None = None
    notes: str = ""


class ExamResponse(BaseModel):
    id: int
    user_id: int
    name: str
    subject: str
    exam_date: datetime
    total_score: float
    score: float
    full_score: float
    rank: int | None
    notes: str
    ai_analysis: str
    created_at: datetime
    updated_at: datetime
    questions: list[QuestionResponse] = []

    model_config = {"from_attributes": True}
