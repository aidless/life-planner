"""Exam API router with question-level analysis."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import ApiResponse
from app.modules.exam_analyzer import schemas, services

router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.post("", response_model=ApiResponse)
def create_exam(
    payload: schemas.ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = services.create_exam(db, int(current_user.id), payload)
    return ApiResponse(
        success=True,
        data=schemas.ExamResponse.model_validate(exam).model_dump(),
    )


@router.get("", response_model=ApiResponse)
def list_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exams = services.get_exams(db, int(current_user.id))
    return ApiResponse(
        success=True,
        data=[schemas.ExamResponse.model_validate(e).model_dump() for e in exams],
    )


@router.get("/{exam_id}", response_model=ApiResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = services.get_exam(db, int(current_user.id), exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="考试记录不存在")
    return ApiResponse(
        success=True,
        data=schemas.ExamResponse.model_validate(exam).model_dump(),
    )


@router.delete("/{exam_id}", response_model=ApiResponse)
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = services.delete_exam(db, int(current_user.id), exam_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="考试记录不存在")
    return ApiResponse(success=True, data={"message": "考试记录已删除"})


@router.post("/{exam_id}/questions", response_model=ApiResponse)
def add_question(
    exam_id: int,
    payload: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = services.add_question(db, int(current_user.id), exam_id, payload)
    if not question:
        raise HTTPException(status_code=404, detail="考试记录不存在")
    return ApiResponse(
        success=True,
        data=schemas.QuestionResponse.model_validate(question).model_dump(),
    )


@router.post("/{exam_id}/analyze", response_model=ApiResponse)
async def analyze_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = await services.generate_exam_analysis(db, int(current_user.id), exam_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="考试记录不存在")
    return ApiResponse(success=True, data={"analysis": analysis})
