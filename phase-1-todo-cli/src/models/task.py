"""Task model with SQLModel integration for SQLite persistence."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.engine import Engine


class PriorityEnum(str, Enum):
    """Task priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class StatusEnum(str, Enum):
    """Task status values."""
    PENDING = "Pending"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"


class Task(SQLModel, table=True):
    """
    Task entity for todo management.

    Attributes:
        id: Auto-incremented unique identifier
        title: Task title (1-200 characters)
        description: Optional detailed description (max 500 characters)
        created_date: Timestamp when task was created
        priority: Task priority level (Low, Medium, High)
        status: Current task status (Pending, In-Progress, Completed)
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    created_date: datetime = Field(default_factory=datetime.now)
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    status: StatusEnum = Field(default=StatusEnum.PENDING)


# Database engine configuration
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """
    Get or create the SQLite database engine.
    Uses file-based SQLite for persistent storage.

    Returns:
        Engine: SQLModel database engine configured for SQLite
    """
    global _engine
    if _engine is None:
        # Use file-based SQLite for persistence (per user requirement)
        _engine = create_engine("sqlite:///todo.db", echo=False)
    return _engine


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
