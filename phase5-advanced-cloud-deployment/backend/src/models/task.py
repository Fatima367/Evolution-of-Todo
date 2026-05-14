"""Task entity model"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .reminder import Reminder
    from .recurring_pattern import RecurringPattern


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


class RecurringType(str, Enum):
    """Recurring task type enumeration"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Task(SQLModel, table=True):
    """Task entity representing a user's todo item

    Attributes:
        id: Unique identifier (UUID)
        title: Task title (1-200 characters)
        description: Detailed description (optional, max 10000 characters)
        status: Task status (pending, in_progress, completed)
        priority: Task priority (low, medium, high, urgent)
        due_date: Optional deadline for the task
        reminder_offset: Minutes before due_date to send reminder (default: 15)
        tags: Array of tags (max 10 tags, each max 50 characters)
        is_favorite: Whether the task is starred/favorited
        recurring_type: How often the task repeats (none, daily, weekly, monthly, yearly)
        user_id: Foreign key to owning user
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
        completed_at: Timestamp when task was marked as completed
        user: Relationship to owning user
        reminders: Relationship to task reminders
        recurring_pattern: Relationship to recurring pattern (1:1)
    """
    __tablename__ = "tasks"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=10000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, nullable=False, index=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_offset: int = Field(default=15, ge=0, le=1440, nullable=False)  # minutes before due_date
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    is_favorite: bool = Field(default=False, nullable=False, index=True)
    recurring_type: RecurringType = Field(default=RecurringType.NONE, nullable=False, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")
    reminders: List["Reminder"] = Relationship(back_populates="task")
    recurring_pattern: Optional["RecurringPattern"] = Relationship(back_populates="task")
