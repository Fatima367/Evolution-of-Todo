"""Add soft delete fields to users table

Revision ID: 005
Revises: 004
Create Date: 2026-01-06 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add soft delete fields to users table with defaults for existing rows
    op.add_column('users', sa.Column('deletion_scheduled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('scheduled_for_deletion_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove soft delete fields from users table
    op.drop_column('users', 'deletion_scheduled')
    op.drop_column('users', 'scheduled_for_deletion_at')