"""Create recurring_patterns table

Revision ID: 007
Revises: 006
Create Date: 2026-01-13 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Database default expressions
_DB_NOW = sa.text('now()')


def upgrade() -> None:
    """Create recurring_patterns table for recurring task configuration"""

    op.create_table(
        'recurring_patterns',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('month_of_year', sa.Integer(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('last_generated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=_DB_NOW),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=_DB_NOW),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['task_id'],
            ['tasks.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE'
        ),
        sa.UniqueConstraint('task_id', name='uq_recurring_patterns_task_id')
    )

    # Create indexes for efficient queries
    op.create_index(
        'ix_recurring_patterns_user_id',
        'recurring_patterns',
        ['user_id'],
        unique=False
    )

    op.create_index(
        'ix_recurring_patterns_task_id',
        'recurring_patterns',
        ['task_id'],
        unique=True
    )


def downgrade() -> None:
    """Drop recurring_patterns table"""

    op.drop_index('ix_recurring_patterns_task_id', table_name='recurring_patterns')
    op.drop_index('ix_recurring_patterns_user_id', table_name='recurring_patterns')
    op.drop_table('recurring_patterns')
