"""Reminder entity model"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .task import Task
    from .user import User


class Reminder(SQLModel, table=True):
    """Reminder for tasks with due dates

    Attributes:
        id: Unique identifier (auto-increment)
        task_id: Foreign key to associated task
        user_id: Foreign key to owning user (for isolation)
        remind_at: When to send reminder (UTC)
        sent: Has reminder been sent
        sent_at: When reminder was sent
        created_at: Reminder creation timestamp
    """
    __tablename__ = "reminders"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", nullable=False, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    remind_at: datetime = Field(nullable=False, index=True)
    sent: bool = Field(default=False, nullable=False, index=True)
    sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="reminders")
    user: Optional["User"] = Relationship(back_populates="reminders")
