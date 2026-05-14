"""Create audit_logs table

Revision ID: 009
Revises: 008
Create Date: 2026-01-13 00:03:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Database default expressions
_DB_NOW = sa.text('now()')


def upgrade() -> None:
    """Create audit_logs table for complete task operation history"""

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),  # nullable - task may be deleted
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operation', sa.String(length=20), nullable=False),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('request_id', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=_DB_NOW),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE'
        )
    )

    # Create indexes for efficient queries
    op.create_index(
        'ix_audit_logs_user_id',
        'audit_logs',
        ['user_id'],
        unique=False
    )

    # Partial index for task_id (only when not null)
    op.execute(
        "CREATE INDEX ix_audit_logs_task_id ON audit_logs(task_id) WHERE task_id IS NOT NULL"
    )

    op.create_index(
        'ix_audit_logs_created_at',
        'audit_logs',
        ['created_at'],
        unique=False
    )

    op.create_index(
        'ix_audit_logs_operation',
        'audit_logs',
        ['operation'],
        unique=False
    )


def downgrade() -> None:
    """Drop audit_logs table"""

    op.drop_index('ix_audit_logs_operation', table_name='audit_logs')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_task_id")
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')
