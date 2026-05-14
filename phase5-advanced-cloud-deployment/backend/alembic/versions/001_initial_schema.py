"""Initial schema with User and Task tables

Revision ID: 001
Revises:
Create Date: 2025-12-22 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Database default expressions
_DB_NOW = sa.text('now()')


def upgrade() -> None:
    """Create users and tasks tables with proper indexes"""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=_DB_NOW),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=_DB_NOW),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create unique index on email for fast authentication lookups
    op.create_index(
        'ix_users_email',
        'users',
        ['email'],
        unique=True
    )

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=10000), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('priority', sa.String(), nullable=False, server_default='medium'),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=_DB_NOW),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=_DB_NOW),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE'  # When user is deleted, their tasks are also deleted
        )
    )

    # Create indexes as per data-model.md specification
    # Task.user_id: Index for efficient user-specific queries (required for data isolation)
    op.create_index(
        'ix_tasks_user_id',
        'tasks',
        ['user_id'],
        unique=False
    )

    # Task.created_at: Index for chronological sorting
    op.create_index(
        'ix_tasks_created_at',
        'tasks',
        ['created_at'],
        unique=False
    )

    # Task.status: Index for filtering by status
    op.create_index(
        'ix_tasks_status',
        'tasks',
        ['status'],
        unique=False
    )

    # Task.due_date: Index for due date queries
    op.create_index(
        'ix_tasks_due_date',
        'tasks',
        ['due_date'],
        unique=False
    )

    # Task.priority: Index for priority-based sorting
    op.create_index(
        'ix_tasks_priority',
        'tasks',
        ['priority'],
        unique=False
    )

    # Composite index for common query pattern: user tasks filtered by status
    op.create_index(
        'ix_tasks_user_id_status',
        'tasks',
        ['user_id', 'status'],
        unique=False
    )

    # Composite index for user tasks sorted by creation date
    op.create_index(
        'ix_tasks_user_id_created_at',
        'tasks',
        ['user_id', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    """Drop tasks and users tables"""

    # Drop tasks table indexes first
    op.drop_index('ix_tasks_user_id_created_at', table_name='tasks')
    op.drop_index('ix_tasks_user_id_status', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_index('ix_tasks_due_date', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_created_at', table_name='tasks')
    op.drop_index('ix_tasks_user_id', table_name='tasks')

    # Drop tasks table
    op.drop_table('tasks')

    # Drop users table indexes
    op.drop_index('ix_users_email', table_name='users')

    # Drop users table
    op.drop_table('users')