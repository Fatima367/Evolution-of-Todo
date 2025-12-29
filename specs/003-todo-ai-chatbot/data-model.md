# Data Model: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Created**: 2025-12-28
**Purpose**: Define database schema, entity relationships, and validation rules

## Overview

Phase III extends the existing Phase II database schema with two new entities: `Conversation` and `Message`. The existing `Task` model is reused with no changes required.

## Entity Relationship Diagram

```
┌─────────────┐         ┌───────────────┐         ┌─────────────┐
│   User      │───────1│  Conversation  │───────*│  Message    │
│             │         │               │         │             │
│ id          │         │ id            │         │ id          │
│ email       │         │ user_id       │         │ user_id     │
│ password    │         │ created_at    │         │ conv_id     │
│ ...         │         │ updated_at    │         │ role        │
└─────────────┘         └───────────────┘         │ content     │
                                                    │ created_at  │
                                                    └─────────────┘

┌─────────────┐
│    Task     │
│             │
│ id          │
│ user_id     │───┬── User
│ title       │
│ description │
│ completed   │
│ created_at  │
│ updated_at  │
└─────────────┘
```

## Entities

### Task

**Purpose**: Represents a todo item managed by users.
**Status**: Existing from Phase II - no changes required.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|----------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | auto | Unique identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY | - | Owner of this task |
| title | VARCHAR(500) | NOT NULL | - | Task title |
| description | TEXT | NULLABLE | NULL | Optional description |
| completed | BOOLEAN | NOT NULL | FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- `idx_tasks_user_id` on `user_id`

**Validation Rules**:
- `title` must be non-empty (min length: 1)
- `user_id` must reference valid user
- `completed` can only be TRUE or FALSE
- `updated_at` must be >= `created_at`

### Conversation

**Purpose**: Represents a chat session between a user and the AI assistant.
**Status**: NEW for Phase III.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|----------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | auto | Unique identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY | - | Owner of this conversation |
| created_at | TIMESTAMP | NOT NULL | NOW() | Session creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last message timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- `idx_conversations_user_id` on `user_id`
- `idx_conversations_updated_at` on `updated_at` (DESC)

**Foreign Keys**:
- `user_id` → `users(id)` ON DELETE CASCADE

**Validation Rules**:
- `user_id` must reference valid user
- `created_at` <= `updated_at`
- `updated_at` must be updated on each message addition

### Message

**Purpose**: Represents a single message in a conversation (user or assistant).
**Status**: NEW for Phase III.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|----------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | auto | Unique identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY | - | Owner of this message |
| conversation_id | INTEGER | NOT NULL, FOREIGN KEY | - | Parent conversation |
| role | VARCHAR(20) | NOT NULL, CHECK | - | 'user' or 'assistant' |
| content | TEXT | NOT NULL | - | Message content |
| created_at | TIMESTAMP | NOT NULL | NOW() | Message timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- `idx_messages_conversation_id` on `conversation_id`
- `idx_messages_user_id` on `user_id`
- `idx_messages_created_at` on `created_at` (ASC)

**Foreign Keys**:
- `user_id` → `users(id)` ON DELETE CASCADE
- `conversation_id` → `conversations(id)` ON DELETE CASCADE

**Validation Rules**:
- `user_id` must reference valid user
- `conversation_id` must reference valid conversation
- `role` must be either 'user' or 'assistant'
- `content` must be non-empty (min length: 1)
- `content` max length: 10000 characters (configurable)

## Relationships

### User → Conversation (1:N)
One user can have many conversations.
When a user is deleted, all their conversations are cascaded.

### Conversation → Message (1:N)
One conversation can have many messages.
When a conversation is deleted, all its messages are cascaded.

### User → Task (1:N)
One user can have many tasks (existing from Phase II).

### User → Message (1:N)
One user can have many messages.
Messages are directly owned by users for isolation and querying.

## SQL DDL

### Conversations Table

```sql
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_id
    ON conversations(user_id);

CREATE INDEX idx_conversations_updated_at
    ON conversations(updated_at DESC);
```

### Messages Table

```sql
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_messages_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,
    CONSTRAINT chk_message_content_length
        CHECK (LENGTH(content) >= 1)
);

CREATE INDEX idx_messages_conversation_id
    ON messages(conversation_id);

CREATE INDEX idx_messages_user_id
    ON messages(user_id);

CREATE INDEX idx_messages_created_at
    ON messages(created_at ASC);
```

## SQLModel Definitions

### Conversation Model

```python
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
import enum

if TYPE_CHECKING:
    from .conversation import Conversation

class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(default=MessageRole.USER)
    content: str = Field(min_length=1, max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

## State Transitions

### Conversation Lifecycle

```
   ┌─────────┐
   │ Created │
   └────┬────┘
        │
        v
   ┌─────────┐
   │  Active │───┐
   └─────────┘   │
                  │  (user sends message)
                  │
                  v
   ┌─────────┐
   │ Updated │───┐
   └─────────┘   │ (repeat)
                  │
                  │
                  v
   ┌─────────┐
   │ Inactive│ (no activity for extended period)
   └─────────┘
```

### Message Flow

```
User Message → Store → Build Context → AI Agent → Tool Calls → Response → Store → Return
     │                                                                      │
     └──────────────────────────────────────────────────────────────────────────┘
                                   (conversation persists)
```

## Query Patterns

### Fetch Conversation History

```python
# Get all messages for a conversation, ordered by creation time
def get_conversation_messages(conversation_id: int, user_id: str) -> list[Message]:
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at)
    ).all()
```

### Create Conversation

```python
def create_conversation(user_id: str) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
```

### Add Message

```python
def add_message(user_id: str, conversation_id: int, role: str, content: str) -> Message:
    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
```

### Update Conversation Timestamp

```python
def update_conversation(conversation_id: int) -> None:
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()
```

## Data Migration

### Migration Script (Alembic)

```python
# migrations/versions/003_add_conversation_tables.py

from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'  # Reference Phase II migration
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')"),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

## Notes

- All queries include `user_id` filter for security (multi-tenant isolation)
- Cascading deletes ensure data consistency when users or conversations are removed
- Indexes are optimized for common query patterns
- Message content length limit prevents storage issues and abuse
- Conversation `updated_at` is updated on each message for sorting by recency
