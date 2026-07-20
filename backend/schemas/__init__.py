"""
Pydantic schemas for Life Planner API.

This package contains all request/response models organized by domain:
- auth: Authentication schemas (register, login, token, profile)
- subject: Subject selection schemas (questions, assessments, recommendations)
- exam: Exam upload and diagnosis schemas
- college: College prediction and query schemas
"""

from schemas.auth import TokenResponse, UserRegister, UserLogin, UserProfileUpdate, UserResponse
from schemas.subject import QuestionOut, AssessmentCreate, AssessmentOut, RecommendationOut, CombinationOut
from schemas.exam import ExamUpload, ExamOut, ExamStatus, DiagnosisOut, ExamHistoryItem
from schemas.college import PredictRequest, PredictResponse, ScoreQuery, RankQuery, CollegeOut, CollegeDetail, RecommendationHistoryItem

__all__ = [
    "TokenResponse",
    "UserRegister",
    "UserLogin",
    "UserProfileUpdate",
    "UserResponse",
    "QuestionOut",
    "AssessmentCreate",
    "AssessmentOut",
    "RecommendationOut",
    "CombinationOut",
    "ExamUpload",
    "ExamOut",
    "ExamStatus",
    "DiagnosisOut",
    "ExamHistoryItem",
    "PredictRequest",
    "PredictResponse",
    "ScoreQuery",
    "RankQuery",
    "CollegeOut",
    "CollegeDetail",
    "RecommendationHistoryItem",
]
