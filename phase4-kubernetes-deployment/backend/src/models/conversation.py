"""Conversation model for ChatKit conversations stored in PostgreSQL"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .message import Message
    from .user import User


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session between user and AI assistant

    Attributes:
        id: Unique identifier (auto-generated UUID)
        user_id: Foreign key to owning user (UUID)
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated (on each message)
        messages: Relationship to messages in this conversation
        user: Relationship to owning user
    """
    __tablename__ = "conversations"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    user: Optional["User"] = Relationship(back_populates="conversations")
