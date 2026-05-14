"""Task entity model"""
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(SQLModel, table=True):
    """Task entity representing a user's todo item

    Attributes:
        id: Unique identifier (UUID)
        title: Task title (1-200 characters)
        description: Detailed description (optional, max 10000 characters)
        status: Task status (pending, in_progress, completed)
        priority: Task priority (low, medium, high, urgent)
        due_date: Optional deadline for the task
        tags: Array of tags (max 10 tags, each max 50 characters)
        user_id: Foreign key to owning user
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
        completed_at: Timestamp when task was marked as completed
        user: Relationship to owning user
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=10000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, nullable=False, index=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")
