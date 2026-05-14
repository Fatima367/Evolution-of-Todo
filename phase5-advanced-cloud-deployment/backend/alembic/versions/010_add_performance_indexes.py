"""Add performance indexes for Phase V tables

Revision ID: 010
Revises: 009
Create Date: 2026-01-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for frequently queried fields"""

    # Indexes for recurring_patterns table
    op.create_index(
        'ix_recurring_patterns_task_id',
        'recurring_patterns',
        ['task_id'],
        unique=False
    )
    op.create_index(
        'ix_recurring_patterns_user_id',
        'recurring_patterns',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_recurring_patterns_next_occurrence',
        'recurring_patterns',
        ['next_occurrence'],
        unique=False
    )
    # Composite index for active recurring patterns by user
    op.create_index(
        'ix_recurring_patterns_user_id_is_active',
        'recurring_patterns',
        ['user_id', 'is_active'],
        unique=False
    )

    # Indexes for reminders table
    op.create_index(
        'ix_reminders_task_id',
        'reminders',
        ['task_id'],
        unique=False
    )
    op.create_index(
        'ix_reminders_user_id',
        'reminders',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_reminders_reminder_time',
        'reminders',
        ['reminder_time'],
        unique=False
    )
    op.create_index(
        'ix_reminders_is_sent',
        'reminders',
        ['is_sent'],
        unique=False
    )
    # Composite index for pending reminders
    op.create_index(
        'ix_reminders_is_sent_reminder_time',
        'reminders',
        ['is_sent', 'reminder_time'],
        unique=False
    )

    # Indexes for audit_logs table
    op.create_index(
        'ix_audit_logs_user_id',
        'audit_logs',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_audit_logs_entity_type',
        'audit_logs',
        ['entity_type'],
        unique=False
    )
    op.create_index(
        'ix_audit_logs_entity_id',
        'audit_logs',
        ['entity_id'],
        unique=False
    )
    op.create_index(
        'ix_audit_logs_action',
        'audit_logs',
        ['action'],
        unique=False
    )
    op.create_index(
        'ix_audit_logs_timestamp',
        'audit_logs',
        ['timestamp'],
        unique=False
    )
    # Composite index for user audit trail
    op.create_index(
        'ix_audit_logs_user_id_timestamp',
        'audit_logs',
        ['user_id', 'timestamp'],
        unique=False
    )
    # Composite index for entity audit trail
    op.create_index(
        'ix_audit_logs_entity_type_entity_id',
        'audit_logs',
        ['entity_type', 'entity_id'],
        unique=False
    )

    # Additional indexes for conversations and messages (if not already present)
    # Check if these tables exist before creating indexes
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'conversations' in tables:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('conversations')]
        if 'ix_conversations_user_id' not in existing_indexes:
            op.create_index(
                'ix_conversations_user_id',
                'conversations',
                ['user_id'],
                unique=False
            )
        if 'ix_conversations_created_at' not in existing_indexes:
            op.create_index(
                'ix_conversations_created_at',
                'conversations',
                ['created_at'],
                unique=False
            )

    if 'messages' in tables:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('messages')]
        if 'ix_messages_conversation_id' not in existing_indexes:
            op.create_index(
                'ix_messages_conversation_id',
                'messages',
                ['conversation_id'],
                unique=False
            )
        if 'ix_messages_created_at' not in existing_indexes:
            op.create_index(
                'ix_messages_created_at',
                'messages',
                ['created_at'],
                unique=False
            )

    # Add GIN index for full-text search on task titles and descriptions
    # This significantly improves search performance
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_tasks_title_gin
        ON tasks USING gin(to_tsvector('english', title))
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_tasks_description_gin
        ON tasks USING gin(to_tsvector('english', COALESCE(description, '')))
    """)

    # Add GIN index for tags array search
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_tasks_tags_gin
        ON tasks USING gin(tags)
    """)


def downgrade() -> None:
    """Remove performance indexes"""

    # Drop GIN indexes
    op.execute("DROP INDEX IF EXISTS ix_tasks_tags_gin")
    op.execute("DROP INDEX IF EXISTS ix_tasks_description_gin")
    op.execute("DROP INDEX IF EXISTS ix_tasks_title_gin")

    # Drop conversation and message indexes if they exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'messages' in tables:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('messages')]
        if 'ix_messages_created_at' in existing_indexes:
            op.drop_index('ix_messages_created_at', table_name='messages')
        if 'ix_messages_conversation_id' in existing_indexes:
            op.drop_index('ix_messages_conversation_id', table_name='messages')

    if 'conversations' in tables:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('conversations')]
        if 'ix_conversations_created_at' in existing_indexes:
            op.drop_index('ix_conversations_created_at', table_name='conversations')
        if 'ix_conversations_user_id' in existing_indexes:
            op.drop_index('ix_conversations_user_id', table_name='conversations')

    # Drop audit_logs indexes
    op.drop_index('ix_audit_logs_entity_type_entity_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')

    # Drop reminders indexes
    op.drop_index('ix_reminders_is_sent_reminder_time', table_name='reminders')
    op.drop_index('ix_reminders_is_sent', table_name='reminders')
    op.drop_index('ix_reminders_reminder_time', table_name='reminders')
    op.drop_index('ix_reminders_user_id', table_name='reminders')
    op.drop_index('ix_reminders_task_id', table_name='reminders')

    # Drop recurring_patterns indexes
    op.drop_index('ix_recurring_patterns_user_id_is_active', table_name='recurring_patterns')
    op.drop_index('ix_recurring_patterns_next_occurrence', table_name='recurring_patterns')
    op.drop_index('ix_recurring_patterns_user_id', table_name='recurring_patterns')
    op.drop_index('ix_recurring_patterns_task_id', table_name='recurring_patterns')
