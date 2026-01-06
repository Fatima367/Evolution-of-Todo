"""Add is_favorite and recurring_type columns to tasks

Revision ID: 002
Revises: 001
Create Date: 2025-01-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_favorite and recurring_type columns to tasks table"""

    # Add is_favorite column
    op.add_column(
        'tasks',
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    op.create_index(
        'ix_tasks_is_favorite',
        'tasks',
        ['is_favorite'],
        unique=False
    )

    # Add recurring_type column
    op.add_column(
        'tasks',
        sa.Column('recurring_type', sa.String(), nullable=False, server_default='NONE')
    )
    op.create_index(
        'ix_tasks_recurring_type',
        'tasks',
        ['recurring_type'],
        unique=False
    )


def downgrade() -> None:
    """Remove is_favorite and recurring_type columns from tasks table"""

    # Drop indexes first
    op.drop_index('ix_tasks_recurring_type', table_name='tasks')
    op.drop_index('ix_tasks_is_favorite', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'recurring_type')
    op.drop_column('tasks', 'is_favorite')
