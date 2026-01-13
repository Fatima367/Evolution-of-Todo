"""Recurring Pattern entity model"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .task import Task
    from .user import User


class RecurringPattern(SQLModel, table=True):
    """Recurring pattern configuration for recurring tasks

    Attributes:
        id: Unique identifier (auto-increment)
        task_id: Foreign key to associated task (1:1 relationship)
        user_id: Foreign key to owning user (for isolation)
        frequency: Recurrence frequency (daily, weekly, monthly, yearly, custom)
        interval: Repeat every N periods (e.g., every 2 weeks)
        day_of_week: For weekly: 0-6 (0=Monday)
        day_of_month: For monthly: 1-31
        month_of_year: For yearly: 1-12
        end_date: When to stop recurring (null = forever)
        last_generated_at: Last time next occurrence was created
        created_at: Pattern creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "recurring_patterns"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", unique=True, nullable=False, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    frequency: str = Field(max_length=20, nullable=False)  # daily, weekly, monthly, yearly, custom
    interval: int = Field(default=1, ge=1, nullable=False)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    month_of_year: Optional[int] = Field(default=None, ge=1, le=12)
    end_date: Optional[datetime] = Field(default=None)
    last_generated_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="recurring_pattern")
    user: Optional["User"] = Relationship(back_populates="recurring_patterns")
