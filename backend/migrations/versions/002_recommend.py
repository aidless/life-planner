"""P5 recommendation tables.

Revision ID: 002_recommend
Revises: 001_init_tables
Create Date: 2026-09-07

Creates recommendation_runs + notifications for the real-time
decision-recommendation system. (Dev.sqlite gets them via create_all;
this migration is for staged/prod parity.)
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_recommend'
down_revision = '001_init_tables'
branch_labels = None
depends_on = None


def _ts_cols():
    return [
        sa.Column('id', sa.Integer(), primary_key=True, index=True,
                  autoincrement=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        'recommendation_runs',
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('date', sa.String(10), nullable=False, index=True),
        sa.Column('slot', sa.String(20), nullable=False, server_default='manual'),
        sa.Column('items_json', sa.Text(), nullable=False, server_default='[]'),
        * _ts_cols(),
    )
    op.create_table(
        'notifications',
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('date', sa.String(10), nullable=False, index=True),
        sa.Column('priority', sa.String(10), nullable=False,
                  server_default='high'),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.String(1000), nullable=True),
        sa.Column('module', sa.String(50), nullable=False,
                  server_default='general'),
        sa.Column('rule', sa.String(20), nullable=False, server_default=''),
        sa.Column('is_read', sa.Integer(), nullable=False, server_default='0'),
        * _ts_cols(),
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('recommendation_runs')
