"""Task API schemas for request/response validation"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from src.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    """Schema for task creation request"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=10000, description="Detailed description")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Optional deadline")
    tags: Optional[List[str]] = Field(None, max_length=10, description="Array of tags")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags array"""
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Each tag must be max 50 characters')
        return v

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate due date is in the future"""
        if v is not None and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v


class TaskUpdate(BaseModel):
    """Schema for task update request (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = Field(None, max_length=10)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags array"""
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Each tag must be max 50 characters')
        return v


class TaskRead(BaseModel):
    """Schema for task response"""
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    tags: Optional[List[str]]
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for task list response with pagination"""
    tasks: List[TaskRead]
    total: int


# Sort field options for task sorting
class SortField(str, Enum):
    """Valid fields to sort tasks by"""
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    TITLE = "title"


# Sort direction options
class SortOrder(str, Enum):
    """Sort direction options"""
    ASC = "asc"
    DESC = "desc"
