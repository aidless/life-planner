"""Exam and exam question models for score analysis."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.shared.base_model import Base, TimestampMixin


class Exam(Base, TimestampMixin):
    """An exam record with total score and metadata."""

    __tablename__ = "exams"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False)
    exam_date = Column(DateTime(timezone=True), nullable=False)
    total_score = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    full_score = Column(Float, default=100.0)
    rank = Column(Integer, nullable=True)
    notes = Column(Text, default="")
    ai_analysis = Column(Text, default="")

    user = relationship("User", back_populates="exams")
    questions = relationship(
        "ExamQuestion", back_populates="exam", cascade="all, delete-orphan"
    )


class ExamQuestion(Base, TimestampMixin):
    """Individual question analysis within an exam."""

    __tablename__ = "exam_questions"

    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    topic = Column(String(200), default="")
    knowledge_point = Column(String(200), default="")
    correct = Column(Boolean, default=False)
    my_answer = Column(String(500), default="")
    correct_answer = Column(String(500), default="")
    difficulty = Column(String(20), default="medium")
    score_value = Column(Float, default=0.0)
    ai_analysis = Column(Text, default="")

    exam = relationship("Exam", back_populates="questions")
