"""
ExamQuestion model for Life Planner application.

Represents individual questions in an exam with OCR-identified content and analysis.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from shared.base_model import BaseModel


class ExamQuestion(BaseModel):
    """
    Exam question model for individual question analysis.
    
    Attributes:
        id: Primary key
        exam_id: Foreign key to Exam
        question_number: Question number in the exam
        content: Question content (after OCR)
        user_answer: User's answer
        correct_answer: Correct answer
        score: Total score for this question
        user_score: User's score for this question
        is_correct: Whether user answered correctly
        knowledge_tags: JSON array of knowledge point tags
        error_reason: Reason for error (概念不清/计算失误/审题错误)
        created_at: Question creation timestamp
    """
    
    __tablename__ = "exam_questions"
    
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    content = Column(String(1000), nullable=True)
    user_answer = Column(String(500), nullable=True)
    correct_answer = Column(String(500), nullable=True)
    score = Column(Float, nullable=True)
    user_score = Column(Float, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    knowledge_tags = Column(JSON, nullable=True)
    error_reason = Column(String(100), nullable=True)
    
    # Relationships
    exam = relationship("Exam", back_populates="questions")
    
    def to_dict(self):
        """Convert question to dictionary."""
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "question_number": self.question_number,
            "content": self.content,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "score": self.score,
            "user_score": self.user_score,
            "is_correct": self.is_correct,
            "knowledge_tags": self.knowledge_tags,
            "error_reason": self.error_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
