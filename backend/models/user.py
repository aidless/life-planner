"""
User model for Life Planner application.

Represents a user (high school student) with authentication and profile information.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from shared.base_model import BaseModel


class User(BaseModel):
    """
    User model for authentication and profile management.
    
    Attributes:
        id: Primary key
        phone: Unique phone number (login credential)
        password_hash: Bcrypt hashed password
        nickname: User's display name
        province: User's province (for college recommendation)
        subject_combination: User's chosen subject combination (e.g., "物化生")
        graduation_year: Expected graduation year
        is_active: Whether account is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "users"
    
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    province = Column(String(50), nullable=True)
    subject_combination = Column(String(50), nullable=True)
    graduation_year = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    subject_assessments = relationship("SubjectAssessment", back_populates="user", cascade="all, delete-orphan")
    subject_recommendations = relationship("SubjectRecommendation", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    college_recommendations = relationship("CollegeRecommendation", back_populates="user", cascade="all, delete-orphan")
    diagnosis_reports = relationship("DiagnosisReport", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "phone": self.phone,
            "nickname": self.nickname,
            "province": self.province,
            "subject_combination": self.subject_combination,
            "graduation_year": self.graduation_year,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
