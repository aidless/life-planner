"""Exam CRUD service with question-level analysis."""

from sqlalchemy.orm import Session, joinedload

from app.modules.exam_analyzer.models import Exam, ExamQuestion
from app.modules.exam_analyzer.schemas import ExamCreate, QuestionCreate
from app.shared.ai_client import ai_client


def create_exam(db: Session, user_id: int, data: ExamCreate) -> Exam:
    exam = Exam(
        user_id=user_id,
        name=data.name,
        subject=data.subject,
        exam_date=data.exam_date,
        total_score=data.total_score,
        score=data.score,
        full_score=data.full_score,
        rank=data.rank,
        notes=data.notes,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


def get_exams(db: Session, user_id: int) -> list[Exam]:
    return (
        db.query(Exam)
        .filter(Exam.user_id == user_id)
        .order_by(Exam.exam_date.desc())
        .all()
    )


def get_exam(db: Session, user_id: int, exam_id: int) -> Exam | None:
    return (
        db.query(Exam)
        .options(joinedload(Exam.questions))
        .filter(Exam.id == exam_id, Exam.user_id == user_id)
        .first()
    )


def delete_exam(db: Session, user_id: int, exam_id: int) -> bool:
    exam = get_exam(db, user_id, exam_id)
    if not exam:
        return False
    db.delete(exam)
    db.commit()
    return True


def add_question(
    db: Session, user_id: int, exam_id: int, data: QuestionCreate
) -> ExamQuestion | None:
    exam = (
        db.query(Exam)
        .filter(Exam.id == exam_id, Exam.user_id == user_id)
        .first()
    )
    if not exam:
        return None

    question = ExamQuestion(
        exam_id=exam_id,
        question_number=data.question_number,
        topic=data.topic,
        knowledge_point=data.knowledge_point,
        correct=data.correct,
        my_answer=data.my_answer,
        correct_answer=data.correct_answer,
        difficulty=data.difficulty,
        score_value=data.score_value,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_wrong_questions(
    db: Session, user_id: int, exam_id: int
) -> list[ExamQuestion]:
    return (
        db.query(ExamQuestion)
        .join(Exam)
        .filter(
            Exam.id == exam_id,
            Exam.user_id == user_id,
            ExamQuestion.correct == False,  # noqa: E712
        )
        .all()
    )


async def generate_exam_analysis(
    db: Session, user_id: int, exam_id: int
) -> str | None:
    exam = get_exam(db, user_id, exam_id)
    if not exam:
        return None

    wrong_qs = get_wrong_questions(db, user_id, exam_id)

    exam_info = {
        "name": exam.name,
        "subject": exam.subject,
        "total_score": exam.total_score,
        "score": exam.score,
        "full_score": exam.full_score,
        "rank": exam.rank,
    }

    questions_data = [
        {
            "question_number": q.question_number,
            "topic": q.topic,
            "knowledge_point": q.knowledge_point,
            "correct": q.correct,
            "my_answer": q.my_answer,
            "correct_answer": q.correct_answer,
            "difficulty": q.difficulty,
        }
        for q in wrong_qs
    ]

    analysis = await ai_client.analyze_exam(exam_info, questions_data)
    setattr(exam, "ai_analysis", analysis)
    db.commit()
    db.refresh(exam)
    return analysis
