"""Create reminders table

Revision ID: 008
Revises: 007
Create Date: 2026-01-13 00:02:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create reminders table for scheduled task reminders"""

    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('remind_at', sa.DateTime(), nullable=False),
        sa.Column('sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
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
        )
    )

    # Create indexes for efficient queries
    op.create_index(
        'ix_reminders_user_id',
        'reminders',
        ['user_id'],
        unique=False
    )

    op.create_index(
        'ix_reminders_task_id',
        'reminders',
        ['task_id'],
        unique=False
    )

    op.create_index(
        'ix_reminders_remind_at',
        'reminders',
        ['remind_at'],
        unique=False
    )

    op.create_index(
        'ix_reminders_sent',
        'reminders',
        ['sent'],
        unique=False
    )

    # Partial index for pending reminders (most common query)
    op.execute(
        "CREATE INDEX ix_reminders_pending ON reminders(remind_at, sent) WHERE sent = false"
    )


def downgrade() -> None:
    """Drop reminders table"""

    op.execute("DROP INDEX IF EXISTS ix_reminders_pending")
    op.drop_index('ix_reminders_sent', table_name='reminders')
    op.drop_index('ix_reminders_remind_at', table_name='reminders')
    op.drop_index('ix_reminders_task_id', table_name='reminders')
    op.drop_index('ix_reminders_user_id', table_name='reminders')
    op.drop_table('reminders')
