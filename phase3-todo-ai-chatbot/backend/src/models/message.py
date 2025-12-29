"""Message model for ChatKit messages stored in PostgreSQL"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .conversation import Conversation
    from .user import User


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation

    Attributes:
        id: Unique identifier (auto-generated integer)
        user_id: Foreign key to owning user (UUID)
        conversation_id: Foreign key to parent conversation (integer)
        role: Message role ('user' or 'assistant')
        content: Message content text (max 10000 characters)
        created_at: Timestamp when message was created
        conversation: Relationship to parent conversation
        user: Relationship to owning user
    """
    __tablename__ = "messages"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(nullable=False)
    content: str = Field(min_length=1, max_length=10000, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")
