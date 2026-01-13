"""Add reminder_offset to tasks table

Revision ID: 006
Revises: 005
Create Date: 2026-01-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add reminder_offset column to tasks table"""

    # Add reminder_offset column (minutes before due_date to send reminder)
    op.add_column(
        'tasks',
        sa.Column('reminder_offset', sa.Integer(), nullable=False, server_default='15')
    )


def downgrade() -> None:
    """Remove reminder_offset column from tasks table"""

    op.drop_column('tasks', 'reminder_offset')
