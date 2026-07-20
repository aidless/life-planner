"""Initial database migration - Create all tables.

Revision ID: 001
Revises: 
Create Date: 2026-06-10

Creates all initial tables for Life Planner application.
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '001_init_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('phone', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('nickname', sa.String(100), nullable=True),
        sa.Column('province', sa.String(50), nullable=True),
        sa.Column('subject_combination', sa.String(50), nullable=True),
        sa.Column('graduation_year', sa.String(10), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create subject_combinations table
    op.create_table(
        'subject_combinations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('compulsory_1', sa.String(10), nullable=False),
        sa.Column('optional_2', sa.String(20), nullable=False),
        sa.Column('coverage_rate', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('career_directions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create subject_assessments table
    op.create_table(
        'subject_assessments',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('answers', sa.JSON(), nullable=False),
        sa.Column('holland_result', sa.JSON(), nullable=True),
        sa.Column('ability_scores', sa.JSON(), nullable=True),
        sa.Column('target_major', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create subject_recommendations table
    op.create_table(
        'subject_recommendations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('assessment_id', sa.Integer(), sa.ForeignKey('subject_assessments.id'), nullable=False),
        sa.Column('top3_combinations', sa.JSON(), nullable=True),
        sa.Column('recommended_rank_1', sa.String(50), nullable=True),
        sa.Column('recommended_rank_2', sa.String(50), nullable=True),
        sa.Column('recommended_rank_3', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create exams table
    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('subject', sa.String(50), nullable=False),
        sa.Column('exam_name', sa.String(100), nullable=False),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('user_score', sa.Float(), nullable=True),
        sa.Column('exam_date', sa.Date(), nullable=True),
        sa.Column('image_path', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), default='pending', nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create exam_questions table
    op.create_table(
        'exam_questions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('exam_id', sa.Integer(), sa.ForeignKey('exams.id'), nullable=False, index=True),
        sa.Column('question_number', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(1000), nullable=True),
        sa.Column('user_answer', sa.String(500), nullable=True),
        sa.Column('correct_answer', sa.String(500), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('user_score', sa.Float(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('knowledge_tags', sa.JSON(), nullable=True),
        sa.Column('error_reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create diagnosis_reports table
    op.create_table(
        'diagnosis_reports',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('exam_id', sa.Integer(), sa.ForeignKey('exams.id'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('knowledge_mastery', sa.JSON(), nullable=True),
        sa.Column('weak_points', sa.JSON(), nullable=True),
        sa.Column('study_suggestions', sa.JSON(), nullable=True),
        sa.Column('ai_summary', sa.String(2000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create college_info table
    op.create_table(
        'college_info',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('province', sa.String(50), nullable=True, index=True),
        sa.Column('city', sa.String(50), nullable=True),
        sa.Column('ownership', sa.String(20), nullable=True),
        sa.Column('level', sa.String(20), nullable=True),
        sa.Column('features', sa.String(100), nullable=True),
        sa.Column('website', sa.String(200), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create college_scores table
    op.create_table(
        'college_scores',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('province', sa.String(50), nullable=False, index=True),
        sa.Column('college_name', sa.String(100), nullable=False, index=True),
        sa.Column('major_name', sa.String(100), nullable=False, index=True),
        sa.Column('batch', sa.String(50), nullable=True),
        sa.Column('min_score', sa.Float(), nullable=True),
        sa.Column('avg_score', sa.Float(), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=True),
        sa.Column('rank_min', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create index on college_scores
    op.create_index('idx_year_province_college', 'college_scores', ['year', 'province', 'college_name', 'major_name'])
    
    # Create province_ranks table
    op.create_table(
        'province_ranks',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('province', sa.String(50), nullable=False, index=True),
        sa.Column('score', sa.Integer(), nullable=False, index=True),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('batch_category', sa.String(50), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )
    
    # Create index on province_ranks
    op.create_index('idx_year_province_score', 'province_ranks', ['year', 'province', 'score'])
    
    # Create college_recommendations table
    op.create_table(
        'college_recommendations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('score_input', sa.Float(), nullable=False),
        sa.Column('rank_input', sa.Integer(), nullable=True),
        sa.Column('province', sa.String(50), nullable=False),
        sa.Column('subject_combination', sa.String(50), nullable=True),
        sa.Column('dash_colleges', sa.JSON(), nullable=True),
        sa.Column('steady_colleges', sa.JSON(), nullable=True),
        sa.Column('safe_colleges', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False, index=True),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('college_recommendations')
    op.drop_table('province_ranks')
    op.drop_table('college_scores')
    op.drop_table('college_info')
    op.drop_table('diagnosis_reports')
    op.drop_table('exam_questions')
    op.drop_table('exams')
    op.drop_table('subject_recommendations')
    op.drop_table('subject_assessments')
    op.drop_table('subject_combinations')
    op.drop_table('users')
