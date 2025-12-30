"""User entity model"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr


class User(SQLModel, table=True):
    """User entity representing an application user

    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        name: User's display name
        password_hash: Hashed password (never exposed via API)
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
        is_active: Whether the user account is active
        tasks: Relationship to user's tasks
    """
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)
    name: str = Field(min_length=1, max_length=100, nullable=False)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)
