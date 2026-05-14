"""Add notification settings to users table

Revision ID: 004
Revises: 003_add_conversations_and_messages
Create Date: 2026-01-06 16:08:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notification settings columns to users table with defaults for existing rows
    op.add_column('users', sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('task_reminders', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('weekly_summary', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    # Remove notification settings columns from users table
    op.drop_column('users', 'email_notifications')
    op.drop_column('users', 'task_reminders')
    op.drop_column('users', 'weekly_summary')