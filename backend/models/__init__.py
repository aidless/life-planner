"""
SQLAlchemy data models for Life Planner application.

This package contains all database models organized by domain:
- User and authentication models
- Subject selection models (assessment, recommendation, combinations)
- Exam and diagnosis models (exam, questions, diagnosis reports)
- College admission models (scores, ranks, college info, recommendations)

All models inherit from BaseModel which provides:
- id: Primary key
- created_at: Creation timestamp
- updated_at: Last update timestamp
"""

from models.user import User
from models.subject_assessment import SubjectAssessment
from models.subject_recommendation import SubjectRecommendation
from models.subject_combination import SubjectCombination
from models.exam import Exam
from models.exam_question import ExamQuestion
from models.diagnosis_report import DiagnosisReport
from models.college_score import CollegeScore
from models.province_rank import ProvinceRank
from models.college_info import CollegeInfo
from models.college_recommendation import CollegeRecommendation

__all__ = [
    "User",
    "SubjectAssessment",
    "SubjectRecommendation",
    "SubjectCombination",
    "Exam",
    "ExamQuestion",
    "DiagnosisReport",
    "CollegeScore",
    "ProvinceRank",
    "CollegeInfo",
    "CollegeRecommendation",
]
